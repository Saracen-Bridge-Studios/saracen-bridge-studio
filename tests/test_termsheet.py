"""Finance Plan: term sheets read into proposed sources (1.0.8), with the model stood in for."""
from pathlib import Path

import pytest

from studio import llm, termsheet

FIX = Path(__file__).parent / "fixtures"
DOCX = (FIX / "sample_term_sheet.docx").read_bytes()


@pytest.fixture
def fake_model(monkeypatch):
    def chat(engine, system, user, *, schema=None, **kw):
        assert "Harbour Light Capital" in user and "FINANCE CONTROLS" not in system and "Unknown values remain unconfirmed" in system
        base = {"interest": "Not stated", "fees": "Not stated", "term": "Not stated", "security": "Not stated", "recoupment": "Not stated",
                "conditions": [], "key_dates": [], "amount_words": ""}
        return {"instruments": [
            base | {"provider": "Harbour Light Capital Ltd", "recipient": "Night Ferry Productions Ltd", "instrument": "Gap / mezzanine debt", "amount": 1250000, "currency": "eur",
                    "status": "Confirmed cash", "status_words": "non-binding", "interest": "12% per annum", "fees": "2% arrangement fee",
                    "term": "18 months", "conditions": ["Completion bond", "Sales agency agreement"]},
            base | {"provider": "Northgate Films", "recipient": "Night Ferry Productions Ltd", "instrument": "Equity", "amount": 500000, "currency": "EUR", "status": "Draft / conditional",
                    "status_words": "subject to contract"},
            base | {"provider": "Invented Fund", "recipient": "", "instrument": "Soft money / grant", "amount": 777777, "currency": "EUR", "status": "Signed but conditional",
                    "status_words": ""},
            base | {"provider": "Somebody", "recipient": "", "instrument": "In-kind / services", "amount": None, "currency": "", "status": "Assumption only", "status_words": ""}],
            "parties": "Night Ferry Productions Ltd; Harbour Light Capital Ltd; Northgate Films", "governing_law": "England and Wales", "notes": []}

    monkeypatch.setattr(llm, "resolve", lambda settings, mode=None, use="writing": (llm.Engine("openai", "http://127.0.0.1:1/v1", "gemma"), ""))
    monkeypatch.setattr(llm, "chat", chat)


def test_terms_are_checked_against_the_document(fake_model):
    res = termsheet.read("sample_term_sheet.docx", DOCX, {})
    gap, equity, grant, inkind = res["rows"]
    assert gap["amount"] == 1250000 and gap["amount_in_document"] and gap["currency"] == "EUR" and gap["is_debt"] and gap["cash"]
    assert gap["status"] == "LOI / non-binding" and "non-binding" in gap["terms"]["status_note"]      # never above the document's words
    assert equity["status"] == "LOI / non-binding" and not equity["is_debt"]
    assert grant["status"] == "Assumption only" and not grant["amount_in_document"]                 # 777,777 isn't in the document
    assert inkind["amount"] is None and not inkind["cash"]
    assert any("doesn't appear" in c for c in res["checks"]) and any("Unknown" in c for c in res["checks"])
    assert res["governing_law"] == "England and Wales"


def test_amounts_and_binding_words():
    found = termsheet.amounts_in("A facility of EUR 1,250,000 and £2.5m equity, 18 months, 12%")
    assert termsheet.in_document(1250000, found) and termsheet.in_document(2500000, found) and not termsheet.in_document(1300000, found)
    assert termsheet.binding_cap("Letter of intent only") == "LOI / non-binding"
    assert termsheet.binding_cap("Our overdraft facility") is None
    assert termsheet.cap("Confirmed cash", "Draft / conditional") == "Draft / conditional"
    assert termsheet.cap("LOI / non-binding", "Signed but conditional") == "LOI / non-binding"


def test_the_endpoint_saves_the_reading_in_the_library(fake_model, tmp_path, monkeypatch):
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path))
    from fastapi.testclient import TestClient
    from studio.server import app
    c = TestClient(app)
    r = c.post("/api/tools/finance/termsheet", files={"file": ("sample_term_sheet.docx", DOCX)}).json()
    assert len(r["rows"]) == 4 and r["run_id"]
    run = c.get(f"/api/runs/finance/{r['run_id']}").json()
    assert run["outputs"]["termsheet"]["rows"][0]["name"].startswith("Harbour Light Capital")
    assert c.post("/api/tools/finance/termsheet", files={"file": ("x.xlsx", b"PK..")}).status_code == 400
