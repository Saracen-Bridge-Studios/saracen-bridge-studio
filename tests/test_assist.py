"""Ask Saracen and the optional cloud AI, against fake servers on this machine (no network, no real keys)."""
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest
from fastapi.testclient import TestClient

from studio import assist, keys, llm, store

SEEN = []


class Fake(BaseHTTPRequestHandler):
    """Speaks just enough of the OpenAI, Anthropic and Ollama streaming formats."""
    protocol_version = "HTTP/1.0"

    def log_message(self, *a):
        pass

    def _json(self, obj, code=200):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        SEEN.append(("GET", self.path, {k.lower(): v for k, v in self.headers.items()}))
        if self.path.endswith("/models"):
            return self._json({"data": [{"id": "models/model-a"}, {"id": "model-b"}]})
        self._json({}, 404)

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        SEEN.append(("POST", self.path, {k.lower(): v for k, v in self.headers.items()}, body))
        self.send_response(200)
        self.end_headers()
        if self.path.endswith("/messages"):                       # Anthropic
            if not body.get("stream"):
                return self.wfile.write(json.dumps({"content": [{"type": "text", "text": '```json\n{"ok": true}\n```'}], "stop_reason": "end_turn"}).encode())
            for ev in ({"type": "message_start"}, {"type": "ping"},
                       {"type": "content_block_delta", "delta": {"type": "text_delta", "text": "Hello "}},
                       {"type": "content_block_delta", "delta": {"type": "text_delta", "text": "Tim."}}, {"type": "message_stop"}):
                self.wfile.write(f"event: {ev['type']}\ndata: {json.dumps(ev)}\n\n".encode())
        elif self.path.endswith("/chat/completions"):              # OpenAI-compatible
            for piece in ("Open ", "[Location & Incentives](#/tool/incentives)", "."):
                self.wfile.write(f"data: {json.dumps({'choices': [{'delta': {'content': piece}}]})}\n\n".encode())
            self.wfile.write(b"data: [DONE]\n\n")
        elif self.path == "/api/chat":                              # Ollama
            for piece, done in (("Local ", False), ("answer.", True)):
                self.wfile.write((json.dumps({"message": {"content": piece}, "done": done}) + "\n").encode())


@pytest.fixture()
def fake():
    srv = HTTPServer(("127.0.0.1", 0), Fake)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    SEEN.clear()
    yield f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()


@pytest.fixture()
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path))
    return tmp_path


def test_stream_reads_openai_anthropic_and_ollama(fake):
    oa = llm.Engine("openai", fake + "/v1", "m")
    assert "".join(llm.stream(oa, "sys", [{"role": "user", "content": "hi"}])) == "Open [Location & Incentives](#/tool/incentives)."
    sent = SEEN[-1][3]
    assert sent["stream"] is True and sent["messages"][0] == {"role": "system", "content": "sys"}
    an = llm.Engine("anthropic", fake + "/v1", "claude-x", "sk-test", "anthropic")
    assert "".join(llm.stream(an, "sys", [{"role": "user", "content": "hi"}])) == "Hello Tim."
    hdr, body = SEEN[-1][2], SEEN[-1][3]
    assert hdr["x-api-key"] == "sk-test" and hdr["anthropic-version"] == llm.ANTHROPIC_VERSION and body["system"] == "sys"
    ol = llm.Engine("ollama", fake, "gemma")
    assert "".join(llm.stream(ol, "sys", [{"role": "user", "content": "hi"}])) == "Local answer."


def test_cloud_writing_parses_fenced_json_and_openai_uses_completion_tokens(fake, monkeypatch):
    an = llm.Engine("anthropic", fake + "/v1", "claude-x", "sk-test", "anthropic")
    assert llm.chat(an, "sys", "go", schema={"type": "object"}) == {"ok": True}
    oa = llm.Engine("cloud", fake + "/v1", "gpt-x", "sk-o", "openai")
    body = llm._cloud_body(oa, "sys", [{"role": "user", "content": "hi"}], 500, 0.2, False)
    assert body["max_completion_tokens"] == 500 and "temperature" not in body and "max_tokens" not in body


