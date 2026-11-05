"""AI engine: one client for every local model server the Studio can use.

The model reads and drafts. It never produces a figure the engine relies on.

Which engine runs (settings["ai_engine"]["provider"]):
  auto     (fresh install) 1. Ollama on this computer with a Gemma model installed
                           2. the Gemma model bundled with the installer (llama.cpp server, started on first use)
                           3. none: calculation tools only
  ollama   an Ollama server at `url` (default http://127.0.0.1:11434)
  openai   any OpenAI-compatible server at `url` (llama.cpp, LM Studio, vLLM; later Ada)
  bundled  always the bundled model
  none     no AI engine

Reasoning modes (settings["ai_engine"]["modes"]), chosen per job:
  quick    thinking off: fast, the default
  deep     thinking on: the model reasons before answering (slower, longer)
Each mode may name its own model (blank = the engine's model), so Quick can be Gemma and Deep a heavier model.

Optional cloud AI (settings["cloud_ai"], off by default): the user's own Claude, OpenAI or Gemini account and key
(key kept by studio.keys, never in settings.json). When on, it serves the uses ticked in cloud_ai.use_for:
  chat     the Ask Saracen assistant
  writing  the writing tools (coverage)
Anything sent then leaves the computer under the user's account, so the UI marks every cloud answer.

Port 8799 is never probed or used: on DADS_BEAST it belongs to A.I.D.E.N..
"""
from __future__ import annotations

import atexit
import json
import platform
import os
import signal
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path

from . import refdata, store

OLLAMA_DEFAULT = "http://127.0.0.1:11434"
FORBIDDEN_PORTS = {8799}


class EngineError(RuntimeError):
    pass


class OutputError(EngineError):
    """The engine answered, but not with usable output (empty, cut off, or not the JSON asked for)."""


JSON_HINT = ("\n\nRespond with one JSON object only, no other text, starting with {{ and matching this JSON schema:\n"
             "{schema}")


@dataclass
class Engine:
    kind: str            # "ollama" | "openai" | "bundled" | "anthropic" | "cloud" (OpenAI-compatible cloud API)
    url: str             # base URL (no trailing slash); openai/bundled/cloud include /v1 (or the provider's base)
    model: str
    api_key: str = ""
    provider: str = ""   # cloud only: anthropic | openai | gemini

    @property
    def is_cloud(self) -> bool:
        return self.kind in ("anthropic", "cloud")

    def describe(self) -> str:
        if self.is_cloud:
            return f"{self.model} ({CLOUD[self.provider]['name']}, your cloud account)"
        where = {"ollama": "Ollama", "openai": "local model server", "bundled": "built-in engine"}[self.kind]
        return f"{self.model} ({where}{'' if self.kind == 'bundled' else ' at ' + self.url})"


# The user's own cloud account. Model ids change often: the default is a starting point and Settings lists the
# account's real models (13 Oct 2026: Anthropic docs use claude-opus-5-5; Google's OpenAI-compatible examples use
# gemini-3.8-flash; OpenAI's newest are the GPT-6 family).
CLOUD = {
    "anthropic": {"name": "Claude", "maker": "Anthropic", "url": "https://api.anthropic.com/v1", "model": "claude-sonnet-5-5",
                  "keys_at": "https://console.anthropic.com/settings/keys"},
    "openai": {"name": "ChatGPT", "maker": "OpenAI", "url": "https://api.openai.com/v1", "model": "gpt-5.5",
               "keys_at": "https://platform.openai.com/api-keys"},
    "gemini": {"name": "Gemini", "maker": "Google", "url": "https://generativelanguage.googleapis.com/v1beta/openai",
               "model": "gemini-3.8-flash", "keys_at": "https://aistudio.google.com/apikey"},
}
ANTHROPIC_VERSION = "2023-06-01"


def cloud_engine(settings: dict, use: str) -> Engine | None:
    """The user's cloud engine when it is switched on for this use ("chat" or "writing") and a key is saved."""
    from . import keys
    c = settings.get("cloud_ai") or {}
    prov = c.get("provider", "anthropic")
    if not c.get("enabled") or not (c.get("use_for") or {}).get(use) or prov not in CLOUD:
        return None
    key = keys.get(prov)
    if not key:
        return None
    return Engine("anthropic" if prov == "anthropic" else "cloud", CLOUD[prov]["url"], c.get("model") or CLOUD[prov]["model"], key, prov)


