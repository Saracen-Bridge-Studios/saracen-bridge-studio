"""The Room inside the Studio (1.0.8): the local /api/room routes the page uses, against a real hub, with real crypto."""
import io
import time

import pytest
from fastapi.testclient import TestClient

from room_world import World, space_named
from studio.room import service as S
from studio.room.client import RoomClient


@pytest.fixture
def room(tmp_path, monkeypatch):
    """A hub with Tim (an executive) and SHADE; this Studio (STUDIO_HOME) is a new PC that joins through the routes."""
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path / "studio"))
    w = World(tmp_path / "w")
    w.shade = w.tim.create_production("ZZSHADEZZ")
    w.camera = w.tim.add_department(w.shade, "Camera")
    hub_http = TestClient(w.app)
    S.reset_for_tests()
    monkeypatch.setattr(S, "client", lambda hub=None: S._CLIENT or _make(hub_http))
    monkeypatch.setattr(S, "start_live", lambda: None)
    from studio.server import app
    return w, TestClient(app)


def _make(http):
    S._CLIENT = RoomClient(S.folder(), http=http)
    return S._CLIENT


def _join(w, c, tier="crew", name="ZZNINAZZ", dept=None):
    inv = w.tim.invite(w.shade, tier, name, role="1st AC", department=dept or w.camera)
    r = c.post("/api/room/join", json={"invite": f"http://testserver/app/#join={inv['token']}", "name": name}).json()
    assert r == {"stage": "waiting"}
    me = S._CLIENT.device.id
    w.tim.start_check(me)
    words = c.get("/api/room/join").json()["words"]
    p = next(x for x in w.tim.pending() if x["device"]["id"] == me)
    assert p["words"] == words
    w.tim.approve(me)
    assert c.get("/api/room/join").json() == {"stage": "approved"}
    w.tim.sync()
    c.post("/api/room/sync")


def test_a_new_pc_joins_through_the_studio(room):
    w, c = room
    assert c.get("/api/room/state").json()["status"] == "none"
    assert c.get("/api/room/view").status_code == 409            # nothing until it has joined
    _join(w, c)
    v = c.get("/api/room/view").json()
    assert v["production_name"] == "ZZSHADEZZ" and v["me"]["name"] == "ZZNINAZZ" and v["tier"] == "crew"
    assert [s["name"] for s in v["spaces"]] == ["Camera"] and v["my_day"] and not v["can_manage"]


def test_messages_notes_mentions_search_and_files(room):
    w, c = room
    _join(w, c)
    cam = space_named(w.tim, w.shade, "Camera")
    c.post("/api/room/note", json={"spaces": [cam], "title": "Lens test", "body": "Vote by Friday", "status": "Needs review"})
    c.post("/api/room/message", json={"space": cam, "text": "Hello @ZZTIMMARLOWEZZ"})
    sv = c.get(f"/api/room/space/{cam}").json()
    assert sv["messages"][-1]["text"] == "Hello @ZZTIMMARLOWEZZ" and sv["member"]
    v = c.get("/api/room/view").json()
    note = next(n for n in v["board"] if n["title"] == "Lens test")
    assert note["status"] == "Needs review" and note["spaces"] == ["Camera"]
    c.post(f"/api/room/note/{note['id']}", json={"status": "Decision", "pinned": True})
    v = c.get("/api/room/view").json()
    assert v["board"][0]["title"] == "Lens test" and v["board"][0]["status"] == "Decision" and v["board"][0]["pinned"]
    assert c.get(f"/api/room/search?production={w.shade}&q=hello").json()[0]["kind"] == "msg"
    assert any(n["kind"] == "mention" for n in w.tim.sync()["notifications"])
    # a file through the page's upload route, then downloaded through the Studio
    data = b"ZZDAILIESZZ" * 50000
    key = c.post("/api/room/upload", data={"space": cam}, files={"file": ("dailies.mov", io.BytesIO(data))}).json()["key"]
    for _ in range(100):
        if S.UPLOADS[key]["stage"] in ("done", "failed"):
            break
        time.sleep(0.05)
    assert S.UPLOADS[key]["stage"] == "done", S.UPLOADS[key]
    f = c.get(f"/api/room/space/{cam}").json()["files"][0]
    assert f["name"] == "dailies.mov" and f["version"] == 1
    assert c.get(f"/api/room/file/{f['id']}").content == data
    assert not list((S.folder()).rglob("upload.bin"))          # the plaintext temp copy is gone


def test_the_local_cache_holds_no_plaintext(room):
    w, c = room
    _join(w, c)
    cam = space_named(w.tim, w.shade, "Camera")
    w.tim.post([cam], "msg", {"text": "ZZSECRETPLANZZ"})
    c.post("/api/room/sync")
    assert any(m["text"] == "ZZSECRETPLANZZ" for m in c.get(f"/api/room/space/{cam}").json()["messages"])
    blob = b"".join(p.read_bytes() for p in S.folder().rglob("*") if p.is_file())
    for marker in (b"ZZSECRETPLANZZ", b"ZZSHADEZZ", b"ZZTIMMARLOWEZZ"):
        assert marker not in blob, marker


def test_executive_oversight_through_the_studio(room, monkeypatch, tmp_path):
    w, c = room
    # this Studio is the executive's second PC
    inv = w.tim.invite(None, None, "", user=w.tim.me)
    r = c.post("/api/room/join", json={"invite": inv["token"], "name": "Tim"}).json()
    assert r["stage"] == "waiting"
    w.tim.start_check(S._CLIENT.device.id)
    c.get("/api/room/join")
    w.tim.approve(S._CLIENT.device.id)
    assert c.get("/api/room/join").json()["stage"] == "approved"
    w.tim.sync()
    c.post("/api/room/sync")
    cast = space_named(w.tim, w.shade, "Cast")
    lea = w.join(w.tim.invite(w.shade, "cast", "ZZLEAZZ"), "lea")
    pat = w.join(w.tim.invite(w.shade, "producer", "ZZPATZZ"), "pat")
    dm = lea.dm(w.shade, pat.me)
    lea.post([dm], "msg", {"text": "ZZPRIVATEZZ"})
    c.post("/api/room/sync")
    v = c.get("/api/room/view").json()
    assert v["is_exec"] and any(d["id"] == dm and d["oversight"] for d in v["dms"])
    locked = c.get(f"/api/room/space/{dm}").json()
    assert locked["locked_oversight"] and "messages" not in locked
    opened = c.get(f"/api/room/space/{dm}?oversight=true").json()
    assert opened["messages"][0]["text"] == "ZZPRIVATEZZ"
    acc = c.get(f"/api/room/access?production={w.shade}").json()
    assert any("read a space they aren't in" in e["what"] for e in acc["audit"]["entries"])
    assert {t["name"]: t["count"] for t in acc["tiers"]}["Cast"] == 1 and acc["audit"]["intact"]
    assert cast


def test_invite_links_name_the_hub_and_carry_the_token(room):
    from studio.room.routes import _hub_from, _token_from
    assert _token_from("https://room.example.com/app/#join=abc123") == "abc123"
    assert _token_from("https://room.example.com/app/?join=xyz") == "xyz"
    assert _token_from("  plain-token ") == "plain-token"
    assert _hub_from("https://room.example.com/app/#join=abc") == "https://room.example.com"
    assert _hub_from("abc") is None
