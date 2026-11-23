"""Web host mode (1.3.2; Tim, 22 Nov 2026): the web version hosted from the desktop app, behind a tunnel."""
import importlib
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _launcher(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT))
    import studio_launcher
    return importlib.reload(studio_launcher)


def test_web_setup_uses_its_own_folder_and_reads_the_ai_settings(tmp_path, monkeypatch):
    for k in ("STUDIO_HOME", "STUDIO_WEB", "STUDIO_AI_KEY", "STUDIO_AI_PROVIDER", "STUDIO_AI_MODEL"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("APPDATA", str(tmp_path))
    L = _launcher(monkeypatch)
    folder = Path(L.web_setup())
    assert os.environ["STUDIO_WEB"] == "1"
    assert "web" in folder.name.lower() and folder.name not in ("SaracenStudio", ".saracen-studio")   # never the desktop Library
    f = folder / L.WEB_SETTINGS
    assert "STUDIO_AI_KEY=" in f.read_text()
    assert not os.environ.get("STUDIO_AI_KEY")                     # blank in the file means not set
    assert os.environ["STUDIO_AI_PROVIDER"] == "local"             # and no key means this computer's Gemma (1.3.3)
    f.write_text("STUDIO_AI_PROVIDER=anthropic\nSTUDIO_AI_KEY= test-not-a-real-key \nSTUDIO_AI_MODEL=\n")
    L.web_setup()
    assert os.environ["STUDIO_AI_KEY"] == "test-not-a-real-key" and os.environ["STUDIO_AI_PROVIDER"] == "anthropic"
    for k in ("STUDIO_HOME", "STUDIO_WEB", "STUDIO_AI_KEY", "STUDIO_AI_PROVIDER"):
        os.environ.pop(k, None)


def test_web_host_serves_the_sign_in_page_and_marks_the_cookie_secure_behind_https(tmp_path):
    env = {**os.environ, "STUDIO_HOME": str(tmp_path / "home"), "PYTHONPATH": str(ROOT / "engine")}
    for k in ("STUDIO_WEB", "STUDIO_AI_KEY"):
        env.pop(k, None)
    made = subprocess.run([sys.executable, "-c",
                           "import os,sys; sys.path.insert(0, r'%s'); os.environ['STUDIO_WEB']='1'\n"
                           "from studio import web; print(web.add_user('t@example.com','T','admin'))" % (ROOT / "engine")],
                          env=env, capture_output=True, text=True, timeout=120)
    pw = made.stdout.strip().splitlines()[-1]
    port = 8791
    p = subprocess.Popen([sys.executable, str(ROOT / "studio_launcher.py"), "--web", "--headless", "--port", str(port)], env=env,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        for _ in range(200):
            try:
                op.open(f"http://127.0.0.1:{port}/api/health", timeout=1)
                break
            except OSError:
                time.sleep(0.2)
        try:                                                                     # not signed in: nothing of the Library
            op.open(f"http://127.0.0.1:{port}/api/runs", timeout=5)
            raise AssertionError("the Library answered without a sign-in")
        except urllib.error.HTTPError as e:
            assert e.code in (401, 403)
        import json
        req = urllib.request.Request(f"http://127.0.0.1:{port}/api/web/login", method="POST",
                                     data=json.dumps({"email": "t@example.com", "password": pw}).encode(),
                                     headers={"Content-Type": "application/json", "Host": "studio.example.com",
                                              "Origin": "https://studio.example.com", "X-Forwarded-Proto": "https"})
        r = op.open(req, timeout=10)
        cookie = r.headers.get("set-cookie", "")
        assert "Secure" in cookie and "HttpOnly" in cookie
    finally:
        p.terminate()
        p.wait(timeout=20)


def test_the_web_host_can_use_the_host_computers_gemma(tmp_path, monkeypatch):
    """1.3.3 (Tim, 22 Nov): "have it so jon or whoever can use my gemma for now"."""
    from studio import llm, web
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path / "home"))
    monkeypatch.setenv("STUDIO_AI_PROVIDER", "local")
    monkeypatch.delenv("STUDIO_AI_KEY", raising=False)
    monkeypatch.setattr(web, "ENABLED", True)
    monkeypatch.setattr(web, "SCRYPT", {"n": 2 ** 10, "r": 8, "p": 1, "dklen": 32})
    web._sessions.clear(); web._fails.clear()
    gemma = llm.Engine("openai", "http://127.0.0.1:1/v1", "gemma-test")
    monkeypatch.setattr(llm, "_resolve", lambda settings: (gemma, ""))
    monkeypatch.setattr(llm, "can_see", lambda eng: (False, ""))
    assert web.local_ai()
    eng, why = llm.resolve({}, use="writing")
    assert eng is gemma and not why                                # no cloud engine steps in front
    from fastapi.testclient import TestClient
    from studio.server import app
    c = TestClient(app)
    web.add_user("t@example.com", "T", "admin", "correct horse battery")
    assert c.post("/api/web/login", json={"email": "t@example.com", "password": "correct horse battery"}).status_code == 200
    me = c.get("/api/web/me").json()
    assert me["web"] and me["ai"]["local"] and me["ai"]["ready"] and me["ai"]["model"] == "gemma-test"
    st = c.get("/api/ai/status").json()
    assert st["connected"] and st["web"] and st["cloud"]["enabled"] is False


