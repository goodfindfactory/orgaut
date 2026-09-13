# autoorg

Backyard file sorter. Point it at a messy folder and it **moves** (does not copy)
loose files into buckets by extension:

`images/` `docs/` `code/` `archives/` `audio/` `video/` `other/`

No watcher. No cloud. No config file. One command, then you're done.

Built as a GoodFindFactory backyard cut — small, local, and boring on purpose.

## Install

Python 3.10+. From this repo:

```bash
pip install -e ".[dev]"
```

That puts the `autoorg` script on your PATH and pulls pytest for the tests.

## Use

```bash
# look first — nothing moves
autoorg ~/Downloads --dry-run

# sort the top of the folder (default: not recursive)
autoorg ~/Downloads

# walk subfolders too (skips the category buckets it already made)
autoorg ~/Downloads --recursive
```

Flags:

| Flag | What it does |
| --- | --- |
| `--dry-run` | Print the plan. Do not create dirs. Do not move files. |
| `--recursive` | Scan nested folders. Skip `images/docs/code/archives/audio/video/other`. |

Rules of the yard:

- **Files only.** Directories stay put.
- **Move, not copy.** The original path is gone after a real run.
- **Non-recursive by default.** Only the folder you named.
- **Collisions** get `_1`, `_2`, … on the stem (`photo.jpg` → `photo_1.jpg`).
- Unknown extensions and extensionless names land in `other/`.
- Category folders live at the path you passed, not next to every nested file.

## Categories

| Bucket | Extensions (not exhaustive — see `util.py`) |
| --- | --- |
| `images` | jpg, png, gif, webp, svg, heic, … |
| `docs` | pdf, docx, txt, md, csv, xlsx, … |
| `code` | py, js, ts, go, rs, json, html, … |
| `archives` | zip, tar, gz, 7z, rar, … |
| `audio` | mp3, wav, flac, aac, ogg, … |
| `video` | mp4, mkv, mov, webm, avi, … |
| `other` | everything else |

## Develop

```bash
pip install -e ".[dev]"
pytest -q
```

CI on `main` (push + PR) is the same two commands on Python 3.11.

## Live demo

**Vercel (GitHub-linked `orgaut`):** https://orgaut.vercel.app  
**Vercel (GitHub-linked `autorg-app`):** https://autorg-app.vercel.app

Type prompts (`dry-run`, `organize`, `undo`, `report`, `where does Vacation.JPG go?`) and watch the yard move. This is AutOrg, not SlanguageOS. Pushes to this repo deploy through the Vercel GitHub app.

GitHub Pages mirror: https://goodfindfactory.github.io/orgaut/

Download **AutoOrganizer-Mac.zip** from either page.

## MacBook zip

On the Mac, download **AutoOrganizer-Mac.zip** from the
[live demo](https://goodfindfactory.github.io/orgaut/),
[Releases](https://github.com/goodfindfactory/orgaut/releases),
or the **Mac zip archive** Actions artifact. Unzip, then double-click
**Install Auto Organizer.command**. That copies the tree to `~/orgaut`,
installs `aoctl`, and puts **AutoOrganizer.app** in `~/Applications`.

Rebuild the zip from this repo:

```bash
bash auto_organizer/mac/package-mac-zip.sh
# writes dist/AutoOrganizer-Mac.zip
```

Details: [`auto_organizer/mac/INSTALL-MAC.txt`](auto_organizer/mac/INSTALL-MAC.txt).

## Auto Organizer (CLI + GUI)

The full Auto Organizer app lives in [`auto_organizer/`](auto_organizer/README.md):

```bash
cd auto_organizer
pip install -r requirements.txt
python cli.py --path <target>
python cli.py --path <target> --dry-run
python cli.py --undo
python cli.py --report
python gui.py
```

## License

Proprietary — All Rights Reserved

ORGAUT is free to download but not open-source licensed.

