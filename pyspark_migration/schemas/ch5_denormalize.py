"""Schemas for Chapter 5 Denormalize job."""
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

# Input schema: categories-to-denormalize.csv (sep=";")
DENORMALIZE_INPUT_SCHEMA = StructType([
    StructField("product_id", IntegerType(), nullable=True),
    StructField("category", StringType(), nullable=True),
])

# Output schema: after denormalize, semicolon-joined categories
DENORMALIZE_OUTPUT_SCHEMA = StructType([
    StructField("product_id", IntegerType(), nullable=True),
    StructField("category", StringType(), nullable=True),
])
