"""Schemas for Chapter 4 DB jobs."""
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType

# products table schema
PRODUCTS_SCHEMA = StructType([
    StructField("product_id", IntegerType(), nullable=False),
    StructField("product_name", StringType(), nullable=True),
    StructField("price", FloatType(), nullable=True),
])

# brands table schema
BRANDS_SCHEMA = StructType([
    StructField("id", IntegerType(), nullable=False),
    StructField("product_id", IntegerType(), nullable=False),
    StructField("brand", StringType(), nullable=False),
])
