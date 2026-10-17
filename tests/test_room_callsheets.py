"""Call sheets in the Room (1.0.8): per-person times, private pickups, Got it per version, reminders, the PDF."""
import json

import pytest

from room_world import shade
from studio.room import callsheets as CS
from studio.room import service as S
from studio.room.client import RoomError


@pytest.fixture(scope="module")
def w(tmp_path_factory):
    return shade(tmp_path_factory.mktemp("cs"))


def rows(w):
    return [{"user": w.gaffer.me, "call": "6.15"},
            {"user": w.lea.me, "pickup": "05:10", "pickup_address": "ZZ12 HARBOUR ROWZZ", "driver": "ZZDRIVERDANZZ",
             "hmu": "05:40", "costume": "06:20", "on_set": "07:15", "character": "Mara", "scenes": "14, 15"}]


def test_publish_confirm_remind_and_a_new_version(w):
    data = {"day": "Day 12", "date": "2026-10-20", "unit_call": "06:30", "location": "Quarry", "weather_cover": "Stage B",
            "scenes": [{"no": "14", "slug": "EXT. QUARRY - DAY", "pages": "2"}], "rows": rows(w)}
    pdf = w.pat.upload(CS.audience(w.pat, w.shade)[0], "callsheet_d12.pdf", b"%PDF-1.4 ZZPDFZZ" * 100,
                       share=CS.audience(w.pat, w.shade)[1:])
    r = CS.publish(w.pat, w.shade, data, pdf_file={"id": pdf["h"]["ref"], "name": "callsheet_d12.pdf", "size": 1600})
    assert r["version"] == 1
    for c in (w.gaffer, w.lea, w.grip, w.tim):
        c.sync()
    ppl = S.people(w.gaffer, w.shade)
    g = CS.today(w.gaffer, w.shade, ppl, {})
    assert g["unit_call"] == "06:30" and g["my_row"]["call"] == "06:15" and g["on_sheet"] and not g["can_remind"]
    l = CS.today(w.lea, w.shade, S.people(w.lea, w.shade), {})
    assert l["my_row"]["pickup"] == "05:10" and l["my_row"]["driver"] == "ZZDRIVERDANZZ"
    # pickups and drivers reach only that person and the production office
    seen = json.dumps([i["payload"] for i in w.gaffer.items.values()])
    assert "ZZ12 HARBOUR ROWZZ" not in seen and "ZZDRIVERDANZZ" not in seen
    assert CS.today(w.grip, w.shade, S.people(w.grip, w.shade), {})["my_row"] is None
    # everyone on it can open the PDF, wherever it was uploaded
    assert b"ZZPDFZZ" in w.gaffer.download(g["pdf"]["id"])
    # Got it, then the producer's count and reminders
    CS.confirm(w.lea, l["item"])
    w.pat.sync()
    p = CS.today(w.pat, w.shade, S.people(w.pat, w.shade), {})
    assert (p["confirmed"], p["expected"]) == (1, 2) and p["can_remind"]
    assert {x["name"]: x["confirmed"] for x in p["people"]} == {"ZZGAFFERZZ": False, "ZZLEACASTZZ": True}
    before = len(w.lea.sync()["notifications"])
    assert CS.remind(w.pat, p["item"]) == 1
    assert any(n["kind"] == "reminder" for n in w.gaffer.sync()["notifications"])
    assert len(w.lea.sync()["notifications"]) == before
    # a new version notifies everyone on it and starts the count again
    data["unit_call"] = "07:00"
    r2 = CS.publish(w.pat, w.shade, dict(data, lineage=r["lineage"]))
    assert r2["version"] == 2
    w.pat.sync()
    p2 = CS.today(w.pat, w.shade, S.people(w.pat, w.shade), {})
    assert p2["version"] == 2 and p2["unit_call"] == "07:00" and p2["confirmed"] == 0
    assert sum(n["kind"] == "callsheet" for n in w.lea.sync()["notifications"]) >= 2


def test_only_producers_and_executives_publish(w):
    with pytest.raises(RoomError):
        CS.publish(w.gaffer, w.shade, {"day": "Day 1", "unit_call": "06:00", "rows": []})
    with pytest.raises(RoomError, match="isn't a time"):
        CS.publish(w.pat, w.shade, {"day": "Day 1", "unit_call": "6 in the morning", "rows": []})


def test_times_from_a_csv(w):
    ppl = S.people(w.pat, w.shade)
    r = CS.parse_csv("Name,Call,Pickup,Pickup address\nZZGAFFERZZ,0615,,\nZZLEACASTZZ,,5:10,1 Pier St\nNobody Here,07:00,,\n", ppl)
    assert [x["user"] for x in r["rows"]] == [w.gaffer.me, w.lea.me] and r["unknown"] == ["Nobody Here"]
    assert r["rows"][0]["call"] == "06:15" and r["rows"][1]["pickup"] == "05:10"
    with pytest.raises(RoomError, match="Name"):
        CS.parse_csv("Who,Call\nx,06:00\n", ppl)
