"""Human-readable summaries of organize runs."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable

from autoorg.organizer import Move
from autoorg.util import CATEGORIES


def format_report(moves: Iterable[Move], *, dry_run: bool | None = None) -> str:
    """Render a move list as a backyard report.

    When *dry_run* is omitted, the flag is taken from the first move (or
    treated as a real run if the list is empty).
    """
    moves = list(moves)
    if dry_run is None:
        dry_run = bool(moves and moves[0].dry_run)

    verb = "Would move" if dry_run else "Moved"
    skip_verb = "Would skip" if dry_run else "Skipped"

    lines: list[str] = []
    acted = [m for m in moves if not m.skipped]
    skipped = [m for m in moves if m.skipped]

    for move in acted:
        dest_name = f"{move.category}/{move.dest.name}"
        lines.append(f"{verb}: {move.src.name} -> {dest_name}")

    for move in skipped:
        why = f" ({move.reason})" if move.reason else ""
        lines.append(f"{skip_verb}: {move.src.name}{why}")

    if not lines:
        lines.append("Nothing to organize.")

    lines.append("")
    lines.append(_totals(acted, skipped, dry_run=dry_run))
    return "\n".join(lines)


def _totals(acted: list[Move], skipped: list[Move], *, dry_run: bool) -> str:
    label = "Would organize" if dry_run else "Organized"
    parts = [f"{label}: {len(acted)} file(s)"]
    counts = Counter(move.category for move in acted)
    for category in CATEGORIES:
        n = counts.get(category, 0)
        if n:
            parts.append(f"  {category}: {n}")
    extra = sorted(cat for cat in counts if cat not in CATEGORIES)
    for category in extra:
        parts.append(f"  {category}: {counts[category]}")
    if skipped:
        parts.append(f"  skipped: {len(skipped)}")
    return "\n".join(parts)


def print_report(moves: Iterable[Move], *, dry_run: bool | None = None) -> str:
    """Format and print a report. Returns the same text."""
    text = format_report(moves, dry_run=dry_run)
    print(text)
    return text
