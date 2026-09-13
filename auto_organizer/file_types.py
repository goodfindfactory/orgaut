"""Detect extensions and map them to categories from config.json."""

from __future__ import annotations

import json
from pathlib import Path

CONFIG_PATH = Path(__file__).resolve().parent / "config.json"


def load_config(path: Path | None = None) -> dict:
    """Load the JSON config. *path* defaults to the bundled config.json."""
    cfg_path = Path(path) if path is not None else CONFIG_PATH
    with cfg_path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if "categories" not in data or not isinstance(data["categories"], dict):
        raise ValueError("config.json is missing a categories object")
    data.setdefault("undo_folder", "_undo")
    data.setdefault("report_file", "summary_report.txt")
    return data


def extension_of(path: str | Path) -> str:
    """Lowercase extension without the leading dot. Empty if none."""
    suffix = Path(path).suffix
    if not suffix or suffix == ".":
        return ""
    return suffix[1:].lower()


def build_extension_map(categories: dict[str, list[str]]) -> dict[str, str]:
    """Invert ``{category: [ext, …]}`` to ``{ext: category}``."""
    mapping: dict[str, str] = {}
    for category, extensions in categories.items():
        for ext in extensions:
            mapping[ext.lower().lstrip(".")] = category
    return mapping


def detect_type(path: str | Path, categories: dict[str, list[str]] | None = None) -> str | None:
    """Master-block alias for :func:`category_for`."""
    return category_for(path, categories)


def category_for(path: str | Path, categories: dict[str, list[str]] | None = None) -> str | None:
    """Return the category name for *path*, or None if unknown."""
    if categories is None:
        categories = load_config()["categories"]
    ext = extension_of(path)
    if not ext:
        return None
    return build_extension_map(categories).get(ext)


def known_categories(categories: dict[str, list[str]] | None = None) -> list[str]:
    """Stable category folder names from config."""
    if categories is None:
        categories = load_config()["categories"]
    return list(categories.keys())


if __name__ == "__main__":
    cfg = load_config()
    print("file_types OK", list(cfg["categories"]))
    print("detect_type example.pdf ->", detect_type("example.pdf"))
