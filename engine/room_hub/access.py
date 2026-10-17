"""Who sees what in the Room. The hub applies these rules to everything it sends, even though the content is
encrypted: a space, file, person or production a member can't see never appears anywhere (hidden, not locked).

Tiers are set per production; executive is company-wide.

| Tier | Sees | Can start a conversation with |
|---|---|---|
| executive | every production, space, file and private message (reads outside their own spaces are logged) | everyone |
| producer | every space in their productions except other people's private messages | executives, producers, keys |
| key | their department, heads of department, spaces opened to them | producers, keys, their department's crew |
| crew | their department's channel and posts shared with it | their head of department, their department (the 2nd AD also cast) |
| cast | their own day, the cast channel, posts shared with cast | the 2nd AD, producers |
| guest | only spaces shared with them | people in those spaces |

Contact grants open a line between two named people outside these rules.
"""
from __future__ import annotations

import json
from functools import cached_property

TIERS = ("producer", "key", "crew", "cast", "guest")


class View:
    """Everything one user may see, computed from the store at one moment."""

    def __init__(self, store, user: str):
        self.s = store
        self.user = user
        u = store.one("SELECT * FROM users WHERE id=? AND deleted=0", (user,))
        self.exec = bool(u and u["exec"])
        self.my = {r["production"]: dict(r) for r in store.q("SELECT * FROM memberships WHERE user=?", (user,))}

    # ------------------------------------------------------------ raw tables
    @cached_property
    def productions(self) -> dict:
        return {r["id"]: dict(r) for r in self.s.q("SELECT * FROM productions")}

    @cached_property
    def members(self) -> dict:
        """production -> user -> membership"""
        out: dict = {}
        for r in self.s.q("SELECT m.* FROM memberships m JOIN users u ON u.id=m.user WHERE u.deleted=0"):
            out.setdefault(r["production"], {})[r["user"]] = dict(r)
        return out

    @cached_property
    def execs(self) -> set:
        return {r["id"] for r in self.s.q("SELECT id FROM users WHERE exec=1 AND deleted=0")}

    @cached_property
    def spaces(self) -> dict:
        out = {r["id"]: dict(r, audience=json.loads(r["audience"] or "{}")) for r in self.s.q("SELECT * FROM spaces")}
        for r in self.s.q("SELECT space, user FROM space_members"):
            if r["space"] in out:
                out[r["space"]].setdefault("explicit", set()).add(r["user"])
        return out

    @cached_property
    def grants(self) -> list:
        return [dict(r) for r in self.s.q("SELECT * FROM grants WHERE revoked=0")]

    # ------------------------------------------------------------ productions
    def productions_visible(self) -> set:
        if self.exec:
            return set(self.productions)
        return {p for p in self.my if p in self.productions}

    def tier(self, p: str, user: str | None = None) -> str | None:
        user = user or self.user
        if user in self.execs:
            return "executive"
        m = self.members.get(p, {}).get(user)
        return m["tier"] if m else None

    # ------------------------------------------------------------ spaces
    def space_members(self, sid: str) -> set:
        """The members of a space: they sync its content and get its keys. Executives are not members unless added;
        they can still open any space (and every such read is logged)."""
        sp = self.spaces.get(sid)
        if not sp:
            return set()
        p, kind, aud = sp["production"], sp["kind"], sp["audience"]
        mem = self.members.get(p, {})
        producers = {u for u, m in mem.items() if m["tier"] == "producer"}
        explicit = sp.get("explicit", set())
        if kind == "directory":
            return set(mem)
        if kind == "dm":
            return set(explicit)
        if kind == "personal":
            return ({sp["owner"]} if sp["owner"] in mem else set()) | producers
        out = set(explicit) | producers
        tiers, depts = set(aud.get("tiers", [])), set(aud.get("departments", []))
        for u, m in mem.items():
            if m["tier"] in tiers and (not depts or m["department"] in depts):
                out.add(u)
            if aud.get("second_ad") and m["second_ad"]:
                out.add(u)
        return {u for u in out if u in mem or u in self.execs}

    def can_see_space(self, sid: str) -> bool:
        sp = self.spaces.get(sid)
        if not sp or sp["production"] not in self.productions_visible():
            return False
        if self.exec:
            return True
        return self.user in self.space_members(sid)

    def is_member(self, sid: str) -> bool:
        return self.user in self.space_members(sid)

    def visible_spaces(self) -> list[str]:
        return [s for s in self.spaces if self.can_see_space(s)]

    def key_recipients(self, sid: str) -> set:
        """Users whose devices get this space's keys: its members, plus every executive."""
        return self.space_members(sid) | self.execs

    # ------------------------------------------------------------ people
    def can_reach(self, p: str, other: str) -> bool:
        """May this user start a private conversation with `other` in production p?"""
        if other == self.user:
            return False
        if self.exec:
            return other in self.members.get(p, {}) or other in self.execs
        me, them = self.members.get(p, {}).get(self.user), self.members.get(p, {}).get(other)
        if not me:
            return False
        for g in self.grants:
            if g["production"] == p and {g["a"], g["b"]} == {self.user, other}:
                return True
        if other in self.execs:
            return me["tier"] == "producer"
        if not them:
            return False
        t, o = me["tier"], them["tier"]
        same_dept = bool(me["department"]) and me["department"] == them["department"]
        if t == "producer":
            return o in ("producer", "key")
        if t == "key":
            return o in ("producer", "key") or (o == "crew" and same_dept)
        if me["second_ad"] and o == "cast":            # the 2nd AD looks after cast (pickups, sides)
            return True
        if t == "crew":
            return o in ("key", "crew") and same_dept
        if t == "cast":
            return o == "producer" or bool(them["second_ad"])
        if t == "guest":
            return any(other in self.space_members(s) and self.user in self.space_members(s)
                       for s in self.spaces if self.spaces[s]["production"] == p and self.spaces[s]["kind"] != "directory")
        return False

    def visible_people(self) -> dict:
        """production -> set of users this user can see. Others don't appear in lists, search, counts or names."""
        out: dict = {}
        for p in self.productions_visible():
            mem = self.members.get(p, {})
            if self.exec:
                out[p] = set(mem) | self.execs
                continue
            seen = {self.user}
            seen |= {u for u in mem if self.can_reach(p, u)}
            for sid, sp in self.spaces.items():
                if sp["production"] == p and sp["kind"] not in ("directory",) and self.is_member(sid):
                    seen |= self.space_members(sid)
            # executives and anyone else who wrote something this user can read
            seen |= self.authors_in(p)
            if self.tier(p) == "producer":
                seen |= self.execs
            out[p] = seen
        return out

    def authors_in(self, p: str) -> set:
        sids = [s for s, sp in self.spaces.items() if sp["production"] == p and sp["kind"] != "directory" and self.is_member(s)]
        if not sids:
            return set()
        qs = ",".join("?" * len(sids))
        return {r["author"] for r in self.s.q(
            f"SELECT DISTINCT i.author FROM items i JOIN item_spaces x ON x.item=i.id WHERE x.space IN ({qs})", sids)}

    def can_manage(self, p: str) -> bool:
        """Create spaces, invite, add people to spaces, publish call sheets."""
        return self.exec or self.tier(p) == "producer"
