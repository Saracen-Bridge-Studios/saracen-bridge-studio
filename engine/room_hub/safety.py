"""Safety in the Room (1.2.0): the Room's terms, reporting, blocking, and deleting your own account.

Built for Apple's App Review rules for anything people post (guideline 1.2) and for deleting an account from inside
the app (5.1.1(v)). The Room stays end-to-end encrypted, so the hub still sees no content: a report carries only
which item or person, and a reason picked from a fixed list. The production's executives and producers, who hold the
keys, read the item in their own Room and act on it: remove it, remove the person, or dismiss the report. Every one
of those actions is in the audit log.

Blocking is per person and follows them to all their devices: someone you've blocked can't start a conversation
with you or post in one you share, and their messages are hidden on your devices.
"""
from __future__ import annotations

import time

import room_crypto as rc
from fastapi import Body, Depends, HTTPException

TERMS_VERSION = "2026-11-04"
REASONS = ("abusive", "harassment", "hate", "sexual", "violence", "self-harm", "spam", "other")
OUTCOMES = ("dismissed", "item_removed", "person_removed")

SCHEMA = """
CREATE TABLE IF NOT EXISTS reports (id TEXT PRIMARY KEY, production TEXT, item TEXT, about TEXT, reporter TEXT,
  reason TEXT, ts INTEGER, status TEXT, resolved_by TEXT, outcome TEXT, resolved_ts INTEGER, seq INTEGER);
CREATE TABLE IF NOT EXISTS blocks (user TEXT, blocked TEXT, seq INTEGER, PRIMARY KEY (user, blocked));
CREATE TABLE IF NOT EXISTS terms (user TEXT, version TEXT, ts INTEGER, PRIMARY KEY (user, version));
"""


def ensure_schema(store) -> None:
    with store.lock:
        store.c.executescript(SCHEMA)


def blocked_either_way(store, a: str, b: str) -> bool:
    return bool(store.one("SELECT 1 FROM blocks WHERE (user=? AND blocked=?) OR (user=? AND blocked=?)", (a, b, b, a)))


def blockers_of(store, user: str) -> set:
    """Everyone who has blocked this user."""
    return {r["user"] for r in store.q("SELECT user FROM blocks WHERE blocked=?", (user,))}


def accept_terms(store, user: str, version: str) -> None:
    store.x("INSERT OR IGNORE INTO terms (user, version, ts) VALUES (?,?,?)", (user, version, int(time.time())))


def sync_part(store, user: str, v) -> dict:
    """What a device needs: who this person blocks, whether they've accepted the current terms, and, for producers
    and executives, how many reports are open in each production they look after."""
    out = {"blocks": [r["blocked"] for r in store.q("SELECT blocked FROM blocks WHERE user=? ORDER BY blocked", (user,))],
           "terms": TERMS_VERSION,
           "terms_accepted": bool(store.one("SELECT 1 FROM terms WHERE user=? AND version=?", (user, TERMS_VERSION))),
           "reports_open": {}}
    for p in v.productions_visible():
        if v.can_manage(p):
            n = store.one("SELECT COUNT(*) AS n FROM reports WHERE production=? AND status='open'", (p,))["n"]
            if n:
                out["reports_open"][p] = n
    return out


