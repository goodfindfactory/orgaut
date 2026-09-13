"""Move files into category folders with per-file rollback support."""

from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path

from folder_manager import ensure_category_folder
from utils.logger import error, info
from utils.paths import unique_path


@dataclass
class MoveRecord:
    """One completed or planned relocation."""

    src: Path
    dest: Path
    category: str
    undone: bool = False


@dataclass
class MoveBatch:
    """Moves applied in one organize run, with rollback."""

    records: list[MoveRecord] = field(default_factory=list)

    def add(self, record: MoveRecord) -> None:
        self.records.append(record)

    def rollback(self) -> list[MoveRecord]:
        """Move completed files back to their original paths (last first)."""
        restored: list[MoveRecord] = []
        for record in reversed(self.records):
            if record.undone:
                continue
            if not record.dest.exists():
                continue
            record.dest.parent.mkdir(parents=True, exist_ok=True)
            record.src.parent.mkdir(parents=True, exist_ok=True)
            dest = unique_path(record.src) if record.src.exists() else record.src
            shutil.move(str(record.dest), str(dest))
            record.undone = True
            restored.append(record)
        return restored


def plan_destination(target: Path, src: Path, category: str) -> Path:
    """Choose a collision-safe destination under the category folder."""
    folder = target / category
    return unique_path(folder / src.name)


def move_file(src: Path, dest: Path, *, dry_run: bool = False) -> MoveRecord:
    """Move one file. Dry-run only returns the planned record."""
    record = MoveRecord(src=src, dest=dest, category=dest.parent.name)
    if dry_run:
        return record
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dest))
    info(f"moved {src.name} -> {dest}")
    return record


def safe_move(src: Path | str, dest: Path | str, *, dry_run: bool = False) -> MoveRecord:
    """Master-block alias for :func:`move_file`."""
    return move_file(Path(src), Path(dest), dry_run=dry_run)


def organize_files(
    target: Path,
    items: list[tuple[Path, str]],
    *,
    dry_run: bool = False,
) -> MoveBatch:
    """Move ``(file, category)`` pairs. Rollback the batch if one move fails."""
    batch = MoveBatch()
    try:
        for src, category in items:
            if not dry_run:
                ensure_category_folder(target, category)
            dest = plan_destination(target, src, category)
            if dry_run:
                batch.add(MoveRecord(src=src, dest=dest, category=category))
                continue
            batch.add(move_file(src, dest, dry_run=False))
    except Exception as exc:
        error(f"move failed, rolling back batch: {exc}")
        if not dry_run:
            batch.rollback()
        raise
    return batch


if __name__ == "__main__":
    print("mover OK", MoveRecord, safe_move)
