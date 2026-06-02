"""Unit tests for utils/diff_comparator.py."""
import os
import pytest


class TestCompareCsvFiles:
    """Tests for diff_comparator.compare_csv_files."""

    def test_identical_files(self, tmp_path):
        """Verify match=True for identical files."""
        from utils.diff_comparator import compare_csv_files

        content = "a;1\nb;2\nc;3\n"
        f1 = tmp_path / "f1.csv"
        f2 = tmp_path / "f2.csv"
        f1.write_text(content)
        f2.write_text(content)

        result = compare_csv_files(str(f1), str(f2))
        assert result["match"] is True
        assert result["expected_line_count"] == 3
        assert result["actual_line_count"] == 3

    def test_different_files(self, tmp_path):
        """Verify match=False for different files."""
        from utils.diff_comparator import compare_csv_files

        f1 = tmp_path / "f1.csv"
        f2 = tmp_path / "f2.csv"
        f1.write_text("a;1\nb;2\n")
        f2.write_text("a;1\nc;3\n")

        result = compare_csv_files(str(f1), str(f2))
        assert result["match"] is False
        assert len(result["missing_lines"]) > 0

    def test_different_line_counts(self, tmp_path):
        """Verify mismatch when line counts differ."""
        from utils.diff_comparator import compare_csv_files

        f1 = tmp_path / "f1.csv"
        f2 = tmp_path / "f2.csv"
        f1.write_text("a;1\nb;2\n")
        f2.write_text("a;1\n")

        result = compare_csv_files(str(f1), str(f2))
        assert result["match"] is False
        assert result["expected_line_count"] == 2
        assert result["actual_line_count"] == 1

    def test_sorted_comparison(self, tmp_path):
        """Verify sorted comparison matches regardless of line order."""
        from utils.diff_comparator import compare_csv_files

        f1 = tmp_path / "f1.csv"
        f2 = tmp_path / "f2.csv"
        f1.write_text("a;1\nb;2\n")
        f2.write_text("b;2\na;1\n")

        result = compare_csv_files(str(f1), str(f2), sort=True)
        assert result["match"] is True

    def test_unsorted_comparison_detects_order(self, tmp_path):
        """Verify unsorted comparison detects order differences."""
        from utils.diff_comparator import compare_csv_files

        f1 = tmp_path / "f1.csv"
        f2 = tmp_path / "f2.csv"
        f1.write_text("a;1\nb;2\n")
        f2.write_text("b;2\na;1\n")

        result = compare_csv_files(str(f1), str(f2), sort=False)
        assert result["match"] is False


class TestAssertOutputsMatch:
    """Tests for diff_comparator.assert_outputs_match."""

    def test_matching_outputs_pass(self, tmp_path):
        """Verify no exception for matching files."""
        from utils.diff_comparator import assert_outputs_match

        content = "x;1\ny;2\n"
        f1 = tmp_path / "f1.csv"
        f2 = tmp_path / "f2.csv"
        f1.write_text(content)
        f2.write_text(content)

        assert_outputs_match(str(f1), str(f2))  # Should not raise

    def test_mismatched_outputs_raise(self, tmp_path):
        """Verify OutputMismatchError for different files."""
        from utils.diff_comparator import assert_outputs_match, OutputMismatchError

        f1 = tmp_path / "f1.csv"
        f2 = tmp_path / "f2.csv"
        f1.write_text("x;1\n")
        f2.write_text("y;2\n")

        with pytest.raises(OutputMismatchError):
            assert_outputs_match(str(f1), str(f2))


class TestFindSingleCsvInDir:
    """Tests for diff_comparator.find_single_csv_in_dir."""

    def test_finds_single_part_file(self, tmp_path):
        """Verify it finds the single part file."""
        from utils.diff_comparator import find_single_csv_in_dir

        (tmp_path / "part-00000-abc.csv").write_text("data")
        (tmp_path / "_SUCCESS").write_text("")

        result = find_single_csv_in_dir(str(tmp_path))
        assert "part-00000-abc.csv" in result

    def test_raises_on_no_part_file(self, tmp_path):
        """Verify FileNotFoundError when no part file exists."""
        from utils.diff_comparator import find_single_csv_in_dir

        (tmp_path / "_SUCCESS").write_text("")
        with pytest.raises(FileNotFoundError):
            find_single_csv_in_dir(str(tmp_path))

    def test_raises_on_multiple_part_files(self, tmp_path):
        """Verify ValueError when multiple part files exist."""
        from utils.diff_comparator import find_single_csv_in_dir

        (tmp_path / "part-00000.csv").write_text("data1")
        (tmp_path / "part-00001.csv").write_text("data2")
        with pytest.raises(ValueError, match="Multiple part files"):
            find_single_csv_in_dir(str(tmp_path))