def _auth(engine: Engine) -> dict:
    if engine.kind == "anthropic":
        return {"x-api-key": engine.api_key, "anthropic-version": ANTHROPIC_VERSION}
    return {"Authorization": f"Bearer {engine.api_key}"} if engine.api_key else {}


def cloud_models(provider: str, key: str) -> list[str]:
    e = Engine("anthropic" if provider == "anthropic" else "cloud", CLOUD[provider]["url"], "", key, provider)
    data = _http(e.url + "/models", timeout=12, headers=_auth(e)).get("data", [])
    ids = [m.get("id", "") for m in data]
    return [i.split("/", 1)[-1] for i in ids if i]


# ---------------------------------------------------------------- HTTP

def _port_allowed(url: str) -> bool:
    from urllib.parse import urlparse
    try:
        return urlparse(url).port not in FORBIDDEN_PORTS
    except ValueError:
        return False


# Calls to this machine never go through a system proxy: Windows proxy settings do not exempt 127.0.0.1 by default.
_DIRECT = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def _is_local(url: str) -> bool:
    from urllib.parse import urlparse
    try:
        return (urlparse(url).hostname or "") in ("127.0.0.1", "localhost", "::1")
    except ValueError:
        return False


def _request(url: str, body: dict | None, api_key: str = "", headers: dict | None = None) -> urllib.request.Request:
    if not _port_allowed(url):
        raise EngineError("Port 8799 is reserved for A.I.D.E.N. and is never used by the Studio.")
    h = {"Content-Type": "application/json", **(headers or {})}
    if api_key and "Authorization" not in h:
        h["Authorization"] = f"Bearer {api_key}"
    return urllib.request.Request(url, data=None if body is None else json.dumps(body).encode(), headers=h)


def _open(req: urllib.request.Request, timeout: float):
    return (_DIRECT.open if _is_local(req.full_url) else urllib.request.urlopen)(req, timeout=timeout)


def _http(url: str, body: dict | None = None, timeout: float = 5, api_key: str = "", headers: dict | None = None) -> dict:
    req = _request(url, body, api_key, headers)
    try:
        with _open(req, timeout) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        detail = e.read()[:400].decode("utf-8", "replace")
        raise EngineError(f"{e.code} from {url}: {detail}") from e
    except (OSError, ValueError) as e:
        raise EngineError(f"{url} not reachable ({e.__class__.__name__})") from e


# ---------------------------------------------------------------- discovery

def ollama_models(url: str = OLLAMA_DEFAULT) -> list[dict]:
    return _http(url.rstrip("/") + "/api/tags", timeout=2).get("models", [])


def pick_gemma(models: list[dict]) -> str | None:
    """Largest installed Gemma (Ollama reports size in bytes)."""
    gemmas = [m for m in models if "gemma" in m.get("name", "").lower()]
    return max(gemmas, key=lambda m: m.get("size", 0))["name"] if gemmas else None


def openai_models(url: str, api_key: str = "") -> list[str]:
    return [m.get("id", "") for m in _http(url.rstrip("/") + "/models", timeout=3, api_key=api_key).get("data", [])]


SERVER_EXE = "llama-server.exe" if sys.platform == "win32" else "llama-server"


def _llm_dirs() -> list[Path]:
    """Where a built-in engine may live, first match wins:
    STUDIO_LLM_DIR (tests, support) · <install folder>/llm (installed by the Setup.exe "Install Gemma" option;
    outside _internal so upgrades never delete a multi-GB model) · <bundle>/llm (a build that packs the model in)."""
    dirs = [Path(os.environ["STUDIO_LLM_DIR"])] if os.environ.get("STUDIO_LLM_DIR") else []
    if getattr(sys, "frozen", False):
        dirs.append(Path(sys.executable).resolve().parent / "llm")
    dirs.append(refdata.app_root() / "llm")
    from . import store
    dirs.append(store.home() / "llm")      # where the Studio downloads Gemma when the install folder is read-only
    return dirs


def bundled_dir() -> Path:
    dirs = _llm_dirs()
    return next((d for d in dirs if (d / SERVER_EXE).exists()), dirs[0])


def _models(d: Path) -> list[Path]:
    found = (d / "models").glob("*.gguf") if (d / "models").exists() else []
    return [m for m in found if not m.name.lower().startswith("mmproj")]       # vision projectors are not models


def _size_tag(name: str) -> str:
    """'gemma-4-12b-it-qat-q4_0' -> '12b'; 'gemma-4-E4B_q4_0-it' -> 'e4b'."""
    import re
    m = re.search(r"(?<![a-z0-9])(e?\d+b)(?![a-z0-9])", name.lower())
    return m.group(1) if m else ""


