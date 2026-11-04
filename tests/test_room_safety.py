"""Safety in the Room (1.2.0): terms, reporting, blocking and deleting your own account, against a real hub with real
crypto. These are what Apple's App Review asks of anything people post in (guideline 1.2) and of deleting an account
from inside the app (5.1.1(v))."""
import json

import pytest

from room_hub.safety import TERMS_VERSION
from studio.room.client import RoomError

from room_world import shade, space_named


@pytest.fixture()
def w(tmp_path):
    return shade(tmp_path)


def _msg(c, sid, text):
    return c.post([sid], "msg", {"text": text})["h"]["id"]


def test_terms_are_recorded_once_accepted(w):
    assert w.lea.sync()["safety"]["terms_accepted"] is False
    assert w.lea.snapshot["safety"]["terms"] == TERMS_VERSION
    with pytest.raises(RoomError, match="terms have changed"):
        w.lea.accept_terms("2000-01-01")
    w.lea.accept_terms(TERMS_VERSION)
    assert w.lea.sync()["safety"]["terms_accepted"] is True
    assert any(e["action"] == "accepted the Room's terms" for e in w.tim.audit()["entries"])


def test_joining_with_the_terms_ticked_records_them(w):
    inv = w.tim.invite(w.shade, "crew", "ZZNEWCREWZZ", department=w.camera)
    c = w.client("newcrew")
    c._new_device()
    import os
    import room_crypto as rc
    r = c._req("POST", "/api/join", auth=False, json={"token": inv["token"], "device": c.device.public(),
                                                      "commit": rc.commitment(c.device.public(), os.urandom(32)),
                                                      "terms": TERMS_VERSION})
    assert r["terms"] == TERMS_VERSION
    assert w.store.one("SELECT 1 FROM terms WHERE user=? AND version=?", (r["user"], TERMS_VERSION))


def test_a_report_reaches_producers_and_executives_only(w):
    camera = space_named(w.gaffer, w.shade, "ZZCAMERAZZ")
    iid = _msg(w.gaffer, camera, "ZZOFFENSIVEZZ")
    w.dp.sync()
    with pytest.raises(RoomError, match="reason"):
        w.dp.report("rude-ish", item=iid)
    with pytest.raises(RoomError, match="yourself"):
        w.gaffer.report("abusive", item=iid)
    with pytest.raises(RoomError, match="Unknown item"):            # an item you can't see can't be reported
        w.lea.report("abusive", item=iid)
    rid = w.dp.report("abusive", item=iid)
    assert w.dp.report("abusive", item=iid) == rid                  # the same report twice is one report
    for c in (w.tim, w.pat):
        rows = c.reports(w.shade)
        assert [(r["id"], r["item"], r["about"], r["reason"], r["status"]) for r in rows] == \
               [(rid, iid, w.gaffer.me, "abusive", "open")]
        assert c.sync()["safety"]["reports_open"] == {w.shade: 1}
        assert any(n["kind"] == "report" for n in c.snapshot["notifications"])
    for c in (w.gaffer, w.dp, w.lea):
        with pytest.raises(RoomError, match="Only producers and executives"):
            c.reports(w.shade)
    # the hub learns which item and why, never what it said
    raw = json.dumps([dict(r) for r in w.store.q("SELECT * FROM reports")])
    assert "ZZOFFENSIVEZZ" not in raw


def test_removing_a_reported_item_takes_it_off_every_device(w):
    camera = space_named(w.gaffer, w.shade, "ZZCAMERAZZ")
    iid = _msg(w.gaffer, camera, "ZZREMOVEMEZZ")
    w.dp.sync()
    assert iid in w.dp.items
    rid = w.dp.report("harassment", item=iid)
    w.pat.resolve_report(rid, "item_removed")
    w.dp.sync()
    assert iid not in w.dp.items
    assert w.pat.reports(w.shade) == []
    done = w.pat.reports(w.shade, status="all")[0]
    assert (done["status"], done["outcome"], done["resolved_by"], done["gone"]) == ("resolved", "item_removed", w.pat.me, True)
    with pytest.raises(RoomError, match="already been dealt with"):
        w.pat.resolve_report(rid, "dismissed")
    actions = [e["action"] for e in w.tim.audit()["entries"]]
    assert {"reported content", "deleted an item", "dealt with a report"} <= set(actions)
    assert w.tim.audit()["intact"]


