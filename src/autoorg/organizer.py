"""Move scanned files into category folders."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path

from autoorg.scanner import scan
from autoorg.util import category_for, unique_destination


@dataclass(frozen=True)
class Move:
    """One planned or completed relocation."""

    src: Path
    dest: Path
    category: str
    dry_run: bool
    skipped: bool = False
    reason: str = ""


def organize(
    root: Path | str,
    files: list[Path] | None = None,
    *,
    dry_run: bool = False,
    recursive: bool = False,
) -> list[Move]:
    """Move *files* under *root* into category folders.

    Destination folders (`images/`, `docs/`, …) are created at *root*.
    Files are moved, never copied. When *dry_run* is true, no directories
    are created and no files are relocated; destinations are still
    collision-resolved as if earlier moves in this batch had happened.

    If *files* is omitted, the tree is scanned first (same *recursive*
    rule as :func:`autoorg.scanner.scan`).
    """
    root = Path(root)
    if files is None:
        files = scan(root, recursive=recursive)

    reserved: set[Path] = set()
    moves: list[Move] = []

    for src in files:
        src = Path(src)
        if not src.is_file() and not dry_run:
            moves.append(
                Move(
                    src=src,
                    dest=src,
                    category=category_for(src),
                    dry_run=dry_run,
                    skipped=True,
                    reason="not a file",
                )
            )
            continue

        category = category_for(src)
        dest_dir = root / category

        try:
            already_home = src.parent.resolve() == dest_dir.resolve()
        except OSError:
            already_home = src.parent == dest_dir

        if already_home:
            reserved.add(src)
            moves.append(
                Move(
                    src=src,
                    dest=src,
                    category=category,
                    dry_run=dry_run,
                    skipped=True,
                    reason="already in category folder",
                )
            )
            continue

        dest = unique_destination(dest_dir, src.name, reserved)
        reserved.add(dest)

        if not dry_run:
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dest))

        moves.append(Move(src=src, dest=dest, category=category, dry_run=dry_run))

    return moves
