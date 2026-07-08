# Chapter 3 Talend → Python + Polars + Dagster migration

A faithful reimplementation of the eight **Chapter 3** example jobs from the
Talend Open Studio *Getting Started* project as a modern
[Dagster](https://dagster.io) code location backed by
[Polars](https://pola.rs) and [lxml](https://lxml.de).

Each Talend job (`ExampleJobs/GETTINGSTARTEDTOS/process/Chapter3/*.item`) is
migrated to a small group of Dagster **assets** — one per read / transform /
write step — so the asset graph mirrors the original node/connection wiring.

## Layout

```
chapter3_migration/
├── pyproject.toml / requirements.txt
├── chapter3_migration/
│   ├── definitions.py          # Dagster Definitions (code location)
│   ├── resources.py            # Chapter3Paths resource (replaces Windows paths)
│   ├── helpers.py              # Talend routine reimplementations
│   ├── io_utils.py             # delimited / XML writers honouring encodings
│   └── assets/                 # one module per migrated job
│       ├── csv2xml.py
│       ├── xml2csv.py
│       ├── expressions.py
│       ├── advanced_xml_output.py
│       ├── multi_schema.py
│       ├── state_lookup.py
│       ├── spreadsheet1.py
│       └── spreadsheet2.py
├── scripts/make_chapter3_fixtures.py   # regenerate the Excel fixtures
└── tests/test_validation.py            # validation harness
```

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e chapter3_migration            # or: pip install -r chapter3_migration/requirements.txt

# launch the Dagster UI (from the repo root)
dagster dev -m chapter3_migration.definitions
```

Then open http://localhost:3000 and **Materialize all**. Outputs are written to
`chapter3_migration/output/` by default.

## Configuration / resources

The original jobs hard-code Windows paths such as
`C:/Talend/Workspace/GETTINGSTARTED/DataIn/Chapter3/…` and `…/DataOut/Chapter3/…`.
These are replaced by the `Chapter3Paths` resource (`resources.py`) exposing:

| field          | default                          | purpose                        |
| -------------- | -------------------------------- | ------------------------------ |
| `data_in_dir`  | `SampleDataFiles/Chapter3`       | input directory                |
| `data_out_dir` | `chapter3_migration/output`      | output directory               |
| `emit_dtd`     | `true`                           | AdvancedXMLOutput DTD reference |

Override via run config, e.g.:

```yaml
resources:
  paths:
    config:
      data_in_dir: /path/to/inputs
      data_out_dir: /path/to/outputs
      emit_dtd: true
```

### Encodings

Per-job encodings from the `.item` files are preserved:

| direction | delimited        | XML          | Excel |
| --------- | ---------------- | ------------ | ----- |
| input     | US-ASCII         | UTF-8 / ISO-8859-15 | UTF-8 |
| output    | ISO-8859-15      | UTF-8        | —     |

(`ms-catalogue.xml` is ISO-8859-15; `catalogue.xml` is UTF-8.)

## Job-by-job mapping

| Talend job | Assets | Input → Output | Notes |
| ---------- | ------ | -------------- | ----- |
| **CSV2XML** | `csv2xml_input` → `csv2xml_output` | `csv2xml-catalogue.csv` (`;`, no header) → `csv2xml-out.xml` | flat `<catalogue><sku>` with 5 child elements |
| **XML2CSV** | `xml2csv_rows` → `xml2csv_output` | `catalogue.xml` (loop `/catalogue/sku`) → `catalogue-out.csv` (`;`, no header) | |
| **Expressions** | `expressions_input` → `expressions_mapped` → `expressions_output` | `expressions.csv` (`;`, header) → `expressions-out.xml` | tMap transforms (see below) |
| **AdvancedXMLOutput** | `advanced_xml_input` → `advanced_xml_shipped` → `advanced_xml_output` | `order_status.csv` (`;`, header) → `order_status.xml` | filter `shipping_status=="shipped"`; nested `DISPATCH_DOCUMENT > ORDER > ORDER_LINE`; DTD reference |
| **MultiSchema** | `ms_catalogue_parsed` → `ms_skus`, `ms_inventory` | `ms-catalogue.xml` → Dagster logs | single parse fans out to two schemas (was two `tLogRow`) |
| **StateLookup** | `corporate_addresses`, `states_lookup` → `state_lookup_joined` → `state_lookup_output` | `corporate-addresses.csv` (`;`) + `states.csv` (`,`) → `address-lookup-out.csv` (`;`, no header) | LEFT join `state == state_name` (`USE_INNER_JOIN=false`); unmatched rows kept with empty `state_code` |
| **Spreadsheet1** | `products_excel` → `spreadsheet1_output` | `products.xls` (sheets dresses/skirts/knitwear) → `product-excel-out.csv` (`;`, **with** header) | reads cols 1–2 of each sheet and concatenates |
| **Spreadsheet2** | `customers_sheet`, `addresses_sheet` → `spreadsheet2_matched`, `spreadsheet2_rejects` → `spreadsheet2_output` | `customers.xls` → `customer-addresses.csv` + `customer-addresses-rejects.csv` (both `;`, no header) | INNER join on `customer_id`; unmatched customers routed to rejects (`rejectInnerJoin`) |

### Expressions tMap transforms (`helpers.py`)

| Output column | Talend expression | Python |
| ------------- | ----------------- | ------ |
| `id` | `String.format("%08d", CustomerID)` | `zero_pad(id, 8)` |
| `name` | `FirstName + " " + LastName` | `full_name(...)` |
| `address_1` | `Address2.equals("") ? Address1 : Address1 + ", " + Address2` | `address_line_1(...)` |
| `address_2` | `TownCity + ", " + County + ", " + Postcode` | `address_line_2(...)` |
| `telephone_number` | `Telephone.replaceAll("[^\\d]", "")` | `digits_only(...)` |

`AdvancedXMLOutput` uses `TalendDate.getCurrentDate()` → `helpers.get_current_date()`.

## Excel fixtures (newly created)

The Spreadsheet jobs require `products.xls` and `customers.xls`. These ship in
the repository but were **not** part of the original book download, so they are
documented here as project fixtures and can be regenerated deterministically
(legacy `.xls`, matching `VERSION_2007=false`):

```bash
python chapter3_migration/scripts/make_chapter3_fixtures.py
```

- **`products.xls`** — sheets `dresses`, `skirts`, `knitwear`; each with a
  header row and columns `product_id`, `product_name`. (Spreadsheet1 reads only
  columns 1–2 positionally and emits them as `product_code`/`product_name`.)
- **`customers.xls`** — sheet `customers` (`customer_id`, `title`, `first_name`,
  `last_name`, `email_address`) and sheet `addresses` (`customer_id`,
  `address1`, `city`, `postcode`, `telephone_number`). Customer **12349**
  (George Wickham) deliberately has **no** matching address row so the
  Spreadsheet2 reject flow is exercised.

## Validation harness

`tests/test_validation.py` materialises every asset against
`SampleDataFiles/Chapter3` and asserts row counts and content against the
fixture-derived expected outputs:

```bash
pytest chapter3_migration/tests
# or a standalone PASS/FAIL summary:
python chapter3_migration/tests/test_validation.py
```

## Caveats

- **Legacy `.xls`** is read via `polars.read_excel(engine="calamine")`
  (fastexcel), which handles the old BIFF format; the fixtures are generated
  with `xlwt`. `openpyxl` is included for `.xlsx` should the fixtures be
  regenerated in that format (the reader engine would then need adjusting).
- **DTD** — AdvancedXMLOutput emits
  `<!DOCTYPE DISPATCH_DOCUMENT SYSTEM "Talend.dtd">`; a `Talend.dtd` file is not
  shipped, so the reference is informational (toggle with `emit_dtd=false`).
- **`dispatch_date`** is intentionally non-deterministic (current datetime), so
  the harness validates it is present and parseable rather than a fixed value.
- Numeric Excel columns (`product_id`, `customer_id`) are emitted as plain
  integers (no `.0`), matching the expected delimited output.
