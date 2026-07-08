"""Deterministically (re)generate the Chapter 3 Excel fixtures.

``products.xls`` and ``customers.xls`` are required by the Spreadsheet1 and
Spreadsheet2 jobs. Both jobs set ``VERSION_2007=false`` in Talend, so we emit
legacy ``.xls`` workbooks via ``xlwt``.

These files already ship in the repository; this script reproduces byte-stable
content (same sheets, headers and rows) so the fixtures can be regenerated on
demand. Run from anywhere::

    python chapter3_migration/scripts/make_chapter3_fixtures.py [OUTPUT_DIR]

The default OUTPUT_DIR is ``SampleDataFiles/Chapter3`` at the repo root.
"""

from __future__ import annotations

import os
import sys

import xlwt

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_OUT = os.path.join(_REPO_ROOT, "SampleDataFiles", "Chapter3")

# --- products.xls -----------------------------------------------------------
# Spreadsheet1 reads columns 1-2 of every sheet (header row 1) and concatenates
# them. The header of column 1 is ``product_id`` in the original workbook.
PRODUCTS: dict[str, list[tuple[int, str]]] = {
    "dresses": [
        (12345678, "Red Dress"),
        (12345679, "Pink Dress"),
        (12345680, "Blue Dress"),
        (12345681, "Green Dress"),
        (12345682, "Black Dress"),
    ],
    "skirts": [
        (98765432, "Blue Striped Skirt"),
        (98765431, "Pink Spotted Skirt"),
        (98765430, "Multi-coloured Skirt"),
        (98765429, "Yellow Check Skirt"),
        (98765428, "Black Skirt"),
    ],
    "knitwear": [
        (23456789, "Blue Cardigan"),
        (23456790, "Pink Jumper"),
        (23456791, "Green Cardigan"),
        (23456792, "Black Turtle Neck"),
    ],
}
PRODUCTS_HEADER = ["product_id", "product_name"]

# --- customers.xls ----------------------------------------------------------
# Spreadsheet2 INNER-joins ``customers`` to ``addresses`` on ``customer_id`` and
# routes unmatched customers to a reject flow. Customer 12349 (George Wickham)
# deliberately has NO matching address row so the reject flow is exercised.
CUSTOMERS_HEADER = ["customer_id", "title", "first_name", "last_name", "email_address"]
CUSTOMERS = [
    (12345, "Mr", "Fitzwilliam", "Darcy", "fdarcy@darcy.com"),
    (12346, "Mr", "Charles", "Bingley", "charlesb@bingley.com"),
    (12347, "Ms", "Elizabeth", "Bennet", "ebennet@bennet.com"),
    (12348, "Ms", "Charlotte", "Lucas", "clucas@lucas.com"),
    (12349, "Mr", "George", "Wickham", "gw@wickham.com"),
]
ADDRESSES_HEADER = ["customer_id", "address1", "city", "postcode", "telephone_number"]
ADDRESSES = [
    (12345, "1 High Street", "Meryton", "MY2 3RG", "01234-567837"),
    (12346, "22 The Dales", "Meryton", "MY3 4RJ", "01234-678593"),
    (12347, "52 Green Lane", "Meryton", "MY1 3SH", "01234-678294"),
    (12348, "78 Smith Street", "Meryton", "MY3 6AR", "01234-278303"),
    # NOTE: no row for customer 12349 -> reject flow.
]


def _write_sheet(sheet, header, rows) -> None:
    for col, name in enumerate(header):
        sheet.write(0, col, name)
    for r, row in enumerate(rows, start=1):
        for c, value in enumerate(row):
            sheet.write(r, c, value)


def make_products(out_dir: str) -> str:
    wb = xlwt.Workbook()
    for sheet_name, rows in PRODUCTS.items():
        _write_sheet(wb.add_sheet(sheet_name), PRODUCTS_HEADER, rows)
    path = os.path.join(out_dir, "products.xls")
    wb.save(path)
    return path


def make_customers(out_dir: str) -> str:
    wb = xlwt.Workbook()
    _write_sheet(wb.add_sheet("customers"), CUSTOMERS_HEADER, CUSTOMERS)
    _write_sheet(wb.add_sheet("addresses"), ADDRESSES_HEADER, ADDRESSES)
    path = os.path.join(out_dir, "customers.xls")
    wb.save(path)
    return path


def main() -> None:
    out_dir = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OUT
    os.makedirs(out_dir, exist_ok=True)
    print("wrote", make_products(out_dir))
    print("wrote", make_customers(out_dir))


if __name__ == "__main__":
    main()
