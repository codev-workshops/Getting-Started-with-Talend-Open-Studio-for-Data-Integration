"""Unit tests for utils/db_io.py - tests function signatures and parameter handling.

Note: Actual JDBC integration requires a running MySQL instance and is covered
in integration tests. These unit tests verify the module loads and functions
have correct signatures.
"""
import pytest


class TestDbIoModule:
    """Tests for db_io module structure."""

    def test_module_imports(self):
        """Verify db_io module can be imported."""
        from utils.db_io import read_table, write_table, DEFAULT_JDBC_DRIVER
        assert callable(read_table)
        assert callable(write_table)
        assert DEFAULT_JDBC_DRIVER == "com.mysql.cj.jdbc.Driver"

    def test_read_table_signature(self):
        """Verify read_table has expected parameters."""
        import inspect
        from utils.db_io import read_table
        sig = inspect.signature(read_table)
        param_names = list(sig.parameters.keys())
        assert "spark" in param_names
        assert "jdbc_url" in param_names
        assert "table" in param_names
        assert "user" in param_names
        assert "password" in param_names
        assert "pushdown_query" in param_names

    def test_write_table_signature(self):
        """Verify write_table has expected parameters."""
        import inspect
        from utils.db_io import write_table
        sig = inspect.signature(write_table)
        param_names = list(sig.parameters.keys())
        assert "df" in param_names
        assert "jdbc_url" in param_names
        assert "table" in param_names
        assert "mode" in param_names
