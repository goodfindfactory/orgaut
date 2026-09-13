"""Write summary_report.txt for an organize or undo run."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

from file_types import load_config
from mover import MoveRecord
from utils.logger import info
from utils.paths import safe_join


def report_path(target: Path, name: str | None = None) -> Path:
    if name is None:
        name = load_config()["report_file"]
    return safe_join(target, name)


def write_report(
    target: Path,
    records: list[MoveRecord],
    *,
    dry_run: bool = False,
    action: str = "organize",
    report_name: str | None = None,
) -> Path:
    """Write a human-readable summary next to the target folder."""
    path = report_path(target, report_name)
    verb = "Would move" if dry_run else ("Restored" if action == "undo" else "Moved")
    counts = Counter(record.category for record in records if record.category)
    lines = [
        "Auto Organizer summary",
        f"target: {target}",
        f"action: {action}",
        f"dry_run: {dry_run}",
        f"count: {len(records)}",
        "",
    ]
    if counts:
        lines.append("by category:")
        for category, n in sorted(counts.items()):
            lines.append(f"  {category}: {n}")
        lines.append("")
    for record in records:
        lines.append(f"{verb}: {record.src} -> {record.dest}")
    if not records:
        lines.append("Nothing to do.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    info(f"report written to {path}")
    return path


def read_report(target: Path, name: str | None = None) -> str:
    path = report_path(target, name)
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")
