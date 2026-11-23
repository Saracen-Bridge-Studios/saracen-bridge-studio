"""1.3.1 (Tim, 18 Nov): all AI work in one place with time left and Stop all; removing from the Library; the cloud
model chooser and retired models; casting's reading of the script's own wording, tier pairing and name search."""
import time
from pathlib import Path

import pytest

from studio import casting, jobs, llm, refdata, script, store

FIX = Path(__file__).parent / "fixtures"
FERRY = (FIX / "night_ferry.fountain").read_bytes()


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path))
    monkeypatch.setattr(jobs, "ensure_worker", lambda *a, **k: None)            # jobs are run by hand below
    monkeypatch.setattr(llm, "resolve", lambda settings, mode=None, use="writing": (llm.Engine("openai", "http://127.0.0.1:1/v1", "gemma"), ""))
    from fastapi.testclient import TestClient
    from studio.server import app
    return TestClient(app)


def _intake(c, tool="schedule", name="ferry.fountain"):
    return c.post("/api/tools/script/intake", data={"tool": tool}, files=[("files", (name, FERRY))]).json()[0]["run_id"]


def _ago(seconds):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() - seconds))


# ------------------------------------------------------------------------------------------------ all AI work
def test_every_kind_of_job_shows_as_ai_work_and_stop_all_stops_them(client):
    rid = _intake(client)
    cov = _intake(client, "coverage")
    assert client.post("/api/tools/schedule/elements", json={"run_ids": [rid]}).json()["queued"] == 1
    assert client.post(f"/api/casting/schedule/{rid}/read", json={}).json()["queued"] == 1
    assert client.post("/api/tools/coverage/write", json={"tool": "coverage", "run_ids": [cov]}).json()["queued"] == 1
    work = client.get("/api/jobs/active").json()
    assert [j["kind"] for j in work["jobs"]] == ["elements", "casting", "coverage"] and work["queued"] == 3 and work["running"] == 0
    assert work["kinds"]["elements"] == "Tagging elements"
    # the coverage-only count the top bar used to show would have said 1
    assert sum(client.get("/api/jobs?kind=coverage").json()["counts"].get(k, 0) for k in ("queued", "running")) == 1
    job = store.claim_job()                                             # the worker takes the first
    assert client.get("/api/jobs/active").json()["running"] == 1
    assert client.post("/api/jobs/stop-all").json()["stopped"] == 3
    assert client.get("/api/jobs/active").json()["jobs"] == []
    assert store.get_job(job["id"])["status"] == "cancelled"
    assert store.list_runs()["total"] == 2                              # the scripts are untouched


def test_a_stopped_job_still_in_its_last_step_is_shown_as_finishing(client, monkeypatch):
    rid = _intake(client)
    client.post("/api/tools/schedule/elements", json={"run_ids": [rid]})
    job = store.claim_job()
    monkeypatch.setattr(jobs, "_current", job)                          # the worker is inside this job's step
    client.post(f"/api/jobs/{job['id']}/cancel")
    work = client.get("/api/jobs/active").json()
    assert work["jobs"] == [] and work["finishing"]["id"] == job["id"] and work["finishing"]["title"]
    monkeypatch.setattr(jobs, "_current", None)
    assert client.get("/api/jobs/active").json()["finishing"] is None


