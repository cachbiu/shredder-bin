"""Resolve bundled assets for source runs and PyInstaller."""

from __future__ import annotations

import sys
from pathlib import Path


def asset_path(name: str) -> Path:
    if getattr(sys, "frozen", False):
        base = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
        bundled = base / "assets" / name
        if bundled.is_file():
            return bundled
        beside = Path(sys.executable).resolve().parent / "assets" / name
        if beside.is_file():
            return beside
        return bundled
    return Path(__file__).resolve().parents[2] / "assets" / name
