"""Schedule and budget (1.0.4): stripboard, day-out-of-days, budget lines from Jon's rate cards, API and workbook."""
import io
import math
from pathlib import Path

import openpyxl
import pytest
from fastapi.testclient import TestClient

from studio import budget, refdata, script

FIX = Path(__file__).parent / "fixtures"


def breakdown(n=12, lines=20):
    """A synthetic script: three locations, day and night, a long scene, four characters."""
    scenes = []
    for i in range(n):
        loc = ["KITCHEN", "HARBOUR", "OFFICE"][i % 3]
        scenes.append({"number": i + 1, "heading": f"INT. {loc} - DAY", "int_ext": "EXT" if loc == "HARBOUR" else "INT", "location": loc,
                       "time_of_day": "NIGHT" if i % 4 == 0 else "DAY", "characters": ["ANNA"] + (["BEN"] if i % 2 else []) + (["CARL"] if i == 5 else []),
                       "lines": lines * (6 if i == 7 else 1)})
    cast = [{"name": "ANNA", "dialogue_blocks": 40}, {"name": "BEN", "dialogue_blocks": 20}, {"name": "CARL", "dialogue_blocks": 2}]
    return {"pages": 30, "scene_count": n, "scenes": scenes, "cast": cast}


def test_stripboard_packs_by_location_never_mixes_day_and_night_and_covers_every_scene():
    b = breakdown()
    lens = budget.scene_eighths(b)
    assert sum(lens) == pytest.approx(30 * 8, abs=len(lens))         # each scene's share of 30 pages, in eighths
    for ppd in (5, 4, 3):
        board = budget.stripboard(b, ppd)
        assert {s for d in board for s in d["scenes"]} == set(range(1, 13))
        assert all(d["eighths"] <= ppd * 8 for d in board)
        day_e = sum(e for e, sc in zip(lens, b["scenes"]) if not budget._night(sc["time_of_day"]))
        assert len(board) == math.ceil(day_e / (ppd * 8)) + math.ceil((sum(lens) - day_e) / (ppd * 8))   # days follow the pace
        assert sum(d["eighths"] for d in board) == sum(lens)
        for d in board:                                               # a day is all day work or all night work
            nights = {budget._night(b["scenes"][s - 1]["time_of_day"]) for s in d["scenes"]}
            assert nights == {d["night"]}
    assert len(budget.stripboard(b, 3)) > len(budget.stripboard(b, 5))
    long = [d for d in budget.stripboard(b, 3) if 8 in d["scenes"]]   # scene 8 is 6× longer than the rest: more than a day
    assert len(long) >= 2


def test_sets_at_one_site_are_not_company_moves():
    assert budget.site({"location": "JOHN'S HOUSE - KITCHEN"}) == budget.site({"location": "JOHN'S HOUSE - HALL"}) == "JOHN'S HOUSE"
    assert budget.site({"location": "POLICE STATION, CELLS"}) == "POLICE STATION" and budget.site({"location": "CAR (MOVING)"}) == "CAR"
    scenes = [{"number": i + 1, "location": f"MANOR - ROOM {i}", "int_ext": "INT", "time_of_day": "DAY", "characters": [], "lines": 10} for i in range(6)]
    board = budget.stripboard({"pages": 3, "scenes": scenes, "cast": []}, 4)
    assert len(board) == 1 and board[0]["moves"] == 0 and board[0]["sites"] == ["MANOR"] and len(board[0]["locations"]) == 6


def test_day_out_of_days_counts_each_characters_days():
    b = breakdown()
    board = budget.stripboard(b, 4)
    dood = {c["name"]: c for c in budget.day_out_of_days(b, board)}
    assert dood["ANNA"]["work_days"] == len(board)                    # ANNA is in every scene
    assert dood["CARL"]["work_days"] == 1 and dood["CARL"]["hold_days"] == 0
    ben_days = [d["day"] for d in board if "BEN" in d["cast"]]
    assert dood["BEN"]["days"] == ben_days and dood["BEN"]["hold_days"] == ben_days[-1] - ben_days[0] + 1 - len(ben_days)