def test_time_left_from_steps_and_from_earlier_runs(client):
    rid = _intake(client)
    client.post("/api/tools/schedule/elements", json={"run_ids": [rid]})
    job = store.claim_job()
    store.set_job(job["id"], started=_ago(600), progress="Tagging scenes 72–84 of 134")
    j = client.get("/api/jobs/active").json()["jobs"][0]
    assert j["eta_basis"] == "steps" and 500 <= j["eta_seconds"] <= 560      # 71 done in 600 s: 63 to go
    store.set_job(job["id"], progress="Tagging scenes 1–12 of 134")          # nothing finished yet: no made-up figure
    j = client.get("/api/jobs/active").json()["jobs"][0]
    assert j["eta_seconds"] is None and j["eta_basis"] is None
    store.set_job(job["id"], status="done", started=_ago(900), finished=_ago(300))      # that one took 10 minutes
    # a job with no steps to count (the shooting order) goes by how long it took before
    for took in (240, 300, 360):
        jid = store.enqueue("schedreason", "schedule", rid, "Night Ferry", {"mode": "deep"})["id"]
        store.set_job(jid, status="done", started=_ago(1000 + took), finished=_ago(1000))
    jid = store.enqueue("schedreason", "schedule", rid, "Night Ferry", {"mode": "deep"})["id"]
    store.claim_job()
    store.set_job(jid, started=_ago(100), progress="Reasoning out the shooting order")
    j = next(x for x in client.get("/api/jobs/active").json()["jobs"] if x["id"] == jid)
    assert j["eta_basis"] == "history" and 180 <= j["eta_seconds"] <= 220     # the middle run took 300 s; 100 s gone
    store.set_job(jid, started=_ago(400))
    j = next(x for x in client.get("/api/jobs/active").json()["jobs"] if x["id"] == jid)
    assert j["eta_seconds"] is None and j["eta_basis"] == "over"              # past the usual time: said, not guessed


def test_a_job_stopped_while_running_stays_stopped_not_failed(client, monkeypatch):
    rid = _intake(client)
    client.post("/api/tools/schedule/elements", json={"run_ids": [rid]})

    def boom(job):
        store.cancel_job(job["id"])                                       # stopped mid-step ...
        raise RuntimeError("the engine connection was reset")             # ... and then the step fails

    monkeypatch.setattr(jobs, "HANDLERS", {"elements": boom})
    monkeypatch.setattr(jobs._stop, "is_set", iter([False, True]).__next__)
    jobs._loop()
    j = client.get("/api/jobs?kind=elements").json()["jobs"][0]
    assert j["status"] == "cancelled" and not j["error"]
    assert jobs.busy() is None


def test_clear_history_takes_finished_jobs_off_the_lists_only(client):
    rid = _intake(client)
    for status in ("done", "error", "cancelled"):
        jid = store.enqueue("elements", "schedule", rid, "Night Ferry")["id"]
        store.set_job(jid, status=status)
    live = store.enqueue("casting", "schedule", rid, "Night Ferry")["id"]
    assert client.post("/api/jobs/clear-history").json()["cleared"] == 3
    left = client.get("/api/jobs").json()
    assert left["counts"].get("queued") == 1 and not any(left["counts"].get(k) for k in ("done", "error", "cancelled"))
    assert store.get_job(live)["status"] == "queued" and store.list_runs()["total"] == 1


# ------------------------------------------------------------------------------------------------ removing
def test_remove_puts_an_item_in_removed_and_it_can_be_put_back_or_deleted(client, tmp_path):
    rid = _intake(client)
    other = _intake(client, "coverage")
    client.post("/api/tools/schedule/elements", json={"run_ids": [rid]})
    folder = tmp_path / "runs" / "schedule" / rid
    assert folder.is_dir()
    r = client.delete(f"/api/runs/schedule/{rid}")
    assert r.status_code == 200 and r.json()["title"]
    assert not folder.exists() and (tmp_path / "removed" / "schedule" / rid / "run.json").is_file()      # moved, not erased
    assert [x["id"] for x in client.get("/api/runs").json()["runs"]] == [other]
    assert client.get(f"/api/runs/schedule/{rid}").status_code == 404
    assert client.get("/api/jobs/active").json()["jobs"] == []                # its waiting job was stopped
    assert client.delete(f"/api/runs/schedule/{rid}").status_code == 404      # already gone
    gone = client.get("/api/removed").json()["removed"]
    assert len(gone) == 1 and gone[0]["id"] == rid and gone[0]["removed"]
    back = client.post("/api/removed/restore", json={"key": gone[0]["key"]}).json()
    assert back["id"] == rid and folder.is_dir() and not (folder / "removed.json").exists()
    assert client.get(f"/api/runs/schedule/{rid}").status_code == 200 and client.get("/api/removed").json()["removed"] == []
    # remove again, then delete for good
    client.delete(f"/api/runs/schedule/{rid}")
    key = client.get("/api/removed").json()["removed"][0]["key"]
    assert client.post("/api/removed/delete", json={}).status_code == 400     # must say which, or all
    assert client.post("/api/removed/delete", json={"key": key}).json()["deleted"] == 1
    assert not (tmp_path / "removed" / "schedule" / rid).exists() and client.get("/api/removed").json()["removed"] == []
    assert client.post("/api/removed/restore", json={"key": key}).status_code == 404
    assert client.get(f"/api/runs/coverage/{other}").status_code == 200       # the other script never moved


