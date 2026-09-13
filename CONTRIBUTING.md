# Contributing

This is a backyard tool. Keep it that way: small surface, real moves, tests that
touch the filesystem.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Checks

```bash
pytest -q
```

CI on `main` runs `pip install -e ".[dev]"` then `pytest -q` on Python 3.11.
If that is red, the change is not ready.

## Ground rules

- Complete code. No stubs, no TODOs left in the tree.
- Moves, not copies. Dry-run must not create directories or relocate files.
- Collision names are `_1`, `_2` on the stem — not `(1)` and not overwrites.
- Recursive scans skip the category buckets (`images`, `docs`, `code`,
  `archives`, `audio`, `video`, `other`).
- Files only. Leave directories where they are.
- Tests go in `tests/test_scanner.py`, `tests/test_organizer.py`, or
  `tests/test_report.py`. Cover the behavior you changed.

## Pull requests

Branch off `main`. Say what you moved in the yard and how you proved it
(`pytest -q` plus a dry-run if the CLI changed).
