#!/bin/bash
set -euo pipefail

pip install pyspark pytest
cd "$(dirname "$0")"
pytest test_db2db.py -v --tb=short
