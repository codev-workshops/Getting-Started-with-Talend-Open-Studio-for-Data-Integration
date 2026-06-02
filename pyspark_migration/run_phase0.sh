#!/usr/bin/env bash
# Phase 0: Bootstrap the PySpark migration scaffold
# Usage: cd pyspark_migration && bash run_phase0.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Phase 0: PySpark Migration Bootstrap ==="
echo ""

# Step 1: Create virtualenv and install dependencies
echo "[1/4] Setting up virtualenv and installing dependencies..."
make venv
echo ""

# Step 2: Copy fixture files from SampleDataFiles/
echo "[2/4] Copying fixture files..."
make fixtures
echo ""

# Step 3: Lint check
echo "[3/4] Running lint checks..."
make lint
echo ""

# Step 4: Run full test suite
echo "[4/4] Running test suite..."
make test
echo ""

echo "=== Phase 0 complete ==="
echo "All utilities, schemas, configs, and fixtures are in place."
echo "Run 'make test' to re-run the test suite at any time."
