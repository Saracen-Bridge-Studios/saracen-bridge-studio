"""Coverage writer, job queue and branded report, with a fake model standing in for Gemma."""
import io
import json
import time
from pathlib import Path

import docx
import pytest
from fastapi.testclient import TestClient

from studio import coverage, jobs, llm, report, store

FIX = Path(__file__).parent / "fixtures"
CANNED = json.loads((FIX / "coverage_result.json").read_text())["sections"]
CALLS = []


def fake_chat(engine, system, user, *, schema=None, **kw):
    CALLS.append((system, user, schema, kw))
    keys = set(schema["properties"])
    if "beats" in keys:
        return {"beats": ["Mara hauls a crate.", "The fuel fails."], "characters": [{"name": "MARA", "note": "Keeper"}],
                "turning_points": [], "tone": "Bleak", "dialogue": "Spare", "production_demands": ["Night exteriors"]}
    for name, sec in CANNED.items():
        if keys == set(sec):
            return sec
    raise AssertionError(f"unexpected schema {keys}")


@pytest.fixture()
def fake_model(monkeypatch, tmp_path):
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path / "home"))
    monkeypatch.setattr(llm, "resolve", lambda s, mode=None: (llm.Engine("bundled", "", "gemma-fake"), ""))
    monkeypatch.setattr(llm, "chat", fake_chat)
    monkeypatch.setattr(jobs, "POLL", 0.05)
    CALLS.clear()


def test_spec_is_jons_skill_file():
    sp = coverage.spec()
    assert sorted(sp["sections"]) == list(range(1, 12))
    assert "senior Film and Television Development Executive" in sp["rules"]
    assert sp["sections"][10][0] == "WEIGHTED SCORING MATRIX"


def test_write_reads_in_parts_then_writes_sections(fake_model):
    data = (FIX / "sample.fountain").read_bytes()
    from studio import script
    b = script.parse("sample.fountain", data)
    res = coverage.write("sample.fountain", data, b, store.load_settings(), chunk_chars=400)
    reads = [c for c in CALLS if "beats" in c[2]["properties"]]
    assert len(reads) == 2 and len(CALLS) == 2 + 5
    assert "VERIFIED BREAKDOWN FACTS" in CALLS[-1][1] and "Scenes: 4" in CALLS[-1][1]
    assert "Never refer to ChatGPT" in CALLS[0][0]                    # Jon's house rules reach the model
    assert res["composite"] == pytest.approx(6.5) and res["verdict"] == "Consider"
    assert res["made_with"]["parts_read"] == 2


def test_composite_is_computed_not_taken_from_model():
    sec = json.loads(json.dumps(CANNED))
    sec["verdict"]["scores"] = {k: 10 for k in coverage.WEIGHTS} | {"Dialogue": 0}      # 0 is clamped to 1
    res = coverage.finish(sec, {"title": "T"}, llm.Engine("bundled", "", "m"), 1, 1)
    assert res["scores"]["Dialogue"] == 1 and res["composite"] == pytest.approx(9.1)
    assert any("G-01" in c for c in res["checks"])                                      # readiness 64 vs 91


def test_forbidden_mentions_are_flagged():
    sec = json.loads(json.dumps(CANNED))
    sec["market"]["risks"].append("See https://example.com, written by ChatGPT.")
    checks = coverage.finish(sec, {"title": "T"}, llm.Engine("bundled", "", "m"), 1, 1)["checks"]
    assert any("web address" in c for c in checks) and any("ChatGPT" in c for c in checks)


def test_report_is_built_on_jons_template():
    res = json.loads((FIX / "coverage_result.json").read_text())
    d = docx.Document(io.BytesIO(report.coverage_docx(res)))
    text = "\n".join(p.text for p in d.paragraphs)
    cells = "\n".join(c.text for t in d.tables for r in t.rows for c in r.cells)
    assert "SCRIPT COVERAGE REPORT" in text and "The Lighthouse Keeper" in text
    for h in report.SECTIONS:
        assert h in text
    assert "[" not in text.replace("[[", "") and "[D MONTH YYYY]" not in cells and "[ANALYST" not in cells   # no placeholders left
    assert "6.50 / 10" in cells and "Florence Pugh" in cells
    header = "".join(c.text for s in d.sections for t in s.header.tables for r in t.rows for c in r.cells)
    assert "SCRIPT COVERAGE REPORT  |  The Lighthouse Keeper" in header
    assert "DOCUMENT STANDARD" not in cells                               # template authoring note removed


