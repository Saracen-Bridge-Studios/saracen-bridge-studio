"""The Studio's Room service: one RoomClient for this PC, a live link to the hub, and the view the Room pages draw.

Everything here runs inside the local Studio server (127.0.0.1). The page never talks to the hub directly; it asks
this service, which holds the keys and decrypts. The hub only ever sees ciphertext.
"""
from __future__ import annotations

import ipaddress
import json
import threading
import time
from pathlib import Path
from urllib.parse import urlparse

import room_crypto as rc

from .. import store
from .client import RoomClient, RoomError

OVERSIGHT = ("Executives on this production can read every space, file and private message in the Room. "
             "Every read is recorded in the audit log.")
TIER_LABEL = {"executive": "Executive", "producer": "Producer", "key": "Key personnel", "crew": "Crew", "cast": "Cast",
              "guest": "Guest"}
TIER_SEES = {
    "executive": ("Everything: every production, space, file and private message, plus the audit log. Approves devices, "
                  "sets tiers, creates productions.", "everyone"),
    "producer": ("Everything inside their productions. Invites keys, crew, cast and guests for an executive to approve.",
                 "executives, producers, their keys"),
    "key": ("Their department, heads of department, and spaces opened to them.", "their producers, other keys, their team"),
    "crew": ("Their department channel and board posts shared with it.", "their head of department, teammates"),
    "cast": ("Their own call and pickup times, their sides, the cast channel and posts shared with cast. No crew channels, "
             "no finance, no contact details.", "the 2nd AD, their producers, people they're granted"),
    "guest": ("Only the spaces and files shared with them.", "the people in those spaces"),
}
NOTE_STATUSES = ("Open", "Needs review", "Decision", "Done")

_LOCK = threading.RLock()
_CLIENT: RoomClient | None = None
_LIVE: dict = {"thread": None, "stop": None, "seq": 0, "error": "", "cond": threading.Condition()}


def folder() -> Path:
    p = store.home() / "room"
    p.mkdir(parents=True, exist_ok=True)
    return p


def client(hub: str | None = None) -> RoomClient:
    global _CLIENT
    with _LOCK:
        if _CLIENT is None or hub:
            _CLIENT = RoomClient(folder(), hub=hub)
            if hub:
                _CLIENT._save_state()
        return _CLIENT


def reset_for_tests():
    global _CLIENT
    stop_live()
    _CLIENT = None


def is_local(url: str) -> bool:
    host = urlparse(url).hostname or ""
    if host in ("localhost",):
        return True
    try:
        ip = ipaddress.ip_address(host)
        return ip.is_private or ip.is_loopback
    except ValueError:
        return host.endswith(".local") or host.endswith(".lan")


# ------------------------------------------------------------------ live link to the hub
def start_live():
    c = client()
    if c.state.get("status") != "approved" or not c.state.get("hub"):
        return
    with _LOCK:
        if _LIVE["thread"] and _LIVE["thread"].is_alive():
            return
        stop = threading.Event()
        _LIVE["stop"] = stop
        _LIVE["thread"] = threading.Thread(target=_live_loop, args=(stop,), daemon=True, name="room-live")
        _LIVE["thread"].start()


def stop_live():
    if _LIVE["stop"]:
        _LIVE["stop"].set()


def bumped():
    with _LIVE["cond"]:
        _LIVE["seq"] += 1
        _LIVE["cond"].notify_all()


def wait(since: int, timeout: float = 25) -> int:
    with _LIVE["cond"]:
        _LIVE["cond"].wait_for(lambda: _LIVE["seq"] > since, timeout=timeout)
        return _LIVE["seq"]


