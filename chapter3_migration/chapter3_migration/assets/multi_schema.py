"""MultiSchema job.

Talend flow: tFileInputMSXML (ms-catalogue.xml, root loop ``/catalogue``)
produces TWO schemas from a single parse, each originally sent to a tLogRow:

    skus      loop ``skus/sku``       -> skuid, skuname, size, colour, price
    inventory loop ``inventory/sku``  -> skuid, stock_on_hand

The single parse fans out into two downstream assets that log their rows
(replacing tLogRow with Dagster logging). ``TRIMALL`` is honoured.

    input encoding : ISO-8859-15
"""

import polars as pl
from lxml import etree
from dagster import AssetExecutionContext, asset

from ..resources import Chapter3Paths

SKUS_COLUMNS = ["skuid", "skuname", "size", "colour", "price"]
INVENTORY_COLUMNS = ["skuid", "stock_on_hand"]
GROUP = "multi_schema"


@asset(group_name=GROUP)
def ms_catalogue_parsed(paths: Chapter3Paths) -> dict[str, list[list[str]]]:
    """Parse ms-catalogue.xml once, extracting both loops (TRIMALL=true)."""
    tree = etree.parse(paths.in_path("ms-catalogue.xml"))

    def rows(loop: str, columns: list[str]) -> list[list[str]]:
        out = []
        for node in tree.xpath(loop):
            out.append([(node.findtext(c) or "").strip() for c in columns])
        return out

    return {
        "skus": rows("/catalogue/skus/sku", SKUS_COLUMNS),
        "inventory": rows("/catalogue/inventory/sku", INVENTORY_COLUMNS),
    }


@asset(group_name=GROUP)
def ms_skus(
    context: AssetExecutionContext,
    ms_catalogue_parsed: dict[str, list[list[str]]],
) -> pl.DataFrame:
    """The ``skus`` schema (was tLogRow_1)."""
    df = pl.DataFrame(ms_catalogue_parsed["skus"], schema=SKUS_COLUMNS, orient="row")
    for row in df.iter_rows():
        context.log.info("|".join(row))
    context.log.info("skus rows: %d", df.height)
    return df


@asset(group_name=GROUP)
def ms_inventory(
    context: AssetExecutionContext,
    ms_catalogue_parsed: dict[str, list[list[str]]],
) -> pl.DataFrame:
    """The ``inventory`` schema (was tLogRow_2)."""
    df = pl.DataFrame(
        ms_catalogue_parsed["inventory"], schema=INVENTORY_COLUMNS, orient="row"
    )
    for row in df.iter_rows():
        context.log.info("|".join(row))
    context.log.info("inventory rows: %d", df.height)
    return df
