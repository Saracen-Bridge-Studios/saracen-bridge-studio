"""The hub's settings from its environment (the deploy kit's .env)."""
from __future__ import annotations

import os


def load() -> dict:
    cfg: dict = {}
    if os.environ.get("LIVEKIT_URL"):
        cfg["livekit"] = {"url": os.environ["LIVEKIT_URL"], "public_url": os.environ.get("LIVEKIT_PUBLIC_URL", os.environ["LIVEKIT_URL"]),
                          "key": os.environ.get("LIVEKIT_API_KEY", ""), "secret": os.environ.get("LIVEKIT_API_SECRET", "")}
    if os.environ.get("VAPID_PRIVATE_KEY"):
        from .push import Push
        cfg["push"] = Push(os.environ["VAPID_PRIVATE_KEY"], os.environ.get("VAPID_SUBJECT", "mailto:room@example.invalid"))
    return cfg
