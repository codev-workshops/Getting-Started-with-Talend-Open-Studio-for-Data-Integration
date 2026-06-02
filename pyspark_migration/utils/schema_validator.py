"""Schema validation utilities to ensure DataFrame schemas match Talend metadata contracts."""
from pyspark.sql import DataFrame
from pyspark.sql.types import StructType, StructField


class SchemaValidationError(Exception):
    """Raised when a DataFrame schema does not match the expected schema."""
    pass


def assert_schema_equal(
    df: DataFrame,
    expected_schema: StructType,
    check_nullability: bool = True,
) -> None:
    """Assert that a DataFrame's schema matches the expected StructType exactly.

    Args:
        df: DataFrame to validate.
        expected_schema: Expected StructType.
        check_nullability: Whether to compare nullable flags.

    Raises:
        SchemaValidationError: If schemas do not match.
    """
    actual = df.schema
    errors = []

    # Check column count
    if len(actual.fields) != len(expected_schema.fields):
        errors.append(
            f"Column count mismatch: actual={len(actual.fields)}, "
            f"expected={len(expected_schema.fields)}"
        )

    # Check each field
    expected_map = {f.name: f for f in expected_schema.fields}
    actual_map = {f.name: f for f in actual.fields}

    # Check for missing columns
    for name in expected_map:
        if name not in actual_map:
            errors.append(f"Missing column: '{name}'")

    # Check for extra columns
    for name in actual_map:
        if name not in expected_map:
            errors.append(f"Unexpected column: '{name}'")

    # Check matching columns for type and nullability
    for name in expected_map:
        if name in actual_map:
            exp_field = expected_map[name]
            act_field = actual_map[name]
            if act_field.dataType != exp_field.dataType:
                errors.append(
                    f"Column '{name}' type mismatch: "
                    f"actual={act_field.dataType}, expected={exp_field.dataType}"
                )
            if check_nullability and act_field.nullable != exp_field.nullable:
                errors.append(
                    f"Column '{name}' nullability mismatch: "
                    f"actual={act_field.nullable}, expected={exp_field.nullable}"
                )

    # Check column order
    if not errors:
        actual_names = [f.name for f in actual.fields]
        expected_names = [f.name for f in expected_schema.fields]
        if actual_names != expected_names:
            errors.append(
                f"Column order mismatch: actual={actual_names}, expected={expected_names}"
            )

    if errors:
        raise SchemaValidationError(
            "Schema validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
        )


def get_schema_diff(
    actual_schema: StructType,
    expected_schema: StructType,
) -> dict:
    """Return a dict describing differences between two schemas.

    Returns:
        Dict with keys: missing_columns, extra_columns, type_mismatches, nullability_mismatches.
    """
    expected_map = {f.name: f for f in expected_schema.fields}
    actual_map = {f.name: f for f in actual_schema.fields}

    return {
        "missing_columns": [n for n in expected_map if n not in actual_map],
        "extra_columns": [n for n in actual_map if n not in expected_map],
        "type_mismatches": {
            n: {"actual": str(actual_map[n].dataType), "expected": str(expected_map[n].dataType)}
            for n in expected_map
            if n in actual_map and actual_map[n].dataType != expected_map[n].dataType
        },
        "nullability_mismatches": {
            n: {"actual": actual_map[n].nullable, "expected": expected_map[n].nullable}
            for n in expected_map
            if n in actual_map and actual_map[n].nullable != expected_map[n].nullable
        },
    }