def _live_loop(stop: threading.Event):
    from websockets.sync.client import connect
    backoff = 1
    while not stop.is_set():
        c = client()
        try:
            url = c.state["hub"].replace("https://", "wss://").replace("http://", "ws://") + "/api/live"
            kw = {"proxy": None} if is_local(c.state["hub"]) else {}
            with connect(url, open_timeout=15, **kw) as ws:
                ws.send(json.dumps({"token": c._bearer()}))
                _LIVE["error"], backoff = "", 1
                while not stop.is_set():
                    try:
                        msg = json.loads(ws.recv(timeout=30))
                    except TimeoutError:
                        continue
                    if msg.get("seq", 0) > c.state.get("seq", 0):
                        with _LOCK:
                            c.sync()
                        bumped()
        except Exception as e:  # noqa: BLE001 - reconnect with backoff; the page shows the state
            _LIVE["error"] = f"Reconnecting to the Room ({type(e).__name__})."
            if stop.wait(backoff):
                return
            backoff = min(backoff * 2, 60)


# ------------------------------------------------------------------ view models
def _initials(name: str) -> str:
    parts = [p for p in (name or "?").replace("-", " ").split() if p]
    return ("".join(p[0] for p in parts[:2]) or "?").upper()


def people(c: RoomClient, p: str) -> dict:
    names = c.names(p)
    depts = names["department"]
    out = {}
    for x in c.snapshot.get("people", []):
        if x["production"] != p:
            continue
        info = names["person"].get(x["user"], {})
        out[x["user"]] = {"user": x["user"], "name": info.get("name") or "Someone", "role": info.get("role") or "",
                          "tier": x["tier"], "tier_label": TIER_LABEL.get(x["tier"], x["tier"]),
                          "department": (depts.get(x["department"]) or {}).get("name", "") if x["department"] else "",
                          "department_id": x["department"], "second_ad": x["second_ad"], "can_reach": x["can_reach"],
                          "initials": _initials(info.get("name") or "")}
    return out


def _space_name(c, names, sp, ppl) -> str:
    if sp["kind"] == "dm":
        other = [u for u in sp["members"] if u != c.me]
        if len(other) == 2:                                  # an executive looking at someone else's conversation
            return " ↔ ".join(ppl.get(u, {}).get("name", "Someone") for u in other)
        return ppl.get(other[0], {}).get("name", "Private conversation") if other else "Private conversation"
    if sp["kind"] == "personal":
        return "My day" if sp["owner"] == c.me else ppl.get(sp["owner"], {}).get("name", "Someone") + "'s day"
    return (names["space"].get(sp["id"]) or {}).get("name") or "Untitled space"


def _audience_text(c, names, sp) -> str:
    if sp["kind"] == "dm":
        return "A private conversation. Executives can read it, and every read is logged."
    if sp["kind"] == "personal":
        return "Only this person and the production office can see this."
    a = sp["audience"] or {}
    bits = [TIER_LABEL.get(t, t).lower() for t in a.get("tiers", [])]
    depts = [(names["department"].get(d) or {}).get("name", "a department") for d in a.get("departments", [])]
    who = ", ".join(bits) or "the people added"
    if depts:
        who += " in " + ", ".join(depts)
    if a.get("second_ad"):
        who += ", the 2nd AD"
    return f"Visible to {who}, producers and executives."


def productions(c: RoomClient) -> list[dict]:
    out = []
    for pr in c.snapshot.get("productions", []):
        nm = (c.names(pr["id"])["production"].get(pr["id"]) or {}).get("name") or "Untitled production"
        out.append({"id": pr["id"], "name": nm, "archived": bool(pr["archived"]),
                    "members": sum(1 for x in c.snapshot.get("people", []) if x["production"] == pr["id"])})
    return out


def my_tier(c: RoomClient, p: str) -> str:
    if c.is_exec:
        return "executive"
    for m in c.snapshot.get("me", {}).get("memberships", []):
        if m["production"] == p:
            return m["tier"]
    return ""


def notes_latest(c: RoomClient, spaces: set) -> dict:
    """note id -> its latest status/pin from note_update items"""
    upd: dict = {}
    for it in sorted(c.items.values(), key=lambda r: r["seq"]):
        if it["h"]["kind"] == "note_update" and it["payload"] and it["h"].get("ref"):
            upd.setdefault(it["h"]["ref"], {}).update(it["payload"])
    return upd