def test_keys_are_kept_out_of_settings_and_never_returned(home, monkeypatch, fake):
    from studio.server import app
    monkeypatch.setitem(llm.CLOUD["anthropic"], "url", fake + "/v1")
    c = TestClient(app)
    r = c.put("/api/cloud", json={"provider": "anthropic", "enabled": True})
    assert r.status_code == 409 and "key" in r.json()["detail"]              # no key: cannot switch on
    r = c.put("/api/cloud", json={"provider": "anthropic", "key": "sk-ant-secret-1234", "enabled": True})
    assert r.status_code == 200 and r.json()["enabled"] and r.json()["keys"]["anthropic"] == "…1234"
    assert "sk-ant-secret" not in (home / "settings.json").read_text() and "sk-ant-secret" not in json.dumps(c.get("/api/cloud").json())
    assert "sk-ant-secret" not in json.dumps(c.get("/api/settings").json())
    assert keys.get("anthropic") == "sk-ant-secret-1234"
    assert c.get("/api/cloud/models", params={"provider": "anthropic"}).json()["models"] == ["model-a", "model-b"]
    assert c.get("/api/ai/status").json()["cloud"]["active"] == {"chat": True, "writing": False}
    c.put("/api/cloud", json={"provider": "anthropic", "clear_key": True})
    assert keys.get("anthropic") == "" and not llm.cloud_engine(store.load_settings(), "chat")


def test_writing_uses_cloud_only_when_ticked(home, monkeypatch, fake):
    keys.put("gemini", "g-key-000000")
    s = store.load_settings()
    s["cloud_ai"] = {"enabled": True, "provider": "gemini", "model": "", "use_for": {"chat": True, "writing": False}}
    assert llm.cloud_engine(s, "writing") is None and llm.cloud_engine(s, "chat").provider == "gemini"
    s["cloud_ai"]["use_for"]["writing"] = True
    eng, _ = llm.resolve(s, "quick")
    assert eng.is_cloud and eng.model == llm.CLOUD["gemini"]["model"] and eng.kind == "cloud"
    s["cloud_ai"]["enabled"] = False
    assert not llm.cloud_engine(s, "writing")


def test_chat_endpoint_streams_with_page_context(home, monkeypatch, fake):
    from studio.server import app
    s = store.load_settings()
    s["ai_engine"].update(provider="openai", url=fake + "/v1", model="gemma")
    store.save_settings(s)
    c = TestClient(app)
    r = c.post("/api/assist/chat", json={"messages": [{"role": "assistant", "content": "Hi"}, {"role": "user", "content": "Where do I work out the rebate?"}],
                                          "page": {"title": "Finance Plan", "path": "#/tool/finance", "text": "SOURCES 5,800,236"}})
    assert r.status_code == 200 and r.headers["x-cloud"] == "0"
    assert r.text == "Open [Location & Incentives](#/tool/incentives)."
    sent = SEEN[-1][3]["messages"]
    assert sent[1] == {"role": "user", "content": "Where do I work out the rebate?"}          # leading assistant turn dropped
    assert "Finance Plan" in sent[0]["content"] and "SOURCES 5,800,236" in sent[0]["content"] and "#/tool/incentives" in sent[0]["content"]


def test_chat_puts_jons_documents_in_front_of_the_model(home, monkeypatch, fake):
    from urllib.parse import unquote
    from studio import knowledge
    from studio.server import app
    s = store.load_settings()
    s["ai_engine"].update(provider="openai", url=fake + "/v1", model="gemma")
    store.save_settings(s)
    monkeypatch.setattr(knowledge, "search", lambda q, tool=None, k=5, **kw: [
        {"title": "07 GMOT Golden Test", "heading": "Purpose", "text": "The golden test checks the incentive engine.", "tool": tool}])
    r = TestClient(app).post("/api/assist/chat", json={"messages": [{"role": "user", "content": "What is the golden test?"}],
                                                         "page": {"title": "Location & Incentives", "path": "#/tool/incentives", "text": ""}})
    assert json.loads(unquote(r.headers["x-sources"])) == [{"title": "07 GMOT Golden Test", "heading": "Purpose"}]
    system = SEEN[-1][3]["messages"][0]["content"]
    assert "[1] 07 GMOT Golden Test — Purpose" in system and "The golden test checks the incentive engine." in system
    assert "You are Jonny" in system


