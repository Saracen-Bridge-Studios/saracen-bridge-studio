"""Scanned scripts (1.0.6): Tesseract OCR, bundled with the Studio.

A PDF made by scanning paper has no text layer, so the reader found no scenes (register S-12). Pages are rendered with
PDFium (already bundled for look books) at 200 dpi and read by Tesseract 5.3 (Apache-2.0; the signed Windows build from
Universität Mannheim, English model). Tesseract's word boxes are put back into screenplay lines: indentation from each
line's left edge (12-point Courier is 10 characters an inch, 20 pixels at 200 dpi) and a blank line wherever the gap to
the next line is wider than single spacing, so the same reader that handles typed PDFs finds the headings and cues.
Results are cached by the file's SHA-256, so a script is read once.

Speed (measured here, 15 Oct, on an 18-page noisy scan, 2-core Linux container, Tesseract 5.3): 300 dpi with Tesseract's
default threading took 10.8 s a page; one thread per Tesseract 4.0 s; one thread at 200 dpi 2.8 s, and 200 dpi read all
60 scene headings and 6 speaking roles exactly where 300 dpi misread one heading. So pages are read at 200 dpi, one
thread per Tesseract, several pages at a time (one fewer than the processor count, up to 4).
"""
from __future__ import annotations

import hashlib
import os
import threading
import shutil
import re
import statistics
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from . import refdata

DPI = 200
CHAR_PX = DPI / 10                  # Courier 12 pt: 10 characters per inch
WORKERS = min(4, max(1, (os.cpu_count() or 2) - 1))
_lock = threading.Lock()
_active: dict[str, dict] = {}       # scripts being read now, for the progress line on screen
MIN_TEXT_PER_PAGE = 40              # fewer characters per page than this in the text layer: treat the PDF as scanned


def tesseract() -> Path | None:
    """The bundled OCR (installed app), or one given by STUDIO_TESSERACT, or Tesseract on PATH (development).
    Windows bundles tesseract.exe; the Mac bundles studio-ocr, Apple's Vision text recognition answering in
    Tesseract's TSV (packaging/macos/studio-ocr.swift)."""
    env = os.environ.get("STUDIO_TESSERACT")
    root = refdata.app_root()
    bundled = ([root / "ocr" / "tesseract.exe", root / "packaging" / "ocr" / "tesseract.exe"] if sys.platform == "win32"
               else [root / "ocr" / "studio-ocr"] if sys.platform == "darwin" else [])
    for cand in ([Path(env)] if env else []) + bundled:
        if cand.is_file():
            return cand
    found = shutil.which("tesseract")
    return Path(found) if found else None


def available() -> bool:
    return tesseract() is not None


def _tessdata(exe: Path) -> Path | None:
    d = exe.parent / "tessdata"
    return d if (d / "eng.traineddata").is_file() else None


def is_scanned(pages_text: list[str]) -> bool:
    text = sum(len((t or "").strip()) for t in pages_text)
    return bool(pages_text) and text < MIN_TEXT_PER_PAGE * len(pages_text)


def _cache_dir() -> Path:
    from . import store
    d = store.home() / "ocr"
    d.mkdir(parents=True, exist_ok=True)
    return d


def progress() -> list[dict]:
    """Scanned scripts being read now: pages done of pages."""
    with _lock:
        return [dict(v) for v in _active.values()]


