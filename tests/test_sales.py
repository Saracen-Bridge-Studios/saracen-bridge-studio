"""Sales Estimates territory valuation (1.0.5): Jon's Sales Valuation Engine v4.1 evaluated in the Studio.

The golden file is LibreOffice's recalculation of Jon's workbook filled with tests/fixtures/sales_sample_project.py
(deals in three territories with adjustment factors, public proxies in two, a worldwide anchor, cast, director, rights
and finance): the Studio must reproduce it cell for cell."""
import copy
import importlib.util
import json
import shutil
import subprocess
from pathlib import Path

import openpyxl
import pytest
from fastapi.testclient import TestClient

from studio import sales

FIX = Path(__file__).parent / "fixtures"
_spec = importlib.util.spec_from_file_location("sales_sample_project", FIX / "sales_sample_project.py")
SAMPLE = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(SAMPLE)
SAMPLE = SAMPLE.SAMPLE
GOLD = json.loads((FIX / "sales_golden_libreoffice.json").read_text())
COLS = ("ask", "expected", "take", "bankable", "confidence", "evidence_count", "status")


def same(a, b):
    if a in (None, "") and b in (None, ""):
        return True
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return abs(a - b) <= 1e-6 * max(1, abs(a))
    return a == b


def assert_matches_gold(res):
    for g, t in zip(GOLD["territories"], res["territories"]):
        assert g["territory"] == t["territory"]
        for k in COLS:
            assert same(g[k], t[k]), (t["territory"], k, g[k], t[k])
    for k, v in GOLD["summary"].items():
        assert same(v, res["summary"][k]), k
    assert res["finance"]["lender_result"] == GOLD["lender_result"] and same(GOLD["bankable"], res["finance"]["bankable"])


def test_the_engine_reproduces_jons_workbook_and_resets_between_projects():
    res = sales.evaluate(SAMPLE)
    assert_matches_gold(res)
    usa = res["territories"][0]
    assert usa["territory"] == "USA" and usa["evidence_count"] == 3 and usa["basis"] == "Verified transaction model"
    assert {t["method"] for t in res["territories"]} >= {"Selected verified deal evidence", "Direct public buyer-capacity proxy", "Worldwide anchor allocation"}
    china = next(t for t in res["territories"] if t["territory"] == "China")
    assert china["status"] == "NO VALUE"                                       # rights unavailable there
    assert res["controls"] == {"order": "PASS", "fx": "PASS", "selection": "PASS"}
    empty = sales.evaluate({})                                                 # nothing carries over from the last project
    assert {t["status"] for t in empty["territories"]} == {"NO VALUE"} and empty["summary"]["ask"] == 0
    assert empty["controls"]["fx"] == "NO DEALS LOADED"
    fewer = copy.deepcopy(SAMPLE)
    fewer["deals"], fewer["proxies"], fewer["anchor"] = fewer["deals"][:2], [], {}
    f = sales.evaluate(fewer)
    assert [t["territory"] for t in f["territories"] if t["status"] == "Complete"] == ["USA"]
    assert_matches_gold(sales.evaluate(SAMPLE))                                # and back again, same numbers


def test_the_evaluator_reproduces_every_formula_in_jons_workbook():
    """All 21,759 formulas, blank workbook, against the values Excel saved in Jon's file."""
    import datetime
    from studio import xlcalc
    wb = openpyxl.load_workbook(sales.WORKBOOK)
    cached = openpyxl.load_workbook(sales.WORKBOOK, data_only=True)
    book = xlcalc.Book(wb)
    bad = []
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value, str) and c.value.startswith("="):
                    want = cached[ws.title][c.coordinate].value
                    got = book.evaluate(f"{ws.title}!{c.coordinate}")
                    if hasattr(want, "year"):
                        want = (want - datetime.datetime(1899, 12, 30)).total_seconds() / 86400
                    got = got.code if isinstance(got, xlcalc.Err) else got
                    if not same(want, got):
                        bad.append((ws.title, c.coordinate, want, got))
    assert not bad, bad[:5]


