"""Schemas for Chapter 5 SampleRow job."""
from pyspark.sql.types import StructType, StructField, StringType

# Same as FindAndReplace - uses country-codes.csv
SAMPLE_ROW_SCHEMA = StructType([
    StructField("country_code", StringType(), nullable=True),
])