def test_remove_everything_shown_and_paths_cannot_escape(client, tmp_path):
    a, b = _intake(client), _intake(client, "coverage")
    assert client.post("/api/runs/remove", json={}).status_code == 400
    r = client.post("/api/runs/remove", json={"all": True, "tool": "coverage"}).json()
    assert r["removed"] == 1 and [x["id"] for x in client.get("/api/runs").json()["runs"]] == [a]
    assert client.post("/api/runs/remove", json={"all": True}).json()["removed"] == 1
    assert client.get("/api/runs").json()["total"] == 0 and len(client.get("/api/removed").json()["removed"]) == 2
    (tmp_path / "keep.txt").write_text("x")
    for key in ("../..", "schedule/../../keep.txt", "..%2F..", "/etc"):
        assert client.post("/api/removed/delete", json={"key": key}).status_code == 404
        assert client.post("/api/removed/restore", json={"key": key}).status_code == 404
    assert (tmp_path / "keep.txt").exists() and (tmp_path / "library.db").exists()
    assert client.post("/api/removed/delete", json={"all": True}).json()["deleted"] == 2


def test_a_job_whose_script_was_removed_does_not_stop_the_queue(client, monkeypatch):
    rid = _intake(client)
    job = store.enqueue("elements", "schedule", rid, "Night Ferry")
    store.claim_job()
    store.remove_run("schedule", rid)                                     # removed while it ran
    assert store.get_job(job["id"])["status"] == "cancelled"              # so the worker's step check stops it
    monkeypatch.setattr(jobs._stop, "is_set", iter([False, True]).__next__)
    store.set_job(job["id"], status="queued")                             # even if it were still queued, the worker survives
    jobs._loop()
    assert store.get_job(job["id"])["status"] == "error" and "no longer in the Library" in store.get_job(job["id"])["error"]
    assert jobs.busy() is None


# ------------------------------------------------------------------------------------------------ cloud models
def test_a_retired_cloud_model_is_said_in_plain_words(monkeypatch):
    e = llm.Engine("cloud", "https://api.openai.com/v1", "gpt-5.5", "k", "openai")
    for raw in ('404 from u: {"error":{"message":"The model `gpt-5.5` does not exist or you do not have access to it.","code":"model_not_found"}}',
                '404 from u: {"type":"error","error":{"type":"not_found_error","message":"model: claude-sonnet-5-5"}}',
                '404 from u: {"error":{"code":404,"message":"models/gemini-3.8-flash is not found for API version v1beta"}}',
                '400 from u: {"error":{"message":"The model gpt-5.5 has been deprecated"}}'):
        got = llm.retired(e, llm.EngineError(raw))
        assert isinstance(got, llm.ModelRetired) and "gpt-5.5" in str(got) and "Settings" in str(got) and "404" not in str(got)
    for raw in ("401 from u: bad key", "429 from u: rate limit reached for model", '400 from u: {"error":{"message":"Unsupported parameter: response_format"}}',
                "500 from u: model overloaded"):
        err = llm.EngineError(raw)
        assert llm.retired(e, err) is err
    local = llm.Engine("openai", "http://127.0.0.1:1/v1", "gemma")
    err = llm.EngineError("404 from u: model_not_found")
    assert llm.retired(local, err) is err                                 # only the cloud account's models retire

    def gone(url, body=None, **kw):
        raise llm.EngineError('404 from u: {"error":{"code":"model_not_found","message":"The model `gpt-5.5` does not exist"}}')

    monkeypatch.setattr(llm, "_http", gone)
    with pytest.raises(llm.ModelRetired):
        llm.chat(e, "s", "u", settings={})
    with pytest.raises(llm.ModelRetired):
        llm.chat(e, "s", "u", settings={}, schema={"type": "object", "properties": {}})


