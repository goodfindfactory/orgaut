#!/usr/bin/env bash
# Build AutoOrganizer-Mac.zip — Finder-ready archive of the whole repo.
# Does not include .git, venvs, caches, or prior dist zips.
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/../.." && pwd)
NAME="${AUTOORG_ZIP_NAME:-AutoOrganizer-Mac}"
OUT_DIR="${AUTOORG_ZIP_OUT:-$ROOT/dist}"
DEST="$OUT_DIR/${NAME}.zip"

if ! command -v zip >/dev/null 2>&1; then
  echo "package-mac-zip: zip is required" >&2
  exit 1
fi

STAGING=$(mktemp -d)
trap 'rm -rf "$STAGING"' EXIT
BUNDLE="$STAGING/$NAME"
mkdir -p "$BUNDLE" "$OUT_DIR"

copy_tree() {
  local src=$1
  local dest=$2
  if command -v rsync >/dev/null 2>&1; then
    rsync -a \
      --exclude='.git/' \
      --exclude='.git' \
      --exclude='venv/' \
      --exclude='.venv/' \
      --exclude='__pycache__/' \
      --exclude='.pytest_cache/' \
      --exclude='dist/' \
      --exclude='build/' \
      --exclude='*.egg-info/' \
      --exclude='.DS_Store' \
      --exclude='_undo/' \
      --exclude='summary_report.txt' \
      --exclude='AutoOrganizer-Mac.zip' \
      --exclude='docs/AutoOrganizer-Mac.zip' \
      --exclude='auto_organizer_prod.zip' \
      "$src/" "$dest/"
  else
    tar -C "$src" \
      --exclude='.git' \
      --exclude='venv' \
      --exclude='.venv' \
      --exclude='__pycache__' \
      --exclude='.pytest_cache' \
      --exclude='dist' \
      --exclude='build' \
      --exclude='.DS_Store' \
      --exclude='_undo' \
      --exclude='AutoOrganizer-Mac.zip' \
      --exclude='docs/AutoOrganizer-Mac.zip' \
      -cf - . | tar -C "$dest" -xf -
  fi
}

copy_tree "$ROOT" "$BUNDLE"

# Finder-facing files sit at the zip root (next to auto_organizer/).
cp "$ROOT/auto_organizer/mac/Install Auto Organizer.command" "$BUNDLE/"
cp "$ROOT/auto_organizer/mac/INSTALL-MAC.txt" "$BUNDLE/"

chmod +x \
  "$BUNDLE/Install Auto Organizer.command" \
  "$BUNDLE/auto_organizer/mac/aoctl" \
  "$BUNDLE/auto_organizer/mac/install-mac.sh" \
  "$BUNDLE/auto_organizer/mac/package-mac-zip.sh" \
  "$BUNDLE/auto_organizer/mac/AutoOrganizer.app/Contents/MacOS/launcher" \
  "$BUNDLE/auto_organizer/pipelines/auto_organizer_build.sh"

# Drop leftover junk the copy might have kept.
find "$BUNDLE" -name '.DS_Store' -delete
find "$BUNDLE" -name '__pycache__' -type d -exec rm -rf {} +
find "$BUNDLE" -name '.pytest_cache' -type d -exec rm -rf {} +
rm -rf "$BUNDLE/.git" "$BUNDLE/dist" "$BUNDLE/auto_organizer/venv"

# LF-only text so macOS .command files run from Finder.
if command -v sed >/dev/null 2>&1; then
  sed -i 's/\r$//' \
    "$BUNDLE/Install Auto Organizer.command" \
    "$BUNDLE/auto_organizer/mac/install-mac.sh" \
    "$BUNDLE/auto_organizer/mac/aoctl" \
    "$BUNDLE/auto_organizer/mac/AutoOrganizer.app/Contents/MacOS/launcher" \
    "$BUNDLE/INSTALL-MAC.txt"
fi

rm -f "$DEST"
# -X: no extra extra fields. -y: store symlinks. Unix perms stay on the entries.
(cd "$STAGING" && zip -r -X -y "$DEST" "$NAME")

python3 - "$DEST" "$NAME" <<'PY'
import sys
import zipfile

dest, name = sys.argv[1], sys.argv[2]
required = {
    f"{name}/INSTALL-MAC.txt",
    f"{name}/Install Auto Organizer.command",
    f"{name}/auto_organizer/cli.py",
    f"{name}/auto_organizer/gui.py",
    f"{name}/auto_organizer/config.json",
    f"{name}/auto_organizer/mac/install-mac.sh",
    f"{name}/auto_organizer/mac/aoctl",
    f"{name}/auto_organizer/mac/AutoOrganizer.app/Contents/Info.plist",
    f"{name}/auto_organizer/mac/AutoOrganizer.app/Contents/MacOS/launcher",
    f"{name}/src/autoorg/main.py",
    f"{name}/LICENSE",
    f"{name}/README.md",
    f"{name}/requirements.txt",
}
with zipfile.ZipFile(dest) as zf:
    names = set(zf.namelist())
missing = sorted(path for path in required if path not in names)
if missing:
    raise SystemExit("package-mac-zip: missing " + ", ".join(missing))
banned = [n for n in names if "/.git/" in n or n.endswith("/.git") or "/venv/" in n]
if banned:
    raise SystemExit("package-mac-zip: zip contains excluded paths")
print(f"packed {len(names)} entries -> {dest}")
PY

echo "MAC ZIP READY $DEST"
ls -lh "$DEST"
