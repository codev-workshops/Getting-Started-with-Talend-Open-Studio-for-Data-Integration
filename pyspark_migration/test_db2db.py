import pytest
from datetime import datetime

from pyspark.sql import functions as F

from db2db_job import transform
from conftest import (
    create_order_lines, create_orders, create_products, create_brands,
    ORDER_LINES_SCHEMA, ORDERS_SCHEMA, PRODUCTS_SCHEMA, BRANDS_SCHEMA,
)

# ---------------------------------------------------------------------------
# Shared test-data constants
# ---------------------------------------------------------------------------

_DT1 = datetime(2024, 1, 15, 10, 30, 0)
_DT2 = datetime(2024, 2, 20, 14, 0, 0)
_DT3 = datetime(2024, 3, 5, 9, 0, 0)
_DT_MIN = datetime(1970, 1, 1, 0, 0, 0)
_DT_FUTURE = datetime(2099, 12, 31, 23, 59, 59)

# ---------------------------------------------------------------------------
# Happy-path data builders
# ---------------------------------------------------------------------------

def _happy_order_lines(spark):
    return create_order_lines(spark, [
        (1, 100, 10, 2),
        (2, 100, 11, 1),
        (3, 101, 10, 5),
        (4, 102, 12, 3),
        (5, 101, 12, 1),
    ])


def _happy_orders(spark):
    return create_orders(spark, [
        (100, _DT1, 150.0, "shipped"),
        (101, _DT2, 300.0, "pending"),
        (102, _DT3, 75.0, "delivered"),
    ])


def _happy_products(spark):
    return create_products(spark, [
        (10, "Widget A", 25.0),
        (11, "Widget B", 50.0),
        (12, "Gadget C", 15.0),
    ])


def _happy_brands(spark):
    return create_brands(spark, [
        (1, 10, "BrandX"),
        (2, 11, "BrandY"),
    ])


# ======================================================================
# Happy Path Tests
# ======================================================================

class TestHappyPath:

    def test_basic_join_all_matching(self, spark):
        """All order_lines have matching orders, products, and brands. Verify all 10 columns."""
        ol = create_order_lines(spark, [
            (1, 100, 10, 2),
            (2, 100, 11, 1),
        ])
        orders = create_orders(spark, [
            (100, _DT1, 150.0, "shipped"),
        ])
        products = create_products(spark, [
            (10, "Widget A", 25.0),
            (11, "Widget B", 50.0),
        ])
        brands = create_brands(spark, [
            (1, 10, "BrandX"),
            (2, 11, "BrandY"),
        ])

        result = transform(ol, orders, products, brands)
        rows = result.orderBy("line_id").collect()

        assert len(rows) == 2

        r0 = rows[0]
        assert r0["order_date"] == _DT1
        assert r0["order_id"] == 100
        assert r0["line_id"] == 1
        assert r0["order_status"] == "shipped"
        assert r0["product_id"] == 10
        assert r0["product_name"] == "Widget A"
        assert r0["brand"] == "BrandX"
        assert r0["unit_price"] == pytest.approx(25.0)
        assert r0["quantity"] == 2
        assert r0["extended_price"] == pytest.approx(50.0)

        r1 = rows[1]
        assert r1["line_id"] == 2
        assert r1["product_name"] == "Widget B"
        assert r1["brand"] == "BrandY"
        assert r1["unit_price"] == pytest.approx(50.0)
        assert r1["quantity"] == 1
        assert r1["extended_price"] == pytest.approx(50.0)

    def test_extended_price_calculation(self, spark):
        """Verify extended_price = quantity * price for multiple rows."""
        ol = _happy_order_lines(spark)
        orders = _happy_orders(spark)
        products = _happy_products(spark)
        brands = _happy_brands(spark)

        result = transform(ol, orders, products, brands)
        rows = {r["line_id"]: r for r in result.collect()}

        # line 1: qty=2, price=25 => 50
        assert rows[1]["extended_price"] == pytest.approx(50.0)
        # line 2: qty=1, price=50 => 50
        assert rows[2]["extended_price"] == pytest.approx(50.0)
        # line 3: qty=5, price=25 => 125
        assert rows[3]["extended_price"] == pytest.approx(125.0)
        # line 4: qty=3, price=15 => 45
        assert rows[4]["extended_price"] == pytest.approx(45.0)
        # line 5: qty=1, price=15 => 15
        assert rows[5]["extended_price"] == pytest.approx(15.0)

    def test_column_renaming(self, spark):
        """Verify order_lines.id -> line_id and products.price -> unit_price."""
        ol = create_order_lines(spark, [(1, 100, 10, 2)])
        orders = create_orders(spark, [(100, _DT1, 150.0, "shipped")])
        products = create_products(spark, [(10, "Widget A", 25.0)])
        brands = create_brands(spark, [(1, 10, "BrandX")])

        result = transform(ol, orders, products, brands)
        cols = result.columns
        assert "line_id" in cols
        assert "unit_price" in cols
        assert "id" not in cols
        assert "price" not in cols

        row = result.collect()[0]
        assert row["line_id"] == 1
        assert row["unit_price"] == pytest.approx(25.0)

    def test_output_schema(self, spark):
        """Verify the output DataFrame has exactly the 10 expected columns with correct types."""
        ol = _happy_order_lines(spark)
        orders = _happy_orders(spark)
        products = _happy_products(spark)
        brands = _happy_brands(spark)

        result = transform(ol, orders, products, brands)
        expected_cols = [
            "order_date", "order_id", "line_id", "order_status",
            "product_id", "product_name", "brand", "unit_price",
            "quantity", "extended_price",
        ]
        assert result.columns == expected_cols

    def test_multiple_order_lines_per_order(self, spark):
        """Multiple lines for one order should all appear in output."""
        ol = create_order_lines(spark, [
            (1, 100, 10, 1),
            (2, 100, 11, 2),
            (3, 100, 12, 3),
        ])
        orders = create_orders(spark, [(100, _DT1, 200.0, "shipped")])
        products = create_products(spark, [
            (10, "A", 10.0),
            (11, "B", 20.0),
            (12, "C", 30.0),
        ])
        brands = create_brands(spark, [(1, 10, "BX")])

        result = transform(ol, orders, products, brands)
        assert result.count() == 3
        order_ids = [r["order_id"] for r in result.collect()]
        assert all(oid == 100 for oid in order_ids)


