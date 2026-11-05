"""The system's own Open dialog, so a person can point the Studio at a file anywhere on their computer (1.2.2).

A web page can't learn where a chosen file lives, so the Studio, which runs on the same computer, opens the dialog
itself: Finder's on the Mac (AppleScript), the Windows Open dialog (PowerShell), zenity on Linux. Returns the full
path, or None if the person cancels.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys

TIMEOUT = 900          # seconds the dialog may stay open


def choose_file(prompt: str, extension: str = "gguf") -> str | None:
    if sys.platform == "darwin":
        safe = prompt.replace('"', "'")
        r = subprocess.run(["osascript", "-e", "tell me to activate",
                            "-e", f'set f to choose file with prompt "{safe}" default location (path to downloads folder)',
                            "-e", "POSIX path of f"], capture_output=True, text=True, timeout=TIMEOUT)
        return r.stdout.strip() or None if r.returncode == 0 else None
    if sys.platform == "win32":
        ps = ("[Console]::OutputEncoding=[Text.Encoding]::UTF8;"
              "Add-Type -AssemblyName System.Windows.Forms;"
              "$d=New-Object System.Windows.Forms.OpenFileDialog;"
              f"$d.Title='{prompt.replace(chr(39), chr(39) * 2)}';"
              f"$d.Filter='Model file (*.{extension})|*.{extension}|All files (*.*)|*.*';"
              "$d.InitialDirectory=[Environment]::GetFolderPath('UserProfile')+'\\Downloads';"
              "$o=New-Object System.Windows.Forms.Form;$o.TopMost=$true;"
              "if($d.ShowDialog($o) -eq 'OK'){[Console]::Out.Write($d.FileName)}")
        r = subprocess.run(["powershell", "-NoProfile", "-STA", "-Command", ps], capture_output=True, text=True,
                           encoding="utf-8", timeout=TIMEOUT, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        return r.stdout.strip() or None
    if shutil.which("zenity"):
        r = subprocess.run(["zenity", "--file-selection", f"--title={prompt}", f"--file-filter=*.{extension}",
                            f"--filename={os.path.expanduser('~/Downloads')}/"], capture_output=True, text=True,
                           timeout=TIMEOUT)
        return r.stdout.strip() or None if r.returncode == 0 else None
    raise RuntimeError("No file dialog on this system: type the model file's full path instead.")
