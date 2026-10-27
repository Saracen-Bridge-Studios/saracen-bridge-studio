"""Casting Director (1.1.6): roles from the breakdown, the model's reading stood in for, shortlists from the database."""
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from studio import casting, llm, refdata, script

FIX = Path(__file__).parent / "fixtures"
DATA = (FIX / "night_ferry.fountain").read_bytes()
B = script.parse("night_ferry.fountain", DATA)


def test_roles_come_from_the_breakdown_largest_first():
    rs = casting.roles(B)
    assert rs[0]["name"] == "MARA" and rs[0]["size"] == "Lead"
    assert all(r["scenes"] >= 1 and 0 < r["share"] <= 1 and r["days"] >= 1 for r in rs)
    assert [r["scenes"] for r in rs] == sorted((r["scenes"] for r in rs), reverse=True)
    assert {r["size"] for r in rs} <= set(casting.SIZES)


def test_ages_printed_in_the_script_are_read_without_the_model():
    assert casting.age_from_text("MARA OKAFOR (34), a ship's engineer", "MARA") == (34, 34)      # after the surname too
    assert casting.age_from_text("Mara drives (fast) to MARA'S house", "MARA") is None
    assert casting.age_from_text("PRIYA (40s), waves her through", "PRIYA") == (40, 49)
    assert casting.age_from_text("TOM (late 60s) makes tea", "TOM") == (66, 69)
    assert casting.age_from_text("JO (mid-twenties)", "JO") == (23, 26)
    assert casting.age_from_text("JO (early 30s)", "JO") == (30, 33)
    assert casting.age_from_text("JO (V.O.)", "JO") is None
    ages = casting.script_ages("night_ferry.fountain", DATA, B)
    assert ages["MARA"]["age_low"] == 34 and ages["MARA"]["source"] == "script"


def test_shortlists_fit_gender_age_and_budget_and_never_repeat_an_actor():
    cast = [{"name": "MARA", "size": "Lead", "gender": "Female", "age_low": 30, "age_high": 39},
            {"name": "TOM", "size": "Supporting", "gender": "Male", "age_low": 65, "age_high": 72}]
    res = casting.shortlist(cast, genre="Thriller", budget_usd=5_000_000)
    mara, tom = res
    assert 0 < len(mara["shortlist"]) <= casting.SHORTLIST and len(tom["shortlist"]) > 0
    rows = {r["actor"]: r for r in refdata.rows("SELECT actor, gender, approx_playing_age, minimum_sensible_budget_usd FROM talent_actors")}
    for a in mara["shortlist"]:
        r = rows[a["actor"]]                                   # every name is in the database, and fits
        assert r["gender"] == "Female" and r["approx_playing_age"] == "30–49" and (r["minimum_sensible_budget_usd"] or 0) <= 5_000_000
    for a in tom["shortlist"]:
        assert rows[a["actor"]]["gender"] == "Male" and rows[a["actor"]]["approx_playing_age"] in ("50–69", "70+")
    assert not {a["actor"] for a in mara["shortlist"]} & {a["actor"] for a in tom["shortlist"]}
    assert mara["over_budget"] > 0                               # bigger names left out by the budget, and counted
    # genre matches come first, then by value
    flags = [a["genre_match"] for a in mara["shortlist"]]
    assert flags == sorted(flags, reverse=True)
    big = casting.shortlist(cast[:1], genre="Thriller", budget_usd=None)[0]
    assert big["over_budget"] == 0 and max(a["value"] for a in big["shortlist"]) >= max(a["value"] for a in mara["shortlist"])


@pytest.fixture
def fake_model(monkeypatch):
    said = {"MARA": ("Female", 32, 36, "A ship's engineer who never stops working."), "TOM": ("Male", 66, 70, "Her father, a retired lighthouse keeper.")}

    def chat(engine, system, user, *, schema=None, **kw):
        names = schema["properties"]["roles"]["items"]["properties"]["name"]["enum"]
        assert "Never name or suggest an actor" in system
        return {"roles": [{"name": n, "gender": said.get(n, ("Any", 0, 0, ""))[0], "age_low": said.get(n, ("", 30, 40))[1],
                           "age_high": said.get(n, ("", 30, 40, ""))[2], "stated": False, "description": said.get(n, ("", 0, 0, "Someone."))[3],
                           "qualities": ["grit"]} for n in names]}

    monkeypatch.setattr(llm, "resolve", lambda settings, mode=None, use="writing": (llm.Engine("openai", "http://127.0.0.1:1/v1", "gemma"), ""))
    monkeypatch.setattr(llm, "chat", chat)


