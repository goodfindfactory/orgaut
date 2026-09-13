"""CLI entry: ``python cli.py --path <target> [--dry-run|--undo|--report]``."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from main import organize, report, undo
from utils.logger import error, info


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cli.py",
        description=(
            "Auto Organizer — scan a folder, create category directories, "
            "and safely move files. Undo and reports included."
        ),
    )
    parser.add_argument(
        "--path",
        default=".",
        help="target directory (default: current directory)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="plan moves without creating folders or relocating files",
    )
    parser.add_argument(
        "--undo",
        action="store_true",
        help="restore files from the undo log under --path",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="print the last summary_report.txt under --path",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    target = Path(args.path)

    exclusive = [args.undo, args.report]
    if sum(1 for flag in exclusive if flag) > 1:
        error("use only one of --undo or --report")
        return 2

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
        batch = organize(target, dry_run=args.dry_run)
        info(f"{'would move' if args.dry_run else 'moved'} {len(batch.records)} file(s)")
        return 0
    except (FileNotFoundError, NotADirectoryError, ValueError) as exc:
        error(str(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