def test_the_model_list_leaves_out_models_that_cannot_write_and_says_if_the_one_in_use_is_gone(client, monkeypatch):
    from studio import keys
    ids = ["gpt-5.6-luna", "gpt-5.5-mini", "text-embedding-3-large", "whisper-1", "gpt-image-2", "tts-1", "omni-moderation-latest", "o4-mini"]
    monkeypatch.setattr(llm, "_http", lambda url, body=None, **kw: {"data": [{"id": i} for i in ids]})
    monkeypatch.setattr(keys, "get", lambda p: "sk-test")
    r = client.get("/api/cloud/models?provider=openai").json()
    assert r["models"] == ["gpt-5.6-luna", "gpt-5.5-mini", "o4-mini"]
    assert r["in_use"] == llm.CLOUD["openai"]["model"] and r["listed"] is False       # the built-in default has been retired
    s = store.load_settings()
    s["cloud_ai"].update(provider="openai", model="gpt-5.6-luna")
    store.save_settings(s)
    r = client.get("/api/cloud/models?provider=openai").json()
    assert r["in_use"] == "gpt-5.6-luna" and r["listed"] is True


def test_web_admin_chooses_the_ai_brain_model(tmp_path, monkeypatch):
    from studio import web
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path))
    monkeypatch.setenv("STUDIO_AI_PROVIDER", "openai")
    monkeypatch.setenv("STUDIO_AI_KEY", "sk-test")
    monkeypatch.setenv("STUDIO_AI_MODEL", "gpt-old")
    assert web.ai()["model"] == "gpt-old"
    s = store.load_settings()
    s["web_ai"] = {"provider": "openai", "model": "gpt-new"}
    store.save_settings(s)
    assert web.ai()["model"] == "gpt-new"                                 # the admin's choice comes before the server's
    s["web_ai"] = {"provider": "anthropic", "model": "claude-x"}          # 1.3.4: the admin's provider choice wins outright
    store.save_settings(s)
    a = web.ai()
    assert a["provider"] == "anthropic" and a["model"] == "claude-x" and a["key"] == ""   # the server's OpenAI key isn't Claude's
    s["web_ai"] = {"provider": "openai", "model": ""}                     # blank: back to the server's own setting
    store.save_settings(s)
    assert web.ai()["model"] == "gpt-old"


# ------------------------------------------------------------------------------------------------ casting
INTRO = ("INT. PUB - NIGHT\n\nDAVIE (20s), a nervous Scotsman with boyish looks, grins at MIRREN (20s), a calm Scots woman "
         "with titian hair. She nods.\n\nZANDER, 23, movie-star handsome, slumps at the bar. He drinks.\n\n"
         "SARAH OKAFOR, early forties, waits by the door. She checks her phone.\n\nHOLLIE brings coffee for ZANDER, who ignores her.\n")


@pytest.mark.parametrize("name, age, gender", [
    ("DAVIE", (20, 29), ("Male", "words")), ("MIRREN", (20, 29), ("Female", "words")), ("ZANDER", (23, 23), ("Male", "pronoun")),
    ("SARAH", (40, 43), ("Female", "pronoun")), ("HOLLIE", None, None)])
def test_the_scripts_own_wording_gives_age_and_gender(name, age, gender):
    assert casting.age_from_text(INTRO, name) == age
    assert casting.gender_from_text(INTRO, name) == gender


