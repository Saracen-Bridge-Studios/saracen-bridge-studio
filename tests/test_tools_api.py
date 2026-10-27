"""Every tool endpoint, end to end through the local API."""
from pathlib import Path

import openpyxl
import pytest
from fastapi.testclient import TestClient

FIX = Path(__file__).parent / "fixtures"


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path / "home"))
    from studio.server import app
    return TestClient(app)


def test_catalog_lists_all_tools(client):
    ids = [t["id"] for t in client.get("/api/catalog").json()["tools"]]
    assert ids == ["coverage", "lookbook", "casting", "schedule", "incentives", "bfi", "sales", "agents", "brand",
                   "finance", "greenlight", "agreement", "aiden", "frat"]


def test_script_batch_intake_all_formats(client):
    files = [("files", (n, (FIX / n).read_bytes())) for n in ("sample.fountain", "sample.fdx", "sample.pdf")]
    res = {r["file"]: r for r in client.post("/api/tools/script/intake", data={"tool": "coverage"}, files=files).json()}
    assert res["sample.fountain"]["scene_count"] == 4 and res["sample.fountain"]["speaking_roles"] == 3
    assert res["sample.fdx"]["scene_count"] == 2 and res["sample.fdx"]["speaking_roles"] == 2
    assert res["sample.pdf"]["scene_count"] == 4 and res["sample.pdf"]["pages_estimated"] is False
    assert res["sample.pdf"]["title"] == "The Lighthouse Keeper"     # "Title:" label stripped
    lib = client.get("/api/runs", params={"tool": "coverage"}).json()
    assert lib["total"] == 3 and len({r["id"] for r in lib["runs"]}) == 3   # same title, same second: no overwrite
    detail = client.get(f"/api/runs/coverage/{lib['runs'][0]['id']}").json()
    assert "breakdown" in detail["outputs"]
    assert client.get("/api/runs", params={"q": "radio"}).json()["total"] == 1


def test_redropped_scripts_are_skipped_so_batches_resume(client):
    files = lambda: [("files", (n, (FIX / n).read_bytes())) for n in ("sample.fountain", "sample.fdx")]
    first = client.post("/api/tools/script/intake", data={"tool": "coverage"}, files=files()).json()
    again = client.post("/api/tools/script/intake", data={"tool": "coverage"}, files=files()).json()
    assert not any(r["duplicate"] for r in first) and all(r["duplicate"] for r in again)
    assert [r["run_id"] for r in again] == [r["run_id"] for r in first]
    assert again[0]["scene_count"] == 4
    assert client.get("/api/runs").json()["total"] == 2


def test_library_index_rebuilds_from_folders(client, tmp_path):
    client.post("/api/tools/script/intake", files=[("files", ("sample.fountain", (FIX / "sample.fountain").read_bytes()))])
    (tmp_path / "home" / "library.db").unlink()
    assert client.get("/api/runs").json()["total"] == 1


def test_bad_file_does_not_stop_batch(client):
    files = [("files", ("broken.fdx", b"<not xml")), ("files", ("sample.fountain", (FIX / "sample.fountain").read_bytes()))]
    res = client.post("/api/tools/script/intake", files=files).json()
    assert "error" in res[0] and res[1]["scene_count"] == 4


def test_coverage_matrix(client):
    s = {k: 7 for k in client.get("/api/tools/coverage/weights").json()}
    assert client.post("/api/tools/coverage/score", json=s).json()["composite"] == 7.0
    s["Dialogue"] = None
    assert client.post("/api/tools/coverage/score", json=s).json()["missing"] == ["Dialogue"]


