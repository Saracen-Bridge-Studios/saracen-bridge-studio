"""AI engine selection and calls, against fake Ollama and OpenAI-compatible servers on this machine."""
import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from studio import llm

SEEN = []


class Fake(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, obj, code=200):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        if self.path == "/api/tags":
            return self._send({"models": [{"name": "qwen3:14b", "size": 9e9}, {"name": "gemma4:e4b", "size": 5e9},
                                          {"name": "gemma4:26b", "size": 17e9}]})
        if self.path == "/v1/models":
            return self._send({"data": [{"id": "other"}, {"id": "gemma-4-12b-it"}]})
        self._send({}, 404)

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        SEEN.append((self.path, body, self.headers.get("Authorization")))
        if self.path == "/api/chat":
            content = json.dumps({"logline": "x"}) if body.get("format") else "plain text"
            return self._send({"message": {"content": content}})
        if self.path == "/v1/chat/completions":
            content = json.dumps({"logline": "y"}) if body.get("response_format") else "plain text"
            return self._send({"choices": [{"message": {"content": content}}]})
        self._send({}, 404)


@pytest.fixture()
def fake():
    srv = HTTPServer(("127.0.0.1", 0), Fake)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    SEEN.clear()
    yield f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()


def cfg(**kw):
    return {"ai_engine": {"provider": "auto", "url": "", "model": "", "api_key": "", "context": 8192, "gpu_layers": 0, **kw}}


def test_auto_uses_largest_local_gemma(fake, monkeypatch):
    monkeypatch.setattr(llm, "OLLAMA_DEFAULT", fake)
    eng, _ = llm.resolve(cfg())
    assert eng.kind == "ollama" and eng.model == "gemma4:26b"


def test_auto_falls_back_to_bundled_then_none(monkeypatch, tmp_path):
    monkeypatch.setattr(llm, "OLLAMA_DEFAULT", "http://127.0.0.1:9")          # nothing listening
    monkeypatch.setenv("STUDIO_LLM_DIR", str(tmp_path))
    assert llm.resolve(cfg())[0] is None
    (tmp_path / "models").mkdir()
    (tmp_path / ("llama-server.exe" if llm.sys.platform == "win32" else "llama-server")).write_bytes(b"")
    (tmp_path / "models" / "mmproj-F16.gguf").write_bytes(b"")
    (tmp_path / "models" / "gemma-4-E2B-it-Q4_K_M.gguf").write_bytes(b"")
    eng, _ = llm.resolve(cfg())
    assert eng.kind == "bundled" and eng.model == "gemma-4-E2B-it-Q4_K_M"     # projector file is not the model


def test_explicit_ollama_reports_missing_model(fake):
    eng, why = llm.resolve(cfg(provider="ollama", url=fake, model="gemma4:31b"))
    assert eng is None and "gemma4:31b" in why


def test_openai_server_picks_gemma_and_sends_key(fake):
    eng, _ = llm.resolve(cfg(provider="openai", url=fake + "/v1", api_key="k1"))
    assert eng.kind == "openai" and eng.model == "gemma-4-12b-it"
    out = llm.chat(eng, "sys", "user", schema={"type": "object", "properties": {"logline": {"type": "string"}}})
    assert out == {"logline": "y"}
    path, body, auth = SEEN[-1]
    assert body["response_format"]["type"] == "json_schema" and auth == "Bearer k1"


def test_ollama_chat_sets_schema_and_context(fake):
    eng = llm.Engine("ollama", fake, "gemma4:26b")
    assert llm.chat(eng, "s", "u", schema={"type": "object"}, settings=cfg(context=32768)) == {"logline": "x"}
    _, body, _ = SEEN[-1]
    assert body["format"] == {"type": "object"} and body["options"]["num_ctx"] == 32768
    assert llm.chat(eng, "s", "u") == "plain text"


def test_port_8799_is_never_used():
    eng, why = llm.resolve(cfg(provider="openai", url="http://127.0.0.1:8799/v1"))
    assert eng is None and "8799" in why
    with pytest.raises(llm.EngineError, match="8799"):
        llm.chat(llm.Engine("ollama", "http://127.0.0.1:8799", "m"), "s", "u")


def test_none_means_none():
    eng, why = llm.resolve(cfg(provider="none"))
    assert eng is None and "Settings" in why


