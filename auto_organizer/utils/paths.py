"""Safe, cross-platform path helpers. Never escape the target root."""

from __future__ import annotations

import os
from pathlib import Path


def resolve_dir(path: str | Path) -> Path:
    """Return an absolute directory path, or raise."""
    target = Path(path).expanduser()
    try:
        target = target.resolve(strict=False)
    except OSError as exc:
        raise ValueError(f"cannot resolve path: {path}") from exc
    return target


def ensure_directory(path: str | Path) -> Path:
    """Create *path* as a directory if missing. Refuse if it is a file."""
    target = resolve_dir(path)
    if target.exists() and not target.is_dir():
        raise NotADirectoryError(f"not a directory: {target}")
    target.mkdir(parents=True, exist_ok=True)
    return target


def is_within(child: Path, parent: Path) -> bool:
    """True when *child* is inside *parent* (after resolve)."""
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except (ValueError, OSError):
        return False


def safe_join(root: Path, *parts: str) -> Path:
    """Join under *root* and reject any escape via ``..`` or absolute parts."""
    root = resolve_dir(root)
    candidate = root
    for part in parts:
        if not part or part in (".",):
            continue
        piece = Path(part)
        if piece.is_absolute() or os.path.splitdrive(part)[0]:
            raise ValueError(f"absolute path not allowed: {part}")
        if ".." in piece.parts:
            raise ValueError(f"parent traversal not allowed: {part}")
        candidate = candidate / piece
    if not is_within(candidate, root):
        raise ValueError(f"path escapes root: {candidate}")
    return candidate


def unique_path(dest: Path) -> Path:
    """If *dest* exists, return ``stem_1.ext``, ``stem_2.ext``, …"""
    if not dest.exists():
        return dest
    stem = dest.stem
    suffix = dest.suffix
    parent = dest.parent
    n = 1
    while True:
        candidate = parent / f"{stem}_{n}{suffix}"
        if not candidate.exists():
            return candidate
        n += 1


def is_reserved_name(name: str, undo_folder: str) -> bool:
    """Category-adjacent names the organizer must not treat as loose files."""
    lowered = name.lower()
    return lowered == undo_folder.lower() or lowered == "summary_report.txt"