def test_an_admin_picks_the_ai_and_adds_a_key_in_settings(tmp_path, monkeypatch):
    """1.3.4 (Tim, 22 Nov): the three cloud accounts and Gemma as tabs, a key added with Add, then OK to use it."""
    from studio import llm, web, keys
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path / "home"))
    monkeypatch.setenv("STUDIO_AI_PROVIDER", "local")
    monkeypatch.delenv("STUDIO_AI_KEY", raising=False)
    monkeypatch.setattr(web, "ENABLED", True)
    monkeypatch.setattr(web, "SCRYPT", {"n": 2 ** 10, "r": 8, "p": 1, "dklen": 32})
    web._sessions.clear(); web._fails.clear()
    monkeypatch.setattr(llm, "_resolve", lambda settings: (llm.Engine("openai", "http://127.0.0.1:1/v1", "gemma-test"), ""))
    monkeypatch.setattr(llm, "can_see", lambda eng: (False, ""))
    from fastapi.testclient import TestClient
    from studio.server import app
    c = TestClient(app)
    web.add_user("boss@example.com", "Boss", "admin", "correct horse battery")
    web.add_user("crew@example.com", "Crew", "member", "correct horse battery")
    assert c.post("/api/web/login", json={"email": "crew@example.com", "password": "correct horse battery"}).status_code == 200
    assert c.get("/api/web/ai").status_code == 403                       # members can't change it
    assert c.put("/api/web/ai", json={"provider": "openai", "key": "x" * 40}).status_code == 403
    c.post("/api/web/logout")
    assert c.post("/api/web/login", json={"email": "boss@example.com", "password": "correct horse battery"}).status_code == 200
    v = c.get("/api/web/ai").json()
    assert v["provider"] == "local" and [p["id"] for p in v["providers"]] == ["local", "anthropic", "openai", "gemini"]
    assert c.put("/api/web/ai", json={"provider": "openai", "use": True}).status_code == 409   # no key yet
    assert c.put("/api/web/ai", json={"provider": "openai", "key": "too short"}).status_code == 400
    key = "sk-test-" + "a" * 40
    v = c.put("/api/web/ai", json={"provider": "openai", "key": key}).json()
    ch = next(p for p in v["providers"] if p["id"] == "openai")
    assert ch["has_key"] and ch["hint"] and key not in str(v) and v["provider"] == "local"   # added, not yet in use; never echoed
    v = c.put("/api/web/ai", json={"provider": "openai", "use": True}).json()
    assert v["provider"] == "openai" and web.ai()["key"] == key and not web.local_ai()
    me = c.get("/api/web/me").json()
    assert me["ai"]["provider"] == "openai" and me["ai"]["ready"]
    c.put("/api/web/ai", json={"provider": "openai", "remove_key": True})
    assert keys.get("openai") == "" and not c.get("/api/web/me").json()["ai"]["ready"]
    v = c.put("/api/web/ai", json={"provider": "local", "use": True}).json()
    assert v["provider"] == "local" and web.local_ai()


def test_an_admin_can_choose_a_persons_password(tmp_path, monkeypatch):
    """1.3.4 (Tim, 22 Nov): the admin can type the password when adding someone or resetting theirs."""
    from studio import web
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path / "home"))
    monkeypatch.setattr(web, "ENABLED", True)
    monkeypatch.setattr(web, "SCRYPT", {"n": 2 ** 10, "r": 8, "p": 1, "dklen": 32})
    web._sessions.clear(); web._fails.clear()
    from fastapi.testclient import TestClient
    from studio.server import app
    c = TestClient(app)
    web.add_user("boss@example.com", "Boss", "admin", "correct horse battery")
    c.post("/api/web/login", json={"email": "boss@example.com", "password": "correct horse battery"})
    r = c.post("/api/web/users", json={"email": "Jon@Example.com", "name": "Jon", "role": "member", "password": "chosen-by-boss-1"}).json()
    assert r["password"] == "chosen-by-boss-1" and r["email"] == "jon@example.com" and web.check_password("jon@example.com", "chosen-by-boss-1")
    r = c.post("/api/web/users/jon@example.com/reset", json={"password": "second-choice-22"}).json()
    assert r["password"] == "second-choice-22" and web.check_password("jon@example.com", "second-choice-22")
    r = c.post("/api/web/users/jon@example.com/reset", json={}).json()          # blank: the Studio makes one
    assert len(r["password"]) >= 10 and web.check_password("jon@example.com", r["password"])
    assert c.post("/api/web/users/jon@example.com/reset", json={"password": "short"}).status_code == 400
