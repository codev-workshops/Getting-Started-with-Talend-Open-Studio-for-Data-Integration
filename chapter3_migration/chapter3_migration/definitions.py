"""Dagster code location for the migrated Talend Chapter 3 jobs.

Every input/transform/output step is a Dagster asset; dependencies mirror the
Talend node/connection wiring. Each of the 8 jobs is its own asset group.
"""

from __future__ import annotations

from dagster import Definitions, load_assets_from_package_module

from . import assets
from .resources import Chapter3Paths

all_assets = load_assets_from_package_module(assets)

defs = Definitions(
    assets=all_assets,
    resources={"paths": Chapter3Paths()},
)
