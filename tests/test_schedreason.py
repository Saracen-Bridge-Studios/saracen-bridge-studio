"""Scheduling & Budgeting: the reasoned shooting order (1.1.6), with the model stood in for."""
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from studio import budget, llm, schedreason, script

FIX = Path(__file__).parent / "fixtures"
DATA = (FIX / "night_ferry.fountain").read_bytes()
B = script.parse("night_ferry.fountain", DATA)
NIGHT = {s["number"] for s in B["scenes"] if budget._night(s.get("time_of_day"))}
ALL = [s["number"] for s in B["scenes"]]


def _answer(days, changes=None):
    return {"days": [{"scenes": d, "note": f"note {i}"} for i, d in enumerate(days, 1)],
            "changes": changes or [{"change": "Blocked Mara's scenes", "reason": "Fewer hold days"}], "risks": ["Rain cover"]}


@pytest.fixture
def model(monkeypatch):
    box = {}

    def chat(engine, system, user, *, schema=None, **kw):
        box.update(system=system, user=user, schema=schema, kw=kw)
        return box["answer"]

    monkeypatch.setattr(llm, "resolve", lambda settings, mode=None, use="writing": (llm.Engine("openai", "http://127.0.0.1:1/v1", "gemma"), ""))
    monkeypatch.setattr(llm, "chat", chat)
    return box


