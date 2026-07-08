"""Expressions job.

Talend flow: tFileInputDelimited (expressions.csv) -> tMap -> tFileOutputXML.
Demonstrates the Talend expression/routine language; the tMap output columns
are reproduced exactly by :mod:`chapter3_migration.helpers`.

    input encoding : US-ASCII        output encoding : UTF-8

tMap output ``map_output``:
    id               = String.format("%08d", CustomerID)
    name             = FirstName + " " + LastName
    address_1        = Address2.equals("") ? Address1 : Address1 + ", " + Address2
    address_2        = TownCity + ", " + County + ", " + Postcode
    telephone_number = Telephone.replaceAll("[^\\d]", "")
"""

import polars as pl
from dagster import AssetExecutionContext, MetadataValue, asset

from .. import helpers
from ..io_utils import write_flat_xml
from ..resources import Chapter3Paths

INPUT_COLUMNS = [
    "CustomerID", "FirstName", "LastName", "Address1", "Address2",
    "TownCity", "County", "Postcode", "Telephone",
]
OUTPUT_COLUMNS = ["id", "name", "address_1", "address_2", "telephone_number"]
GROUP = "expressions"


@asset(group_name=GROUP)
def expressions_input(paths: Chapter3Paths) -> pl.DataFrame:
    """Read expressions.csv (semicolon-delimited, one header row)."""
    return pl.read_csv(
        paths.in_path("expressions.csv"),
        separator=";",
        has_header=True,
        infer_schema=False,
        encoding="utf8",
    )


@asset(group_name=GROUP)
def expressions_mapped(expressions_input: pl.DataFrame) -> pl.DataFrame:
    """Apply the tMap transforms row by row."""
    mapped: list[dict[str, str]] = []
    for r in expressions_input.iter_rows(named=True):
        mapped.append(
            {
                "id": helpers.zero_pad(r["CustomerID"], 8),
                "name": helpers.full_name(r["FirstName"], r["LastName"]),
                "address_1": helpers.address_line_1(r["Address1"], r["Address2"]),
                "address_2": helpers.address_line_2(
                    r["TownCity"], r["County"], r["Postcode"]
                ),
                "telephone_number": helpers.digits_only(r["Telephone"]),
            }
        )
    return pl.DataFrame(mapped, schema=OUTPUT_COLUMNS)


@asset(group_name=GROUP)
def expressions_output(
    context: AssetExecutionContext,
    paths: Chapter3Paths,
    expressions_mapped: pl.DataFrame,
) -> None:
    """Write expressions-out.xml (root ``customers``, row tag ``customer``)."""
    out = paths.out_path("expressions-out.xml")
    n = write_flat_xml(
        out,
        root_tag="customers",
        row_tag="customer",
        columns=OUTPUT_COLUMNS,
        rows=expressions_mapped.iter_rows(),
        encoding="UTF-8",
    )
    context.add_output_metadata({"rows": n, "path": MetadataValue.path(out)})
