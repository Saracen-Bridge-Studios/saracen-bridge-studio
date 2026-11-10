"""The web version (1.3.0; Tim and Jon, 9 Nov 2026): team sign-in, the company's cloud AI brain, Import data, and the
desktop-only parts switched off. The desktop app is unchanged without STUDIO_WEB=1."""
import io
import json
import zipfile

import pytest

from studio import llm, store, web


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path / "home"))
    monkeypatch.setattr(web, "ENABLED", True)
    monkeypatch.setattr(web, "SCRYPT", {"n": 2 ** 10, "r": 8, "p": 1, "dklen": 32})   # quick in tests; real figures checked below
    web._sessions.clear(); web._fails.clear()
    from fastapi.testclient import TestClient
    from studio.server import app
    return TestClient(app)


def signin(c, email="jon@saracenbridge.com", pw="correct horse battery"):
    r = c.post("/api/web/login", json={"email": email, "password": pw})
    assert r.status_code == 200, r.text
    return r


def test_the_real_password_hash_uses_owasps_scrypt_figures():
    assert web.SCRYPT == {"n": 2 ** 17, "r": 8, "p": 1, "dklen": 32} and web.SCRYPT_MAXMEM >= 128 * 2 ** 17 * 8


def test_everything_is_behind_sign_in(client):
    assert client.get("/api/health").status_code == 200                        # open: the setup checks it
    assert client.get("/login").status_code == 200 and b"Sign in" in client.get("/login").content
    assert client.get("/ui/studio.css").status_code == 200                     # the sign-in page's own look
    r = client.get("/api/runs")
    assert r.status_code == 401 and r.json()["signin"]
    page = client.get("/", follow_redirects=False)
    assert page.status_code == 303 and page.headers["location"] == "/login"


def test_sign_in_sessions_and_sign_out(client):
    web.add_user("Jon@SaracenBridge.com", "Jon Chadwick", "admin", "correct horse battery")
    stored = json.loads((store.home() / web.USERS_FILE).read_text())
    assert "correct horse" not in json.dumps(stored)                            # never in clear
    assert client.post("/api/web/login", json={"email": "jon@saracenbridge.com", "password": "nope nope nope"}).status_code == 401
    r = signin(client)
    ck = r.headers["set-cookie"].lower()
    assert "httponly" in ck and "samesite=strict" in ck
    assert client.get("/api/runs").status_code == 200
    me = client.get("/api/web/me").json()
    assert me["web"] and me["user"]["name"] == "Jon Chadwick" and me["user"]["role"] == "admin"
    first = client.cookies.get(web.COOKIE)
    signin(client)
    assert client.cookies.get(web.COOKIE) != first and web.session(first) is not None   # a new id at each sign-in
    client.post("/api/web/logout", json={})
    assert client.get("/api/runs").status_code == 401


def test_too_many_wrong_passwords_wait(client):
    web.add_user("colin@example.com", "Colin", "member", "a long password")
    for _ in range(web.MAX_FAILS_EMAIL):
        assert client.post("/api/web/login", json={"email": "colin@example.com", "password": "wrong guess!"}).status_code == 401
    r = client.post("/api/web/login", json={"email": "colin@example.com", "password": "a long password"})
    assert r.status_code == 429 and "Try again" in r.json()["detail"] and int(r.headers["retry-after"]) > 0


def test_cross_site_changes_are_refused(client):
    web.add_user("jon@saracenbridge.com", "Jon", "admin", "correct horse battery")
    signin(client)
    r = client.post("/api/web/users", json={"email": "x@evil.com", "name": "x"}, headers={"sec-fetch-site": "cross-site"})
    assert r.status_code == 403
    r = client.post("/api/web/users", json={"email": "x@evil.com", "name": "x"}, headers={"origin": "https://evil.example", "host": "studio.example"})
    assert r.status_code == 403
    assert client.post("/api/web/users", json={"email": "amy@example.com", "name": "Amy"}, headers={"sec-fetch-site": "same-origin"}).status_code == 200