def test_only_an_executive_removes_a_reported_person(w):
    rid = w.dp.report("abusive", production=w.shade, about=w.gaffer.me)
    with pytest.raises(RoomError, match="Only an executive"):
        w.pat.resolve_report(rid, "person_removed")
    w.tim.resolve_report(rid, "person_removed")
    assert not w.store.one("SELECT 1 FROM memberships WHERE user=? AND production=?", (w.gaffer.me, w.shade))
    rid2 = w.pat.report("abusive", production=w.shade, about=w.tim.me)
    with pytest.raises(RoomError, match="executive can't be removed"):
        w.tim.resolve_report(rid2, "person_removed")
    w.tim.resolve_report(rid2, "dismissed")


def test_blocking_stops_conversations_and_unblocking_restores_them(w):
    dm = w.alex.dm(w.shade, w.lea.me)                 # the 2nd AD and a cast member already talk
    w.lea.sync()
    w.lea.block(w.alex.me)
    assert w.lea.snapshot["safety"]["blocks"] == [w.alex.me]
    with pytest.raises(RoomError, match="isn't taking messages"):
        _msg(w.alex, dm, "ZZAFTERBLOCKZZ")
    alex_view = {p["user"]: p for p in w.alex.sync()["people"]}
    assert alex_view[w.lea.me]["can_reach"] is False
    lea_view = {p["user"]: p for p in w.lea.snapshot["people"]}
    assert lea_view[w.alex.me]["can_reach"] is False
    w.lea.block(w.alex.me, on=False)
    assert w.lea.snapshot["safety"]["blocks"] == []
    assert _msg(w.alex, dm, "ZZAFTERUNBLOCKZZ").startswith("m_")
    with pytest.raises(RoomError, match="Pick someone"):
        w.lea.block(w.lea.me)


def test_deleting_your_own_account(w):
    office = space_named(w.pat, w.shade, "Production office")
    sam_space = next(sp["id"] for sp in w.sam.snapshot["spaces"] if sp["kind"] == "personal")
    iid = _msg(w.sam, sam_space, "ZZSAMWASHEREZZ")
    w.sam.report("spam", production=w.shade, about=w.pat.me)
    with pytest.raises(RoomError, match="Confirm"):
        w.sam._req("POST", "/api/me/delete", json={})
    w.sam.delete_my_account()
    with pytest.raises(RoomError, match="Unknown device|removed from the Room"):
        w.sam.sync()
    assert not w.store.one("SELECT 1 FROM items WHERE id=?", (iid,))
    assert not w.store.one("SELECT 1 FROM memberships WHERE user=?", (w.sam.me,))
    assert w.store.one("SELECT deleted FROM users WHERE id=?", (w.sam.me,))["deleted"] == 1
    assert w.store.one("SELECT reporter FROM reports")["reporter"] == ""          # the report stays, without her
    assert "deleted their own account" in [e["action"] for e in w.tim.audit()["entries"]]
    assert w.tim.audit()["intact"]
    assert office                                                                 # the production carries on
    with pytest.raises(RoomError, match="set up this Room"):
        w.tim.delete_my_account()


def test_the_studio_shows_reports_with_what_was_posted(w):
    from studio.room import access
    camera = space_named(w.gaffer, w.shade, "ZZCAMERAZZ")
    iid = _msg(w.gaffer, camera, "ZZSHOWNTOEXECZZ")
    w.dp.sync()
    w.dp.report("hate", item=iid)
    w.tim.sync()
    rows = access.reports(w.tim, w.shade)
    assert [(r["reason"], r["about"], r["reporter"], r["text"], r["can_remove_person"]) for r in rows] == \
           [("Hate or discrimination", "ZZGAFFERZZ", "ZZDPKEYZZ", "ZZSHOWNTOEXECZZ", True)]
    w.pat.sync()
    assert access.reports(w.pat, w.shade)[0]["can_remove_person"] is False     # only executives remove people
