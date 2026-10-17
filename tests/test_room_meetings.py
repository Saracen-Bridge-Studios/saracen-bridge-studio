"""Voice huddles and meetings (1.0.8): tokens match stage and audience, executives promote and demote live, the
75-person cap, and the media key never reaches the hub or LiveKit. LiveKit's room service is stood in for here;
the full flow was also run against a real LiveKit server in a browser (see the CHANGELOG)."""
import json

import httpx
import jwt
import pytest

from room_world import shade, space_named
from studio.room import meetings as M


class FakeLiveKit:
    def __init__(self):
        self.calls, self.here = [], {}

    def handler(self, request: httpx.Request):
        method = request.url.path.rsplit("/", 1)[-1]
        body = json.loads(request.content or b"{}")
        claims = jwt.decode(request.headers["Authorization"][7:], "secret", algorithms=["HS256"])
        assert claims["video"]["roomAdmin"] and claims["iss"] == "devkey"
        self.calls.append((method, body))
        if method == "ListParticipants":
            return httpx.Response(200, json={"participants": [{"identity": u} for u in self.here.get(body["room"], [])]})
        if method == "ListRooms":
            assert claims["video"]["roomList"]
            return httpx.Response(200, json={"rooms": [{"name": r, "num_participants": len(self.here.get(r, []))}
                                                       for r in body["names"] if r in self.here]})
        return httpx.Response(200, json={})


@pytest.fixture(scope="module")
def w(tmp_path_factory):
    fake = FakeLiveKit()
    world = shade(tmp_path_factory.mktemp("meet"), livekit={"url": "http://livekit.test", "public_url": "wss://media.example",
                                                              "key": "devkey", "secret": "secret",
                                                              "http": httpx.Client(transport=httpx.MockTransport(fake.handler))})
    world.fake = fake
    return world


def claims(t):
    return jwt.decode(t["token"], "secret", algorithms=["HS256"])["video"]


def test_meeting_tokens_put_executives_on_stage_and_others_in_the_audience(w):
    office, hods = space_named(w.pat, w.shade, "Production office"), space_named(w.pat, w.shade, "Heads of department")
    mid = M.start(w.pat, w.shade, [office, hods], "meeting", "ZZBOARDROOMZZ", "2026-10-20T18:00:00+00:00", 60)
    assert ("CreateRoom", {"name": mid, "max_participants": 75, "empty_timeout": 600}) in w.fake.calls
    for c in (w.tim, w.dp, w.gaffer):
        c.sync()
    t_exec, t_key = M.join(w.tim, mid), M.join(w.dp, mid)
    assert claims(t_exec)["canPublish"] is True and t_exec["on_stage"] and t_exec["can_direct"]
    assert claims(t_key)["canPublish"] is False and claims(t_key)["canSubscribe"] is True and not t_key["can_direct"]
    assert claims(t_key)["room"] == mid and t_key["url"] == "wss://media.example"
    assert jwt.decode(t_key["token"], "secret", algorithms=["HS256"])["sub"] == w.dp.me     # an id, never a name
    assert t_exec["key"] == t_key["key"] and len(t_key["key"]) >= 40                          # one media key, from the Room
    with pytest.raises(Exception):
        M.join(w.gaffer, mid)                    # crew aren't in the spaces it was scheduled for


def test_executives_promote_and_demote_live(w):
    mid = next(m["id"] for m in M.listing(w.tim, w.shade, {}) if m["title"] == "ZZBOARDROOMZZ")
    w.fake.here[mid] = [w.tim.me, w.dp.me]
    w.tim._req("POST", f"/api/meetings/{mid}/stage", json={"user": w.dp.me, "on": True})
    assert ("UpdateParticipant", {"room": mid, "identity": w.dp.me, "permission": {"can_publish": True, "can_subscribe": True,
            "can_publish_data": True, "can_update_metadata": True}}) in w.fake.calls
    assert claims(M.join(w.dp, mid))["canPublish"] is True              # a later token keeps the stage
    w.tim._req("POST", f"/api/meetings/{mid}/stage", json={"user": w.dp.me, "on": False})
    assert w.fake.calls[-1][1]["permission"]["can_publish"] is False
    with pytest.raises(Exception, match="Only an executive"):
        w.pat._req("POST", f"/api/meetings/{mid}/stage", json={"user": w.dp.me, "on": True})
    assert any(e["action"] == "brought someone on stage" for e in w.tim.audit()["entries"])


def test_the_75_person_cap(w):
    mid = next(m["id"] for m in M.listing(w.tim, w.shade, {}) if m["title"] == "ZZBOARDROOMZZ")
    w.fake.here[mid] = [f"u_{i}" for i in range(74)] + [w.dp.me]
    with pytest.raises(Exception, match="full"):
        M.join(w.pat, mid)
    assert claims(M.join(w.dp, mid))["roomJoin"]                       # someone already in can rejoin


def test_huddles_let_everyone_in_the_space_talk(w):
    cam = space_named(w.dp, w.shade, "ZZCAMERAZZ")
    mid = M.start(w.dp, w.shade, [cam], "huddle", "Huddle")
    w.gaffer.sync()
    assert claims(M.join(w.gaffer, mid))["canPublish"] is True
    assert ("CreateRoom", {"name": mid, "max_participants": 25, "empty_timeout": 600}) in w.fake.calls
    with pytest.raises(Exception):
        M.join(w.lea, mid)


def test_the_media_key_never_reaches_the_hub(w):
    keys = [it["payload"]["media_key"] for c in (w.tim,) for it in c.items.values() if it["h"]["kind"] in ("meeting", "huddle")]
    blob = b"".join(f.read_bytes() for f in w.store.root.rglob("*") if f.is_file())
    assert keys and all(k.encode() not in blob for k in keys)
    assert all(k not in json.dumps(w.fake.calls) for k in keys)


def test_a_calendar_invite_for_a_scheduled_meeting(w):
    mid = next(m["id"] for m in M.listing(w.dp, w.shade, {}) if m["title"] == "ZZBOARDROOMZZ")
    ics = M.ics(w.dp, mid, "SHADE")
    assert "DTSTART:20261020T180000Z" in ics and "DTEND:20261020T190000Z" in ics and "SUMMARY:ZZBOARDROOMZZ (SHADE)" in ics


def test_listings_say_how_many_are_in_a_call_but_not_who(w):
    cam = space_named(w.dp, w.shade, "ZZCAMERAZZ")
    mid = next(m["id"] for m in M.listing(w.dp, w.shade, {}) if m["kind"] == "huddle")
    w.fake.here[mid] = [w.dp.me, w.gaffer.me]
    rows = {m["id"]: m for m in w.gaffer._req("GET", "/api/meetings", params={"production": w.shade})}
    assert rows[mid]["here"] == 2 and set(rows[mid]) == {"id", "item", "kind", "created", "here"}
    assert any(c[0] == "ListRooms" for c in w.fake.calls) and cam


def test_a_media_server_that_is_down_gets_a_plain_answer(tmp_path):
    def down(request):
        raise httpx.ConnectError("refused", request=request)
    world = shade(tmp_path, livekit={"url": "http://livekit.test", "key": "devkey", "secret": "secret",
                                     "http": httpx.Client(transport=httpx.MockTransport(down))})
    cam = space_named(world.dp, world.shade, "ZZCAMERAZZ")
    with pytest.raises(Exception, match="media server isn't answering"):
        M.start(world.dp, world.shade, [cam], "huddle", "Huddle")
    assert world.dp._req("GET", "/api/meetings", params={"production": world.shade}) == []