def view(c: RoomClient, production: str | None = None) -> dict:
    prods = productions(c)
    if not prods:
        return {"me": _me(c, None), "productions": [], "production": None}
    pid = production if any(x["id"] == production for x in prods) else c.state.get("last_production")
    if not any(x["id"] == pid for x in prods):
        pid = next((x["id"] for x in prods if not x["archived"]), prods[0]["id"])
    if c.state.get("last_production") != pid:
        c.state["last_production"] = pid
        c._save_state()
    names, ppl = c.names(pid), people(c, pid)
    read = c.state.get("read", {})
    spaces, dms, mine = [], [], None
    for sp in c.snapshot.get("spaces", []):
        if sp["production"] != pid or sp["kind"] == "directory":
            continue
        if sp["kind"] == "personal" and sp["owner"] != c.me:
            continue
        unread = sum(1 for it in c.items.values() if it["author"] != c.me and it["seq"] > read.get(sp["id"], 0)
                     and it["h"]["kind"] in ("msg", "note", "file", "callsheet", "callsheet_row")
                     and sp["id"] in {s for s, _ in it["h"]["spaces"]})
        row = {"id": sp["id"], "kind": sp["kind"], "name": _space_name(c, names, sp, ppl), "member": sp["member"],
               "unread": unread, "about": _audience_text(c, names, sp), "count": len(sp["members"]),
               "has_key": (sp["id"], sp["epoch"]) in c.keys}
        if sp["kind"] == "dm":
            other = next((u for u in sp["members"] if u != c.me), None)
            row["tier"] = ppl.get(other, {}).get("tier_label", "")
            row["oversight"] = c.me not in sp["members"]
            dms.append(row)
        elif sp["kind"] == "personal":
            mine = row
        else:
            spaces.append(row)
    spaces.sort(key=lambda s: s["name"].lower())
    visible_ids = {s["id"] for s in spaces} | {s["id"] for s in dms} | ({mine["id"]} if mine else set())
    sname = {s["id"]: s["name"] for s in spaces + dms + ([mine] if mine else [])}
    upd = notes_latest(c, visible_ids)
    files = {f["item"]: f for f in c.files()}
    board = []
    for it in c.items.values():
        h = it["h"]
        if h["kind"] != "note" or h.get("prod") != pid or not it["payload"]:
            continue
        pl = dict(it["payload"], **upd.get(h["id"], {}))
        att = files.get(pl.get("file_item")) if pl.get("file_item") else None
        board.append({"id": h["id"], "title": pl.get("title", ""), "body": pl.get("body", ""),
                      "status": pl.get("status", "Open"), "pinned": bool(pl.get("pinned")), "ts": h["ts"], "seq": it["seq"],
                      "spaces": [sname[s] for s, _ in h["spaces"] if s in sname], "space_ids": [s for s, _ in h["spaces"]],
                      "author": ppl.get(it["author"], {}).get("name", "Someone"),
                      "file": att and {"id": att["id"], "name": att["name"], "size": att["size"]}})
    board.sort(key=lambda n: (not n["pinned"], -n["seq"]))
    tier = my_tier(c, pid)
    out = {"me": _me(c, pid), "productions": prods, "production": pid,
           "production_name": next(x["name"] for x in prods if x["id"] == pid),
           "archived": next(x["archived"] for x in prods if x["id"] == pid),
           "spaces": spaces, "dms": dms, "my_day": mine, "board": board,
           "people": sorted(ppl.values(), key=lambda x: x["name"].lower()),
           "departments": [{"id": k, "name": v.get("name", "")} for k, v in names["department"].items()],
           "can_manage": tier in ("executive", "producer"), "is_exec": c.is_exec, "tier": tier,
           "pending": c.snapshot.get("pending", 0), "oversight": OVERSIGHT,
           "oversight_seen": bool(c.state.get("oversight_seen")),
           "notifications": _notifications(c, pid), "live": not _LIVE["error"], "live_error": _LIVE["error"],
           "uploads": list(UPLOADS.values()), "problems": c.problems[-5:]}
    from . import callsheets
    out["callsheet"] = callsheets.today(c, pid, ppl, sname)
    return out


