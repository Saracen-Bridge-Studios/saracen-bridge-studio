"""Sales Agents: Jon's Sales Agent scoring specification v1.0 (21 Oct 2026). Tests 01-20 are his acceptance tests,
in his numbering; the rest cover his register, delivery checklist and invariants."""
import itertools

import pytest
from fastapi.testclient import TestClient

from studio import agents as A

G = {"horror", "thriller", "drama", "comedy", "action"}
INT, DIST = "INTERNATIONAL_SALES", "DISTRIBUTION"


def s(base, f1, f2=None, *, g1="horror", g2=None, scope=INT, req=INT):
    return A.score_agent(base, scope, req, g1, f1, g2 if g2 or f2 is None else "thriller", f2, known_genres=G)


def test_01_to_05_single_genre():
    assert s(93, "CORE")["adjustedScore"] == 93
    r = s(93, "SECONDARY"); assert (r["adjustedScore"], r["rawScore"]) == (84, 83.70)
    r = s(93, "LIMITED"); assert (r["adjustedScore"], r["rawScore"]) == (70, 69.75)
    r = s(93, "OUTSIDE"); assert (r["adjustedScore"], r["rawScore"]) == (56, 55.80)
    assert s(80, "CORE")["adjustedScore"] == 80


def test_06_to_09_two_genres_at_70_30():
    r = s(88, "CORE", "OUTSIDE")
    assert (r["status"], r["adjustedScore"], r["weightedMultiplier"], r["discountPercent"], r["rawScore"], r["pointsDeducted"]) == \
        ("SCORED", 77, 0.88, 12, 77.44, 11)
    r = s(88, "OUTSIDE", "CORE"); assert (r["adjustedScore"], r["rawScore"]) == (63, 63.36)
    r = s(83, "SECONDARY", "LIMITED"); assert (r["adjustedScore"], r["rawScore"]) == (71, 70.965)
    assert s(83, "CORE", "CORE")["adjustedScore"] == 83


def test_10_half_rounds_up_and_11_bounds():
    r = s(90, "LIMITED"); assert (r["adjustedScore"], r["rawScore"]) == (68, 67.5)
    assert s(0, "CORE")["adjustedScore"] == 0 and s(100, "CORE")["adjustedScore"] == 100


def test_12_13_unverified_fit_needs_review():
    r = s(88, "UNVERIFIED"); assert r["status"] == "NEEDS_REVIEW" and r["adjustedScore"] is None and r["rawScore"] is None
    r = s(88, "CORE", "UNVERIFIED"); assert r["status"] == "NEEDS_REVIEW" and r["adjustedScore"] is None   # never primary alone


def test_14_to_17_invalid_input():
    assert A.score_agent(88, INT, INT, "horror", "CORE", None, "CORE", known_genres=G)["status"] == "INVALID_INPUT"   # 14
    assert A.score_agent(88, INT, INT, "horror", "CORE", "horror", "CORE", known_genres=G)["reasonCode"] == "GENRES_IDENTICAL"  # 15
    for bad in (None, -1, 101, 82.5, "83", True):                                                                  # 16
        assert A.score_agent(bad, INT, INT, "horror", "CORE", known_genres=G)["status"] == "INVALID_INPUT", bad
    assert A.score_agent(88, INT, INT, None, "CORE", known_genres=G)["reasonCode"] == "PRIMARY_GENRE_MISSING"        # 17
    assert A.score_agent(88, INT, INT, "noir", "CORE", known_genres=G)["reasonCode"] == "PRIMARY_GENRE_UNKNOWN"
    assert A.score_agent(88, INT, INT, "horror", "GREAT", known_genres=G)["reasonCode"] == "PRIMARY_FIT_INVALID"


def test_18_19_saban_scope():
    r = s(83, "CORE", scope=DIST, req=INT); assert r["status"] == "SCOPE_MISMATCH" and r["adjustedScore"] is None
    r = s(83, "CORE", scope=DIST, req=DIST); assert r["status"] == "SCORED" and r["adjustedScore"] == 83


def test_20_same_input_same_output_and_invariants():
    assert s(83, "SECONDARY", "LIMITED") == s(83, "SECONDARY", "LIMITED")
    order = ["CORE", "SECONDARY", "LIMITED", "OUTSIDE"]
    for base in (0, 37, 80, 83, 88, 93, 100):
        for f1, f2 in itertools.product(order, [None, *order]):
            r = s(base, f1, f2)
            assert isinstance(r["adjustedScore"], int) and 0 <= r["adjustedScore"] <= base       # integer, 0..base
            weaker = order[min(order.index(f1) + 1, 3)]
            assert s(base, weaker, f2)["adjustedScore"] <= r["adjustedScore"]                    # weakening never raises


