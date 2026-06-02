"""Schemas for Chapter 5 Normalize job."""
from pyspark.sql.types import StructType, StructField, StringType

# Input schema: categories-to-normalise.csv (sep="|")
NORMALIZE_INPUT_SCHEMA = StructType([
    StructField("product_id", StringType(), nullable=True),
    StructField("categories", StringType(), nullable=True),
])

# Output schema: after explode, single category per row
NORMALIZE_OUTPUT_SCHEMA = StructType([
    StructField("product_id", StringType(), nullable=True),
    StructField("categories", StringType(), nullable=True),
])
