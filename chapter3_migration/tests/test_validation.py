"""Validation harness for the migrated Chapter 3 jobs.

Materialises every asset against the checked-in ``SampleDataFiles/Chapter3``
inputs and asserts row counts and content against the fixture-derived expected
outputs. Because ``products.xls`` / ``customers.xls`` are regenerated fixtures
(not from the original book), expectations are derived from those fixtures
rather than any book-supplied golden files.

Run with pytest::

    pytest chapter3_migration/tests

or as a standalone harness that prints a per-job PASS/FAIL summary::

    python chapter3_migration/tests/test_validation.py
"""

from __future__ import annotations

import os
import tempfile
from datetime import datetime

import polars as pl
import pytest
from dagster import materialize
from lxml import etree

from chapter3_migration.definitions import all_assets
from chapter3_migration.resources import Chapter3Paths


@pytest.fixture(scope="module")
def run():
    """Materialise all assets once into a throwaway output dir."""
    tmp = tempfile.mkdtemp()
    result = materialize(all_assets, resources={"paths": Chapter3Paths(data_out_dir=tmp)})
    assert result.success
    return result, tmp


def _read(tmp: str, name: str, encoding: str = "ISO-8859-15") -> str:
    with open(os.path.join(tmp, name), encoding=encoding) as fh:
        return fh.read()


def _data_lines(text: str) -> list[str]:
    return [ln for ln in text.splitlines() if ln != ""]


def test_csv2xml(run):
    _, tmp = run
    root = etree.parse(os.path.join(tmp, "csv2xml-out.xml")).getroot()
    assert root.tag == "catalogue"
    skus = root.findall("sku")
    assert len(skus) == 12
    for sku in skus:
        assert [c.tag for c in sku] == ["skuid", "skuname", "size", "colour", "price"]
    assert skus[0].findtext("skuid") == "1233212406"
    assert skus[0].findtext("price") == "39.99"


def test_xml2csv(run):
    _, tmp = run
    lines = _data_lines(_read(tmp, "catalogue-out.csv"))
    assert len(lines) == 12
    assert all(len(ln.split(";")) == 5 for ln in lines)
    assert lines[0] == "1233212406;Summer Dress;6;Green;39.99"


def test_expressions(run):
    _, tmp = run
    root = etree.parse(os.path.join(tmp, "expressions-out.xml")).getroot()
    assert root.tag == "customers"
    customers = root.findall("customer")
    assert len(customers) == 4
    # id zero-padded to 8 digits
    assert customers[0].findtext("id") == "00000001"
    assert customers[0].findtext("name") == "John Black"
    # Address2 present -> appended with ", "
    assert customers[0].findtext("address_1") == "123 North Street, West Hill"
    assert customers[0].findtext("address_2") == "Nottingham, Nottinghamshire, NG1 3RD"
    # telephone digits only
    assert customers[0].findtext("telephone_number") == "01153213333"
    # second customer: Address2 empty -> no trailing ", "
    assert customers[1].findtext("address_1") == "45 South Drive"
    # non-digit junk stripped from telephone
    assert customers[2].findtext("telephone_number") == "01216355656"


def test_advanced_xml_output(run):
    _, tmp = run
    text = _read(tmp, "order_status.xml", encoding="UTF-8")
    assert '<!DOCTYPE DISPATCH_DOCUMENT SYSTEM "Talend.dtd">' in text
    root = etree.fromstring(text.encode("UTF-8"))
    assert root.tag == "DISPATCH_DOCUMENT"
    orders = root.findall("ORDER")
    # only "shipped" orders survive the filter: 1233 and 1236
    assert sorted(o.get("ID") for o in orders) == ["1233", "1236"]
    lines = root.findall(".//ORDER_LINE")
    assert len(lines) == 8
    for line in lines:
        # dispatch date is stamped and parseable
        datetime.strptime(line.get("DISPATCHED_DATE"), "%Y-%m-%d %H:%M")
        assert line.get("SKU")


def test_multi_schema(run):
    result, _ = run
    skus: pl.DataFrame = result.output_for_node("ms_skus")
    inventory: pl.DataFrame = result.output_for_node("ms_inventory")
    assert skus.columns == ["skuid", "skuname", "size", "colour", "price"]
    assert skus.height == 10
    assert inventory.columns == ["skuid", "stock_on_hand"]
    assert inventory.height == 10
    assert skus.row(0)[0] == "432345"


def test_state_lookup(run):
    _, tmp = run
    lines = _data_lines(_read(tmp, "address-lookup-out.csv"))
    assert len(lines) == 5
    assert lines[0] == "Microsoft;One Microsoft Way;Redmond;WA;98052"
    # state codes resolved via the lookup
    assert lines[3].split(";")[3] == "TX"


def test_spreadsheet1(run):
    _, tmp = run
    text = _read(tmp, "product-excel-out.csv")
    all_lines = text.splitlines()
    # header present
    assert all_lines[0] == "product_code;product_name"
    data = _data_lines(text)[1:]
    assert len(data) == 14  # 5 dresses + 5 skirts + 4 knitwear
    assert data[0] == "12345678;Red Dress"


def test_spreadsheet2(run):
    _, tmp = run
    matched = _data_lines(_read(tmp, "customer-addresses.csv"))
    rejects = _data_lines(_read(tmp, "customer-addresses-rejects.csv"))
    assert len(matched) == 4
    assert all(len(ln.split(";")) == 9 for ln in matched)
    assert matched[0].startswith("12345;Mr;Fitzwilliam;Darcy;fdarcy@darcy.com")
    # customer 12349 has no address -> single reject row
    assert len(rejects) == 1
    assert rejects[0] == "12349;Mr;George;Wickham;gw@wickham.com"


if __name__ == "__main__":
    tmp = tempfile.mkdtemp()
    result = materialize(all_assets, resources={"paths": Chapter3Paths(data_out_dir=tmp)})
    if not result.success:
        raise SystemExit("materialization failed")
    checks = [
        ("CSV2XML", test_csv2xml),
        ("XML2CSV", test_xml2csv),
        ("Expressions", test_expressions),
        ("AdvancedXMLOutput", test_advanced_xml_output),
        ("MultiSchema", test_multi_schema),
        ("StateLookup", test_state_lookup),
        ("Spreadsheet1", test_spreadsheet1),
        ("Spreadsheet2", test_spreadsheet2),
    ]
    run_value = (result, tmp)
    failed = 0
    for name, fn in checks:
        try:
            fn(run_value)
            print(f"PASS  {name}")
        except AssertionError as exc:  # noqa: PERF203
            failed += 1
            print(f"FAIL  {name}: {exc}")
    print(f"\n{len(checks) - failed}/{len(checks)} jobs validated")
    raise SystemExit(1 if failed else 0)
