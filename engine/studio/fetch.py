"""Gemma and its engine, downloaded by the Studio itself, in the background.

Why (Tim, 13 Oct, on Jon's PC): the installer's built-in downloader stalled on the 6.1 GB model, Windows gave up
("Error reading data: (12002) The operation timed out") and "Try again" could only start the file from zero. Here
every file is fetched with HTTP Range requests into "<name>.part", so a dropped connection, a closed Studio or a
restarted PC carries on from the last byte saved. Each file is checked against its SHA-256 before it is used; the
engine zip is unpacked beside the models. Nothing here runs unless the user (or the installer, through
llm/wanted.json) asked for a model.
"""
from __future__ import annotations

import hashlib
import http.client
import json
import os
import shutil
import platform
import sys
import tarfile
import threading
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

from . import store

# Official sources, sizes and SHA-256 (the same files and checks as the 1.0.1 installer; Hugging Face API and the
# llama.cpp release page, 13 Oct 2026). Tests replace ITEMS with a local server.
# The engine is per system: Windows (Vulkan, any GPU) and Mac (Apple Silicon, Metal), the same llama.cpp release.
ENGINES: dict[str, dict] = {
    "win32": {"label": "AI engine (llama.cpp)", "name": "llama-win.zip", "dir": "", "unzip": True, "size": 91287837,
              "url": "https://github.com/ggml-org/llama.cpp/releases/download/b11577/llama-b11577-bin-win-vulkan-x64.zip",
              "sha256": "1d9a92d7bd92d41ace1ac21fb3ac2241a8175b932b9229b0d54e8bf625df8a81", "done_when": "llama-server.exe"},
    # Mac (18 Oct 2026): a .tar.gz with one top folder, symlinked libraries and executable files; unpacked without
    # the top folder, so llama-server sits where the Windows one does.
    "darwin": {"label": "AI engine (llama.cpp)", "name": "llama-mac.tar.gz", "dir": "", "unzip": True, "size": 12112274,
               "url": "https://github.com/ggml-org/llama.cpp/releases/download/b11577/llama-b11577-bin-macos-arm64.tar.gz",
               "sha256": "fa6526afe087293ac83709fe6529fa087e7070f606e30dd452173c16ccebed8c", "done_when": "llama-server",
               "strip": "llama-b11577/"},
    # Intel Macs (5 Nov 2026: Jon's 2019 MacBook Pro): the same release's macOS x64 build, checked when downloaded here
    "darwin-x86_64": {"label": "AI engine (llama.cpp)", "name": "llama-mac.tar.gz", "dir": "", "unzip": True, "size": 11608121,
               "url": "https://github.com/ggml-org/llama.cpp/releases/download/b11577/llama-b11577-bin-macos-x64.tar.gz",
               "sha256": "a623d9b4a3bf6c4d1c3447b6d7d52b43976ab4b624426158d9ee4ec0a13370ea", "done_when": "llama-server",
               "strip": "llama-b11577/"},
}
ITEMS: dict[str, dict] = {
    "engine": ENGINES[("darwin-x86_64" if platform.machine() == "x86_64" else "darwin") if sys.platform == "darwin" else "win32"],
    "12b": {"label": "Gemma 4 12B", "name": "gemma-4-12b-it-qat-q4_0.gguf", "dir": "models", "size": 6975879296,
            "url": "https://huggingface.co/google/gemma-4-12B-it-qat-q4_0-gguf/resolve/main/gemma-4-12b-it-qat-q4_0.gguf",
            "sha256": "93567e57a8fe10b23569b9d9ec38cd005deedf71e29477c421a4b83f418a538b"},
    "12b-vision": {"label": "Gemma 4 12B vision add-on", "name": "mmproj-gemma-4-12b-it-qat-q4_0.gguf", "dir": "models", "size": 175115616,
                   "url": "https://huggingface.co/google/gemma-4-12B-it-qat-q4_0-gguf/resolve/main/mmproj-gemma-4-12b-it-qat-q4_0.gguf",
                   "sha256": "cb018338a7538a9814d994bfe54644c71eb7ed54e31eae2f721e45fd3c260da7"},
    "e4b": {"label": "Gemma 4 E4B", "name": "gemma-4-E4B_q4_0-it.gguf", "dir": "models", "size": 5154941280,
            "url": "https://huggingface.co/google/gemma-4-E4B-it-qat-q4_0-gguf/resolve/main/gemma-4-E4B_q4_0-it.gguf",
            "sha256": "676c35070db6dbe52f93e9c864ee0fba4eddea94b9c875d9cb10daff453fbaee"},
    "e4b-vision": {"label": "Gemma 4 E4B vision add-on", "name": "gemma-4-E4B-it-mmproj.gguf", "dir": "models", "size": 991552256,
                   "url": "https://huggingface.co/google/gemma-4-E4B-it-qat-q4_0-gguf/resolve/main/gemma-4-E4B-it-mmproj.gguf",
                   "sha256": "7498a37cb619e55f2fcf87eb931f56e99389ed6d432e4c5c66110694c0d65578"},
}
PLANS = {"12b": ("engine", "12b", "12b-vision"), "e4b": ("engine", "e4b", "e4b-vision")}
if os.environ.get("STUDIO_FETCH_ITEMS"):        # test builds only: the same items served from a local test server
    ITEMS = {**ITEMS, **json.loads(Path(os.environ["STUDIO_FETCH_ITEMS"]).read_text(encoding="utf-8"))}
