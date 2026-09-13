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

From this folder, or from the repo root (CI runs both suites).

## Full ops (local + GitHub + CI + release)

This tree already lives in **goodfindfactory/orgaut**. Do not `git init` here — the repo is live. Use these commands from `auto_organizer/`.

### Local setup

```bash
cd auto_organizer
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Local run (CLI)

```bash
python cli.py --path <TARGET_DIRECTORY>
python cli.py --undo
python cli.py --report
```

Preview first with `python cli.py --path <TARGET_DIRECTORY> --dry-run`.

### Local run (GUI)

```bash
python gui.py
```

### Local tests

```bash
pytest -q
```

### Git / GitHub (this repo)

Remote is already `https://github.com/goodfindfactory/orgaut.git`. Feature work goes on a branch and a PR into `main` — do not re-init or force-push `main`.

```bash
git remote -v
git pull origin main
```

### CI

Repo-root `.github/workflows/ci.yml` is **Auto Organizer CI**:

- push + PR to `main`
- Python 3.11
- `pip install -r requirements.txt`
- `pytest -q`
- `flake8 auto_organizer` (E9, F63, F7, F82)

### Optional: tag and release (after `main` is good)

```bash
git tag v1.0.0
git push origin v1.0.0
```

Then GitHub → Releases → Draft new release → attach zip/tar.gz.

### Optional: branch protection

GitHub → Settings → Branches → Protect `main` → require PRs + this CI check.

### Install on a MacBook

On the Mac (Terminal). This cloud agent cannot do it for you.

```bash
xcode-select --install
# optional: brew install python python-tk

git clone https://github.com/goodfindfactory/orgaut.git ~/orgaut
bash ~/orgaut/auto_organizer/mac/install-mac.sh
export PATH="$HOME/.local/bin:$PATH"
aoctl status
aoctl dry-run
```

Double-click **~/Applications/AutoOrganizer.app** (created by the installer). First run uses the Tk GUI.

Optional real `.app` via py2app (Mac only):

```bash
cd ~/orgaut/auto_organizer
source venv/bin/activate
pip install py2app
python mac/setup-py2app.py py2app
```

### iPhone control (simple SSH commands)

1. Mac → System Settings → General → Sharing → **Remote Login** on. Note the Mac’s LAN IP (`ipconfig getifaddr en0`).
2. Prefer an SSH key on the phone/Shortcuts over a password. Do not commit passwords.
3. iPhone → Shortcuts → **Run Script Over SSH**
   - Host: Mac IP
   - User: your Mac username
   - Script: one of:

```bash
$HOME/orgaut/auto_organizer/mac/aoctl status
$HOME/orgaut/auto_organizer/mac/aoctl test
$HOME/orgaut/auto_organizer/mac/aoctl dry-run
$HOME/orgaut/auto_organizer/mac/aoctl organize ~/Downloads
$HOME/orgaut/auto_organizer/mac/aoctl undo ~/Downloads
$HOME/orgaut/auto_organizer/mac/aoctl report ~/Downloads
```

Name shortcuts “AO dry-run”, “AO organize”, then add to the Home Screen or Siri. The Mac must be on, unlocked for GUI, and on the same Wi-Fi (or reachable via VPN).

`aoctl` never pushes `git` to `main` and never enables SSH itself.

### iPhone-triggered build (Mac as optional local server)

This cloud agent is not your MacBook. Remote Login and Shortcuts are set up
on the Mac and the phone. The repo already has a safer phone trigger that does
**not** need SSH or a password in Shortcuts.

**Preferred — GitHub Actions from the iPhone**

1. GitHub app → **goodfindfactory/orgaut** → Actions → **iPhone Auto Organizer Build**
2. Run workflow (branch `main` or this PR branch)
3. Or Siri / Shortcuts: open that Actions page, or call the GitHub API
   `workflow_dispatch` on `.github/workflows/iphone-build.yml`

That job installs deps, runs `pytest -q`, and self-checks the CLI/config.

**Optional — SSH from iPhone into a Mac**

On the Mac (you run these; they need admin):

```bash
sudo systemsetup -setremotelogin on
ipconfig getifaddr en0
```

Copy `auto_organizer/pipelines/auto_organizer_build.sh` to the Mac (or clone
this repo). Do **not** put the account password in the repo. In Shortcuts →
Run Script Over SSH:

```bash
export AUTOORG_BRANCH=main
bash /path/to/orgaut/auto_organizer/pipelines/auto_organizer_build.sh
```

The script pulls, makes a fresh venv, installs, and tests. It does **not**
`git add .` / push `main`, and it does **not** organize `Downloads` unless you
set `ORGANIZE_PATH` (add `ORGANIZE_APPLY=1` only when you really want moves).

A separate Mac login for SSH is optional and is a local admin task, not
something this repo can do from Linux CI. Do not store that password here.

### Optional: publish as a standalone `auto_organizer` repo

If you create an empty GitHub repo named `auto_organizer` (no README) and want this folder as the root:

```bash
# from a clean copy of this directory only
git init
git add .
git commit -m "Initial commit: Auto Organizer full build"
git remote add origin https://github.com/<YOUR_USERNAME>/auto_organizer.git
git branch -M main
git push -u origin main
```

Copy `.github/workflows/ci.yml` to that new repo root and change the flake8 path to `.` (there will be no nested `auto_organizer/` folder).

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
    mac/aoctl
    mac/install-mac.sh
    mac/AutoOrganizer.app
    README.md
    requirements.txt
    .gitignore
```