# ======================================================================
# Edge-Case Tests
# ======================================================================

class TestEdgeCases:

    def test_no_matching_brand_left_join(self, spark):
        """order_line with matching order and product but no brand => brand is NULL."""
        ol = create_order_lines(spark, [(1, 100, 10, 2)])
        orders = create_orders(spark, [(100, _DT1, 50.0, "shipped")])
        products = create_products(spark, [(10, "Widget", 25.0)])
        brands = create_brands(spark, [])  # empty brands

        result = transform(ol, orders, products, brands)
        row = result.collect()[0]
        assert row["brand"] is None
        assert row["product_name"] == "Widget"
        assert row["extended_price"] == pytest.approx(50.0)

    def test_null_price_product(self, spark):
        """Product with price=NULL => unit_price=NULL, extended_price=NULL."""
        ol = create_order_lines(spark, [(1, 100, 10, 3)])
        orders = create_orders(spark, [(100, _DT1, 0.0, "pending")])
        products = create_products(spark, [(10, "NullPrice", None)])
        brands = create_brands(spark, [(1, 10, "BX")])

        result = transform(ol, orders, products, brands)
        row = result.collect()[0]
        assert row["unit_price"] is None
        assert row["extended_price"] is None

    def test_null_product_name(self, spark):
        """Product with product_name=NULL => product_name is NULL in output."""
        ol = create_order_lines(spark, [(1, 100, 10, 1)])
        orders = create_orders(spark, [(100, _DT1, 10.0, "shipped")])
        products = create_products(spark, [(10, None, 10.0)])
        brands = create_brands(spark, [(1, 10, "BX")])

        result = transform(ol, orders, products, brands)
        row = result.collect()[0]
        assert row["product_name"] is None
        assert row["unit_price"] == pytest.approx(10.0)

    def test_zero_quantity(self, spark):
        """quantity=0 => extended_price=0.0."""
        ol = create_order_lines(spark, [(1, 100, 10, 0)])
        orders = create_orders(spark, [(100, _DT1, 0.0, "shipped")])
        products = create_products(spark, [(10, "Widget", 25.0)])
        brands = create_brands(spark, [(1, 10, "BX")])

        result = transform(ol, orders, products, brands)
        row = result.collect()[0]
        assert row["quantity"] == 0
        assert row["extended_price"] == pytest.approx(0.0)

    def test_large_values(self, spark):
        """Large quantity and price values produce correct extended_price."""
        ol = create_order_lines(spark, [(1, 100, 10, 999999)])
        orders = create_orders(spark, [(100, _DT1, 0.0, "shipped")])
        products = create_products(spark, [(10, "Expensive", 99999.99)])
        brands = create_brands(spark, [(1, 10, "BX")])

        result = transform(ol, orders, products, brands)
        row = result.collect()[0]
        expected = 999999 * 99999.99
        assert row["extended_price"] == pytest.approx(expected, rel=1e-3)

    def test_duplicate_brands_unique_match(self, spark):
        """Multiple brands for same product_id.

        Talend uses UNIQUE_MATCH so it takes the first match.  The PySpark
        job deduplicates brands by product_id before joining so only one
        row per order_line is produced (matching Talend behaviour).
        """
        ol = create_order_lines(spark, [(1, 100, 10, 1)])
        orders = create_orders(spark, [(100, _DT1, 10.0, "shipped")])
        products = create_products(spark, [(10, "Widget", 10.0)])
        brands = create_brands(spark, [
            (1, 10, "BrandA"),
            (2, 10, "BrandB"),
            (3, 10, "BrandC"),
        ])

        result = transform(ol, orders, products, brands)
        assert result.count() == 1
        row = result.collect()[0]
        assert row["brand"] in ("BrandA", "BrandB", "BrandC")

    def test_all_empty_inputs(self, spark):
        """All four inputs empty => output is empty with correct schema."""
        ol = create_order_lines(spark, [])
        orders = create_orders(spark, [])
        products = create_products(spark, [])
        brands = create_brands(spark, [])

        result = transform(ol, orders, products, brands)
        assert result.count() == 0
        expected_cols = [
            "order_date", "order_id", "line_id", "order_status",
            "product_id", "product_name", "brand", "unit_price",
            "quantity", "extended_price",
        ]
        assert result.columns == expected_cols

    def test_order_date_edge_values(self, spark):
        """Boundary dates: 1970-01-01 and far future."""
        ol = create_order_lines(spark, [
            (1, 100, 10, 1),
            (2, 101, 10, 1),
        ])
        orders = create_orders(spark, [
            (100, _DT_MIN, 10.0, "old"),
            (101, _DT_FUTURE, 10.0, "future"),
        ])
        products = create_products(spark, [(10, "W", 5.0)])
        brands = create_brands(spark, [])

        result = transform(ol, orders, products, brands)
        rows = {r["order_id"]: r for r in result.collect()}
        assert rows[100]["order_date"] == _DT_MIN
        assert rows[101]["order_date"] == _DT_FUTURE


