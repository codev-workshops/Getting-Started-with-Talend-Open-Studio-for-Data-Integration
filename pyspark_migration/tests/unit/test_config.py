"""Unit tests for config/job_config.yaml - verify structure and required fields."""
import os
import yaml
import pytest


@pytest.fixture(scope="module")
def config():
    config_path = os.path.join(os.path.dirname(__file__), "..", "..", "config", "job_config.yaml")
    with open(config_path) as f:
        return yaml.safe_load(f)


class TestJobConfig:
    def test_config_has_fixtures_base(self, config):
        assert "fixtures_base" in config
        assert config["fixtures_base"] == "fixtures"

    def test_config_has_database_section(self, config):
        assert "database" in config
        db = config["database"]
        assert "jdbc_url" in db
        assert "user" in db
        assert "driver" in db

    def test_config_has_jobs_section(self, config):
        assert "jobs" in config
        assert isinstance(config["jobs"], dict)
        assert len(config["jobs"]) > 0

    def test_chapter5_jobs_present(self, config):
        jobs = config["jobs"]
        ch5_jobs = [
            "filtering1", "filtering2", "filtering3", "sorting",
            "aggregating", "normalize", "denormalize",
            "extract_delimited_fields", "find_and_replace", "sample_row",
        ]
        for job_name in ch5_jobs:
            assert job_name in jobs, f"Missing job config: {job_name}"

    def test_chapter3_jobs_present(self, config):
        assert "expressions" in config["jobs"]

    def test_chapter4_jobs_present(self, config):
        assert "db_extract" in config["jobs"]
        assert "db2db" in config["jobs"]

    def test_each_file_job_has_input_path(self, config):
        file_jobs = [
            "filtering1", "filtering2", "filtering3", "sorting",
            "aggregating", "normalize", "denormalize",
            "extract_delimited_fields", "find_and_replace", "sample_row",
            "expressions",
        ]
        for job_name in file_jobs:
            job = config["jobs"][job_name]
            assert "input_path" in job, f"Job '{job_name}' missing input_path"
            assert job["input_path"].startswith("fixtures/"), (
                f"Job '{job_name}' input_path should start with 'fixtures/'"
            )
