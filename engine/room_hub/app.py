"""The Room hub (1.0.8): a separate, always-on service that routes and stores the Room's encrypted traffic.

It never sees plaintext content: devices encrypt before sending. It does enforce who may see and do what (access.py),
verifies every signature, keeps the append-only audit log, issues meeting tokens and sends content-free pushes.
Run: python -m room_hub serve --data <folder> [--host 0.0.0.0 --port 8710]
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import os
import time
from pathlib import Path

from fastapi import Body, Depends, FastAPI, Header, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles

import room_crypto as rc

from .access import TIERS, View
from .db import Store

VERSION = "1.0.8"
TOKEN_HOURS = 12
INVITE_DAYS = 14
MAX_CHUNK = rc.CHUNK + 1024
POST_KINDS = {"msg", "note", "note_update", "file", "callsheet", "callsheet_row", "reaction"}
DIR_KINDS = {"person", "space", "department", "production"}


def _h(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def create_app(data: Path | str, *, livekit: dict | None = None, push=None) -> FastAPI:
    store = Store(Path(data))
    app = FastAPI(title="Saracen Bridge Room hub", version=VERSION, docs_url=None, redoc_url=None)
    app.state.store = store
    app.state.livekit = livekit or {}
    app.state.push = push
    @app.exception_handler(ValueError)
    async def _bad_input(request, exc):           # e.g. a signed header that isn't ASCII
        return JSONResponse({"detail": "The request wasn't in the expected format."}, status_code=400)

    @app.middleware("http")
    async def _limit(request: Request, call_next):
        n = int(request.headers.get("content-length") or 0)
        if n > (MAX_CHUNK if "/chunks/" in request.url.path else 4 * 1024 * 1024):
            return JSONResponse({"detail": "That's too large to send in one request."}, status_code=413)
        return await call_next(request)

    marks: dict[str, int] = {}                 # user -> last seq that concerned them (for the live channel)

    def _bump(seq, users):
        if users is None:
            marks["*"] = seq
        else:
            for u in users:
                marks[u] = seq
    store.listeners.append(_bump)

    # ------------------------------------------------------------------ auth
    class Ctx:
        def __init__(self, device: dict):
            self.device = device
            self.user = device["user"]
            self.status = device["status"]

        def view(self) -> View:
            return View(store, self.user)

    def _device_from_token(token: str | None) -> dict:
        if not token:
            raise HTTPException(401, "Sign in first.")
        r = store.one("SELECT t.device, t.expires FROM tokens t WHERE t.hash=?", (_h(token),))
        if not r or r["expires"] < time.time():
            raise HTTPException(401, "Your session has ended. Sign in again.")
        d = store.one("SELECT * FROM devices WHERE id=?", (r["device"],))
        if not d or d["status"] in ("revoked", "declined"):
            raise HTTPException(403, "This device has been removed from the Room.")
        u = store.one("SELECT deleted FROM users WHERE id=?", (d["user"],))
        if not u or u["deleted"]:
            raise HTTPException(403, "This account has been removed from the Room.")
        return dict(d)

    def any_device(authorization: str | None = Header(None)) -> Ctx:
        return Ctx(_device_from_token((authorization or "").removeprefix("Bearer ").strip() or None))

    def approved(ctx: Ctx = Depends(any_device)) -> Ctx:
        if ctx.status != "approved":
            raise HTTPException(403, "This device is waiting for an executive to approve it.")
        return ctx

    def executive(ctx: Ctx = Depends(approved)) -> Ctx:
        if not ctx.view().exec:
            raise HTTPException(403, "Only an executive can do that.")
        return ctx

    def _verify_signed(rec: dict, by_device: dict) -> None:
        if rec["r"].get("by") != by_device["id"] or not rc.verify(by_device["ed"], rc.canon(rec["r"]), rec["sig"]):
            raise HTTPException(400, "The signature doesn't check out.")

    # ------------------------------------------------------------------ health, bootstrap, sign-in
    @app.get("/api/health")
    def health():
        return {"ok": True, "version": VERSION, "founded": bool(store.one("SELECT 1 FROM users WHERE founder=1"))}

    @app.post("/api/bootstrap")
    def bootstrap(body: dict = Body(...)):
        """The first executive's first device. The founder token is printed once by `room_hub init`."""
        th = store.meta("founder_token")
        if not th or _h(body.get("token", "")) != th or store.one("SELECT 1 FROM users WHERE founder=1"):
            raise HTTPException(403, "That founder link isn't valid.")
        rec = body["record"]
        r = rec["r"]
        if r["by"] != r["id"] or not rc.verify(r["ed"], rc.canon(r), rec["sig"]):
            raise HTTPException(400, "The founder record must be signed by its own device.")
        with store.tx() as seq:
            store.x("INSERT INTO users (id, exec, founder, seq) VALUES (?,1,1,?)", (r["user"], seq))
            store.x("INSERT INTO devices (id, user, x, ed, status, record, created, seq) VALUES (?,?,?,?,?,?,?,?)",
                    (r["id"], r["user"], r["x"], r["ed"], "approved", json.dumps(rec), int(time.time()), seq))
            store.meta("founder_token", "")
            store.meta("founder_device", r["id"])
            store.audit(seq, r["user"], r["id"], "founded the Room", None, {"device": r["id"]})
        return {"ok": True}

    @app.post("/api/auth/challenge")
    def challenge(body: dict = Body(...)):
        d = store.one("SELECT id, status FROM devices WHERE id=?", (body.get("device", ""),))
        if not d or d["status"] in ("revoked", "declined"):
            raise HTTPException(404, "Unknown device.")
        ch = rc.b64e(os.urandom(24))
        with store.lock:
            store.x("INSERT OR REPLACE INTO challenges (device, challenge, expires) VALUES (?,?,?)",
                    (d["id"], ch, int(time.time()) + 120))
        return {"challenge": ch}

    @app.post("/api/auth/token")
    def token(body: dict = Body(...)):
        did = body.get("device", "")
        c = store.one("SELECT * FROM challenges WHERE device=?", (did,))
        d = store.one("SELECT * FROM devices WHERE id=?", (did,))
        if not c or not d or c["expires"] < time.time() or c["challenge"] != body.get("challenge"):
            raise HTTPException(401, "Sign-in expired. Try again.")
        if not rc.verify(d["ed"], rc.canon({"t": "auth", "device": did, "challenge": c["challenge"]}), body.get("sig", "")):
            raise HTTPException(401, "Sign-in signature didn't check out.")
        tok = rc.b64e(os.urandom(32))
        with store.lock:
            store.x("DELETE FROM challenges WHERE device=?", (did,))
            store.x("DELETE FROM tokens WHERE expires < ?", (int(time.time()),))
            store.x("INSERT INTO tokens (hash, device, expires) VALUES (?,?,?)",
                    (_h(tok), did, int(time.time()) + TOKEN_HOURS * 3600))
        return {"token": tok, "status": d["status"], "user": d["user"], "expires_in": TOKEN_HOURS * 3600}

    # ------------------------------------------------------------------ joining with safety words
    def _founder_record():
        fid = store.meta("founder_device")
        r = store.one("SELECT record FROM devices WHERE id=?", (fid,)) if fid else None
        return json.loads(r["record"]) if r else None

    @app.post("/api/join")
    def join(body: dict = Body(...)):
        inv = store.one("SELECT * FROM invites WHERE token_hash=?", (_h(body.get("token", "")),))
        if not inv or inv["status"] != "open" or inv["expires"] < time.time():
            raise HTTPException(403, "This invite has been used, cancelled or has expired. Ask for a new one.")
        dev, commit = body["device"], body.get("commit", "")
        if not (dev.get("id") and dev.get("x") and dev.get("ed") and commit):
            raise HTTPException(400, "The app didn't send its keys.")
        if store.one("SELECT 1 FROM devices WHERE id=?", (dev["id"],)):
            raise HTTPException(409, "That device is already registered.")
        user = inv["user"] or rc.new_id("u_")
        with store.tx(users=set()) as seq:
            if not inv["user"]:
                store.x("INSERT INTO users (id, seq) VALUES (?,?)", (user, seq))
            store.x("INSERT INTO devices (id, user, x, ed, status, invite, commit_, created, seq) VALUES (?,?,?,?,?,?,?,?,?)",
                    (dev["id"], user, dev["x"], dev["ed"], "pending", inv["id"], commit, int(time.time()), seq))
            store.x("UPDATE invites SET status='joining', user=?, seq=? WHERE id=?", (user, seq, inv["id"]))
        return {"user": user, "founder": _founder_record(), "production": inv["production"]}

    @app.get("/api/join/state")
    def join_state(ctx: Ctx = Depends(any_device)):
        d = store.one("SELECT * FROM devices WHERE id=?", (ctx.device["id"],))
        out = {"status": d["status"], "founder": _founder_record(), "n_approver": d["n_approver"], "approver": None,
               "record": json.loads(d["record"]) if d["record"] else None, "revealed": bool(d["n_joiner"])}
        if d["approver"]:
            a = store.one("SELECT id, x, ed, record FROM devices WHERE id=?", (d["approver"],))
            out["approver"] = {"id": a["id"], "x": a["x"], "ed": a["ed"], "record": json.loads(a["record"])}
        return out

    @app.post("/api/join/reveal")
    def join_reveal(body: dict = Body(...), ctx: Ctx = Depends(any_device)):
        d = store.one("SELECT * FROM devices WHERE id=?", (ctx.device["id"],))
        if d["status"] != "pending" or not d["n_approver"]:
            raise HTTPException(409, "Wait for the executive to start the check.")
        if d["n_joiner"]:
            raise HTTPException(409, "Already revealed.")
        with store.tx(users=set()) as seq:
            store.x("UPDATE devices SET n_joiner=?, seq=? WHERE id=?", (body["nonce"], seq, d["id"]))
        return {"ok": True}

    @app.get("/api/pending")
    def pending(ctx: Ctx = Depends(executive)):
        out = []
        for d in store.q("SELECT * FROM devices WHERE status='pending' ORDER BY created"):
            inv = store.one("SELECT * FROM invites WHERE id=?", (d["invite"],)) if d["invite"] else None
            out.append({"device": {"id": d["id"], "x": d["x"], "ed": d["ed"]}, "user": d["user"], "commit": d["commit_"],
                        "approver": d["approver"], "n_approver": d["n_approver"], "n_joiner": d["n_joiner"],
                        "created": d["created"],
                        "invite": inv and {"id": inv["id"], "production": inv["production"], "tier": inv["tier"],
                                           "department": inv["department"], "second_ad": bool(inv["second_ad"]),
                                           "details": json.loads(inv["details"]) if inv["details"] else None,
                                           "created_by": inv["created_by"]}})
        return out

    def _pending(device_id: str):
        d = store.one("SELECT * FROM devices WHERE id=? AND status='pending'", (device_id,))
        if not d:
            raise HTTPException(404, "No device waiting with that id.")
        return d

    @app.post("/api/pending/{device_id}/start")
    def pending_start(device_id: str, body: dict = Body(...), ctx: Ctx = Depends(executive)):
        d = _pending(device_id)
        if d["approver"]:
            raise HTTPException(409, "Another check is already running for this device. Decline it and send a new invite.")
        with store.tx(users={d["user"]}) as seq:
            store.x("UPDATE devices SET approver=?, n_approver=?, seq=? WHERE id=?",
                    (ctx.device["id"], body["nonce"], seq, device_id))
        return {"ok": True}

    @app.post("/api/pending/{device_id}/approve")
    def pending_approve(device_id: str, body: dict = Body(...), ctx: Ctx = Depends(executive)):
        d = _pending(device_id)
        if d["approver"] != ctx.device["id"] or not d["n_joiner"]:
            raise HTTPException(409, "Compare the safety words first.")
        rec = body["record"]
        _verify_signed(rec, ctx.device)
        r = rec["r"]
        if (r["t"], r["id"], r["user"], r["x"], r["ed"]) != ("device", d["id"], d["user"], d["x"], d["ed"]):
            raise HTTPException(400, "The approval doesn't match the waiting device.")
        inv = store.one("SELECT * FROM invites WHERE id=?", (d["invite"],)) if d["invite"] else None
        with store.tx() as seq:
            store.x("UPDATE devices SET status='approved', record=?, seq=? WHERE id=?", (json.dumps(rec), seq, device_id))
            if inv:
                store.x("UPDATE invites SET status='used', seq=? WHERE id=?", (seq, inv["id"]))
                if inv["production"] and inv["tier"]:
                    store.x("INSERT OR REPLACE INTO memberships (user, production, tier, department, second_ad, seq) "
                            "VALUES (?,?,?,?,?,?)", (d["user"], inv["production"], inv["tier"], inv["department"],
                                                    inv["second_ad"], seq))
                    store.audit(seq, ctx.user, ctx.device["id"], "added a member", inv["production"],
                                {"user": d["user"], "tier": inv["tier"], "department": inv["department"]})
            store.audit(seq, ctx.user, ctx.device["id"], "approved a device", inv["production"] if inv else None,
                        {"device": device_id, "user": d["user"]})
        return {"ok": True}

    @app.post("/api/pending/{device_id}/decline")
    def pending_decline(device_id: str, ctx: Ctx = Depends(executive)):
        d = _pending(device_id)
        with store.tx(users={d["user"]}) as seq:
            store.x("UPDATE devices SET status='declined', seq=? WHERE id=?", (seq, device_id))
            if d["invite"]:
                store.x("UPDATE invites SET status='declined', seq=? WHERE id=?", (seq, d["invite"]))
            store.audit(seq, ctx.user, ctx.device["id"], "declined a device", None, {"device": device_id, "user": d["user"]})
        return {"ok": True}

    # ------------------------------------------------------------------ executives, devices, people
    @app.post("/api/execs")
    def set_exec(body: dict = Body(...), ctx: Ctx = Depends(executive)):
        g = body["grant"]
        _verify_signed(g, ctx.device)
        u = store.one("SELECT * FROM users WHERE id=? AND deleted=0", (g["r"]["user"],))
        if not u or u["founder"]:
            raise HTTPException(400, "Can't change that person's executive status.")
        with store.tx() as seq:
            store.x("UPDATE users SET exec=?, seq=? WHERE id=?", (1 if g["r"]["on"] else 0, seq, u["id"]))
            store.x("INSERT INTO exec_grants (rec, seq) VALUES (?,?)", (json.dumps(g), seq))
            if not g["r"]["on"]:
                _mark_rotation_for_user(u["id"], seq)
            store.audit(seq, ctx.user, ctx.device["id"], "made an executive" if g["r"]["on"] else "removed an executive",
                        None, {"user": u["id"]})
        return {"ok": True}

    def _mark_rotation_for_user(user: str, seq: int, production: str | None = None):
        """Every space whose keys this user's devices hold gets new keys (done by the next manager's device)."""
        devs = [r["id"] for r in store.q("SELECT id FROM devices WHERE user=?", (user,))]
        if not devs:
            return
        qs = ",".join("?" * len(devs))
        rows = store.q(f"SELECT DISTINCT w.space FROM wraps w JOIN spaces s ON s.id=w.space WHERE w.device IN ({qs})"
                       + (" AND s.production=?" if production else ""), devs + ([production] if production else []))
        for r in rows:
            store.x("UPDATE spaces SET rotate=1, seq=? WHERE id=?", (seq, r["space"]))

    @app.post("/api/devices/{device_id}/revoke")
    def revoke(device_id: str, body: dict = Body(...), ctx: Ctx = Depends(executive)):
        v = body["revocation"]
        _verify_signed(v, ctx.device)
        if v["r"]["device"] != device_id or device_id == store.meta("founder_device"):
            raise HTTPException(400, "Can't remove that device.")
        d = store.one("SELECT * FROM devices WHERE id=?", (device_id,))
        if not d:
            raise HTTPException(404, "Unknown device.")
        with store.tx() as seq:
            store.x("UPDATE devices SET status='revoked', seq=? WHERE id=?", (seq, device_id))
            store.x("INSERT INTO revocations (device, rec, seq) VALUES (?,?,?)", (device_id, json.dumps(v), seq))
            store.x("DELETE FROM tokens WHERE device=?", (device_id,))
            for r in store.q("SELECT DISTINCT space FROM wraps WHERE device=?", (device_id,)):
                store.x("UPDATE spaces SET rotate=1, seq=? WHERE id=?", (seq, r["space"]))
            store.audit(seq, ctx.user, ctx.device["id"], "removed a device", None, {"device": device_id, "user": d["user"]})
        return {"ok": True}

    @app.post("/api/productions")
    def create_production(body: dict = Body(...), ctx: Ctx = Depends(executive)):
        pid = body.get("id") or ""
        if not pid.startswith("p_") or store.one("SELECT 1 FROM productions WHERE id=?", (pid,)):
            raise HTTPException(400, "Bad or duplicate production id.")
        with store.tx() as seq:
            store.x("INSERT INTO productions (id, created_by, created, seq) VALUES (?,?,?,?)",
                    (pid, ctx.user, int(time.time()), seq))
            store.audit(seq, ctx.user, ctx.device["id"], "created a production", pid, {})
        return {"ok": True}

    @app.post("/api/productions/{pid}/archive")
    def archive_production(pid: str, body: dict = Body({}), ctx: Ctx = Depends(executive)):
        if not store.one("SELECT 1 FROM productions WHERE id=?", (pid,)):
            raise HTTPException(404, "Unknown production.")
        on = body.get("archived", True)
        with store.tx() as seq:
            store.x("UPDATE productions SET archived=?, seq=? WHERE id=?", (int(time.time()) if on else None, seq, pid))
            store.audit(seq, ctx.user, ctx.device["id"], "archived a production" if on else "restored a production", pid, {})
        return {"ok": True}

    @app.post("/api/invites")
    def create_invite(body: dict = Body(...), ctx: Ctx = Depends(approved)):
        """An invite to a production at a tier; or (executives) a person's extra device, or someone joining the
        company with no production yet (a new executive, say)."""
        v = ctx.view()
        p, tier = body.get("production"), body.get("tier")
        if body.get("user") or body.get("company"):
            if not v.exec:
                raise HTTPException(403, "Only an executive can do that.")
            p, tier = None, None
            if body.get("user") and not store.one("SELECT 1 FROM users WHERE id=? AND deleted=0", (body["user"],)):
                raise HTTPException(400, "Unknown person.")
        else:
            if p not in v.productions_visible() or tier not in TIERS:
                raise HTTPException(400, "Pick a production and a tier.")
            if not v.exec and not (v.tier(p) == "producer" and tier != "producer"):
                raise HTTPException(403, "Only executives and producers can invite, and producers invite keys, crew, cast and guests.")
        details = body.get("details")
        if details and not rc.verify_item(details, ctx.device["ed"]):
            raise HTTPException(400, "The invite details aren't signed by this device.")
        tok = rc.b64e(os.urandom(24))
        iid = rc.new_id("i_")
        with store.tx(users=v.execs) as seq:
            store.x("INSERT INTO invites (id, token_hash, production, tier, department, second_ad, user, details, "
                    "created_by, status, expires, seq) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                    (iid, _h(tok), p, tier, body.get("department") or "", 1 if body.get("second_ad") else 0,
                     body.get("user"), json.dumps(details) if details else None, ctx.user, "open",
                     int(time.time()) + INVITE_DAYS * 86400, seq))
            store.audit(seq, ctx.user, ctx.device["id"], "created an invite", p, {"invite": iid, "tier": tier,
                                                                                "user": body.get("user")})
        return {"id": iid, "token": tok, "expires_in_days": INVITE_DAYS}

    @app.post("/api/invites/{iid}/cancel")
    def cancel_invite(iid: str, ctx: Ctx = Depends(approved)):
        inv = store.one("SELECT * FROM invites WHERE id=?", (iid,))
        v = ctx.view()
        if not inv or not (v.exec or inv["created_by"] == ctx.user):
            raise HTTPException(404, "Unknown invite.")
        with store.tx(users=set()) as seq:
            store.x("UPDATE invites SET status='cancelled', seq=? WHERE id=?", (seq, iid))
            store.audit(seq, ctx.user, ctx.device["id"], "cancelled an invite", inv["production"], {"invite": iid})
        return {"ok": True}

    @app.get("/api/invites")
    def list_invites(ctx: Ctx = Depends(approved)):
        v = ctx.view()
        rows = store.q("SELECT * FROM invites WHERE status IN ('open','joining') ORDER BY seq DESC")
        return [{"id": r["id"], "production": r["production"], "tier": r["tier"], "department": r["department"],
                 "status": r["status"], "details": json.loads(r["details"]) if r["details"] else None,
                 "created_by": r["created_by"], "expires": r["expires"]}
                for r in rows if v.exec or (r["created_by"] == ctx.user and r["production"] in v.productions_visible())]

    @app.post("/api/members/set")
    def set_member(body: dict = Body(...), ctx: Ctx = Depends(executive)):
        p, user, tier = body["production"], body["user"], body["tier"]
        if tier not in TIERS or not store.one("SELECT 1 FROM productions WHERE id=?", (p,)):
            raise HTTPException(400, "Pick a production and a tier.")
        if not store.one("SELECT 1 FROM users WHERE id=? AND deleted=0", (user,)):
            raise HTTPException(404, "Unknown person.")
        old = store.one("SELECT * FROM memberships WHERE user=? AND production=?", (user, p))
        with store.tx() as seq:
            store.x("INSERT OR REPLACE INTO memberships (user, production, tier, department, second_ad, seq) VALUES (?,?,?,?,?,?)",
                    (user, p, tier, body.get("department") or "", 1 if body.get("second_ad") else 0, seq))
            if old and (old["tier"], old["department"], old["second_ad"]) != (tier, body.get("department") or "",
                                                                                1 if body.get("second_ad") else 0):
                _mark_rotation_for_user(user, seq, p)
            store.audit(seq, ctx.user, ctx.device["id"], "set a member's tier", p,
                        {"user": user, "tier": tier, "department": body.get("department") or "",
                         "second_ad": bool(body.get("second_ad"))})
        return {"ok": True}

    @app.post("/api/members/remove")
    def remove_member(body: dict = Body(...), ctx: Ctx = Depends(executive)):
        p, user = body["production"], body["user"]
        with store.tx() as seq:
            _mark_rotation_for_user(user, seq, p)
            store.x("DELETE FROM memberships WHERE user=? AND production=?", (user, p))
            store.x("DELETE FROM space_members WHERE user=? AND space IN (SELECT id FROM spaces WHERE production=?)", (user, p))
            store.audit(seq, ctx.user, ctx.device["id"], "removed a member", p, {"user": user})
        return {"ok": True}

    @app.post("/api/users/{user}/delete")
    def delete_person(user: str, ctx: Ctx = Depends(executive)):
        """A person's data deleted on request: their messages, files, memberships and devices."""
        u = store.one("SELECT * FROM users WHERE id=?", (user,))
        if not u or u["founder"]:
            raise HTTPException(400, "Can't delete that person.")
        with store.tx() as seq:
            _mark_rotation_for_user(user, seq)
            _delete_items(store.q("SELECT id FROM items WHERE author=? OR (subject=? AND kind='person')", (user, user)), seq)
            store.x("DELETE FROM memberships WHERE user=?", (user,))
            store.x("DELETE FROM space_members WHERE user=?", (user,))
            store.x("DELETE FROM confirmations WHERE user=?", (user,))
            store.x("DELETE FROM notifications WHERE user=?", (user,))
            store.x("DELETE FROM tokens WHERE device IN (SELECT id FROM devices WHERE user=?)", (user,))
            store.x("UPDATE devices SET status='revoked', seq=? WHERE user=?", (seq, user))
            store.x("UPDATE users SET deleted=1, exec=0, seq=? WHERE id=?", (seq, user))
            store.audit(seq, ctx.user, ctx.device["id"], "deleted a person's data", None, {"user": user})
        return {"ok": True}

    def _delete_items(rows, seq):
        for r in rows:
            iid = r["id"]
            for f in store.q("SELECT id, chunks FROM files WHERE item=? OR id IN (SELECT id FROM files WHERE item=?)", (iid, iid)):
                for i in range(f["chunks"]):
                    try:
                        store.chunk_path(f["id"], i).unlink()
                    except OSError:
                        pass
                store.x("DELETE FROM files WHERE id=?", (f["id"],))
            store.x("DELETE FROM items WHERE id=?", (iid,))
            store.x("DELETE FROM item_spaces WHERE item=?", (iid,))
            store.x("INSERT OR REPLACE INTO tombstones (item, seq) VALUES (?,?)", (iid, seq))

    @app.post("/api/grants")
    def grant_contact(body: dict = Body(...), ctx: Ctx = Depends(executive)):
        p, a, b = body["production"], body["a"], body["b"]
        if a == b or not store.one("SELECT 1 FROM productions WHERE id=?", (p,)):
            raise HTTPException(400, "Pick two people in a production.")
        gid = rc.new_id("g_")
        with store.tx(users={a, b}) as seq:
            store.x("INSERT INTO grants (id, production, a, b, granted_by, seq) VALUES (?,?,?,?,?,?)",
                    (gid, p, a, b, ctx.user, seq))
            store.audit(seq, ctx.user, ctx.device["id"], "granted contact", p, {"grant": gid, "a": a, "b": b})
        return {"id": gid}

    @app.post("/api/grants/{gid}/revoke")
    def revoke_grant(gid: str, ctx: Ctx = Depends(executive)):
        g = store.one("SELECT * FROM grants WHERE id=?", (gid,))
        if not g:
            raise HTTPException(404, "Unknown grant.")
        with store.tx(users={g["a"], g["b"]}) as seq:
            store.x("UPDATE grants SET revoked=1, seq=? WHERE id=?", (seq, gid))
            store.audit(seq, ctx.user, ctx.device["id"], "revoked contact", g["production"], {"grant": gid})
        return {"ok": True}

    # ------------------------------------------------------------------ spaces and keys
    def _check_wraps(wraps: list, ctx: Ctx, v: View, *, new_epoch: tuple | None = None) -> list:
        """Every wrap is signed by the caller's device, for a device whose user may hold that key. new_epoch:
        (space, epoch) the caller is creating now (so it doesn't hold the key yet on the hub)."""
        ok = []
        for w in wraps:
            if w.get("by") != ctx.device["id"] or not rc.verify(ctx.device["ed"], rc.wrap_signed_bytes(w), w.get("sig", "")):
                raise HTTPException(400, "A key wrap isn't signed by this device.")
            sp = v.spaces.get(w["space"])
            if not sp or w["epoch"] < 1 or w["epoch"] > sp["epoch"] + (1 if new_epoch == (w["space"], w["epoch"]) else 0):
                raise HTTPException(400, "A key wrap names an unknown space or epoch.")
            if new_epoch != (w["space"], w["epoch"]) and not store.one(
                    "SELECT 1 FROM wraps WHERE space=? AND epoch=? AND device=?", (w["space"], w["epoch"], ctx.device["id"])):
                raise HTTPException(403, "This device doesn't hold that key.")
            d = store.one("SELECT user, status FROM devices WHERE id=?", (w["device"],))
            if not d or d["status"] != "approved" or d["user"] not in v.key_recipients(w["space"]):
                continue                                   # not entitled (any more): quietly skipped
            ok.append(w)
        return ok

    def _store_wraps(wraps: list, seq: int):
        for w in wraps:
            store.x("INSERT OR IGNORE INTO wraps (space, epoch, device, w, seq) VALUES (?,?,?,?,?)",
                    (w["space"], w["epoch"], w["device"], json.dumps(w), seq))

    @app.post("/api/spaces")
    def create_space(body: dict = Body(...), ctx: Ctx = Depends(approved)):
        v = ctx.view()
        sid, p, kind = body["id"], body["production"], body["kind"]
        if not sid.startswith("s_") or store.one("SELECT 1 FROM spaces WHERE id=?", (sid,)):
            raise HTTPException(400, "Bad or duplicate space id.")
        if p not in v.productions_visible() or kind not in ("channel", "dm", "personal", "directory"):
            raise HTTPException(400, "Unknown production or kind of space.")
        if store.one("SELECT archived FROM productions WHERE id=?", (p,))["archived"]:
            raise HTTPException(409, "This production is archived.")
        members, owner = list(body.get("members") or []), body.get("owner")
        if kind == "dm":
            if len(members) != 2 or ctx.user not in members:
                raise HTTPException(400, "A private conversation has two people, you and one other.")
            other = next(m for m in members if m != ctx.user)
            if not v.can_reach(p, other):
                raise HTTPException(403, "You can't start a conversation with that person.")
            existing = [s for s, sp in v.spaces.items() if sp["kind"] == "dm" and sp["production"] == p
                        and sp.get("explicit", set()) == set(members)]
            if existing:
                return {"id": existing[0], "existing": True}
        elif not v.can_manage(p):
            raise HTTPException(403, "Only producers and executives create spaces.")
        if kind == "directory" and store.one("SELECT 1 FROM spaces WHERE production=? AND kind='directory'", (p,)):
            raise HTTPException(409, "This production already has a directory.")
        if kind == "personal" and (not owner or store.one(
                "SELECT 1 FROM spaces WHERE production=? AND kind='personal' AND owner=?", (p, owner))):
            raise HTTPException(409, "That person already has a personal space here.")
        audience = body.get("audience") or {}
        aud = {"tiers": [t for t in audience.get("tiers", []) if t in TIERS],
               "departments": [str(d) for d in audience.get("departments", [])], "second_ad": bool(audience.get("second_ad"))}
        with store.tx() as seq:
            store.x("INSERT INTO spaces (id, production, kind, audience, owner, epoch, created_by, seq) VALUES (?,?,?,?,?,?,?,?)",
                    (sid, p, kind, json.dumps(aud), owner, 1, ctx.user, seq))
            for m in members:
                store.x("INSERT OR IGNORE INTO space_members (space, user, seq) VALUES (?,?,?)", (sid, m, seq))
            v2 = View(store, ctx.user)
            wraps = _check_wraps(body.get("wraps", []), ctx, v2, new_epoch=(sid, 1))
            if not any(w["device"] == ctx.device["id"] for w in wraps):
                raise HTTPException(400, "Include a key wrap for your own device.")
            _store_wraps(wraps, seq)
            store.audit(seq, ctx.user, ctx.device["id"], "created a space", p, {"space": sid, "kind": kind})
        return {"id": sid}

    @app.post("/api/spaces/{sid}/members")
    def space_members(sid: str, body: dict = Body(...), ctx: Ctx = Depends(approved)):
        v = ctx.view()
        sp = v.spaces.get(sid)
        if not sp or not v.can_see_space(sid) or not v.can_manage(sp["production"]) or sp["kind"] in ("dm", "directory"):
            raise HTTPException(404, "Unknown space.")
        with store.tx() as seq:
            for u in body.get("add", []):
                store.x("INSERT OR IGNORE INTO space_members (space, user, seq) VALUES (?,?,?)", (sid, u, seq))
            if body.get("remove"):
                for u in body["remove"]:
                    store.x("DELETE FROM space_members WHERE space=? AND user=?", (sid, u))
                store.x("UPDATE spaces SET rotate=1, seq=? WHERE id=?", (seq, sid))
            if "audience" in body:
                a = body["audience"]
                store.x("UPDATE spaces SET audience=?, rotate=1, seq=? WHERE id=?",
                        (json.dumps({"tiers": [t for t in a.get("tiers", []) if t in TIERS],
                                     "departments": [str(d) for d in a.get("departments", [])],
                                     "second_ad": bool(a.get("second_ad"))}), seq, sid))
            store.audit(seq, ctx.user, ctx.device["id"], "changed who is in a space", sp["production"],
                        {"space": sid, "add": body.get("add", []), "remove": body.get("remove", [])})
        return {"ok": True}

    @app.post("/api/spaces/{sid}/rotate")
    def rotate(sid: str, body: dict = Body(...), ctx: Ctx = Depends(approved)):
        v = ctx.view()
        sp = v.spaces.get(sid)
        if not sp or not v.can_see_space(sid):
            raise HTTPException(404, "Unknown space.")
        if not (v.can_manage(sp["production"]) or (sp["kind"] == "dm" and v.is_member(sid))):
            raise HTTPException(403, "Only producers and executives change a space's keys.")
        if body.get("epoch") != sp["epoch"] + 1:
            raise HTTPException(409, "Someone else changed the keys first. Sync and try again.")
        wraps = _check_wraps(body.get("wraps", []), ctx, v, new_epoch=(sid, sp["epoch"] + 1))
        if not any(w["device"] == ctx.device["id"] for w in wraps):
            raise HTTPException(400, "Include a key wrap for your own device.")
        with store.tx() as seq:
            store.x("UPDATE spaces SET epoch=?, rotate=0, seq=? WHERE id=?", (sp["epoch"] + 1, seq, sid))
            _store_wraps(wraps, seq)
            store.audit(seq, ctx.user, ctx.device["id"], "changed a space's keys", sp["production"],
                        {"space": sid, "epoch": sp["epoch"] + 1})
        return {"epoch": sp["epoch"] + 1}

    @app.post("/api/wraps")
    def add_wraps(body: dict = Body(...), ctx: Ctx = Depends(approved)):
        v = ctx.view()
        wraps = _check_wraps(body.get("wraps", []), ctx, v)
        users = {store.one("SELECT user FROM devices WHERE id=?", (w["device"],))["user"] for w in wraps}
        with store.tx(users=users) as seq:
            _store_wraps(wraps, seq)
        return {"stored": len(wraps)}

    # ------------------------------------------------------------------ items
    def _item_spaces_ok(item: dict, v: View, ctx: Ctx) -> tuple[str, list]:
        h = item["h"]
        spaces = [s for s, _ in h.get("spaces", [])]
        if not spaces or set(item.get("keys", {})) != set(spaces):
            raise HTTPException(400, "The item's spaces and keys don't match.")
        prods = {v.spaces[s]["production"] for s in spaces if s in v.spaces}
        if len(prods) != 1 or len([s for s in spaces if s in v.spaces]) != len(spaces) or h.get("prod") not in prods:
            raise HTTPException(400, "An item belongs to spaces in one production.")
        p = prods.pop()
        for s, e in h["spaces"]:
            sp = v.spaces[s]
            if e != sp["epoch"]:
                raise HTTPException(409, "A space's keys changed. Sync and send again.")
            if sp["kind"] == "directory":
                if h["kind"] not in DIR_KINDS or not v.can_manage(p):
                    raise HTTPException(403, "Only producers and executives change names in the Room.")
            elif h["kind"] in DIR_KINDS or h["kind"] not in POST_KINDS:
                raise HTTPException(400, "Unknown kind of item.")
            elif not (v.is_member(s) or v.exec):
                raise HTTPException(403, "You can't post there.")
            if h["kind"] in ("callsheet", "callsheet_row") and not v.can_manage(p):
                raise HTTPException(403, "Only producers and executives publish call sheets.")
        return p, spaces

    @app.post("/api/items")
    def post_item(body: dict = Body(...), ctx: Ctx = Depends(approved)):
        v = ctx.view()
        it = body["item"]
        h = it["h"]
        if h.get("by") != ctx.device["id"] or not rc.verify_item(it, ctx.device["ed"]):
            raise HTTPException(400, "The item isn't signed by this device.")
        if not str(h.get("id", "")).startswith("m_") or store.one("SELECT 1 FROM items WHERE id=?", (h["id"],)):
            raise HTTPException(400, "Bad or duplicate item id.")
        p, spaces = _item_spaces_ok(it, v, ctx)
        if store.one("SELECT archived FROM productions WHERE id=?", (p,))["archived"]:
            raise HTTPException(409, "This production is archived.")
        readers = set().union(*(v.space_members(s) for s in spaces))
        mentions = [m for m in body.get("mentions", []) if m in readers or m in v.execs]
        wake = readers | v.execs
        with store.tx(users=wake) as seq:
            store.x("INSERT INTO items (id, production, kind, author, device, subject, body, ts, seq) VALUES (?,?,?,?,?,?,?,?,?)",
                    (h["id"], p, h["kind"], ctx.user, ctx.device["id"], h.get("subject"), json.dumps(it),
                     int(time.time()), seq))
            for s in spaces:
                store.x("INSERT INTO item_spaces (item, space) VALUES (?,?)", (h["id"], s))
            note = set(mentions)
            if any(v.spaces[s]["kind"] == "dm" for s in spaces):
                note |= readers
            if h["kind"] == "callsheet" or h["kind"] == "callsheet_row":
                note |= readers
            for u in note - {ctx.user}:
                store.x("INSERT INTO notifications (user, production, kind, item, ts, seq) VALUES (?,?,?,?,?,?)",
                        (u, p, "mention" if u in mentions else ("callsheet" if h["kind"].startswith("callsheet") else "dm"),
                         h["id"], int(time.time()), seq))
            if h["kind"] == "file" and h.get("ref"):
                store.x("UPDATE files SET item=?, status=CASE WHEN status='uploaded' THEN 'ready' ELSE status END, seq=? "
                        "WHERE id=? AND created_by=?", (h["id"], seq, h["ref"], ctx.device["id"]))
        if app.state.push and note - {ctx.user}:
            app.state.push.notify(store, note - {ctx.user}, p)
        return {"id": h["id"], "seq": seq}

    @app.post("/api/items/{iid}/delete")
    def delete_item(iid: str, ctx: Ctx = Depends(approved)):
        r = store.one("SELECT * FROM items WHERE id=?", (iid,))
        v = ctx.view()
        if not r or not (r["author"] == ctx.user or v.can_manage(r["production"])):
            raise HTTPException(404, "Unknown item.")
        with store.tx() as seq:
            _delete_items([r], seq)
            store.audit(seq, ctx.user, ctx.device["id"], "deleted an item", r["production"], {"item": iid})
        return {"ok": True}

    @app.get("/api/spaces/{sid}/items")
    def space_items(sid: str, before: int | None = None, limit: int = 200, ctx: Ctx = Depends(approved)):
        """A space's items. An executive opening a space they aren't in is recorded in the audit log."""
        v = ctx.view()
        if not v.can_see_space(sid):
            raise HTTPException(404, "Unknown space.")
        if not v.is_member(sid) and v.spaces[sid]["kind"] != "directory":
            with store.tx(users=set()) as seq:
                store.audit(seq, ctx.user, ctx.device["id"], "read a space they aren't in", v.spaces[sid]["production"],
                            {"space": sid, "kind": v.spaces[sid]["kind"]})
        rows = store.q("SELECT i.body, i.seq FROM items i JOIN item_spaces x ON x.item=i.id WHERE x.space=? "
                       + ("AND i.seq < ? " if before else "") + "ORDER BY i.seq DESC LIMIT ?",
                       (sid, before, min(limit, 500)) if before else (sid, min(limit, 500)))
        return {"items": [dict(json.loads(r["body"]), seq=r["seq"]) for r in reversed(rows)]}

    # ------------------------------------------------------------------ files (encrypted chunks, resumable)
    @app.post("/api/files")
    def create_file(body: dict = Body(...), ctx: Ctx = Depends(approved)):
        v = ctx.view()
        sid = body["space"]
        if not v.can_see_space(sid) or not (v.is_member(sid) or v.exec) or v.spaces[sid]["kind"] == "directory":
            raise HTTPException(403, "You can't add files there.")
        chunks, size = int(body["chunks"]), int(body["size"])
        if chunks < 1 or chunks > 100000 or size < 0:
            raise HTTPException(400, "Bad file size.")
        fid = rc.new_id("f_")
        lineage = body.get("lineage") or fid
        prev = store.one("SELECT MAX(version) AS v FROM files WHERE lineage=? AND space=?", (lineage, sid))
        version = (prev["v"] or 0) + 1
        with store.tx(users=set()) as seq:
            store.x("INSERT INTO files (id, space, lineage, version, chunks, size, status, created_by, seq) VALUES (?,?,?,?,?,?,?,?,?)",
                    (fid, sid, lineage, version, chunks, size, "uploading", ctx.device["id"], seq))
        return {"id": fid, "lineage": lineage, "version": version}

    def _file(fid: str, ctx: Ctx, write=False):
        f = store.one("SELECT * FROM files WHERE id=?", (fid,))
        v = ctx.view()
        if not f or not v.can_see_space(f["space"]):
            raise HTTPException(404, "Unknown file.")
        if write and f["created_by"] != ctx.device["id"]:
            raise HTTPException(403, "Only the device uploading a file can send its parts.")
        return f, v

    @app.put("/api/files/{fid}/chunks/{i}")
    async def put_chunk(fid: str, i: int, request: Request, ctx: Ctx = Depends(approved)):
        f, _ = _file(fid, ctx, write=True)
        if not 0 <= i < f["chunks"] or f["status"] not in ("uploading", "uploaded"):
            raise HTTPException(400, "Bad part number.")
        data = bytearray()
        async for part in request.stream():
            data += part
            if len(data) > MAX_CHUNK:
                raise HTTPException(413, "That part is too large.")
        data = bytes(data)
        if len(data) < 40:
            raise HTTPException(413, "That part is the wrong size.")
        p = store.chunk_path(fid, i)
        tmp = p.with_suffix(".part")
        tmp.write_bytes(data)
        os.replace(tmp, p)
        present = sum(1 for k in range(f["chunks"]) if store.chunk_path(fid, k).exists())
        if present == f["chunks"]:
            with store.tx(users=set()) as seq:
                store.x("UPDATE files SET status=CASE WHEN item IS NULL THEN 'uploaded' ELSE 'ready' END, seq=? WHERE id=?",
                        (seq, fid))
        return {"ok": True, "present": present}

    @app.get("/api/files/{fid}")
    def file_status(fid: str, ctx: Ctx = Depends(approved)):
        f, _ = _file(fid, ctx)
        have = [k for k in range(f["chunks"]) if store.chunk_path(fid, k).exists()]
        return {"id": fid, "space": f["space"], "lineage": f["lineage"], "version": f["version"], "chunks": f["chunks"],
                "size": f["size"], "status": f["status"], "present": have}

    @app.get("/api/files/{fid}/chunks/{i}")
    def get_chunk(fid: str, i: int, ctx: Ctx = Depends(approved)):
        f, v = _file(fid, ctx)
        p = store.chunk_path(fid, i)
        if not 0 <= i < f["chunks"] or not p.exists():
            raise HTTPException(404, "That part hasn't arrived yet.")
        if i == 0 and not v.is_member(f["space"]):
            with store.tx(users=set()) as seq:
                store.audit(seq, ctx.user, ctx.device["id"], "opened a file in a space they aren't in",
                            v.spaces[f["space"]]["production"], {"file": fid})
        return Response(p.read_bytes(), media_type="application/octet-stream")

    # ------------------------------------------------------------------ call-sheet confirmations
    @app.post("/api/confirm")
    def confirm(body: dict = Body(...), ctx: Ctx = Depends(approved)):
        v = ctx.view()
        iid, version = body["item"], int(body["version"])
        spaces = [r["space"] for r in store.q("SELECT space FROM item_spaces WHERE item=?", (iid,))]
        it = store.one("SELECT production, kind FROM items WHERE id=?", (iid,))
        if not it or it["kind"] != "callsheet" or not any(v.is_member(s) for s in spaces):
            raise HTTPException(404, "Unknown call sheet.")
        managers = {u for u, m in v.members.get(it["production"], {}).items() if m["tier"] == "producer"} | v.execs
        with store.tx(users=managers | {ctx.user}) as seq:
            store.x("INSERT OR REPLACE INTO confirmations (item, version, user, ts, seq) VALUES (?,?,?,?,?)",
                    (iid, version, ctx.user, int(time.time()), seq))
        return {"ok": True}

    @app.post("/api/callsheets/{iid}/remind")
    def remind(iid: str, body: dict = Body(...), ctx: Ctx = Depends(approved)):
        v = ctx.view()
        it = store.one("SELECT production FROM items WHERE id=? AND kind='callsheet'", (iid,))
        if not it or not v.can_manage(it["production"]):
            raise HTTPException(404, "Unknown call sheet.")
        version = int(body["version"])
        expected = set(body.get("people") or [])
        mem = set(v.members.get(it["production"], {}))
        done = {r["user"] for r in store.q("SELECT user FROM confirmations WHERE item=? AND version=?", (iid, version))}
        todo = (expected & mem) - done
        with store.tx(users=todo) as seq:
            for u in todo:
                store.x("INSERT INTO notifications (user, production, kind, item, ts, seq) VALUES (?,?,?,?,?,?)",
                        (u, it["production"], "reminder", iid, int(time.time()), seq))
            store.audit(seq, ctx.user, ctx.device["id"], "sent call-sheet reminders", it["production"],
                        {"item": iid, "version": version, "count": len(todo)})
        if app.state.push and todo:
            app.state.push.notify(store, todo, it["production"])
        return {"reminded": len(todo)}

    # ------------------------------------------------------------------ sync
    @app.get("/api/sync")
    def sync(since: int = 0, ctx: Ctx = Depends(approved)):
        return _sync(ctx, since)

    def _sync(ctx: Ctx, since: int) -> dict:
        v = ctx.view()
        prods = v.productions_visible()
        people = v.visible_people()
        seen_users = set().union(*people.values()) if people else {ctx.user}
        seen_users |= v.execs | {ctx.user}
        spaces = v.visible_spaces()
        member_spaces = [s for s in spaces if v.is_member(s)]
        dev_rows = store.q("SELECT * FROM devices WHERE status IN ('approved','revoked') AND record IS NOT NULL")
        out = {
            "seq": store.seq,
            "me": {"user": ctx.user, "device": ctx.device["id"], "exec": v.exec,
                   "memberships": [{"production": p, "tier": m["tier"], "department": m["department"],
                                    "second_ad": bool(m["second_ad"])} for p, m in v.my.items() if p in prods]},
            "founder": _founder_record(),
            "productions": [{"id": p, "archived": v.productions[p]["archived"]} for p in sorted(prods)],
            "people": [{"user": u, "production": p, "tier": v.tier(p, u),
                        "department": (v.members.get(p, {}).get(u) or {}).get("department", ""),
                        "second_ad": bool((v.members.get(p, {}).get(u) or {}).get("second_ad")),
                        "can_reach": v.can_reach(p, u)}
                       for p, us in people.items() for u in sorted(us)],
            "devices": [{"record": json.loads(d["record"]), "status": d["status"]} for d in dev_rows
                        if d["user"] in seen_users],
            "exec_grants": [json.loads(r["rec"]) for r in store.q("SELECT rec FROM exec_grants ORDER BY id")],
            "revocations": [json.loads(r["rec"]) for r in store.q("SELECT rec FROM revocations ORDER BY id")],
            "spaces": [{"id": s, "production": v.spaces[s]["production"], "kind": v.spaces[s]["kind"],
                        "audience": v.spaces[s]["audience"], "owner": v.spaces[s]["owner"], "epoch": v.spaces[s]["epoch"],
                        "member": v.is_member(s),
                        "members": sorted(v.space_members(s) & seen_users) if v.spaces[s]["kind"] != "directory" else [],
                        "rotate": bool(v.spaces[s]["rotate"])} for s in spaces],
            "grants": [g for g in v.grants if g["production"] in prods and (v.exec or ctx.user in (g["a"], g["b"]))],
        }
        # what's new for this device
        out["wraps"] = [json.loads(r["w"]) for r in store.q(
            "SELECT w FROM wraps WHERE device=? AND seq>? ORDER BY seq", (ctx.device["id"], since))]
        items, files = [], []
        if member_spaces:
            qs = ",".join("?" * len(member_spaces))
            rows = store.q(f"SELECT DISTINCT i.id, i.body, i.seq, i.kind, i.subject, i.production FROM items i "
                           f"JOIN item_spaces x ON x.item=i.id WHERE x.space IN ({qs}) AND i.seq>? ORDER BY i.seq",
                           member_spaces + [since])
            for r in rows:
                if r["kind"] == "person" and r["subject"] not in people.get(r["production"], set()):
                    continue                       # a person this user can't see stays hidden
                items.append(dict(json.loads(r["body"]), seq=r["seq"]))
            files = [dict(r) for r in store.q(f"SELECT id, space, lineage, version, chunks, size, status, item, seq "
                                              f"FROM files WHERE space IN ({qs}) AND seq>? ORDER BY seq", member_spaces + [since])]
        # executives also get the directory of every production (names), but no content of spaces they aren't in
        if v.exec:
            dirs = [s for s in spaces if v.spaces[s]["kind"] == "directory" and s not in member_spaces]
            if dirs:
                qs = ",".join("?" * len(dirs))
                items += [dict(json.loads(r["body"]), seq=r["seq"]) for r in store.q(
                    f"SELECT DISTINCT i.body, i.seq FROM items i JOIN item_spaces x ON x.item=i.id "
                    f"WHERE x.space IN ({qs}) AND i.seq>? ORDER BY i.seq", dirs + [since])]
        out["items"], out["files"] = items, files
        out["deleted"] = [r["item"] for r in store.q("SELECT item FROM tombstones WHERE seq>?", (since,))]
        out["notifications"] = [dict(r) for r in store.q(
            "SELECT id, production, kind, item, ts FROM notifications WHERE user=? AND seq>? ORDER BY seq", (ctx.user, since))]
        # call-sheet confirmations: your own, and everyone's for producers and executives
        conf = store.q("SELECT c.item, c.version, c.user, c.ts, i.production FROM confirmations c JOIN items i ON i.id=c.item")
        out["confirmations"] = [dict(r) for r in conf if r["user"] == ctx.user or v.can_manage(r["production"])]
        out["tasks"] = _tasks(ctx, v, spaces)
        if v.exec:
            out["pending"] = store.one("SELECT COUNT(*) AS n FROM devices WHERE status='pending'")["n"]
        return out

    def _tasks(ctx: Ctx, v: View, spaces: list) -> dict:
        """Key upkeep this device can do: wrap keys it holds for devices entitled to them, give spaces new keys after
        someone left, make a personal space for members who lack one."""
        mine = {}
        for r in store.q("SELECT space, epoch FROM wraps WHERE device=?", (ctx.device["id"],)):
            mine.setdefault(r["space"], set()).add(r["epoch"])
        devs_by_user: dict = {}
        for d in store.q("SELECT id, user, x FROM devices WHERE status='approved'"):
            devs_by_user.setdefault(d["user"], []).append({"id": d["id"], "x": d["x"]})
        have = {}
        for r in store.q("SELECT space, epoch, device FROM wraps"):
            have.setdefault((r["space"], r["epoch"]), set()).add(r["device"])
        wrap, rotate, personal = [], [], []
        for s in spaces:
            sp = v.spaces[s]
            if not mine.get(s):
                continue
            can_rotate = v.can_manage(sp["production"]) or (sp["kind"] == "dm" and v.is_member(s))
            if sp["rotate"] and can_rotate and sp["epoch"] in mine[s]:
                rotate.append({"space": s, "epoch": sp["epoch"]})
            for u in v.key_recipients(s):
                for d in devs_by_user.get(u, []):
                    for e in sorted(mine[s]):
                        if d["id"] not in have.get((s, e), set()):
                            wrap.append({"space": s, "epoch": e, "device": d["id"], "user": u})
        for p in v.productions_visible():
            if not v.can_manage(p) or v.productions[p]["archived"]:
                continue
            has = {sp["owner"] for sp in v.spaces.values() if sp["production"] == p and sp["kind"] == "personal"}
            for u, m in v.members.get(p, {}).items():
                if u not in has:
                    personal.append({"production": p, "user": u})
        person = []
        if v.exec:                                # an executive's own name in every production's directory
            named = {(r["production"]) for r in store.q("SELECT production FROM items WHERE kind='person' AND subject=?",
                                                         (ctx.user,))}
            dirs = {sp["production"] for sp in v.spaces.values() if sp["kind"] == "directory"
                    and (sp["id"], sp["epoch"]) in {(s, e) for s in mine for e in mine[s]}}
            person = [{"production": p} for p in sorted(dirs - named) if not v.productions[p]["archived"]]
        return {"wrap": wrap[:500], "rotate": rotate, "personal": personal, "person": person}

    # ------------------------------------------------------------------ audit log (executives)
    @app.get("/api/audit")
    def audit(limit: int = 500, ctx: Ctx = Depends(executive)):
        rows = store.q("SELECT * FROM audit ORDER BY n DESC LIMIT ?", (min(limit, 5000),))
        return {"intact": store.audit_ok(),
                "entries": [{"n": r["n"], "ts": r["ts"], "actor": r["actor"], "device": r["device"], "action": r["action"],
                             "production": r["production"], "target": json.loads(r["target"])} for r in rows]}

    # ------------------------------------------------------------------ live channel
    @app.websocket("/api/live")
    async def live(ws: WebSocket):
        await ws.accept()
        try:
            msg = await asyncio.wait_for(ws.receive_json(), timeout=15)
            d = _device_from_token(msg.get("token"))
        except Exception:  # noqa: BLE001
            await ws.close(code=4401)
            return
        user, last = d["user"], store.seq
        await ws.send_json({"seq": last})
        try:
            while True:
                await asyncio.sleep(0.5)
                m = max(marks.get(user, 0), marks.get("*", 0))
                if m > last:
                    last = m
                    await ws.send_json({"seq": m})
        except (WebSocketDisconnect, RuntimeError):
            return

    # ------------------------------------------------------------------ the phone app (served by the hub)
    static = Path(__file__).with_name("static")
    if static.exists():
        app.mount("/app", StaticFiles(directory=static, html=True), name="app")

        @app.get("/")
        def root():
            return FileResponse(static / "index.html")

    from . import meetings, retention   # noqa: E402 - feature routes share the store and auth above
    meetings.install(app, store, approved, View)
    retention.install(app, store)
    return app
