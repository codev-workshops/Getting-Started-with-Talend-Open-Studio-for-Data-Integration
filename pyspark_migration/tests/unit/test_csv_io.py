"""Unit tests for utils/csv_io.py."""
import os
import tempfile
import pytest
from pyspark.sql.types import StructType, StructField, StringType, IntegerType


class TestReadCsv:
    """Tests for csv_io.read_csv."""

    def test_read_csv_with_semicolon_separator(self, spark, tmp_path):
        """Verify reading a semicolon-separated CSV produces correct DataFrame."""
        csv_content = "Denmark;DKK\nAustria;EUR\n"
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        from utils.csv_io import read_csv
        schema = StructType([
            StructField("country", StringType(), True),
            StructField("currency", StringType(), True),
        ])
        df = read_csv(spark, str(csv_file), sep=";", header=False, schema=schema)
        assert df.count() == 2
        assert df.columns == ["country", "currency"]
        rows = df.collect()
        assert rows[0]["country"] == "Denmark"
        assert rows[0]["currency"] == "DKK"

    def test_read_csv_with_pipe_separator(self, spark, tmp_path):
        """Verify reading a pipe-separated CSV."""
        csv_content = "123|dresses;summer\n456|tops\n"
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        from utils.csv_io import read_csv
        schema = StructType([
            StructField("id", StringType(), True),
            StructField("cats", StringType(), True),
        ])
        df = read_csv(spark, str(csv_file), sep="|", header=False, schema=schema)
        assert df.count() == 2
        assert df.collect()[0]["cats"] == "dresses;summer"

    def test_read_csv_with_header(self, spark, tmp_path):
        """Verify reading a CSV with header row."""
        csv_content = "name;value\nAlpha;100\nBeta;200\n"
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        from utils.csv_io import read_csv
        df = read_csv(spark, str(csv_file), sep=";", header=True)
        assert df.columns == ["name", "value"]
        assert df.count() == 2

    def test_read_csv_with_explicit_schema(self, spark, tmp_path):
        """Verify schema is enforced on read."""
        csv_content = "1;Alpha\n2;Beta\n"
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)

        from utils.csv_io import read_csv
        schema = StructType([
            StructField("id", IntegerType(), True),
            StructField("name", StringType(), True),
        ])
        df = read_csv(spark, str(csv_file), sep=";", schema=schema)
        assert df.schema == schema
        assert df.collect()[0]["id"] == 1

    def test_read_csv_empty_file(self, spark, tmp_path):
        """Verify reading empty CSV returns empty DataFrame."""
        csv_file = tmp_path / "empty.csv"
        csv_file.write_text("")

        from utils.csv_io import read_csv
        schema = StructType([
            StructField("col1", StringType(), True),
        ])
        df = read_csv(spark, str(csv_file), sep=";", schema=schema)
        assert df.count() == 0


class TestWriteCsv:
    """Tests for csv_io.write_csv."""

    def test_write_csv_semicolon_separator(self, spark, tmp_path):
        """Verify writing with semicolon separator."""
        from utils.csv_io import read_csv, write_csv
        from utils.diff_comparator import find_single_csv_in_dir

        df = spark.createDataFrame(
            [("Denmark", "DKK"), ("Austria", "EUR")],
            ["country", "currency"],
        )
        out_dir = str(tmp_path / "out")
        write_csv(df, out_dir, sep=";", header=False, single_file=True)

        part_file = find_single_csv_in_dir(out_dir)
        with open(part_file) as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
        assert len(lines) == 2
        assert ";" in lines[0]

    def test_write_csv_with_header(self, spark, tmp_path):
        """Verify header row is written when header=True."""
        from utils.csv_io import write_csv
        from utils.diff_comparator import find_single_csv_in_dir

        df = spark.createDataFrame([("A", 1)], ["name", "value"])
        out_dir = str(tmp_path / "out")
        write_csv(df, out_dir, sep=";", header=True, single_file=True)

        part_file = find_single_csv_in_dir(out_dir)
        with open(part_file) as f:
            first_line = f.readline().strip()
        assert first_line == "name;value"

    def test_write_csv_single_file_produces_one_part(self, spark, tmp_path):
        """Verify single_file=True produces exactly one part file."""
        from utils.csv_io import write_csv

        df = spark.createDataFrame([(i,) for i in range(100)], ["val"])
        out_dir = str(tmp_path / "out")
        write_csv(df, out_dir, sep=",", single_file=True)

        part_files = [f for f in os.listdir(out_dir) if f.startswith("part-")]
        assert len(part_files) == 1
