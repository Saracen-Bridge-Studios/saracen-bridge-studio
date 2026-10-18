"""The user's cloud AI keys: kept on this computer only, never in settings.json, never sent to the page.

Windows: encrypted with DPAPI for the signed-in Windows user (only that user on this computer can decrypt it).
Mac: encrypted with a random key kept in the user's login Keychain (the Mac's equivalent of DPAPI); if the Keychain
  can't be reached (a locked build machine), the file falls back to owner-only, as on Linux.
Elsewhere (tests, the Linux build): the file is readable by the owner only.

The Room's device keys are sealed with these same functions (studio.room.client).
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
    KEYCHAIN_SERVICE = "Saracen Bridge Studio"
    KEYCHAIN_ACCOUNT = "sealing key"

    def _keychain_key(create: bool) -> bytes | None:
        """The 32-byte sealing key from the Mac's login Keychain (made on first use); None off the Mac or if the
        Keychain can't be reached."""
        if sys.platform != "darwin":
            return None
        try:
            import keyring
            got = keyring.get_password(KEYCHAIN_SERVICE, KEYCHAIN_ACCOUNT)
            if got:
                return base64.b64decode(got)
            if not create:
                return None
            k = os.urandom(32)
            keyring.set_password(KEYCHAIN_SERVICE, KEYCHAIN_ACCOUNT, base64.b64encode(k).decode())
            return k
        except Exception:  # noqa: BLE001 - no Keychain (locked build machine): owner-only file, as on Linux
            return None

    def _seal(b: bytes) -> str:
        k = _keychain_key(create=True)
        if k:
            from nacl.secret import SecretBox
            return "kc:" + base64.b64encode(bytes(SecretBox(k).encrypt(b))).decode()
        return "plain:" + base64.b64encode(b).decode()

    def _open(s: str) -> bytes:
        if s.startswith("kc:"):
            k = _keychain_key(create=False)
            if not k:
                raise OSError("This key was sealed in another Mac user's Keychain.")
            from nacl.secret import SecretBox
            return SecretBox(k).decrypt(base64.b64decode(s[3:]))
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
    except Exception:  # noqa: BLE001 - a key sealed for another user or computer reads as no key
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