# ======================================================================
# Failure / Rejection Cases
# ======================================================================

class TestFailureCases:

    def test_no_matching_order_drops_row(self, spark):
        """order_line with order_id not in orders => row is dropped (inner join)."""
        ol = create_order_lines(spark, [(1, 999, 10, 1)])
        orders = create_orders(spark, [(100, _DT1, 10.0, "shipped")])
        products = create_products(spark, [(10, "W", 5.0)])
        brands = create_brands(spark, [(1, 10, "BX")])

        result = transform(ol, orders, products, brands)
        assert result.count() == 0

    def test_no_matching_product_drops_row(self, spark):
        """order_line with product_id not in products => row is dropped (inner join)."""
        ol = create_order_lines(spark, [(1, 100, 999, 1)])
        orders = create_orders(spark, [(100, _DT1, 10.0, "shipped")])
        products = create_products(spark, [(10, "W", 5.0)])
        brands = create_brands(spark, [(1, 10, "BX")])

        result = transform(ol, orders, products, brands)
        assert result.count() == 0

    def test_no_matching_order_and_product(self, spark):
        """order_line with neither matching order nor product => dropped."""
        ol = create_order_lines(spark, [(1, 999, 999, 1)])
        orders = create_orders(spark, [(100, _DT1, 10.0, "shipped")])
        products = create_products(spark, [(10, "W", 5.0)])
        brands = create_brands(spark, [(1, 10, "BX")])

        result = transform(ol, orders, products, brands)
        assert result.count() == 0

    def test_mixed_matching_and_nonmatching(self, spark):
        """Mix of matching and non-matching order_lines => only matching rows survive.

        Create 5 order_lines: 3 have valid order+product, 2 don't.
        Assert output has exactly 3 rows.
        """
        ol = create_order_lines(spark, [
            (1, 100, 10, 1),   # valid
            (2, 100, 11, 2),   # valid
            (3, 999, 10, 1),   # bad order_id
            (4, 100, 999, 1),  # bad product_id
            (5, 101, 12, 3),   # valid
        ])
        orders = create_orders(spark, [
            (100, _DT1, 100.0, "shipped"),
            (101, _DT2, 200.0, "pending"),
        ])
        products = create_products(spark, [
            (10, "A", 10.0),
            (11, "B", 20.0),
            (12, "C", 30.0),
        ])
        brands = create_brands(spark, [(1, 10, "BX")])

        result = transform(ol, orders, products, brands)
        assert result.count() == 3
        line_ids = sorted([r["line_id"] for r in result.collect()])
        assert line_ids == [1, 2, 5]