def test_mode_can_name_its_own_model(fake, monkeypatch):
    monkeypatch.setattr(llm, "OLLAMA_DEFAULT", fake)
    s = cfg(modes={"quick": {"model": "gemma4:e4b", "think": False}, "deep": {"model": "", "think": True}})
    assert llm.resolve(s, "quick")[0].model == "gemma4:e4b"          # quick: a smaller, faster Gemma
    assert llm.resolve(s, "deep")[0].model == "gemma4:26b"           # deep: blank = the largest Gemma found
    assert llm.mode_settings(s, None)["mode"] == "quick" and llm.mode_settings(s, "deep")["think"] is True
    bad = cfg(modes={"deep": {"model": "qwen3.8:27b", "think": True}})
    eng, why = llm.resolve(bad, "deep")
    assert eng is None and "qwen3.8:27b" in why


def test_installed_engine_next_to_the_program_is_found(monkeypatch, tmp_path):
    """Setup.exe's "Install Gemma" puts the engine in <install folder>\\llm, beside the program, not inside it."""
    install = tmp_path / "Saracen Bridge Studio"
    (install / "llm" / "models").mkdir(parents=True)
    (install / "llm" / llm.SERVER_EXE).write_bytes(b"")
    (install / "llm" / "models" / "gemma-4-E4B_q4_0-it.gguf").write_bytes(b"x" * 10)
    (install / "llm" / "models" / "gemma-4-12b-it-qat-q4_0.gguf").write_bytes(b"x" * 20)
    (install / "llm" / "models" / "mmproj-gemma-4-12b-it-qat-q4_0.gguf").write_bytes(b"x" * 99)
    monkeypatch.delenv("STUDIO_LLM_DIR", raising=False)
    monkeypatch.setattr(llm.sys, "frozen", True, raising=False)
    monkeypatch.setattr(llm.sys, "executable", str(install / "SaracenBridgeStudio.exe"))
    exe, model = llm.bundled_files()
    assert exe.parent == install / "llm" and model.name == "gemma-4-12b-it-qat-q4_0.gguf"   # largest real model
    monkeypatch.setattr(llm, "OLLAMA_DEFAULT", "http://127.0.0.1:9")
    assert llm.resolve(cfg())[0].model == "gemma-4-12b-it-qat-q4_0"


def test_engine_test_endpoint(monkeypatch, tmp_path):
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path / "home"))
    from fastapi.testclient import TestClient
    from studio.server import app
    monkeypatch.setattr(llm, "resolve", lambda s, mode=None: (llm.Engine("bundled", "", "gemma-x"), ""))
    monkeypatch.setattr(llm, "chat", lambda *a, **k: "Engine ready.")
    r = TestClient(app).post("/api/ai/test", json={}).json()
    assert r["ok"] and r["reply"] == "Engine ready." and "gemma-x" in r["engine"]


def test_schema_requests_say_json_and_retry_once(monkeypatch):
    sent, replies = [], ["", '{"reply": "ready"}']
    def fake_http(url, body=None, timeout=5, api_key=""):
        sent.append(body)
        return {"choices": [{"message": {"content": replies[len(sent) - 1]}, "finish_reason": "stop"}]}
    monkeypatch.setattr(llm, "_http", fake_http)
    eng = llm.Engine("openai", "http://127.0.0.1:1/v1", "gemma")
    schema = {"type": "object", "properties": {"reply": {"type": "string"}}, "required": ["reply"]}
    assert llm.chat(eng, "sys", "Say it is ready.", schema=schema) == {"reply": "ready"}
    assert len(sent) == 2                                                  # first reply empty -> one retry
    first_user = sent[0]["messages"][1]["content"]
    assert "JSON object only" in first_user and '"reply"' in first_user   # the request itself asks for JSON
    assert "previous reply" in sent[1]["messages"][1]["content"] and sent[1]["temperature"] == 0.0
    replies[:] = ["not json", "still not json"]
    sent.clear()
    with pytest.raises(llm.OutputError):
        llm.chat(eng, "sys", "x", schema=schema)
    assert len(sent) == 2                                                  # gives up after one retry


def test_plain_text_is_not_rewritten(monkeypatch):
    sent = []
    monkeypatch.setattr(llm, "_http", lambda url, body=None, **k: sent.append(body) or
                        {"choices": [{"message": {"content": "Ready."}, "finish_reason": "stop"}]})
    assert llm.chat(llm.Engine("openai", "http://127.0.0.1:1/v1", "g"), "s", "Say ready.") == "Ready."
    assert sent[0]["messages"][1]["content"] == "Say ready."


