"""The 0.4 Studio window (Tauri) and its fallbacks, with stand-in programs for the window."""
import os
import stat
import sys

import studio_launcher as L
from studio import server as srv


def _fake(tmp_path, body):
    """A stand-in window program: a .cmd file on Windows, a Python script elsewhere."""
    if sys.platform == "win32":
        f = tmp_path / "studio-window.cmd"
        f.write_text("@echo off\r\n" + ("ping -n 2 127.0.0.1 >nul\r\n" if "sleep" in body else "exit /b 3\r\n"))
        return str(f)
    f = tmp_path / "studio-window"
    f.write_text(f"#!{sys.executable}\nimport time, sys\n{body}\n")
    f.chmod(f.stat().st_mode | stat.S_IEXEC)
    return str(f)


def test_window_that_shows_the_page_runs_until_closed(tmp_path, monkeypatch):
    monkeypatch.setenv("STUDIO_SHELL", _fake(tmp_path, "time.sleep(1.2)"))
    monkeypatch.setattr(srv, "last_heartbeat", lambda: 1.0)          # the page checked in
    assert L.shell_window_until_closed("http://127.0.0.1:8798/", connect_seconds=5) is True


def test_window_that_never_shows_the_page_falls_back(tmp_path, monkeypatch):
    monkeypatch.setenv("STUDIO_SHELL", _fake(tmp_path, "sys.exit(3)"))
    monkeypatch.setattr(srv, "last_heartbeat", lambda: None)
    assert L.shell_window_until_closed("http://127.0.0.1:8798/", connect_seconds=2) is False


def test_no_window_program_means_fallback(monkeypatch):
    monkeypatch.delenv("STUDIO_SHELL", raising=False)
    assert L.find_shell() is None or getattr(sys, "frozen", False)
    assert L.shell_window_until_closed("http://127.0.0.1:8798/", connect_seconds=1) is False


def test_open_url_only_takes_web_links(monkeypatch):
    from fastapi.testclient import TestClient
    opened = []
    monkeypatch.setattr(srv.webbrowser, "open", opened.append)
    c = TestClient(srv.app)
    assert c.post("/api/open-url", json={"url": "https://console.anthropic.com/settings/keys"}).status_code == 200
    assert c.post("/api/open-url", json={"url": "file:///C:/Windows/System32/calc.exe"}).status_code == 400
    assert c.post("/api/open-url", json={"url": "javascript:alert(1)"}).status_code == 400
    assert opened == ["https://console.anthropic.com/settings/keys"]
