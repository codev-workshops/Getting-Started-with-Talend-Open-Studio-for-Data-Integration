"""Schemas for Chapter 5 FindAndReplace job."""
from pyspark.sql.types import StructType, StructField, StringType

# Input and output schema: country-codes.csv (sep=";")
COUNTRY_CODES_SCHEMA = StructType([
    StructField("country_code", StringType(), nullable=True),
])
