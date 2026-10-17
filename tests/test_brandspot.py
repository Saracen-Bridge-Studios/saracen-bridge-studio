"""Brand Integration: scene-by-scene opportunities and outreach drafts (1.0.7), with the model stood in for."""
import io
from pathlib import Path

import openpyxl
import pytest

from studio import brandspot, llm, script

FIX = Path(__file__).parent / "fixtures"
DATA = (FIX / "night_ferry.fountain").read_bytes()


@pytest.fixture
def fake_model(monkeypatch):
    calls = []

    def chat(engine, system, user, *, schema=None, **kw):
        calls.append((system, user, schema))
        props = schema["properties"]
        if "opportunities" in props:
            scenes = props["opportunities"]["items"]["properties"]["scene"]["enum"]
            ids = props["opportunities"]["items"]["properties"]["brands"]["items"]["enum"]
            out = []
            if 1 in scenes:
                out.append({"scene": 1, "moment": "Mara checks the time on her watch.", "item": "Smartwatch", "category": "Technology & Electronics",
                            "placement": "functional", "in_script": True, "narrative_reason": "She is always late.", "creative_change": "None",
                            "risks": "None evident", "brands": ["SB-BR-0001"], "feasibility": 5, "value": 4})
            if 2 in scenes:
                out.append({"scene": 2, "moment": "Mara drives through Dover.", "item": "Defender 4x4", "category": "Automotive",
                            "placement": "hero", "in_script": True, "narrative_reason": "Her rugged car is her character.",
                            "creative_change": "None", "risks": "Rain stunt driving", "brands": [], "feasibility": 4, "value": 5})
                out.append({"scene": 2, "moment": "She drinks from a can.", "item": "Energy drink", "category": "Alcohol",
                            "placement": "background", "in_script": True, "narrative_reason": "Tired.", "creative_change": "None",
                            "risks": "None", "brands": [], "feasibility": 3, "value": 2})
            out.append({"scene": 999, "moment": "not shown", "item": "x", "category": "Other", "placement": "background",
                        "in_script": False, "narrative_reason": "", "creative_change": "", "risks": "", "brands": [ids[0]],
                        "feasibility": 1, "value": 1})
            return {"opportunities": out}
        if "targets" in props:
            ids = props["targets"]["items"]["properties"]["brand_id"]["enum"]
            return {"targets": [{"brand_id": i, "group": "Anchor Partner" if n == 0 else "Alternative",
                                 "outreach_angle": f"Angle {n}", "next_action": "Find the partnerships lead"} for n, i in enumerate(ids)]}
        return {"subject": "The Night Ferry", "email": "Dear [Contact name], write to jon@example.com", "follow_up": "Following up.",
                "linkedin": "Hello.", "call_brief": ["One", "Two", "Three"]}

    monkeypatch.setattr(llm, "resolve", lambda settings, mode=None, use="writing": (llm.Engine("openai", "http://127.0.0.1:1/v1", "gemma"), ""))
    monkeypatch.setattr(llm, "chat", chat)
    return calls


def test_opportunities_are_grounded_in_scenes_and_jon_database(fake_model):
    b = script.parse("night_ferry.fountain", DATA)
    res = brandspot.spot("night_ferry.fountain", DATA, b, {"ai_engine": {"context": 16384}},
                         options={"avoid": ["Alcohol"], "rating": "12A"}, targets=["SB-BR-0016"])
    opps = res["opportunities"]
    assert [o["id"] for o in opps] == ["BI-001", "BI-002"]                     # scene 999 and the avoided category dropped
    watch, car = opps
    assert watch["targets"][0] == "SB-BR-0001" and len(watch["targets"]) == 3   # model's pick, then two from the category
    assert car["targets"][0] == "SB-BR-0016"                                    # the script names Land Rover in scene 2
    assert all(t in {r["brand_id"] for r in brandspot.catalogue()} for o in opps for t in o["targets"])
    assert car["page"] == 1 and car["scene_heading"].startswith("INT. MARA'S LAND ROVER")
    assert car["priority"] == brandspot.priority(4, 5, {"priority": "High"}) or car["priority"] == brandspot.priority(4, 5, None)
    assert {n["brand_name"] for n in res["named_in_script"]} == {"Apple", "Land Rover"}
    assert res["targets"][0]["group"] == "Anchor Partner" and res["targets"][0]["outreach_angle"] == "Angle 0"
    assert all("No named contact" in t["route"] or "No public route" in t["route"] for t in res["targets"])
    assert len(res["outreach"]) == min(5, len(res["targets"])) and res["outreach"][0]["status"] == "Draft: not sent"
    assert any("email address" in c for c in res["checks"]) and any("already names" in c for c in res["checks"])
    system = fake_model[0][0]
    assert "SCRIPT-SPECIFIC OPPORTUNITY MAPPING" in system and "Alcohol" in system and "12A" in system
    assert "SB-BR-0001 Apple" in system and "Land Rover" in system


def test_the_workbook_has_the_register_targets_and_drafts(fake_model):
    b = script.parse("night_ferry.fountain", DATA)
    res = brandspot.spot("night_ferry.fountain", DATA, b, {"ai_engine": {"context": 16384}})
    wb = openpyxl.load_workbook(io.BytesIO(brandspot.workbook(res)))
    assert wb.sheetnames == ["Opportunity Register", "Target Brands", "Outreach Drafts", "Notes"]
    reg = wb["Opportunity Register"]
    assert reg["A2"].value == "BI-001" and reg["T2"].value.startswith("To price")
    assert wb["Outreach Drafts"]["C2"].value == "Draft: not sent"


def test_a_breakdown_from_an_older_reading_is_refused(fake_model):
    b = script.parse("night_ferry.fountain", DATA) | {"scene_count": 3}
    with pytest.raises(ValueError, match="read again"):
        brandspot.spot("night_ferry.fountain", DATA, b, {})


def test_named_brands_are_registered_and_cross_category_picks_dropped(monkeypatch):
    def chat(engine, system, user, *, schema=None, **kw):
        props = schema["properties"]
        if "opportunities" in props:
            scenes = props["opportunities"]["items"]["properties"]["scene"]["enum"]
            return {"opportunities": [{"scene": 1, "moment": "Mara checks the time.", "item": "Smartwatch", "category": "Technology & Electronics",
                                       "placement": "functional", "in_script": True, "narrative_reason": "Late.", "creative_change": "None",
                                       "risks": "None", "brands": ["SB-BR-0016"], "feasibility": 5, "value": 4}] if 1 in scenes else []}
        if "targets" in props:
            return {"targets": [{"brand_id": i, "group": "Alternative", "outreach_angle": "", "next_action": ""}
                                for i in props["targets"]["items"]["properties"]["brand_id"]["enum"]]}
        return {"subject": "s", "email": "e", "follow_up": "f", "linkedin": "l", "call_brief": ["a", "b", "c"]}

    monkeypatch.setattr(llm, "resolve", lambda settings, mode=None, use="writing": (llm.Engine("openai", "http://127.0.0.1:1/v1", "gemma"), ""))
    monkeypatch.setattr(llm, "chat", chat)
    b = script.parse("night_ferry.fountain", DATA)
    res = brandspot.spot("night_ferry.fountain", DATA, b, {})
    watch = res["opportunities"][0]
    assert "SB-BR-0016" not in watch["targets"] and watch["targets"][0] == "SB-BR-0001"     # Land Rover on a watch: dropped
    rover = next(o for o in res["opportunities"] if o["scene"] == 2)
    assert rover["source"] == "named in the script" and rover["targets"][0] == "SB-BR-0016" and "Land Rover Defender" in rover["moment"]
