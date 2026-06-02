"""Schemas for Chapter 5 ExtractDelimitedFields job."""
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

# Input schema: employees.csv (sep="|")
EMPLOYEES_INPUT_SCHEMA = StructType([
    StructField("employee_id", IntegerType(), nullable=True),
    StructField("name", StringType(), nullable=True),
])

# Output schema: after splitting name by ","
EMPLOYEES_OUTPUT_SCHEMA = StructType([
    StructField("employee_id", IntegerType(), nullable=True),
    StructField("first_name", StringType(), nullable=True),
    StructField("last_name", StringType(), nullable=True),
])
