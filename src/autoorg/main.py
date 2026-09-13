"""CLI entry: ``autoorg PATH [--dry-run] [--recursive]``."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from autoorg import __version__
from autoorg.organizer import organize
from autoorg.report import format_report
from autoorg.scanner import scan


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="autoorg",
        description=(
            "Move files in PATH into images/docs/code/archives/audio/video/other "
            "by extension. Moves, never copies."
        ),
    )
    parser.add_argument(
        "path",
        type=Path,
        help="directory to organize",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print the plan without moving anything",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="walk nested folders; skip category directories",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"autoorg {__version__}",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    root: Path = args.path

    if not root.exists():
        print(f"autoorg: path does not exist: {root}", file=sys.stderr)
        return 2
    if not root.is_dir():
        print(f"autoorg: not a directory: {root}", file=sys.stderr)
        return 2

    files = scan(root, recursive=args.recursive)
    moves = organize(root, files, dry_run=args.dry_run)
    print(format_report(moves, dry_run=args.dry_run))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
