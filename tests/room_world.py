"""A Room with real crypto for the tests: a hub in a temp folder and one RoomClient per device, every one joined
with the safety-word check. Names, messages and files use marker strings so the no-plaintext scan can look for them."""
from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from room_hub.__main__ import founder_token
from room_hub.app import create_app
from studio.room.client import RoomClient


class World:
    def __init__(self, tmp: Path, **app_kw):
        self.tmp = Path(tmp)
        self.app = create_app(self.tmp / "hub", **app_kw)
        self.store = self.app.state.store
        self.n = 0
        self.tim = self.client("tim")
        self.tim.bootstrap(founder_token(self.store), "ZZTIMMARLOWEZZ", "Executive producer")

    def client(self, name: str) -> RoomClient:
        self.n += 1
        return RoomClient(self.tmp / f"dev_{self.n}_{name}", http=TestClient(self.app))

    def join(self, invite: dict, name: str, approver: RoomClient | None = None) -> RoomClient:
        """A new device joins with the invite; the approver (an executive) checks words and approves."""
        approver = approver or self.tim
        c = self.client(name)
        c.join(invite["token"], name)
        assert c.join_progress() == {"stage": "waiting"}
        approver.start_check(c.device.id)
        words = c.join_progress()
        assert words["stage"] == "words"
        p = next(x for x in approver.pending() if x["device"]["id"] == c.device.id)
        assert p["words"] == words["words"], "safety words differ"
        approver.approve(c.device.id)
        assert c.join_progress() == {"stage": "approved"}
        approver.sync()
        c.sync()
        return c


def shade(tmp: Path, **app_kw) -> World:
    """SHADE with a producer, a camera key and crew, a grip, a 2nd AD, a cast member and a guest; plus a second
    production (NIGHT FERRY) with its own producer."""
    w = World(tmp, **app_kw)
    t = w.tim
    w.shade = t.create_production("ZZSHADEZZ")
    w.camera = t.add_department(w.shade, "ZZCAMERAZZ")
    w.grips = t.add_department(w.shade, "ZZGRIPSZZ")
    w.ad = t.add_department(w.shade, "ZZADDEPTZZ")
    inv = lambda tier, name, dept="", second_ad=False: t.invite(w.shade, tier, name, role=name + " role", department=dept,
                                                                  second_ad=second_ad)
    w.pat = w.join(inv("producer", "ZZPATPRODUCERZZ"), "pat")
    w.dp = w.join(inv("key", "ZZDPKEYZZ", w.camera), "dp")
    w.gaffer = w.join(inv("crew", "ZZGAFFERZZ", w.camera), "gaffer")
    w.grip = w.join(inv("crew", "ZZGRIPZZ", w.grips), "grip")
    w.alex = w.join(inv("crew", "ZZALEX2NDADZZ", w.ad, True), "alex")
    # producers invite too; an executive approves
    w.lea = w.join(w.pat.invite(w.shade, "cast", "ZZLEACASTZZ", role="ZZROLEMARAZZ"), "lea")
    w.sam = w.join(inv("guest", "ZZSAMGUESTZZ"), "sam")
    w.ferry = t.create_production("ZZNIGHTFERRYZZ")
    w.quinn = w.join(t.invite(w.ferry, "producer", "ZZQUINNZZ"), "quinn")
    for c in (t, w.pat, w.dp, w.gaffer, w.grip, w.alex, w.lea, w.sam, w.quinn):
        c.sync()
    return w


def space_named(c: RoomClient, production: str, name: str) -> str:
    names = c.names(production)["space"]
    for sid, v in names.items():
        if v.get("name") == name:
            return sid
    raise KeyError(name)