@pytest.mark.parametrize("text, name, age, gender", [
    ("MARA (34) wipes her hands.", "MARA", (34, 34), None),                                 # 1.1.6's bracket form still reads
    ("MARA OKAFOR (late 40s) wipes her hands.", "MARA", (46, 49), None),
    ("JEN - 16 years old - stares.", "JEN", (16, 16), None),
    ("We meet RUTH, a sharp journalist in her fifties.", "RUTH", (50, 59), ("Female", "words")),
    ("JACK, 40s, the kind of man who irons his jeans, waits.", "JACK", (40, 49), ("Male", "words")),
    ("LANA - a tall woman - enters.", "LANA", None, ("Female", "words")),
    ("MRS HALE opens the door.", "MRS HALE", None, ("Female", "name")),
    ("GIRLFRIEND rolls her eyes.", "GIRLFRIEND", None, ("Female", "name")),
    ("TEENAGE MIRREN runs.", "TEENAGE MIRREN", (13, 19), None),
    # nothing is read into words about someone else, a time, or a decade
    ("MARA hugs him. He cries.", "MARA", None, None),
    ("MARA and TOM wait. He sighs.", "MARA", None, None),
    ("MARA hugs her son.", "MARA", None, None),
    ("DAVIE, 2 minutes later, returns.", "DAVIE", None, None),
    ("In 1980s Glasgow, BILL waits.", "BILL", None, None),
    ("SKY watches the human crowd.", "SKY", None, None)])
def test_readings_of_the_wording_are_careful(text, name, age, gender):
    assert casting.age_from_text(text, name) == age
    assert casting.gender_from_text(text, name) == gender


def test_script_reading_covers_every_part_and_the_model_fills_the_rest():
    b = script.parse("ferry.fountain", FERRY)
    said = casting.script_reading("ferry.fountain", FERRY, b)
    names = {r["name"] for r in casting.roles(b)}
    assert said and set(said) <= names
    assert all(v["source"] == "script" and v["gender"] in casting.GENDERS for v in said.values())
    one = next(iter(said))
    # the model's reading wins; where it leaves the gender open, the script's stays
    merged = casting.merge_readings({one: {"gender": "Female", "gender_from": "words", "source": "script", "age_low": 30, "age_high": 39}},
                                    {one: {"gender": "Any", "age_low": None, "age_high": None, "description": "d", "source": "model"}})
    assert merged[one]["gender"] == "Female" and merged[one]["age_low"] == 30 and merged[one]["description"] == "d"
    merged = casting.merge_readings({one: {"gender": "Female", "source": "script"}}, {one: {"gender": "Male", "age_low": 50, "age_high": 55, "source": "model"}})
    assert merged[one]["gender"] == "Male" and merged[one]["age_low"] == 50
    assert casting.merge_readings({"X": {"gender": "Male", "source": "script"}}, None) == {"X": {"gender": "Male", "source": "script"}}


def _tier(name):
    return refdata.rows("SELECT commercial_tier t FROM talent_actors WHERE actor = ?", name)[0]["t"]


def test_pairing_follows_the_tier_level():
    cast = [{"name": "MARA", "size": "Lead", "gender": "Female", "age_low": 30, "age_high": 39},
            {"name": "TOM", "size": "Supporting", "gender": "Male", "age_low": 40, "age_high": 49}]
    rows = refdata.rows("SELECT commercial_tier, minimum_sensible_budget_usd FROM talent_actors")
    top = casting.top_tier(rows, 20_000_000)
    assert top == "A-" and casting.top_tier(rows, None) is None
    mara, tom = casting.shortlist(cast, budget_usd=20_000_000)
    ti = casting.TIERS.index
    assert mara["shortlist"] and all(ti(a["tier"]) >= ti(top) for a in mara["shortlist"])
    assert mara["shortlist"][0]["tier"] == top                                 # the best the budget carries leads
    assert tom["shortlist"] and all(ti(a["tier"]) > ti(top) for a in tom["shortlist"])      # support starts a tier below
    assert "one below" in tom["filters"]["tier_basis"] and top in mara["filters"]["tier_basis"]
    assert all(a["tier_fit"] in ("within", "stretch") for a in mara["shortlist"] + tom["shortlist"])
    assert all(a["tier"] == _tier(a["actor"]) for a in mara["shortlist"] + tom["shortlist"])    # tiers are the database's
    # a chosen level keeps to that level, for leads and for support
    mara, tom = casting.shortlist(cast, budget_usd=20_000_000, tier_lead="B", tier_support="C")
    assert {a["tier"] for a in mara["shortlist"]} <= {"B+", "B", "B-"} and {a["tier"] for a in tom["shortlist"]} <= {"C+", "C", "Emerging"}
    # a level the budget can't carry gives no one, and says how many need a bigger budget
    mara = casting.shortlist(cast[:1], budget_usd=2_000_000, tier_lead="A")[0]
    assert mara["shortlist"] == [] and mara["over_budget"] == mara["considered"] > 0
    # no budget: nothing to grade against, every tier open
    assert casting.shortlist(cast[:1])[0]["filters"]["tiers"] == list(casting.TIERS)