def test_admins_run_the_team_and_members_cant(client):
    web.add_user("jon@saracenbridge.com", "Jon", "admin", "correct horse battery")
    signin(client)
    pw = client.post("/api/web/users", json={"email": "amy@example.com", "name": "Amy", "role": "member"}).json()["password"]
    assert len(pw) >= 10
    assert [u["email"] for u in client.get("/api/web/users").json()["users"]] == ["amy@example.com", "jon@saracenbridge.com"]
    assert client.delete("/api/web/users/jon@saracenbridge.com").status_code == 400            # not yourself
    from fastapi.testclient import TestClient
    from studio.server import app
    amy = TestClient(app)
    signin(amy, "amy@example.com", pw)
    assert amy.get("/api/web/users").status_code == 403
    new = client.post("/api/web/users/amy@example.com/reset", json={}).json()["password"]
    assert amy.get("/api/runs").status_code == 401                                              # a reset ends her sessions
    signin(amy, "amy@example.com", new)
    assert amy.post("/api/web/password", json={"current": new, "new": "short"}).status_code == 400
    assert amy.post("/api/web/password", json={"current": new, "new": "a much longer one"}).json()["ok"]
    assert client.delete("/api/web/users/amy@example.com").json()["ok"]


def test_desktop_only_parts_are_off(client):
    web.add_user("jon@saracenbridge.com", "Jon", "admin", "correct horse battery")
    signin(client)
    for method, path in [("post", "/api/ai/locate"), ("post", "/api/open-url"), ("post", "/api/external/aiden/launch"),
                         ("get", "/api/room/view"), ("post", "/api/ai/download"), ("get", "/api/cloud")]:
        r = getattr(client, method)(path, **({"json": {}} if method == "post" else {}))
        assert r.status_code == 403 and "desktop" in r.json()["detail"], path


def test_the_ai_brain_is_the_company_key_on_the_server(client, monkeypatch):
    web.add_user("jon@saracenbridge.com", "Jon", "admin", "correct horse battery")
    signin(client)
    st = client.get("/api/ai/status").json()
    assert st["connected"] is False and "STUDIO_AI_KEY" in st["reason"]
    monkeypatch.setenv("STUDIO_AI_PROVIDER", "anthropic")
    monkeypatch.setenv("STUDIO_AI_KEY", "sk-ant-company")
    monkeypatch.setenv("STUDIO_AI_MODEL", "claude-sonnet-5-5")
    st = client.get("/api/ai/status").json()
    assert st["connected"] and st["cloud"]["name"] == "Claude" and "sk-ant" not in json.dumps(st)
    me = client.get("/api/web/me").json()
    assert me["ai"]["ready"] and me["ai"]["model"] == "claude-sonnet-5-5" and "sk-ant" not in json.dumps(me)
    for use in ("chat", "writing"):
        e = llm.cloud_engine({}, use)
        assert e.provider == "anthropic" and e.api_key == "sk-ant-company" and e.model == "claude-sonnet-5-5"


def _zip(entries: dict) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for name, data in entries.items():
            z.writestr(name, data)
    return buf.getvalue()


