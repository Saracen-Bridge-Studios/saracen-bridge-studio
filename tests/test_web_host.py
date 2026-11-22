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