def test_the_models_reading_feeds_the_shortlist(fake_model):
    res = casting.read_roles("night_ferry.fountain", DATA, B, {"ai_engine": {"context": 16384}})
    assert res["roles"]["MARA"]["gender"] == "Female" and res["roles"]["MARA"]["source"] == "model"
    out = casting.suggest(B, res["roles"], genre="Thriller", budget_usd=10_000_000)
    mara = next(r for r in out["roles"] if r["name"] == "MARA")
    assert mara["gender"] == "Female" and mara["filters"]["bands"] == ["30–49"] and mara["shortlist"]
    # a correction beats the reading
    out = casting.suggest(B, res["roles"], edits={"MARA": {"age_low": 52, "age_high": 58}})
    mara = next(r for r in out["roles"] if r["name"] == "MARA")
    assert mara["filters"]["bands"] == ["50–69"] and mara["read"]["edited"]


def test_api_reads_saves_corrections_and_prefills_from_sales(tmp_path, monkeypatch, fake_model):
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path))
    from studio import jobs, store
    from studio.server import app
    c = TestClient(app)
    rec = store.save_run("coverage", "The Night Ferry", {"file": "night_ferry.fountain", "sha256": "nf"}, {"breakdown": B},
                         files={"night_ferry.fountain": DATA}, summary={"scene_count": B["scene_count"]})
    store.save_run("sales", "The Night Ferry", {"intake": {"genre": "Thriller", "budget": 4_000_000, "budget_currency": "USD"}}, {"valuation": {}})
    r = c.get(f"/api/casting/coverage/{rec['id']}").json()
    assert r["genre"] == "Thriller" and r["budget_usd"] == 4_000_000 and r["prefill_from"] == "The Night Ferry" and r["read"] is None
    assert r["roles"][0]["name"] == "MARA"
    monkeypatch.setattr(jobs, "ensure_worker", lambda: None)         # run the job here, not on the worker thread
    q = c.post(f"/api/casting/coverage/{rec['id']}/read", json={"mode": "quick"}).json()
    assert q["queued"] == 1
    jobs.run_casting(store.claim_job())
    r = c.get(f"/api/casting/coverage/{rec['id']}").json()
    assert r["read"]["mode"] == "quick" and next(x for x in r["roles"] if x["name"] == "MARA")["gender"] == "Female"
    r = c.put(f"/api/casting/coverage/{rec['id']}", json={"genre": "Drama", "budget_usd": None,
                                                            "edits": {"MARA": {"gender": "Female", "age_low": 45, "age_high": 50, "size": "Lead"}}}).json()
    mara = next(x for x in r["roles"] if x["name"] == "MARA")
    assert r["genre"] == "Drama" and r["budget_usd"] is None and mara["age_low"] == 45 and mara["read"]["edited"]
    r = c.put(f"/api/casting/coverage/{rec['id']}", json={"edits": {"MARA": {"reset": True}}}).json()
    assert next(x for x in r["roles"] if x["name"] == "MARA")["age_low"] == 34      # the age the script prints, over the reading
    assert c.get("/api/casting/coverage/nope").status_code == 404


def test_open_and_non_binary_parts_are_not_filtered_by_gender_and_child_parts_are_flagged():
    cast = [{"name": "SAM", "size": "Lead", "gender": "Any", "age_low": 30, "age_high": 39},
            {"name": "ALEX", "size": "Supporting", "gender": "Non-binary", "age_low": 30, "age_high": 39},
            {"name": "AMY", "size": "Supporting", "gender": "Female", "age_low": 8, "age_high": 9}]
    sam, alex, amy = casting.shortlist(cast)
    rows = {r["actor"]: r["gender"] for r in refdata.rows("SELECT actor, gender FROM talent_actors")}
    assert sam["filters"]["gender"] is None and alex["filters"]["gender"] is None and sam["considered"] > alex["considered"] - 50
    assert len({rows[a["actor"]] for a in sam["shortlist"] + alex["shortlist"]}) >= 1 and alex["shortlist"]
    assert amy["flags"] and "reg. 22" in amy["flags"][0] and not sam["flags"]
    assert all(rows[a["actor"]] == "Female" for a in amy["shortlist"])
