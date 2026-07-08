"""CSV2XML job.

Talend flow: tFileInputDelimited (csv2xml-catalogue.csv) -> tFileOutputXML.
Reads a headerless semicolon CSV and writes a flat ``<catalogue><sku>..``
XML document.

    input encoding : US-ASCII        output encoding : UTF-8
"""

import polars as pl
from dagster import AssetExecutionContext, MetadataValue, asset

from ..io_utils import write_flat_xml
from ..resources import Chapter3Paths

COLUMNS = ["skuid", "skuname", "size", "colour", "price"]
GROUP = "csv2xml"


@asset(group_name=GROUP)
def csv2xml_input(paths: Chapter3Paths) -> pl.DataFrame:
    """Read csv2xml-catalogue.csv (semicolon-delimited, no header)."""
    return pl.read_csv(
        paths.in_path("csv2xml-catalogue.csv"),
        separator=";",
        has_header=False,
        new_columns=COLUMNS,
        infer_schema=False,  # keep every field as text to preserve values
        encoding="utf8",
    )


@asset(group_name=GROUP)
def csv2xml_output(
    context: AssetExecutionContext,
    paths: Chapter3Paths,
    csv2xml_input: pl.DataFrame,
) -> None:
    """Write csv2xml-out.xml (root ``catalogue``, row tag ``sku``)."""
    out = paths.out_path("csv2xml-out.xml")
    n = write_flat_xml(
        out,
        root_tag="catalogue",
        row_tag="sku",
        columns=COLUMNS,
        rows=csv2xml_input.iter_rows(),
        encoding="UTF-8",
    )
    context.add_output_metadata({"rows": n, "path": MetadataValue.path(out)})
