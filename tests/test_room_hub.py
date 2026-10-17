"""The Room (1.0.8): access rules, joining, encryption and the audit log, with real crypto against a real hub."""
import json
import time

import pytest

import room_crypto as rc
from room_hub.retention import purge
from studio.room.client import RoomError

from room_world import World, shade, space_named


@pytest.fixture(scope="module")
def w(tmp_path_factory):
    return shade(tmp_path_factory.mktemp("room"))


def visible_space_names(c, production):
    names = c.names(production)["space"]
    return {names.get(sp["id"], {}).get("name") or sp["kind"] for sp in c.snapshot["spaces"] if sp["production"] == production}


def visible_people(c, production):
    people = c.names(production)["person"]
    return {people.get(p["user"], {}).get("name") for p in c.snapshot["people"] if p["production"] == production}


# ------------------------------------------------------------------ the permission matrix
def test_each_tier_sees_its_own_spaces_and_nothing_else(w):
    s = w.shade
    assert visible_space_names(w.pat, s) == {"directory", "Production office", "Heads of department", "Cast",
                                            "ZZCAMERAZZ", "ZZGRIPSZZ", "ZZADDEPTZZ", "personal"}
    assert visible_space_names(w.dp, s) == {"directory", "Heads of department", "ZZCAMERAZZ", "personal"}
    assert visible_space_names(w.gaffer, s) == {"directory", "ZZCAMERAZZ", "personal"}
    assert visible_space_names(w.grip, s) == {"directory", "ZZGRIPSZZ", "personal"}
    assert visible_space_names(w.alex, s) == {"directory", "ZZADDEPTZZ", "Cast", "personal"}
    assert visible_space_names(w.lea, s) == {"directory", "Cast", "personal"}
    assert visible_space_names(w.sam, s) == {"directory", "personal"}
    # personal spaces: only your own (producers see everyone's)
    assert sum(sp["kind"] == "personal" for sp in w.lea.snapshot["spaces"]) == 1
    assert sum(sp["kind"] == "personal" for sp in w.pat.snapshot["spaces"]) == 7     # one per member


def test_other_productions_are_hidden_entirely(w):
    for c in (w.pat, w.dp, w.gaffer, w.lea, w.sam):
        assert [p["id"] for p in c.snapshot["productions"]] == [w.shade]
        assert all(sp["production"] == w.shade for sp in c.snapshot["spaces"])
        assert all(p["production"] == w.shade for p in c.snapshot["people"])
    assert [p["id"] for p in w.quinn.snapshot["productions"]] == [w.ferry]
    assert {p["id"] for p in w.tim.snapshot["productions"]} == {w.shade, w.ferry}
    # nor can anyone fetch a hidden space by id
    camera = space_named(w.tim, w.shade, "ZZCAMERAZZ")
    for c in (w.quinn, w.lea, w.grip):
        with pytest.raises(RoomError):
            c._req("GET", f"/api/spaces/{camera}/items")


def test_people_lists_follow_the_rules(w):
    s = w.shade
    assert "ZZGAFFERZZ" not in visible_people(w.lea, s)           # cast never see crew
    assert "ZZGRIPZZ" not in visible_people(w.lea, s)
    assert {"ZZALEX2NDADZZ", "ZZPATPRODUCERZZ"} <= visible_people(w.lea, s)
    assert "ZZGRIPZZ" not in visible_people(w.gaffer, s)           # other departments' crew stay hidden
    assert "ZZLEACASTZZ" not in visible_people(w.gaffer, s)
    assert visible_people(w.sam, s) <= {"ZZSAMGUESTZZ", "ZZPATPRODUCERZZ", None}
    assert {"ZZGAFFERZZ", "ZZGRIPZZ", "ZZLEACASTZZ", "ZZSAMGUESTZZ"} <= visible_people(w.pat, s)
    assert "ZZQUINNZZ" not in visible_people(w.pat, s)