def _me(c: RoomClient, p: str | None) -> dict:
    prof = c.state.get("profile") or {}
    nm = prof.get("name") or ""
    if p:
        nm = (c.names(p)["person"].get(c.me) or {}).get("name") or nm
    tier = my_tier(c, p) if p else ("executive" if c.is_exec else "")
    return {"user": c.me, "name": nm or "You", "initials": _initials(nm), "tier": tier,
            "tier_label": TIER_LABEL.get(tier, ""), "device": c.device.id if c.device else ""}


def _notifications(c: RoomClient, p: str) -> list:
    """New notifications with who and where (the hub sends only ids; names come from this device's directory)."""
    seen = c.state.get("notes_seen", 0)
    ppl, names = people(c, p), c.names(p)
    out = []
    for n in c.snapshot.get("notifications", []):
        if n["production"] != p or n["id"] <= seen:
            continue
        it = c.items.get(n["item"])
        who, where = "Someone", ""
        if it:
            who = ppl.get(it["author"], {}).get("name", "Someone")
            for s, _ in it["h"]["spaces"]:
                try:
                    where = _space_name(c, names, c.space(s), ppl)
                    break
                except RoomError:
                    continue
        out.append(dict(n, who=who, where=where))
    return out[-50:]


def space_view(c: RoomClient, sid: str, *, open_oversight: bool = False) -> dict:
    sp = c.space(sid)
    p = sp["production"]
    names, ppl = c.names(p), people(c, p)
    if not sp["member"] and sp["kind"] != "directory":
        if not open_oversight:
            return {"id": sid, "locked_oversight": True, "name": _space_name(c, names, sp, ppl),
                    "about": _audience_text(c, names, sp)}
        c.open_space(sid)                                  # the hub logs this read
    files = {f["item"]: f for f in c.files(sid)}
    msgs = []
    for it in sorted(c.items.values(), key=lambda r: r["seq"]):
        h = it["h"]
        if sid not in {s for s, _ in h["spaces"]} or h["kind"] not in ("msg", "file"):
            continue
        who = ppl.get(it["author"], {})
        pl = it["payload"] or {}
        m = {"id": h["id"], "author": who.get("name", "Someone"), "initials": who.get("initials", "?"),
             "tier": who.get("tier_label", ""), "ts": h["ts"], "mine": it["author"] == c.me, "seq": it["seq"]}
        if h["kind"] == "msg":
            m["text"] = pl.get("text", "") if it["payload"] is not None else "This message can't be opened on this device yet."
        else:
            f = files.get(h["id"])
            m["text"] = pl.get("note", "")
            m["file"] = f and {"id": f["id"], "name": f["name"], "size": f["size"], "version": f["version"]}
        msgs.append(m)
    lineages: dict = {}
    for f in c.files(sid):
        lineages.setdefault(f["lineage"], []).append(f)
    flist = []
    for versions in lineages.values():
        last = max(versions, key=lambda f: f["version"])
        flist.append({"id": last["id"], "name": last["name"], "size": last["size"], "version": last["version"],
                      "versions": [{"id": v["id"], "version": v["version"], "ts": v["ts"],
                                    "by": ppl.get(v["author"], {}).get("name", "Someone")} for v in sorted(versions, key=lambda v: -v["version"])],
                      "by": ppl.get(last["author"], {}).get("name", "Someone"), "ts": last["ts"]})
    flist.sort(key=lambda f: -f["ts"])
    if msgs:
        read = c.state.setdefault("read", {})
        read[sid] = max(read.get(sid, 0), max(m["seq"] for m in msgs))
        c._save_state()
    members = [ppl[u] for u in sp["members"] if u in ppl]
    return {"id": sid, "kind": sp["kind"], "name": _space_name(c, names, sp, ppl), "about": _audience_text(c, names, sp),
            "messages": msgs[-400:], "files": flist, "members": members, "member": sp["member"],
            "oversight_read": not sp["member"], "has_key": (sid, sp["epoch"]) in c.keys}


