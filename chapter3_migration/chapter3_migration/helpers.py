"""Python reimplementations of the Talend routines used by the Chapter 3 jobs.

Each function mirrors a specific piece of Java logic found in the original
``.item`` tMap expressions so the migrated pipelines produce byte-identical
output (modulo the intentionally non-deterministic dispatch date).
"""

from __future__ import annotations

import re
from datetime import datetime

# ``dd-MM-yyyy`` style Java patterns are irrelevant here; the AdvancedXMLOutput
# job stamps ``dispatch_date`` with this pattern (Talend ``"yyyy-MM-dd hh:mm"``).
DISPATCH_DATE_PATTERN = "%Y-%m-%d %I:%M"


def get_current_date(now: datetime | None = None) -> datetime:
    """Equivalent of ``TalendDate.getCurrentDate()``.

    Returns the current local datetime. ``now`` may be injected for
    deterministic testing.
    """
    return now if now is not None else datetime.now()


def format_dispatch_date(value: datetime) -> str:
    """Format a datetime the way the AdvancedXMLOutput schema pattern does."""
    return value.strftime(DISPATCH_DATE_PATTERN)


def zero_pad(value: object, width: int = 8) -> str:
    """Equivalent of Java ``String.format("%08d", value)``.

    Talend applies this to the integer ``CustomerID`` column.
    """
    return f"{int(value):0{width}d}"


def digits_only(value: object) -> str:
    """Equivalent of Java ``x.replaceAll("[^\\\\d]", "")`` — strip non-digits."""
    if value is None:
        return ""
    return re.sub(r"[^\d]", "", str(value))


def full_name(first_name: object, last_name: object) -> str:
    """Equivalent of ``row1.FirstName + " " + row1.LastName``."""
    return f"{_s(first_name)} {_s(last_name)}"


def address_line_1(address1: object, address2: object) -> str:
    """Equivalent of the Talend ternary::

        row1.Address2.equals("") ? row1.Address1
                                  : row1.Address1 + ", " + row1.Address2
    """
    a1 = _s(address1)
    a2 = _s(address2)
    return a1 if a2 == "" else f"{a1}, {a2}"


def address_line_2(town_city: object, county: object, postcode: object) -> str:
    """Equivalent of ``TownCity + ", " + County + ", " + Postcode``."""
    return f"{_s(town_city)}, {_s(county)}, {_s(postcode)}"


def _s(value: object) -> str:
    """Coerce to a Java-``String``-like value (null -> empty string)."""
    return "" if value is None else str(value)
