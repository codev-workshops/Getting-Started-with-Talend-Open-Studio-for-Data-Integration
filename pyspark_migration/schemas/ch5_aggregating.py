"""Schemas for Chapter 5 Aggregating job."""
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DecimalType

# Input schema: invoices.csv (sep=";")
INVOICES_INPUT_SCHEMA = StructType([
    StructField("invoice_number", IntegerType(), nullable=True),
    StructField("customer_name", StringType(), nullable=True),
    StructField("invoice_value", DecimalType(8, 2), nullable=True),
])

# Output schema: aggregated by customer
INVOICES_AGGREGATED_SCHEMA = StructType([
    StructField("customer_name_out", StringType(), nullable=True),
    StructField("total_invoiced_value", DecimalType(8, 2), nullable=True),
])