def mentions_in(text: str, members: list[dict]) -> list[str]:
    low = text.lower()
    return [m["user"] for m in members if m["name"] and "@" + m["name"].lower() in low]


def search(c: RoomClient, p: str, q: str) -> list[dict]:
    q = q.strip().lower()
    if len(q) < 2:
        return []
    ppl, names = people(c, p), c.names(p)
    sname = {sp["id"]: _space_name(c, names, sp, ppl) for sp in c.snapshot.get("spaces", []) if sp["production"] == p}
    out = []
    for it in sorted(c.items.values(), key=lambda r: -r["seq"]):
        h, pl = it["h"], it["payload"]
        if h.get("prod") != p or not pl or h["kind"] not in ("msg", "note", "file"):
            continue
        text = " ".join(str(pl.get(k, "")) for k in ("text", "title", "body", "name", "note"))
        if q in text.lower():
            sp = next((s for s, _ in h["spaces"] if s in sname), None)
            out.append({"kind": h["kind"], "text": text.strip()[:200], "space": sp, "space_name": sname.get(sp, ""),
                        "author": ppl.get(it["author"], {}).get("name", "Someone"), "ts": h["ts"], "id": h["id"]})
        if len(out) >= 50:
            break
    return out


# ------------------------------------------------------------------ uploads in the background
UPLOADS: dict = {}


def start_upload(space: str, name: str, path: Path, size: int, note: str = "", note_card: dict | None = None):
    """Encrypt and send a file from a temporary copy, in the background. The temporary plaintext copy is deleted as
    soon as it has been encrypted into the outbox."""
    key = rc.new_id("up_")
    UPLOADS[key] = {"key": key, "name": name, "space": space, "stage": "encrypting", "done": 0, "total": 1, "error": ""}

    def prog(stage, i, n):
        UPLOADS[key].update(stage=stage, done=i, total=n)

    def run():
        c = client()
        try:
            with open(path, "rb") as fh:
                item = c.upload(space, name, fh, size=size, note=note, progress=prog)
            if note_card is not None:
                c.post(note_card["spaces"], "note", dict(note_card["payload"], file_item=item["h"]["id"]))
            UPLOADS[key].update(stage="done")
        except Exception as e:  # noqa: BLE001 - shown on the page; the outbox keeps the parts for Resume
            UPLOADS[key].update(stage="failed", error=str(e))
        finally:
            try:
                path.unlink()
            except OSError:
                pass
            bumped()
    threading.Thread(target=run, daemon=True, name="room-upload").start()
    return key


def resume_uploads():
    """Uploads interrupted earlier (the app closed, the connection dropped) carry on from the outbox."""
    c = client()
    for fid, up in list((c.state.get("uploads") or {}).items()):
        key = "resume_" + fid
        if key in UPLOADS and UPLOADS[key]["stage"] not in ("failed", "done"):
            continue
        UPLOADS[key] = {"key": key, "name": up["name"], "space": up["space"], "stage": "sending", "done": 0,
                        "total": up["chunks"], "error": ""}

        def run(fid=fid, key=key):
            try:
                client().resume_upload(fid, progress=lambda st, i, n: UPLOADS[key].update(stage=st, done=i, total=n))
                UPLOADS[key]["stage"] = "done"
            except Exception as e:  # noqa: BLE001
                UPLOADS[key].update(stage="failed", error=str(e))
            bumped()
        threading.Thread(target=run, daemon=True, name="room-resume").start()


def wait_seconds() -> float:
    return 25.0


def now() -> float:
    return time.time()


__all__ = ["client", "view", "space_view", "search", "RoomError"]
