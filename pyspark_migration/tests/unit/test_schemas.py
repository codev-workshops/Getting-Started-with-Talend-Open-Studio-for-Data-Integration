"""Unit tests for schema definitions - verify all schemas are valid StructTypes with correct fields."""
import pytest
from pyspark.sql.types import StructType, StringType, IntegerType, FloatType, DecimalType, TimestampType


class TestCh5FilteringSchemas:
    def test_currencies_schema(self):
        from schemas.ch5_filtering import CURRENCIES_SCHEMA
        assert isinstance(CURRENCIES_SCHEMA, StructType)
        assert len(CURRENCIES_SCHEMA.fields) == 2
        assert CURRENCIES_SCHEMA["country"].dataType == StringType()
        assert CURRENCIES_SCHEMA["currency"].dataType == StringType()

    def test_currencies_reject_schema(self):
        from schemas.ch5_filtering import CURRENCIES_REJECT_SCHEMA
        assert isinstance(CURRENCIES_REJECT_SCHEMA, StructType)
        assert len(CURRENCIES_REJECT_SCHEMA.fields) == 3
        assert "errorMessage" in [f.name for f in CURRENCIES_REJECT_SCHEMA.fields]


class TestCh5AggregatingSchemas:
    def test_invoices_input_schema(self):
        from schemas.ch5_aggregating import INVOICES_INPUT_SCHEMA
        assert isinstance(INVOICES_INPUT_SCHEMA, StructType)
        assert len(INVOICES_INPUT_SCHEMA.fields) == 3
        assert INVOICES_INPUT_SCHEMA["invoice_number"].dataType == IntegerType()
        assert isinstance(INVOICES_INPUT_SCHEMA["invoice_value"].dataType, DecimalType)

    def test_invoices_aggregated_schema(self):
        from schemas.ch5_aggregating import INVOICES_AGGREGATED_SCHEMA
        assert len(INVOICES_AGGREGATED_SCHEMA.fields) == 2
        assert INVOICES_AGGREGATED_SCHEMA["customer_name_out"].dataType == StringType()


class TestCh5NormalizeSchemas:
    def test_normalize_schemas(self):
        from schemas.ch5_normalize import NORMALIZE_INPUT_SCHEMA, NORMALIZE_OUTPUT_SCHEMA
        assert len(NORMALIZE_INPUT_SCHEMA.fields) == 2
        assert len(NORMALIZE_OUTPUT_SCHEMA.fields) == 2


class TestCh5DenormalizeSchemas:
    def test_denormalize_schemas(self):
        from schemas.ch5_denormalize import DENORMALIZE_INPUT_SCHEMA, DENORMALIZE_OUTPUT_SCHEMA
        assert DENORMALIZE_INPUT_SCHEMA["product_id"].dataType == IntegerType()
        assert DENORMALIZE_OUTPUT_SCHEMA["category"].dataType == StringType()


class TestCh5ExtractDelimitedFieldsSchemas:
    def test_employees_schemas(self):
        from schemas.ch5_extract_delimited_fields import EMPLOYEES_INPUT_SCHEMA, EMPLOYEES_OUTPUT_SCHEMA
        assert len(EMPLOYEES_INPUT_SCHEMA.fields) == 2
        assert len(EMPLOYEES_OUTPUT_SCHEMA.fields) == 3
        assert "first_name" in [f.name for f in EMPLOYEES_OUTPUT_SCHEMA.fields]
        assert "last_name" in [f.name for f in EMPLOYEES_OUTPUT_SCHEMA.fields]


class TestCh5FindAndReplaceSchemas:
    def test_country_codes_schema(self):
        from schemas.ch5_find_and_replace import COUNTRY_CODES_SCHEMA
        assert len(COUNTRY_CODES_SCHEMA.fields) == 1
        assert COUNTRY_CODES_SCHEMA["country_code"].dataType == StringType()


class TestCh4DbSchemas:
    def test_products_schema(self):
        from schemas.ch4_db_extract import PRODUCTS_SCHEMA
        assert len(PRODUCTS_SCHEMA.fields) == 3
        assert PRODUCTS_SCHEMA["product_id"].dataType == IntegerType()
        assert PRODUCTS_SCHEMA["product_id"].nullable is False
        assert PRODUCTS_SCHEMA["price"].dataType == FloatType()

    def test_brands_schema(self):
        from schemas.ch4_db_extract import BRANDS_SCHEMA
        assert len(BRANDS_SCHEMA.fields) == 3


class TestCh4Db2dbSchemas:
    def test_order_data_schema(self):
        from schemas.ch4_db2db import ORDER_DATA_SCHEMA
        assert len(ORDER_DATA_SCHEMA.fields) == 10
        assert ORDER_DATA_SCHEMA["order_date"].dataType == TimestampType()
        assert ORDER_DATA_SCHEMA["extended_price"].dataType == FloatType()
        assert ORDER_DATA_SCHEMA["order_id"].nullable is False


class TestCh3ExpressionsSchemas:
    def test_expressions_input_schema(self):
        from schemas.ch3_expressions import EXPRESSIONS_INPUT_SCHEMA
        assert len(EXPRESSIONS_INPUT_SCHEMA.fields) == 9
        assert EXPRESSIONS_INPUT_SCHEMA["CustomerID"].dataType == IntegerType()

    def test_expressions_output_schema(self):
        from schemas.ch3_expressions import EXPRESSIONS_OUTPUT_SCHEMA
        assert len(EXPRESSIONS_OUTPUT_SCHEMA.fields) == 5
        assert EXPRESSIONS_OUTPUT_SCHEMA["telephone_number"].dataType == StringType()


class TestTypeMappingRegistry:
    def test_all_expected_types_present(self):
        from schemas.type_mapping import TALEND_TYPE_MAP
        assert "id_String" in TALEND_TYPE_MAP
        assert "id_Integer" in TALEND_TYPE_MAP
        assert "id_Float" in TALEND_TYPE_MAP
        assert "id_BigDecimal" in TALEND_TYPE_MAP
        assert "id_Date" in TALEND_TYPE_MAP

    def test_type_mapping_returns_pyspark_types(self):
        from schemas.type_mapping import TALEND_TYPE_MAP
        assert TALEND_TYPE_MAP["id_String"] == StringType()
        assert TALEND_TYPE_MAP["id_Integer"] == IntegerType()
        assert TALEND_TYPE_MAP["id_Float"] == FloatType()
        assert TALEND_TYPE_MAP["id_Date"] == TimestampType()
