"""Spreadsheet1 job.

Talend flow: tFileInputExcel (products.xls, VERSION_2007=false) ->
tFileOutputDelimited.

Reads sheets ``dresses``, ``skirts`` and ``knitwear`` (header row 1, columns
1-2), concatenates them and writes a semicolon CSV *with* a header. Only the
first two columns matter; they are emitted as ``product_code`` / ``product_name``.

    input encoding : UTF-8           output encoding : ISO-8859-15
"""

import polars as pl
from dagster import AssetExecutionContext, MetadataValue, asset

from ..io_utils import write_delimited
from ..resources import Chapter3Paths

SHEETS = ["dresses", "skirts", "knitwear"]
OUTPUT_COLUMNS = ["product_code", "product_name"]
GROUP = "spreadsheet1"


def _read_sheet(path: str, sheet: str) -> pl.DataFrame:
    df = pl.read_excel(path, sheet_name=sheet, engine="calamine", has_header=True)
    # Talend reads FIRST_COLUMN=1..LAST_COLUMN=2 positionally.
    df = df.select(df.columns[:2])
    df.columns = OUTPUT_COLUMNS
    return df.with_columns(pl.all().cast(pl.String))


@asset(group_name=GROUP)
def products_excel(paths: Chapter3Paths) -> pl.DataFrame:
    """Read + concatenate the three product worksheets."""
    path = paths.in_path("products.xls")
    frames = [_read_sheet(path, sheet) for sheet in SHEETS]
    return pl.concat(frames, how="vertical")


@asset(group_name=GROUP)
def spreadsheet1_output(
    context: AssetExecutionContext,
    paths: Chapter3Paths,
    products_excel: pl.DataFrame,
) -> None:
    """Write product-excel-out.csv (semicolon, WITH header)."""
    out = paths.out_path("product-excel-out.csv")
    n = write_delimited(
        out,
        products_excel.iter_rows(),
        header=OUTPUT_COLUMNS,
        sep=";",
        encoding="ISO-8859-15",
    )
    context.add_output_metadata({"rows": n, "path": MetadataValue.path(out)})
