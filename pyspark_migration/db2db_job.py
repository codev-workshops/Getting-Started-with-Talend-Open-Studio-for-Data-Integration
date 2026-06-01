from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType, StructField, IntegerType, StringType,
    FloatType, DateType, TimestampType
)


def create_spark_session(app_name="DB2DB_Migration"):
    return SparkSession.builder.appName(app_name).getOrCreate()


def read_order_lines(spark, jdbc_url, properties):
    """Read order_lines table - columns: id, order_id, product_id, quantity (all INT)"""
    return spark.read.jdbc(jdbc_url, "order_lines", properties=properties) \
        .select("id", "order_id", "product_id", "quantity")


def read_orders(spark, jdbc_url, properties):
    """Read orders table - columns: id, order_date (DATETIME), order_value (FLOAT), order_status (VARCHAR)"""
    return spark.read.jdbc(jdbc_url, "orders", properties=properties) \
        .select("id", "order_date", "order_value", "order_status")


def read_products(spark, jdbc_url, properties):
    """Read products table - columns: product_id (INT), product_name (VARCHAR), price (FLOAT)"""
    return spark.read.jdbc(jdbc_url, "products", properties=properties) \
        .select("product_id", "product_name", "price")


def read_brands(spark, jdbc_url, properties):
    """Read brands table - columns: id (INT), product_id (INT), brand (VARCHAR)"""
    return spark.read.jdbc(jdbc_url, "brands", properties=properties) \
        .select("id", "product_id", "brand")


def deduplicate_brands(brands_df):
    """Replicate Talend UNIQUE_MATCH + LOAD_ONCE semantics.

    When there are duplicate keys in a lookup table, Talend only uses the
    first match.  ``dropDuplicates`` on the join key achieves the same
    one-row-per-key guarantee in Spark.
    """
    return brands_df.dropDuplicates(["product_id"])


def transform(order_lines_df, orders_df, products_df, brands_df):
    """Core transformation logic replicating the tMap_1 component.

    - INNER JOIN order_lines with orders on order_lines.order_id = orders.id
    - INNER JOIN with products on order_lines.product_id = products.product_id
    - LEFT JOIN with brands on products.product_id = brands.product_id
      (brands is deduplicated first to match Talend UNIQUE_MATCH)
    - Compute extended_price = quantity * price
    - Rename: order_lines.id -> line_id, products.price -> unit_price
    - Select final 10 columns
    """
    brands_deduped = deduplicate_brands(brands_df)

    joined = order_lines_df.join(
        orders_df,
        order_lines_df["order_id"] == orders_df["id"],
        "inner"
    )

    joined = joined.join(
        products_df,
        order_lines_df["product_id"] == products_df["product_id"],
        "inner"
    )

    joined = joined.join(
        brands_deduped,
        products_df["product_id"] == brands_deduped["product_id"],
        "left"
    )

    result = joined.select(
        orders_df["order_date"],
        order_lines_df["order_id"],
        order_lines_df["id"].alias("line_id"),
        orders_df["order_status"],
        order_lines_df["product_id"],
        products_df["product_name"],
        brands_deduped["brand"],
        products_df["price"].alias("unit_price"),
        order_lines_df["quantity"],
        (order_lines_df["quantity"] * products_df["price"]).alias("extended_price")
    )

    return result


def write_output(df, jdbc_url, properties, table="order_data", mode="append"):
    """Write to target table using INSERT (append mode).

    Talend used batch insert with commit every 10000 rows.
    """
    df.write.jdbc(jdbc_url, table, mode=mode, properties=properties)


def run(source_jdbc_url, target_jdbc_url, source_props, target_props):
    spark = create_spark_session()
    order_lines = read_order_lines(spark, source_jdbc_url, source_props)
    orders = read_orders(spark, source_jdbc_url, source_props)
    products = read_products(spark, source_jdbc_url, source_props)
    brands = read_brands(spark, source_jdbc_url, source_props)
    result = transform(order_lines, orders, products, brands)
    write_output(result, target_jdbc_url, target_props)
    spark.stop()
