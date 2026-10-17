"""Members & access: what an executive (or a producer, for their own production) sees about who is in the Room."""
from __future__ import annotations

import time

from . import service as S

KIND = {"read a space they aren't in": "OVERSIGHT", "opened a file in a space they aren't in": "OVERSIGHT",
        "granted contact": "ACCESS", "revoked contact": "ACCESS", "changed who is in a space": "ACCESS",
        "made an executive": "ACCESS", "removed an executive": "ACCESS", "set a member's tier": "ACCESS",
        "changed a space's keys": "KEYS"}


def _all_names(c) -> dict:
    """user, space and production ids -> names, from every production directory this device can read."""
    out = {}
    for pr in c.snapshot.get("productions", []):
        n = c.names(pr["id"])
        for k in ("person", "space", "production", "department"):
            for sid, v in n[k].items():
                if v.get("name"):
                    out[sid] = v["name"]
    return out


def _say(e: dict, names: dict) -> str:
    nm = lambda x: names.get(x) or "someone" if x else ""
    t = e.get("target") or {}
    who = nm(e["actor"]) if e["actor"] != "hub" else "The Room"
    bits = []
    if t.get("user"):
        bits.append(nm(t["user"]))
    if t.get("space"):
        bits.append(names.get(t["space"]) or ("a private conversation" if t.get("kind") == "dm" else "a space"))
    if t.get("a") and t.get("b"):
        bits.append(f"{nm(t['a'])} ↔ {nm(t['b'])}")
    if t.get("tier"):
        bits.append(S.TIER_LABEL.get(t["tier"], t["tier"]))
    if t.get("count") is not None:
        bits.append(f"{t['count']} reminded")
    where = names.get(e.get("production") or "", "")
    return f"{who} {e['action']}" + (": " + ", ".join(b for b in bits if b) if bits else "") + (f" ({where})" if where else "")


def view(c, production: str) -> dict:
    ppl = S.people(c, production)
    names = c.names(production)
    tier = S.my_tier(c, production)
    if tier not in ("executive", "producer"):
        raise S.RoomError("Only producers and executives see Members & access.")
    devices: dict = {}
    for d in c.snapshot.get("devices", []):
        if d["status"] == "approved":
            devices.setdefault(d["record"]["r"]["user"], []).append(d["record"]["r"]["id"])
    spaces_of: dict = {}
    for sp in c.snapshot.get("spaces", []):
        if sp["production"] == production and sp["kind"] in ("channel",):
            for u in sp["members"]:
                spaces_of.setdefault(u, []).append((names["space"].get(sp["id"]) or {}).get("name", "a space"))
    members = [dict(p, spaces=sorted(spaces_of.get(p["user"], [])), devices=len(devices.get(p["user"], [])),
                    device_ids=devices.get(p["user"], [])) for p in ppl.values()]
    members.sort(key=lambda m: (list(S.TIER_LABEL).index(m["tier"]) if m["tier"] in S.TIER_LABEL else 9, m["name"].lower()))
    counts = {t: sum(1 for m in members if m["tier"] == t) for t in S.TIER_LABEL}
    out = {"production": production, "can_approve": c.is_exec, "is_exec": c.is_exec,
           "tiers": [{"tier": t, "name": S.TIER_LABEL[t], "count": counts.get(t, 0), "sees": S.TIER_SEES[t][0],
                      "reach": S.TIER_SEES[t][1]} for t in S.TIER_LABEL],
           "members": members, "departments": [{"id": k, "name": v.get("name", "")} for k, v in names["department"].items()],
           "oversight": S.OVERSIGHT, "pending": [], "grants": [], "audit": None, "invites": []}
    allnames = _all_names(c)
    for g in c.snapshot.get("grants", []):
        if g["production"] == production:
            out["grants"].append({"id": g["id"], "pair": f"{allnames.get(g['a'], 'someone')} ↔ {allnames.get(g['b'], 'someone')}",
                                  "by": "Granted by " + allnames.get(g["granted_by"], "an executive")})
    if c.is_exec:
        for p in c.pending():
            inv = p.get("invite") or {}
            det = p.get("details") or {}
            out["pending"].append({
                "device": p["device"]["id"], "user": p["user"], "name": det.get("name") or "New device",
                "role": det.get("role") or "",
                "tier": S.TIER_LABEL.get(inv.get("tier"), "Company") if inv.get("tier") else "Extra device or new executive",
                "department": (names["department"].get(inv.get("department")) or {}).get("name", "") if inv.get("department") else "",
                "production": allnames.get(inv.get("production") or "", ""),
                "invited_by": allnames.get(inv.get("created_by") or "", "an executive"),
                "since": p["created"], "words": p["words"], "problem": p.get("problem"),
                "checking": bool(p["approver"]), "mine": p["approver"] == c.device.id,
                "waiting_for_them": bool(p["approver"] == c.device.id and not p["n_joiner"])})
        a = c.audit()
        out["audit"] = {"intact": a["intact"], "entries": [
            {"when": e["ts"], "what": _say(e, allnames), "kind": KIND.get(e["action"], "MEMBER" if "device" in e["action"]
                                                                          or "member" in e["action"] or "invite" in e["action"]
                                                                          else "ROOM")}
            for e in a["entries"][:300]]}
    for inv in c._req("GET", "/api/invites"):
        if inv["production"] == production:
            det = c._open_dir_item(inv["details"], production) if inv.get("details") else None
            out["invites"].append({"id": inv["id"], "name": (det or {}).get("name", "Someone"), "tier": S.TIER_LABEL.get(inv["tier"], ""),
                                   "status": "Joining" if inv["status"] == "joining" else "Not used yet",
                                   "expires": inv["expires"], "days_left": max(0, int((inv["expires"] - time.time()) // 86400))})
    return out
