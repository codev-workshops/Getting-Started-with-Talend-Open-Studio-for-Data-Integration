"""StateLookup job.

Talend flow: tJoin with main = corporate-addresses.csv and lookup = states.csv.

    JOIN_KEY : main.state == lookup.state_name
    output   : state_code taken from the lookup
    USE_INNER_JOIN = false  ->  LEFT join (unmatched main rows are kept,
                                 state_code becomes null/empty)

Output columns: company_name, address, city, state_code, zip.

    main encoding   : US-ASCII (semicolon)   output encoding : ISO-8859-15
    lookup encoding : US-ASCII (comma)
"""

import polars as pl
from dagster import AssetExecutionContext, MetadataValue, asset

from ..io_utils import write_delimited
from ..resources import Chapter3Paths

MAIN_COLUMNS = ["company_name", "address", "city", "state", "zip"]
OUTPUT_COLUMNS = ["company_name", "address", "city", "state_code", "zip"]
GROUP = "state_lookup"


@asset(group_name=GROUP)
def corporate_addresses(paths: Chapter3Paths) -> pl.DataFrame:
    """Main input: corporate-addresses.csv (semicolon, one header row)."""
    return pl.read_csv(
        paths.in_path("corporate-addresses.csv"),
        separator=";",
        has_header=True,
        infer_schema=False,
        encoding="utf8",
    )


@asset(group_name=GROUP)
def states_lookup(paths: Chapter3Paths) -> pl.DataFrame:
    """Lookup input: states.csv (comma, one header row)."""
    return pl.read_csv(
        paths.in_path("states.csv"),
        separator=",",
        has_header=True,
        infer_schema=False,
        encoding="utf8",
    )


@asset(group_name=GROUP)
def state_lookup_joined(
    corporate_addresses: pl.DataFrame,
    states_lookup: pl.DataFrame,
) -> pl.DataFrame:
    """Left-join corporate.state == states.state_name; keep unmatched rows."""
    joined = corporate_addresses.join(
        states_lookup, left_on="state", right_on="state_name", how="left"
    )
    return joined.select(
        "company_name",
        "address",
        "city",
        pl.col("state_code"),
        "zip",
    )


@asset(group_name=GROUP)
def state_lookup_output(
    context: AssetExecutionContext,
    paths: Chapter3Paths,
    state_lookup_joined: pl.DataFrame,
) -> None:
    """Write address-lookup-out.csv (semicolon, no header)."""
    out = paths.out_path("address-lookup-out.csv")
    n = write_delimited(
        out, state_lookup_joined.iter_rows(), sep=";", encoding="ISO-8859-15"
    )
    unmatched = state_lookup_joined.filter(pl.col("state_code").is_null()).height
    context.add_output_metadata(
        {"rows": n, "unmatched": unmatched, "path": MetadataValue.path(out)}
    )
