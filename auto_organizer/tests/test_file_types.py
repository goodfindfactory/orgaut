"""file_types: extensions and config category map."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from file_types import (  # noqa: E402
    build_extension_map,
    category_for,
    detect_type,
    extension_of,
    known_categories,
    load_config,
)


def test_load_config_has_required_keys() -> None:
    config = load_config()
    assert set(config["categories"]) == {
        "documents",
        "images",
        "videos",
        "audio",
        "archives",
        "code",
        "executables",
    }
    assert config["undo_folder"] == "_undo"
    assert config["report_file"] == "summary_report.txt"
    assert config["categories"]["documents"] == ["pdf", "docx", "txt", "md"]
    assert config["categories"]["images"] == ["jpg", "jpeg", "png", "gif", "bmp"]
    assert config["categories"]["videos"] == ["mp4", "mov", "avi"]
    assert config["categories"]["audio"] == ["mp3", "wav", "flac"]
    assert config["categories"]["archives"] == ["zip", "rar", "7z"]
    assert config["categories"]["code"] == ["py", "js", "ts", "html", "css"]
    assert config["categories"]["executables"] == ["exe", "dmg", "app"]


def test_extension_of() -> None:
    assert extension_of("Paper.PDF") == "pdf"
    assert extension_of(Path("shot.jpeg")) == "jpeg"
    assert extension_of("LICENSE") == ""
    assert extension_of(".gitignore") == ""


def test_category_for_known_and_unknown() -> None:
    cats = load_config()["categories"]
    assert category_for("notes.MD", cats) == "documents"
    assert category_for("pic.JPG", cats) == "images"
    assert category_for("clip.mov", cats) == "videos"
    assert category_for("song.flac", cats) == "audio"
    assert category_for("pack.7z", cats) == "archives"
    assert category_for("app.ts", cats) == "code"
    assert detect_type("Setup.exe", cats) == category_for("Setup.exe", cats) == "executables"
    assert category_for("weird.xyz", cats) is None
    assert category_for("noext", cats) is None


def test_build_extension_map_and_known_categories() -> None:
    cats = {"images": ["png", "JPG"], "code": ["py"]}
    mapping = build_extension_map(cats)
    assert mapping["png"] == "images"
    assert mapping["jpg"] == "images"
    assert mapping["py"] == "code"
    assert known_categories(cats) == ["images", "code"]


def test_load_config_rejects_bad_file(tmp_path: Path) -> None:
    bad = tmp_path / "config.json"
    bad.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError):
        load_config(bad)
