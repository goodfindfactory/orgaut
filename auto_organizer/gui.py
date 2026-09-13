"""Optional Tkinter GUI: pick a directory and run Auto Organizer."""

from __future__ import annotations

import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from main import organize
from utils.logger import error


def run_organizer(path: str, dry_run: bool, status: tk.StringVar) -> None:
    target = Path(path)
    if not target.exists() or not target.is_dir():
        messagebox.showerror("Auto Organizer", f"Not a directory:\n{path}")
        return
    try:
        batch = organize(target, dry_run=dry_run)
    except Exception as exc:  # GUI must not crash the desktop
        error(str(exc))
        messagebox.showerror("Auto Organizer", str(exc))
        return
    verb = "Would move" if dry_run else "Moved"
    status.set(f"{verb} {len(batch.records)} file(s). Report: {target / 'summary_report.txt'}")
    messagebox.showinfo("Auto Organizer", status.get())


def build_window() -> tk.Tk:
    root = tk.Tk()
    root.title("Auto Organizer")
    root.geometry("560x220")
    root.minsize(420, 200)

    path_var = tk.StringVar(value=str(Path.cwd()))
    dry_var = tk.BooleanVar(value=True)
    status = tk.StringVar(value="Pick a folder, then Run. Dry-run is on by default.")

    frame = ttk.Frame(root, padding=16)
    frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(frame, text="Target folder").pack(anchor=tk.W)
    row = ttk.Frame(frame)
    row.pack(fill=tk.X, pady=(4, 12))
    entry = ttk.Entry(row, textvariable=path_var)
    entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def browse() -> None:
        chosen = filedialog.askdirectory(initialdir=path_var.get() or str(Path.cwd()))
        if chosen:
            path_var.set(chosen)

    ttk.Button(row, text="Browse…", command=browse).pack(side=tk.LEFT, padx=(8, 0))
    ttk.Checkbutton(frame, text="Dry-run (no moves)", variable=dry_var).pack(anchor=tk.W)

    ttk.Button(
        frame,
        text="Run",
        command=lambda: run_organizer(path_var.get(), dry_var.get(), status),
    ).pack(anchor=tk.W, pady=(16, 8))
    ttk.Label(frame, textvariable=status, wraplength=520).pack(anchor=tk.W)
    return root


def main() -> int:
    try:
        window = build_window()
    except tk.TclError as exc:
        error(f"Tkinter GUI unavailable: {exc}")
        print("Tkinter GUI unavailable. Use: python cli.py --path <target>", file=sys.stderr)
        return 1
    window.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
