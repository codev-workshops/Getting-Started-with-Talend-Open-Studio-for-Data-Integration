"""Spreadsheet2 job.

Talend flow: two tFileInputExcel readers over customers.xls feed a tMap that
INNER-joins customers (main, row1) to addresses (lookup, row2) on
``customer_id``. The tMap has a second output flagged ``rejectInnerJoin="true"``
capturing main rows with no lookup match.

    main   (row1) sheet ``customers``  : customer_id, title, first_name,
                                         last_name, email_address
    lookup (row2) sheet ``addresses``  : customer_id, address1, city,
                                         postcode, telephone_number

Outputs (both semicolon, no header, ISO-8859-15):
    customer-addresses.csv          customer_id, title, first_name, last_name,
                                    email, address1, city, postcode,
                                    telephone_number
    customer-addresses-rejects.csv  customer_id, title, first_name, last_name,
                                    email_address

    input encoding : UTF-8           output encoding : ISO-8859-15
"""

import polars as pl
from dagster import AssetExecutionContext, MetadataValue, asset

from ..io_utils import write_delimited
from ..resources import Chapter3Paths

MATCHED_COLUMNS = [
    "customer_id", "title", "first_name", "last_name", "email",
    "address1", "city", "postcode", "telephone_number",
]
REJECT_COLUMNS = ["customer_id", "title", "first_name", "last_name", "email_address"]
GROUP = "spreadsheet2"


def _read_sheet(path: str, sheet: str) -> pl.DataFrame:
    df = pl.read_excel(path, sheet_name=sheet, engine="calamine", has_header=True)
    return df.with_columns(pl.col("customer_id").cast(pl.Int64).cast(pl.String))


@asset(group_name=GROUP)
def customers_sheet(paths: Chapter3Paths) -> pl.DataFrame:
    """Main input: the ``customers`` worksheet."""
    return _read_sheet(paths.in_path("customers.xls"), "customers")


@asset(group_name=GROUP)
def addresses_sheet(paths: Chapter3Paths) -> pl.DataFrame:
    """Lookup input: the ``addresses`` worksheet."""
    return _read_sheet(paths.in_path("customers.xls"), "addresses")


@asset(group_name=GROUP)
def spreadsheet2_matched(
    customers_sheet: pl.DataFrame,
    addresses_sheet: pl.DataFrame,
) -> pl.DataFrame:
    """INNER join customers to addresses on customer_id."""
    joined = customers_sheet.join(
        addresses_sheet, on="customer_id", how="inner", maintain_order="left"
    )
    return joined.select(
        "customer_id",
        "title",
        "first_name",
        "last_name",
        pl.col("email_address").alias("email"),
        "address1",
        "city",
        "postcode",
        "telephone_number",
    )


@asset(group_name=GROUP)
def spreadsheet2_rejects(
    customers_sheet: pl.DataFrame,
    addresses_sheet: pl.DataFrame,
) -> pl.DataFrame:
    """rejectInnerJoin: customers with no matching address row."""
    matched_ids = addresses_sheet["customer_id"].to_list()
    return customers_sheet.filter(~pl.col("customer_id").is_in(matched_ids)).select(
        REJECT_COLUMNS
    )


@asset(group_name=GROUP)
def spreadsheet2_output(
    context: AssetExecutionContext,
    paths: Chapter3Paths,
    spreadsheet2_matched: pl.DataFrame,
    spreadsheet2_rejects: pl.DataFrame,
) -> None:
    """Write both the matched and reject CSVs."""
    matched_out = paths.out_path("customer-addresses.csv")
    reject_out = paths.out_path("customer-addresses-rejects.csv")
    n_matched = write_delimited(
        matched_out, spreadsheet2_matched.iter_rows(), sep=";", encoding="ISO-8859-15"
    )
    n_rejects = write_delimited(
        reject_out, spreadsheet2_rejects.iter_rows(), sep=";", encoding="ISO-8859-15"
    )
    context.add_output_metadata(
        {
            "matched": n_matched,
            "rejects": n_rejects,
            "matched_path": MetadataValue.path(matched_out),
            "rejects_path": MetadataValue.path(reject_out),
        }
    )
