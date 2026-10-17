"""The 1.0.7 AI features through the API and the job queue, with the model stood in for."""
from pathlib import Path

import pytest

from studio import elements, jobs, llm, store

FIX = Path(__file__).parent / "fixtures"
FERRY = (FIX / "night_ferry.fountain").read_bytes()


def fake_chat(engine, system, user, *, schema=None, **kw):
    props = schema["properties"]
    if "opportunities" in props:
        nums = props["opportunities"]["items"]["properties"]["scene"]["enum"]
        return {"opportunities": [{"scene": nums[0], "moment": "m", "item": "Smartwatch", "category": "Technology & Electronics",
                                   "placement": "functional", "in_script": True, "narrative_reason": "r", "creative_change": "None",
                                   "risks": "None", "brands": [], "feasibility": 4, "value": 4}]}
    if "targets" in props:
        return {"targets": [{"brand_id": i, "group": "Alternative", "outreach_angle": "a", "next_action": "n"}
                            for i in props["targets"]["items"]["properties"]["brand_id"]["enum"]]}
    if "email" in props:
        return {"subject": "s", "email": "e", "follow_up": "f", "linkedin": "l", "call_brief": ["a", "b", "c"]}
    if "scenes" in props and "stunts" in props["scenes"]["items"]["properties"]:
        nums = props["scenes"]["items"]["properties"]["scene"]["enum"]
        blank = {k: ([] if kind == "list" else False if kind == "flag" else 0) for k, (_, kind) in elements.FIELDS.items()}
        return {"scenes": [blank | {"scene": n, "notes": "", "background": "11-30" if n == 5 else "none",
                                    "stunts": ["Fall"] if n == 5 else [], "stunt_performers": 1 if n == 5 else 0} for n in nums]}
    if "scenes" in props:
        nums = props["scenes"]["items"]["properties"]["scene"]["enum"]
        return {"scenes": [{"scene": n, "country": "England", "place": "Dover", "evidence": "h", "explicit": True, "languages": []} for n in nums],
                "leads": [], "subject": ""}
    return {"leads": [{"name": n, "qualifies": "Unclear", "reason": ""} for n in props["leads"]["items"]["properties"]["name"]["enum"]],
            "a3": {"proposed": 4, "conservative": 0, "reason": "r"}, "b": {"proposed": 0, "conservative": 0, "reason": ""},
            "answers": {"A3": "a3", "B": "b"}}


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path))
    monkeypatch.setattr(jobs, "ensure_worker", lambda: None)            # jobs are run by hand below
    monkeypatch.setattr(llm, "resolve", lambda settings, mode=None, use="writing": (llm.Engine("openai", "http://127.0.0.1:1/v1", "gemma"), ""))
    monkeypatch.setattr(llm, "chat", fake_chat)
    from fastapi.testclient import TestClient
    from studio.server import app
    return TestClient(app)


def _intake(c, tool):
    return c.post("/api/tools/script/intake", data={"tool": tool}, files=[("files", ("ferry.fountain", FERRY))]).json()[0]["run_id"]


def _run_next():
    job = store.claim_job()
    jobs.HANDLERS[job["kind"]](job)
    return job


def test_brand_spotting_job_saves_and_downloads(client):
    rid = _intake(client, "brand")
    r = client.post("/api/tools/brand/spot", json={"run_ids": [rid], "options": {"avoid": ["Alcohol", "Nonsense"], "rating": "15"}}).json()
    assert r["queued"] == 1 and r["jobs"][0]["kind"] == "brandspot"
    assert _run_next()["options"]["brand"] == {"avoid": ["Alcohol"], "rating": "15", "withhold_title": False}
    run = client.get(f"/api/runs/brand/{rid}").json()
    assert run["outputs"]["brand_spotting"]["opportunities"] and run["summary"]["opportunities"] >= 1
    assert client.get(f"/api/runs/brand/{rid}/opportunities.xlsx").content[:2] == b"PK"
    assert client.post("/api/tools/brand/spot", json={"run_ids": []}).status_code == 400


def test_element_tagging_job_feeds_the_budget(client):
    rid = _intake(client, "schedule")
    assert client.post("/api/tools/schedule/elements", json={"run_ids": [rid]}).json()["queued"] == 1
    _run_next()
    run = client.get(f"/api/runs/schedule/{rid}").json()
    assert run["summary"]["elements_tagged"] == 14
    res = client.post("/api/tools/schedule/budget", json={"run_id": rid, "jurisdiction": "United Kingdom"}).json()
    lines = {l["description"] for l in res["budget"]["base"]["lines"]}
    assert "Stunt coordinator" in lines and "Background artists (from the script read)" in lines and res["elements"]["tagged"] == 14
    plain = client.post("/api/tools/schedule/budget", json={"run_id": rid, "jurisdiction": "United Kingdom", "use_elements": False}).json()
    assert "Stunt coordinator" not in {l["description"] for l in plain["budget"]["base"]["lines"]}
    xl = client.get(f"/api/runs/schedule/{rid}/budget.xlsx").content
    assert xl[:2] == b"PK"


def test_bfi_read_job_and_pack(client):
    rid = _intake(client, "coverage")
    assert client.post("/api/tools/bfi/read", json={"tool": "coverage", "run_id": rid}).json()["queued"] == 1
    assert client.post("/api/tools/bfi/read", json={"tool": "lookbook", "run_id": rid}).status_code == 400
    _run_next()
    res = client.get(f"/api/runs/coverage/{rid}").json()["outputs"]["bfi_read"]
    assert res["criteria"]["A1"]["proposed"] == 4 and {p["ref"]: p["status"] for p in res["answer_pack"]}["A3"] == "DO NOT SUBMIT"
    assert client.get(f"/api/runs/coverage/{rid}/bfi_pack.xlsx").content[:2] == b"PK"


def test_without_an_engine_the_ai_tools_say_so(client, monkeypatch):
    monkeypatch.setattr(llm, "resolve", lambda settings, mode=None, use="writing": (None, "No AI engine found on this computer."))
    rid = _intake(client, "brand")
    for path, body in (("/api/tools/brand/spot", {"run_ids": [rid]}), ("/api/tools/schedule/elements", {"run_ids": [rid], "tool": "brand"}),
                       ("/api/tools/bfi/read", {"tool": "brand", "run_id": rid})):
        r = client.post(path, json=body)
        assert r.status_code == 409 and "No AI engine" in r.json()["detail"]