def test_history_is_trimmed_and_alternates():
    msgs = [{"role": "user", "content": "a"}, {"role": "user", "content": "b"}, {"role": "assistant", "content": ""},
            {"role": "system", "content": "ignore me"}, {"role": "assistant", "content": "c"}]
    assert assist.clean_history(msgs) == [{"role": "user", "content": "a\n\nb"}, {"role": "assistant", "content": "c"}]
    many = [{"role": "user" if i % 2 == 0 else "assistant", "content": str(i)} for i in range(40)]
    out = assist.clean_history(many)
    assert len(out) <= assist.HISTORY and out[0]["role"] == "user"


def test_a_long_conversation_is_fitted_to_the_engine():
    """Tim's PC, 13 Oct: "Context size has been exceeded". The oldest turns go first, then excerpts, then page text."""
    from studio.server import CATALOG
    long = "x" * 6000
    msgs = [{"role": "user" if i % 2 == 0 else "assistant", "content": f"{i} {long}"} for i in range(15)]
    refs = [{"title": f"Doc {i}", "heading": "", "text": "y" * 3000} for i in range(5)]
    page = {"title": "Finance Plan", "path": "#/tool/finance", "text": "z" * 6000}
    budget = 16384 - assist.CHAT_TOKENS - 512
    system, kept, kept_refs = assist.fit(CATALOG, page, True, refs, msgs, budget)
    used = assist.est_tokens(system) + sum(assist.est_tokens(m["content"]) + 8 for m in kept)
    assert used <= budget and kept[-1] == msgs[-1] and kept[0]["role"] == "user" and len(kept) < len(msgs)
    assert len(kept_refs) == 5                                    # dropping old turns was enough
    system, kept, kept_refs = assist.fit(CATALOG, page, True, refs, msgs[-1:], 3000)
    assert kept_refs == [] and "z" * 6000 not in system           # a tiny engine: excerpts and page text give way
    assert assist.fit(CATALOG, page, True, refs, msgs[-1:], 16000)[2] == refs   # nothing cut when it fits


def test_chat_tries_again_when_the_engine_has_no_room(home, monkeypatch):
    from studio import server
    from studio.server import app
    monkeypatch.setattr(llm, "resolve", lambda s, mode=None, use="writing": (llm.Engine("bundled", "", "gemma"), ""))
    calls = []
    def stream(engine, system, messages, **k):
        calls.append(messages)
        if len(calls) == 1:
            raise llm.EngineError('500 from http://127.0.0.1:1/v1/chat/completions: {"error":{"message":"Context size has been exceeded."}}')
        yield "Step one: open Finance Plan."
    monkeypatch.setattr(llm, "stream", stream)
    msgs = [{"role": "user", "content": "Hi"}, {"role": "assistant", "content": "Hello"}, {"role": "user", "content": "Walk me through Finance Plan"}]
    r = TestClient(app).post("/api/assist/chat", json={"messages": msgs, "documents": False})
    assert r.text == "Step one: open Finance Plan." and calls[1] == [msgs[-1]]   # second try: the question alone
    def full(engine, system, messages, **k):
        raise llm.EngineError("Context size has been exceeded.")
        yield ""
    monkeypatch.setattr(llm, "stream", full)
    r = TestClient(app).post("/api/assist/chat", json={"messages": msgs, "documents": False})
    assert r.text == "\u0000" + server.CONTEXT_FULL                          # plain words, not the server's message


def test_jon_knows_what_is_ai_and_what_each_tool_takes():
    """Tim, 13 Oct: Jon called the tool "Script Coverage [02]", said the breakdown was done by AI, and told him to
    upload a look book and character breakdowns to coverage, which takes only the script."""
    from studio.server import CATALOG
    sp = assist.system_prompt(CATALOG, {"title": "Development / Script Coverage", "path": "#/tool/coverage"}, True)
    assert "[02]" not in sp and "[04]" not in sp
    line = next(l for l in sp.splitlines() if l.startswith("- Script Coverage"))
    assert "no AI" in line and "Look book" not in line and "only the Studio takes" not in line
    assert "Coverage takes only the script file" in sp and "Never refer to tools by number" in sp
