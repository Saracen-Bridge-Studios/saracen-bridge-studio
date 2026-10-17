"""Look Book Analytics: the deck as page images, Gemma's vision add-on, Jon's 16 sections, the Word report."""
import io
import json

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from studio import jobs, llm, lookbook, report, store


def _pdf(n=3) -> bytes:
    imgs = [Image.new("RGB", (1600, 900), (40 + 60 * i, 20, 90)) for i in range(n)]
    buf = io.BytesIO()
    imgs[0].save(buf, "PDF", save_all=True, append_images=imgs[1:])
    return buf.getvalue()


def _png() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (800, 1200), (200, 160, 60)).save(buf, "PNG")
    return buf.getvalue()


def test_deck_pages_from_pdf_and_images():
    pages = lookbook.pages([("deck.pdf", _pdf(3))])
    assert len(pages) == 3
    im = Image.open(io.BytesIO(pages[0]["image"]))
    assert im.format == "JPEG" and max(im.size) <= lookbook.LONG_SIDE
    assert len(lookbook.pages([("a.png", _png()), ("b.png", _png())])) == 2
    with pytest.raises(ValueError, match="export the deck to PDF"):
        lookbook.pages([("deck.pptx", b"PK..")])


def test_vision_add_on_is_found_beside_its_own_model(tmp_path, monkeypatch):
    m = tmp_path / "models"
    m.mkdir()
    (tmp_path / llm.SERVER_EXE).write_bytes(b"x")
    g12 = m / "gemma-4-12b-it-qat-q4_0.gguf"
    g12.write_bytes(b"x" * 100)
    (m / "gemma-4-E4B_q4_0-it.gguf").write_bytes(b"x" * 50)
    (m / "gemma-4-E4B-it-mmproj.gguf").write_bytes(b"x")
    assert llm.projector_for(g12) is None                         # E4B's add-on is not the 12B's
    assert llm.projector_for(m / "gemma-4-E4B_q4_0-it.gguf").name == "gemma-4-E4B-it-mmproj.gguf"
    monkeypatch.setenv("STUDIO_LLM_DIR", str(tmp_path))
    eng = llm.Engine("bundled", "", g12.stem)
    ok, why = llm.can_see(eng)
    assert not ok and "vision add-on" in why
    (m / "mmproj-gemma-4-12b-it-qat-q4_0.gguf").write_bytes(b"x")
    assert llm.projector_for(g12).name == "mmproj-gemma-4-12b-it-qat-q4_0.gguf"
    assert llm.can_see(eng) == (True, "")
    assert llm.bundled_files()[1] == g12                          # an add-on is never mistaken for a model


def test_images_go_in_the_form_each_server_expects():
    img = _png()
    oa = llm._user_message(llm.Engine("bundled", "", "g"), "look", [img])
    assert oa["content"][0]["image_url"]["url"].startswith("data:image/png;base64,") and oa["content"][-1] == {"type": "text", "text": "look"}
    ol = llm._user_message(llm.Engine("ollama", "", "g"), "look", [img])
    assert ol["content"] == "look" and len(ol["images"]) == 1
    an = llm._user_message(llm.Engine("anthropic", "", "c", "k", "anthropic"), "look", [img])
    assert an["content"][0]["source"]["media_type"] == "image/png" and an["content"][-1]["text"] == "look"
    assert llm._user_message(llm.Engine("bundled", "", "g"), "plain", None) == {"role": "user", "content": "plain"}


def _fake_chat(seen):
    """Answers each schema with a plausible object, and records which calls carried an image."""
    def chat(engine, system, user, *, schema=None, images=None, **kw):
        seen.append((schema, bool(images)))
        if schema is lookbook.PAGE:
            return {"role": "cover", "shows": "a lighthouse at dusk", "words": "THE LIGHTHOUSE KEEPER", "visual_score": 7, "sells": "mood", "issues": []}
        if schema is lookbook.SNAPSHOT:
            return {k: "x" for k in lookbook.SNAPSHOT["properties"]} | {"current_logline": ""}
        if schema is lookbook.STORY:
            return {"story_sell": "clear", "clear": ["world"], "unclear": [], "move_earlier": [],
                    "characters": [{"character": "Mara", "function": "lead", "emotional_hook": "grief", "casting_appeal": "high",
                                    "actor_type": "30s lead", "status": "Attached", "names": ["Florence Pugh"]}],
                    "director_named": "", "director_assessment": "none named", "director_suggestions": [{"name": "Nobody Real", "why": "x"}]}
        if schema is lookbook.VISUAL:
            return {k: "x" for k in lookbook.VISUAL["properties"]} | {"strongest_pages": [{"page": 1, "why": "cover"}],
                                                                       "weakest_pages": [{"page": 9, "why": "not a page"}], "cut_simplify_redesign": ["cut page 3"]}
        if schema is lookbook.MARKET:
            return {k: "x" for k in lookbook.MARKET["properties"]} | {"better_comparables": [{"title": "Calm with Horses", "year": 2019, "why": "x"}],
                                                                       "scale_signals": ["a", "b", "c"], "budget_feel": "Mid", "sales_tool_usefulness_score": 62}
        if schema is lookbook.REBUILD:
            return {"slides": [{"slide": i, "title": "t", "purpose": "p", "content": "c", "visual_direction": "v"} for i in range(1, 13)],
                    "must_fix": ["logline"], "should_improve": ["comps"], "optional_enhancement": []}
        if schema is lookbook.SCORES:
            return {"scores": {k: 60 for k in lookbook.CATEGORIES}, "final_score": 85, "verdict": "Good with Revisions", "verdict_reason": "x"}
        raise AssertionError("unexpected schema")
    return chat