def test_incentives_calc_matches_jon_regression(client):
    res = client.post("/api/tools/incentives/calc", json={"routes": [
        {"programme_id": "ESP-NAT-FOR", "qualifying_spend": 6_000_000, "project_cost": 10_000_000, "eligibility": "Eligible"},
        {"programme_id": "GBR-IFTC", "qualifying_spend": 6_000_000, "project_cost": 10_000_000, "eligibility": "Eligible"}]}).json()
    assert res[0]["gross_benefit"] == pytest.approx(1_550_000) and res[1]["net_after_tax"] == pytest.approx(2_385_000)
    assert len(client.get("/api/tools/incentives/programmes").json()) == 69


def test_bfi_pass_borderline_and_golden_rule(client):
    crit = client.get("/api/tools/bfi/criteria").json()
    assert sum(c["max_points"] for c in crit) == 37   # raw maxima; C1 cap (6 -> 4) brings the test to 35
    strong = {"A1": 4, "A2": 4, "A4": 6, "C1(a)": 2, "C1(b)": 2, "C1(c)": 2, "C2": 1, "D1": 1, "D2": 1, "D3": 1}
    weak = {"A4": 6, "C1(a)": 2, "D1": 1}
    r = client.post("/api/tools/bfi/assess", json={"proposed": strong, "conservative": weak}).json()
    assert r["proposed"]["sections"]["C"] == 5 and r["proposed"]["passed"] and r["verdict"] == "BORDERLINE"
    golden = {"A4": 6, "C1(a)": 2, "C1(b)": 2, "C2": 1, **{f"D{i}": 1 for i in range(1, 9)}}
    g = client.post("/api/tools/bfi/assess", json={"proposed": golden, "conservative": golden}).json()
    assert g["proposed"]["total"] == 19 and g["proposed"]["golden_rule_failed"] and g["verdict"] == "FAIL"


def test_finance_plan_catches_shade_double_count(client):
    ex = client.get("/api/tools/finance/example").json()
    ok = client.post("/api/tools/finance/plan", json=ex).json()
    assert ok["residual_debt_needed"] == pytest.approx(3_168_657.42, abs=1) and not ok["double_count"]
    bad = dict(ex, sources=ex["sources"] + [{"id": "nonstop", "name": "Non-Stop package total", "amount": 4484446.89,
                                              "status": "User instruction / to document"}])
    r = client.post("/api/tools/finance/plan", json=bad).json()
    assert r["double_count"] and r["residual_debt_needed"] == pytest.approx(3_168_657.42, abs=1)


def test_greenlight_rules(client):
    base = dict(overall=92, finance=91, legal=88, bond_insurance=93, production_delivery=86,
                critical_blockers=0, funding_gap=False, signoffs_approved=True)
    assert client.post("/api/tools/greenlight/decide", json=base).json()["decision"] == "GREENLIGHT READY"
    assert client.post("/api/tools/greenlight/decide", json=base | {"overall": 50}).json()["decision"].startswith("DEVELOPMENT")
    assert client.post("/api/tools/greenlight/decide", json=base | {"funding_gap": True}).json()["decision"].startswith("HOLD")
    assert client.post("/api/tools/greenlight/decide", json=base | {"signoffs_approved": False, "cures_owned_and_timed": True}).json()["decision"] == "CONDITIONAL GREENLIGHT"


def test_agreement_blank_and_validation_errors_reported(client):
    blank = client.get("/api/tools/agreement/blank")
    assert blank.status_code == 200 and len(blank.content) > 10_000
    r = client.post("/api/tools/agreement/build", files={"file": ("in.xlsx", blank.content)}, data={"draft_name": "T_DRAFT_01"}).json()
    assert r["ok"] in (True, False)       # an empty workbook may validate with every field Unknown
    if not r["ok"]:
        assert r["error"]


