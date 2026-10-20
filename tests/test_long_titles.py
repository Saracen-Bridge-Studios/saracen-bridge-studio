"""1.1.1: Tim's "Where the Sparrows Fly" (20 Oct). Its title page has no title in its text, so the reader took the
registration line as the title; the long title made a long run id, which the lookup cut short, so the script could be
neither re-dropped nor queued for coverage ("Internal Server Error"), and Jonny blamed server traffic."""
import pytest
from fastapi.testclient import TestClient

from studio import script, store

FILE = "Where the Sparrows Fly .pdf"


def test_a_registration_line_is_not_the_title():
    page = ["Written by", "A WRITER", "writer@example.com   BOWER CARD DRAFT: 28/07/2026",
            "Registered with the Writer's Guild of Great Britain."]
    assert script._pick_title(page) == ""
    assert script._pick_title(page + ["FADE IN:", "A sparrow on a wire."]) == ""        # the script's first page isn't it
    assert script.title_from_filename("Where the Sparrows Fly ") == "Where the Sparrows Fly"
    assert script.title_from_filename("Where the Sparrows Fly - Script - 250926") == "Where the Sparrows Fly"
    assert script.title_from_filename("1917") == "1917" and script.title_from_filename("Heat - 20260925 - v3") == "Heat"
    for line in ("Registered WGA West #123456", "WGGB Registration 2026", "Registered with the Writers Guild of America"):
        assert script.NOT_TITLE.search(line), line


def test_runs_with_long_titles_open_again(tmp_path, monkeypatch):
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path))
    rec = store.save_run("coverage", "Registered with the Writer's Guild of Great Britain.", {"file": FILE}, {"x": 1})
    assert len(rec["id"]) > 60                                   # longer than a title slug: the 1.1.0 lookup lost the end
    got, folder = store.get_run("coverage", rec["id"])
    assert got["id"] == rec["id"] and folder.name == rec["id"]
    with pytest.raises(FileNotFoundError):
        store.get_run("coverage", "../../settings")              # ids stay inside the runs folder


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path / "home"))
    from studio import llm, server
    monkeypatch.setattr(llm, "resolve", lambda settings, mode: (llm.Engine("openai", "http://127.0.0.1:9", "test"), ""))
    monkeypatch.setattr(server.jobs, "ensure_worker", lambda: None)
    return TestClient(server.app, raise_server_exceptions=False)


def _breakdown_run(title):
    res = {"title": title, "parser": script.PARSER_VERSION, "scene_count": 1}
    return store.save_run("coverage", title, {"file": FILE}, {"breakdown": res})


def test_a_long_titled_script_queues_for_coverage_once(client):
    rec = _breakdown_run("Registered with the Writer's Guild of Great Britain.")
    r = client.post("/api/tools/coverage/write", json={"run_ids": [rec["id"], rec["id"]], "mode": "quick"})
    assert r.status_code == 200 and r.json()["queued"] == 1


def test_a_script_no_longer_in_the_library_says_so(client):
    r = client.post("/api/tools/coverage/write", json={"run_ids": ["20261020-160812_Gone"], "mode": "quick"})
    assert r.status_code == 404 and "no longer in the Library" in r.json()["detail"]


def test_a_studio_fault_says_what_it_is_and_what_to_do(client, monkeypatch):
    from studio import server
    monkeypatch.setattr(server.store, "get_run", lambda *a: (_ for _ in ()).throw(RuntimeError("boom")))
    r = client.post("/api/tools/coverage/write", json={"run_ids": ["x"], "mode": "quick"})
    d = r.json()["detail"]
    assert r.status_code == 500 and "inside the Studio" in d and "studio.log" in d and "Internal Server Error" not in d


def test_jonny_knows_errors_are_the_studios_own():
    from studio import assist
    assert "never suggest waiting for traffic" in assist.RULES and "studio.log" in assist.RULES


def test_reference_data_reads_from_many_threads_at_once():
    """Tim's log, 20 Oct: the Sales warm-up thread and a page request shared one database connection and one failed."""
    from concurrent.futures import ThreadPoolExecutor
    from studio import refdata
    with ThreadPoolExecutor(16) as pool:
        got = list(pool.map(lambda _: refdata.fx_usd_per_unit("GBP"), range(400)))
    assert len(set(got)) == 1 and got[0] > 1