def projector_for(gguf: Path) -> Path | None:
    """The vision add-on (mmproj) that belongs to this model, if installed: Gemma reads images with it."""
    tag = _size_tag(gguf.stem)
    d = gguf.parent
    for p in sorted(d.glob("*.gguf")) if d.exists() else []:
        if "mmproj" in p.name.lower() and tag and _size_tag(p.stem.lower().replace("mmproj", "")) == tag:
            return p
    return None


def can_see(engine: "Engine | None") -> tuple[bool, str]:
    """Whether this engine can read images (Look Book). The built-in Gemma needs its vision add-on installed."""
    if not engine:
        return False, "No AI engine connected."
    if engine.kind == "bundled":
        files = bundled_files()
        gguf = model_file(engine.model) or (files[1] if files else None)
        if gguf and projector_for(gguf):
            return True, ""
        return False, ("Gemma's vision add-on is not installed yet. Settings › Gemma on this computer downloads it "
                       "(175 MB for Gemma 4 12B, 1.0 GB for E4B).")
    return True, ""


MIN_MODEL_BYTES = 500_000_000      # anything smaller isn't a usable Gemma (or is still downloading)


def chosen_model() -> Path | None:
    """The model file picked with Settings › Locate a model (1.2.2), wherever it is, if it is still there."""
    from . import store
    p = ((store.load_settings().get("ai_engine") or {}).get("model_path") or "").strip()
    f = Path(p).expanduser() if p else None
    return f if f and f.is_file() and f.suffix.lower() == ".gguf" else None


def located_models() -> list[Path]:
    """Models outside the Studio's own folder (1.2.2; Tim, 5 Nov, on Jon's Mac): the chosen file, then any Gemma
    .gguf at the top of Downloads. Downloads isn't searched when a test or support build sets STUDIO_LLM_DIR."""
    out = [m for m in [chosen_model()] if m]
    if not os.environ.get("STUDIO_LLM_DIR"):
        try:
            for f in sorted((Path.home() / "Downloads").glob("*.gguf")):
                n = f.name.lower()
                if "gemma" in n and "mmproj" not in n and f not in out and f.stat().st_size >= MIN_MODEL_BYTES:
                    out.append(f)
        except OSError:
            pass
    return out


def model_file(stem: str) -> Path | None:
    """The file for a model name, in the Studio's folder or where it was found."""
    return next((m for m in _models(bundled_dir()) + located_models() if m.stem == stem), None)


def bundled_files() -> tuple[Path, Path] | None:
    """The engine and the model to run: the one chosen in Settings, else the largest in the Studio's folder (the larger
    Gemma writes better), else the largest Gemma found in Downloads."""
    exe = bundled_dir() / SERVER_EXE
    if not exe.exists():
        return None
    chosen = chosen_model()
    if chosen:
        return exe, chosen
    models = _models(bundled_dir()) or located_models()
    return (exe, max(models, key=lambda m: m.stat().st_size)) if models else None


def _memory_gb() -> int:
    from . import fetch
    return fetch.memory_gb()


def fit_engine(ctx: int, gpu_layers: int, slots: int) -> tuple[list[int], int, int]:
    """Size the engine to the machine (1.2.2). On 12 GB or less: one slot and at most an 8K context, so loading the
    model can't take the whole memory (Jon's 8 GB MacBook locked up with two 16K slots). Intel Macs run it on the
    processor: their built-in graphics share the same small memory."""
    tries = [slots, 1] if slots > 1 else [1]
    mem = _memory_gb()
    if mem and mem <= 12:
        tries, ctx = [1], min(ctx, 8192)
    if sys.platform == "darwin" and platform.machine() == "x86_64":
        gpu_layers = 0
    return tries, ctx, gpu_layers


MODES = ("quick", "deep")
DEFAULT_MODES = {"quick": {"model": "", "think": False}, "deep": {"model": "", "think": True}}


def mode_settings(settings: dict, mode: str | None) -> dict:
    s = settings.get("ai_engine", {})
    mode = mode if mode in MODES else s.get("default_mode", "quick")
    return {"mode": mode, **DEFAULT_MODES[mode], **(s.get("modes") or {}).get(mode, {})}