def test_analysis_runs_jons_sections_and_checks(monkeypatch):
    seen = []
    monkeypatch.setattr(llm, "chat", _fake_chat(seen))
    monkeypatch.setattr(llm, "resolve", lambda s, mode=None, use="writing": (llm.Engine("bundled", "", "gemma"), ""))
    monkeypatch.setattr(llm, "can_see", lambda e: (True, ""))
    deck = lookbook.pages([("deck.pdf", _pdf(2))])
    r = lookbook.write(deck, {"title": "The Lighthouse Keeper", "opinion": "I think the cover is weak"}, {})
    assert [s for s, img in seen if img] == [lookbook.PAGE, lookbook.PAGE]          # every page was looked at, as an image
    assert r["pages"] == 2 and r["average"] == 60.0 and r["final_score"] == 85
    assert any("more than 12 points" in c for c in r["checks"])                    # final vs average, G-01
    assert any("marked as attached" in c for c in r["checks"]) and r["sections"]["story"]["characters"][0]["status"] == "Suggested"
    assert any("Nobody Real" in c for c in r["checks"])
    assert r["sections"]["visual"]["weakest_pages"] == []                          # page 9 of a 2-page deck dropped
    assert r["verdict_text"].startswith("Good with revisions")
    doc = report.lookbook_docx(r)
    assert len(doc) > 100_000
    from docx import Document
    text = "\n".join(p.text for p in Document(io.BytesIO(doc)).paragraphs)
    assert "16. Final Verdict" in text and "LOOK BOOK SALES TOOL ANALYSIS" in text


def test_jons_spec_is_read_whole():
    sp = lookbook.spec()
    assert sorted(sp["sections"]) == list(range(1, 17))
    assert "Never refer to ChatGPT" in sp["rules"] and "ask the user" not in sp["rules"] and "GPT-generated" not in json.dumps(sp)


def test_api_intake_then_queue(tmp_path, monkeypatch):
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path))
    from studio.server import app
    c = TestClient(app)
    deck = _pdf(3)                              # built once: PIL stamps the PDF with the time, so two builds can differ
    r = c.post("/api/tools/lookbook/intake", data={"title": "Lighthouse", "cast": "Florence Pugh", "opinion": "too dark?"},
               files=[("files", ("deck.pdf", deck))]).json()
    assert r["pages"] == 3 and not r["duplicate"]
    again = c.post("/api/tools/lookbook/intake", files=[("files", ("deck.pdf", deck))]).json()
    assert again["duplicate"] and again["run_id"] == r["run_id"]
    img = c.get(f"/api/runs/lookbook/{r['run_id']}/files/pages/p01.jpg", params={"inline": 1})
    assert img.status_code == 200 and img.content[:2] == b"\xff\xd8"
    assert c.get(f"/api/runs/lookbook/{r['run_id']}/files/..%2F..%2Fsettings.json").status_code == 404
    monkeypatch.setattr(llm, "resolve", lambda s, mode=None, use="writing": (llm.Engine("bundled", "", "gemma"), ""))
    monkeypatch.setattr(llm, "can_see", lambda e: (False, "Gemma's vision add-on is not installed yet"))
    assert c.post("/api/tools/lookbook/analyse", json={"run_ids": [r["run_id"]]}).status_code == 409
    monkeypatch.setattr(llm, "can_see", lambda e: (True, ""))
    monkeypatch.setattr(jobs, "ensure_worker", lambda: None)
    q = c.post("/api/tools/lookbook/analyse", json={"run_ids": [r["run_id"]], "info": {"budget": "£3m"}}).json()
    assert q["queued"] == 1
    rec, _ = store.get_run("lookbook", r["run_id"])
    assert rec["inputs"]["info"] == {"title": "Lighthouse", "cast": "Florence Pugh", "opinion": "too dark?", "budget": "£3m"}
    seen = []
    monkeypatch.setattr(llm, "chat", _fake_chat(seen))
    job = store.claim_job()
    jobs.run_lookbook(job)
    rec, folder = store.get_run("lookbook", r["run_id"])
    assert rec["summary"]["verdict"] == "Good with Revisions" and rec["summary"]["score"] == 85
    assert any(f.endswith("Look Book Analysis.docx") for f in rec["files"])
    assert not any("marked as attached" in c for c in rec["outputs"]["lookbook"]["checks"])   # Florence Pugh was supplied as attached