def test_budget_lines_come_from_jons_card_and_unknowns_stay_unknown():
    b = breakdown()
    res = budget.build(b, jurisdiction="United Kingdom", tier=2, inputs={"vfx_shots": 0})
    base = res["budget"]["base"]
    days = res["schedule"]["base"]["shoot_days"]
    lines = {l["description"]: l for l in base["lines"]}
    # a crew line: tier 2 week rate × (prep + shoot + wrap) / 5, London factor 1.0
    lp = lines["Line producer / UPM"]
    week = refdata.rows("""SELECT tier_2_week FROM rate_crew WHERE jurisdiction = 'United Kingdom' AND production_type LIKE 'Feature%'
        AND english_budget_role = 'Line Producer / UPM'""")[0]["tier_2_week"]
    assert lp["rate"] == week and lp["amount"] == pytest.approx(week * (1.5 * days + days + 7.5) / 5, rel=1e-6)
    assert lp["account"] == "2001" and lp["status"] == "benchmark"
    # negotiated roles and producer fees are Unknown, never zero
    for d in ("Director of photography", "Production designer", "Script and rights", "Director", "Music: composer and licences"):
        assert lines[d]["amount"] is None and lines[d]["status"] == "unknown", d
    # 1.1.6: the fringe takes the UK card's payroll rules until a % is entered (NI 15% alone in lean; + the 3% pension proxy
    # in base, no levy on a pay bill under £3m; + 12.07% rolled-up holiday in conservative), as an allowance
    fr = {s: next(l for l in res["budget"][s]["lines"] if l["description"] == "Fringes on crew payroll") for s in budget.SCENARIOS}
    assert [fr[s]["rate"] for s in budget.SCENARIOS] == [15, 18, pytest.approx(30.07)]
    assert fr["base"]["status"] == "allowance" and fr["base"]["basis"].startswith("allowance: 15% employer National Insurance + 3% pension")
    # the levy only on a pay bill over £3 million, less the £15,000 allowance
    card = budget.Card("United Kingdom")
    assert card.payroll_load("base", 2_000_000)[0] == 18 and card.payroll_load("base", 6_000_000)[0] == pytest.approx(18 + (30_000 - 15_000) / 6_000_000 * 100, abs=1e-3)
    # allowances fill the blank but stay out of the priced total and still count as lines to price (Jon: fees stay producer inputs)
    allow = [l for l in base["lines"] if l["status"] == "allowance"]
    assert base["allowance_total"] == pytest.approx(sum(l["amount"] for l in allow)) and base["allowance_lines"] == len(allow) >= 2
    assert base["unknown_lines"] == sum(1 for l in base["lines"] if l["amount"] is None or l["status"] == "allowance")
    # a principal part with no fee takes the card's planning band for its size of part, in the card's currency
    lead = refdata.rows("SELECT planning_base, currency FROM rate_cast WHERE jurisdiction = 'United Kingdom' AND english_role = 'Lead Actor'")[0]
    gbp = refdata.fx_usd_per_unit("GBP")
    allowances = [l for l in base["lines"] if l["account"] == "1401" and l["basis"].startswith("allowance: Lead Actor")]
    assert allowances and allowances[0]["amount"] == pytest.approx(lead["planning_base"] / gbp, rel=1e-6) and lead["currency"] == "USD"
    assert base["status"] == "PRELIMINARY"
    # contingency is 10% of direct cost, bond at the card's rate
    direct = sum(l["amount"] or 0 for l in base["lines"] if l["status"] != "allowance" and l["phase"] in ("Above the Line", "Production", "Post Production", "Other"))
    assert lines["Contingency (10%)"]["amount"] == pytest.approx(direct * 0.10, rel=1e-6)
    assert lines["Completion bond fee"]["rate"] == 0.025
    # cases: more days and higher bands from lean to conservative
    tot = [res["budget"][s]["known_total"] for s in budget.SCENARIOS]
    assert tot[0] < tot[1] < tot[2]
    assert res["schedule"]["lean"]["shoot_days"] <= res["schedule"]["base"]["shoot_days"] <= res["schedule"]["conservative"]["shoot_days"]