def test_the_model_sees_every_scene_and_the_first_pass(model):
    day = [n for n in ALL if n not in NIGHT]
    model["answer"] = _answer([day[:len(day) // 2], day[len(day) // 2:], sorted(NIGHT)])
    res = schedreason.reason(B, {"ai_engine": {"context": 16384}}, pages_per_day=4)
    assert all(f"S{n} |" in model["user"] for n in ALL) and "STARTING STRIPBOARD" in model["user"] and "already optimised" in model["user"]
    assert "never more than 5 pages" in model["system"] and model["kw"]["think"] is True        # Deep by default
    assert sorted(n for d in res["days"] for n in d) == ALL and not res["repairs"]
    assert res["changes"][0]["reason"] == "Fewer hold days" and res["risks"] == ["Rain cover"]
    m = res["measures"]
    assert set(m) == {"reasoned", "first_pass", "optimised"} and m["first_pass"]["days"] == len(budget.stripboard(B, 4))
    assert m["reasoned"]["days"] == 3 and all(not (d["night"] and set(d["scenes"]) - NIGHT) for d in res["board"])


def test_a_bad_answer_is_repaired_not_trusted(model):
    day = [n for n in ALL if n not in NIGHT]
    mixed = [day[0], sorted(NIGHT)[0]]                                  # day and night on one day
    rest = [n for n in ALL if n not in mixed]
    model["answer"] = _answer([mixed, rest[:-1] + [rest[0]], [999]])    # a repeat, an unknown scene, the last scene left out
    res = schedreason.reason(B, {}, pages_per_day=40)
    flat = [n for d in res["days"] for n in d]
    assert sorted(flat) == ALL and len(flat) == len(set(flat))
    text = " ".join(res["repairs"])
    assert "twice" in text and "mixed day and night" in text and f"Scene {rest[-1]} was left out" in text
    assert all(len({budget._night(next(s for s in B["scenes"] if s["number"] == n).get("time_of_day")) for n in d}) == 1 for d in res["days"])


def test_the_budget_can_use_the_reasoned_order(model, tmp_path, monkeypatch):
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path))
    from studio import jobs, store
    from studio.server import app
    c = TestClient(app)
    rec = store.save_run("schedule", "The Night Ferry", {"file": "night_ferry.fountain", "sha256": "nf"}, {"breakdown": B},
                         files={"night_ferry.fountain": DATA}, summary={"scene_count": B["scene_count"]})
    day = [n for n in ALL if n not in NIGHT]
    model["answer"] = _answer([day, sorted(NIGHT)])
    monkeypatch.setattr(jobs, "ensure_worker", lambda: None)
    assert c.post("/api/tools/schedule/reason", json={"run_id": rec["id"]}).json()["mode"] == "deep"
    jobs.run_schedreason(store.claim_job())
    saved, _ = store.get_run("schedule", rec["id"])
    assert len(saved["outputs"]["schedule_reasoned"]["days"]) == 2
    body = {"run_id": rec["id"], "jurisdiction": "United Kingdom", "pages_per_day": {"lean": 40, "base": 40, "conservative": 40}}
    first = c.post("/api/tools/schedule/budget", json=body).json()
    used = c.post("/api/tools/schedule/budget", json=dict(body, use_reasoned=True)).json()
    assert used["schedule_source"] == "reasoned" and used["settings"]["use_reasoned"] and not first["settings"]["use_reasoned"]
    assert [d["scenes"] for d in used["stripboard"]] == [day, sorted(NIGHT)] and used["schedule"]["base"]["shoot_days"] == 2
    assert "reasoned order" in used["assumptions"][1]
    assert c.post("/api/tools/schedule/reason", json={"run_id": "nope"}).status_code == 404


def _held_breakdown():
    """Six one-page scenes at three sites. XAN works at sites A and C, YUL only at B: the first pass (by site) holds
    XAN for the two B days; shooting A, C, then B holds nobody."""
    scenes = []
    for i, (site, who) in enumerate([("ALPHA", ["XAN"]), ("ALPHA", ["XAN"]), ("BRAVO", ["YUL"]), ("BRAVO", ["YUL"]),
                                     ("CHARLIE", ["XAN"]), ("CHARLIE", ["XAN"])], 1):
        scenes.append({"number": i, "heading": f"INT. {site} - DAY", "int_ext": "INT", "location": site, "time_of_day": "DAY",
                       "characters": who, "lines": 56})
    return {"pages": 6, "scene_count": 6, "scenes": scenes, "cast": [{"name": "XAN", "dialogue_blocks": 20}, {"name": "YUL", "dialogue_blocks": 10}]}


def test_the_studio_optimises_the_order_itself_before_any_ai():
    b = _held_breakdown()
    first = schedreason.metrics(b, budget.stripboard(b, 1), 1)
    opt = schedreason.optimise(b, 1)
    assert first["hold_days"] == 2 and opt["measures"]["hold_days"] == 0
    assert opt["measures"]["days"] <= first["days"] and opt["measures"]["moves"] <= first["moves"]
    assert sorted(opt["order"]) == [1, 2, 3, 4, 5, 6] and opt["first_pass"] == first
    # never worse than the first pass on the fixture either, every scene once, day and night apart
    o = schedreason.optimise(B, 4)
    key = lambda m: (m["days"], m["moves"], m["hold_days"])
    assert key(o["measures"]) <= key(o["first_pass"]) and sorted(o["order"]) == ALL
    assert all(len({budget._night(next(s for s in B["scenes"] if s["number"] == n).get("time_of_day")) for n in d["scenes"]}) == 1 for d in o["board"])


def test_the_budget_can_use_the_optimised_order(tmp_path, monkeypatch):
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path))
    from studio import store
    from studio.server import app
    c = TestClient(app)
    b = _held_breakdown()
    rec = store.save_run("schedule", "Held", {"file": "x.fountain", "sha256": "h"}, {"breakdown": b}, summary={"scene_count": 6})
    r = c.post("/api/tools/schedule/optimise", json={"run_id": rec["id"], "pages_per_day": 1}).json()
    assert r["measures"]["hold_days"] == 0
    body = {"run_id": rec["id"], "jurisdiction": "United Kingdom", "pages_per_day": {"lean": 1, "base": 1, "conservative": 1}}
    used = c.post("/api/tools/schedule/budget", json=dict(body, use_order="optimised")).json()
    assert used["schedule_source"] == "optimised" and used["settings"]["use_order"] == "optimised"
    dood = {d["name"]: d for d in used["dood"]}
    assert dood["XAN"]["hold_days"] == 0 and "optimised order" in used["assumptions"][1]
    plain = c.post("/api/tools/schedule/budget", json=body).json()
    assert plain["settings"]["use_order"] == "first" and {d["name"]: d for d in plain["dood"]}["XAN"]["hold_days"] == 2


def test_the_fast_evaluator_agrees_with_the_stripboard():
    import random
    rng = random.Random(7)
    b = _held_breakdown()
    big = {"pages": 40, "scene_count": 40, "cast": [{"name": f"A{i}", "dialogue_blocks": 5} for i in range(6)],
           "scenes": [{"number": i + 1, "heading": "x", "int_ext": rng.choice(["INT", "EXT"]), "location": f"S{rng.randint(1, 8)}",
                       "time_of_day": rng.choice(["DAY", "NIGHT"]), "characters": rng.sample([f"A{k}" for k in range(6)], rng.randint(1, 3)),
                       "lines": rng.randint(5, 150)} for i in range(40)]}
    for bd, ppd in ((b, 1), (big, 4), (big, 2.5), (B, 4)):
        ev = schedreason._Eval(bd, ppd)
        nums = [s["number"] for s in bd["scenes"]]
        for _ in range(30):
            rng.shuffle(nums)
            m = schedreason.metrics(bd, budget.stripboard(bd, ppd, order=nums), ppd)
            assert ev(nums) == (m["days"], m["moves"], m["hold_days"])