def test_lookups(client):
    assert client.get("/api/lookup/directors", params={"q": "Nolan"}).json()
    assert len(client.get("/api/lookup/brands").json()) == 110
    rates = client.get("/api/lookup/rates", params={"jurisdiction": "Spain", "q": "Gaffer"}).json()
    assert "Spain" in rates["jurisdictions"] and rates["basis"] == "official_plus_market" and rates["rows"][0]["d1"] > 0
    uk = client.get("/api/lookup/rates", params={"jurisdiction": "United Kingdom", "q": "Gaffer"}).json()
    assert uk["basis"] == "four_tier" and uk["rows"][0]["d1"] == 420 and uk["labels"][0] == "Tier 1 / day"
    d = client.get("/api/lookup/directors", params={"q": "Nolan"}).json()[0]
    assert "nationality_base" not in d and "representation" not in d       # personal data kept out


def test_name_finder_narrows_as_you_type(client):
    """Tim, 13 Oct: typing "chris" narrows to the Chrises, first names first; accents don't matter; a pick fills the profile."""
    names = lambda q, kind="actors": [r["actor" if kind == "actors" else "director_name"] for r in client.get(f"/api/lookup/{kind}", params={"q": q, "limit": 12}).json()]
    chris = names("chris")
    assert chris[:4] == ["Chris Evans", "Chris Hemsworth", "Chris Pratt", "Chris Rock"] and len(chris) <= 12
    assert names("chris hem") == ["Chris Hemsworth"]                    # every word typed must match
    assert names("timothee") == ["Timothée Chalamet"] and names("cuaron", "directors") == ["Alfonso Cuarón"]
    assert names("zzzz") == []
    a = client.get("/api/lookup/actor", params={"name": "Chris Evans"}).json()
    assert a["indicative_cash_fee_high_usd"] > a["indicative_cash_fee_low_usd"] > 0 and a["optimal_budget_floor_usd"] and "gender" not in a
    did = client.get("/api/lookup/directors", params={"q": "nolan"}).json()[0]["director_id"]
    d = client.get("/api/lookup/director", params={"id": did}).json()
    assert d["fee_high"] > d["fee_mid"] > d["fee_low"] > 0 and d["proven_maximum_budget_usd"]
    assert not {"nationality_base", "representation", "reputational_or_production_concerns", "known_cast_relationships"} & set(d)
    assert client.get("/api/lookup/actor", params={"name": "Nobody Real"}).status_code == 404
    assert client.get("/api/lookup/director", params={"id": "SB-DIR-9999"}).status_code == 404


def test_external_app_unconfigured_is_clear(client):
    r = client.post("/api/external/aiden/launch")
    assert r.status_code == 409 and "Settings" in r.json()["detail"]


def test_ai_status_without_engine(client):
    assert client.get("/api/ai/status").json()["connected"] is False


def test_heartbeat_recorded(client):
    from studio import server
    assert client.post("/api/heartbeat").json()["ok"] and server.last_heartbeat() is not None


@pytest.fixture(autouse=True)
def _fresh_launcher_state():
    import studio_launcher as L
    L._browser_opened = False
    yield
    L._browser_opened = False


def test_launcher_browser_mode_stops_when_page_goes_quiet(monkeypatch):
    import studio_launcher as L
    from studio import server
    opened = []
    monkeypatch.setattr(L.webbrowser, "open", opened.append)
    monkeypatch.setattr(L.time, "sleep", lambda s: None)
    server._HEARTBEAT[:] = [0.0]                          # last check-in long ago
    L.browser_until_idle("http://127.0.0.1:1/", idle_seconds=300)
    assert opened == ["http://127.0.0.1:1/"]


def test_launcher_skips_native_window_without_webview2(monkeypatch):
    import studio_launcher as L
    monkeypatch.setattr(L, "webview2_installed", lambda: False)
    assert L.native_window("http://127.0.0.1:1/") is False


def _fake_webview(monkeypatch, start):
    import sys, types
    class Ev:
        def __init__(self): self.handlers = []
        def __iadd__(self, f): self.handlers.append(f); return self
        def fire(self): [h() for h in self.handlers]
    win = types.SimpleNamespace(events=types.SimpleNamespace(loaded=Ev()))
    mod = types.ModuleType("webview")
    mod.create_window = lambda *a, **k: win
    mod.start = lambda **k: start(win)
    monkeypatch.setitem(sys.modules, "webview", mod)
    return win


