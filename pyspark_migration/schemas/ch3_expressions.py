"""Schemas for Chapter 3 Expressions job."""
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

# Input schema: expressions.csv (sep=";", header=True)
EXPRESSIONS_INPUT_SCHEMA = StructType([
    StructField("CustomerID", IntegerType(), nullable=False),
    StructField("FirstName", StringType(), nullable=True),
    StructField("LastName", StringType(), nullable=True),
    StructField("Address1", StringType(), nullable=True),
    StructField("Address2", StringType(), nullable=True),
    StructField("TownCity", StringType(), nullable=True),
    StructField("County", StringType(), nullable=True),
    StructField("Postcode", StringType(), nullable=True),
    StructField("Telephone", StringType(), nullable=True),
])

# Output schema: after tMap expression transformations
EXPRESSIONS_OUTPUT_SCHEMA = StructType([
    StructField("id", StringType(), nullable=True),
    StructField("name", StringType(), nullable=True),
    StructField("address_1", StringType(), nullable=True),
    StructField("address_2", StringType(), nullable=True),
    StructField("telephone_number", StringType(), nullable=True),
])
