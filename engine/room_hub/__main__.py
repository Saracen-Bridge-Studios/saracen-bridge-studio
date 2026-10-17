"""Run the Room hub.

  python -m room_hub init  --data <folder>          prints the one-time founder link token (first run only)
  python -m room_hub serve --data <folder> [--host 0.0.0.0] [--port 8710]

The hub listens on plain HTTP; in production it sits behind Caddy, which adds TLS (see deploy/README.md).
Never use port 8799 (A.I.D.E.N. on DADS_BEAST).
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys
from pathlib import Path

import room_crypto as rc


def founder_token(store) -> str:
    """A new one-time founder token (only while nobody has founded the Room). Stored hashed."""
    if store.one("SELECT 1 FROM users WHERE founder=1"):
        raise SystemExit("This Room already has a founder.")
    tok = rc.b64e(os.urandom(24))
    with store.lock:
        store.meta("founder_token", hashlib.sha256(tok.encode()).hexdigest())
    return tok


def main(argv=None):
    ap = argparse.ArgumentParser(prog="room_hub")
    ap.add_argument("command", choices=["init", "serve", "purge", "vapid"])
    ap.add_argument("--data", default=os.environ.get("ROOM_DATA", "room-data"))
    ap.add_argument("--host", default=os.environ.get("ROOM_HOST", "127.0.0.1"))
    ap.add_argument("--port", type=int, default=int(os.environ.get("ROOM_PORT", "8710")))
    a = ap.parse_args(argv)
    if a.port == 8799:
        raise SystemExit("Port 8799 is reserved. Pick another.")
    from .db import Store
    if a.command == "init":
        print("Founder token (use it once, in the Studio: Room › Set up this Room):")
        print(founder_token(Store(Path(a.data))))
        return
    if a.command == "vapid":
        from .push import new_vapid_key
        print("VAPID_PRIVATE_KEY=" + new_vapid_key())
        return
    if a.command == "purge":
        from .retention import purge
        print("Deleted:", purge(Store(Path(a.data))) or "nothing due")
        return
    import uvicorn
    from .app import create_app
    from .settings import load
    from .retention import start
    cfg = load()
    app = create_app(Path(a.data), livekit=cfg.get("livekit"), push=cfg.get("push"))
    start(app.state.store)
    uvicorn.run(app,
                host=a.host, port=a.port, proxy_headers=True, forwarded_allow_ips="*", log_level="info")


if __name__ == "__main__":
    main(sys.argv[1:])