def test_producer_figures_price_the_unknown_lines():
    b = breakdown()
    plain = budget.build(b, jurisdiction="United Kingdom", inputs={"vfx_shots": 0})["budget"]["base"]
    days_anna = next(c for c in budget.day_out_of_days(b, budget.stripboard(b, 4)) if c["name"] == "ANNA")["work_days"]
    res = budget.build(b, jurisdiction="United Kingdom", inputs={
        "vfx_shots": 0, "fringe_pct": 20, "cast": {"ANNA": {"amount": 1000, "basis": "day"}},
        "overrides": {"3101|Director of photography": 50000, "1101|Script and rights": 25000}})["budget"]["base"]
    lines = {l["description"]: l for l in res["lines"]}
    assert lines["ANNA"]["amount"] == 1000 * days_anna and lines["ANNA"]["status"] == "input"
    assert lines["Director of photography"]["amount"] == 50000 and lines["Script and rights"]["amount"] == 25000
    payroll = sum(l["amount"] for l in res["lines"] if l["payroll"] and l["amount"])
    assert lines["Fringes on crew payroll"]["amount"] == pytest.approx(payroll * 0.20, rel=1e-6)
    assert res["unknown_lines"] == plain["unknown_lines"] - 4          # ANNA and the fringe were allowances: still to price until entered


def test_every_jurisdiction_builds_in_its_own_currency():
    b = breakdown()
    for j in budget.jurisdictions():
        res = budget.build(b, jurisdiction=j["jurisdiction"], inputs={"vfx_shots": 0})
        assert res["currency"] == j["currency"]
        assert res["budget"]["base"]["known_total"] > 0
        assert all(l["amount"] is None or l["amount"] >= 0 for l in res["budget"]["base"]["lines"])
    spain = budget.build(b, jurisdiction="Spain")["budget"]                # Spain's card: market low / base / high day rates
    lp = [next(l for l in spain[s]["lines"] if l["account"] == "2001") for s in budget.SCENARIOS]
    assert lp[0]["rate"] < lp[1]["rate"] < lp[2]["rate"]


def test_api_builds_saves_and_exports_the_workbook(tmp_path, monkeypatch):
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path))
    from studio import store
    from studio.server import app
    c = TestClient(app)
    run = c.post("/api/tools/script/intake", data={"tool": "schedule"}, files=[("files", ("sample.pdf", (FIX / "sample.pdf").read_bytes()))]).json()[0]
    opts = c.get("/api/tools/schedule/budget/options").json()
    assert len(opts["jurisdictions"]) == 13 and opts["pages_per_day"]["base"] == 4
    assert c.post("/api/tools/schedule/budget", json={"run_id": run["run_id"], "jurisdiction": "Narnia"}).status_code == 400
    assert c.post("/api/tools/schedule/budget", json={"run_id": "nope", "jurisdiction": "Ireland"}).status_code == 404
    res = c.post("/api/tools/schedule/budget", json={"run_id": run["run_id"], "jurisdiction": "Ireland", "tier": 3,
                                                     "inputs": {"vfx_shots": 0}}).json()
    assert res["currency"] == "EUR" and res["settings"]["tier"] == 3
    rec, _ = store.get_run("schedule", run["run_id"])
    assert rec["outputs"]["budget"]["budget"]["base"]["known_total"] == res["budget"]["base"]["known_total"]
    assert rec["summary"]["shoot_days"] == res["schedule"]["base"]["shoot_days"] and rec["outputs"]["breakdown"]["scenes"]
    x = c.get(f"/api/runs/schedule/{run['run_id']}/budget.xlsx")
    assert x.status_code == 200 and "Schedule and Budget.xlsx" in x.headers["content-disposition"]
    wb = openpyxl.load_workbook(io.BytesIO(x.content))
    assert wb.sheetnames == ["Top sheet", "Budget detail", "Stripboard (base)", "Day out of days", "Assumptions and sources"]
    assert any(str(v).startswith("=SUMIFS(") for row in wb["Top sheet"].iter_rows(values_only=True) for v in row if v)
    lb = c.post("/api/tools/lookbook/intake", files=[("files", ("deck.pdf", (FIX / "sample.pdf").read_bytes()))]).json()
    assert c.post("/api/tools/schedule/budget", json={"tool": "lookbook", "run_id": lb["run_id"], "jurisdiction": "Ireland"}).status_code == 400


def test_a_real_script_read_schedules_end_to_end():
    b = script.parse("sample.fountain", (FIX / "sample.fountain").read_bytes())
    res = budget.build(b, jurisdiction="United States", inputs={"vfx_shots": 2, "background_per_day": 10})
    assert res["schedule"]["base"]["shoot_days"] >= 1 and res["dood"]
    lines = {l["description"]: l for l in res["budget"]["base"]["lines"]}
    assert lines["VFX shots (2)"]["amount"] > 0 and lines["Background artists (10 a day)"]["status"] in ("benchmark", "unknown")
