# Auto Organizer

Cross-platform file organizer for Mac, Windows, and Linux. It scans a directory,
maps extensions from `config.json`, creates category folders, and **moves** files
into them. Undo and a text report are built in. Optional Tkinter GUI.

Safe by default: dry-run plans without touching disk, unknown types stay put,
moves are logged for undo, and nothing asks for admin privileges.

## Install

Python 3.10+. From this folder:

```bash
pip install -r requirements.txt
```

`rich` and `colorama` colorize the CLI. `pytest` runs the tests. Tkinter ships
with most Python installs and is only needed for the GUI.

## Run

```bash
python cli.py --path <target>
python cli.py --path <target> --dry-run
python cli.py --undo
python cli.py --report
python gui.py
```

`--path` defaults to the current directory. `--undo` and `--report` also honor
`--path` when you pass it.

### CLI usage

| Command | What it does |
| --- | --- |
| `python cli.py --path ~/Downloads --dry-run` | Print the plan. Create nothing. Move nothing. |
| `python cli.py --path ~/Downloads` | Create category folders and move matching files. |
| `python cli.py --path ~/Downloads --undo` | Put those files back using `_undo/manifest.json`. |
| `python cli.py --path ~/Downloads --report` | Print `summary_report.txt`. |

Only files sitting directly in `--path` are scanned (not nested folders).
Category folders and `_undo` are skipped so a second run does not reshuffle.

### GUI usage

```bash
python gui.py
```

Pick a folder with Browse…, leave **Dry-run** checked for a preview, then Run.
Uncheck dry-run when you want a real organize. The GUI will not start if
Tkinter is missing; use the CLI instead.

## Config rules

`config.json` is the only settings file:

```json
{
  "categories": {
    "documents": ["pdf", "docx", "txt", "md"],
    "images": ["jpg", "jpeg", "png", "gif", "bmp"],
    "videos": ["mp4", "mov", "avi"],
    "audio": ["mp3", "wav", "flac"],
    "archives": ["zip", "rar", "7z"],
    "code": ["py", "js", "ts", "html", "css"],
    "executables": ["exe", "dmg", "app"]
  },
  "undo_folder": "_undo",
  "report_file": "summary_report.txt"
}
```

- Extensions are matched case-insensitively, without the dot.
- Unknown extensions are left in place (no silent “misc” dump).
- Name collisions become `file_1.ext`, `file_2.ext`, …
- Edit categories in `config.json`. Do not point `--path` at a system folder.

## Safety notes

- **Moves, never deletes.** There is no wipe, shred, or empty-trash path.
- **Dry-run first** on any folder you care about.
- **Undo** reads `_undo/manifest.json` and moves files back. If you deleted a
  destination by hand, that entry is skipped.
- If a move fails mid-run, the current batch is rolled back.
- Paths cannot escape the target root (`..` and absolute joins are rejected).
- No admin / elevated privileges are required or requested.
- Do not run this on `/`, `C:\`, or a project that contains `.git` you still
  need — it only sorts the top of `--path`, but you still own the folder.

## Tests

```bash
pytest -q
```

From the repo root, CI also runs the package tests plus these.

## Layout

```
auto_organizer/
    main.py
    cli.py
    gui.py
    file_types.py
    folder_manager.py
    mover.py
    undo.py
    report.py
    config.json
    utils/logger.py
    utils/paths.py
    tests/
    README.md
    requirements.txt
    .gitignore
```
