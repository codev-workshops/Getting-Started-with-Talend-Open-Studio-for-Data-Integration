"""Reusable CSV I/O functions that enforce delimiter, encoding, and header parity with Talend jobs."""
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import StructType


def read_csv(
    spark: SparkSession,
    path: str,
    sep: str = ";",
    header: bool = False,
    schema: StructType = None,
    encoding: str = "UTF-8",
) -> DataFrame:
    """Read a CSV file into a DataFrame with explicit schema and delimiter.

    Args:
        spark: Active SparkSession.
        path: Path to the CSV file.
        sep: Field separator (default ";", matching most Talend jobs in this project).
        header: Whether the first row is a header.
        schema: Explicit StructType schema. If None, schema is inferred.
        encoding: Character encoding of the file.

    Returns:
        DataFrame with the specified schema.
    """
    reader = spark.read.option("sep", sep).option("encoding", encoding)
    if schema is not None:
        reader = reader.schema(schema)
    if header:
        reader = reader.option("header", "true")
    else:
        reader = reader.option("header", "false")
    return reader.csv(path)


def write_csv(
    df: DataFrame,
    path: str,
    sep: str = ";",
    header: bool = False,
    encoding: str = "UTF-8",
    mode: str = "overwrite",
    single_file: bool = True,
) -> None:
    """Write a DataFrame to CSV with explicit delimiter and encoding.

    Args:
        df: DataFrame to write.
        path: Output directory path.
        sep: Field separator.
        header: Whether to write header row.
        encoding: Character encoding for the output file.
        mode: Write mode (overwrite, append, etc.).
        single_file: If True, coalesce to 1 partition for a single output file.
    """
    writer = df
    if single_file:
        writer = df.coalesce(1)
    (
        writer.write
        .option("sep", sep)
        .option("encoding", encoding)
        .option("header", str(header).lower())
        .mode(mode)
        .csv(path)
    )
