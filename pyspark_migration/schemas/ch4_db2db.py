"""Schemas for Chapter 4 DB2DB job."""
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType, FloatType, TimestampType,
)

# Output schema: order_data table in db2db database
ORDER_DATA_SCHEMA = StructType([
    StructField("order_date", TimestampType(), nullable=True),
    StructField("order_id", IntegerType(), nullable=False),
    StructField("line_id", IntegerType(), nullable=False),
    StructField("order_status", StringType(), nullable=True),
    StructField("product_id", IntegerType(), nullable=True),
    StructField("product_name", StringType(), nullable=True),
    StructField("brand", StringType(), nullable=True),
    StructField("unit_price", FloatType(), nullable=True),
    StructField("quantity", IntegerType(), nullable=True),
    StructField("extended_price", FloatType(), nullable=True),
])
