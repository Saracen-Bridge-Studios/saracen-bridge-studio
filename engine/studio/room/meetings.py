"""Huddles and meetings on the Studio side (1.0.8): the encrypted meeting item (title, time, agenda and the media
key) and the hub's LiveKit token. The media key goes only to this PC's own page, which does LiveKit's end-to-end
encryption; LiveKit never sees it."""
from __future__ import annotations

import os
import time
from datetime import datetime, timedelta, timezone

import room_crypto as rc

from .client import RoomError


def _items(c, production: str, kinds=("meeting", "huddle")) -> dict:
    return {it["h"]["id"]: it for it in c.items.values() if it["h"]["kind"] in kinds and it["h"].get("prod") == production
            and it["payload"]}


def listing(c, production: str, people: dict) -> list[dict]:
    """Meetings and huddles this device can read, with who is in each right now."""
    try:
        live = {m["item"]: m for m in c._req("GET", "/api/meetings", params={"production": production})}
    except RoomError:
        live = {}
    out = []
    for iid, it in _items(c, production).items():
        m = live.get(iid)
        if not m:
            continue
        pl = it["payload"]
        out.append({"id": m["id"], "item": iid, "kind": m["kind"], "title": pl.get("title", ""), "starts": pl.get("starts"),
                    "minutes": pl.get("minutes"), "agenda": pl.get("agenda", ""), "spaces": [s for s, _ in it["h"]["spaces"]],
                    "by": people.get(it["author"], {}).get("name", "Someone"), "created": m["created"]})
    return sorted(out, key=lambda x: (x["starts"] or "", x["created"]))


def huddle_for(c, space: str) -> dict | None:
    sp = c.space(space)
    for m in listing(c, sp["production"], {}):
        if m["kind"] == "huddle" and m["spaces"] == [space]:
            return m
    return None


def start(c, production: str, spaces: list[str], kind: str, title: str, starts: str | None = None, minutes: int = 60,
          agenda: str = "") -> str:
    payload = {"title": title[:200], "starts": starts, "minutes": int(minutes or 60), "agenda": agenda[:4000],
               "media_key": rc.b64e(os.urandom(32))}
    item = c.post(spaces, kind, payload)
    return c._req("POST", "/api/meetings", json={"item": item["h"]["id"]})["id"]


def join(c, meeting_id: str) -> dict:
    """What the page needs to join: LiveKit's address and token from the hub, and the media key from the Room."""
    t = c._req("POST", f"/api/meetings/{meeting_id}/token")
    st = c._req("GET", f"/api/meetings/{meeting_id}")
    it = c.items.get(st["item"])
    if not it or not it["payload"] or not it["payload"].get("media_key"):
        raise RoomError("This device can't open the meeting's key yet. Sync and try again.")
    return dict(t, key=it["payload"]["media_key"], title=it["payload"].get("title", ""), meeting=meeting_id,
                stage=st["stage"], can_direct=st["can_direct"])


def ics(c, meeting_id: str, production_name: str) -> str:
    """A calendar invite (iCalendar) for a scheduled meeting. It carries the title and time only."""
    st = c._req("GET", f"/api/meetings/{meeting_id}")
    it = c.items.get(st["item"])
    if not it or not it["payload"] or not it["payload"].get("starts"):
        raise RoomError("That meeting has no time to put in a calendar.")
    pl = it["payload"]
    start = datetime.fromisoformat(pl["starts"])
    if start.tzinfo is None:
        start = start.astimezone()
    end = start + timedelta(minutes=int(pl.get("minutes") or 60))
    fmt = lambda d: d.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    esc = lambda s: str(s).replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")
    return "\r\n".join([
        "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Saracen Bridge//Room 1.0.8//EN", "BEGIN:VEVENT",
        f"UID:{meeting_id}@room", f"DTSTAMP:{fmt(datetime.now(timezone.utc))}", f"DTSTART:{fmt(start)}", f"DTEND:{fmt(end)}",
        f"SUMMARY:{esc(pl.get('title') or 'Meeting')} ({esc(production_name)})",
        "DESCRIPTION:Join from the Room in Saracen Bridge Studio or the Room app.", "END:VEVENT", "END:VCALENDAR", ""])