def install(app, store, approved, any_device, delete_items, mark_rotation):
    ensure_schema(store)

    def _managers(v, p: str) -> set:
        producers = {u for u, m in v.members.get(p, {}).items() if m["tier"] == "producer"}
        return producers | v.execs

    def _item_visible(v, iid: str):
        r = store.one("SELECT * FROM items WHERE id=?", (iid,))
        if not r:
            return None, []
        spaces = [x["space"] for x in store.q("SELECT space FROM item_spaces WHERE item=?", (iid,))]
        if not any(v.can_see_space(s) for s in spaces):
            return None, spaces
        return r, spaces

    # ------------------------------------------------------------------ terms
    @app.post("/api/terms")
    def terms(body: dict = Body(...), ctx=Depends(any_device)):
        if body.get("version") != TERMS_VERSION:
            raise HTTPException(409, "The Room's terms have changed. Read the new ones and accept them.")
        with store.tx(users={ctx.user}) as seq:
            accept_terms(store, ctx.user, TERMS_VERSION)
            store.audit(seq, ctx.user, ctx.device["id"], "accepted the Room's terms", None, {"version": TERMS_VERSION})
        return {"ok": True, "version": TERMS_VERSION}

    # ------------------------------------------------------------------ reports
    @app.post("/api/reports")
    def report(body: dict = Body(...), ctx=Depends(approved)):
        v = ctx.view()
        reason = body.get("reason")
        if reason not in REASONS:
            raise HTTPException(400, "Pick a reason for the report.")
        iid, about = body.get("item"), body.get("about")
        if iid:
            r, _ = _item_visible(v, iid)
            if not r:
                raise HTTPException(404, "Unknown item.")
            p, about = r["production"], r["author"]
        else:
            p = body.get("production")
            if not about or p not in v.productions_visible() or about not in v.visible_people().get(p, set()):
                raise HTTPException(404, "Unknown person.")
        if about == ctx.user:
            raise HTTPException(400, "You can't report yourself.")
        dup = store.one("SELECT id FROM reports WHERE reporter=? AND status='open' AND production=? AND "
                        "COALESCE(item,'')=? AND about=?", (ctx.user, p, iid or "", about))
        if dup:
            return {"id": dup["id"], "existing": True}
        rid = rc.new_id("r_")
        tell = _managers(v, p) - {ctx.user, about}
        with store.tx(users=tell | {ctx.user}) as seq:
            store.x("INSERT INTO reports (id, production, item, about, reporter, reason, ts, status, seq) "
                    "VALUES (?,?,?,?,?,?,?,?,?)", (rid, p, iid, about, ctx.user, reason, int(time.time()), "open", seq))
            for u in tell:
                store.x("INSERT INTO notifications (user, production, kind, item, ts, seq) VALUES (?,?,?,?,?,?)",
                        (u, p, "report", iid, int(time.time()), seq))
            store.audit(seq, ctx.user, ctx.device["id"], "reported content", p,
                        {"report": rid, "item": iid, "about": about, "reason": reason})
        if app.state.push and tell:
            app.state.push.notify(store, tell, p)
        return {"id": rid}

    @app.get("/api/reports")
    def reports(production: str, status: str = "open", ctx=Depends(approved)):
        v = ctx.view()
        if production not in v.productions_visible() or not v.can_manage(production):
            raise HTTPException(403, "Only producers and executives see reports.")
        rows = store.q("SELECT * FROM reports WHERE production=? AND (?='all' OR status=?) ORDER BY ts DESC LIMIT 500",
                       (production, status, status))
        out = []
        for r in rows:
            it = store.one("SELECT kind FROM items WHERE id=?", (r["item"],)) if r["item"] else None
            spaces = [x["space"] for x in store.q("SELECT space FROM item_spaces WHERE item=?", (r["item"],))] if r["item"] else []
            out.append({"id": r["id"], "production": r["production"], "item": r["item"], "kind": it["kind"] if it else None,
                        "gone": bool(r["item"]) and not it, "spaces": spaces,
                        "readable": bool(it) and (v.exec or any(v.is_member(s) for s in spaces)),
                        "about": r["about"], "reporter": r["reporter"], "reason": r["reason"], "ts": r["ts"],
                        "status": r["status"], "outcome": r["outcome"], "resolved_by": r["resolved_by"],
                        "resolved_ts": r["resolved_ts"], "about_is_exec": r["about"] in v.execs})
        return out

    @app.post("/api/reports/{rid}/resolve")
    def resolve(rid: str, body: dict = Body(...), ctx=Depends(approved)):
        v = ctx.view()
        r = store.one("SELECT * FROM reports WHERE id=?", (rid,))
        if not r or r["production"] not in v.productions_visible() or not v.can_manage(r["production"]):
            raise HTTPException(404, "Unknown report.")
        outcome, p = body.get("outcome"), r["production"]
        if outcome not in OUTCOMES:
            raise HTTPException(400, "Pick what was done: dismissed, item removed or person removed.")
        if r["status"] != "open":
            raise HTTPException(409, "That report has already been dealt with.")
        if outcome == "person_removed":
            if not v.exec:
                raise HTTPException(403, "Only an executive can remove a person from a production.")
            if r["about"] in v.execs:
                raise HTTPException(409, "An executive can't be removed from a production here.")
        now = int(time.time())
        with store.tx() as seq:
            if outcome == "item_removed" and r["item"]:
                rows = store.q("SELECT id FROM items WHERE id=?", (r["item"],))
                delete_items(rows, seq)
                store.audit(seq, ctx.user, ctx.device["id"], "deleted an item", p, {"item": r["item"], "report": rid})
            if outcome == "person_removed":
                mark_rotation(r["about"], seq, p)
                store.x("DELETE FROM memberships WHERE user=? AND production=?", (r["about"], p))
                store.x("DELETE FROM space_members WHERE user=? AND space IN (SELECT id FROM spaces WHERE production=?)",
                        (r["about"], p))
                store.audit(seq, ctx.user, ctx.device["id"], "removed a member", p, {"user": r["about"], "report": rid})
            # one decision settles every open report about the same thing
            same = ("item=?", r["item"]) if r["item"] and outcome == "item_removed" else \
                   ("about=?", r["about"]) if outcome == "person_removed" else ("id=?", rid)
            store.x(f"UPDATE reports SET status='resolved', outcome=?, resolved_by=?, resolved_ts=?, seq=? "
                    f"WHERE production=? AND status='open' AND {same[0]}", (outcome, ctx.user, now, seq, p, same[1]))
            store.audit(seq, ctx.user, ctx.device["id"], "dealt with a report", p, {"report": rid, "outcome": outcome})
        return {"ok": True}

    # ------------------------------------------------------------------ blocking
    @app.post("/api/blocks")
    def block(body: dict = Body(...), ctx=Depends(approved)):
        other, on = body.get("user"), bool(body.get("blocked", True))
        if not other or other == ctx.user or not store.one("SELECT 1 FROM users WHERE id=?", (other,)):
            raise HTTPException(400, "Pick someone to block.")
        with store.tx(users={ctx.user}) as seq:
            if on:
                store.x("INSERT OR IGNORE INTO blocks (user, blocked, seq) VALUES (?,?,?)", (ctx.user, other, seq))
            else:
                store.x("DELETE FROM blocks WHERE user=? AND blocked=?", (ctx.user, other))
        return {"ok": True, "blocked": on}

    # ------------------------------------------------------------------ deleting your own account
    @app.post("/api/me/delete")
    def delete_me(body: dict = Body(...), ctx=Depends(approved)):
        """Your account in this Room deleted at your request: your messages, notes, files, call-sheet confirmations,
        memberships and devices. The audit log keeps its record that this happened (it's append-only)."""
        if body.get("confirm") != "DELETE":
            raise HTTPException(400, "Confirm the deletion first.")
        u = store.one("SELECT * FROM users WHERE id=?", (ctx.user,))
        if not u or u["founder"]:
            raise HTTPException(409, "The person who set up this Room can't delete their account from a phone. "
                                     "Hand the Room to another executive in the Studio first.")
        user = ctx.user
        with store.tx() as seq:
            mark_rotation(user, seq)
            delete_items(store.q("SELECT id FROM items WHERE author=? OR (subject=? AND kind='person')", (user, user)), seq)
            for t in ("memberships", "space_members", "confirmations", "notifications", "blocks", "terms"):
                store.x(f"DELETE FROM {t} WHERE user=?", (user,))
            store.x("DELETE FROM blocks WHERE blocked=?", (user,))
            store.x("UPDATE reports SET reporter='' WHERE reporter=?", (user,))
            store.x("DELETE FROM tokens WHERE device IN (SELECT id FROM devices WHERE user=?)", (user,))
            store.x("DELETE FROM push_subs WHERE device IN (SELECT id FROM devices WHERE user=?)", (user,))
            store.x("UPDATE devices SET status='revoked', seq=? WHERE user=?", (seq, user))
            store.x("UPDATE users SET deleted=1, exec=0, seq=? WHERE id=?", (seq, user))
            store.audit(seq, user, ctx.device["id"], "deleted their own account", None, {"user": user})
        return {"ok": True}
