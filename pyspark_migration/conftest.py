import pytest
from datetime import date, datetime

from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType, StructField, IntegerType, StringType,
    FloatType, TimestampType
)

# ---------------------------------------------------------------------------
# Schema constants – mirror the Talend source table definitions
# ---------------------------------------------------------------------------

ORDER_LINES_SCHEMA = StructType([
    StructField("id", IntegerType(), nullable=False),
    StructField("order_id", IntegerType(), nullable=False),
    StructField("product_id", IntegerType(), nullable=False),
    StructField("quantity", IntegerType(), nullable=False),
])

ORDERS_SCHEMA = StructType([
    StructField("id", IntegerType(), nullable=False),
    StructField("order_date", TimestampType(), nullable=False),
    StructField("order_value", FloatType(), nullable=False),
    StructField("order_status", StringType(), nullable=False),
])

PRODUCTS_SCHEMA = StructType([
    StructField("product_id", IntegerType(), nullable=False),
    StructField("product_name", StringType(), nullable=True),
    StructField("price", FloatType(), nullable=True),
])

BRANDS_SCHEMA = StructType([
    StructField("id", IntegerType(), nullable=False),
    StructField("product_id", IntegerType(), nullable=False),
    StructField("brand", StringType(), nullable=False),
])

OUTPUT_SCHEMA = StructType([
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

# ---------------------------------------------------------------------------
# Session-scoped Spark fixture
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def spark():
    spark = (
        SparkSession.builder
        .master("local[*]")
        .appName("DB2DB_Test")
        .getOrCreate()
    )
    yield spark
    spark.stop()

# ---------------------------------------------------------------------------
# Helper factories for creating typed DataFrames
# ---------------------------------------------------------------------------

def create_order_lines(spark, data):
    return spark.createDataFrame(data, ORDER_LINES_SCHEMA)


def create_orders(spark, data):
    return spark.createDataFrame(data, ORDERS_SCHEMA)


def create_products(spark, data):
    return spark.createDataFrame(data, PRODUCTS_SCHEMA)


def create_brands(spark, data):
    return spark.createDataFrame(data, BRANDS_SCHEMA)
