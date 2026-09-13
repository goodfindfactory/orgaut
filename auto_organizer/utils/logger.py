"""Simple cross-platform logger. Rich/Colorama when present, else logging."""

from __future__ import annotations

import logging
import sys

_LOGGER_NAME = "auto_organizer"
_configured = False


def _try_colorama() -> None:
    try:
        from colorama import just_fix_windows_console

        just_fix_windows_console()
    except Exception:
        return


def get_logger() -> logging.Logger:
    """Return the shared Auto Organizer logger (idempotent)."""
    global _configured
    logger = logging.getLogger(_LOGGER_NAME)
    if _configured:
        return logger

    _try_colorama()
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(levelname)s  %(message)s"))
    logger.addHandler(handler)
    logger.propagate = False
    _configured = True
    return logger


def enable_debug() -> None:
    """Turn the shared logger up to DEBUG (``--debug`` / master-block)."""
    get_logger().setLevel(logging.DEBUG)


def info(message: str) -> None:
    get_logger().info(_color("INFO", message, "cyan"))


def warn(message: str) -> None:
    get_logger().warning(_color("WARN", message, "yellow"))


def error(message: str) -> None:
    get_logger().error(_color("ERROR", message, "red"))


def debug(message: str) -> None:
    get_logger().debug(message)


def log(message: str) -> None:
    """Master-block alias for :func:`info`."""
    info(message)


def _color(level: str, message: str, style: str) -> str:
    try:
        from rich.console import Console

        # Rich is used only to confirm it imports; keep log lines plain so
        # tests and pipes stay readable. Presence of the extra is enough.
        Console(file=sys.stdout, highlight=False)
        return message
    except Exception:
        return message
