"""Talend-to-PySpark type mapping reference.

Talend Type        -> PySpark Type
-----------------------------------------
id_String          -> StringType()
id_Integer         -> IntegerType()
id_Float           -> FloatType()
id_BigDecimal      -> DecimalType(precision, scale)
id_Date            -> TimestampType()
id_Boolean         -> BooleanType()
id_Long            -> LongType()
id_Short           -> ShortType()
id_Double          -> DoubleType()
"""
from pyspark.sql.types import (
    StringType, IntegerType, FloatType, DecimalType,
    TimestampType, BooleanType, LongType, ShortType, DoubleType,
)

TALEND_TYPE_MAP = {
    "id_String": StringType(),
    "id_Integer": IntegerType(),
    "id_Float": FloatType(),
    "id_BigDecimal": DecimalType(10, 2),  # default; override precision/scale per job
    "id_Date": TimestampType(),
    "id_Boolean": BooleanType(),
    "id_Long": LongType(),
    "id_Short": ShortType(),
    "id_Double": DoubleType(),
}