def resolve(settings: dict, mode: str | None = None, use: str = "writing") -> tuple[Engine | None, str]:
    """Pick the engine (and the mode's model, if it names one). Never starts anything.
    The user's cloud AI wins when it is switched on for this use; otherwise the local engine."""
    cloud = cloud_engine(settings, use) if use else None
    if cloud:
        return cloud, ""
    engine, why = _resolve(settings)
    want = mode_settings(settings, mode)["model"].strip() if mode else ""
    if not engine or not want or want == engine.model:
        return engine, why
    if engine.kind == "ollama":
        names = [m["name"] for m in ollama_models(engine.url)]
        if want not in names:
            return None, f"The {mode} model '{want}' is not installed in Ollama at {engine.url}."
    elif engine.kind == "bundled":
        if not model_file(want):
            return None, f"The {mode} model '{want}' is not in this installation."
    return Engine(engine.kind, engine.url, want, engine.api_key), ""


def _resolve(settings: dict) -> tuple[Engine | None, str]:
    s = settings.get("ai_engine", {})
    provider = s.get("provider", "auto")
    url = (s.get("url") or s.get("ollama_url") or "").rstrip("/")
    model = s.get("model", "")
    if provider == "none":
        return None, "No AI engine selected. Choose one in Settings."
    if provider in ("ollama", "auto"):
        o_url = url if provider == "ollama" and url else OLLAMA_DEFAULT
        try:
            models = ollama_models(o_url)
            names = [m["name"] for m in models]
            chosen = model if (provider == "ollama" and model) else pick_gemma(models)
            if chosen and chosen in names:
                return Engine("ollama", o_url, chosen), ""
            if provider == "ollama":
                return None, (f"Model '{model}' is not installed in Ollama at {o_url}." if model
                              else f"No Gemma model installed in Ollama at {o_url}.")
        except EngineError as e:
            if provider == "ollama":
                return None, f"Ollama not reachable at {o_url}. {e}"
    if provider == "openai":
        if not url:
            return None, "Enter the model server's address in Settings (for example http://127.0.0.1:8080/v1)."
        try:
            ids = openai_models(url, s.get("api_key", ""))
        except EngineError as e:
            return None, f"Model server not reachable at {url}. {e}"
        chosen = model or next((i for i in ids if "gemma" in i.lower()), ids[0] if ids else "")
        return (Engine("openai", url, chosen, s.get("api_key", "")), "") if chosen else (None, f"No models listed at {url}.")
    if provider in ("bundled", "auto"):
        files = bundled_files()
        if files:
            return Engine("bundled", "", files[1].stem), ""
        if provider == "bundled":
            return None, "No built-in model in this installation."
    return None, "No AI engine found on this computer. Writing tools need one; calculation tools work without it."


# ---------------------------------------------------------------- bundled server

_JOB = None   # Windows job object handle; kept open for the life of the Studio


def _tie_to_studio(proc: subprocess.Popen) -> None:
    """Make the OS stop the engine if the Studio dies (crash, Task Manager), not only on a clean exit."""
    global _JOB
    if sys.platform != "win32":
        return                                        # POSIX: handled by the parent-death signal in _child_setup
    try:
        import ctypes
        from ctypes import wintypes
        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        k32.CreateJobObjectW.restype = wintypes.HANDLE

        class BASIC(ctypes.Structure):
            _fields_ = [("PerProcessUserTimeLimit", ctypes.c_int64), ("PerJobUserTimeLimit", ctypes.c_int64),
                        ("LimitFlags", wintypes.DWORD), ("MinimumWorkingSetSize", ctypes.c_size_t),
                        ("MaximumWorkingSetSize", ctypes.c_size_t), ("ActiveProcessLimit", wintypes.DWORD),
                        ("Affinity", ctypes.c_size_t), ("PriorityClass", wintypes.DWORD), ("SchedulingClass", wintypes.DWORD)]

        class IO(ctypes.Structure):
            _fields_ = [(n, ctypes.c_uint64) for n in ("r", "w", "o", "rb", "wb", "ob")]

        class EXTENDED(ctypes.Structure):
            _fields_ = [("Basic", BASIC), ("Io", IO), ("ProcessMemoryLimit", ctypes.c_size_t),
                        ("JobMemoryLimit", ctypes.c_size_t), ("PeakProcessMemoryUsed", ctypes.c_size_t),
                        ("PeakJobMemoryUsed", ctypes.c_size_t)]
        if _JOB is None:
            job = k32.CreateJobObjectW(None, None)
            info = EXTENDED()
            info.Basic.LimitFlags = 0x2000                 # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
            if not k32.SetInformationJobObject(job, 9, ctypes.byref(info), ctypes.sizeof(info)):
                return
            _JOB = job
        k32.AssignProcessToJobObject(wintypes.HANDLE(_JOB), wintypes.HANDLE(int(proc._handle)))
    except Exception:  # noqa: BLE001 - never block the engine; a clean exit still stops it
        pass


