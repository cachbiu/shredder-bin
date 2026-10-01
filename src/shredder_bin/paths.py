"""Resolve dropped URLs to local filesystem paths."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import unquote, urlparse

from PyQt6.QtCore import QUrl


def local_path_from_url(url: QUrl) -> str | None:
    """Return a local path, or None if the URL is not a local file."""
    local = url.toLocalFile()
    if local:
        return str(Path(local))
    raw = url.toString()
    parsed = urlparse(raw)
    if parsed.scheme not in {"file", ""}:
        return None
    path = unquote(parsed.path)
    if parsed.netloc and parsed.netloc not in {"localhost", "127.0.0.1"}:
        # UNC: file://server/share/...
        return str(Path(f"//{parsed.netloc}{path}"))
    if len(path) >= 3 and path[0] == "/" and path[2] == ":":
        path = path[1:]
    if not path:
        return None
    return str(Path(path))


def collect_local_paths(urls: list[QUrl]) -> tuple[list[str], list[str]]:
    """Split drop URLs into existing local paths and rejected descriptions."""
    accepted: list[str] = []
    rejected: list[str] = []
    for url in urls:
        path = local_path_from_url(url)
        if path is None:
            rejected.append(url.toString())
            continue
        if not Path(path).exists():
            rejected.append(path)
            continue
        accepted.append(path)
    return accepted, rejected
