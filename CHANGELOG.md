# Changelog

All notable changes to autoorg live here.

## Unreleased

- Live demo: https://goodfindfactory.github.io/orgaut/
- Mac zip: `bash auto_organizer/mac/package-mac-zip.sh` writes `dist/AutoOrganizer-Mac.zip`
- Finder installer: `Install Auto Organizer.command` copies the zip tree to `~/orgaut`
- GitHub Actions **Mac zip archive** uploads the zip and attaches it to `v*` / `mac-v*` releases

## 0.1.0 — 2026-09-13

First backyard cut.

- CLI: `autoorg PATH [--dry-run] [--recursive]`
- Scan files only; non-recursive by default
- Move (not copy) into `images/`, `docs/`, `code/`, `archives/`, `audio/`, `video/`, `other/`
- Collision-safe destinations: `name_1.ext`, `name_2.ext`, …
- Recursive mode skips category directories so already-sorted files stay put
- Dry-run prints the plan without touching the tree
- pytest suite for scanner, organizer, and report