def test_launcher_window_that_never_shows_falls_back_to_browser(monkeypatch, tmp_path):
    """13 Oct, Tim's PC: the engine started but the window never appeared and nothing said so."""
    import threading
    import studio_launcher as L
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path / "home"))
    monkeypatch.setattr(L, "webview2_installed", lambda: True)
    release, stuck = threading.Event(), threading.Event()
    _fake_webview(monkeypatch, lambda win: release.wait(5))          # the window call blocks and never loads
    def on_stuck():
        stuck.set(); release.set()
    assert L.native_window("http://127.0.0.1:1/", load_seconds=0.2, on_stuck=on_stuck) is False
    assert stuck.is_set() and L.window_failed_before()               # next start goes straight to the browser


def test_launcher_window_closed_before_loading_falls_back(monkeypatch, tmp_path):
    import studio_launcher as L
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path / "home"))
    monkeypatch.setattr(L, "webview2_installed", lambda: True)
    _fake_webview(monkeypatch, lambda win: None)                      # returns at once, page never loaded
    assert L.native_window("http://127.0.0.1:1/", load_seconds=5) is False and L.window_failed_before()


def test_launcher_working_window_clears_the_failure_note(monkeypatch, tmp_path):
    import time
    import studio_launcher as L
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path / "home"))
    monkeypatch.setattr(L, "webview2_installed", lambda: True)
    L.remember_window_failed()
    def start(win):
        win.events.loaded.fire(); time.sleep(0.3)                    # page loads, user closes the window later
    _fake_webview(monkeypatch, start)
    assert L.native_window("http://127.0.0.1:1/", load_seconds=5) is True and not L.window_failed_before()


def test_launcher_failed_window_does_not_trigger_the_watchdog_later(monkeypatch, tmp_path):
    """Seen under Wine: the window failed at once, the browser opened, then the watchdog fired and stopped the app."""
    import time
    import studio_launcher as L
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path / "home"))
    monkeypatch.setattr(L, "webview2_installed", lambda: True)
    def start(win):
        raise RuntimeError("Failed to create a .NET runtime")
    _fake_webview(monkeypatch, start)
    fired = []
    assert L.native_window("http://127.0.0.1:1/", load_seconds=0.2, on_stuck=lambda: fired.append(1)) is False
    time.sleep(0.4)
    assert fired == []


def test_launcher_windows_default_falls_back_from_edge_to_browser_to_message(monkeypatch):
    """0.3.4: Edge app window first; if it never shows the page, the default browser; then a message with the address."""
    import studio_launcher as L
    calls = []
    monkeypatch.setattr(L, "wait_until_idle", lambda *a, **k: calls.append("idle"))
    monkeypatch.setattr(L, "open_app_window", lambda url: calls.append("edge") or True)
    monkeypatch.setattr(L, "open_default_browser", lambda url: calls.append("browser") or True)
    monkeypatch.setattr(L, "_say_where", lambda url: calls.append("message"))
    pages = iter([False, True])                                   # Edge never checks in; the browser tab does
    monkeypatch.setattr(L, "wait_for_page", lambda s: next(pages))
    L.app_window_until_idle("http://127.0.0.1:1/", connect_seconds=0)
    assert calls == ["edge", "browser", "idle"]
    calls.clear(); L._browser_opened = False
    monkeypatch.setattr(L, "wait_for_page", lambda s: False)      # nothing ever shows the page
    L.app_window_until_idle("http://127.0.0.1:1/", connect_seconds=0)
    assert calls == ["edge", "browser", "message", "idle"]
    calls.clear(); L._browser_opened = False
    monkeypatch.setattr(L, "wait_for_page", lambda s: True)       # the normal case: Edge window opens
    L.app_window_until_idle("http://127.0.0.1:1/", connect_seconds=0)
    assert calls == ["edge", "idle"]


