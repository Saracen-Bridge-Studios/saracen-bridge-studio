"""Sales Estimates: reading an existing sales estimate (1.1.6). Tim's own samples haven't arrived: these are made
in the shapes sales companies send (ask/take columns in thousands, high/low, a Word table, figures with k and m)."""
import io

import docx
import openpyxl
from fastapi.testclient import TestClient

from studio import estimates


def _xlsx(rows):
    wb = openpyxl.Workbook()
    ws = wb.active
    for r in rows:
        ws.append(r)
    b = io.BytesIO()
    wb.save(b)
    return b.getvalue()


def test_territories_are_matched_by_the_names_estimates_use():
    t = estimates.territory
    assert t("United States") == "USA" and t("North America") == "USA" and t("UK & Ireland") == "UK / Ireland"
    assert t("German-speaking") == "Germany" and t("Nordics") == "Scandinavia" and t("Russia/CIS") == "CIS"
    assert t("Latin America") == "Rest of Latin America" and t("Rest of Latin America") == "Rest of Latin America"
    assert t("Australia/NZ") == "Australia / New Zealand" and t("Middle East") == "Middle East (ex-Israel/Turkey)"
    assert t("Benelux") == "Benelux" and t("Holland") == "Benelux" and t("Airlines") == "Airlines"
    assert t("Notes") is None and t("") is None


def test_an_ask_take_spreadsheet_in_thousands():
    data = _xlsx([["NIGHT FERRY: SALES ESTIMATES (USD 000s)"], [], ["Territory", "Ask", "Take"],
                  ["United Kingdom", 250, 150], ["Germany", "300", "200"], ["France", 280, 180], ["Sweden", 40, 25], ["Norway", 30, 20],
                  ["Moonbase", 5, 1], ["TOTAL", 900, 575]])
    r = estimates.read("est.xlsx", data)
    rows = {x["territory"]: x for x in r["rows"]}
    assert r["thousands"] and r["currency"] == "USD" and r["currency_stated"]
    assert rows["UK / Ireland"]["ask"] == 250_000 and rows["UK / Ireland"]["take"] == 150_000 and rows["UK / Ireland"]["how"] == "by column heading"
    assert rows["Scandinavia"]["ask"] == 70_000 and "Sweden + Norway" in rows["Scandinavia"]["as_written"]     # two rows, one territory
    assert r["total"]["ask"] == 900_000 and r["stated_total"]["ask"] == 900_000 and not r["checks"]
    assert any("Moonbase" in u for u in r["unplaced"])


def test_high_low_csv_with_whole_amounts_and_currency():
    data = ("Territory,Low,High\nUSA,\"$400,000\",\"$750,000\"\nJapan,$60k,$90k\nSpain,1.2m,0.9m\n"
            "Total,\"1,660,000\",\"2,040,000\"\n").encode()
    r = estimates.read("est.csv", data)
    rows = {x["territory"]: x for x in r["rows"]}
    assert not r["thousands"] and rows["USA"]["ask"] == 750_000 and rows["USA"]["take"] == 400_000      # High is the ask
    assert rows["Japan"]["ask"] == 90_000 and rows["Spain"]["take"] == 1_200_000 and rows["Spain"]["ask"] == 900_000
    assert "Take above ask in Spain." in r["checks"]           # Low 1.2m, High 0.9m: flagged, not swapped
    assert any("total ask" in c for c in r["checks"])


def test_a_word_table_without_headings_takes_the_larger_figure_as_the_ask():
    d = docx.Document()
    t = d.add_table(rows=3, cols=3)
    for i, row in enumerate([("Italy", "120,000", "180,000"), ("Brazil", "50,000", "35,000"), ("South Korea", "75,000", "")]):
        for j, v in enumerate(row):
            t.cell(i, j).text = v
    b = io.BytesIO()
    d.save(b)
    r = estimates.read("est.docx", b.getvalue())
    rows = {x["territory"]: x for x in r["rows"]}
    assert rows["Italy"]["ask"] == 180_000 and rows["Italy"]["take"] == 120_000 and rows["Italy"]["how"] == "larger figure as ask"
    assert rows["South Korea"]["ask"] == 75_000 and rows["South Korea"]["take"] is None


def test_api_ingests_keeps_and_compares(tmp_path, monkeypatch):
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path))
    from studio import store
    from studio.server import app
    c = TestClient(app)
    data = _xlsx([["Territory", "Ask", "Take"], ["UK", 250000, 150000], ["Germany", 300000, 200000]])
    r = c.post("/api/tools/sales/estimate/read", files={"file": ("agent.xlsx", data)}).json()
    assert [x["territory"] for x in r["rows"]] == ["UK / Ireland", "Germany"]
    rec = store.save_run("sales", "Night Ferry", {"intake": {}}, {"valuation": {"territories": [
        {"territory": "UK / Ireland", "ask": 200000, "take": 120000}, {"territory": "Germany", "ask": 300000, "take": 180000}]}})
    kept = c.put(f"/api/tools/sales/{rec['id']}/estimate", json={"estimate": dict(r, company="XYZ Films", date="2026-10-01")}).json()
    cmp = {x["territory"]: x for x in kept["comparison"]}
    assert round(cmp["UK / Ireland"]["diff_ask"], 2) == 0.25 and cmp["Germany"]["diff_ask"] == 0
    saved, _ = store.get_run("sales", rec["id"])
    assert saved["outputs"]["existing_estimate"]["company"] == "XYZ Films"
    assert c.post("/api/tools/sales/estimate/read", files={"file": ("x.pages", b"..")}).status_code == 400


def test_a_pdf_table_and_a_label_naming_two_territories():
    """A borderless table in a PDF (made from a Word table by LibreOffice), read from pypdf's layout text."""
    from pathlib import Path
    data = (Path(__file__).parent / "fixtures" / "sales_estimate_sample.pdf").read_bytes()
    r = estimates.read("sample.pdf", data)
    rows = {x["territory"]: x for x in r["rows"]}
    assert r["thousands"] and rows["UK / Ireland"]["ask"] == 250_000 and rows["Rest of World"]["take"] == 30_000
    assert rows["Germany"]["also"] == ["Austria"] and any("Germany / Austria" in c and "Austria" in c for c in r["checks"])
    assert r["stated_total"]["ask"] == 1_080_000 and r["total"]["ask"] == 1_080_000
