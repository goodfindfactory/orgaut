"""Organizer: categories, move-not-copy, dry-run, collision suffixes."""

from __future__ import annotations

from pathlib import Path

from autoorg.main import main
from autoorg.organizer import organize
from autoorg.util import category_for, unique_destination


def _touch(path: Path, text: str = "payload") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_category_for_known_and_unknown() -> None:
    assert category_for("shot.JPG") == "images"
    assert category_for("notes.PDF") == "docs"
    assert category_for("app.py") == "code"
    assert category_for("pack.tar.gz") == "archives"
    assert category_for("song.mp3") == "audio"
    assert category_for("clip.mkv") == "video"
    assert category_for("weird.xyz") == "other"
    assert category_for("LICENSE") == "other"
    assert category_for(".gitignore") == "other"


def test_organize_moves_into_category_folders(tmp_path: Path) -> None:
    photo = _touch(tmp_path / "photo.jpg", "img")
    paper = _touch(tmp_path / "paper.pdf", "doc")
    script = _touch(tmp_path / "script.py", "code")
    archive = _touch(tmp_path / "bundle.zip", "zip")
    song = _touch(tmp_path / "song.mp3", "audio")
    clip = _touch(tmp_path / "clip.mp4", "video")
    odd = _touch(tmp_path / "notes.xyz", "???")

    moves = organize(tmp_path)

    assert not photo.exists()
    assert not paper.exists()
    assert (tmp_path / "images" / "photo.jpg").read_text(encoding="utf-8") == "img"
    assert (tmp_path / "docs" / "paper.pdf").read_text(encoding="utf-8") == "doc"
    assert (tmp_path / "code" / "script.py").read_text(encoding="utf-8") == "code"
    assert (tmp_path / "archives" / "bundle.zip").read_text(encoding="utf-8") == "zip"
    assert (tmp_path / "audio" / "song.mp3").read_text(encoding="utf-8") == "audio"
    assert (tmp_path / "video" / "clip.mp4").read_text(encoding="utf-8") == "video"
    assert (tmp_path / "other" / "notes.xyz").read_text(encoding="utf-8") == "???"

    by_src = {m.src.name: m for m in moves if not m.skipped}
    assert by_src["photo.jpg"].category == "images"
    assert by_src["paper.pdf"].dest == tmp_path / "docs" / "paper.pdf"
    assert {p.name for p in (tmp_path.iterdir()) if p.is_file()} == set()


def test_organize_moves_not_copies(tmp_path: Path) -> None:
    src = _touch(tmp_path / "solo.png", "only-once")
    organize(tmp_path, [src])

    dest = tmp_path / "images" / "solo.png"
    assert dest.is_file()
    assert not src.exists()
    assert dest.read_text(encoding="utf-8") == "only-once"


def test_dry_run_does_not_move_or_create_dirs(tmp_path: Path) -> None:
    src = _touch(tmp_path / "hold.pdf", "stay")
    before = {p.name for p in tmp_path.iterdir()}

    moves = organize(tmp_path, dry_run=True)

    assert src.exists()
    assert src.read_text(encoding="utf-8") == "stay"
    assert {p.name for p in tmp_path.iterdir()} == before
    assert not (tmp_path / "docs").exists()
    assert len(moves) == 1
    assert moves[0].dry_run is True
    assert moves[0].dest == tmp_path / "docs" / "hold.pdf"


def test_collision_suffixes_increment(tmp_path: Path) -> None:
    dest_dir = tmp_path / "images"
    dest_dir.mkdir()
    _touch(dest_dir / "photo.jpg", "old")
    incoming = _touch(tmp_path / "photo.jpg", "new")
    extra = _touch(tmp_path / "inbox" / "photo.jpg", "newer")

    first = unique_destination(dest_dir, "photo.jpg")
    assert first == dest_dir / "photo_1.jpg"

    moves = organize(tmp_path, [incoming, extra])
    dests = sorted(m.dest.name for m in moves if not m.skipped)

    assert dests == ["photo_1.jpg", "photo_2.jpg"]
    assert (dest_dir / "photo.jpg").read_text(encoding="utf-8") == "old"
    assert (dest_dir / "photo_1.jpg").read_text(encoding="utf-8") == "new"
    assert (dest_dir / "photo_2.jpg").read_text(encoding="utf-8") == "newer"
    assert not incoming.exists()
    assert not extra.exists()


def test_dry_run_collision_plan_uses_reserved_names(tmp_path: Path) -> None:
    dest_dir = tmp_path / "images"
    dest_dir.mkdir()
    _touch(dest_dir / "shot.png", "existing")
    a = _touch(tmp_path / "shot.png", "a")
    b = _touch(tmp_path / "more" / "shot.png", "b")

    moves = organize(tmp_path, [a, b], dry_run=True)
    dests = [m.dest.name for m in moves]

    assert dests == ["shot_1.png", "shot_2.png"]
    assert a.exists() and b.exists()
    assert (dest_dir / "shot.png").read_text(encoding="utf-8") == "existing"
    assert list(dest_dir.iterdir()) == [dest_dir / "shot.png"]


def test_recursive_organize_skips_category_dirs(tmp_path: Path) -> None:
    loose = _touch(tmp_path / "deep" / "pic.gif", "gif")
    already = _touch(tmp_path / "images" / "old.gif", "stay")

    moves = organize(tmp_path, recursive=True)
    acted = [m for m in moves if not m.skipped]

    assert len(acted) == 1
    assert acted[0].src == loose
    assert (tmp_path / "images" / "pic.gif").read_text(encoding="utf-8") == "gif"
    assert already.exists()
    assert already.read_text(encoding="utf-8") == "stay"


def test_already_in_category_folder_is_skipped(tmp_path: Path) -> None:
    home = _touch(tmp_path / "docs" / "manual.txt", "keep")

    moves = organize(tmp_path, [home])

    assert home.exists()
    assert moves[0].skipped is True
    assert "already" in moves[0].reason


def test_cli_dry_run_and_real_run(tmp_path: Path, capsys: object) -> None:
    _touch(tmp_path / "song.wav", "wave")

    assert main([str(tmp_path), "--dry-run"]) == 0
    out = capsys.readouterr().out
    assert "Would move" in out
    assert (tmp_path / "song.wav").exists()
    assert not (tmp_path / "audio").exists()

    assert main([str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "Moved" in out
    assert not (tmp_path / "song.wav").exists()
    assert (tmp_path / "audio" / "song.wav").is_file()


def test_cli_rejects_missing_and_file_paths(tmp_path: Path, capsys: object) -> None:
    assert main([str(tmp_path / "missing")]) == 2
    file_path = _touch(tmp_path / "not-a-dir.txt")
    assert main([str(file_path)]) == 2
    err = capsys.readouterr().err
    assert "does not exist" in err or "not a directory" in err
