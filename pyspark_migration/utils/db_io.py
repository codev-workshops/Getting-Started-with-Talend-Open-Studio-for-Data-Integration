"""JDBC read/write helpers for MySQL database integration."""
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import StructType
from typing import Optional


DEFAULT_JDBC_DRIVER = "com.mysql.cj.jdbc.Driver"


def read_table(
    spark: SparkSession,
    jdbc_url: str,
    table: str,
    user: str,
    password: str,
    schema: Optional[StructType] = None,
    driver: str = DEFAULT_JDBC_DRIVER,
    pushdown_query: Optional[str] = None,
) -> DataFrame:
    """Read a MySQL table or pushdown query into a DataFrame.

    Args:
        spark: Active SparkSession.
        jdbc_url: JDBC connection URL, e.g. "jdbc:mysql://127.0.0.1:3306/demo_db".
        table: Table name to read. Ignored if pushdown_query is provided.
        user: Database username.
        password: Database password.
        schema: Optional explicit schema to apply after read.
        driver: JDBC driver class name.
        pushdown_query: Optional SQL query to push down to the DB.
            If provided, used as the dbtable value wrapped in parentheses.

    Returns:
        DataFrame with the table data.
    """
    dbtable = f"({pushdown_query}) AS tmp" if pushdown_query else table
    reader = (
        spark.read
        .format("jdbc")
        .option("url", jdbc_url)
        .option("dbtable", dbtable)
        .option("user", user)
        .option("password", password)
        .option("driver", driver)
    )
    df = reader.load()
    if schema is not None:
        # Cast to expected schema
        for field in schema.fields:
            df = df.withColumn(field.name, df[field.name].cast(field.dataType))
    return df


def write_table(
    df: DataFrame,
    jdbc_url: str,
    table: str,
    user: str,
    password: str,
    mode: str = "append",
    driver: str = DEFAULT_JDBC_DRIVER,
) -> None:
    """Write a DataFrame to a MySQL table.

    Args:
        df: DataFrame to write.
        jdbc_url: JDBC connection URL.
        table: Target table name.
        user: Database username.
        password: Database password.
        mode: Write mode - "append", "overwrite", "ignore", "error".
        driver: JDBC driver class name.
    """
    (
        df.write
        .format("jdbc")
        .option("url", jdbc_url)
        .option("dbtable", table)
        .option("user", user)
        .option("password", password)
        .option("driver", driver)
        .mode(mode)
        .save()
    )
