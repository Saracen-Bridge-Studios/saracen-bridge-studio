"""Call sheets in the Room (1.0.8).

A call sheet is one shooting day (a lineage). Each publish is a new version: a `callsheet` item with the day's facts,
shared with every channel of the production, plus one `callsheet_row` per person in that person's own space (only
they and the production office can read it: pickup addresses and drivers never go further). Each person taps
Got it; the hub records it per version, so a new version starts the count again and notifies everyone on it.
The PDF, if attached, is a Room file shared the same way as the sheet. PDF reading is not in 1.0.8.
"""
from __future__ import annotations

import csv
import io
import re
import time

import room_crypto as rc

from .client import RoomError

TIME = re.compile(r"^([01]?\d|2[0-3])[:.]?([0-5]\d)$")
CREW_FIELDS = ("call",)
CAST_FIELDS = ("pickup", "hmu", "costume", "on_set")
PRIVATE = ("pickup_address", "driver")
ALL_FIELDS = CREW_FIELDS + CAST_FIELDS + PRIVATE + ("character", "scenes", "notes")


def clean_time(t: str) -> str:
    t = (t or "").strip()
    if not t:
        return ""
    m = TIME.match(t.replace(" ", ""))
    if not m:
        raise RoomError(f"“{t}” isn't a time. Use 24-hour times like 06:30.")
    return f"{int(m.group(1)):02d}:{m.group(2)}"


def audience(c, production: str) -> list[str]:
    """Where a call sheet goes: every channel of the production this device can post in (departments, heads of
    department, cast, production office). Personal spaces get the per-person rows instead."""
    return [sp["id"] for sp in c.snapshot.get("spaces", []) if sp["production"] == production and sp["kind"] == "channel"
            and (sp["id"], sp["epoch"]) in c.keys]


def personal_space(c, production: str, user: str) -> str:
    for sp in c.snapshot.get("spaces", []):
        if sp["production"] == production and sp["kind"] == "personal" and sp["owner"] == user:
            return sp["id"]
    return c.create_space(production, "", kind="personal", owner=user)


def sheets(c, production: str) -> dict:
    """lineage -> versions (newest first), from the call-sheet items this device can read."""
    out: dict = {}
    for it in c.items.values():
        h, pl = it["h"], it["payload"]
        if h["kind"] == "callsheet" and h.get("prod") == production and pl:
            out.setdefault(pl["lineage"], []).append({"item": h["id"], "seq": it["seq"], "ts": h["ts"], **pl})
    for v in out.values():
        v.sort(key=lambda x: -x["version"])
    return out


def rows_for(c, production: str, lineage: str, version: int) -> dict:
    """user -> their row, for the rows this device can read (your own; everyone's in the production office)."""
    out = {}
    for it in sorted(c.items.values(), key=lambda r: r["seq"]):
        pl = it["payload"]
        if it["h"]["kind"] == "callsheet_row" and it["h"].get("prod") == production and pl and \
                pl.get("lineage") == lineage and pl.get("version") == version:
            out[pl["user"]] = pl
    return out


def confirmations(c, item: str) -> set:
    return {x["user"] for x in c.snapshot.get("confirmations", []) if x["item"] == item}


def pick_today(sh: dict) -> dict | None:
    """Today's sheet, else the next one coming, else the latest posted."""
    today = time.strftime("%Y-%m-%d")
    latest = [v[0] for v in sh.values()]
    if not latest:
        return None
    dated = sorted([s for s in latest if s.get("date")], key=lambda s: s["date"])
    for s in dated:
        if s["date"] >= today:
            return s
    return max(latest, key=lambda s: s["seq"])


def view(c, production: str, sheet: dict, people: dict) -> dict:
    rows = rows_for(c, production, sheet["lineage"], sheet["version"])
    conf = confirmations(c, sheet["item"])
    expected = list(sheet.get("people") or [])
    me = c.me
    manage = c.is_exec or any(m["production"] == production and m["tier"] == "producer"
                              for m in c.snapshot.get("me", {}).get("memberships", []))
    out = {k: sheet.get(k) for k in ("item", "lineage", "version", "day", "date", "unit_call", "location", "weather_cover",
                                     "base", "hospital", "scenes", "notes", "pdf")}
    out.update(posted=sheet["ts"], expected=len(expected), confirmed=len(conf & set(expected)), me_confirmed=me in conf,
               on_sheet=me in expected, my_row=rows.get(me), can_remind=manage)
    if manage:
        out["people"] = [dict(rows.get(u, {}), user=u, name=people.get(u, {}).get("name", "Someone"),
                              tier=people.get(u, {}).get("tier_label", ""), confirmed=u in conf) for u in expected]
    return out


def today(c, production: str, people: dict, space_names: dict) -> dict | None:
    s = pick_today(sheets(c, production))
    return view(c, production, s, people) if s else None


