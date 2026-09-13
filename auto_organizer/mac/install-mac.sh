#!/usr/bin/env bash
# Install Auto Organizer on this Mac: copy zip/git tree to ~/orgaut, venv, aoctl, app.
set -euo pipefail

REPO_URL="${AUTOORG_REPO_URL:-https://github.com/goodfindfactory/orgaut.git}"
HOME_INSTALL="${AUTOORG_CLONE_DIR:-$HOME/orgaut}"

if [[ -f "$(cd "$(dirname "$0")/.." && pwd)/cli.py" ]]; then
  APP_DIR=$(cd "$(dirname "$0")/.." && pwd)
  REPO_ROOT=$(cd "$APP_DIR/.." && pwd)
elif [[ -d "$HOME_INSTALL/auto_organizer" ]]; then
  REPO_ROOT=$HOME_INSTALL
  APP_DIR=$HOME_INSTALL/auto_organizer
else
  git clone "$REPO_URL" "$HOME_INSTALL"
  REPO_ROOT=$HOME_INSTALL
  APP_DIR=$HOME_INSTALL/auto_organizer
fi

copy_tree_to_home() {
  local src=$1
  local dest=$2
  mkdir -p "$dest"
  if command -v rsync >/dev/null 2>&1; then
    rsync -a \
      --exclude='venv/' \
      --exclude='.venv/' \
      --exclude='.git/' \
      --exclude='__pycache__/' \
      --exclude='.pytest_cache/' \
      --exclude='dist/' \
      "$src/" "$dest/"
  else
    tar -C "$src" \
      --exclude='venv' \
      --exclude='.venv' \
      --exclude='.git' \
      --exclude='__pycache__' \
      --exclude='.pytest_cache' \
      --exclude='dist' \
      -cf - . | tar -C "$dest" -xf -
  fi
}

# Zip / Downloads copies land in ~/orgaut so aoctl and the .app keep a stable path.
should_home_install=0
if [[ "${AUTOORG_INSTALL_HOME:-}" == 1 ]]; then
  should_home_install=1
elif [[ "$(uname -s)" == Darwin && -f "$REPO_ROOT/Install Auto Organizer.command" && "$REPO_ROOT" != "$HOME_INSTALL" ]]; then
  should_home_install=1
fi

if [[ "$should_home_install" == 1 && "$REPO_ROOT" != "$HOME_INSTALL" ]]; then
  echo "Copying Auto Organizer to $HOME_INSTALL"
  copy_tree_to_home "$REPO_ROOT" "$HOME_INSTALL"
  REPO_ROOT=$HOME_INSTALL
  APP_DIR=$HOME_INSTALL/auto_organizer
fi

if [[ ! -f "$APP_DIR/cli.py" ]]; then
  echo "install-mac: auto_organizer/cli.py not found under $APP_DIR" >&2
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "install-mac: python3 is required (Xcode CLT, python.org, or brew install python python-tk)" >&2
  exit 1
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
  "$APP_DIR/mac/package-mac-zip.sh" \
  "$APP_DIR/mac/Install Auto Organizer.command" \
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