def test_who_can_start_a_conversation(w):
    s = w.shade
    u = {n: getattr(w, n).me for n in ("pat", "dp", "gaffer", "grip", "alex", "lea", "sam")}
    ok = [("lea", "alex"), ("lea", "pat"), ("gaffer", "dp"), ("dp", "pat"), ("pat", "dp")]
    no = [("lea", "gaffer"), ("gaffer", "grip"), ("grip", "dp"), ("gaffer", "pat"), ("sam", "gaffer"), ("lea", "dp")]
    for a, b in ok:
        assert getattr(w, a).dm(s, u[b]).startswith("s_")
    for a, b in no:
        with pytest.raises(RoomError, match="can't start a conversation"):
            getattr(w, a).dm(s, u[b])
    with pytest.raises(RoomError):
        w.gaffer.dm(s, w.tim.me)                                   # crew can't message executives
    # a contact grant opens one line, and records who granted it
    g = w.tim.grant_contact(s, u["lea"], u["gaffer"])
    w.lea.sync()
    assert w.lea.dm(s, u["gaffer"]).startswith("s_")
    assert any(e["action"] == "granted contact" and e["target"]["grant"] == g for e in w.tim.audit()["entries"])


def test_content_reaches_only_the_spaces_it_was_shared_with(w):
    s = w.shade
    cam = space_named(w.pat, s, "ZZCAMERAZZ")
    cast = space_named(w.pat, s, "Cast")
    w.gaffer.post([cam], "msg", {"text": "ZZCAMERASECRETZZ"})
    w.pat.post([cam, cast], "note", {"title": "ZZSHAREDNOTEZZ", "status": "Open"})
    for c in (w.dp, w.gaffer, w.grip, w.lea, w.alex, w.sam, w.pat):
        c.sync()
    texts = lambda c: {json.dumps(i["payload"]) for i in c.items.values() if i["payload"]}
    assert any("ZZCAMERASECRETZZ" in t for t in texts(w.dp))
    assert not any("ZZCAMERASECRETZZ" in t for t in texts(w.lea) | texts(w.grip) | texts(w.sam))
    assert any("ZZSHAREDNOTEZZ" in t for t in texts(w.lea)) and any("ZZSHAREDNOTEZZ" in t for t in texts(w.gaffer))
    assert not any("ZZSHAREDNOTEZZ" in t for t in texts(w.grip))
    # crew can't post to a space they can't see
    with pytest.raises(RoomError):
        w.grip._req("POST", "/api/items", json={"item": rc.seal_item({"id": rc.new_id("m_"), "kind": "msg", "prod": s, "ts": 1},
                                                                      {"t": "x"}, {cam: (1, rc.new_key())}, w.grip.device)})


def test_mentions_never_notify_someone_who_cant_see_the_space(w):
    cam = space_named(w.gaffer, w.shade, "ZZCAMERAZZ")
    before = len(w.lea.sync()["notifications"])
    w.gaffer.post([cam], "msg", {"text": "hi"}, mentions=[w.lea.me, w.dp.me])
    assert len(w.lea.sync()["notifications"]) == before
    assert any(n["kind"] == "mention" for n in w.dp.sync()["notifications"])


def test_cast_cannot_publish_call_sheets_or_change_names(w):
    cast = space_named(w.lea, w.shade, "Cast")
    with pytest.raises(RoomError, match="call sheets"):
        w.lea.post([cast], "callsheet", {"day": 1})
    with pytest.raises(RoomError):
        w.lea.post([w.lea.directory_space(w.shade)["id"]], "person", {"name": "x"}, subject=w.lea.me)


# ------------------------------------------------------------------ joining
def test_an_unapproved_device_gets_nothing(w):
    inv = w.tim.invite(w.shade, "crew", "ZZWAITINGZZ", department=w.camera)
    c = w.client("waiting")
    c.join(inv["token"])
    for path in ("/api/sync", "/api/audit", "/api/pending", "/api/invites"):
        with pytest.raises(RoomError, match="waiting for an executive|Only an executive"):
            c._req("GET", path)
    with pytest.raises(RoomError):
        c._req("POST", "/api/items", json={"item": {}})
    w.tim.decline(c.device.id)