def test_launcher_page_check_in_counts_as_shown(monkeypatch):
    import studio_launcher as L
    from studio import server
    server._HEARTBEAT[:] = []
    assert L.wait_for_page(0.2) is False
    server._HEARTBEAT[:] = [1.0]
    assert L.wait_for_page(0.2) is True


def test_a_retried_job_replaces_its_failure(tmp_path, monkeypatch):
    """Tim's queue, 13 Oct: two failed SNOWSTORM attempts kept counting as failed after a new attempt was queued."""
    from studio import store
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path))
    first = store.enqueue("coverage", "coverage", "run-1", "SNOWSTORM")
    store.set_job(first["id"], status="error", error="OutputError: x")
    other = store.enqueue("coverage", "coverage", "run-2", "KNOWN ASSOCIATE")
    store.set_job(other["id"], status="error", error="OutputError: x")
    assert store.list_jobs("coverage")["counts"].get("error") == 2
    again = store.enqueue("coverage", "coverage", "run-1", "SNOWSTORM")
    counts = store.list_jobs("coverage")["counts"]
    assert counts.get("error") == 1 and counts.get("queued") == 1 and store.get_job(first["id"])["status"] == "retried"
    assert again["id"] != first["id"]


def test_failed_jobs_clear_one_or_all(client):
    """Tim, 13 Oct: an individual clear per failed row, and a full clear; done jobs and the Library are untouched."""
    from studio import store
    a = store.enqueue("coverage", "coverage", "run-a", "KNOWN ASSOCIATE"); store.set_job(a["id"], status="error", error="x")
    b = store.enqueue("coverage", "coverage", "run-b", "SNOWSTORM"); store.set_job(b["id"], status="error", error="x")
    c = store.enqueue("coverage", "coverage", "run-c", "WEREWOLF"); store.set_job(c["id"], status="done")
    assert client.post("/api/jobs/clear", json={"kind": "coverage", "id": a["id"]}).json()["cleared"] == 1
    counts = client.get("/api/jobs", params={"kind": "coverage"}).json()["counts"]
    assert counts.get("error") == 1 and counts.get("done") == 1
    assert client.post("/api/jobs/clear", json={"kind": "coverage", "id": c["id"]}).json()["cleared"] == 0   # done stays
    assert client.post("/api/jobs/clear", json={"kind": "coverage"}).json()["cleared"] == 1
    counts = client.get("/api/jobs", params={"kind": "coverage"}).json()["counts"]
    assert not counts.get("error") and counts.get("done") == 1
    assert client.post("/api/jobs/retry", json={"kind": "coverage"}).json()["requeued"] == 0              # cleared isn't retried


def test_brand_shortlist_and_script_targets(client):
    """Tim, 13 Oct: click brands to add as many as you like; a script read for Brand takes them as its targets."""
    some = client.get("/api/lookup/brands", params={"q": "a"}).json()[:3]
    ids = [b["brand_id"] for b in some]
    assert client.get("/api/brand/shortlist").json()["brands"] == []
    saved = client.put("/api/brand/shortlist", json={"ids": ids + [ids[0], "SB-BR-NOPE"]}).json()["brands"]
    assert [b["brand_id"] for b in saved] == ids                                    # order kept, duplicates and unknowns dropped
    assert [b["brand_id"] for b in client.get("/api/brand/shortlist").json()["brands"]] == ids
    csv_text = client.get("/api/brand/shortlist.csv").text.lstrip("﻿")
    assert csv_text.splitlines()[0].startswith("Brand,Parent company") and some[0]["brand_name"] in csv_text
    files = [("files", ("sample.fountain", (FIX / "sample.fountain").read_bytes()))]
    run = client.post("/api/tools/script/intake", data={"tool": "brand"}, files=files).json()[0]
    assert run["brand_targets"] == 3
    detail = client.get(f"/api/runs/brand/{run['run_id']}").json()
    assert [b["brand_id"] for b in detail["outputs"]["brand_targets"]] == ids
    client.put("/api/brand/shortlist", json={"ids": ids[:1]})
    t = client.put(f"/api/runs/brand/{run['run_id']}/targets", json={"ids": ids[:1]}).json()["brand_targets"]
    assert len(t) == 1 and some[0]["brand_name"] in client.get("/api/brand/shortlist.csv", params={"run": run["run_id"]}).text
    cov = client.post("/api/tools/script/intake", data={"tool": "coverage"}, files=files).json()[0]
    assert "brand_targets" not in cov                                                 # only Brand scripts take targets


