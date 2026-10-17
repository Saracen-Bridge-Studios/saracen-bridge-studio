"""Scheduling & Budgeting: element tagging and the budget lines it drives (1.0.8), with the model stood in for."""
import io
from pathlib import Path

import openpyxl
import pytest

from studio import budget, elements, llm, script

FIX = Path(__file__).parent / "fixtures"
DATA = (FIX / "night_ferry.fountain").read_bytes()
TAGS = {   # what a careful reader would tag in the Night Ferry fixture
    1: {"background": "11-30", "vehicles": ["Lorries"], "props": ["Toolbag"]},
    2: {"vehicles": ["Land Rover Defender"], "special_equipment": ["Camera car"]},
    3: {"animals": ["Sheepdog"]},
    5: {"background": "31-100", "stunts": ["Lorry slides, Mara dives with a child"], "stunt_performers": 2, "sfx": ["Rain", "Ship pitching"],
        "vfx": ["Ferry in the storm, aerial"], "vfx_shots": 3, "minors": ["Amy (8)"]},
    9: {"weapons": ["Handgun"]},
    10: {"stunts": ["Forklift near miss", "Motorbike slide into the harbour"], "stunt_performers": 1, "weapons": ["Pistol"],
         "vehicles": ["Forklift", "Motorbike"], "sfx": ["Rain", "Sparks"], "water": True},
    13: {"vfx": ["Helicopter searchlight"], "vfx_shots": 2, "special_equipment": ["Boats", "Drone"]},
}


@pytest.fixture
def fake_model(monkeypatch):
    def chat(engine, system, user, *, schema=None, **kw):
        scenes = schema["properties"]["scenes"]["items"]["properties"]["scene"]["enum"]
        blank = {k: ([] if kind == "list" else False if kind == "flag" else 0) for k, (_, kind) in elements.FIELDS.items()} | {"background": "none"}
        return {"scenes": [blank | {"scene": n, "notes": ""} | TAGS.get(n, {}) for n in scenes]}

    monkeypatch.setattr(llm, "resolve", lambda settings, mode=None, use="writing": (llm.Engine("openai", "http://127.0.0.1:1/v1", "gemma"), ""))
    monkeypatch.setattr(llm, "chat", chat)


def test_every_scene_is_tagged_and_summarised(fake_model):
    b = script.parse("night_ferry.fountain", DATA)
    res = elements.tag("night_ferry.fountain", DATA, b, {"ai_engine": {"context": 16384}})
    assert len(res["scenes"]) == 14 and all(s["tagged"] for s in res["scenes"]) and not res["checks"]
    s = res["summary"]
    assert s["stunts"]["scenes"] == [5, 10] and s["weapons"]["scenes"] == [9, 10] and s["minors"]["scenes"] == [5]
    assert s["background"]["total"] == 80 and s["vfx_shots"]["total"] == 5 and s["water"]["scenes"] == [10]
    assert {i["item"] for i in s["vehicles"]["items"]} == {"Lorries", "Land Rover Defender", "Forklift", "Motorbike"}


def test_the_budget_prices_what_the_tagging_found(fake_model):
    b = script.parse("night_ferry.fountain", DATA)
    tags = elements.tag("night_ferry.fountain", DATA, b, {"ai_engine": {"context": 16384}})
    plain = budget.build(b, jurisdiction="United Kingdom")
    res = budget.build(b, jurisdiction="United Kingdom", elements=tags)
    lines = {l["description"]: l for l in res["budget"]["base"]["lines"]}
    for desc in ("Stunt coordinator", "Stunt performers", "Special effects supervisor", "Picture vehicles", "Armourer / firearms specialist",
                 "Animal trainer / wrangler", "Chaperone and tutor for child performers", "Drone / aerial unit", "Safety / camera boat"):
        assert lines[desc]["driver"] == "elements", desc
    assert lines["Picture vehicle mechanic"]["status"] == "benchmark" and lines["Picture vehicle mechanic"]["amount"] > 0   # on Jon's UK card
    assert lines["Stunt coordinator"]["status"] == "unknown" and "negotiated" in lines["Stunt coordinator"]["note"]     # UK card: negotiated
    assert lines["Armourer / firearms specialist"]["status"] == "unknown" and "quote" in lines["Armourer / firearms specialist"]["note"]
    de = {l["description"]: l for l in budget.build(b, jurisdiction="Germany", elements=tags)["budget"]["base"]["lines"]}
    assert de["Stunt coordinator"]["status"] == "benchmark" and de["Stunt performers"]["qty"] >= 2       # Germany prices stunts as cast
    assert lines["Background artists (from the script read)"]["qty"] > 0
    assert "VFX shots (5)" in lines and "Intimacy coordinator" not in lines
    assert res["budget"]["base"]["known_total"] > plain["budget"]["base"]["known_total"]
    assert res["elements"]["tagged"] == 14 and any("element tagging" in a for a in res["assumptions"])
    # the same lines in every case, so producer overrides and the workbook line up
    keys = {s: {(l["account"], l["description"]) for l in res["budget"][s]["lines"]} for s in budget.SCENARIOS}
    assert keys["lean"] == keys["base"] == keys["conservative"]
    over = budget.build(b, jurisdiction="United Kingdom", elements=tags,
                        inputs={"background_per_day": 0, "vfx_shots": 0, "overrides": {"2505|Armourer / firearms specialist": 1200}})
    ol = {l["description"]: l for l in over["budget"]["base"]["lines"]}
    assert ol["Background artists (none)"]["amount"] == 0 and not any(d.startswith("VFX shots") for d in ol)
    assert ol["Armourer / firearms specialist"]["amount"] == 1200 and ol["Armourer / firearms specialist"]["status"] == "input"
    wb = openpyxl.load_workbook(io.BytesIO(budget.workbook("Night Ferry", res, tags)))
    assert "Elements" in wb.sheetnames and wb["Elements"]["A2"].value == 1


def test_a_producer_zero_for_background_is_priced_as_none_without_tagging():
    b = script.parse("night_ferry.fountain", DATA)
    res = budget.build(b, jurisdiction="United Kingdom", inputs={"background_per_day": 0})
    lines = {l["description"]: l for l in res["budget"]["base"]["lines"]}
    assert lines["Background artists (none)"]["status"] == "input" and "Background artists" not in lines


def test_a_weak_reading_is_reined_in(monkeypatch):
    def chat(engine, system, user, *, schema=None, **kw):
        nums = schema["properties"]["scenes"]["items"]["properties"]["scene"]["enum"]
        blank = {k: ([] if kind == "list" else False if kind == "flag" else 0) for k, (_, kind) in elements.FIELDS.items()}
        return {"scenes": [blank | {"scene": n, "notes": "", "background": "over 100", "stunt_performers": 2, "vfx_shots": 4} for n in nums]}

    monkeypatch.setattr(llm, "resolve", lambda settings, mode=None, use="writing": (llm.Engine("openai", "http://127.0.0.1:1/v1", "gemma"), ""))
    monkeypatch.setattr(llm, "chat", chat)
    b = script.parse("night_ferry.fountain", DATA)
    res = elements.tag("night_ferry.fountain", DATA, b, {})
    assert all(s["stunt_performers"] == 0 and s["vfx_shots"] == 0 for s in res["scenes"])      # nothing to perform, no VFX listed
    assert all(s["background"] == 150 for s in res["scenes"]) and any("overstated" in c for c in res["checks"])