PIDFILE = "llm-server.pid"


def _reap_stale() -> None:
    """Mac (and Linux): stop an engine a Studio that crashed or was force-quit left running. Windows ties the
    engine to the Studio with a job object and Linux with a parent-death signal; the Mac has neither, so the
    engine's process id is kept in the data folder and checked on the next start."""
    if sys.platform == "win32":
        return
    f = store.home() / PIDFILE
    try:
        pid = int(f.read_text().strip())
    except (OSError, ValueError):
        return
    try:
        # the program, or a script's path after its interpreter (macOS reports a script as /bin/sh); -ww: no width cut (1.2.1)
        cmd = subprocess.run(["ps", "-ww", "-p", str(pid), "-o", "command="], capture_output=True, text=True, timeout=5).stdout.split()
        if any(Path(a).name == "llama-server" for a in cmd[:2]):
            os.kill(pid, signal.SIGTERM)
    except (OSError, subprocess.SubprocessError):
        pass
    f.unlink(missing_ok=True)


_PRCTL = None
if sys.platform.startswith("linux"):
    try:
        import ctypes
        _PRCTL = ctypes.CDLL("libc.so.6", use_errno=True).prctl         # loaded here, in the Studio, never in the child
    except Exception:  # noqa: BLE001
        _PRCTL = None


def _child_setup():
    """Linux only (runs in the child between fork and exec): get SIGTERM if the Studio dies. Nothing is imported or
    loaded here: the Studio has many threads, and an import or library load in a forked child can hang on a lock
    another thread held (1.2.1: on the Mac the engine never started; the Mac uses _reap_stale instead)."""
    if _PRCTL is not None:
        _PRCTL(1, 15)                                                   # PR_SET_PDEATHSIG, SIGTERM

class _Bundled:
    """Starts the bundled llama.cpp server on first use and stops it when the Studio exits.

    Two slots, each with its own full context (Tim's PC, 13 Oct): llama-server's default is four slots sharing one
    unified context. A Deep-mode coverage step (7k prompt + 7k thinking) filled the shared 16k while Ask Jon asked a
    question, and both failed with "Context size has been exceeded". With a slot each, a background job and the chat
    can never take each other's room; a third request waits its turn. If a machine can't hold the second slot's
    memory, the engine falls back to one slot, where requests queue instead of failing."""

    SLOTS = 2

    def __init__(self):
        self.lock = threading.Lock()
        self.proc: subprocess.Popen | None = None
        self.url = ""
        self.model: Path | None = None
        self.projector: Path | None = None
        self.slots = self.SLOTS

    def ensure(self, ctx: int, gpu_layers: int, model: str = "", load_timeout: float = 600) -> str:
        with self.lock:
            files = bundled_files()
            if not files:
                raise EngineError("No built-in model in this installation.")
            exe, gguf = files
            if model and model_file(model):
                gguf = model_file(model)
            projector = projector_for(gguf)
            if self.proc and self.proc.poll() is None:
                if self.model == gguf and self.projector == projector:
                    return self.url
                self.stop()                                   # switching model: one loaded at a time
            self.model, self.projector = gguf, projector
            tries, ctx, gpu_layers = fit_engine(ctx, gpu_layers, self.SLOTS)
            for slots in tries:
                if self._start(exe, gguf, projector, ctx, gpu_layers, slots, load_timeout):
                    self.slots = slots
                    return self.url
            raise EngineError(f"Built-in engine stopped while loading (exit {self.proc.returncode if self.proc else '?'}).")

    def _start(self, exe: Path, gguf: Path, projector: Path | None, ctx: int, gpu_layers: int, slots: int,
               load_timeout: float) -> bool:
        """True once the server answers /health; False if it exits while loading (e.g. not enough memory)."""
        with socket.socket() as s:
            s.bind(("127.0.0.1", 0))
            port = s.getsockname()[1]
        _reap_stale()
        log = open(store.home() / "llm-server.log", "ab")
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        args = [str(exe), "-m", str(gguf), "--host", "127.0.0.1", "--port", str(port),
                "-c", str(ctx * slots), "-np", str(slots), "-ngl", str(gpu_layers), "--jinja", "--no-webui"]
        if slots > 1:
            args.append("--no-kv-unified")                # each slot keeps its own ctx; nobody borrows another's
        if projector:                                     # Gemma reads images (Look Book) with its vision add-on
            args += ["--mmproj", str(projector)]
        self.proc = subprocess.Popen(args,
                                     stdout=log, stderr=log, creationflags=flags,
                                     preexec_fn=_child_setup if _PRCTL is not None else None)
        _tie_to_studio(self.proc)
        if sys.platform != "win32":
            try:
                (store.home() / PIDFILE).write_text(str(self.proc.pid))
            except OSError:
                pass
        self.url = f"http://127.0.0.1:{port}"
        deadline = time.time() + load_timeout
        while time.time() < deadline:
            if self.proc.poll() is not None:
                return False
            try:
                _http(self.url + "/health", timeout=2)
                return True
            except EngineError:
                time.sleep(0.5)
        self.stop()
        raise EngineError("Built-in engine did not finish loading the model.")

    def exited(self) -> bool:
        return self.proc is not None and self.proc.poll() is not None

    def stopped_message(self) -> str:
        # Seen 12 Oct under test: the engine was killed for lack of memory part-way through a coverage.
        # The next request starts it again, so Retry works once memory is free.
        code = self.proc.returncode if self.proc else "?"
        return (f"The built-in AI engine stopped part-way through (exit code {code}). This usually means the computer "
                "ran out of memory. Close other programs and press Retry; if it happens again, run the installer again "
                "and choose the smaller model. Details: llm-server.log in the Studio data folder.")

    def stop(self):
        if self.proc and self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(10)
            except subprocess.TimeoutExpired:
                self.proc.kill()
        if self.proc is not None and sys.platform != "win32":
            (store.home() / PIDFILE).unlink(missing_ok=True)
        self.proc = None


