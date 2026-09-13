#!/usr/bin/env bash
# Install Auto Organizer on this Mac: venv, aoctl, optional ~/Applications app.
set -euo pipefail

REPO_URL="${AUTOORG_REPO_URL:-https://github.com/goodfindfactory/orgaut.git}"
CLONE_DIR="${AUTOORG_CLONE_DIR:-$HOME/orgaut}"

if [[ -f "$(cd "$(dirname "$0")/.." && pwd)/cli.py" ]]; then
  APP_DIR=$(cd "$(dirname "$0")/.." && pwd)
  REPO_ROOT=$(cd "$APP_DIR/.." && pwd)
elif [[ -d "$CLONE_DIR/auto_organizer" ]]; then
  REPO_ROOT=$CLONE_DIR
  APP_DIR=$CLONE_DIR/auto_organizer
else
  git clone "$REPO_URL" "$CLONE_DIR"
  REPO_ROOT=$CLONE_DIR
  APP_DIR=$CLONE_DIR/auto_organizer
fi

echo "Installing Auto Organizer from $APP_DIR"

cd "$APP_DIR"
python3 -m venv venv
# shellcheck disable=SC1091
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
pytest -q

chmod +x "$APP_DIR/mac/aoctl" \
  "$APP_DIR/mac/install-mac.sh" \
  "$APP_DIR/mac/AutoOrganizer.app/Contents/MacOS/launcher" \
  "$APP_DIR/pipelines/auto_organizer_build.sh" 2>/dev/null || true

BIN_DIR=$HOME/.local/bin
mkdir -p "$BIN_DIR"
ln -sfn "$APP_DIR/mac/aoctl" "$BIN_DIR/aoctl"

if [[ "$(uname -s)" == Darwin ]]; then
  mkdir -p "$HOME/Applications"
  rm -rf "$HOME/Applications/AutoOrganizer.app"
  cp -R "$APP_DIR/mac/AutoOrganizer.app" "$HOME/Applications/AutoOrganizer.app"
  echo "App copied to ~/Applications/AutoOrganizer.app"
fi

cat <<TXT

Install complete.

Terminal:
  export PATH="\$HOME/.local/bin:\$PATH"
  aoctl status
  aoctl dry-run
  aoctl organize ~/Downloads

Double-click:
  ~/Applications/AutoOrganizer.app   (Mac only)

iPhone (after System Settings → General → Sharing → Remote Login):
  Shortcuts → Run Script Over SSH → this Mac's user and LAN IP
  Script:  \$HOME/orgaut/auto_organizer/mac/aoctl status

Do not put your Mac password in this repo. Prefer SSH keys.

Repo: $REPO_ROOT
TXT
