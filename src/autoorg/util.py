"""Extension maps, category lookup, and collision-safe destinations."""

from __future__ import annotations

from pathlib import Path

# Destination folder names. Recursive scans skip these so already-sorted
# files are not picked up again.
CATEGORIES: tuple[str, ...] = (
    "images",
    "docs",
    "code",
    "archives",
    "audio",
    "video",
    "other",
)

CATEGORY_DIRS: frozenset[str] = frozenset(CATEGORIES)

# Lowercase extensions without the leading dot.
_IMAGES = frozenset(
    {
        "jpg",
        "jpeg",
        "jpe",
        "jfif",
        "png",
        "gif",
        "webp",
        "bmp",
        "tif",
        "tiff",
        "svg",
        "svgz",
        "ico",
        "icns",
        "heic",
        "heif",
        "avif",
        "raw",
        "cr2",
        "cr3",
        "nef",
        "arw",
        "dng",
        "orf",
        "rw2",
        "psd",
        "xcf",
        "ai",
        "eps",
    }
)

_DOCS = frozenset(
    {
        "pdf",
        "doc",
        "docx",
        "docm",
        "dot",
        "dotx",
        "xls",
        "xlsx",
        "xlsm",
        "xlsb",
        "ppt",
        "pptx",
        "pptm",
        "odt",
        "ods",
        "odp",
        "odg",
        "rtf",
        "txt",
        "text",
        "md",
        "markdown",
        "rst",
        "csv",
        "tsv",
        "tex",
        "ltx",
        "epub",
        "mobi",
        "azw",
        "azw3",
        "pages",
        "numbers",
        "key",
        "log",
        "org",
        "adoc",
        "asciidoc",
    }
)

_CODE = frozenset(
    {
        "py",
        "pyi",
        "pyw",
        "ipynb",
        "js",
        "mjs",
        "cjs",
        "jsx",
        "ts",
        "tsx",
        "java",
        "kt",
        "kts",
        "scala",
        "groovy",
        "c",
        "h",
        "cc",
        "cpp",
        "cxx",
        "hpp",
        "hh",
        "cs",
        "go",
        "rs",
        "rb",
        "php",
        "swift",
        "m",
        "mm",
        "r",
        "jl",
        "lua",
        "pl",
        "pm",
        "t",
        "sh",
        "bash",
        "zsh",
        "fish",
        "ps1",
        "psm1",
        "bat",
        "cmd",
        "sql",
        "json",
        "jsonc",
        "json5",
        "yaml",
        "yml",
        "toml",
        "xml",
        "html",
        "htm",
        "xhtml",
        "css",
        "scss",
        "sass",
        "less",
        "vue",
        "svelte",
        "astro",
        "dart",
        "ex",
        "exs",
        "erl",
        "hrl",
        "hs",
        "lhs",
        "clj",
        "cljs",
        "edn",
        "lisp",
        "el",
        "vim",
        "cmake",
        "make",
        "mk",
        "gradle",
        "nim",
        "zig",
        "v",
        "ml",
        "mli",
        "fs",
        "fsx",
        "f90",
        "for",
        "asm",
        "s",
        "wat",
        "wasm",
        "proto",
        "graphql",
        "gql",
        "tf",
        "hcl",
        "nix",
        "lock",
        "ini",
        "cfg",
        "conf",
        "env",
        "dockerfile",
    }
)

_ARCHIVES = frozenset(
    {
        "zip",
        "zipx",
        "tar",
        "gz",
        "tgz",
        "bz2",
        "tbz",
        "tbz2",
        "xz",
        "txz",
        "7z",
        "rar",
        "lz",
        "lzma",
        "zst",
        "zstd",
        "cab",
        "iso",
        "img",
        "dmg",
        "apk",
        "jar",
        "war",
        "ear",
        "whl",
        "egg",
        "deb",
        "rpm",
        "sit",
        "sitx",
    }
)

_AUDIO = frozenset(
    {
        "mp3",
        "wav",
        "wave",
        "flac",
        "aac",
        "m4a",
        "ogg",
        "oga",
        "opus",
        "wma",
        "aiff",
        "aif",
        "aifc",
        "alac",
        "ape",
        "mid",
        "midi",
        "amr",
        "3ga",
        "caf",
        "au",
        "ra",
        "ac3",
    }
)

_VIDEO = frozenset(
    {
        "mp4",
        "m4v",
        "mkv",
        "avi",
        "mov",
        "qt",
        "wmv",
        "flv",
        "webm",
        "mpg",
        "mpeg",
        "m2v",
        "m2ts",
        "mts",
        "ts",
        "3gp",
        "3g2",
        "ogv",
        "vob",
        "asf",
        "f4v",
        "rm",
        "rmvb",
        "divx",
    }
)

_EXT_TO_CATEGORY: dict[str, str] = {}
for _ext in _IMAGES:
    _EXT_TO_CATEGORY[_ext] = "images"
for _ext in _DOCS:
    _EXT_TO_CATEGORY[_ext] = "docs"
for _ext in _CODE:
    _EXT_TO_CATEGORY[_ext] = "code"
for _ext in _ARCHIVES:
    _EXT_TO_CATEGORY[_ext] = "archives"
for _ext in _AUDIO:
    _EXT_TO_CATEGORY[_ext] = "audio"
for _ext in _VIDEO:
    _EXT_TO_CATEGORY[_ext] = "video"


def extension_of(path: Path | str) -> str:
    """Return the lowercase extension without a leading dot.

    ``archive.tar.gz`` is treated as ``gz``. A name with no suffix (including
    lone dotfiles like ``.gitignore``) returns an empty string.
    """
    suffix = Path(path).suffix
    if not suffix or suffix == ".":
        return ""
    return suffix[1:].lower()


def category_for(path: Path | str) -> str:
    """Map a file path to one of the seven category folder names."""
    ext = extension_of(path)
    if not ext:
        return "other"
    return _EXT_TO_CATEGORY.get(ext, "other")


def is_category_dir(name: str) -> bool:
    """True when *name* is one of the destination bucket folder names."""
    return name.lower() in CATEGORY_DIRS


def unique_destination(
    dest_dir: Path,
    filename: str,
    reserved: set[Path] | None = None,
) -> Path:
    """Pick a collision-safe path under *dest_dir*.

    First try ``filename``. If that path already exists on disk or is in
    *reserved*, try ``stem_1`` + suffix, then ``stem_2``, and so on.
    """
    reserved = reserved if reserved is not None else set()
    dest_dir = Path(dest_dir)
    first = dest_dir / filename
    if not _taken(first, reserved):
        return first

    stem = Path(filename).stem
    suffix = Path(filename).suffix
    n = 1
    while True:
        candidate = dest_dir / f"{stem}_{n}{suffix}"
        if not _taken(candidate, reserved):
            return candidate
        n += 1


def _taken(path: Path, reserved: set[Path]) -> bool:
    if path in reserved:
        return True
    try:
        return path.exists()
    except OSError:
        return False