BUNDLED = _Bundled()
atexit.register(BUNDLED.stop)


# ---------------------------------------------------------------- calls

def _b64(data: bytes) -> str:
    import base64
    return base64.b64encode(data).decode("ascii")


def _mime(data: bytes) -> str:
    return "image/png" if data[:8] == b"\x89PNG\r\n\x1a\n" else "image/webp" if data[8:12] == b"WEBP" else "image/jpeg"


def _user_message(engine: Engine, text: str, images: list[bytes] | None) -> dict:
    """The user turn, with images in the form each kind of server expects."""
    if not images:
        return {"role": "user", "content": text}
    if engine.kind == "ollama":
        return {"role": "user", "content": text, "images": [_b64(i) for i in images]}
    if engine.kind == "anthropic":
        return {"role": "user", "content": [{"type": "image", "source": {"type": "base64", "media_type": _mime(i), "data": _b64(i)}}
                                            for i in images] + [{"type": "text", "text": text}]}
    return {"role": "user", "content": [{"type": "image_url", "image_url": {"url": f"data:{_mime(i)};base64,{_b64(i)}"}}
                                        for i in images] + [{"type": "text", "text": text}]}


def chat(engine: Engine, system: str, user: str, *, schema: dict | None = None, settings: dict | None = None,
         max_tokens: int = 2048, temperature: float = 0.2, timeout: float = 1800, think: bool | None = None,
         images: list[bytes] | None = None, think_budget: int | None = None):
    """One completion. With a schema, the parsed JSON object is returned.

    Thinking models (Gemma 4, Qwen 3) reason before answering by default, which can spend the whole token budget
    and return nothing, so thinking is off unless settings or the caller turn it on. When it is on, the built-in
    engine gets a thinking budget (think_budget, default 60% of max_tokens) and is told to write the answer when it
    runs out: on Tim's PC (13 Oct) Deep-mode coverage thought for 7,200 tokens and returned nothing.
    Structured output: servers constrain the reply to the schema, but llama.cpp applies that constraint lazily for
    models with a thinking channel. Tested 12 Oct with Gemma 4 on llama.cpp b11577: unless the user message itself
    asks for JSON, the model can drift into its thought channel and return nothing. So the request always says so,
    with the schema, and one retry with a firmer instruction follows an empty or invalid reply."""
    once = lambda u, t: _chat_once(engine, system, u, schema=schema, settings=settings, max_tokens=max_tokens,
                                   temperature=t, timeout=timeout, think=think, images=images, think_budget=think_budget)
    if not schema:
        return once(user, temperature)
    ask = user + JSON_HINT.format(schema=json.dumps(schema, ensure_ascii=False))
    try:
        return once(ask, temperature)
    except OutputError:
        return once(ask + "\n\nYour previous reply was empty or was not valid JSON. Reply with the JSON object only.", 0.0)


