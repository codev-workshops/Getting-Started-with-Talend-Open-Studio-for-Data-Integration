"""Unit tests for utils/schema_validator.py."""
import pytest
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType, FloatType,
)


class TestAssertSchemaEqual:
    """Tests for schema_validator.assert_schema_equal."""

    def test_matching_schema_passes(self, spark):
        """Verify no error when schemas match exactly."""
        from utils.schema_validator import assert_schema_equal

        schema = StructType([
            StructField("name", StringType(), True),
            StructField("age", IntegerType(), True),
        ])
        df = spark.createDataFrame([("Alice", 30)], schema=schema)
        assert_schema_equal(df, schema)  # Should not raise

    def test_column_count_mismatch(self, spark):
        """Verify error on column count mismatch."""
        from utils.schema_validator import assert_schema_equal, SchemaValidationError

        df = spark.createDataFrame([("Alice", 30)], ["name", "age"])
        expected = StructType([StructField("name", StringType(), True)])
        with pytest.raises(SchemaValidationError, match="Column count mismatch"):
            assert_schema_equal(df, expected)

    def test_missing_column(self, spark):
        """Verify error when expected column is missing."""
        from utils.schema_validator import assert_schema_equal, SchemaValidationError

        df = spark.createDataFrame([("Alice",)], ["name"])
        expected = StructType([
            StructField("name", StringType(), True),
            StructField("age", IntegerType(), True),
        ])
        with pytest.raises(SchemaValidationError, match="Missing column.*age"):
            assert_schema_equal(df, expected)

    def test_extra_column(self, spark):
        """Verify error when DataFrame has unexpected column."""
        from utils.schema_validator import assert_schema_equal, SchemaValidationError

        df = spark.createDataFrame([("Alice", 30, "extra")], ["name", "age", "bonus"])
        expected = StructType([
            StructField("name", StringType(), True),
            StructField("age", IntegerType(), True),
        ])
        with pytest.raises(SchemaValidationError, match="Unexpected column.*bonus"):
            assert_schema_equal(df, expected)

    def test_type_mismatch(self, spark):
        """Verify error when column types don't match."""
        from utils.schema_validator import assert_schema_equal, SchemaValidationError

        schema = StructType([
            StructField("name", StringType(), True),
            StructField("age", StringType(), True),  # String, not Integer
        ])
        df = spark.createDataFrame([("Alice", "30")], schema=schema)
        expected = StructType([
            StructField("name", StringType(), True),
            StructField("age", IntegerType(), True),
        ])
        with pytest.raises(SchemaValidationError, match="type mismatch"):
            assert_schema_equal(df, expected)

    def test_nullability_mismatch(self, spark):
        """Verify error when nullability doesn't match."""
        from utils.schema_validator import assert_schema_equal, SchemaValidationError

        schema = StructType([
            StructField("name", StringType(), True),
        ])
        df = spark.createDataFrame([("Alice",)], schema=schema)
        expected = StructType([
            StructField("name", StringType(), False),  # not nullable
        ])
        with pytest.raises(SchemaValidationError, match="nullability mismatch"):
            assert_schema_equal(df, expected)

    def test_nullability_check_disabled(self, spark):
        """Verify nullability is skipped when check_nullability=False."""
        from utils.schema_validator import assert_schema_equal

        schema = StructType([StructField("name", StringType(), True)])
        df = spark.createDataFrame([("Alice",)], schema=schema)
        expected = StructType([StructField("name", StringType(), False)])
        assert_schema_equal(df, expected, check_nullability=False)  # Should not raise

    def test_column_order_mismatch(self, spark):
        """Verify error when column order differs."""
        from utils.schema_validator import assert_schema_equal, SchemaValidationError

        schema = StructType([
            StructField("age", IntegerType(), True),
            StructField("name", StringType(), True),
        ])
        df = spark.createDataFrame([(30, "Alice")], schema=schema)
        expected = StructType([
            StructField("name", StringType(), True),
            StructField("age", IntegerType(), True),
        ])
        with pytest.raises(SchemaValidationError, match="order mismatch"):
            assert_schema_equal(df, expected)


class TestGetSchemaDiff:
    """Tests for schema_validator.get_schema_diff."""

    def test_identical_schemas(self):
        """Verify empty diff for matching schemas."""
        from utils.schema_validator import get_schema_diff

        schema = StructType([StructField("name", StringType(), True)])
        result = get_schema_diff(schema, schema)
        assert result["missing_columns"] == []
        assert result["extra_columns"] == []
        assert result["type_mismatches"] == {}
        assert result["nullability_mismatches"] == {}

    def test_diff_with_missing_and_extra(self):
        """Verify diff detects missing and extra columns."""
        from utils.schema_validator import get_schema_diff

        actual = StructType([
            StructField("name", StringType(), True),
            StructField("bonus", StringType(), True),
        ])
        expected = StructType([
            StructField("name", StringType(), True),
            StructField("age", IntegerType(), True),
        ])
        result = get_schema_diff(actual, expected)
        assert "age" in result["missing_columns"]
        assert "bonus" in result["extra_columns"]
