"""Web mode (1.3.0): the Studio on a server, for a team, in their browsers (Tim and Jon, 9 Nov 2026).

Switched on by STUDIO_WEB=1 (the server's setup sets it). The desktop app is unchanged: without the switch none of this
runs. What web mode adds:

* team sign-in: a login per person (email and password), kept in the data folder as web_users.json. Passwords are
  hashed with scrypt (n=2^17, r=8, p=1, 16-byte salt: OWASP's figures), never stored or logged in clear.
* sessions held on the server: a random 256-bit id in an HttpOnly, SameSite=Strict cookie (Secure over https), a new id
  at every sign-in, 12 hours idle and 7 days at most, and every session of a person ends when their password changes.
* sign-in throttling: five wrong passwords in 15 minutes for one email, or twenty from one address, wait 15 minutes
  (a pause, not a permanent lock-out, so nobody can lock a colleague out on purpose).
* cross-site requests refused: a request that changes something must come from the Studio's own pages (the browser's
  Sec-Fetch-Site or Origin header), on top of the SameSite cookie.
* the AI brain from the server: the company's cloud AI key lives on the server (STUDIO_AI_KEY), never in a browser.
* Import data: the desktop Studio's data folder, zipped, brings its Library across; entries that would land outside the
  Library are refused (a "zip slip" restore was CVE-2026-29065 in another app).

Sources: Rule 1 pass, 9 Nov (MDN session management; OWASP ASVS V3; OWASP scrypt figures; FastAPI behind a proxy;
Anthropic API and data retention), in docs/CIPHER_SARACEN_STUDIO_WEB_20261109.md.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import shutil
import threading
import time
import zipfile
from pathlib import Path

from . import store

ENABLED = os.environ.get("STUDIO_WEB") == "1"
COOKIE = "sb_session"
USERS_FILE = "web_users.json"
IDLE_S, ABSOLUTE_S = 12 * 3600, 7 * 24 * 3600
SCRYPT = {"n": 2 ** 17, "r": 8, "p": 1, "dklen": 32}
SCRYPT_MAXMEM = 256 * 1024 * 1024
MAX_FAILS_EMAIL, MAX_FAILS_IP, WINDOW_S = 5, 20, 15 * 60
MAX_IMPORT_BYTES = int(os.environ.get("STUDIO_WEB_MAX_IMPORT_GB", "20")) * 1024 ** 3
ROLES = ("admin", "member")

_lock = threading.Lock()
_sessions: dict[str, dict] = {}
_fails: dict[str, list[float]] = {}


class WebError(Exception):
    def __init__(self, status: int, message: str, retry_after: int | None = None):
        super().__init__(message)
        self.status, self.retry_after = status, retry_after


# ---------------------------------------------------------------- people
def _users_path() -> Path:
    return store.home() / USERS_FILE


def users() -> dict:
    f = _users_path()
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}


def _save(us: dict) -> None:
    f = _users_path()
    tmp = f.with_suffix(".tmp")
    tmp.write_text(json.dumps(us, indent=1), encoding="utf-8")
    try:
        os.chmod(tmp, 0o600)
    except OSError:
        pass
    tmp.replace(f)


def _hash(password: str, salt: bytes) -> str:
    return hashlib.scrypt(password.encode("utf-8"), salt=salt, maxmem=SCRYPT_MAXMEM, **SCRYPT).hex()


def _norm(email: str) -> str:
    return (email or "").strip().lower()


def public(email: str, u: dict) -> dict:
    return {"email": email, "name": u.get("name", ""), "role": u.get("role", "member"), "created": u.get("created", "")}


def add_user(email: str, name: str, role: str = "member", password: str | None = None) -> str:
    """Add a person; returns their password (a new random one unless given). Shown once, never stored in clear."""
    email = _norm(email)
    if "@" not in email or len(email) > 200:
        raise WebError(400, "Enter the person's email address.")
    if role not in ROLES:
        raise WebError(400, "Role is admin or member.")
    password = password or secrets.token_urlsafe(12)
    if len(password) < 10:
        raise WebError(400, "Passwords are at least 10 characters.")
    salt = os.urandom(16)
    with _lock:
        us = users()
        if email in us:
            raise WebError(409, f"{email} already has a login.")
        us[email] = {"name": (name or "").strip()[:120], "role": role, "salt": salt.hex(), "hash": _hash(password, salt),
                     "created": time.strftime("%Y-%m-%d %H:%M")}
        _save(us)
    return password


def remove_user(email: str, by: str) -> None:
    email = _norm(email)
    with _lock:
        us = users()
        if email not in us:
            raise WebError(404, "No such login.")
        if email == by:
            raise WebError(400, "You can't remove your own login.")
        if us[email].get("role") == "admin" and sum(u.get("role") == "admin" for u in us.values()) == 1:
            raise WebError(400, "The last admin can't be removed.")
        del us[email]
        _save(us)
    end_sessions(email)


def set_password(email: str, password: str | None = None) -> str:
    """A new password (random unless given); every session of that person ends."""
    email = _norm(email)
    password = password or secrets.token_urlsafe(12)
    if len(password) < 10:
        raise WebError(400, "Passwords are at least 10 characters.")
    salt = os.urandom(16)
    with _lock:
        us = users()
        if email not in us:
            raise WebError(404, "No such login.")
        us[email].update(salt=salt.hex(), hash=_hash(password, salt))
        _save(us)
    end_sessions(email)
    return password


def check_password(email: str, password: str) -> bool:
    u = users().get(_norm(email))
    salt = bytes.fromhex(u["salt"]) if u else b"\0" * 16           # unknown email: same work, so timing tells nothing
    got = _hash(password or "", salt)
    return bool(u) and hmac.compare_digest(got, u["hash"])


# ---------------------------------------------------------------- sessions
def _throttled(key: str, limit: int, now: float) -> int:
    hits = [t for t in _fails.get(key, []) if now - t < WINDOW_S]
    _fails[key] = hits
    return int(WINDOW_S - (now - hits[0])) + 1 if len(hits) >= limit else 0


def login(email: str, password: str, ip: str = "") -> tuple[str, dict]:
    email, now = _norm(email), time.time()
    with _lock:
        wait = max(_throttled("e:" + email, MAX_FAILS_EMAIL, now), _throttled("i:" + ip, MAX_FAILS_IP, now) if ip else 0)
    if wait:
        raise WebError(429, f"Too many attempts. Try again in {max(1, wait // 60)} minutes.", wait)
    if not check_password(email, password):
        with _lock:
            _fails.setdefault("e:" + email, []).append(now)
            if ip:
                _fails.setdefault("i:" + ip, []).append(now)
        raise WebError(401, "That email and password don't match.")
    sid = secrets.token_urlsafe(32)                                   # 256 bits; a new id at every sign-in
    with _lock:
        _fails.pop("e:" + email, None)
        _sessions[sid] = {"email": email, "created": now, "seen": now}
    return sid, public(email, users()[email])


def session(sid: str | None) -> dict | None:
    if not sid:
        return None
    now = time.time()
    with _lock:
        s = _sessions.get(sid)
        if not s or now - s["seen"] > IDLE_S or now - s["created"] > ABSOLUTE_S:
            _sessions.pop(sid, None)
            return None
        s["seen"] = now
        email = s["email"]
    u = users().get(email)
    if not u:                                                         # removed while signed in
        logout(sid)
        return None
    return public(email, u)


def logout(sid: str | None) -> None:
    with _lock:
        _sessions.pop(sid or "", None)


def end_sessions(email: str) -> None:
    with _lock:
        for sid in [k for k, v in _sessions.items() if v["email"] == email]:
            del _sessions[sid]


def same_site(headers) -> bool:
    """A state-changing request must come from the Studio's own pages. Browsers send Sec-Fetch-Site; older ones send
    Origin. A request with neither isn't from a browser, so it carries no one's cookie."""
    site = headers.get("sec-fetch-site")
    if site:
        return site in ("same-origin", "none")
    origin = headers.get("origin")
    if not origin:
        return True
    host = headers.get("x-forwarded-host") or headers.get("host") or ""
    return origin.split("://", 1)[-1].rstrip("/") == host


# ---------------------------------------------------------------- the AI brain
def ai() -> dict:
    """The company's cloud AI, set on the server: STUDIO_AI_PROVIDER (openai, the default; anthropic or gemini),
    STUDIO_AI_KEY, STUDIO_AI_MODEL (optional: blank uses the Studio's default for that provider)."""
    prov = os.environ.get("STUDIO_AI_PROVIDER", "openai").strip().lower()      # Tim, 9 Nov: through Jon's OpenAI account
    return {"provider": prov, "key": os.environ.get("STUDIO_AI_KEY", "").strip(), "model": os.environ.get("STUDIO_AI_MODEL", "").strip()}


# ---------------------------------------------------------------- Import data
def import_zip(path: Path) -> dict:
    """Bring a desktop Studio's Library across: the data folder zipped (SaracenStudio, or its contents). Takes the run
    folders (runs/<tool>/<id>/...) and nothing else: settings, saved keys (locked to the old computer), the AI model and
    the Room stay behind. A run already here is kept as it is."""
    root = (store.home() / "runs").resolve()
    new, skipped, refused = set(), set(), 0
    try:
        z = zipfile.ZipFile(path)
    except zipfile.BadZipFile as e:
        raise WebError(400, "That isn't a zip file. Zip the SaracenStudio folder and upload the .zip.") from e
    with z:
        infos = [i for i in z.infolist() if not i.is_dir()]
        if sum(i.file_size for i in infos) > MAX_IMPORT_BYTES:
            raise WebError(413, f"That zip unpacks to more than {MAX_IMPORT_BYTES // 1024 ** 3} GB.")
        before = {(p.parent.parent.name, p.parent.name) for p in root.glob("*/*/run.json")} if root.exists() else set()
        for info in infos:
            name = info.filename.replace("\\", "/")
            parts = [p for p in name.split("/") if p not in ("", ".")]
            is_link = (info.external_attr >> 16) & 0o170000 == 0o120000
            if name.startswith("/") or ".." in parts or (parts and ":" in parts[0]) or is_link:
                refused += 1                                          # would land outside the Library: never written
                continue
            if "runs" not in parts:
                continue                                              # settings, keys, model, Room: stay behind
            rel = parts[parts.index("runs") + 1:]
            if len(rel) < 3:
                continue
            tool, rid = rel[0], rel[1]
            if (tool, rid) in before:
                skipped.add((tool, rid))
                continue
            dest = (root.joinpath(*rel)).resolve()
            if root not in dest.parents:
                refused += 1
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            with z.open(info) as src, open(dest, "wb") as out:
                shutil.copyfileobj(src, out, 1 << 20)
            new.add((tool, rid))
    indexed = 0
    for tool, rid in sorted(new):
        f = root / tool / rid / "run.json"
        if f.exists():
            try:
                store.index_run(json.loads(f.read_text(encoding="utf-8")))
                indexed += 1
            except (ValueError, KeyError, OSError):
                pass
    return {"imported": indexed, "already_here": len(skipped), "refused": refused}


# ---------------------------------------------------------------- the server's own command line
def main(argv: list[str] | None = None) -> int:
    """python -m studio.web add-user EMAIL "Name" [--admin]   |   reset EMAIL   |   list"""
    import sys
    a = list(sys.argv[1:] if argv is None else argv)
    try:
        if a[:1] == ["add-user"] and len(a) >= 3:
            pw = add_user(a[1], a[2], "admin" if "--admin" in a else "member")
            print(f"Login for {_norm(a[1])} ({'admin' if '--admin' in a else 'member'}). Password, shown once: {pw}")
        elif a[:1] == ["reset"] and len(a) == 2:
            print(f"New password for {_norm(a[1])}, shown once: {set_password(a[1])}")
        elif a[:1] == ["list"]:
            for e, u in users().items():
                print(f"{e}\t{u.get('role')}\t{u.get('name')}")
        else:
            print(main.__doc__)
            return 2
    except WebError as e:
        print(e)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