THINK_DONE = "\n\nThinking time is up. Write the answer now.\n"


def _chat_once(engine: Engine, system: str, user: str, *, schema: dict | None, settings: dict | None,
               max_tokens: int, temperature: float, timeout: float, think: bool | None, images: list[bytes] | None = None,
               think_budget: int | None = None):
    s = (settings or {}).get("ai_engine", {})
    ctx = int(s.get("context", 16384))
    think = bool(s.get("thinking", False)) if think is None else think
    messages = [{"role": "system", "content": system}, _user_message(engine, user, images)]
    if engine.is_cloud:
        text, finish = _cloud_once(engine, system, [_user_message(engine, user, images)], schema=schema, max_tokens=max_tokens,
                                   temperature=temperature, timeout=min(timeout, 600))
    elif engine.kind == "ollama":
        body = {"model": engine.model, "messages": messages, "stream": False, "think": think,
                "options": {"temperature": temperature, "num_ctx": ctx, "num_predict": max_tokens}}
        if schema:
            body["format"] = schema
        try:
            res = _http(engine.url + "/api/chat", body, timeout=timeout)
        except EngineError as e:
            if "think" not in str(e).lower():
                raise
            body.pop("think")                       # model without a thinking mode
            res = _http(engine.url + "/api/chat", body, timeout=timeout)
        text, finish = res["message"].get("content", ""), res.get("done_reason", "")
    else:
        base = engine.url
        if engine.kind == "bundled":
            base = BUNDLED.ensure(ctx, int(s.get("gpu_layers", 99)), engine.model) + "/v1"
        body = {"model": engine.model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens,
                "chat_template_kwargs": {"enable_thinking": think}}
        if think and engine.kind == "bundled":           # our llama.cpp build stops thinking at the budget
            body["reasoning_budget_tokens"] = int(think_budget if think_budget is not None else max_tokens * 0.6)
            body["reasoning_budget_message"] = THINK_DONE
        if schema:
            body["response_format"] = {"type": "json_schema", "json_schema": {"name": "output", "strict": True, "schema": schema}}
        try:
            res = _http(base.rstrip("/") + "/chat/completions", body, timeout=timeout, api_key=engine.api_key)
        except EngineError:
            if engine.kind == "bundled" and BUNDLED.exited():
                raise EngineError(BUNDLED.stopped_message()) from None
            raise
        choice = res["choices"][0]
        text, finish = choice["message"].get("content") or "", choice.get("finish_reason", "")
    if not text.strip():
        raise OutputError("The model returned no text" + (" before reaching its length limit." if finish == "length" else "."))
    if not schema:
        return text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        a, b = text.find("{"), text.rfind("}")           # cloud models may wrap the object in a code fence
        if engine.is_cloud and 0 <= a < b:
            try:
                return json.loads(text[a:b + 1])
            except json.JSONDecodeError:
                pass
        raise OutputError(f"The model returned output that is not valid JSON ({e}).") from e


def _cloud_body(engine: Engine, system: str, messages: list[dict], max_tokens: int, temperature: float, stream: bool) -> dict:
    if engine.kind == "anthropic":
        return {"model": engine.model, "system": system, "messages": messages, "max_tokens": max_tokens,
                "temperature": temperature, "stream": stream}
    body = {"model": engine.model, "messages": [{"role": "system", "content": system}, *messages], "stream": stream}
    if engine.provider == "openai":                   # newer OpenAI models take max_completion_tokens and fixed sampling
        body["max_completion_tokens"] = max_tokens
    else:
        body.update(max_tokens=max_tokens, temperature=temperature)
    return body


def _cloud_once(engine: Engine, system: str, messages: list[dict], *, schema: dict | None, max_tokens: int,
                temperature: float, timeout: float) -> tuple[str, str]:
    body = _cloud_body(engine, system, messages, max_tokens, temperature, stream=False)
    if engine.kind == "anthropic":
        res = _http(engine.url + "/messages", body, timeout=timeout, headers=_auth(engine))
        text = "".join(b.get("text", "") for b in res.get("content", []) if b.get("type") == "text")
        return text, {"max_tokens": "length"}.get(res.get("stop_reason", ""), res.get("stop_reason", ""))
    if schema:
        body["response_format"] = {"type": "json_object"}
    try:
        res = _http(engine.url + "/chat/completions", body, timeout=timeout, headers=_auth(engine))
    except EngineError as e:
        if not schema or not str(e).startswith("400"):
            raise
        body.pop("response_format")                  # a provider without JSON mode: the prompt still asks for JSON
        res = _http(engine.url + "/chat/completions", body, timeout=timeout, headers=_auth(engine))
    choice = res["choices"][0]
    return choice["message"].get("content") or "", choice.get("finish_reason", "")