def test_queue_writes_coverage_for_library_scripts(fake_model):
    from studio.server import app
    c = TestClient(app)
    files = [("files", (n, (FIX / n).read_bytes())) for n in ("sample.fountain", "sample.fdx")]
    rows = c.post("/api/tools/script/intake", data={"tool": "coverage"}, files=files).json()
    q = c.post("/api/tools/coverage/write", json={"missing": True}).json()
    assert q["queued"] == 2 and "gemma-fake" in q["engine"]
    assert c.post("/api/tools/coverage/write", json={"missing": True}).json()["queued"] == 2   # same jobs, not duplicated
    for _ in range(200):
        counts = c.get("/api/jobs", params={"kind": "coverage"}).json()["counts"]
        if counts.get("done") == 2:
            break
        time.sleep(0.05)
    assert counts == {"done": 2}
    run = c.get(f"/api/runs/coverage/{rows[0]['run_id']}").json()
    assert run["outputs"]["coverage"]["verdict"] == "Consider"
    assert any(f.endswith("Script Coverage.docx") for f in run["files"]) and "coverage.json" in run["files"]
    lib = c.get("/api/runs", params={"tool": "coverage"}).json()["runs"]
    assert all(r["summary"]["verdict"] == "Consider" for r in lib)
    assert c.post("/api/tools/coverage/write", json={"missing": True}).json()["queued"] == 0     # nothing left to do


def test_queue_survives_restart_and_cancel(tmp_path, monkeypatch):
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path / "home"))
    a = store.enqueue("coverage", "coverage", "r1", "One")
    b = store.enqueue("coverage", "coverage", "r2", "Two")
    assert store.claim_job()["id"] == a["id"]                     # r1 running when the app "crashes"
    assert store.requeue_interrupted() == 1 and store.get_job(a["id"])["status"] == "queued"
    store.cancel_job(b["id"])
    assert store.get_job(b["id"])["status"] == "cancelled"
    assert store.list_jobs("coverage")["counts"] == {"queued": 1, "cancelled": 1}


def test_coverage_needs_an_engine(tmp_path, monkeypatch):
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path / "home"))
    monkeypatch.setattr(llm, "OLLAMA_DEFAULT", "http://127.0.0.1:9")
    monkeypatch.setenv("STUDIO_LLM_DIR", str(tmp_path / "nothing"))
    from studio.server import app
    r = TestClient(app).post("/api/tools/coverage/write", json={"missing": True})
    assert r.status_code == 409 and "engine" in r.json()["detail"].lower()


def test_quick_is_default_and_deep_turns_thinking_on(fake_model):
    from studio import script
    data = (FIX / "sample.fountain").read_bytes()
    b = script.parse("sample.fountain", data)
    quick = coverage.write("sample.fountain", data, b, store.load_settings())
    assert quick["made_with"]["mode"] == "quick" and all(c[3]["think"] is False for c in CALLS)
    CALLS.clear()
    deep = coverage.write("sample.fountain", data, b, store.load_settings(), mode="deep")
    assert deep["made_with"]["mode"] == "deep" and all(c[3]["think"] is True for c in CALLS)
    assert CALLS[-1][3]["max_tokens"] > 6000                     # room to think before answering


def test_job_carries_the_mode(tmp_path, monkeypatch):
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path / "home"))
    j = store.enqueue("coverage", "coverage", "r1", "One", {"mode": "deep"})
    assert store.get_job(j["id"])["options"] == {"mode": "deep"}


def test_casting_names_checked_against_jons_actor_database():
    sec = json.loads(json.dumps(CANNED))
    sec["creative"]["casting"] = [{"role": "Mara", "names": ["Florence Pugh", "Anya Taylor game"]},
                                  {"role": "Tom", "names": ["Josh O’Connor", "Ben Whishield"]}]
    checks = coverage.finish(sec, {"title": "T"}, llm.Engine("bundled", "", "m"), 1, 1)["checks"]
    flagged = next(c for c in checks if "actor database" in c)
    assert "Anya Taylor game" in flagged and "Ben Whishield" in flagged
    assert "Florence Pugh" not in flagged and "Connor" not in flagged      # real names, curly apostrophe tolerated


def test_comparables_are_titles_with_years():
    item = coverage.MARKET["properties"]["comparables"]["items"]
    assert set(item["properties"]) == {"title", "year", "relevance"}
    assert coverage.comparable_text({"title": "Enys Men", "year": 2022, "relevance": "x"}) == "Enys Men (2022): x"