def pdf_pages(data: bytes, name: str = "") -> list[str]:
    """The scanned PDF read page by page: each page as screenplay-shaped text."""
    key = hashlib.sha256(data).hexdigest()
    cached = _cache_dir() / f"{key}.pages.txt"                   # pages separated by form feeds
    if cached.is_file():
        return cached.read_text(encoding="utf-8").split("\f")
    exe = tesseract()
    if exe is None:
        raise RuntimeError("OCR isn't installed with this copy of the Studio.")
    import pypdfium2 as pdfium
    pdf = pdfium.PdfDocument(data)
    n = len(pdf)
    state = {"file": name, "done": 0, "pages": n}
    with _lock:
        _active[key] = state

    def read(path: Path) -> list[str]:
        out = _page_lines(exe, path)
        with _lock:
            state["done"] += 1
        path.unlink(missing_ok=True)
        return out

    try:
        with tempfile.TemporaryDirectory(prefix="sb-ocr-") as tmp, ThreadPoolExecutor(WORKERS) as pool:
            futures = []
            for i in range(n):                                   # PDFium renders one page at a time (not thread-safe)
                page = pdf[i]
                img = page.render(scale=DPI / 72, grayscale=True).to_pil()
                page.close()
                path = Path(tmp) / f"p{i + 1:04d}.png"
                img.save(path)
                futures.append(pool.submit(read, path))
                if len(futures) > 2 * WORKERS:                   # stay a few pages ahead, not the whole script on disk
                    futures[-2 * WORKERS - 1].result()
            pages = ["\n".join(f.result()) for f in futures]
    finally:
        pdf.close()
        with _lock:
            _active.pop(key, None)
    cached.write_text("\f".join(pages), encoding="utf-8")
    return pages


def pdf_lines(data: bytes, name: str = "") -> list[str]:
    """The scanned PDF as screenplay-shaped text lines (pages separated by a blank line)."""
    return [ln for page in pdf_pages(data, name) for ln in page.split("\n") + [""]]


def _page_lines(exe: Path, image: Path) -> list[str]:
    env = dict(os.environ)
    td = _tessdata(exe)
    if td:
        env["TESSDATA_PREFIX"] = str(td)
    env["OMP_THREAD_LIMIT"] = "1"                                    # pages run side by side instead
    flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if sys.platform == "win32" else 0
    out = subprocess.run([str(exe), str(image), "stdout", "-l", "eng", "--psm", "4", "--dpi", str(DPI), "tsv"],
                         capture_output=True, env=env, timeout=180, creationflags=flags)
    if out.returncode != 0:
        raise RuntimeError("OCR failed on a page: " + out.stderr.decode("utf-8", "replace").strip()[:200])
    return tsv_to_lines(out.stdout.decode("utf-8", "replace"))


def tsv_to_lines(tsv: str) -> list[str]:
    """Tesseract TSV (word boxes) -> lines with screenplay indentation and blank lines between elements."""
    words: dict = {}
    for row in tsv.splitlines()[1:]:
        f = row.split("\t")
        if len(f) < 12 or f[0] != "5" or not f[11].strip():
            continue
        key = (int(f[2]), int(f[3]), int(f[4]))                     # block, paragraph, line
        left, top, w, h = (int(x) for x in f[6:10])
        words.setdefault(key, []).append((left, top, w, h, f[11]))
    rows = []
    for ws in words.values():
        ws.sort()
        left, top = ws[0][0], min(w[1] for w in ws)
        height = max(w[3] for w in ws)
        text, prev_end = "", None
        for lx, _, w, _, t in ws:                                    # keep wide gaps inside a line (scene numbers)
            if prev_end is not None:
                gap = max(1, round((lx - prev_end) / CHAR_PX))
                text += " " * min(gap, 40)
            text += t
            prev_end = lx + w
        rows.append((top, left, height, text))
    if not rows:
        return []
    rows.sort()
    pitch = statistics.median([b[0] - a[0] for a, b in zip(rows, rows[1:]) if b[0] - a[0] > 0] or [DPI / 6])
    margin = min(r[1] for r in rows)
    out, prev_top = [], None
    for top, left, _, text in rows:
        if prev_top is not None and top - prev_top > 1.5 * min(pitch, DPI / 6 * 1.2):
            out.append("")
        out.append(" " * max(0, round((left - margin) / CHAR_PX)) + _fix_extension(text))
        prev_top = top
    return out


def _fix_extension(text: str) -> str:
    """A cue's extension as printed: OCR can read the O of (O.S.), (V.O.) or (O.C.) as a zero (Mac Vision, 5 Nov:
    "TOM (0.S.)"), and a cue with a zero isn't seen as a cue."""
    return re.sub(r"\((0|O)\.? ?(S|C)\.?\)|\(V\.? ?(0|O)\.?\)",
                  lambda m: "(V.O.)" if m.group(0).upper().startswith("(V") else f"(O.{m.group(2)}.)", text)
