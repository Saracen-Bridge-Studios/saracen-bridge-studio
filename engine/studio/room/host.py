"""This PC hosts the Room (1.0.8.1).

Whoever starts a project hosts it: their Studio runs the Room's hub on their own PC, and everyone they invite connects
to that PC. Jon's projects live on Jon's PC, Colin's on Colin's; a person in both sees them together in one Studio.
Nobody types an address: the invite link carries it.

The hub runs inside the Studio process on its own listener (port 8710, all network interfaces, so the team can reach
it). The Studio's own pages and API stay on 127.0.0.1. The hub holds ciphertext only, as before. Voice and meetings
use LiveKit (Apache-2.0), started beside it when the Studio carries it (TCP 7880-7881, UDP 50000-50100). Never port 8799.
"""
from __future__ import annotations

import atexit
import json
import os
import secrets
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

from .. import refdata, store
from .client import RoomError

PORT = int(os.environ.get("ROOM_HOST_PORT", "8710"))
LK_PORT, LK_TCP, LK_UDP = 7880, 7881, (50000, 50100)
assert PORT != 8799, "8799 is reserved"

_S: dict = {"server": None, "thread": None, "app": None, "lk": None, "error": "", "lock": threading.Lock()}


def folder() -> Path:
    p = store.home() / "room-host"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _cfg() -> dict:
    f = folder() / "host.json"
    cfg = json.loads(f.read_text()) if f.exists() else {}
    if not cfg.get("vapid") or not cfg.get("lk_secret"):
        from room_hub.push import new_vapid_key
        cfg.setdefault("vapid", new_vapid_key())
        cfg.setdefault("lk_key", "room-" + secrets.token_hex(4))
        cfg.setdefault("lk_secret", secrets.token_urlsafe(36))
        cfg.setdefault("enabled", False)
        f.write_text(json.dumps(cfg, indent=1))
        try:
            os.chmod(f, 0o600)
        except OSError:
            pass
    return cfg


def _save(cfg: dict):
    (folder() / "host.json").write_text(json.dumps(cfg, indent=1))


def enabled() -> bool:
    f = folder() / "host.json"
    return f.exists() and bool(json.loads(f.read_text()).get("enabled"))


def lan_ip() -> str:
    """This PC's address on the local network (no traffic is sent: a UDP socket just picks its route)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        ip = s.getsockname()[0]
    except OSError:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def address() -> str:
    """The address people on this network use: it goes into invite links."""
    return f"http://{lan_ip()}:{PORT}"


def local() -> str:
    """The address this PC's own Studio uses (never changes when the network does)."""
    return f"http://127.0.0.1:{PORT}"


def running() -> bool:
    return bool(_S["server"] and _S["server"].started and _S["thread"] and _S["thread"].is_alive())


def status() -> dict:
    return {"hosting": running(), "enabled": enabled(), "address": address() if running() else "", "error": _S["error"],
            "meetings": bool(_S["lk"])}


# ------------------------------------------------------------------ LiveKit beside the hub
def _livekit_bin() -> Path | None:
    for p in (os.environ.get("ROOM_LIVEKIT_BIN"), refdata.app_root() / "livekit" / "livekit-server.exe",
              refdata.app_root() / "livekit" / "livekit-server"):
        if p and Path(p).exists():
            return Path(p)
    return None


def _lk_up() -> bool:
    try:
        with socket.create_connection(("127.0.0.1", LK_PORT), timeout=0.5):
            return True
    except OSError:
        return False


def _start_livekit(cfg: dict) -> dict | None:
    """Start LiveKit for huddles and meetings (or reuse one this PC already started). None if it isn't bundled."""
    lk = {"url": f"http://127.0.0.1:{LK_PORT}", "public_url": "ws://{host}:%d" % LK_PORT,
          "key": cfg["lk_key"], "secret": cfg["lk_secret"]}
    if _lk_up():
        return lk
    exe = _livekit_bin()
    if not exe:
        return None
    conf = folder() / "livekit.yaml"
    # A UDP port range rather than one shared UDP port: the shared-port mode failed to open its socket on the
    # Windows test machine (winapi error 10045); the range works. Keys go in the file (kept in this user's folder).
    conf.write_text(f"port: {LK_PORT}\nrtc:\n  tcp_port: {LK_TCP}\n  port_range_start: {LK_UDP[0]}\n"
                    f"  port_range_end: {LK_UDP[1]}\n  use_external_ip: false\n"
                    f"keys:\n  {cfg['lk_key']}: {cfg['lk_secret']}\nlogging:\n  level: warn\n")
    try:
        os.chmod(conf, 0o600)
    except OSError:
        pass
    env = dict(os.environ)
    flags = 0x08000000 if sys.platform == "win32" else 0          # CREATE_NO_WINDOW
    log = open(folder() / "livekit.log", "ab")
    proc = subprocess.Popen([str(exe), "--config", str(conf)], env=env, stdout=log, stderr=log,
                            stdin=subprocess.DEVNULL, creationflags=flags)
    _S["lk_proc"] = proc
    atexit.register(lambda: proc.poll() is None and proc.terminate())
    for _ in range(40):
        if _lk_up():
            return lk
        if proc.poll() is not None:
            return None
        time.sleep(0.25)
    return lk if _lk_up() else None


# ------------------------------------------------------------------ the hub
def start() -> dict:
    """Run the hub on this PC (idempotent). Raises RoomError with a plain reason if it can't."""
    with _S["lock"]:
        if running():
            return status()
        import uvicorn
        from room_hub import retention
        from room_hub.app import create_app
        from room_hub.push import Push
        cfg = _cfg()
        lk = _start_livekit(cfg)
        _S["lk"] = lk
        app = create_app(folder() / "hub", livekit=lk, push=Push(cfg["vapid"], "mailto:room@saracen.local"))
        server = uvicorn.Server(uvicorn.Config(app, host="0.0.0.0", port=PORT, log_level="warning", proxy_headers=False,
                                               ws="websockets", lifespan="off"))
        server.install_signal_handlers = lambda: None   # the Studio owns the process's signals
        th = threading.Thread(target=server.run, daemon=True, name="room-host")
        th.start()
        for _ in range(100):
            if server.started or not th.is_alive():
                break
            time.sleep(0.1)
        if not server.started:
            _S["error"] = f"Port {PORT} on this PC is in use by another program, so the Room couldn't start."
            raise RoomError(_S["error"])
        retention.start(app.state.store)
        _S.update(server=server, thread=th, app=app, error="")
        cfg["enabled"] = True
        _save(cfg)
        return status()


def founder_token() -> str | None:
    """A one-time founder code for this PC's own hub, or None if it already has its founder."""
    from room_hub.__main__ import founder_token as ft
    st = _S["app"].state.store
    if st.one("SELECT 1 FROM users WHERE founder=1"):
        return None
    return ft(st)


def autostart():
    """On Studio start: if this PC hosts a Room, bring it up so the team can connect."""
    if enabled():
        try:
            start()
        except Exception as e:  # noqa: BLE001 - the Room page shows the reason
            _S["error"] = str(e)


def stop():
    """Stop hosting in this process (tests, and the Studio shutting down)."""
    srv = _S.get("server")
    if srv:
        srv.should_exit = True
        if _S["thread"]:
            _S["thread"].join(timeout=10)
    p = _S.get("lk_proc")
    if p and p.poll() is None:
        p.terminate()
    _S.update(server=None, thread=None, app=None, lk=None, lk_proc=None)
