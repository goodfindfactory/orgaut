#!/bin/bash
# Double-click in Finder to install Auto Organizer on this Mac.
set -euo pipefail

HERE=$(cd "$(dirname "$0")" && pwd)
cd "$HERE"

if command -v xattr >/dev/null 2>&1; then
  xattr -dr com.apple.quarantine "$HERE" 2>/dev/null || true
fi

INSTALL="$HERE/auto_organizer/mac/install-mac.sh"
if [[ ! -f "$INSTALL" ]]; then
  if command -v osascript >/dev/null 2>&1; then
    osascript -e 'display dialog "install-mac.sh is missing. Unzip AutoOrganizer-Mac.zip first and keep this file next to the auto_organizer folder." buttons {"OK"} default button 1' || true
  else
    echo "install-mac.sh is missing. Unzip AutoOrganizer-Mac.zip first." >&2
  fi
  exit 1
fi

chmod +x "$INSTALL" \
  "$HERE/auto_organizer/mac/aoctl" \
  "$HERE/auto_organizer/mac/AutoOrganizer.app/Contents/MacOS/launcher" \
  2>/dev/null || true

export AUTOORG_INSTALL_HOME=1
if bash "$INSTALL"; then
  if command -v osascript >/dev/null 2>&1; then
    osascript -e 'display dialog "Auto Organizer is installed.\n\nApp: ~/Applications/AutoOrganizer.app\nTerminal: aoctl status" buttons {"OK"} default button 1' || true
  fi
  if [[ "$(uname -s)" == Darwin ]]; then
    open "$HOME/Applications" 2>/dev/null || true
  fi
  exit 0
fi

if command -v osascript >/dev/null 2>&1; then
  osascript -e "display dialog \"Install failed. Open Terminal and run:\\n\\nbash $INSTALL\" buttons {\"OK\"} default button 1" || true
fi
exit 1
