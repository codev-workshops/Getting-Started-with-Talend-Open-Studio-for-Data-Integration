"""Output comparison utilities for validating PySpark output against Talend baselines."""
import os
from typing import List, Optional


class OutputMismatchError(Exception):
    """Raised when output files do not match."""
    pass


def compare_csv_files(
    expected_path: str,
    actual_path: str,
    sep: str = ";",
    sort: bool = True,
    ignore_trailing_whitespace: bool = True,
) -> dict:
    """Compare two CSV files line by line after optional sorting.

    Args:
        expected_path: Path to the Talend baseline output file.
        actual_path: Path to the PySpark output file.
        sep: Delimiter (used for context in error messages).
        sort: Whether to sort lines before comparing.
        ignore_trailing_whitespace: Strip trailing whitespace from each line.

    Returns:
        Dict with keys: match (bool), expected_lines (int), actual_lines (int),
        mismatched_lines (list of tuples), missing_lines (list), extra_lines (list).
    """
    def _read_lines(path):
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        if ignore_trailing_whitespace:
            lines = [line.rstrip() for line in lines]
        # Remove empty trailing lines
        while lines and lines[-1] == "":
            lines.pop()
        return lines

    expected_lines = _read_lines(expected_path)
    actual_lines = _read_lines(actual_path)

    if sort:
        expected_lines = sorted(expected_lines)
        actual_lines = sorted(actual_lines)

    result = {
        "match": True,
        "expected_line_count": len(expected_lines),
        "actual_line_count": len(actual_lines),
        "mismatched_lines": [],
        "missing_lines": [],
        "extra_lines": [],
    }

    expected_set = set(expected_lines)
    actual_set = set(actual_lines)

    result["missing_lines"] = sorted(expected_set - actual_set)
    result["extra_lines"] = sorted(actual_set - expected_set)

    # Line-by-line comparison on sorted
    max_lines = max(len(expected_lines), len(actual_lines))
    for i in range(max_lines):
        exp = expected_lines[i] if i < len(expected_lines) else "<MISSING>"
        act = actual_lines[i] if i < len(actual_lines) else "<MISSING>"
        if exp != act:
            result["mismatched_lines"].append((i + 1, exp, act))

    if result["missing_lines"] or result["extra_lines"] or result["mismatched_lines"]:
        result["match"] = False

    return result


def assert_outputs_match(
    expected_path: str,
    actual_path: str,
    sep: str = ";",
    sort: bool = True,
) -> None:
    """Assert that two CSV files are identical (after optional sorting).

    Raises:
        OutputMismatchError with detailed diff info.
    """
    result = compare_csv_files(expected_path, actual_path, sep=sep, sort=sort)
    if not result["match"]:
        msg_parts = [
            f"Output mismatch: expected {result['expected_line_count']} lines, "
            f"got {result['actual_line_count']}",
        ]
        if result["missing_lines"]:
            msg_parts.append(f"Missing {len(result['missing_lines'])} lines (in expected, not in actual)")
            for line in result["missing_lines"][:5]:
                msg_parts.append(f"  - {line}")
        if result["extra_lines"]:
            msg_parts.append(f"Extra {len(result['extra_lines'])} lines (in actual, not in expected)")
            for line in result["extra_lines"][:5]:
                msg_parts.append(f"  + {line}")
        raise OutputMismatchError("\n".join(msg_parts))


def find_single_csv_in_dir(directory: str) -> str:
    """Find the single CSV part file in a Spark output directory.

    Spark writes output as part-*.csv files inside a directory. This helper
    locates the single part file for comparison.

    Args:
        directory: Spark output directory path.

    Returns:
        Full path to the part file.

    Raises:
        FileNotFoundError: If no part file found.
        ValueError: If multiple part files found.
    """
    part_files = [
        f for f in os.listdir(directory)
        if f.startswith("part-") and f.endswith(".csv")
    ]
    if len(part_files) == 0:
        raise FileNotFoundError(f"No part-*.csv files in {directory}")
    if len(part_files) > 1:
        raise ValueError(
            f"Multiple part files found in {directory}: {part_files}. "
            "Ensure the DataFrame was coalesced to 1 partition."
        )
    return os.path.join(directory, part_files[0])
