"""Voice huddles and meetings (1.0.8) on LiveKit (Apache-2.0), self-hosted beside the hub.

The hub issues each person a LiveKit access token for a room it has checked they may join. A huddle lets everyone in
it speak. A meeting (up to 75 people) puts executives on stage; everyone else watches until an executive brings
them up, which changes their permission live through LiveKit's room service. Identities are user ids, never names:
names stay encrypted in the Room. Media is end-to-end encrypted with a key from the Room's own key system (it rides
in the meeting's encrypted item), so LiveKit never sees the key.
"""
from __future__ import annotations

import json
import time

import httpx
import jwt
from fastapi import Body, Depends, HTTPException

MEETING_MAX = 75
HUDDLE_MAX = 25

SCHEMA = """
CREATE TABLE IF NOT EXISTS meetings (id TEXT PRIMARY KEY, production TEXT, item TEXT, kind TEXT, created_by TEXT,
  created INTEGER, ended INTEGER, seq INTEGER);
CREATE TABLE IF NOT EXISTS meeting_stage (meeting TEXT, user TEXT, PRIMARY KEY (meeting, user));
"""


class LiveKit:
    """LiveKit's room service over HTTP (Twirp JSON), and access tokens (HS256 JWTs)."""

    def __init__(self, cfg: dict, http: httpx.Client | None = None):
        self.url, self.public_url = cfg["url"].rstrip("/"), cfg.get("public_url", cfg["url"]).rstrip("/")
        self.key, self.secret = cfg["key"], cfg["secret"]
        self.http = http or httpx.Client(timeout=10, trust_env=False)

    def token(self, identity: str, room: str, *, publish: bool, admin: bool = False, ttl: int = 6 * 3600) -> str:
        now = int(time.time())
        video = {"room": room, "roomJoin": True, "canPublish": publish, "canSubscribe": True, "canPublishData": True,
                 "canUpdateOwnMetadata": True}
        if admin:
            video = {"room": room, "roomCreate": True, "roomList": True, "roomAdmin": True}
        return jwt.encode({"iss": self.key, "sub": identity, "nbf": now - 10, "exp": now + ttl, "video": video},
                          self.secret, algorithm="HS256")

    def call(self, method: str, room: str, body: dict) -> dict:
        r = self.http.post(f"{self.url.replace('ws://', 'http://').replace('wss://', 'https://')}/twirp/livekit.RoomService/{method}",
                           json=body, headers={"Authorization": "Bearer " + self.token("room-hub", room, publish=False, admin=True)})
        if r.status_code >= 400:
            raise HTTPException(502, f"The media server said {r.status_code}: {r.text[:160]}")
        return r.json() if r.content else {}

    def create(self, room: str, max_participants: int):
        return self.call("CreateRoom", room, {"name": room, "max_participants": max_participants, "empty_timeout": 600})

    def participants(self, room: str) -> list[dict]:
        try:
            return self.call("ListParticipants", room, {"room": room}).get("participants", [])
        except HTTPException:
            return []

    def permit(self, room: str, identity: str, publish: bool):
        return self.call("UpdateParticipant", room, {"room": room, "identity": identity, "permission": {
            "can_publish": publish, "can_subscribe": True, "can_publish_data": True, "can_update_metadata": True}})

    def mute(self, room: str, identity: str, track_sid: str, muted: bool = True):
        return self.call("MutePublishedTrack", room, {"room": room, "identity": identity, "track_sid": track_sid, "muted": muted})


