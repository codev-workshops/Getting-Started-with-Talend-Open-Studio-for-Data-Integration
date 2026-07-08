"""XML2CSV job.

Talend flow: tFileInputXML (catalogue.xml, loop ``/catalogue/sku``) ->
tFileOutputDelimited. Writes a headerless semicolon CSV.

    input encoding : UTF-8           output encoding : ISO-8859-15
"""

from lxml import etree
from dagster import AssetExecutionContext, MetadataValue, asset

from ..io_utils import write_delimited
from ..resources import Chapter3Paths

COLUMNS = ["skuid", "skuname", "size", "colour", "price"]
LOOP = "/catalogue/sku"
GROUP = "xml2csv"


@asset(group_name=GROUP)
def xml2csv_rows(paths: Chapter3Paths) -> list[list[str]]:
    """Parse catalogue.xml, looping over ``/catalogue/sku``."""
    tree = etree.parse(paths.in_path("catalogue.xml"))
    rows: list[list[str]] = []
    for sku in tree.xpath(LOOP):
        rows.append([(sku.findtext(col) or "").strip() for col in COLUMNS])
    return rows


@asset(group_name=GROUP)
def xml2csv_output(
    context: AssetExecutionContext,
    paths: Chapter3Paths,
    xml2csv_rows: list[list[str]],
) -> None:
    """Write catalogue-out.csv (semicolon-delimited, no header)."""
    out = paths.out_path("catalogue-out.csv")
    n = write_delimited(out, xml2csv_rows, sep=";", encoding="ISO-8859-15")
    context.add_output_metadata({"rows": n, "path": MetadataValue.path(out)})