def test_formula_rules_that_matter():
    from studio import xlcalc
    import openpyxl as ox
    wb = ox.Workbook()
    ws = wb.active
    ws.title = "S"
    for addr, v in {"A1": 0.1, "A2": 0.2, "A3": "x", "B1": "=A1+A2=0.3", "B2": "=C9", "B3": "=IF(C9=\"\",\"blank\",\"no\")",
                    "B4": "=SUMPRODUCT(--(A1:A2<1))", "B5": "=COUNTIF(A1:A3,\"?*\")", "B6": "=MAX(C9,1-2)", "B7": "=IFERROR(1/0,\"e\")",
                    "B8": "=QUARTILE(A1:A3,1)", "B9": "=MATCH(\"X\",A1:A3,0)", "B10": "=-2^2", "B11": "=\"a\"&1&TRUE"}.items():
        ws[addr] = v
    b = xlcalc.Book(wb)
    ev = lambda a: b.evaluate(f"S!{a}")
    assert ev("B1") is True and ev("B2") == 0 and ev("B3") == "blank" and ev("B4") == 2 and ev("B5") == 1
    assert ev("B6") == -1 and ev("B7") == "e" and ev("B8") == pytest.approx(0.125) and ev("B9") == 3 and ev("B10") == 4 and ev("B11") == "a1TRUE"


def test_fx_comes_from_jons_ecb_table_not_the_gbp_identity_rate():
    fx = sales.fx_rates()
    assert fx["USD"] == 1 and 1.2 < fx["GBP"] < 1.5 and 1.0 < fx["EUR"] < 1.3
    assert sales.fx_rates({"JPY": 0.0066})["JPY"] == 0.0066
    w = sales.writes({"deals": [{"id": "D1", "territory": "USA", "currency": "GBP", "amount": 1}]})
    gbp_row = 5 + sales.FX_ORDER.index("GBP")
    assert w[f"FX_RATES!C{gbp_row}"] == pytest.approx(fx["GBP"])


def test_package_records_map_jons_databases():
    a = sales.actor_record("Chris Evans")
    assert a["score"] and 0 <= a["territory_score"] <= 5 and a["confidence"] in "ABCD"
    d = sales.director_record("Christopher Nolan")
    assert d["score"] > 90 and d["confidence"] == "A"
    assert sales.actor_record("Nobody Atall") is None


def test_api_values_saves_and_exports_the_filled_workbook(tmp_path, monkeypatch):
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path))
    from studio.server import app
    c = TestClient(app)
    opts = c.get("/api/tools/sales/engine/options").json()
    assert len(opts["territories"]) == 33 and len(opts["intake"]) == 27 and "Pay-or-play" in opts["attachment"]
    r = c.post("/api/tools/sales/value", json={"project": SAMPLE}).json()
    assert r["title"] == "Night Ferry" and same(r["summary"]["ask"], GOLD["summary"]["ask"])
    again = c.post("/api/tools/sales/value", json={"run_id": r["run_id"], "project": SAMPLE}).json()
    assert again["run_id"] == r["run_id"]                                      # updated in place, not a second item
    runs = c.get("/api/runs?tool=sales").json()
    assert runs["total"] == 1 and runs["runs"][0]["summary"]["valued"] >= 20
    rec = c.get(f"/api/runs/sales/{r['run_id']}").json()
    assert rec["inputs"]["deals"][0]["id"] == "D1" and rec["outputs"]["valuation"]["controls"]["order"] == "PASS"
    x = c.get(f"/api/runs/sales/{r['run_id']}/engine.xlsx")
    wb = openpyxl.load_workbook(__import__("io").BytesIO(x.content))
    assert wb["DEAL_LOG"]["A5"].value == "D1" and wb["PROJECT_INTAKE"]["B6"].value == "Night Ferry"
    assert str(wb["VALUATION_OUTPUT"]["J7"].value).startswith("=")             # his formulas are still there for Excel


