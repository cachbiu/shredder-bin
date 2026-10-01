"""Send paths to the Windows Recycle Bin and open the system bin."""

from __future__ import annotations

import subprocess
from pathlib import Path

from send2trash import send2trash

FailedItem = tuple[str, str]


def send_to_recycle(paths: list[str | Path]) -> list[FailedItem]:
    """Move each path to Recycle Bin. Returns (path, error) for failures."""
    failed: list[FailedItem] = []
    for raw in paths:
        path = str(Path(raw))
        try:
            send2trash(path)
        except Exception as exc:  # noqa: BLE001 — surface any send2trash/OS error
            failed.append((path, str(exc)))
    return failed


def open_recycle_bin() -> None:
    """Open the standard Windows Recycle Bin in Explorer."""
    subprocess.Popen(
        ["explorer.exe", "shell:RecycleBinFolder"],
        shell=False,
    )
