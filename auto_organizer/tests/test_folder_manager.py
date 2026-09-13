"""folder_manager: safe category and undo folder creation."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from file_types import load_config  # noqa: E402
from folder_manager import (  # noqa: E402
    category_root,
    ensure_all_category_folders,
    ensure_category_folder,
    ensure_undo_folder,
)


def test_ensure_category_folder_creates_once(tmp_path: Path) -> None:
    folder = ensure_category_folder(tmp_path, "images")
    assert folder.is_dir()
    assert folder == tmp_path / "images"
    again = ensure_category_folder(tmp_path, "images")
    assert again == folder


def test_ensure_all_category_folders(tmp_path: Path) -> None:
    folders = ensure_all_category_folders(tmp_path)
    names = {path.name for path in folders}
    assert names == set(load_config()["categories"])
    for folder in folders:
        assert folder.is_dir()
        assert folder.parent == tmp_path


def test_ensure_undo_folder(tmp_path: Path) -> None:
    undo = ensure_undo_folder(tmp_path)
    assert undo == tmp_path / "_undo"
    assert undo.is_dir()


def test_category_root_does_not_create(tmp_path: Path) -> None:
    path = category_root(tmp_path, "documents")
    assert path == tmp_path / "documents"
    assert not path.exists()


def test_refuses_file_in_the_way(tmp_path: Path) -> None:
    blocker = tmp_path / "images"
    blocker.write_text("nope", encoding="utf-8")
    with pytest.raises(NotADirectoryError):
        ensure_category_folder(tmp_path, "images")


def test_rejects_parent_escape(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        category_root(tmp_path, "../outside")