def test_the_register_is_jons_26_exactly():
    reg = A.register()
    a = {x["agentId"]: x for x in reg["agents"]}
    assert len(a) == 26 and reg["dataVersion"] == "2026-10-21" and reg["formulaVersion"] == "1.0"
    assert (a["sa001"]["baseScore"], a["sa011"]["baseScore"], a["sa022"]["baseScore"], a["sa025"]["baseScore"]) == (93, 88, 80, 83)
    assert a["sa025"]["scoreScope"] == DIST and all(x["scoreScope"] == INT for k, x in a.items() if k != "sa025")
    assert all(x["baseScoreStatus"] == "PROVISIONAL" and x["estimateAccuracyScore"] is None and x["trustworthinessScore"] is None
               for x in a.values())
    assert sum(x["baseScore"] for x in a.values()) == 2216
    for alias, want in (("High flyers", "sa024"), ("Nora Films", "sa023"), ("Capture", "sa021"), ("Saban", "sa025"),
                        ("International Film Trust", "sa026"), ("IFT", "sa026")):
        assert A.resolve_name(alias)["agentId"] == want


def test_genres_are_tims_list_as_canonical_ids():
    ids = A.genre_ids()
    assert len(ids) == 18 and {"science_fiction", "historical_period", "biographical_biopic", "horror"} <= ids
    assert A.genre_id("Science fiction") == "science_fiction" and A.genre_id("Family") is None


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path))
    from studio.server import app
    return TestClient(app)


def _project(c, genre="Horror", secondary=None):
    from studio import store
    intake = {"title": "Night Ferry", "genre": genre}
    if secondary:
        intake["secondary_genre"] = secondary
    return store.save_run("sales", "Night Ferry", {"intake": intake}, {})["id"]


def test_comparison_ranks_explains_and_keeps_unscored_apart(client):
    pid = _project(client, "Horror", "Thriller")
    c = client.get(f"/api/agents/compare?project={pid}").json()
    assert not c["scored"] and len(c["unscored"]) == 26                         # nothing assessed yet: all need review
    assert {r["result"]["status"] for r in c["unscored"]} == {"NEEDS_REVIEW", "SCOPE_MISMATCH"}
    fit = lambda a, g, f, **kw: client.post("/api/agents/fit", json={"project": pid, "agent": a, "genre": g, "fit": f,
                                             "rationale": "Register: horror is a listed speciality", "evidence": "Register 2026-10-21",
                                             "assessor": "Tim", **kw})
    assert fit("sa002", "horror", "CORE").status_code == 200 and fit("sa002", "thriller", "CORE").status_code == 200
    assert fit("sa011", "horror", "CORE").status_code == 200 and fit("sa011", "thriller", "OUTSIDE").status_code == 200
    bad = client.post("/api/agents/fit", json={"project": pid, "agent": "sa011", "genre": "horror", "fit": "CORE", "assessor": "Tim"})
    assert bad.status_code == 400                                               # a fit needs its rationale and evidence
    c = client.get(f"/api/agents/compare?project={pid}").json()
    assert [r["agentId"] for r in c["scored"]] == ["sa002", "sa011"]
    assert c["scored"][1]["result"]["adjustedScore"] == 77 and "Weighted discount 12%" in c["scored"][1]["explanation"]
    assert c["scored"][0]["provisional"] is True                                # provisional base score and fit
    saban = next(r for r in c["unscored"] if r["agentId"] == "sa025")
    assert saban["result"]["status"] == "SCOPE_MISMATCH" and "unavailable for this mandate" in saban["explanation"]
    d = client.get(f"/api/agents/compare?project={pid}&scope=DISTRIBUTION").json()
    assert all(r["agentId"] != "sa002" for r in d["scored"])                   # international scores never rank here


def test_ties_sort_by_base_then_name(client):
    pid = _project(client, "Drama")
    for a in ("sa012", "sa013", "sa001"):                                       # 83, 83, 93
        client.post("/api/agents/fit", json={"project": pid, "agent": a, "genre": "drama", "fit": "CORE" if a != "sa001" else "LIMITED",
                                             "rationale": "r", "evidence": "e", "assessor": "Tim"})
    c = client.get(f"/api/agents/compare?project={pid}").json()
    assert [(r["agentId"], r["result"]["adjustedScore"]) for r in c["scored"]] == [("sa013", 83), ("sa012", 83), ("sa001", 70)]
    # 83 tie: base equal, so name: Cornerstone before Mister Smith