def stream(engine: Engine, system: str, messages: list[dict], *, settings: dict | None = None, max_tokens: int = 1200,
           temperature: float = 0.4, timeout: float = 600):
    """Yield the reply as it is written (Ask Saracen). Thinking stays off: the assistant should answer, not muse."""
    s = (settings or {}).get("ai_engine", {})
    if engine.kind == "anthropic":
        url, body = engine.url + "/messages", _cloud_body(engine, system, messages, max_tokens, temperature, True)
    elif engine.kind == "cloud":
        url, body = engine.url + "/chat/completions", _cloud_body(engine, system, messages, max_tokens, temperature, True)
    elif engine.kind == "ollama":
        url = engine.url + "/api/chat"
        body = {"model": engine.model, "messages": [{"role": "system", "content": system}, *messages], "stream": True,
                "think": False, "options": {"temperature": temperature, "num_ctx": int(s.get("context", 16384)), "num_predict": max_tokens}}
    else:
        base = engine.url
        if engine.kind == "bundled":
            base = BUNDLED.ensure(int(s.get("context", 16384)), int(s.get("gpu_layers", 99)), engine.model) + "/v1"
        url = base.rstrip("/") + "/chat/completions"
        body = {"model": engine.model, "messages": [{"role": "system", "content": system}, *messages], "stream": True,
                "temperature": temperature, "max_tokens": max_tokens, "chat_template_kwargs": {"enable_thinking": False}}
    req = _request(url, body, "" if engine.is_cloud else engine.api_key, _auth(engine) if engine.is_cloud else None)
    try:
        resp = _open(req, timeout)
    except urllib.error.HTTPError as e:
        raise EngineError(f"{e.code} from {url}: {e.read()[:300].decode('utf-8', 'replace')}") from e
    except OSError as e:
        if engine.kind == "bundled" and BUNDLED.exited():
            raise EngineError(BUNDLED.stopped_message()) from None
        raise EngineError(f"{url} not reachable ({e.__class__.__name__})") from e
    with resp:
        for raw in resp:
            line = raw.decode("utf-8", "replace").strip()
            if not line:
                continue
            if engine.kind == "ollama":
                d = json.loads(line)
                if d.get("error"):
                    raise EngineError(d["error"])
                if d.get("message", {}).get("content"):
                    yield d["message"]["content"]
                if d.get("done"):
                    return
                continue
            if not line.startswith("data:"):
                continue
            data = line[5:].strip()
            if data == "[DONE]":
                return
            try:
                d = json.loads(data)
            except json.JSONDecodeError:
                continue
            if engine.kind == "anthropic":
                if d.get("type") == "content_block_delta" and d.get("delta", {}).get("type") == "text_delta":
                    yield d["delta"]["text"]
                elif d.get("type") == "error":
                    raise EngineError(d.get("error", {}).get("message", "The cloud AI reported an error."))
                elif d.get("type") == "message_stop":
                    return
            else:
                if d.get("error"):
                    raise EngineError(str(d["error"].get("message", d["error"])))
                for c in d.get("choices", []):
                    piece = (c.get("delta") or {}).get("content")
                    if piece:
                        yield piece


def status(settings: dict) -> dict:
    engine, reason = resolve(settings, use="")
    if not engine:
        return {"connected": False, "reason": reason}
    out = {"connected": True, "engine": engine.kind, "model": engine.model, "description": engine.describe(), "reason": ""}
    if engine.kind == "bundled":
        out["note"] = "Starts when a writing tool first runs."
    return out


def cloud_status(settings: dict) -> dict:
    from . import keys
    c = settings.get("cloud_ai") or {}
    prov = c.get("provider", "anthropic")
    prov = prov if prov in CLOUD else "anthropic"
    return {"enabled": bool(c.get("enabled")), "provider": prov, "model": c.get("model") or CLOUD[prov]["model"],
            "use_for": {"chat": True, "writing": False, **(c.get("use_for") or {})},
            "keys": {p: keys.hint(p) for p in CLOUD}, "providers": CLOUD,
            "active": {u: bool(cloud_engine(settings, u)) for u in ("chat", "writing")}}
