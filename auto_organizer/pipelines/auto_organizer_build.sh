#!/usr/bin/env bash
# Auto Organizer MacBook build script (safe for SSH / iPhone Shortcuts).
# Does not push main, does not commit venv, does not sort Downloads unless asked.
set -euo pipefail

REPO_URL="${AUTOORG_REPO_URL:-https://github.com/goodfindfactory/orgaut.git}"
CLONE_DIR="${AUTOORG_CLONE_DIR:-$HOME/orgaut}"
BRANCH="${AUTOORG_BRANCH:-main}"

if [[ -d /workspace/auto_organizer && -f /workspace/auto_organizer/cli.py ]]; then
  APP_DIR=/workspace/auto_organizer
  REPO_ROOT=/workspace
elif [[ -f "$PWD/cli.py" && -f "$PWD/config.json" ]]; then
  APP_DIR=$PWD
  REPO_ROOT=$(cd "$APP_DIR/.." && pwd)
elif [[ -d "$CLONE_DIR/auto_organizer" ]]; then
  REPO_ROOT=$CLONE_DIR
  APP_DIR=$CLONE_DIR/auto_organizer
else
  git clone "$REPO_URL" "$CLONE_DIR"
  REPO_ROOT=$CLONE_DIR
  APP_DIR=$CLONE_DIR/auto_organizer
fi

cd "$REPO_ROOT"
if [[ "${AUTOORG_PULL:-1}" == 1 ]]; then
  git fetch --all
  git checkout "$BRANCH"
  git pull --ff-only origin "$BRANCH"
fi

cd "$APP_DIR"
rm -rf venv
python3 -m venv venv
# shellcheck disable=SC1091
source venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
pytest -q

if [[ -n "${ORGANIZE_PATH:-}" ]]; then
  python cli.py --path "$ORGANIZE_PATH" --dry-run
  if [[ "${ORGANIZE_APPLY:-}" == 1 ]]; then
    python cli.py --path "$ORGANIZE_PATH"
    python cli.py --path "$ORGANIZE_PATH" --report
  fi
fi

deactivate || true
echo "BUILD PIPELINE COMPLETE app=${APP_DIR} branch=${BRANCH}"
