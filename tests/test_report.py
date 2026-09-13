"""Report formatting for real runs and dry-runs."""

from __future__ import annotations

from pathlib import Path

from autoorg.organizer import Move, organize
from autoorg.report import format_report, print_report


def _move(
    name: str,
    category: str,
    *,
    dry_run: bool = False,
    skipped: bool = False,
    reason: str = "",
) -> Move:
    src = Path("/inbox") / name
    dest = Path("/root") / category / name
    return Move(
        src=src,
        dest=dest,
        category=category,
        dry_run=dry_run,
        skipped=skipped,
        reason=reason,
    )


def test_format_report_real_run_lists_moves_and_totals() -> None:
    moves = [
        _move("a.jpg", "images"),
        _move("b.png", "images"),
        _move("c.pdf", "docs"),
    ]

    text = format_report(moves)

    assert "Moved: a.jpg -> images/a.jpg" in text
    assert "Moved: b.png -> images/b.png" in text
    assert "Moved: c.pdf -> docs/c.pdf" in text
    assert "Would move" not in text
    assert "Organized: 3 file(s)" in text
    assert "  images: 2" in text
    assert "  docs: 1" in text
    assert "audio:" not in text


def test_format_report_dry_run_uses_conditional_verbs() -> None:
    moves = [
        _move("track.mp3", "audio", dry_run=True),
        _move("film.mov", "video", dry_run=True),
    ]

    text = format_report(moves)

    assert "Would move: track.mp3 -> audio/track.mp3" in text
    assert "Would move: film.mov -> video/film.mov" in text
    assert "Would organize: 2 file(s)" in text
    assert "Moved:" not in text
    assert "Organized:" not in text


def test_format_report_dry_run_flag_overrides_move_flag() -> None:
    moves = [_move("x.py", "code", dry_run=False)]

    text = format_report(moves, dry_run=True)

    assert "Would move: x.py -> code/x.py" in text


def test_format_report_empty() -> None:
    text = format_report([])

    assert "Nothing to organize." in text
    assert "Organized: 0 file(s)" in text


def test_format_report_includes_skips() -> None:
    moves = [
        _move("ok.zip", "archives"),
        _move(
            "stay.txt",
            "docs",
            skipped=True,
            reason="already in category folder",
        ),
    ]

    text = format_report(moves)

    assert "Moved: ok.zip -> archives/ok.zip" in text
    assert "Skipped: stay.txt (already in category folder)" in text
    assert "  skipped: 1" in text


def test_print_report_writes_stdout(capsys: object) -> None:
    moves = [_move("clip.webm", "video")]

    returned = print_report(moves)
    printed = capsys.readouterr().out

    assert returned in printed
    assert "Moved: clip.webm -> video/clip.webm" in printed


def test_report_matches_organizer_dry_run(tmp_path: Path) -> None:
    (tmp_path / "pic.jpeg").write_text("j", encoding="utf-8")
    (tmp_path / "notes.md").write_text("m", encoding="utf-8")

    moves = organize(tmp_path, dry_run=True)
    text = format_report(moves, dry_run=True)

    assert "Would move: pic.jpeg -> images/pic.jpeg" in text
    assert "Would move: notes.md -> docs/notes.md" in text
    assert "Would organize: 2 file(s)" in text
    assert (tmp_path / "pic.jpeg").exists()
    assert (tmp_path / "notes.md").exists()
