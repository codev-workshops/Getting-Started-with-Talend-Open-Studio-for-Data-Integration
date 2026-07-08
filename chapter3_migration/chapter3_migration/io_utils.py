"""Small IO helpers that honour the per-job encodings and delimiter settings
declared in the original Talend components (tFileOutputDelimited / tFileOutputXML).
"""

from __future__ import annotations

from typing import Iterable, Sequence

from lxml import etree


def write_delimited(
    path: str,
    rows: Iterable[Sequence[object]],
    *,
    header: Sequence[str] | None = None,
    sep: str = ";",
    encoding: str = "ISO-8859-15",
    row_sep: str = "\n",
) -> int:
    """Write a delimited text file the way tFileOutputDelimited does.

    Returns the number of *data* rows written. Fields are stringified and
    ``None`` becomes an empty field (Talend renders nulls as empty strings).
    """
    lines: list[str] = []
    if header is not None:
        lines.append(sep.join(header))
    count = 0
    for row in rows:
        lines.append(sep.join("" if v is None else str(v) for v in row))
        count += 1
    text = row_sep.join(lines) + (row_sep if lines else "")
    with open(path, "w", encoding=encoding, newline="") as fh:
        fh.write(text)
    return count


def write_flat_xml(
    path: str,
    root_tag: str,
    row_tag: str,
    columns: Sequence[str],
    rows: Iterable[Sequence[object]],
    *,
    encoding: str = "UTF-8",
) -> int:
    """Write a flat ``<root><row><col>..</col></row>..</root>`` document.

    Mirrors tFileOutputXML with every mapped column emitted as a child element.
    """
    root = etree.Element(root_tag)
    count = 0
    for row in rows:
        row_el = etree.SubElement(root, row_tag)
        for col, value in zip(columns, row):
            child = etree.SubElement(row_el, col)
            child.text = "" if value is None else str(value)
        count += 1
    tree = etree.ElementTree(root)
    tree.write(path, pretty_print=True, xml_declaration=True, encoding=encoding)
    return count
