"""Persist move history under ``_undo`` and restore files on demand."""

from __future__ import annotations

import json
import shutil
import time
from pathlib import Path

from file_types import load_config
from folder_manager import ensure_undo_folder
from mover import MoveBatch, MoveRecord
from utils.logger import info, warn
from utils.paths import unique_path


MANIFEST_NAME = "manifest.json"


def manifest_path(target: Path, undo_name: str | None = None) -> Path:
    if undo_name is None:
        undo_name = load_config()["undo_folder"]
    return ensure_undo_folder(target, undo_name) / MANIFEST_NAME


def load_manifest(target: Path, undo_name: str | None = None) -> list[dict]:
    path = manifest_path(target, undo_name)
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        return []
    return data


def save_batch(target: Path, batch: MoveBatch, undo_name: str | None = None) -> Path:
    """Append this batch to the undo manifest. No file copies — paths only."""
    entries = load_manifest(target, undo_name)
    stamp = time.strftime("%Y-%m-%dT%H:%M:%S")
    for record in batch.records:
        entries.append(
            {
                "src": str(record.src),
                "dest": str(record.dest),
                "category": record.category,
                "at": stamp,
            }
        )
    path = manifest_path(target, undo_name)
    path.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")
    info(f"undo log written to {path}")
    return path


def restore_all(target: Path, undo_name: str | None = None) -> list[MoveRecord]:
    """Move organized files back to their original locations."""
    entries = load_manifest(target, undo_name)
    if not entries:
        warn("nothing to undo")
        return []

    restored: list[MoveRecord] = []
    for entry in reversed(entries):
        src = Path(entry["src"])
        dest = Path(entry["dest"])
        if not dest.exists():
            warn(f"skip undo, missing {dest}")
            continue
        src.parent.mkdir(parents=True, exist_ok=True)
        back = unique_path(src) if src.exists() else src
        shutil.move(str(dest), str(back))
        restored.append(
            MoveRecord(src=dest, dest=back, category=entry.get("category", ""), undone=True)
        )
        info(f"restored {back}")

    # Drop restored entries; keep ones we could not reverse.
    restored_dests = {str(r.src) for r in restored}
    leftover = [e for e in entries if e.get("dest") not in restored_dests]
    path = manifest_path(target, undo_name)
    path.write_text(json.dumps(leftover, indent=2) + "\n", encoding="utf-8")
    return restored
