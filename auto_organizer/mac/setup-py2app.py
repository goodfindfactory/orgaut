"""Optional py2app recipe. Run on a Mac only: python setup-py2app.py py2app."""

from __future__ import annotations

from setuptools import setup

APP = ["../gui.py"]
OPTIONS = {
    "argv_emulation": False,
    "packages": ["utils"],
    "plist": {
        "CFBundleName": "Auto Organizer",
        "CFBundleIdentifier": "dev.goodfindfactory.autoorganizer",
        "CFBundleShortVersionString": "1.0.0",
    },
}

setup(
    app=APP,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