def publish(c, production: str, data: dict, *, pdf_file: dict | None = None) -> dict:
    """Post a new version of a call sheet. data: day, date, unit_call, location, weather_cover, base, hospital,
    scenes [{no, slug, pages, note}], notes, rows [{user, call, pickup, pickup_address, driver, hmu, costume, on_set,
    character, scenes, notes}], lineage (to publish a new version of an existing sheet)."""
    lineage = data.get("lineage") or rc.new_id("cs_")
    prev = sheets(c, production).get(lineage, [])
    version = (prev[0]["version"] + 1) if prev else 1
    rows = []
    for r in data.get("rows") or []:
        if not r.get("user"):
            continue
        row = {k: (clean_time(r.get(k, "")) if k in CREW_FIELDS + CAST_FIELDS else str(r.get(k, "") or "")[:300])
               for k in ALL_FIELDS}
        row["user"] = r["user"]
        rows.append(row)
    sheet = {"lineage": lineage, "version": version, "day": str(data.get("day") or "")[:40],
             "date": str(data.get("date") or "")[:10], "unit_call": clean_time(data.get("unit_call", "")),
             "location": str(data.get("location") or "")[:300], "weather_cover": str(data.get("weather_cover") or "")[:300],
             "base": str(data.get("base") or "")[:300], "hospital": str(data.get("hospital") or "")[:300],
             "scenes": [{k: str(s.get(k, "") or "")[:200] for k in ("no", "slug", "pages", "note")}
                        for s in (data.get("scenes") or []) if s.get("no") or s.get("slug")],
             "notes": str(data.get("notes") or "")[:4000], "people": [r["user"] for r in rows], "pdf": pdf_file}
    if not sheet["day"] or not sheet["unit_call"]:
        raise RoomError("Give the call sheet a day and a unit call.")
    spaces = audience(c, production)
    if not spaces:
        raise RoomError("There's no channel to post the call sheet in yet.")
    item = c.post(spaces, "callsheet", sheet, ref=lineage)
    for r in rows:
        c.post([personal_space(c, production, r["user"])], "callsheet_row", dict(r, lineage=lineage, version=version),
               ref=item["h"]["id"])
    c.sync()
    return {"item": item["h"]["id"], "lineage": lineage, "version": version}


def confirm(c, item: str):
    it = c.items.get(item)
    if not it or it["h"]["kind"] != "callsheet":
        raise RoomError("Unknown call sheet.")
    c._req("POST", "/api/confirm", json={"item": item, "version": it["payload"]["version"]})
    c.sync(upkeep=False)


def remind(c, item: str) -> int:
    it = c.items.get(item)
    if not it or it["h"]["kind"] != "callsheet":
        raise RoomError("Unknown call sheet.")
    r = c._req("POST", f"/api/callsheets/{item}/remind",
               json={"version": it["payload"]["version"], "people": it["payload"].get("people", [])})
    return r["reminded"]


def parse_csv(text: str, people: dict) -> dict:
    """Times from a spreadsheet: a header row naming a column for the person (name) and any of call, pickup,
    pickup address, driver, hair and make-up, costume, on set, character, scenes, notes. Names are matched to
    people on the production; rows that don't match are reported, not guessed."""
    rd = csv.DictReader(io.StringIO(text.lstrip("﻿")))
    if not rd.fieldnames:
        raise RoomError("The CSV has no header row.")
    key = lambda s: re.sub(r"[^a-z]", "", (s or "").lower())
    alias = {"name": "name", "person": "name", "call": "call", "calltime": "call", "pickup": "pickup",
             "pickupaddress": "pickup_address", "address": "pickup_address", "driver": "driver", "hmu": "hmu",
             "hairandmakeup": "hmu", "hairmakeup": "hmu", "makeup": "hmu", "costume": "costume", "wardrobe": "costume",
             "onset": "on_set", "set": "on_set", "character": "character", "role": "character", "scenes": "scenes",
             "notes": "notes"}
    cols = {f: alias[key(f)] for f in rd.fieldnames if key(f) in alias}
    if "name" not in cols.values():
        raise RoomError("Add a column called Name with each person's name as it appears in the Room.")
    by_name = {p["name"].strip().lower(): u for u, p in people.items() if p.get("name")}
    rows, unknown = [], []
    for line in rd:
        r = {cols[k]: (v or "").strip() for k, v in line.items() if k in cols}
        if not r.get("name"):
            continue
        u = by_name.get(r["name"].lower())
        if not u:
            unknown.append(r["name"])
            continue
        r.pop("name")
        for k in CREW_FIELDS + CAST_FIELDS:
            if r.get(k):
                r[k] = clean_time(r[k])
        rows.append(dict(r, user=u))
    return {"rows": rows, "unknown": unknown}