NAMES = {"12b": "Gemma 4 12B", "e4b": "Gemma 4 E4B"}

CHUNK = 1 << 20
READ_TIMEOUT = 60            # seconds without a byte before a connection counts as stalled
GIVE_UP_AFTER = 40           # failed attempts in a row with no progress before the download stops and asks
SERVER_EXE = "llama-server.exe" if sys.platform == "win32" else "llama-server"

_LOCK = threading.Lock()
_STOP = threading.Event()
_THREAD: threading.Thread | None = None
_STATE: dict = {"state": "idle"}


# ---------------------------------------------------------------- where things go
def _writable(d: Path) -> bool:
    try:
        d.mkdir(parents=True, exist_ok=True)
        probe = d / ".write-test"
        probe.write_bytes(b"")
        probe.unlink()
        return True
    except OSError:
        return False


def candidate_dirs() -> list[Path]:
    """STUDIO_LLM_DIR (tests, support) · <install folder>/llm (beside the program, per-user install) ·
    <Studio data>/llm (when the install folder is read-only, e.g. Program Files; always on the Mac, where writing
    into the app would break its signature)."""
    dirs = [Path(os.environ["STUDIO_LLM_DIR"])] if os.environ.get("STUDIO_LLM_DIR") else []
    if getattr(sys, "frozen", False) and sys.platform != "darwin":   # never write inside a signed Mac app
        dirs.append(Path(sys.executable).resolve().parent / "llm")
    dirs.append(store.home() / "llm")
    return dirs


_TARGET: dict[tuple, Path] = {}


def target_dir() -> Path:
    key = tuple(candidate_dirs())
    if key in _TARGET:
        return _TARGET[key]
    _TARGET[key] = _pick_target()
    return _TARGET[key]


def _pick_target() -> Path:
    for d in candidate_dirs():
        if (d / SERVER_EXE).exists() or (d / "models").exists() or (d / "wanted.json").exists():
            if _writable(d):
                return d
    return next((d for d in candidate_dirs() if _writable(d)), candidate_dirs()[-1])


def wanted() -> str:
    """The model the installer (or Settings) asked for, if any."""
    for d in candidate_dirs():
        try:
            m = json.loads((d / "wanted.json").read_text(encoding="utf-8")).get("model", "")
            if m in PLANS:
                return m
        except (OSError, ValueError, AttributeError):
            continue
    return ""


def _set_wanted(model: str) -> None:
    d = target_dir()
    d.mkdir(parents=True, exist_ok=True)
    (d / "wanted.json").write_text(json.dumps({"model": model, "asked": time.strftime("%Y-%m-%d %H:%M:%S")}), encoding="utf-8")


def _installed(key: str) -> bool:
    it = ITEMS[key]
    for d in candidate_dirs():
        if it.get("done_when"):
            if (d / it["done_when"]).exists():
                return True
        else:
            f = d / it["dir"] / it["name"]
            if f.exists() and f.stat().st_size == it["size"]:
                return True
    return False


def missing(model: str) -> list[str]:
    return [k for k in PLANS.get(model, ()) if not _installed(k)]


def _part(key: str) -> Path:
    it = ITEMS[key]
    return target_dir() / it["dir"] / (it["name"] + ".part")


