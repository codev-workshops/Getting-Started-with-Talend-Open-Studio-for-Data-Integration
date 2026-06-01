#!/usr/bin/env bash
# Validate that demo_db.sql loads into MySQL and contains expected data.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

echo "Validating MySQL database load …"

# Load the dump (idempotent – tables are DROP IF EXISTS)
sudo mysql < "$REPO_ROOT/DBBackup/demo_db.sql"

EXPECTED_TABLES="brands invoices order_lines orders products"
ACTUAL_TABLES=$(sudo mysql -N -e "USE demo_db; SHOW TABLES;" | sort | tr '\n' ' ' | sed 's/ $//')

if [ "$ACTUAL_TABLES" != "$(echo $EXPECTED_TABLES | tr ' ' '\n' | sort | tr '\n' ' ' | sed 's/ $//')" ]; then
    echo "FAIL: Expected tables [$EXPECTED_TABLES], got [$ACTUAL_TABLES]"
    exit 1
fi

# Verify row counts
declare -A EXPECTED_COUNTS=( [brands]=13 [invoices]=25 [order_lines]=17 [orders]=7 [products]=13 )
ERRORS=0
for table in $EXPECTED_TABLES; do
    count=$(sudo mysql -N -e "SELECT COUNT(*) FROM demo_db.$table;")
    expected=${EXPECTED_COUNTS[$table]}
    if [ "$count" -ne "$expected" ]; then
        echo "FAIL: $table has $count rows, expected $expected"
        ERRORS=$((ERRORS + 1))
    fi
done

if [ "$ERRORS" -gt 0 ]; then
    echo "FAILED: $ERRORS table(s) with wrong row count"
    exit 1
fi

echo "ALL PASSED: database loaded with correct schema and data"
