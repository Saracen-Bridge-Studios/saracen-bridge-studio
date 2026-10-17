"""The Studio's own Gemma download: resumes after a dropped connection, checks every file, unpacks the engine.
(Tim, 13 Oct: on Jon's PC the installer's download of the 6.1 GB model timed out and could only restart from zero.)"""
import hashlib
import http.server
import io
import json
import threading
import time
import zipfile

import pytest


def _zip(files: dict[str, bytes]) -> bytes:
    b = io.BytesIO()
    with zipfile.ZipFile(b, "w") as z:
        for n, d in files.items():
            z.writestr(n, d)
    return b.getvalue()


class _Server:
    """Serves files with Range support; can cut the first N responses short, or serve a damaged body."""

    def __init__(self, files: dict[str, bytes]):
        self.files, self.ranges, self.cut, self.damage = files, [], {}, {}
        outer = self

        class H(http.server.BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_GET(self):
                name = self.path.lstrip("/")
                data = outer.files.get(name)
                if data is None:
                    self.send_response(404); self.end_headers(); return
                if outer.damage.get(name, 0) > 0:
                    outer.damage[name] -= 1
                    data = bytes(len(data))
                rng = self.headers.get("Range", "")
                outer.ranges.append((name, rng))
                start = int(rng.split("=")[1].split("-")[0]) if rng.startswith("bytes=") else 0
                body = data[start:]
                self.send_response(206 if start else 200)
                self.send_header("Content-Length", str(len(body)))
                if start:
                    self.send_header("Content-Range", f"bytes {start}-{len(data) - 1}/{len(data)}")
                self.end_headers()
                cut = outer.cut.get(name, 0)
                if cut > 0:
                    outer.cut[name] -= 1
                    self.wfile.write(body[: len(body) // 2]); self.wfile.flush()
                    self.connection.shutdown(2)             # the connection drops half way
                    return
                self.wfile.write(body)

        self.httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
        self.url = f"http://127.0.0.1:{self.httpd.server_address[1]}"
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()


@pytest.fixture()
def env(tmp_path, monkeypatch):
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path / "home"))
    monkeypatch.setenv("STUDIO_LLM_DIR", str(tmp_path / "llm"))
    from studio import fetch
    model = bytes(range(256)) * 4096                     # 1 MB
    vision = b"V" * 300_000
    engine = _zip({"llama-server.exe": b"exe", "llama-server": b"exe", "ggml.dll": b"dll"})   # both names: tests run on Linux too
    srv = _Server({"engine.zip": engine, "model.gguf": model, "vision.gguf": vision})
    sha = lambda b: hashlib.sha256(b).hexdigest()
    items = {
        "engine": {"label": "AI engine", "name": "llama-win.zip", "dir": "", "unzip": True, "size": len(engine),
                   "url": srv.url + "/engine.zip", "sha256": sha(engine), "done_when": "llama-server.exe"},
        "e4b": {"label": "Gemma 4 E4B", "name": "gemma-4-E4B_q4_0-it.gguf", "dir": "models", "size": len(model),
                "url": srv.url + "/model.gguf", "sha256": sha(model)},
        "e4b-vision": {"label": "vision", "name": "gemma-4-E4B-it-mmproj.gguf", "dir": "models", "size": len(vision),
                       "url": srv.url + "/vision.gguf", "sha256": sha(vision)},
    }
    monkeypatch.setattr(fetch, "ITEMS", items)
    monkeypatch.setattr(fetch, "PLANS", {"e4b": ("engine", "e4b", "e4b-vision")})
    monkeypatch.setattr(fetch, "CHUNK", 64 * 1024)
    monkeypatch.setattr(fetch, "_wait", lambda fails, why: fails + 1)      # no back-off pauses in tests
    monkeypatch.setattr(fetch, "_TARGET", {})
    fetch._STATE.clear(); fetch._STATE["state"] = "idle"
    return fetch, srv, tmp_path / "llm", model


def _finish(fetch):
    t0 = time.time()
    while fetch._THREAD is not None and fetch._THREAD.is_alive() and time.time() - t0 < 20:
        time.sleep(.05)
    return fetch.status()


def test_dropped_connection_resumes_from_the_last_byte(env):
    fetch, srv, llm, model = env
    srv.cut["model.gguf"] = 2                       # the model's connection drops twice
    fetch.start("e4b")
    st = _finish(fetch)
    assert st["state"] == "done", st
    assert (llm / "llama-server.exe").exists() and not (llm / "llama-win.zip").exists()      # engine unpacked
    assert (llm / "models" / "gemma-4-E4B_q4_0-it.gguf").read_bytes() == model
    assert not list((llm / "models").glob("*.part"))
    asked = [r for n, r in srv.ranges if n == "model.gguf"]
    assert asked[0] == "bytes=0-" and asked[1] != "bytes=0-" and len(asked) == 3            # carried on, not restarted
    assert json.loads((llm / "wanted.json").read_text())["model"] == "e4b"
    assert fetch.missing("e4b") == []


def test_a_damaged_file_is_fetched_again_and_never_used(env):
    fetch, srv, llm, model = env
    srv.damage["model.gguf"] = 1
    fetch.start("e4b")
    assert _finish(fetch)["state"] == "done"
    assert (llm / "models" / "gemma-4-E4B_q4_0-it.gguf").read_bytes() == model
    srv.damage["vision.gguf"] = 5
    (llm / "models" / "gemma-4-E4B-it-mmproj.gguf").unlink()
    fetch.start("e4b")
    st = _finish(fetch)
    assert st["state"] == "error" and "damaged" in st["error"]
    assert not (llm / "models" / "gemma-4-E4B-it-mmproj.gguf").exists()                    # a bad file is never kept


def test_partial_file_from_a_closed_studio_carries_on_and_installer_wish_starts_it(env):
    fetch, srv, llm, model = env
    (llm / "models").mkdir(parents=True)
    (llm / "models" / "gemma-4-E4B_q4_0-it.gguf.part").write_bytes(model[:300_000])
    (llm / "wanted.json").write_text(json.dumps({"model": "e4b"}))                          # written by the installer
    assert fetch.status()["state"] == "waiting"
    fetch.resume_if_wanted()
    assert _finish(fetch)["state"] == "done"
    assert ("model.gguf", "bytes=300000-") in srv.ranges
    from studio import llm as llm_mod
    assert llm_mod.bundled_files() is not None                                               # the engine finds it


def test_download_api(env, monkeypatch):
    fetch, srv, llm, model = env
    from fastapi.testclient import TestClient
    from studio.server import app
    c = TestClient(app)
    assert c.post("/api/ai/download", json={"model": "nope"}).status_code == 400
    st = c.get("/api/ai/download").json()
    assert st["options"]["e4b"]["installed"] is False and st["options"]["e4b"]["to_download"] > 0
    c.post("/api/ai/download", json={"model": "e4b"})
    _finish(fetch)
    st = c.get("/api/ai/download").json()
    assert st["state"] == "done" and st["options"]["e4b"]["installed"] is True
