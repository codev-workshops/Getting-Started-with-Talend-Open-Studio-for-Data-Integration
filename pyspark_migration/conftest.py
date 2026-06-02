"""Shared pytest fixtures for PySpark migration tests."""
import os
import pytest
from pyspark.sql import SparkSession


@pytest.fixture(scope="session")
def spark():
    """Create a session-scoped SparkSession for testing."""
    session = (
        SparkSession.builder
        .master("local[*]")
        .appName("pyspark_migration_tests")
        .config("spark.sql.shuffle.partitions", "2")
        .config("spark.default.parallelism", "2")
        .config("spark.ui.enabled", "false")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .getOrCreate()
    )
    yield session
    session.stop()


@pytest.fixture(scope="session")
def fixtures_dir():
    """Return the absolute path to the fixtures directory."""
    return os.path.join(os.path.dirname(__file__), "fixtures")