def test_import_a_desktop_library(client):
    web.add_user("jon@saracenbridge.com", "Jon", "admin", "correct horse battery")
    signin(client)
    run = {"tool": "coverage", "id": "20261105-085731_The-Night-Ferry", "title": "The Night Ferry", "created": "2026-11-05 08:57",
           "files": ["night_ferry.fountain"], "sha256": "abc", "outputs": {}}
    data = _zip({"SaracenStudio/runs/coverage/20261105-085731_The-Night-Ferry/run.json": json.dumps(run),
                 "SaracenStudio/runs/coverage/20261105-085731_The-Night-Ferry/night_ferry.fountain": "INT. FERRY - NIGHT",
                 "SaracenStudio/settings.json": "{}", "SaracenStudio/cloud_keys.json": "{}",
                 "SaracenStudio/runs/../../escape.txt": "x", "/etc/evil": "x"})
    r = client.post("/api/web/import", files={"file": ("SaracenStudio.zip", data, "application/zip")}).json()
    assert r == {"imported": 1, "already_here": 0, "refused": 2}
    assert not (store.home().parent / "escape.txt").exists() and not (store.home() / "settings.json").exists()
    lib = client.get("/api/runs").json()
    assert lib["total"] == 1 and lib["runs"][0]["title"] == "The Night Ferry"
    again = client.post("/api/web/import", files={"file": ("SaracenStudio.zip", data, "application/zip")}).json()
    assert again["imported"] == 0 and again["already_here"] == 1
    bad = client.post("/api/web/import", files={"file": ("x.zip", b"not a zip", "application/zip")})
    assert bad.status_code == 400 and "zip" in bad.json()["detail"]


def test_the_desktop_app_is_unchanged(tmp_path, monkeypatch):
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path / "home"))
    monkeypatch.setattr(web, "ENABLED", False)
    from fastapi.testclient import TestClient
    from studio.server import app
    c = TestClient(app)
    assert c.get("/api/runs").status_code == 200 and c.get("/api/web/me").json() == {"web": False}
    assert c.post("/api/web/login", json={"email": "a@b.c", "password": "x"}).status_code == 404


def test_the_server_command_line_adds_an_admin(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path / "home"))
    monkeypatch.setattr(web, "SCRYPT", {"n": 2 ** 10, "r": 8, "p": 1, "dklen": 32})
    assert web.main(["add-user", "jon@saracenbridge.com", "Jon Chadwick", "--admin"]) == 0
    out = capsys.readouterr().out
    assert "admin" in out and "shown once" in out
    assert web.users()["jon@saracenbridge.com"]["role"] == "admin"


def test_jons_openai_account_is_the_default_brain(client, monkeypatch):
    """Tim, 9 Nov: "the engine will be through Jon's OpenAI account"."""
    monkeypatch.delenv("STUDIO_AI_PROVIDER", raising=False); monkeypatch.delenv("STUDIO_AI_MODEL", raising=False)
    monkeypatch.setenv("STUDIO_AI_KEY", "sk-proj-jon")
    web.add_user("jon@saracenbridge.com", "Jon", "admin", "correct horse battery")
    signin(client)
    me = client.get("/api/web/me").json()["ai"]
    assert me["provider"] == "openai" and me["name"] == "ChatGPT" and me["model"] == llm.CLOUD["openai"]["model"] and me["ready"]
    e = llm.cloud_engine({}, "writing")
    assert e.provider == "openai" and e.url == "https://api.openai.com/v1" and llm._auth(e) == {"Authorization": "Bearer sk-proj-jon"}
    monkeypatch.setattr(llm, "cloud_models", lambda p, k: ["gpt-5.5", "gpt-6"])
    r = client.get("/api/web/ai-models").json()
    assert r["models"] == ["gpt-5.5", "gpt-6"] and r["in_use"] == llm.CLOUD["openai"]["model"]


def test_the_web_setup_kit_matches_its_cloud_init():
    import importlib.util
    from pathlib import Path
    here = Path(__file__).resolve().parents[1] / "packaging" / "web"
    spec = importlib.util.spec_from_file_location("mci", here / "make_cloud_init.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    assert (here / "cloud-init.yaml").read_text() == m.build(), "run packaging/web/make_cloud_init.py"
    setup = (here / "setup.sh").read_text()
    assert "STUDIO_WEB=1" in setup and "127.0.0.1:$PORT" in setup and "8799" not in setup.replace("Never port 8799", "")
    assert "STUDIO_AI_KEY=" not in (here / "cloud-init.yaml").read_text().split("write_files:")[1].split("/root/saracen-web-setup.sh")[0]