def test_engine_that_dies_mid_job_says_so(monkeypatch):
    import subprocess, sys
    dead = subprocess.Popen([sys.executable, "-c", "raise SystemExit(9)"])
    dead.wait()
    monkeypatch.setattr(llm.BUNDLED, "proc", dead)
    monkeypatch.setattr(llm.BUNDLED, "ensure", lambda *a, **k: "http://127.0.0.1:1")
    def gone(url, body=None, **k):
        raise llm.EngineError(f"{url} not reachable (RemoteDisconnected)")
    monkeypatch.setattr(llm, "_http", gone)
    with pytest.raises(llm.EngineError) as e:
        llm.chat(llm.Engine("bundled", "", "gemma"), "s", "Say ready.")
    assert "stopped part-way" in str(e.value) and "exit code 9" in str(e.value) and "Retry" in str(e.value)
    monkeypatch.setattr(llm.BUNDLED, "proc", None)                       # a server that is merely unreachable
    with pytest.raises(llm.EngineError, match="not reachable"):
        llm.chat(llm.Engine("bundled", "", "gemma"), "s", "Say ready.")


FAKE_SERVER = '''#!/usr/bin/env python3
import json, os, socketserver, sys
from http.server import BaseHTTPRequestHandler, HTTPServer
open(os.environ["FAKE_ARGS"], "a").write(json.dumps(sys.argv[1:]) + "\\n")
if os.environ.get("FAKE_NO_ROOM") and "-np" in sys.argv and sys.argv[sys.argv.index("-np") + 1] != "1":
    sys.exit(1)                                   # not enough memory for two slots
port = int(sys.argv[sys.argv.index("--port") + 1])
class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers(); self.wfile.write(b"{}")
    def log_message(self, *a):
        pass
class S(HTTPServer):
    def server_bind(self):                      # skip getfqdn(): it can stall for many seconds on a Mac (5 Nov, first Mac run)
        socketserver.TCPServer.server_bind(self); self.server_name, self.server_port = "127.0.0.1", port
S(("127.0.0.1", port), H).serve_forever()
'''


@pytest.mark.skipif(sys.platform == "win32", reason="the fake engine is a POSIX script")
def test_built_in_engine_gives_a_job_and_the_chat_a_slot_each(monkeypatch, tmp_path):
    """Tim's PC, 13 Oct: four slots shared one 16k context; a Deep coverage step and Ask Jon filled it together."""
    (tmp_path / "models").mkdir()
    (tmp_path / "models" / "gemma-4-12b-it-qat-q4_0.gguf").write_bytes(b"x" * 100)
    exe = tmp_path / llm.SERVER_EXE
    exe.write_text(FAKE_SERVER)
    exe.chmod(0o755)
    monkeypatch.setenv("STUDIO_LLM_DIR", str(tmp_path))
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path / "home"))
    monkeypatch.setenv("FAKE_ARGS", str(tmp_path / "args.jsonl"))
    monkeypatch.setattr(llm, "_memory_gb", lambda: 32)   # a 32 GB machine: two slots (smaller ones: tests/test_locate_model.py)
    b = llm._Bundled()
    try:
        b.ensure(16384, 99, load_timeout=30)
        args = json.loads((tmp_path / "args.jsonl").read_text().splitlines()[-1])
        assert args[args.index("-np") + 1] == "2" and "--no-kv-unified" in args and args[args.index("-c") + 1] == "32768"
        assert b.slots == 2
        b.stop()
        monkeypatch.setenv("FAKE_NO_ROOM", "1")                # a machine that can't hold the second slot
        b.ensure(16384, 99, load_timeout=30)
        args = json.loads((tmp_path / "args.jsonl").read_text().splitlines()[-1])
        assert args[args.index("-np") + 1] == "1" and args[args.index("-c") + 1] == "16384" and "--no-kv-unified" not in args
        assert b.slots == 1
    finally:
        b.stop()


def test_deep_thinking_stops_at_its_budget(monkeypatch):
    """Tim's PC, 13 Oct: Deep coverage thought for 7,200 tokens and returned nothing."""
    sent = []
    monkeypatch.setattr(llm, "_http", lambda url, body=None, **k: sent.append(body) or
                        {"choices": [{"message": {"content": "Ready."}, "finish_reason": "stop"}]})
    monkeypatch.setattr(llm.BUNDLED, "ensure", lambda *a, **k: "http://127.0.0.1:1")
    llm.chat(llm.Engine("bundled", "", "g"), "s", "x", max_tokens=7200, think=True, think_budget=6000)
    assert sent[-1]["reasoning_budget_tokens"] == 6000 and "Write the answer now" in sent[-1]["reasoning_budget_message"]
    llm.chat(llm.Engine("bundled", "", "g"), "s", "x", max_tokens=1000, think=True)
    assert sent[-1]["reasoning_budget_tokens"] == 600                       # default: 60% of the reply's room
    llm.chat(llm.Engine("bundled", "", "g"), "s", "x", think=False)
    assert "reasoning_budget_tokens" not in sent[-1]
    llm.chat(llm.Engine("openai", "http://127.0.0.1:1/v1", "g"), "s", "x", think=True)
    assert "reasoning_budget_tokens" not in sent[-1]                        # someone else's server: not our field to send
