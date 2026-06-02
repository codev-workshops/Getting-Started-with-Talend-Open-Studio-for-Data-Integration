# PySpark Migration - Phase 0 Build & Validation
# Usage: make setup && make test

SHELL := /bin/bash
PYTHON := python3
PIP := pip
PYTEST := pytest
VENV := .venv
PROJECT_ROOT := $(shell pwd)
REPO_ROOT := $(shell cd .. && pwd)

.PHONY: help setup fixtures venv test test-unit test-integration lint clean validate

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: venv fixtures ## Full Phase 0 setup: create venv, install deps, copy fixtures

venv: ## Create virtualenv and install requirements
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r requirements.txt

fixtures: ## Copy SampleDataFiles/ into fixtures/ (Chapter3-7 only)
	@echo "Copying fixture files from SampleDataFiles/..."
	@for ch in Chapter3 Chapter4 Chapter5 Chapter6 Chapter7; do \
		if [ -d "$(REPO_ROOT)/SampleDataFiles/$$ch" ]; then \
			mkdir -p fixtures/$$ch; \
			cp -r "$(REPO_ROOT)/SampleDataFiles/$$ch/." "fixtures/$$ch/"; \
			echo "  ✓ $$ch"; \
		else \
			echo "  ⚠ $$ch not found in SampleDataFiles/, skipping"; \
		fi; \
	done
	@echo "Fixtures ready."

test: test-unit test-integration ## Run all tests (unit + integration)

test-unit: ## Run unit tests only
	cd $(PROJECT_ROOT) && PYTHONPATH=$(PROJECT_ROOT) $(VENV)/bin/$(PYTEST) tests/unit/ -v --tb=short

test-integration: ## Run integration tests only
	cd $(PROJECT_ROOT) && PYTHONPATH=$(PROJECT_ROOT) $(VENV)/bin/$(PYTEST) tests/integration/ -v --tb=short

test-parallel: ## Run all tests in parallel (requires pytest-xdist)
	cd $(PROJECT_ROOT) && PYTHONPATH=$(PROJECT_ROOT) $(VENV)/bin/$(PYTEST) tests/ -v --tb=short -n auto

lint: ## Check Python files for syntax errors
	$(VENV)/bin/$(PYTHON) -m py_compile utils/csv_io.py
	$(VENV)/bin/$(PYTHON) -m py_compile utils/db_io.py
	$(VENV)/bin/$(PYTHON) -m py_compile utils/schema_validator.py
	$(VENV)/bin/$(PYTHON) -m py_compile utils/diff_comparator.py
	@echo "All modules compile cleanly."

validate: lint test ## Full validation: lint + test

clean: ## Remove build artifacts and output
	rm -rf $(VENV) output/ __pycache__ .pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
