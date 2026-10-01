"""Create a Desktop shortcut to the frozen EXE."""

from __future__ import annotations

import sys
from pathlib import Path


def ensure_desktop_shortcut() -> None:
    if not getattr(sys, "frozen", False):
        return
    exe = Path(sys.executable).resolve()
    desktop = Path.home() / "Desktop"
    if not desktop.is_dir():
        desktop = Path.home() / "OneDrive" / "Desktop"
    if not desktop.is_dir():
        return
    lnk = desktop / "Shredder Bin.lnk"
    ico = Path(getattr(sys, "_MEIPASS", exe.parent)) / "assets" / "shredder.ico"
    icon_loc = str(ico) if ico.is_file() else str(exe)
    script = (
        "$s = New-Object -ComObject WScript.Shell; "
        f"$c = $s.CreateShortcut('{lnk}'); "
        f"$c.TargetPath = '{exe}'; "
        f"$c.WorkingDirectory = '{exe.parent}'; "
        f"$c.IconLocation = '{icon_loc}'; "
        "$c.Description = 'Виджет корзины со шреддером'; "
        "$c.Save()"
    )
    import subprocess

    subprocess.run(
        ["powershell", "-NoProfile", "-Command", script],
        check=False,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