def test_search_by_name_finds_anyone_and_says_how_they_fit():
    role = {"name": "MARA", "size": "Lead", "gender": "Female", "age_low": 30, "age_high": 39}
    hits = casting.search("chris", role, budget_usd=5_000_000)
    assert hits and all("chris" in h["actor"].lower() for h in hits)
    assert hits[0]["actor"].lower().startswith("chris")                         # names that start with it come first
    assert all(set(h["fits"]) == {"gender", "age", "budget"} for h in hits)
    male = next(h for h in hits if h["gender"] == "Male")
    assert male["fits"]["gender"] is False                                      # shown, and said to be outside the reading
    assert casting.search("", role) == [] and casting.search("zzzzqq", role) == []
    names = {r["actor"] for r in refdata.rows("SELECT actor FROM talent_actors")}
    assert all(h["actor"] in names for h in hits)                               # no name is invented


def test_casting_api_reads_the_wording_keeps_tier_levels_and_searches(client):
    rid = _intake(client)
    view = client.get(f"/api/casting/schedule/{rid}").json()
    assert view["tier_lead"] == "auto" and view["tier_support"] == "auto" and view["read"] is None
    kept = store.get_run("schedule", rid)[0]["outputs"]["casting_script"]
    assert kept["stamp"][0] == casting.SCRIPT_READ_VERSION                       # read once, kept with the run
    view = client.put(f"/api/casting/schedule/{rid}", json={"budget_usd": 20_000_000, "tier_lead": "B", "tier_support": "nonsense"}).json()
    assert view["tier_lead"] == "B" and view["tier_support"] == "auto" and view["top_tier"] == "A-"
    lead = next((r for r in view["roles"] if r["size"] == "Lead"), None)
    if lead and lead["shortlist"]:
        assert {a["tier"] for a in lead["shortlist"]} <= {"B+", "B", "B-"}
    role = view["roles"][0]["name"]
    res = client.get(f"/api/casting/schedule/{rid}/search", params={"q": "chris", "role": role}).json()
    assert res["role"] == role and res["actors"] and "fits" in res["actors"][0]
    assert client.get(f"/api/casting/schedule/{rid}/search", params={"q": "chris", "role": "NOBODY"}).json()["role"] is None
    assert client.get("/api/casting/schedule/nope/search", params={"q": "chris"}).status_code == 404


def test_gender_from_their_own_things_in_the_naming_sentence():
    from studio import casting
    g = casting.gender_from_text("MARA OKAFOR (34), a ship's engineer in a battered waxed jacket, jogs along the quay, a toolbag over her shoulder.", "MARA")
    assert g == ("Female", "pronoun")
    assert casting.gender_from_text("JOHN (40) steadies himself on the rail.", "JOHN") == ("Male", "pronoun")
    assert casting.gender_from_text("JOHN (40) hands her the keys.", "JOHN") is None          # her is someone else
    assert casting.gender_from_text("JOHN (40) puts his coat over her shoulder.", "JOHN") is None   # two people
    assert casting.gender_from_text("ALEX (30) waits with SAM, a bag on her lap.", "ALEX") is None  # someone else is named