def test_an_approved_mapping_is_reused_only_for_the_exact_genre(client):
    p1, p2 = _project(client, "Horror"), _project(client, "Thriller")
    client.post("/api/agents/fit", json={"project": p1, "agent": "sa024", "genre": "horror", "fit": "CORE", "rationale": "Commercial horror",
                                         "evidence": "Register", "assessor": "Tim", "save_mapping": True})
    p3 = _project(client, "Horror")
    r3 = next(r for r in client.get(f"/api/agents/compare?project={p3}").json()["scored"] if r["agentId"] == "sa024")
    assert r3["primary"]["from"] == "approved mapping" and r3["result"]["adjustedScore"] == 80
    r2 = next(r for r in client.get(f"/api/agents/compare?project={p2}").json()["unscored"] if r["agentId"] == "sa024")
    assert r2["primary"]["fit"] == "UNVERIFIED"                                 # thriller isn't horror: never inherited


def test_admin_edit_is_audited_and_versions_the_data(client):
    r = client.put("/api/agents/sa024", json={"baseScore": 82, "editor": "Jon", "reason": "New market slate"})
    assert r.status_code == 200 and r.json()["baseScore"] == 82
    assert client.put("/api/agents/sa024", json={"baseScore": 82.5, "editor": "Jon", "reason": "x"}).status_code == 400
    assert client.put("/api/agents/sa024", json={"baseScore": 81}).status_code == 400              # name and reason needed
    reg = client.get("/api/agents").json()
    assert reg["dataVersion"] != "2026-10-21" and reg["seedVersion"] == "2026-10-21"
    h = client.get("/api/agents/history").json()
    assert h[0]["old"] == 80 and h[0]["new"] == 82 and h[0]["editor"] == "Jon" and h[0]["reason"] == "New market slate"


def test_export_keeps_nulls_unrated_and_saves_a_snapshot(client):
    pid = _project(client, "Horror")
    client.post("/api/agents/fit", json={"project": pid, "agent": "sa002", "genre": "horror", "fit": "CORE", "rationale": "r",
                                         "evidence": "e", "assessor": "Tim"})
    x = client.get(f"/api/agents/compare.csv?project={pid}")
    text = x.content.decode("utf-8-sig")
    assert x.status_code == 200 and "Black Bear International" in text and "Unrated" in text
    row = next(l for l in text.splitlines() if l.startswith("1,Black Bear"))
    assert ",93,SCORED," in row and ",0," not in row


def test_known_sales_feedback_names_a_company_in_the_workbook(tmp_path, monkeypatch):
    from studio import sales
    w = sales.writes({"intake": {"title": "X", "sales_feedback": {"agent": "sa005", "note": "Strong interest at AFM"}}})
    assert w["PROJECT_INTAKE!B29"] == "Protagonist Pictures: Strong interest at AFM"


def test_ai_suggestions_are_provisional_attributed_and_never_overwrite(client, monkeypatch):
    from studio import llm
    pid = _project(client, "Horror")
    client.post("/api/agents/fit", json={"project": pid, "agent": "sa002", "genre": "horror", "fit": "LIMITED", "rationale": "Tim's view",
                                         "evidence": "Call note", "assessor": "Tim"})
    seen = {}

    def fake_chat(engine, system, user, **kw):
        seen["user"] = user
        return {"fits": [{"agentId": "sa002", "genreId": "horror", "fit": "CORE", "rationale": "Horror listed"},      # already assessed
                         {"agentId": "sa011", "genreId": "horror", "fit": "CORE", "rationale": "Horror listed"},
                         {"agentId": "sa012", "genreId": "horror", "fit": "OUTSIDE", "rationale": ""},              # no rationale: dropped
                         {"agentId": "sa013", "genreId": "horror", "fit": "UNVERIFIED", "rationale": "Not mentioned"},
                         {"agentId": "zz999", "genreId": "horror", "fit": "CORE", "rationale": "x"}]}             # not a company
    monkeypatch.setattr(llm, "resolve", lambda s, m=None, use="writing": (llm.Engine("openai", "http://127.0.0.1:9", "t"), ""))
    monkeypatch.setattr(llm, "chat", fake_chat)
    r = client.post("/api/agents/suggest", json={"project": pid}).json()
    assert r["assessed"] == 2 and "sa002 Black Bear" in seen["user"]
    c = client.get(f"/api/agents/compare?project={pid}").json()
    rows = {x["agentId"]: x for x in c["scored"] + c["unscored"]}
    assert rows["sa002"]["primary"]["fit"] == "LIMITED" and rows["sa002"]["primary"]["assessedBy"] == "Tim"
    assert rows["sa011"]["primary"]["assessedBy"] == "Jonny (AI)" and rows["sa011"]["primary"]["evidenceStatus"] == "PROVISIONAL"
    assert rows["sa012"]["primary"]["fit"] == "UNVERIFIED" and rows["sa013"]["result"]["status"] == "NEEDS_REVIEW"
