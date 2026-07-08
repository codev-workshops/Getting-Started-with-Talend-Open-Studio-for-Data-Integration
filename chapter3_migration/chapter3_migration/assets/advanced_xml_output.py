"""AdvancedXMLOutput job.

Talend flow: tFileInputDelimited (order_status.csv) -> tMap -> tAdvancedFileOutputXML.

tMap filter : row1.shipping_status.equals("shipped")
tMap adds   : dispatch_date = TalendDate.getCurrentDate()

Nested output hierarchy (tAdvancedFileOutputXML):

    /DISPATCH_DOCUMENT
        /ORDER                     ID = order_id                (attribute)
            /ORDER_LINE            ID            = line_id       (attribute)
                                   SKU           = sku           (attribute)
                                   QUANTITY      = quantity      (attribute)
                                   DISPATCHED_DATE = dispatch_date(attribute)
                                   TRACKING_ID   = courier_docket_code (attribute)

Multiple ORDER_LINE elements are grouped under a single ORDER per order_id.
The original job emits a ``<!DOCTYPE ... SYSTEM "Talend.dtd">`` reference
(toggle via :attr:`Chapter3Paths.emit_dtd`).

    input encoding : US-ASCII        output encoding : UTF-8
"""

import polars as pl
from lxml import etree
from dagster import AssetExecutionContext, MetadataValue, asset

from .. import helpers
from ..resources import Chapter3Paths

INPUT_COLUMNS = [
    "order_id", "line_id", "sku", "quantity", "shipping_status",
    "courier_docket_code",
]
GROUP = "advanced_xml_output"


@asset(group_name=GROUP)
def advanced_xml_input(paths: Chapter3Paths) -> pl.DataFrame:
    """Read order_status.csv (semicolon-delimited, one header row)."""
    return pl.read_csv(
        paths.in_path("order_status.csv"),
        separator=";",
        has_header=True,
        infer_schema=False,
        encoding="utf8",
    )


@asset(group_name=GROUP)
def advanced_xml_shipped(advanced_xml_input: pl.DataFrame) -> pl.DataFrame:
    """tMap: keep only shipped lines and stamp the dispatch date."""
    dispatch = helpers.format_dispatch_date(helpers.get_current_date())
    return (
        advanced_xml_input.filter(pl.col("shipping_status") == "shipped")
        .with_columns(pl.lit(dispatch).alias("dispatch_date"))
        .select(
            "order_id", "line_id", "sku", "quantity", "dispatch_date",
            "courier_docket_code",
        )
    )


@asset(group_name=GROUP)
def advanced_xml_output(
    context: AssetExecutionContext,
    paths: Chapter3Paths,
    advanced_xml_shipped: pl.DataFrame,
) -> None:
    """Write the nested order_status.xml document."""
    root = etree.Element("DISPATCH_DOCUMENT")
    orders: dict[str, etree._Element] = {}
    n_lines = 0
    for r in advanced_xml_shipped.iter_rows(named=True):
        oid = r["order_id"]
        order_el = orders.get(oid)
        if order_el is None:
            order_el = etree.SubElement(root, "ORDER", ID=str(oid))
            orders[oid] = order_el
        etree.SubElement(
            order_el,
            "ORDER_LINE",
            ID=str(r["line_id"]),
            SKU=str(r["sku"]),
            QUANTITY=str(r["quantity"]),
            DISPATCHED_DATE=str(r["dispatch_date"]),
            TRACKING_ID="" if r["courier_docket_code"] is None else str(r["courier_docket_code"]),
        )
        n_lines += 1

    out = paths.out_path("order_status.xml")
    doctype = '<!DOCTYPE DISPATCH_DOCUMENT SYSTEM "Talend.dtd">' if paths.emit_dtd else None
    etree.ElementTree(root).write(
        out,
        pretty_print=True,
        xml_declaration=True,
        encoding="UTF-8",
        doctype=doctype,
    )
    context.add_output_metadata(
        {
            "orders": len(orders),
            "order_lines": n_lines,
            "path": MetadataValue.path(out),
        }
    )
