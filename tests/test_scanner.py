"""Scanner: files only, non-recursive default, skip category dirs."""

from __future__ import annotations

from pathlib import Path

import pytest

from autoorg.scanner import scan


def _touch(path: Path, text: str = "x") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_scan_missing_path_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        scan(tmp_path / "nope")


def test_scan_file_path_raises(tmp_path: Path) -> None:
    file_path = _touch(tmp_path / "just-a-file.txt")
    with pytest.raises(NotADirectoryError):
        scan(file_path)


def test_scan_default_is_non_recursive(tmp_path: Path) -> None:
    top = _touch(tmp_path / "photo.jpg")
    _touch(tmp_path / "nested" / "deeper.py")
    tmp_path.joinpath("emptydir").mkdir()

    found = scan(tmp_path)

    assert found == [top]
    assert all(p.is_file() for p in found)


def test_scan_explicit_non_recursive_matches_default(tmp_path: Path) -> None:
    _touch(tmp_path / "a.txt")
    _touch(tmp_path / "sub" / "b.txt")

    assert scan(tmp_path) == scan(tmp_path, recursive=False)


def test_scan_files_only_ignores_directories(tmp_path: Path) -> None:
    _touch(tmp_path / "keep.me")
    tmp_path.joinpath("a-folder").mkdir()
    tmp_path.joinpath("images").mkdir()

    names = {p.name for p in scan(tmp_path)}

    assert names == {"keep.me"}


def test_scan_recursive_includes_nested_files(tmp_path: Path) -> None:
    top = _touch(tmp_path / "readme.txt")
    nested = _touch(tmp_path / "src" / "app.py")
    deeper = _touch(tmp_path / "src" / "pkg" / "mod.py")

    found = scan(tmp_path, recursive=True)

    assert set(found) == {top, nested, deeper}
    assert all(p.is_file() for p in found)


def test_scan_recursive_skips_category_directories(tmp_path: Path) -> None:
    loose = _touch(tmp_path / "loose.png")
    nested = _touch(tmp_path / "inbox" / "note.md")
    for bucket in ("images", "docs", "code", "archives", "audio", "video", "other"):
        _touch(tmp_path / bucket / f"already-sorted-{bucket}.dat")
        _touch(tmp_path / "inbox" / bucket / f"nested-{bucket}.dat")

    found = scan(tmp_path, recursive=True)
    names = {p.name for p in found}

    assert names == {"loose.png", "note.md"}
    assert all("already-sorted" not in p.name for p in found)
    assert all("nested-" not in p.name for p in found)


def test_scan_recursive_skips_category_dirs_case_insensitive(tmp_path: Path) -> None:
    keep = _touch(tmp_path / "stay.txt")
    _touch(tmp_path / "Images" / "shot.jpg")
    _touch(tmp_path / "DOCS" / "paper.pdf")

    found = scan(tmp_path, recursive=True)

    assert found == [keep]


def test_scan_non_recursive_does_not_enter_category_or_other_dirs(
    tmp_path: Path,
) -> None:
    top = _touch(tmp_path / "clip.mp4")
    _touch(tmp_path / "images" / "old.jpg")
    _touch(tmp_path / "inbox" / "new.jpg")

    found = scan(tmp_path, recursive=False)

    assert found == [top]


def test_scan_empty_directory(tmp_path: Path) -> None:
    assert scan(tmp_path) == []
    assert scan(tmp_path, recursive=True) == []