def test_visual_feedback_is_coming_soon(client):
    tools = {t["id"]: t for t in client.get("/api/catalog").json()["tools"]}
    assert tools["frat"].get("coming_soon") and tools["aiden"].get("coming_soon")
    assert any("F.R.A.T." in x for x in tools["brand"]["needs_ai"])


def test_wrong_or_blank_workbook_and_unknown_programme_say_so_in_words(client):
    """15 Oct audit: a workbook that isn't the input workbook showed a raw validation report and a temp path; a blank one
    said 'Term sheet built'; an unknown incentive programme was a 500."""
    root = Path(__file__).resolve().parents[1]
    wrong = (root / "data" / "oracle" / "SB_Global_Production_Rate_Database_v1_2.xlsx").read_bytes()
    r = client.post("/api/tools/agreement/build", files={"file": ("rates.xlsx", wrong)}, data={"draft_name": "X"}).json()
    assert r["ok"] is False and "isn't the Studio's input workbook" in r["error"] and "/tmp" not in r["error"] and "validation.json" not in r["error"]
    r = client.post("/api/tools/agreement/build", files={"file": ("notes.xlsx", b"not a workbook")}, data={"draft_name": "Y"}).json()
    assert r["ok"] is False and "can't be opened" in r["error"]
    blank = client.get("/api/tools/agreement/blank").content
    r = client.post("/api/tools/agreement/build", files={"file": ("blank.xlsx", blank)}, data={"draft_name": "Z"}).json()
    assert r["ok"] and r["population"]["populated"] == 0                 # the UI says nothing was filled in
    bad = client.post("/api/tools/incentives/calc", json={"routes": [{"programme_id": "NOPE-1", "qualifying_spend": 1}]})
    assert bad.status_code == 400 and "Unknown programme" in bad.json()["detail"]


def test_saved_runs_of_every_tool_carry_what_the_library_view_needs(client):
    client.post("/api/tools/incentives/calc", json={"title": "T", "routes": [{"programme_id": "GBR-AVEC", "qualifying_spend": 2_000_000, "eligibility": "Eligible"}]})
    client.post("/api/tools/bfi/assess", json={"title": "T", "proposed": {"A1": 4}, "conservative": {"A1": 2}})
    ex = client.get("/api/tools/finance/example").json()
    client.post("/api/tools/finance/plan", json={"title": "T", "currency": ex["currency"], "gross_budget": ex["gross_budget"], "sources": ex["sources"]})
    client.post("/api/tools/greenlight/decide", json={"overall": 80, "finance": 80, "legal": 80, "bond_insurance": 80, "production_delivery": 80})
    runs = {r["tool"]: r for r in client.get("/api/runs?limit=20").json()["runs"]}
    need = {"incentives": lambda o: o["results"][0]["net_after_tax"] is not None, "bfi": lambda o: o["proposed"]["sections"] and o["verdict"],
            "finance": lambda o: "residual_debt_needed" in o and "bankable" in o, "greenlight": lambda o: o["decision"] and "reasons" in o}
    for tool, ok in need.items():
        rec = client.get(f"/api/runs/{tool}/{runs[tool]['id']}").json()
        assert ok(rec["outputs"]) and rec["inputs"], tool
