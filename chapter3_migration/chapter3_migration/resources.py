"""Configuration/resources layer.

The original Talend jobs hard-code Windows paths such as
``C:/Talend/Workspace/GETTINGSTARTED/DataIn/Chapter3/...`` and
``.../DataOut/Chapter3/...``. This resource replaces them with configurable
directories that default to the sample data checked into this repository.
"""

from __future__ import annotations

import os
from pathlib import Path

from dagster import ConfigurableResource

# Repository root: chapter3_migration/chapter3_migration/resources.py -> repo root
_REPO_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_DATA_IN = str(_REPO_ROOT / "SampleDataFiles" / "Chapter3")
DEFAULT_DATA_OUT = str(_REPO_ROOT / "chapter3_migration" / "output")


class Chapter3Paths(ConfigurableResource):
    """Input/output directories replacing the hard-coded Talend paths.

    Values may be overridden via environment variables
    ``CHAPTER3_DATA_IN`` / ``CHAPTER3_DATA_OUT`` or through Dagster run config.
    """

    data_in_dir: str = DEFAULT_DATA_IN
    data_out_dir: str = DEFAULT_DATA_OUT
    # AdvancedXMLOutput emits a ``<!DOCTYPE ... SYSTEM "Talend.dtd">`` reference
    # in the original job; toggle it here.
    emit_dtd: bool = True

    def in_path(self, filename: str) -> str:
        return os.path.join(self.data_in_dir, filename)

    def out_path(self, filename: str) -> str:
        os.makedirs(self.data_out_dir, exist_ok=True)
        return os.path.join(self.data_out_dir, filename)
