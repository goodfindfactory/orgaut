"""Walk a folder and collect files to organize."""

from __future__ import annotations

import os
from pathlib import Path

from autoorg.util import is_category_dir


def scan(root: Path | str, recursive: bool = False) -> list[Path]:
    """Return regular files under *root*.

    Non-recursive (default): only files sitting directly in *root*.
    Recursive: walk nested directories, but do not descend into category
    buckets (`images`, `docs`, `code`, `archives`, `audio`, `video`,
    `other`) so already-sorted files stay put.

    Directories themselves are never returned.
    """
    root = Path(root)
    if not root.exists():
        raise FileNotFoundError(f"path does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"not a directory: {root}")

    if recursive:
        return _scan_recursive(root)
    return _scan_flat(root)


def _scan_flat(root: Path) -> list[Path]:
    files: list[Path] = []
    with os.scandir(root) as entries:
        for entry in entries:
            if entry.is_file(follow_symlinks=False):
                files.append(Path(entry.path))
    files.sort(key=lambda p: p.name.lower())
    return files


def _scan_recursive(root: Path) -> list[Path]:
    files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False, topdown=True):
        dirnames[:] = [name for name in dirnames if not is_category_dir(name)]
        current = Path(dirpath)
        for name in filenames:
            path = current / name
            if path.is_file() and not path.is_symlink():
                files.append(path)
    files.sort(key=lambda p: str(p).lower())
    return files
