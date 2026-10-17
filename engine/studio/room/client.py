"""The Room client inside the Studio (1.0.8): this device's keys, encryption, sync with the hub, and a local cache.

The private keys live in STUDIO_HOME, sealed with Windows DPAPI for the signed-in user (studio.keys). The cache holds
the hub's ciphertext as received plus the key wraps sealed to this device, so it is encrypted at rest; plaintext
exists only in memory. The Studio server stays on 127.0.0.1: only this client's calls to the hub cross the network.
"""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import threading
import time
from pathlib import Path

import httpx

import room_crypto as rc

DEFAULT_SPACES = (  # name, audience
    ("Production office", {"tiers": ["producer"]}),
    ("Heads of department", {"tiers": ["producer", "key"]}),
    ("Cast", {"tiers": ["cast"], "second_ad": True}),
)


class RoomError(Exception):
    pass


def _seal(b: bytes) -> str:
    from studio import keys
    return keys._seal(b)


def _open(s: str) -> bytes:
    from studio import keys
    return keys._open(s)


class RoomClient:
    def __init__(self, folder: Path | str, hub: str | None = None, http: httpx.Client | None = None):
        self.dir = Path(folder)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        self.state = self._load_state()
        if hub:
            self.state["hub"] = hub.rstrip("/")
        self._http = http
        self.device = rc.Device.from_secret(json.loads(_open(self.state["device"]))) if self.state.get("device") else None
        self.db = sqlite3.connect(self.dir / "cache.sqlite3", check_same_thread=False, isolation_level=None)
        self.db.executescript("CREATE TABLE IF NOT EXISTS items (id TEXT PRIMARY KEY, seq INTEGER, body TEXT);"
                              "CREATE TABLE IF NOT EXISTS wraps (k TEXT PRIMARY KEY, body TEXT);"
                              "CREATE TABLE IF NOT EXISTS kv (k TEXT PRIMARY KEY, v TEXT);")
        self._token: tuple[str, float] | None = None
        self.snapshot: dict = {}
        self.keys: dict[tuple[str, int], bytes] = {}
        self.items: dict[str, dict] = {}
        self.trust_ever: dict = {}
        self.trust_now: dict = {}
        self.problems: list[str] = []
        if self.state.get("status") == "approved":
            self._load_cache()

    # ------------------------------------------------------------------ local state
    def _load_state(self) -> dict:
        try:
            return json.loads((self.dir / "state.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}

    def _save_state(self):
        p = self.dir / "state.json"
        tmp = p.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.state), encoding="utf-8")
        os.replace(tmp, p)
        if os.name != "nt":
            os.chmod(p, 0o600)

    def _new_device(self):
        self.device = rc.Device()
        self.state["device"] = _seal(json.dumps(self.device.secret()).encode())

    @property
    def http(self) -> httpx.Client:
        if self._http is None:
            if not self.state.get("hub"):
                raise RoomError("Set the Room's address in Settings first.")
            self._http = httpx.Client(base_url=self.state["hub"], timeout=30, trust_env=False)
        return self._http

    def _req(self, method: str, path: str, *, auth=True, **kw):
        headers = kw.pop("headers", {})
        if auth:
            headers["Authorization"] = "Bearer " + self._bearer()
        try:
            r = self.http.request(method, path, headers=headers, **kw)
        except httpx.HTTPError as e:
            raise RoomError(f"The Room isn't reachable ({type(e).__name__}). Check the connection and try again.") from e
        if r.status_code == 401 and auth:
            self._token = None
            headers["Authorization"] = "Bearer " + self._bearer()
            r = self.http.request(method, path, headers=headers, **kw)
        if r.status_code >= 400:
            try:
                msg = r.json().get("detail")
            except ValueError:
                msg = r.text[:200]
            raise RoomError(msg or f"The Room said {r.status_code}.")
        return r.json() if r.headers.get("content-type", "").startswith("application/json") else r.content

    def _bearer(self) -> str:
        if self._token and self._token[1] > time.time() + 60:
            return self._token[0]
        if not self.device:
            raise RoomError("This device hasn't joined the Room yet.")
        ch = self._req("POST", "/api/auth/challenge", auth=False, json={"device": self.device.id})["challenge"]
        sig = self.device.sign(rc.canon({"t": "auth", "device": self.device.id, "challenge": ch}))
        t = self._req("POST", "/api/auth/token", auth=False, json={"device": self.device.id, "challenge": ch, "sig": sig})
        self._token = (t["token"], time.time() + t["expires_in"])
        if t["status"] != self.state.get("status"):
            self.state["status"] = t["status"]
            self._save_state()
        return t["token"]

    # ------------------------------------------------------------------ founding and joining
    def bootstrap(self, founder_token: str, name: str, role: str = "Executive"):
        """The first executive's first device."""
        self._new_device()
        user = rc.new_id("u_")
        rec = rc.device_record(self.device.public(), user, self.device)
        self._req("POST", "/api/bootstrap", auth=False, json={"token": founder_token, "record": rec})
        self.state.update(user=user, status="approved", founder=rec, profile={"name": name, "role": role})
        self._save_state()
        self.sync()

    def join(self, invite_token: str, name: str = ""):
        """Step 1 on a new device: keys, a commitment, and the invite."""
        self._new_device()
        nonce = os.urandom(32)
        commit = rc.commitment(self.device.public(), nonce)
        r = self._req("POST", "/api/join", auth=False,
                      json={"token": invite_token, "device": self.device.public(), "commit": commit})
        self.state.update(user=r["user"], status="pending", join_nonce=rc.b64e(nonce), join_founder=r["founder"],
                          profile={"name": name, "role": ""})
        self._save_state()
        return r

    def join_progress(self) -> dict:
        """Where the joining device is: waiting for an executive, showing its safety words, or approved."""
        s = self._req("GET", "/api/join/state")
        if s["status"] == "approved":
            return self._finish_join(s)
        if s["status"] != "pending":
            return {"stage": "declined"}
        if not s["approver"]:
            return {"stage": "waiting"}
        if not s["revealed"]:
            self._req("POST", "/api/join/reveal", json={"nonce": self.state["join_nonce"]})
        founder = self.state["join_founder"]
        words = rc.safety_words(self.device.public(), s["approver"], founder["r"]["ed"],
                                rc.b64d(self.state["join_nonce"]), rc.b64d(s["n_approver"]))
        self.state["join_approver"] = s["approver"]
        self._save_state()
        return {"stage": "words", "words": words}

    def _finish_join(self, s: dict) -> dict:
        # the founder and approver we compared words against become this device's roots of trust
        if s["founder"] != self.state.get("join_founder"):
            raise RoomError("The Room's root key changed during joining. Don't use this device; ask for a new invite.")
        appr = self.state.get("join_approver")
        rec = s["record"]
        if not appr or rec["r"]["by"] != appr["id"] or not rc.verify(appr["ed"], rc.canon(rec["r"]), rec["sig"]):
            raise RoomError("The approval wasn't signed by the executive you checked words with.")
        self.state.update(status="approved", founder=s["founder"], approver_pin=appr)
        for k in ("join_nonce", "join_founder", "join_approver"):
            self.state.pop(k, None)
        self._save_state()
        self.sync()
        return {"stage": "approved"}

    # executive side of joining
    def pending(self) -> list[dict]:
        out = []
        for p in self._req("GET", "/api/pending"):
            p["words"] = None
            if p["approver"] == self.device.id and p["n_joiner"]:
                n_a = self.state.get("checks", {}).get(p["device"]["id"])
                if n_a and rc.check_commitment(p["device"], rc.b64d(p["n_joiner"]), p["commit"]):
                    p["words"] = rc.safety_words(p["device"], self.device.public(), self.state["founder"]["r"]["ed"],
                                                 rc.b64d(p["n_joiner"]), rc.b64d(n_a))
                else:
                    p["problem"] = "This device's keys don't match what it promised. Decline it."
            if p.get("invite") and p["invite"].get("details"):
                p["details"] = self._open_dir_item(p["invite"]["details"], p["invite"]["production"])
            out.append(p)
        return out

    def start_check(self, device_id: str):
        n = os.urandom(32)
        self.state.setdefault("checks", {})[device_id] = rc.b64e(n)
        self._save_state()
        self._req("POST", f"/api/pending/{device_id}/start", json={"nonce": rc.b64e(n)})

    def approve(self, device_id: str, name: str = "", role: str = ""):
        """After the words matched: sign the device in and put the person's name in the production's directory."""
        p = next((x for x in self.pending() if x["device"]["id"] == device_id), None)
        if not p or not p["words"]:
            raise RoomError("Compare the safety words first.")
        rec = rc.device_record(p["device"], p["user"], self.device)
        self._req("POST", f"/api/pending/{device_id}/approve", json={"record": rec})
        self.state.get("checks", {}).pop(device_id, None)
        self._save_state()
        self.sync()
        inv = p.get("invite") or {}
        details = p.get("details") or {}
        person = {"name": name or details.get("name") or "", "role": role or details.get("role") or ""}
        if inv.get("production") and person["name"]:
            self.set_person(inv["production"], p["user"], person)
        self.sync()

    def decline(self, device_id: str):
        self._req("POST", f"/api/pending/{device_id}/decline")
        self.state.get("checks", {}).pop(device_id, None)
        self._save_state()

    # ------------------------------------------------------------------ sync and verification
    def _load_cache(self):
        with self.lock:
            self.snapshot = self._kv("snapshot", {})
            self._compute_trust()
            for (body,) in self.db.execute("SELECT body FROM wraps"):
                self._take_wrap(json.loads(body), save=False)
            for (body,) in self.db.execute("SELECT body FROM items ORDER BY seq"):
                self._take_item(json.loads(body), save=False)

    def _compute_trust(self):
        snap = self.snapshot
        if not snap or not self.state.get("founder"):
            return
        if snap.get("founder") and snap["founder"] != self.state["founder"]:
            raise RoomError("The hub's root key doesn't match the one this device trusts. Stop and tell an executive.")
        recs = [d["record"] for d in snap.get("devices", [])]
        self.trust_ever = rc.trusted_devices(self.state["founder"], recs, snap.get("exec_grants", []), [])
        self.trust_now = rc.trusted_devices(self.state["founder"], recs, snap.get("exec_grants", []), snap.get("revocations", []))

    def sync(self, upkeep: bool = True) -> dict:
        with self.lock:
            since = int(self.state.get("seq", 0)) if self.snapshot else 0
            s = self._req("GET", "/api/sync", params={"since": since})
            files = self._kv("files", {}) if since else {}
            notes = self._kv("notes", []) if since else []
            for f in s["files"]:
                files[f["id"]] = f
            notes = (notes + s["notifications"])[-500:]
            self.snapshot = {k: v for k, v in s.items() if k not in ("items", "wraps", "files", "deleted", "notifications")}
            self.snapshot["files"], self.snapshot["notifications"] = files, notes
            self._kv("files", files, save=True)
            self._kv("notes", notes, save=True)
            self._compute_trust()
            for w in s["wraps"]:
                self._take_wrap(w)
            for it in s["items"]:
                self._take_item(it)
            if s["wraps"]:                           # keys that arrived late open items that came earlier
                for rec in list(self.items.values()):
                    if rec["payload"] is None:
                        self._take_item(rec["raw"], save=False)
            for iid in s["deleted"]:
                self.items.pop(iid, None)
                self.db.execute("DELETE FROM items WHERE id=?", (iid,))
            visible = {sp["id"] for sp in s["spaces"]}      # forget spaces this user can no longer see
            for iid, it in list(self.items.items()):
                if not {sp for sp, _ in it["h"]["spaces"]} & visible:
                    self.items.pop(iid)
                    self.db.execute("DELETE FROM items WHERE id=?", (iid,))
            self._kv("snapshot", self.snapshot, save=True)
            self.state["seq"] = s["seq"]
            self._save_state()
        if upkeep:
            self.upkeep()
        return self.snapshot

    def _kv(self, k: str, default=None, save=False):
        if save:
            self.db.execute("INSERT OR REPLACE INTO kv (k, v) VALUES (?, ?)", (k, json.dumps(default)))
            return default
        r = self.db.execute("SELECT v FROM kv WHERE k=?", (k,)).fetchone()
        return json.loads(r[0]) if r else default

    def _take_wrap(self, w: dict, save=True):
        by = self.trust_ever.get("devices", {}).get(w["by"])
        if not by or not rc.verify(by["ed"], rc.wrap_signed_bytes(w), w["sig"]):
            self.problems.append(f"Ignored a key from a device this one doesn't trust ({w['by']}).")
            return
        try:
            self.keys[(w["space"], w["epoch"])] = rc.unwrap_key(w, self.device)
        except Exception:  # noqa: BLE001
            self.problems.append("A key couldn't be opened on this device.")
            return
        if save:
            self.db.execute("INSERT OR REPLACE INTO wraps (k, body) VALUES (?, ?)",
                            (f"{w['space']}|{w['epoch']}", json.dumps(w)))

    def _take_item(self, it: dict, save=True):
        by = self.trust_ever.get("devices", {}).get(it["h"].get("by"))
        if not by or not rc.verify_item(it, by["ed"]):
            self.problems.append(f"Ignored an item that isn't signed by a trusted device ({it['h'].get('id')}).")
            return
        payload = None
        for s, e in it["h"]["spaces"]:
            k = self.keys.get((s, e))
            if k:
                try:
                    payload = rc.open_item(it, s, k)
                    break
                except Exception:  # noqa: BLE001
                    continue
        rec = {"h": it["h"], "seq": it.get("seq", 0), "payload": payload, "author": by["user"], "raw": it}
        self.items[it["h"]["id"]] = rec
        if save:
            self.db.execute("INSERT OR REPLACE INTO items (id, seq, body) VALUES (?, ?, ?)",
                            (it["h"]["id"], it.get("seq", 0), json.dumps(it)))

    def open_space(self, space: str) -> list[dict]:
        """Fetch a space's items directly (an executive reading a space they aren't in; the hub logs it)."""
        r = self._req("GET", f"/api/spaces/{space}/items")
        for it in r["items"]:
            self._take_item(it, save=False)
        return [self.items[it["h"]["id"]] for it in r["items"] if it["h"]["id"] in self.items]

    # ------------------------------------------------------------------ upkeep: keys for others, rotation, personal spaces
    def upkeep(self, rounds: int = 3):
        for _ in range(rounds):
            t = self.snapshot.get("tasks") or {}
            did = False
            if t.get("rotate"):
                for r in t["rotate"]:
                    try:
                        self.rotate(r["space"])
                        did = True
                    except RoomError as e:
                        self.problems.append(str(e))
            wraps = []
            trusted = self.trust_now.get("devices", {})
            for task in t.get("wrap", []):
                rec = trusted.get(task["device"])
                key = self.keys.get((task["space"], task["epoch"]))
                if not rec or rec["user"] != task["user"] or key is None:
                    continue                      # never wrap a key for a device this one doesn't trust
                wraps.append(rc.wrap_key(key, task["space"], task["epoch"], {"id": rec["id"], "x": rec["x"]}, self.device))
            for i in range(0, len(wraps), 200):
                self._req("POST", "/api/wraps", json={"wraps": wraps[i:i + 200]})
                did = True
            for task in t.get("personal", []):
                try:
                    self.create_space(task["production"], "", kind="personal", owner=task["user"])
                    did = True
                except RoomError as e:
                    self.problems.append(str(e))
            for task in t.get("person", []):
                prof = self.state.get("profile") or {}
                if prof.get("name"):
                    self.set_person(task["production"], self.state["user"], prof)
                    did = True
            if not did:
                return
            self.sync(upkeep=False)

    def rotate(self, space: str):
        sp = self.space(space)
        key = rc.new_key()
        e = sp["epoch"] + 1
        w = rc.wrap_key(key, space, e, self.device.public(), self.device)
        self._req("POST", f"/api/spaces/{space}/rotate", json={"epoch": e, "wraps": [w]})
        self.keys[(space, e)] = key
        self.db.execute("INSERT OR REPLACE INTO wraps (k, body) VALUES (?, ?)", (f"{space}|{e}", json.dumps(w)))

    # ------------------------------------------------------------------ lookups
    @property
    def me(self) -> str:
        return self.state.get("user", "")

    @property
    def is_exec(self) -> bool:
        return bool(self.snapshot.get("me", {}).get("exec"))

    def space(self, sid: str) -> dict:
        for sp in self.snapshot.get("spaces", []):
            if sp["id"] == sid:
                return sp
        raise RoomError("That space isn't visible to you.")

    def directory_space(self, production: str) -> dict:
        for sp in self.snapshot.get("spaces", []):
            if sp["production"] == production and sp["kind"] == "directory":
                return sp
        raise RoomError("This production has no directory yet.")

    def names(self, production: str) -> dict:
        """kind -> subject -> payload, latest wins: the production, its spaces, departments and people."""
        out: dict = {"production": {}, "space": {}, "department": {}, "person": {}}
        for it in sorted(self.items.values(), key=lambda r: r["seq"]):
            h = it["h"]
            if h.get("prod") == production and h["kind"] in out and it["payload"] is not None:
                out[h["kind"]][h.get("subject")] = it["payload"]
        return out

    def current_key(self, sid: str) -> tuple[int, bytes]:
        sp = self.space(sid)
        k = self.keys.get((sid, sp["epoch"]))
        if k is None:
            raise RoomError("This device doesn't have the key for that space yet. Sync again in a moment.")
        return sp["epoch"], k

    def _open_dir_item(self, item: dict, production: str):
        try:
            d = self.directory_space(production)
        except RoomError:
            return None
        for (s, e), k in self.keys.items():
            if s == d["id"]:
                try:
                    return rc.open_item(item, s, k)
                except Exception:  # noqa: BLE001
                    continue
        return None

    # ------------------------------------------------------------------ productions, spaces, people
    def post(self, spaces: list[str], kind: str, payload, *, ref: str | None = None, subject: str | None = None,
             mentions: list[str] | None = None, production: str | None = None) -> dict:
        keys = {s: self.current_key(s) for s in spaces}
        prod = production or self.space(spaces[0])["production"]
        h = {"id": rc.new_id("m_"), "kind": kind, "prod": prod, "ts": rc.now()}
        if ref:
            h["ref"] = ref
        if subject:
            h["subject"] = subject
        it = rc.seal_item(h, payload, keys, self.device)
        r = self._req("POST", "/api/items", json={"item": it, "mentions": mentions or []})
        it["seq"] = r["seq"]
        self._take_item(it)
        return self.items[h["id"]]

    def create_production(self, name: str) -> str:
        pid = rc.new_id("p_")
        self._req("POST", "/api/productions", json={"id": pid})
        self.sync(upkeep=False)
        self.create_space(pid, "", kind="directory")
        self.post([self.directory_space(pid)["id"]], "production", {"name": name}, subject=pid, production=pid)
        prof = self.state.get("profile") or {}
        if prof.get("name"):
            self.set_person(pid, self.me, prof)
        for nm, aud in DEFAULT_SPACES:
            self.create_space(pid, nm, audience=aud, members=[self.me])
        self.sync()
        return pid

    def create_space(self, production: str, name: str, *, kind: str = "channel", audience: dict | None = None,
                     members: list[str] | None = None, owner: str | None = None) -> str:
        sid = rc.new_id("s_")
        key = rc.new_key()
        w = rc.wrap_key(key, sid, 1, self.device.public(), self.device)
        r = self._req("POST", "/api/spaces", json={"id": sid, "production": production, "kind": kind, "audience": audience or {},
                                                   "members": members or [], "owner": owner, "wraps": [w]})
        if r.get("existing"):
            return r["id"]
        self.keys[(sid, 1)] = key
        self.db.execute("INSERT OR REPLACE INTO wraps (k, body) VALUES (?, ?)", (f"{sid}|1", json.dumps(w)))
        self.sync(upkeep=False)
        if name and kind != "directory":
            self.post([self.directory_space(production)["id"]], "space", {"name": name}, subject=sid, production=production)
        return sid

    def add_department(self, production: str, name: str) -> str:
        dep = rc.new_id("dep_")
        self.post([self.directory_space(production)["id"]], "department", {"name": name}, subject=dep, production=production)
        self.create_space(production, name, audience={"tiers": ["key", "crew"], "departments": [dep]})
        return dep

    def set_person(self, production: str, user: str, person: dict):
        self.post([self.directory_space(production)["id"]], "person", person, subject=user, production=production)

    def invite(self, production: str | None, tier: str | None, name: str, role: str = "", department: str = "",
               second_ad: bool = False, user: str | None = None, company: bool = False) -> dict:
        details = None
        if production and not user:
            d = self.directory_space(production)
            epoch, key = self.current_key(d["id"])
            details = rc.seal_item({"id": rc.new_id("m_"), "kind": "person", "prod": production, "ts": rc.now()},
                                   {"name": name, "role": role}, {d["id"]: (epoch, key)}, self.device)
        return self._req("POST", "/api/invites", json={"production": production, "tier": tier, "department": department,
                                                       "second_ad": second_ad, "details": details, "user": user,
                                                       "company": company})

    def dm(self, production: str, other: str) -> str:
        return self.create_space(production, "", kind="dm", members=[self.me, other])

    def set_member(self, production: str, user: str, tier: str, department: str = "", second_ad: bool = False):
        self._req("POST", "/api/members/set", json={"production": production, "user": user, "tier": tier,
                                                    "department": department, "second_ad": second_ad})
        self.sync()

    def remove_member(self, production: str, user: str):
        self._req("POST", "/api/members/remove", json={"production": production, "user": user})
        self.sync()

    def revoke_device(self, device_id: str):
        self._req("POST", f"/api/devices/{device_id}/revoke", json={"revocation": rc.revocation(device_id, self.device)})
        self.sync()

    def make_exec(self, user: str, on: bool = True):
        self._req("POST", "/api/execs", json={"grant": rc.exec_grant(user, on, self.device)})
        self.sync()

    def grant_contact(self, production: str, a: str, b: str) -> str:
        return self._req("POST", "/api/grants", json={"production": production, "a": a, "b": b})["id"]

    def audit(self) -> dict:
        return self._req("GET", "/api/audit")

    # ------------------------------------------------------------------ files
    def upload(self, space: str, name: str, data: bytes | Path, *, lineage: str | None = None, progress=None,
               note: str = "") -> dict:
        """Encrypt and send a file in parts. A file with the same name in the space becomes its next version.
        Interrupted uploads resume: call again with resume=<file id> (see resume_upload)."""
        raw = Path(data).read_bytes() if isinstance(data, Path) else data
        if lineage is None:
            for f in self.files(space):
                if f["name"] == name:
                    lineage = f["lineage"]
                    break
        n = max(1, -(-len(raw) // rc.CHUNK))
        f = self._req("POST", "/api/files", json={"space": space, "lineage": lineage, "chunks": n, "size": len(raw)})
        fkey = rc.new_key()
        pending = {"id": f["id"], "space": space, "name": name, "key": rc.b64e(fkey), "lineage": f["lineage"],
                   "version": f["version"], "size": len(raw), "chunks": n, "note": note}
        self.state.setdefault("uploads", {})[f["id"]] = dict(pending, key=_seal(fkey))
        self._save_state()
        return self._send_parts(pending, raw, progress)

    def resume_upload(self, file_id: str, data: bytes | Path, progress=None) -> dict:
        up = dict(self.state.get("uploads", {}).get(file_id) or {})
        if not up:
            raise RoomError("Nothing to resume.")
        up["key"] = rc.b64e(_open(up["key"]))
        raw = Path(data).read_bytes() if isinstance(data, Path) else data
        return self._send_parts(up, raw, progress)

    def _send_parts(self, up: dict, raw: bytes, progress) -> dict:
        fid, n, fkey = up["id"], up["chunks"], rc.b64d(up["key"])
        have = set(self._req("GET", f"/api/files/{fid}")["present"])
        for i in range(n):
            if i in have:
                continue
            blob = rc.encrypt_chunk(fkey, raw[i * rc.CHUNK:(i + 1) * rc.CHUNK], fid, i, n)
            self._req("PUT", f"/api/files/{fid}/chunks/{i}", content=blob,
                      headers={"Content-Type": "application/octet-stream"})
            if progress:
                progress(i + 1, n)
        manifest = {"name": up["name"], "size": up["size"], "file_key": up["key"], "chunks": n, "version": up["version"],
                    "lineage": up["lineage"], "sha256": hashlib.sha256(raw).hexdigest(), "note": up.get("note", "")}
        item = self.post([up["space"]], "file", manifest, ref=fid)
        self.state.get("uploads", {}).pop(fid, None)
        self._save_state()
        return item

    def files(self, space: str | None = None) -> list[dict]:
        out = []
        for it in self.items.values():
            if it["h"]["kind"] == "file" and it["payload"] and (space is None or space in {s for s, _ in it["h"]["spaces"]}):
                out.append(dict(it["payload"], id=it["h"]["ref"], item=it["h"]["id"], author=it["author"], ts=it["h"]["ts"],
                                spaces=[s for s, _ in it["h"]["spaces"]]))
        return sorted(out, key=lambda f: (f["lineage"], f["version"]))

    def download(self, file_id: str) -> bytes:
        f = next((x for x in self.files() if x["id"] == file_id), None)
        if not f:
            raise RoomError("That file isn't visible to you.")
        key, n = rc.b64d(f["file_key"]), f["chunks"]
        parts = [rc.decrypt_chunk(key, self._req("GET", f"/api/files/{file_id}/chunks/{i}"), file_id, i, n) for i in range(n)]
        data = b"".join(parts)
        if hashlib.sha256(data).hexdigest() != f["sha256"]:
            raise RoomError("The file didn't arrive intact.")
        return data
