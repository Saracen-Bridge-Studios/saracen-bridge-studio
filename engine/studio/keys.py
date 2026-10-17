"""The user's cloud AI keys: kept on this computer only, never in settings.json, never sent to the page.

Windows: encrypted with DPAPI for the signed-in Windows user (only that user on this PC can decrypt it).
Elsewhere (tests, the Linux build): the file is readable by the owner only.
"""
from __future__ import annotations

import base64
import json
import os
import sys

from . import store

FILE = "cloud_keys.json"


def _path():
    return store.home() / FILE


if sys.platform == "win32":
    import ctypes
    from ctypes import wintypes

    class _Blob(ctypes.Structure):
        _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_char))]

    def _call(fn, data: bytes) -> bytes:
        buf = ctypes.create_string_buffer(data, len(data))
        src, out = _Blob(len(data), ctypes.cast(buf, ctypes.POINTER(ctypes.c_char))), _Blob()
        if not fn(ctypes.byref(src), None, None, None, None, 0x01, ctypes.byref(out)):   # CRYPTPROTECT_UI_FORBIDDEN
            raise OSError("Windows could not protect the key.")
        try:
            return ctypes.string_at(out.pbData, out.cbData)
        finally:
            ctypes.windll.kernel32.LocalFree(out.pbData)

    def _seal(b: bytes) -> str:
        return "dpapi:" + base64.b64encode(_call(ctypes.windll.crypt32.CryptProtectData, b)).decode()

    def _open(s: str) -> bytes:
        if s.startswith("dpapi:"):
            return _call(ctypes.windll.crypt32.CryptUnprotectData, base64.b64decode(s[6:]))
        return base64.b64decode(s)
else:
    def _seal(b: bytes) -> str:
        return "plain:" + base64.b64encode(b).decode()

    def _open(s: str) -> bytes:
        return base64.b64decode(s.split(":", 1)[-1])


def _load() -> dict:
    try:
        return json.loads(_path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def get(provider: str) -> str:
    raw = _load().get(provider)
    if not raw:
        return ""
    try:
        return _open(raw).decode()
    except Exception:  # noqa: BLE001 - a key sealed for another Windows user or PC reads as no key
        return ""


def put(provider: str, key: str) -> None:
    data = _load()
    key = (key or "").strip()
    if key:
        data[provider] = _seal(key.encode())
    else:
        data.pop(provider, None)
    p = _path()
    p.write_text(json.dumps(data), encoding="utf-8")
    if sys.platform != "win32":
        os.chmod(p, 0o600)


def hint(provider: str) -> str:
    """'…abcd' for a saved key, '' for none: enough to recognise it, never enough to use it."""
    k = get(provider)
    return f"…{k[-4:]}" if len(k) >= 8 else ("saved" if k else "")