@pytest.mark.skipif(not shutil.which("soffice") and not shutil.which("libreoffice"), reason="LibreOffice not installed")
def test_golden_file_is_what_libreoffice_calculates(tmp_path):
    """Rebuild the golden file's reference: fill the workbook, let LibreOffice recalculate it, compare."""
    f = tmp_path / "filled.xlsx"
    f.write_bytes(sales.workbook_bytes(SAMPLE))
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    subprocess.run([soffice, "--headless", "--convert-to", "xlsx", "--outdir", str(tmp_path / "out"), str(f)], check=True, timeout=300,
                   capture_output=True)
    lo = openpyxl.load_workbook(tmp_path / "out" / "filled.xlsx", data_only=True)["CONTROLLED_OUTPUT"]
    for i, g in enumerate(GOLD["territories"]):
        for k, col in zip(COLS, "IJKNOPR"):
            assert same(g[k], lo[f"{col}{15 + i}"].value), (g["territory"], k)


def test_genre_and_subgenre_come_from_tims_list(tmp_path, monkeypatch):
    """20 Oct (1.1.2): Genre and Subgenre are dropdowns from Tim's list. Jon's engine uses the genre in its narrative
    only, so a genre outside his own twelve values the same and writes through to the workbook."""
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path))
    from studio.server import app
    c = TestClient(app)
    g = {x["genre"]: x["subgenres"] for x in c.get("/api/tools/sales/engine/options").json()["genres"]}
    assert len(g) == 18 and "Folk horror" in g["Horror"] and "Heist" in g["Crime"] and "Spaghetti western" in g["Western"]
    assert all(len(v) >= 8 for v in g.values())
    base = c.post("/api/tools/sales/value", json={"project": SAMPLE}).json()
    tagged = dict(SAMPLE, intake=dict(SAMPLE["intake"], genre="Horror", subgenre="Folk horror"))
    r = c.post("/api/tools/sales/value", json={"project": tagged}).json()
    assert same(r["summary"]["ask"], base["summary"]["ask"])
    x = c.get(f"/api/runs/sales/{r['run_id']}/engine.xlsx")
    wb = openpyxl.load_workbook(__import__("io").BytesIO(x.content))
    assert wb["PROJECT_INTAKE"]["B7"].value == "Horror" and wb["PROJECT_INTAKE"]["B8"].value == "Folk horror"


def test_tims_intake_changes_22_oct(tmp_path, monkeypatch):
    """1.1.3: Tone and Co-production gone (and not counted as missing), Tim's dropdown choices, festivals ticked from a
    list, Feature or Episodic. None of it changes the figures: Jon's engine uses these fields for narrative only."""
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path))
    from studio.server import app
    c = TestClient(app)
    o = c.get("/api/tools/sales/engine/options").json()
    keys = [f["key"] for f in o["intake"]]
    assert "tone" not in keys and "coproduction" not in keys and "subgenre" in keys
    ch = o["choices"]
    assert ch["script_status"] == ["Development", "Final"] and "Completed film" in ch["sales_stage"]
    assert ch["release_model"]["Episodic"] == ["Straight to streaming", "Straight to TV"]
    assert ch["release_model"]["Feature"] == ["Theatrical", "VOD", "TVOD", "Straight to streaming", "Straight to TV"]
    assert {"Cannes", "Venice", "Berlinale", "Sundance", "Toronto (TIFF)"} <= set(ch["festivals"])
    base = c.post("/api/tools/sales/value", json={"project": SAMPLE}).json()
    intake = {k: v for k, v in SAMPLE["intake"].items() if k not in ("tone", "coproduction")}
    intake.update(script_status="Final", sales_stage="Pre-sale", format="Episodic", episodes=8, runtime=45,
                  release_model="Direct to streaming", festival={"festivals": ["Cannes", "Toronto (TIFF)"], "note": "Market screening at AFM"})
    r = c.post("/api/tools/sales/value", json={"project": dict(SAMPLE, intake=intake)}).json()
    assert same(r["summary"]["ask"], base["summary"]["ask"])
    wb = openpyxl.load_workbook(__import__("io").BytesIO(c.get(f"/api/runs/sales/{r['run_id']}/engine.xlsx").content))
    ws = wb["PROJECT_INTAKE"]
    assert ws["B28"].value == "Cannes; Toronto (TIFF); Market screening at AFM" and ws["B27"].value == "Straight to streaming"   # saved before 1.1.5: new name
    assert ws["C9"].value == "Optional" and ws["C16"].value == "Optional" and ws["B33"].value.startswith("Episodic, 8 episodes")
    assert r["summary"]["intake_completeness"] >= base["summary"]["intake_completeness"]


