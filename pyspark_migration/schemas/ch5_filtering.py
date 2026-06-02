"""Schemas for Chapter 5 Filtering jobs (Filtering1, Filtering2, Filtering3, Sorting)."""
from pyspark.sql.types import StructType, StructField, StringType

# Input and output schema for Filtering1, Filtering2, Filtering3, Sorting
# Source: Filtering1_0.1.item <metadata> - columns: country (String), currency (String)
CURRENCIES_SCHEMA = StructType([
    StructField("country", StringType(), nullable=True),
    StructField("currency", StringType(), nullable=True),
])

# Filtering2 reject output has an additional errorMessage column
CURRENCIES_REJECT_SCHEMA = StructType([
    StructField("country", StringType(), nullable=True),
    StructField("currency", StringType(), nullable=True),
    StructField("errorMessage", StringType(), nullable=True),
])
