"""BFI Cultural Test: the Section A script read and answer pack (1.0.8), with the model stood in for."""
import io
from pathlib import Path

import openpyxl
import pytest

from studio import bfiread, llm, script

FIX = Path(__file__).parent / "fixtures"
DATA = (FIX / "night_ferry.fountain").read_bytes()
WHERE = {1: ("United Kingdom", True), 2: ("England", True), 3: ("United Kingdom", False), 4: ("Unclear", False), 5: ("At sea", False),
         6: ("France", True), 7: ("France", True), 8: ("England", True), 9: ("Morocco", True), 10: ("United Kingdom", True),
         11: ("United Kingdom", False), 12: ("England", True), 13: ("Unclear", False), 14: ("United Kingdom", True)}
LANG = {4: [{"language": "French", "share": 70}, {"language": "English", "share": 30}], 9: [{"language": "Arabic", "share": 100}]}


@pytest.fixture
def fake_model(monkeypatch):
    seen = []

    def chat(engine, system, user, *, schema=None, **kw):
        seen.append(schema)
        props = schema["properties"]
        if "scenes" in props:
            nums = props["scenes"]["items"]["properties"]["scene"]["enum"]
            leads = []
            if 1 in nums:
                leads.append({"name": "MARA", "scene": 1, "evidence": "Works at Dover harbour, lives locally", "suggests": "UK or EEA"})
            if 6 in nums:
                leads.append({"name": "JULIEN", "scene": 6, "evidence": "Lieutenant of the French police judiciaire", "suggests": "UK or EEA"})
            return {"scenes": [{"scene": n, "country": WHERE[n][0], "place": "", "evidence": "heading", "explicit": WHERE[n][1],
                                "languages": LANG.get(n, [])} for n in nums],
                    "leads": leads, "subject": "Cross-Channel smuggling through Dover; the white cliffs and a South Foreland lighthouse."}
        return {"leads": [{"name": "MARA", "qualifies": "Yes", "reason": "Ship's engineer in Dover."},
                          {"name": "JULIEN", "qualifies": "No", "reason": "French, so not British."},
                          {"name": "TOM", "qualifies": "Unclear", "reason": "Lives in Dover; nationality not stated."}],
                "a3": {"proposed": 4, "conservative": 4, "reason": "Set around Dover and the Channel."},
                "b": {"proposed": 3, "conservative": 1, "reason": "Dover's maritime heritage."},
                "answers": {"A3": "Proposed: 4 points. Draft answer for A3.", "B": "Draft answer for B."}}

    monkeypatch.setattr(llm, "resolve", lambda settings, mode=None, use="writing": (llm.Engine("openai", "http://127.0.0.1:1/v1", "gemma"), ""))
    monkeypatch.setattr(llm, "chat", chat)
    return seen


def test_section_a_is_counted_by_the_studio_not_the_model(fake_model):
    b = script.parse("night_ferry.fountain", DATA)
    res = bfiread.read("night_ferry.fountain", DATA, b, {"ai_engine": {"context": 16384}})
    c = res["criteria"]
    assert res["leads"] == ["MARA", "JULIEN", "TOM"]
    # A1: UK and France count; Morocco, at sea and unclear scenes don't; conservative only where the script says so
    assert 0.5 < c["A1"]["share_proposed"] < 1 and c["A1"]["share_conservative"] < c["A1"]["share_proposed"]
    assert c["A1"]["proposed"] == bfiread.points(c["A1"]["share_proposed"], bfiread.THRESHOLDS_A1)
    # A4: spoken words counted from the script; French qualifies (EEA), Arabic doesn't
    assert c["A4"]["words"] == sum(bfiread.dialogue_words(s["text"]) for s in script.scene_texts("night_ferry.fountain", DATA))
    assert c["A4"]["by_language"]["Arabic"] == 6 and 0.9 < c["A4"]["share"] < 1 and c["A4"]["proposed"] == 6
    # A2: the model said Julien doesn't qualify, but the script calls him French (EEA): proposed 4 (Mara and Julien);
    # conservative only where the evidence names a UK or EEA nationality or country: Julien, the second lead: 2
    leads = {l["name"]: l for l in c["A2"]["leads"]}
    assert leads["JULIEN"]["qualifies"] == "Yes" and leads["JULIEN"]["named"] == "french" and leads["MARA"]["named"] is None
    assert c["A2"]["proposed"] == 4 and c["A2"]["conservative"] == 2
    assert c["B"]["conservative"] <= c["B"]["proposed"]
    pack = {p["ref"]: p for p in res["answer_pack"]}
    assert set(pack) == {"A1", "A2", "A3", "A4", "B"} and all(p["status"] in ("PENDING", "DO NOT SUBMIT") for p in pack.values())
    assert pack["A1"]["answer"].startswith(f"{c['A1']['share_proposed']:.0%} of the film") and "Morocco: scenes 9" in pack["A1"]["answer"]
    assert "Arabic 6" in pack["A4"]["answer"] and pack["A3"]["answer"] == "Draft answer for A3."      # the model's point claim removed
    assert "scenes set in the UK/EEA" in pack["A1"]["reference"]
    assert any("Script-only" in x for x in res["checks"]) and any("unclear" in x.lower() for x in res["checks"])


def test_a_claim_the_script_cannot_support_is_do_not_submit(fake_model, monkeypatch):
    b = script.parse("night_ferry.fountain", DATA)
    res = bfiread.read("night_ferry.fountain", DATA, b, {})
    res["criteria"]["A3"] |= {"proposed": 4, "conservative": 0}
    pack = {p["ref"]: p for p in bfiread._pack(res["criteria"], {}, res["scenes"], res["criteria"]["A2"])}
    assert pack["A3"]["status"] == "DO NOT SUBMIT" and pack["A4"]["status"] == "PENDING"


def test_the_answer_pack_workbook_keeps_jons_columns_and_the_evidence(fake_model):
    b = script.parse("night_ferry.fountain", DATA)
    res = bfiread.read("night_ferry.fountain", DATA, b, {})
    wb = openpyxl.load_workbook(io.BytesIO(bfiread.workbook(res)))
    assert wb.sheetnames == ["Answer Pack", "A1 Setting analysis", "A4 Dialogue count", "A2 Leads", "Notes"]
    head = [c.value for c in wb["Answer Pack"][1]]
    for col in ("BFI Question", "Proposed Answer", "Supporting Document", "Exact Reference", "Assumptions", "Approval Required", "Status"):
        assert col in head
    assert wb["A1 Setting analysis"].max_row == 15 and wb["A4 Dialogue count"]["B5"].value == 17


def test_zones_and_languages():
    assert [bfiread.zone(x) for x in ("Scotland", "Norway", "Switzerland", "", "Morocco")] == ["UK", "EEA", "Other", "Unclear", "Other"]
    assert bfiread.qualifying_language("Welsh") and bfiread.qualifying_language("French") and not bfiread.qualifying_language("Arabic")
    assert bfiread.dialogue_words("MARA\n(quietly)\nTide's turning now.\n\nShe goes.") == 3
