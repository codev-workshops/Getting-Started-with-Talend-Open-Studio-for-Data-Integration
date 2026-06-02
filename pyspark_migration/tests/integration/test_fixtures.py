"""Integration tests - verify fixture files exist and are readable."""
import os
import yaml
import pytest


@pytest.fixture(scope="module")
def config():
    config_path = os.path.join(os.path.dirname(__file__), "..", "..", "config", "job_config.yaml")
    with open(config_path) as f:
        return yaml.safe_load(f)


class TestFixturesExist:
    """Verify that all fixture files referenced by job_config.yaml actually exist."""

    def test_fixtures_directory_exists(self, fixtures_dir):
        assert os.path.isdir(fixtures_dir), f"Fixtures directory not found: {fixtures_dir}"

    def test_chapter_directories_exist(self, fixtures_dir):
        expected_chapters = ["Chapter3", "Chapter4", "Chapter5", "Chapter6", "Chapter7"]
        for chapter in expected_chapters:
            chapter_dir = os.path.join(fixtures_dir, chapter)
            assert os.path.isdir(chapter_dir), f"Missing fixture directory: {chapter}"

    def test_chapter5_csv_files_exist(self, fixtures_dir):
        expected_files = [
            "currencies.csv",
            "invoices.csv",
            "categories-to-normalise.csv",
            "categories-to-denormalize.csv",
            "employees.csv",
            "country-codes.csv",
        ]
        ch5_dir = os.path.join(fixtures_dir, "Chapter5")
        for fname in expected_files:
            fpath = os.path.join(ch5_dir, fname)
            assert os.path.isfile(fpath), f"Missing fixture: Chapter5/{fname}"

    def test_chapter3_csv_files_exist(self, fixtures_dir):
        fpath = os.path.join(fixtures_dir, "Chapter3", "expressions.csv")
        assert os.path.isfile(fpath), "Missing fixture: Chapter3/expressions.csv"

    def test_fixture_files_not_empty(self, fixtures_dir):
        ch5_dir = os.path.join(fixtures_dir, "Chapter5")
        for fname in os.listdir(ch5_dir):
            fpath = os.path.join(ch5_dir, fname)
            if os.path.isfile(fpath):
                assert os.path.getsize(fpath) > 0, f"Empty fixture: Chapter5/{fname}"

    def test_all_config_input_paths_resolve(self, config):
        project_root = os.path.join(os.path.dirname(__file__), "..", "..")
        file_jobs = [
            "filtering1", "filtering2", "filtering3", "sorting",
            "aggregating", "normalize", "denormalize",
            "extract_delimited_fields", "find_and_replace", "sample_row",
            "expressions",
        ]
        for job_name in file_jobs:
            job = config["jobs"][job_name]
            input_path = os.path.join(project_root, job["input_path"])
            assert os.path.isfile(input_path), (
                f"Job '{job_name}' input file not found: {job['input_path']}"
            )
