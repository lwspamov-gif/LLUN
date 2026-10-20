from __future__ import annotations

import os
import sys
from pathlib import Path


def resolve_project_root() -> Path:
    root = Path(__file__).resolve().parents[3]
    return root


def get_resource_path(*parts: str) -> Path:
    base = Path(sys._MEIPASS) if hasattr(sys, "_MEIPASS") else resolve_project_root()
    return base.joinpath(*parts)
