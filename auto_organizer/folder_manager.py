"""Create category folders safely under the target directory."""

from __future__ import annotations

from pathlib import Path

from file_types import known_categories, load_config
from utils.logger import info, warn
from utils.paths import ensure_directory, resolve_dir, safe_join


def category_root(target: str | Path, category: str) -> Path:
    """Return the path of a category folder under *target* without creating it."""
    root = resolve_dir(target)
    return safe_join(root, category)


def ensure_category_folder(target: str | Path, category: str) -> Path:
    """Create one category folder. No-op if it already exists."""
    folder = category_root(target, category)
    if folder.exists() and not folder.is_dir():
        raise NotADirectoryError(f"category path is a file: {folder}")
    created = not folder.exists()
    ensure_directory(folder)
    if created:
        info(f"created folder {folder}")
    return folder


def ensure_all_category_folders(
    target: str | Path,
    categories: dict[str, list[str]] | None = None,
) -> list[Path]:
    """Create every configured category folder under *target*."""
    if categories is None:
        categories = load_config()["categories"]
    folders: list[Path] = []
    for name in known_categories(categories):
        folders.append(ensure_category_folder(target, name))
    return folders


def ensure_undo_folder(target: str | Path, undo_name: str | None = None) -> Path:
    """Create the undo folder under *target*."""
    if undo_name is None:
        undo_name = load_config()["undo_folder"]
    root = resolve_dir(target)
    folder = safe_join(root, undo_name)
    if folder.exists() and not folder.is_dir():
        warn(f"undo path is not a directory: {folder}")
        raise NotADirectoryError(f"undo path is a file: {folder}")
    return ensure_directory(folder)
