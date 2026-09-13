"""mover: move, collision suffix, dry-run, rollback."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from main import organize, undo  # noqa: E402
from mover import MoveBatch, MoveRecord, move_file, organize_files, plan_destination  # noqa: E402


def _touch(path: Path, text: str = "x") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_move_file_relocates_not_copies(tmp_path: Path) -> None:
    src = _touch(tmp_path / "shot.png", "pixels")
    dest = tmp_path / "images" / "shot.png"
    record = move_file(src, dest)
    assert not src.exists()
    assert dest.read_text(encoding="utf-8") == "pixels"
    assert record.category == "images"


def test_dry_run_organize_does_not_move(tmp_path: Path) -> None:
    src = _touch(tmp_path / "notes.txt", "hi")
    batch = organize_files(tmp_path, [(src, "documents")], dry_run=True)
    assert src.exists()
    assert not (tmp_path / "documents").exists()
    assert batch.records[0].dest == tmp_path / "documents" / "notes.txt"


def test_collision_suffix(tmp_path: Path) -> None:
    dest_dir = tmp_path / "images"
    dest_dir.mkdir()
    _touch(dest_dir / "shot.png", "old")
    incoming = _touch(tmp_path / "shot.png", "new")
    dest = plan_destination(tmp_path, incoming, "images")
    assert dest == dest_dir / "shot_1.png"
    move_file(incoming, dest)
    assert (dest_dir / "shot.png").read_text(encoding="utf-8") == "old"
    assert dest.read_text(encoding="utf-8") == "new"


def test_batch_rollback(tmp_path: Path) -> None:
    a = _touch(tmp_path / "a.pdf", "A")
    dest_a = tmp_path / "documents" / "a.pdf"
    dest_a.parent.mkdir()
    record = move_file(a, dest_a)
    batch = MoveBatch(records=[record])
    restored = batch.rollback()
    assert restored
    assert a.exists()
    assert a.read_text(encoding="utf-8") == "A"
    assert record.undone is True


def test_organize_files_rollback_on_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    first = _touch(tmp_path / "one.py", "1")
    second = _touch(tmp_path / "two.py", "2")
    calls = {"n": 0}
    real_move = move_file

    def flaky(src: Path, dest: Path, *, dry_run: bool = False) -> MoveRecord:
        calls["n"] += 1
        if calls["n"] == 2:
            raise OSError("disk full")
        return real_move(src, dest, dry_run=dry_run)

    monkeypatch.setattr("mover.move_file", flaky)
    with pytest.raises(OSError):
        organize_files(tmp_path, [(first, "code"), (second, "code")])
    assert first.exists()
    assert second.exists()
    assert first.read_text(encoding="utf-8") == "1"


def test_organize_and_undo_round_trip(tmp_path: Path) -> None:
    src = _touch(tmp_path / "paper.pdf", "doc")
    batch = organize(tmp_path, dry_run=False)
    assert not src.exists()
    assert (tmp_path / "documents" / "paper.pdf").read_text(encoding="utf-8") == "doc"
    assert (tmp_path / "summary_report.txt").is_file()
    assert batch.records
    restored = undo(tmp_path)
    assert restored
    assert src.exists()
    assert src.read_text(encoding="utf-8") == "doc"