def install(app, store, approved, View):
    with store.lock:
        store.c.executescript(SCHEMA)

    def lk() -> LiveKit:
        if not getattr(app.state, "lk", None):
            cfg = app.state.livekit or {}
            if not cfg.get("url"):
                raise HTTPException(409, "Meetings need the Room's media server, which isn't set up on this hub yet.")
            app.state.lk = LiveKit(cfg, app.state.livekit.get("http"))
        return app.state.lk

    def _meeting(mid: str, ctx):
        m = store.one("SELECT * FROM meetings WHERE id=?", (mid,))
        if not m:
            raise HTTPException(404, "Unknown meeting.")
        v = ctx.view()
        spaces = [r["space"] for r in store.q("SELECT space FROM item_spaces WHERE item=?", (m["item"],))]
        if not any(v.can_see_space(s) for s in spaces):
            raise HTTPException(404, "Unknown meeting.")
        return dict(m), v, spaces

    @app.post("/api/meetings")
    def create_meeting(body: dict = Body(...), ctx=Depends(approved)):
        """Register a huddle or meeting for an item already posted (its encrypted payload holds the title, time and
        media key). Huddles: anyone in the space. Meetings: producers and executives."""
        v = ctx.view()
        item = store.one("SELECT * FROM items WHERE id=?", (body.get("item", ""),))
        if not item or item["kind"] not in ("meeting", "huddle") or item["device"] != ctx.device["id"]:
            raise HTTPException(400, "Post the meeting first.")
        kind = item["kind"]
        if kind == "meeting" and not v.can_manage(item["production"]):
            raise HTTPException(403, "Only producers and executives schedule meetings.")
        mid = "mt_" + item["id"][2:]
        if store.one("SELECT 1 FROM meetings WHERE id=?", (mid,)):
            return {"id": mid}
        lk().create(mid, MEETING_MAX if kind == "meeting" else HUDDLE_MAX)
        with store.tx() as seq:
            store.x("INSERT INTO meetings (id, production, item, kind, created_by, created, seq) VALUES (?,?,?,?,?,?,?)",
                    (mid, item["production"], item["id"], kind, ctx.user, int(time.time()), seq))
            store.audit(seq, ctx.user, ctx.device["id"], "scheduled a meeting" if kind == "meeting" else "started a huddle",
                        item["production"], {"meeting": mid})
        return {"id": mid}

    @app.post("/api/meetings/{mid}/token")
    def meeting_token(mid: str, ctx=Depends(approved)):
        m, v, _ = _meeting(mid, ctx)
        on_stage = m["kind"] == "huddle" or v.exec or bool(store.one(
            "SELECT 1 FROM meeting_stage WHERE meeting=? AND user=?", (mid, ctx.user)))
        cap = MEETING_MAX if m["kind"] == "meeting" else HUDDLE_MAX
        here = {p.get("identity") for p in lk().participants(mid)}
        if len(here) >= cap and ctx.user not in here:
            raise HTTPException(409, f"The meeting is full ({cap} people).")
        cfg = app.state.livekit
        return {"url": cfg.get("public_url") or cfg["url"], "token": lk().token(ctx.user, mid, publish=on_stage),
                "on_stage": on_stage, "kind": m["kind"], "max": cap, "identity": ctx.user}

    @app.get("/api/meetings/{mid}")
    def meeting_state(mid: str, ctx=Depends(approved)):
        m, v, _ = _meeting(mid, ctx)
        stage = [r["user"] for r in store.q("SELECT user FROM meeting_stage WHERE meeting=?", (mid,))]
        here = sorted({p.get("identity") for p in lk().participants(mid)} - {None}) if not m["ended"] else []
        return {"id": mid, "kind": m["kind"], "item": m["item"], "stage": sorted(set(stage) | v.execs), "here": here,
                "ended": bool(m["ended"]),
                "can_direct": v.exec, "max": MEETING_MAX if m["kind"] == "meeting" else HUDDLE_MAX}

    @app.post("/api/meetings/{mid}/stage")
    def meeting_stage(mid: str, body: dict = Body(...), ctx=Depends(approved)):
        """An executive brings someone on stage (they can speak and show video) or sends them back to watching."""
        m, v, _ = _meeting(mid, ctx)
        if not v.exec:
            raise HTTPException(403, "Only an executive decides who is on stage.")
        user, on = body["user"], bool(body.get("on", True))
        with store.tx(users={user}) as seq:
            if on:
                store.x("INSERT OR IGNORE INTO meeting_stage (meeting, user) VALUES (?,?)", (mid, user))
            else:
                store.x("DELETE FROM meeting_stage WHERE meeting=? AND user=?", (mid, user))
            store.audit(seq, ctx.user, ctx.device["id"], "brought someone on stage" if on else "sent someone back to watching",
                        m["production"], {"meeting": mid, "user": user})
        if user in {p.get("identity") for p in lk().participants(mid)}:
            lk().permit(mid, user, on)
        return {"ok": True}

    @app.post("/api/meetings/{mid}/mute")
    def meeting_mute(mid: str, body: dict = Body(...), ctx=Depends(approved)):
        m, v, _ = _meeting(mid, ctx)
        if not v.exec:
            raise HTTPException(403, "Only an executive can mute someone.")
        lk().mute(mid, body["user"], body["track"], True)
        return {"ok": True}

    @app.post("/api/meetings/{mid}/end")
    def meeting_end(mid: str, ctx=Depends(approved)):
        m, v, _ = _meeting(mid, ctx)
        if not (v.exec or m["created_by"] == ctx.user):
            raise HTTPException(403, "Only the person who started it or an executive can end it.")
        try:
            lk().call("DeleteRoom", mid, {"room": mid})
        except HTTPException:
            pass
        with store.tx() as seq:
            store.x("UPDATE meetings SET ended=?, seq=? WHERE id=?", (int(time.time()), seq, mid))
            store.audit(seq, ctx.user, ctx.device["id"], "ended a meeting", m["production"], {"meeting": mid})
        return {"ok": True}

    @app.get("/api/meetings")
    def meetings_list(production: str, ctx=Depends(approved)):
        v = ctx.view()
        out = []
        for m in store.q("SELECT * FROM meetings WHERE production=? AND ended IS NULL ORDER BY created DESC", (production,)):
            spaces = [r["space"] for r in store.q("SELECT space FROM item_spaces WHERE item=?", (m["item"],))]
            if any(v.can_see_space(s) for s in spaces):
                out.append({"id": m["id"], "item": m["item"], "kind": m["kind"], "created": m["created"]})
        return out
