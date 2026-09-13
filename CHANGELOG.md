# Changelog

All notable changes to autoorg live here.

## 0.1.0 — 2026-09-13

First backyard cut.

- CLI: `autoorg PATH [--dry-run] [--recursive]`
- Scan files only; non-recursive by default
- Move (not copy) into `images/`, `docs/`, `code/`, `archives/`, `audio/`, `video/`, `other/`
- Collision-safe destinations: `name_1.ext`, `name_2.ext`, …
- Recursive mode skips category directories so already-sorted files stay put
- Dry-run prints the plan without touching the tree
- pytest suite for scanner, organizer, and report
