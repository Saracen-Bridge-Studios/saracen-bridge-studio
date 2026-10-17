"""Ask Jonny's index of Jon's documents."""
import sqlite3

from docx import Document

from studio import knowledge


def _tree(root):
    (root / "shared").mkdir(parents=True)
    (root / "shared" / "07_Comparable_Film_Methodology.md").write_text(
        "# Comparable Film Methodology\n\n## Selecting comps\n\nPick comparable films by budget band, genre and release year.\n"
        "Never use a comp older than ten years without saying why.\n", encoding="utf-8")
    inc = root / "t06_location_incentive" / "skills" / "instructions"
    inc.mkdir(parents=True)
    (inc / "SKILL.md").write_text("---\nname: x\n---\n# Location incentives\n\n## Gates\n\nCheck the cultural test and the "
                                  "minimum qualifying spend before computing any rebate.\n", encoding="utf-8")
    bfi = root / "t07_bfi_certification" / "skills" / "instructions" / "references"
    bfi.mkdir(parents=True)
    d = Document()
    d.add_heading("Golden Points rule", 1)
    d.add_paragraph("The Golden Points rule applies where the film scores enough points overall but misses section A.")
    t = d.add_table(rows=1, cols=2)
    t.rows[0].cells[0].text, t.rows[0].cells[1].text = "A1", "Set in the UK"
    d.save(str(bfi / "01_Current_BFI_Film_Cultural_Test_Guidance-july-2026.docx"))
    cap = root / "captures"
    cap.mkdir()
    (cap / "FPM_chat_reconstructed_spec.md").write_text("# Captured\n\nOne project's chat, not method: rebate rebate rebate.\n")
    (root / "shared" / "Saracen_Bridge_Analytics_Master_Report_Template.md").write_text("# Template\n\nFill in rebate here.\n")


def test_build_and_search(tmp_path, monkeypatch):
    _tree(tmp_path / "sources")
    db = tmp_path / "knowledge.db"
    counts = knowledge.build(db, tmp_path / "sources")
    assert counts["docs"] == 3                                     # captures and templates are left out
    titles = {r[0] for r in sqlite3.connect(db).execute("SELECT title FROM docs")}
    assert titles == {"07 Comparable Film Methodology", "Location & Incentives: Jon's GPT instructions", "01 Current BFI Film Cultural Test Guidance"}
    monkeypatch.setattr(knowledge, "_db_path", lambda: db)
    hits = knowledge.search("What is the golden points rule?", "bfi")
    assert hits[0]["title"].startswith("01 Current BFI") and "Golden Points" in hits[0]["heading"]
    assert "A1 | Set in the UK" in "".join(h["text"] for h in knowledge.search("A1 set in the UK"))   # table rows are searchable
    gates = knowledge.search("how do the rebate gates work", "incentives")
    assert gates[0]["tool"] == "incentives" and "qualifying spend" in gates[0]["text"]
    assert knowledge.search('comps "older" than (ten) years? -- OR NOT *')[0]["title"] == "07 Comparable Film Methodology"
    assert knowledge.search("the and of to") == []                # only stop words: no search


def test_missing_index_is_built_on_first_use(tmp_path, monkeypatch):
    _tree(tmp_path / "sources")
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path / "home"))
    monkeypatch.setattr(knowledge.refdata, "app_root", lambda: tmp_path)        # no data/knowledge.db shipped here
    assert knowledge.search("comparable films budget band")[0]["title"] == "07 Comparable Film Methodology"
    assert (tmp_path / "home" / knowledge.DB_NAME).exists()


def test_shipped_index_covers_jons_documents():
    hits = knowledge.search("golden points rule cultural test", "bfi")
    assert hits and any("BFI" in h["title"] for h in hits)


def test_a_tools_own_page_keeps_to_its_own_subject():
    """Tim, 13 Oct: on Finance Plan, "walk me through Finance Plan" brought back two BFI AVEC guides."""
    q = "Walk me through Finance Plan, step by step"
    titles = [r["title"] for r in knowledge.search(f"{q} Finance Plan", "finance", k=5, question=q)]
    assert titles and not any("AVEC" in t or "BFI" in t for t in titles)
    q2 = "Does the finance plan need AVEC for the BFI?"                      # a question that asks about BFI may get BFI
    assert any("AVEC" in r["title"] or "BFI" in r["title"] for r in knowledge.search(f"{q2} Finance Plan", "finance", k=5, question=q2))
    assert knowledge.search("Walk me through Finance Plan", None, k=5)[0]["tool"] == "finance"   # named from the home page
