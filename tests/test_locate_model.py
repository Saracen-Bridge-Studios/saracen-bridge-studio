"""1.2.2 (Tim, 5 Nov, with Jon's 2019 Intel MacBook Pro on a call): Gemma downloaded by hand is found in Downloads or
chosen from any folder; the engine is sized to the machine's memory; a queue left from the last session waits until the
window is up. On that 8 GB Mac the Studio stayed black while it loaded Gemma with two 16K slots at launch."""
import os
import threading
import time
from pathlib import Path

import pytest

from studio import fetch, jobs, llm, store

GB = 1_000_000_000


def big(path: Path, size: int = llm.MIN_MODEL_BYTES + 1) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:                       # sparse: the size is what counts, not the bytes
        f.truncate(size)
    return path


@pytest.fixture()
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path / "data"))
    monkeypatch.delenv("STUDIO_LLM_DIR", raising=False)
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path / "user"))
    (tmp_path / "data" / "llm").mkdir(parents=True)
    return tmp_path


def engine(home: Path) -> Path:
    exe = home / "data" / "llm" / llm.SERVER_EXE
    exe.write_text("")
    return exe


def test_a_gemma_in_downloads_is_found(home):
    dl = home / "user" / "Downloads"
    big(dl / "gemma-4-E4B_q4_0-it.gguf"); big(dl / "gemma-4-E4B-it-mmproj.gguf"); big(dl / "other-model.gguf")
    big(dl / "gemma-small.gguf", 1000)                # half-downloaded or not a real model
    assert [m.name for m in llm.located_models()] == ["gemma-4-E4B_q4_0-it.gguf"]
    assert llm.bundled_files() is None                # no engine yet
    engine(home)
    exe, m = llm.bundled_files()
    assert m.name == "gemma-4-E4B_q4_0-it.gguf" and llm.projector_for(m).name == "gemma-4-E4B-it-mmproj.gguf"
    assert llm.model_file("gemma-4-E4B_q4_0-it") == m
    assert llm.resolve({"ai_engine": {"provider": "bundled"}}, use="")[0].model == "gemma-4-E4B_q4_0-it"


def test_the_studios_own_folder_comes_before_downloads_and_a_chosen_file_before_both(home):
    engine(home)
    own = big(home / "data" / "llm" / "models" / "gemma-4-12b-it-qat-q4_0.gguf")
    big(home / "user" / "Downloads" / "gemma-4-E4B_q4_0-it.gguf")
    assert llm.bundled_files()[1] == own
    elsewhere = big(home / "user" / "Films" / "models" / "gemma-4-E4B_q4_0-it.gguf")
    s = store.load_settings(); s.setdefault("ai_engine", {})["model_path"] = str(elsewhere); store.save_settings(s)
    assert llm.bundled_files()[1] == elsewhere


def test_the_engine_is_sized_to_the_machine(monkeypatch):
    monkeypatch.setattr(llm, "_memory_gb", lambda: 32)
    assert llm.fit_engine(16384, 99, 2)[:2] == ([2, 1], 16384)
    monkeypatch.setattr(llm, "_memory_gb", lambda: 8)    # Jon's MacBook Pro
    tries, ctx, _ = llm.fit_engine(16384, 99, 2)
    assert tries == [1] and ctx == 8192
    monkeypatch.setattr(llm.sys, "platform", "darwin"); monkeypatch.setattr(llm.platform, "machine", lambda: "x86_64")
    assert llm.fit_engine(16384, 99, 2)[2] == 0          # Intel Mac: on the processor


@pytest.fixture()
def client(home):
    from fastapi.testclient import TestClient
    from studio.server import app
    return TestClient(app)


def test_locate_a_model_anywhere(client, home, monkeypatch):
    m = big(home / "user" / "Films" / "gemma-4-E4B_q4_0-it.gguf")
    r = client.post("/api/ai/locate", json={"path": str(m)}).json()
    assert r["name"] == "gemma-4-E4B_q4_0-it" and r["engine_installed"] is False and r["vision"] is False
    assert store.load_settings()["ai_engine"]["model_path"] == str(m)
    d = client.get("/api/ai/download").json()
    assert d["located"]["chosen"] and d["engine_installed"] is False and d["engine_bytes"] > 0 and "engine" not in d["options"]
    # the dialog: chosen, then cancelled
    from studio import picker
    monkeypatch.setattr(picker, "choose_file", lambda *a, **k: str(m))
    assert client.post("/api/ai/locate", json={}).json()["path"] == str(m)
    monkeypatch.setattr(picker, "choose_file", lambda *a, **k: None)
    assert client.post("/api/ai/locate", json={}).json() == {"cancelled": True}
    assert client.post("/api/ai/locate", json={"clear": True}).json()["cleared"]
    assert "model_path" not in store.load_settings()["ai_engine"]


@pytest.mark.parametrize("name,size,says", [("notes.txt", llm.MIN_MODEL_BYTES + 1, "ends in .gguf"),
                                            ("gemma-4-E4B-it-mmproj.gguf", llm.MIN_MODEL_BYTES + 1, "vision add-on"),
                                            ("gemma-4-E4B_q4_0-it.gguf", 1000, "too small")])
def test_a_wrong_file_says_why(client, home, name, size, says):
    f = big(home / "user" / name, size)
    r = client.post("/api/ai/locate", json={"path": str(f)})
    assert r.status_code == 400 and says in r.json()["detail"]
    assert client.post("/api/ai/locate", json={"path": str(home / "nope.gguf")}).status_code == 400


def test_the_engine_can_be_fetched_on_its_own():
    assert fetch.PLANS["engine"] == ("engine",) and fetch.NAMES["engine"]


def test_a_queue_from_the_last_session_waits_until_a_job_or_the_delay(monkeypatch):
    jobs.stop_worker(); jobs._stop.clear()
    claimed = []
    monkeypatch.setattr(store, "requeue_interrupted", lambda: 0)
    monkeypatch.setattr(store, "claim_job", lambda: claimed.append(time.time()) or None)
    t0 = time.time()
    jobs.ensure_worker(delay=30)
    time.sleep(0.5)
    assert not claimed                                 # waiting for the window, not loading the engine
    jobs.ensure_worker()                               # someone queues a job: the worker starts at once
    time.sleep(0.5)
    assert claimed and claimed[0] - t0 < 5
    jobs.stop_worker(5)


def test_gemma_is_found_in_a_subfolder_of_downloads_or_on_the_desktop(home):
    """9 Nov: "it's not finding the gemma model" - files unzipped into a folder, or left on the Desktop."""
    a = big(home / "user" / "Downloads" / "gemma-4" / "models" / "gemma-4-E4B_q4_0-it.gguf")
    b = big(home / "user" / "Desktop" / "llm-off" / "models" / "gemma-4-12b-it-qat-q4_0.gguf")
    big(home / "user" / "Downloads" / "a" / "b" / "c" / "gemma-too-deep.gguf")
    assert set(llm.located_models()) == {a, b}
