"""Whoever starts a production hosts it (1.0.8.1): their Studio runs the Room on their own PC, with no web address to
type, and a Studio in several people's productions (Jon's on Jon's PC, Colin's on Colin's) sees them all in one
switcher, with every action going to the PC that holds it."""
import socket

import httpx
import pytest
from fastapi.testclient import TestClient

from room_world import World
from studio.room import host as H
from studio.room import service as S


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def studio(tmp_path, monkeypatch):
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path / "studio"))
    monkeypatch.setattr(S, "start_live", lambda: None)
    S.reset_for_tests()
    from studio.server import app
    yield TestClient(app)
    H.stop()
    S.reset_for_tests()
    S.HTTP_FACTORY = None


def test_starting_a_production_hosts_it_on_this_pc(studio, monkeypatch):
    port = free_port()
    assert port != 8799
    monkeypatch.setattr(H, "PORT", port)
    monkeypatch.setattr(H, "_livekit_bin", lambda: None)
    r = studio.post("/api/room/host", json={"name": "ZZJONZZ", "production": "ZZJONSFILMZZ"})
    assert r.status_code == 200, r.text
    pid = r.json()["id"]
    assert r.json()["address"] == f"http://{H.lan_ip()}:{port}"
    st = studio.get("/api/room/state").json()
    assert st["status"] == "approved" and st["host"]["hosting"] and st["host"]["enabled"]
    v = studio.get("/api/room/view").json()
    assert [(p["id"], p["here"]) for p in v["productions"]] == [(pid, True)] and v["is_exec"]
    # the hub answers on the network address the invite carries; the Studio itself uses 127.0.0.1
    assert httpx.get(f"http://127.0.0.1:{port}/api/health", trust_env=False).json()["founded"] is True
    link = studio.post("/api/room/invite", json={"production": pid, "tier": "crew", "name": "ZZKITZZ"}).json()["link"]
    assert link.startswith(f"http://{H.lan_ip()}:{port}/app/#join=")
    # a second production goes on the same PC, with no name or code asked again
    r2 = studio.post("/api/room/productions", json={"name": "ZZSECONDZZ"})
    assert r2.status_code == 200, r2.text
    assert len(studio.get("/api/room/view").json()["productions"]) == 2
    assert H.founder_token() is None                      # the one-time founder code can't be had again


def test_a_studio_in_two_hosts_productions_sees_both_and_each_action_goes_to_its_host(studio, tmp_path):
    jon, colin = World(tmp_path / "jon"), World(tmp_path / "colin")
    hubs = {"http://jon.test": TestClient(jon.app), "http://colin.test": TestClient(colin.app)}
    S.HTTP_FACTORY = lambda hub: hubs[hub.rstrip("/")]
    jp = jon.tim.create_production("ZZJONPRODZZ")
    cp = colin.tim.create_production("ZZCOLINPRODZZ")

    def join(world, base, prod):
        inv = world.tim.invite(prod, "producer", "ZZTIMZZ", role="Producer")
        r = studio.post("/api/room/join", json={"invite": f"{base}/app/#join={inv['token']}", "name": "ZZTIMZZ"})
        assert r.status_code == 200, r.text
        dev = next(iter(S.clients("pending"))).device.id
        world.tim.start_check(dev)
        words = studio.get("/api/room/join").json()["words"]
        assert next(p for p in world.tim.pending() if p["device"]["id"] == dev)["words"] == words
        world.tim.approve(dev)
        world.tim.sync()
        assert studio.get("/api/room/join").json()["stage"] == "approved"

    join(jon, "http://jon.test", jp)
    join(colin, "http://colin.test", cp)
    v = studio.get(f"/api/room/view?production={cp}").json()
    names = sorted(p["name"] for p in v["productions"])
    assert names == ["ZZCOLINPRODZZ", "ZZJONPRODZZ"] and v["production"] == cp
    # a message in Colin's production goes to Colin's PC and nowhere else
    office = next(s["id"] for s in v["spaces"] if s["name"] == "Production office")
    studio.get(f"/api/room/view?production={jp}")             # the page was last on Jon's production
    assert studio.post("/api/room/message", json={"space": office, "text": "ZZFORCOLINZZ"}).status_code == 200
    colin.tim.sync()
    assert any((it["payload"] or {}).get("text") == "ZZFORCOLINZZ" for it in colin.tim.items.values())
    assert b"ZZFORCOLINZZ" not in b"".join(f.read_bytes() for f in jon.store.root.rglob("*") if f.is_file())
    assert jon.store.one("SELECT COUNT(*) n FROM items WHERE production=?", (cp,))["n"] == 0