def test_a_hub_that_swaps_keys_is_caught_by_the_words(tmp_path):
    w = World(tmp_path)
    p = w.tim.create_production("P")
    inv = w.tim.invite(p, "crew", "X")
    c = w.client("victim")
    c.join(inv["token"])
    w.tim.start_check(c.device.id)
    joiner_words = c.join_progress()["words"]
    # the hub (an attacker) shows the executive its own keys for the waiting device, with a commitment and nonce
    # that match them, hoping the executive approves its keys instead
    evil, n_evil = rc.Device(), b"\x01" * 32
    real = w.tim._req

    def lying_hub(method, path, **kw):
        out = real(method, path, **kw)
        if path == "/api/pending":
            for x in out:
                if x["device"]["id"] == c.device.id:
                    x["device"].update(x=evil.x_pk, ed=evil.ed_pk)
                    x["commit"], x["n_joiner"] = rc.commitment(evil.public(), n_evil), rc.b64e(n_evil)
        return out
    w.tim._req = lying_hub
    exec_words = next(x for x in w.tim.pending() if x["device"]["id"] == c.device.id)["words"]
    assert exec_words and joiner_words != exec_words


def test_a_hub_that_lies_about_the_founder_is_caught_by_the_words(tmp_path):
    w = World(tmp_path)
    p = w.tim.create_production("P")
    inv = w.tim.invite(p, "crew", "X")
    c = w.client("victim")
    r = c.join(inv["token"])
    fake = rc.Device()
    c.state["join_founder"] = rc.device_record(fake.public(), "u_fake", fake)   # what a lying hub would hand over
    w.tim.start_check(c.device.id)
    jw = c.join_progress()["words"]
    ew = next(x for x in w.tim.pending() if x["device"]["id"] == c.device.id)["words"]
    assert jw != ew and r["founder"]["r"]["id"] == w.tim.device.id


def test_safety_words_are_three_words_and_change_with_any_input():
    a, b, f = rc.Device(), rc.Device(), rc.Device()
    n1, n2 = b"\x00" * 32, b"\x01" * 32
    base = rc.safety_words(a.public(), b.public(), f.ed_pk, n1, n2)
    assert len(base) == 3 and all(x in rc.WORDS for x in base)
    assert base != rc.safety_words(a.public(), b.public(), f.ed_pk, n2, n2)
    assert base != rc.safety_words(rc.Device().public(), b.public(), f.ed_pk, n1, n2)
    assert base != rc.safety_words(a.public(), b.public(), rc.Device().ed_pk, n1, n2)


# ------------------------------------------------------------------ encryption
def test_the_hub_holds_no_plaintext(w):
    w.lea.upload(space_named(w.lea, w.shade, "Cast"), "ZZFILENAMEZZ.pdf", b"ZZFILECONTENTZZ" * 1000)
    blob = b""
    for f in sorted(w.store.root.rglob("*")):
        if f.is_file():
            blob += f.read_bytes()
    for marker in ("ZZTIMMARLOWEZZ", "ZZSHADEZZ", "ZZCAMERAZZ", "ZZGAFFERZZ", "ZZLEACASTZZ", "ZZROLEMARAZZ",
                   "ZZCAMERASECRETZZ", "ZZSHAREDNOTEZZ", "ZZFILENAMEZZ", "ZZFILECONTENTZZ", "ZZNIGHTFERRYZZ"):
        assert marker.encode() not in blob, marker
        assert rc.b64e(marker.encode()).encode()[:12] not in blob, marker


def test_a_removed_device_cannot_read_anything_new(w):
    cam = space_named(w.dp, w.shade, "ZZCAMERAZZ")
    old_keys = dict(w.gaffer.keys)
    w.tim.revoke_device(w.gaffer.device.id)                 # the executive's device rotates the keys right away
    assert w.dp.sync() and w.dp.space(cam)["epoch"] >= 2
    item = w.dp.post([cam], "msg", {"text": "ZZAFTERREMOVALZZ"})
    raw = item["raw"]
    s, e = raw["h"]["spaces"][0]
    assert (s, e) not in old_keys                           # the removed device never got the new key
    for k in old_keys.values():
        with pytest.raises(Exception):
            rc.open_item(raw, s, k)
    with pytest.raises(RoomError):
        w.gaffer.sync()