def memory_gb() -> int:
    try:
        if sys.platform == "win32":
            import ctypes

            class MS(ctypes.Structure):
                _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong), ("ullTotalPhys", ctypes.c_ulonglong),
                            ("ullAvailPhys", ctypes.c_ulonglong), ("ullTotalPageFile", ctypes.c_ulonglong),
                            ("ullAvailPageFile", ctypes.c_ulonglong), ("ullTotalVirtual", ctypes.c_ulonglong),
                            ("ullAvailVirtual", ctypes.c_ulonglong), ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
            m = MS(); m.dwLength = ctypes.sizeof(MS)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
            return int(m.ullTotalPhys // 1073741824)
        return int(os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") // 1073741824)
    except Exception:  # noqa: BLE001 - only a recommendation
        return 0


# ---------------------------------------------------------------- status
def _update(**kw) -> None:
    with _LOCK:
        _STATE.update(kw)


def status() -> dict:
    with _LOCK:
        s = dict(_STATE)
    model = s.get("model") or wanted()
    s["wanted"] = wanted()
    s["model"] = model
    s["model_name"] = NAMES.get(model, "")
    s["active"] = s.get("state") in ("downloading", "retrying", "checking", "unpacking", "starting")
    s["memory_gb"] = memory_gb()
    s["options"] = {m: {"name": NAMES[m], "bytes": sum(ITEMS[k]["size"] for k in PLANS[m]),
                        "to_download": sum(ITEMS[k]["size"] for k in missing(m)), "installed": not missing(m)} for m in PLANS}
    if not s["active"] and model and s.get("state") not in ("error", "paused"):
        rest = missing(model)
        s["state"] = "done" if not rest else ("waiting" if s.get("state") == "idle" else s.get("state"))
        if rest:
            done = sum(_part(k).stat().st_size for k in rest if _part(k).exists())
            s["done_bytes"], s["total_bytes"] = done, sum(ITEMS[k]["size"] for k in rest)
    return s


# ---------------------------------------------------------------- the work
class _Stopped(Exception):
    pass


def _fetch(key: str, progress) -> None:
    it = ITEMS[key]
    part = _part(key)
    part.parent.mkdir(parents=True, exist_ok=True)
    fails, retried_bad = 0, False
    while True:
        have = part.stat().st_size if part.exists() else 0
        if have > it["size"]:
            part.unlink(); have = 0
        if have < it["size"]:
            req = urllib.request.Request(it["url"], headers={"User-Agent": "SaracenBridgeStudio", "Range": f"bytes={have}-"})
            try:
                with urllib.request.urlopen(req, timeout=READ_TIMEOUT) as r:
                    if have and r.status != 206:       # the server sent the whole file: start again
                        have = 0
                    with open(part, "ab" if have else "wb") as f:
                        while True:
                            if _STOP.is_set():
                                raise _Stopped
                            chunk = r.read(CHUNK)
                            if not chunk:
                                break
                            f.write(chunk)
                            fails = 0
                            progress(len(chunk))
                            _update(state="downloading", message="")
            except _Stopped:
                raise
            except urllib.error.HTTPError as e:
                if e.code == 416 and part.exists() and part.stat().st_size == it["size"]:
                    pass
                elif e.code in (401, 403, 404, 410):
                    raise RuntimeError(f"The download source refused {it['label']} (HTTP {e.code}).") from e
                else:
                    fails = _wait(fails, f"The server answered {e.code}")
                continue
            except (urllib.error.URLError, http.client.HTTPException, TimeoutError, ConnectionError, OSError) as e:
                fails = _wait(fails, _why(e))
                continue
            if (part.stat().st_size if part.exists() else 0) < it["size"]:
                fails = _wait(fails, "The connection closed early")
                continue
        _update(state="checking", message=f"Checking {it['label']}")
        if _sha256(part) == it["sha256"]:
            break
        part.unlink()
        if retried_bad:
            raise RuntimeError(f"{it['label']} arrived damaged twice. Check the internet connection and try again.")
        retried_bad = True
        progress(-it["size"])
    final = part.with_name(it["name"])
    if it.get("unzip"):
        _update(state="unpacking", message=f"Unpacking {it['label']}")
        unpack(part, part.parent, it.get("strip", ""))
        part.unlink()
    else:
        os.replace(part, final)


def unpack(archive: Path, dest: Path, strip: str = "") -> None:
    """A .zip (Windows engine) or .tar.gz (Mac engine, which keeps its symlinks and executable bits). `strip` drops
    a leading folder, so the engine always lands directly in `dest`."""
    if zipfile.is_zipfile(archive):
        with zipfile.ZipFile(archive) as z:
            z.extractall(dest)
        return
    with tarfile.open(archive) as t:
        members = []
        for m in t.getmembers():
            if strip:
                if not m.name.startswith(strip):
                    continue
                m.name = m.name[len(strip):]
                if not m.name:
                    continue
            members.append(m)
        t.extractall(dest, members=members, filter="data")    # refuses paths or links that leave dest


def _why(e: Exception) -> str:
    r = getattr(e, "reason", None) or e
    text = str(r)
    if "timed out" in text.lower():
        return "The connection stalled"
    return "The connection dropped"


def _wait(fails: int, why: str) -> int:
    fails += 1
    if fails > GIVE_UP_AFTER:
        raise RuntimeError(f"{why} too many times in a row. Check the internet connection, then press Resume: it carries on "
                           "from where it stopped.")
    pause = min(60, 2 ** min(fails, 6))
    for left in range(pause, 0, -1):
        _update(state="retrying", message=f"{why}. Trying again in {left} s; nothing downloaded so far is lost.")
        if _STOP.wait(1):
            raise _Stopped
    return fails


def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while True:
            if _STOP.is_set():
                raise _Stopped
            b = f.read(8 << 20)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def _run(model: str) -> None:
    keys = missing(model)
    total = sum(ITEMS[k]["size"] for k in keys)
    done = sum(_part(k).stat().st_size for k in keys if _part(k).exists())
    speed = 0.0
    last = [time.monotonic(), done]

    def progress(n: int) -> None:
        nonlocal done, speed
        done = max(0, done + n)
        now = time.monotonic()
        if now - last[0] >= 1:
            inst = (done - last[1]) / (now - last[0])
            speed = inst if not speed else .7 * speed + .3 * inst
            last[0], last[1] = now, done
            _update(done_bytes=done, speed=int(max(speed, 0)), eta_s=int((total - done) / speed) if speed > 0 else None)

    try:
        free = shutil.disk_usage(target_dir()).free
        need = total - done + (ITEMS["engine"]["size"] * 2 if "engine" in keys else 0)
        if free < need + (512 << 20):
            raise RuntimeError(f"Not enough free space: {NAMES[model]} needs about {need / 1e9:.1f} GB more on this drive "
                               f"({free / 1e9:.1f} GB free).")
        _update(state="downloading", model=model, total_bytes=total, done_bytes=done, speed=0, eta_s=None, error="", message="",
                started=time.strftime("%Y-%m-%d %H:%M:%S"))
        for k in keys:
            _update(item=ITEMS[k]["label"])
            _fetch(k, progress)
        _update(state="done", item="", message=f"{NAMES[model]} is ready", done_bytes=total, speed=0, eta_s=0,
                finished=time.strftime("%Y-%m-%d %H:%M:%S"))
    except _Stopped:
        _update(state="paused", message="Paused. Resume carries on from where it stopped.", speed=0, eta_s=None)
    except Exception as e:  # noqa: BLE001 - shown to the user with a Try again
        _update(state="error", error=str(e), message="", speed=0, eta_s=None)


def start(model: str) -> dict:
    """Start (or resume) downloading a model and whatever it still needs. Safe to call repeatedly."""
    global _THREAD
    if model not in PLANS:
        raise ValueError("Unknown model")
    with _LOCK:
        running = _THREAD is not None and _THREAD.is_alive()
    if running:
        return status()
    _set_wanted(model)
    if not missing(model):
        _update(state="done", model=model, message=f"{NAMES[model]} is ready")
        return status()
    _STOP.clear()
    _update(state="starting", model=model, error="", message="Starting")
    _THREAD = threading.Thread(target=_run, args=(model,), name="gemma-download", daemon=True)
    _THREAD.start()
    return status()


def pause() -> dict:
    _STOP.set()
    t = _THREAD
    if t is not None:
        t.join(timeout=5)
    return status()


def resume_if_wanted() -> None:
    """At start-up: carry on with a download the installer or the user asked for and that isn't finished."""
    m = wanted()
    if m and missing(m):
        start(m)