def test_logline_and_synopsis_come_from_the_scripts_coverage(tmp_path, monkeypatch):
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path))
    from studio import store
    from studio.server import app
    c = TestClient(app)
    cov = {"sections": {"story": {"logline": "A lighthouse keeper hears a voice in the storm.", "synopsis": ["Part one.", "Part two."]}}}
    rec = store.save_run("coverage", "The Lighthouse Keeper", {"file": "k.pdf", "sha256": "abc"}, {"breakdown": {}, "coverage": cov})
    sched = store.save_run("schedule", "The Lighthouse Keeper", {"file": "k.pdf", "sha256": "abc"}, {"breakdown": {}})
    for tool, rid in (("coverage", rec["id"]), ("schedule", sched["id"])):      # the schedule copy finds the same file's coverage
        pre = c.get(f"/api/tools/sales/engine/prefill?tool={tool}&run_id={rid}").json()
        assert pre["logline"] == "A lighthouse keeper hears a voice in the storm.\n\nPart one.\n\nPart two." and pre["logline_from"] == "coverage"
    bare = store.save_run("schedule", "Radio Night", {"file": "r.pdf", "sha256": "zzz"}, {"breakdown": {}})
    assert "logline" not in c.get(f"/api/tools/sales/engine/prefill?tool=schedule&run_id={bare['id']}").json()


def test_release_routes_in_order_and_casting_director(tmp_path, monkeypatch):
    """Tim, 27 Oct (1.1.5): each release route numbered 1 first; the casting director follows the cast summary. Neither
    changes the valuation (the workbook uses both for narrative and completeness only)."""
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path))
    from studio import sales
    from studio.server import app
    assert sales.release_text(["Theatrical", "VOD", "Straight to streaming"]) == "1 Theatrical; 2 VOD; 3 Straight to streaming"
    assert sales.release_text(["Theatrical-led", "Direct to TV"]) == "1 Theatrical; 2 Straight to TV"
    assert sales.release_text([]) == "" and sales.release_text("Direct to streaming") == "Straight to streaming"
    assert sales.cast_text("Two leads, one attached", "Nina Gold") == "Two leads, one attached; Casting director: Nina Gold"
    assert sales.cast_text("", "Nina Gold") == ""          # a casting director alone doesn't describe the cast
    c = TestClient(app)
    base = c.post("/api/tools/sales/value", json={"project": SAMPLE}).json()
    intake = dict(SAMPLE["intake"], release_model=["TVOD", "Theatrical"], casting_director="Nina Gold",
                  cast_summary=SAMPLE["intake"].get("cast_summary") or "Two leads")
    r = c.post("/api/tools/sales/value", json={"project": dict(SAMPLE, intake=intake)}).json()
    assert same(r["summary"]["ask"], base["summary"]["ask"])
    ws = openpyxl.load_workbook(__import__("io").BytesIO(c.get(f"/api/runs/sales/{r['run_id']}/engine.xlsx").content))["PROJECT_INTAKE"]
    assert ws["B27"].value == "1 TVOD; 2 Theatrical" and ws["B21"].value.endswith("; Casting director: Nina Gold")
