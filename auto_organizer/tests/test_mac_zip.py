"""Mac zip packager: AutoOrganizer-Mac.zip contents and permissions."""

from __future__ import annotations

import os
import stat
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PACKAGER = ROOT / "auto_organizer" / "mac" / "package-mac-zip.sh"
NAME = "AutoOrganizer-Mac"


def test_demo_page_uses_config_categories() -> None:
    html = (ROOT / "docs" / "index.html").read_text(encoding="utf-8")
    import json

    config = json.loads((ROOT / "auto_organizer" / "config.json").read_text(encoding="utf-8"))
    for category, extensions in config["categories"].items():
        assert f'data-cat="{category}"' in html
        for ext in extensions:
            assert ext in html


def test_packager_script_exists_and_is_executable() -> None:
    assert PACKAGER.is_file()
    assert os.access(PACKAGER, os.X_OK)
    command = ROOT / "auto_organizer" / "mac" / "Install Auto Organizer.command"
    assert command.is_file()
    text = command.read_bytes()
    assert text.startswith(b"#!/bin/bash")
    assert b"\r\n" not in text


def test_package_mac_zip_contains_mac_bundle(tmp_path: Path) -> None:
    if not sys.platform.startswith("linux") and sys.platform != "darwin":
        pytest.skip("zip packager is for Unix")
    dest_dir = tmp_path / "out"
    dest_dir.mkdir()
    env = os.environ.copy()
    env["AUTOORG_ZIP_OUT"] = str(dest_dir)
    env["AUTOORG_ZIP_NAME"] = NAME
    subprocess.run(["bash", str(PACKAGER)], check=True, env=env, cwd=ROOT)

    archive = dest_dir / f"{NAME}.zip"
    assert archive.is_file()
    assert archive.stat().st_size > 1000

    with zipfile.ZipFile(archive) as zf:
        names = set(zf.namelist())
        required = {
            f"{NAME}/INSTALL-MAC.txt",
            f"{NAME}/Install Auto Organizer.command",
            f"{NAME}/auto_organizer/cli.py",
            f"{NAME}/auto_organizer/gui.py",
            f"{NAME}/auto_organizer/config.json",
            f"{NAME}/auto_organizer/mac/install-mac.sh",
            f"{NAME}/auto_organizer/mac/aoctl",
            f"{NAME}/auto_organizer/mac/AutoOrganizer.app/Contents/Info.plist",
            f"{NAME}/auto_organizer/mac/AutoOrganizer.app/Contents/MacOS/launcher",
            f"{NAME}/src/autoorg/main.py",
            f"{NAME}/LICENSE",
            f"{NAME}/README.md",
            f"{NAME}/requirements.txt",
        }
        missing = sorted(path for path in required if path not in names)
        assert not missing, missing
        assert not any("/.git/" in name or name.endswith("/.git") for name in names)
        assert not any("/venv/" in name for name in names)
        assert not any("__pycache__" in name for name in names)
        assert not any(name.endswith("/dist/") or "/dist/" in name for name in names)
        assert not any(name.endswith("docs/AutoOrganizer-Mac.zip") for name in names)

        command_info = zf.getinfo(f"{NAME}/Install Auto Organizer.command")
        mode = stat.S_IMODE(command_info.external_attr >> 16)
        assert mode & stat.S_IXUSR, hex(command_info.external_attr)

        launcher_info = zf.getinfo(
            f"{NAME}/auto_organizer/mac/AutoOrganizer.app/Contents/MacOS/launcher"
        )
        launcher_mode = stat.S_IMODE(launcher_info.external_attr >> 16)
        assert launcher_mode & stat.S_IXUSR
