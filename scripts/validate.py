#!/usr/bin/env python3
"""Validate repository data integrity.

Checks:
  1. Talend job XML well-formedness  (ExampleJobs/**/process/**/*.item)
  2. Talend project descriptor        (talend.project)
  3. Sample XML files                  (SampleDataFiles/**/*.xml, non-empty)
  4. Sample CSV files                  (SampleDataFiles/**/*.csv)
  5. SQL dump syntax                   (DBBackup/demo_db.sql)
"""

import csv
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ERRORS: list[str] = []
PASS_COUNT = 0


def ok(msg: str) -> None:
    global PASS_COUNT
    PASS_COUNT += 1


def fail(msg: str) -> None:
    ERRORS.append(msg)
    print(f"  FAIL: {msg}", file=sys.stderr)


# ── 1. Talend job items (XML) ───────────────────────────────────────────────
def validate_talend_jobs() -> None:
    print("Validating Talend job definitions …")
    job_dir = REPO_ROOT / "ExampleJobs" / "GETTINGSTARTEDTOS" / "process"
    if not job_dir.exists():
        fail(f"Missing directory: {job_dir.relative_to(REPO_ROOT)}")
        return
    items = sorted(job_dir.rglob("*.item"))
    if not items:
        fail("No .item files found under ExampleJobs/**/process/")
        return
    for item in items:
        try:
            ET.parse(item)
            ok(str(item.relative_to(REPO_ROOT)))
        except ET.ParseError as exc:
            fail(f"{item.relative_to(REPO_ROOT)}: {exc}")


# ── 2. Talend project descriptor ────────────────────────────────────────────
def validate_talend_project() -> None:
    print("Validating Talend project descriptor …")
    proj = REPO_ROOT / "ExampleJobs" / "GETTINGSTARTEDTOS" / "talend.project"
    if not proj.exists():
        fail("Missing talend.project")
        return
    try:
        tree = ET.parse(proj)
        root = tree.getroot()
        # Expect at least one Project element
        ns = {"tp": "http://www.talend.org/properties"}
        projects = root.findall(".//tp:Project", ns) or root.findall(".//{http://www.talend.org/properties}Project")
        if not projects:
            # Try without namespace (XMI root)
            if "talend" not in root.tag.lower() and not any("Project" in child.tag for child in root):
                fail("talend.project has no Project element")
                return
        ok("talend.project")
    except ET.ParseError as exc:
        fail(f"talend.project: {exc}")


# ── 3. Sample XML files ────────────────────────────────────────────────────
def validate_sample_xml() -> None:
    print("Validating sample XML files …")
    xml_dir = REPO_ROOT / "SampleDataFiles"
    xmls = sorted(xml_dir.rglob("*.xml"))
    if not xmls:
        fail("No XML sample files found")
        return
    for xf in xmls:
        if xf.stat().st_size == 0:
            # Empty placeholder files (Chapter6 FileList) are expected
            ok(f"{xf.relative_to(REPO_ROOT)} (empty placeholder)")
            continue
        try:
            ET.parse(xf)
            ok(str(xf.relative_to(REPO_ROOT)))
        except ET.ParseError as exc:
            fail(f"{xf.relative_to(REPO_ROOT)}: {exc}")


# ── 4. Sample CSV files ────────────────────────────────────────────────────
def validate_sample_csv() -> None:
    print("Validating sample CSV files …")
    csv_dir = REPO_ROOT / "SampleDataFiles"
    csvs = sorted(csv_dir.rglob("*.csv"))
    if not csvs:
        fail("No CSV sample files found")
        return
    for cf in csvs:
        try:
            with open(cf, newline="", encoding="utf-8", errors="replace") as fh:
                reader = csv.reader(fh)
                rows = list(reader)
            if not rows:
                fail(f"{cf.relative_to(REPO_ROOT)}: empty CSV")
            else:
                ok(str(cf.relative_to(REPO_ROOT)))
        except csv.Error as exc:
            fail(f"{cf.relative_to(REPO_ROOT)}: {exc}")


# ── 5. SQL dump basic syntax ───────────────────────────────────────────────
def validate_sql_dump() -> None:
    print("Validating SQL dump …")
    sql_file = REPO_ROOT / "DBBackup" / "demo_db.sql"
    if not sql_file.exists():
        fail("Missing DBBackup/demo_db.sql")
        return
    content = sql_file.read_text(encoding="utf-8", errors="replace")
    # Check for expected structural elements
    expected = ["CREATE DATABASE", "CREATE TABLE", "INSERT INTO"]
    for keyword in expected:
        if keyword not in content.upper():
            fail(f"demo_db.sql missing expected keyword: {keyword}")
            return
    expected_tables = ["brands", "invoices", "order_lines", "orders", "products"]
    for table in expected_tables:
        if table not in content:
            fail(f"demo_db.sql missing expected table: {table}")
            return
    ok("demo_db.sql")


# ── Main ────────────────────────────────────────────────────────────────────
def main() -> int:
    validate_talend_jobs()
    validate_talend_project()
    validate_sample_xml()
    validate_sample_csv()
    validate_sql_dump()

    print()
    if ERRORS:
        print(f"FAILED: {len(ERRORS)} error(s), {PASS_COUNT} passed")
        for e in ERRORS:
            print(f"  • {e}")
        return 1
    print(f"ALL PASSED: {PASS_COUNT} checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