def test_files_are_versioned_resumable_and_private(w):
    office = space_named(w.pat, w.shade, "Production office")
    data = bytes(range(256)) * (rc.CHUNK // 256 + 1000)   # two parts
    # an upload that stops after its first part resumes where it left off
    calls = []
    orig = w.pat._req

    def flaky(method, path, **kw):
        if method == "PUT" and path.endswith("/chunks/1") and not calls:
            calls.append(path)
            raise RoomError("connection dropped")
        return orig(method, path, **kw)
    w.pat._req = flaky
    with pytest.raises(RoomError):
        w.pat.upload(office, "Schedule.xlsx", data)
    w.pat._req = orig
    fid = next(iter(w.pat.state["uploads"]))
    assert w.pat._req("GET", f"/api/files/{fid}")["present"] == [0]
    w.pat.resume_upload(fid, data)
    v2 = w.pat.upload(office, "Schedule.xlsx", data + b"more")
    assert v2["payload"]["version"] == 2 and v2["payload"]["lineage"] == fid
    assert w.pat.download(fid) == data
    w.dp.sync()
    assert all(f["name"] != "Schedule.xlsx" for f in w.dp.files())
    with pytest.raises(RoomError):
        w.dp._req("GET", f"/api/files/{fid}/chunks/0")


# ------------------------------------------------------------------ oversight and the audit log
def test_executive_reads_outside_their_spaces_are_logged(w):
    cam = space_named(w.tim, w.shade, "ZZCAMERAZZ")
    dm = w.lea.dm(w.shade, w.alex.me)
    w.lea.post([dm], "msg", {"text": "ZZPRIVATEZZ"})
    items = w.tim.open_space(dm)
    assert any((i["payload"] or {}).get("text") == "ZZPRIVATEZZ" for i in items)   # executives can read every DM
    w.tim.open_space(cam)
    reads = [e for e in w.tim.audit()["entries"] if e["action"] == "read a space they aren't in"]
    assert {e["target"]["space"] for e in reads} >= {dm, cam}
    assert w.tim.audit()["intact"]
    # producers can't read other people's private messages
    with pytest.raises(RoomError):
        w.pat._req("GET", f"/api/spaces/{dm}/items")


def test_the_audit_log_is_append_only(w):
    import sqlite3
    with pytest.raises(sqlite3.DatabaseError, match="append-only"):
        w.store.c.execute("UPDATE audit SET action='x'")
    with pytest.raises(sqlite3.DatabaseError, match="append-only"):
        w.store.c.execute("DELETE FROM audit")
    assert w.store.audit_ok()
    with pytest.raises(RoomError, match="Only an executive"):
        w.pat.audit()


# ------------------------------------------------------------------ retention and deletion
def test_archived_productions_are_deleted_after_90_days(tmp_path):
    w = World(tmp_path)
    p = w.tim.create_production("ZZGONEZZ")
    sp = space_named(w.tim, p, "Production office")
    w.tim.upload(sp, "a.txt", b"ZZOLDFILEZZ")
    w.tim._req("POST", f"/api/productions/{p}/archive", json={})
    assert purge(w.store) == []
    assert purge(w.store, now=time.time() + 91 * 86400) == [p]
    assert not w.store.q("SELECT 1 FROM items WHERE production=?", (p,))
    assert not list((w.store.blobs).rglob("0*"))
    assert w.store.audit_ok()


def test_a_persons_data_can_be_deleted(w):
    cam = space_named(w.dp, w.shade, "ZZCAMERAZZ")
    it = w.dp.post([cam], "msg", {"text": "ZZDPWROTEZZ"})
    w.tim._req("POST", f"/api/users/{w.dp.me}/delete")
    assert not w.store.q("SELECT 1 FROM items WHERE author=?", (w.dp.me,))
    w.pat.sync()
    assert it["h"]["id"] not in w.pat.items
    assert w.dp.me not in {p["user"] for p in w.pat.snapshot["people"]}
