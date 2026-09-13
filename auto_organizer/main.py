"""Orchestrate scan, categorize, move, undo, and reporting."""

from __future__ import annotations

import argparse
from pathlib import Path

from file_types import category_for, load_config
from folder_manager import ensure_all_category_folders
from mover import MoveBatch, MoveRecord, organize_files
from report import read_report, write_report
from undo import restore_all, save_batch
from utils.logger import enable_debug, info, warn
from utils.paths import is_reserved_name, resolve_dir


def scan_files(target: Path, undo_name: str, categories: dict[str, list[str]]) -> list[Path]:
    """Loose files in *target* only (not recursive). Skip dirs and reserved names."""
    files: list[Path] = []
    reserved = {name.lower() for name in categories}
    reserved.add(undo_name.lower())
    for child in sorted(target.iterdir(), key=lambda p: p.name.lower()):
        if child.is_dir():
            continue
        if child.name.lower() == "summary_report.txt":
            continue
        if is_reserved_name(child.name, undo_name):
            continue
        if child.parent.name.lower() in reserved:
            continue
        files.append(child)
    return files


def categorize(
    files: list[Path], categories: dict[str, list[str]]
) -> tuple[list[tuple[Path, str]], list[Path]]:
    """Split files into (path, category) pairs and leftovers."""
    planned: list[tuple[Path, str]] = []
    unknown: list[Path] = []
    for path in files:
        category = category_for(path, categories)
        if category is None:
            unknown.append(path)
            continue
        planned.append((path, category))
    return planned, unknown


def organize(path: str | Path, *, dry_run: bool = False, write: bool = True) -> MoveBatch:
    """Scan *path*, create folders, move categorized files, write undo + report."""
    target = resolve_dir(path)
    if not target.is_dir():
        raise NotADirectoryError(f"not a directory: {target}")

    config = load_config()
    categories = config["categories"]
    undo_name = config["undo_folder"]

    files = scan_files(target, undo_name, categories)
    planned, unknown = categorize(files, categories)
    for leftover in unknown:
        warn(f"skipped (unknown type): {leftover.name}")

    if not dry_run:
        ensure_all_category_folders(target, categories)

    batch = organize_files(target, planned, dry_run=dry_run)
    if not dry_run and batch.records:
        save_batch(target, batch, undo_name)
    if write and not dry_run:
        write_report(target, batch.records, dry_run=False, action="organize")
    info(f"organized {len(batch.records)} file(s) in {target}")
    return batch


def undo(path: str | Path, *, write: bool = True) -> list[MoveRecord]:
    """Restore the last organized files under *path*."""
    target = resolve_dir(path)
    restored = restore_all(target)
    if write:
        write_report(target, restored, dry_run=False, action="undo")
    return restored


def report(path: str | Path) -> str:
    """Return the existing summary report text (writes nothing)."""
    target = resolve_dir(path)
    text = read_report(target)
    if not text:
        warn("no report yet — run an organize first")
    return text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="Auto Organizer orchestrator. Default is --dry-run when run as a script.",
    )
    parser.add_argument("--path", default=".", help="target directory")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="plan only (default when no --apply)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="actually move files (required for a real run from main.py)",
    )
    parser.add_argument("--undo", action="store_true")
    parser.add_argument("--report", action="store_true")
    parser.add_argument("--debug", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Script entry. Defaults to dry-run so `python main.py` cannot trash the app tree."""
    args = build_parser().parse_args(argv)
    if args.debug:
        enable_debug()
        info("debug on")
    target = Path(args.path)
    try:
        if args.undo:
            restored = undo(target)
            info(f"undo restored {len(restored)} file(s)")
            return 0
        if args.report:
            text = report(target)
            if text:
                print(text, end="" if text.endswith("\n") else "\n")
            return 0
        dry_run = True if not args.apply else args.dry_run
        if args.apply and args.dry_run:
            dry_run = True
        batch = organize(target, dry_run=dry_run)
        info(f"{'would move' if dry_run else 'moved'} {len(batch.records)} file(s)")
        return 0
    except (FileNotFoundError, NotADirectoryError, ValueError) as exc:
        from utils.logger import error

        error(str(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
