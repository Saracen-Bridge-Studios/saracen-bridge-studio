"""The Mac build (1.2): the parts that differ from Windows, run here by standing in for the Mac where needed.
The Mac build machine runs the whole suite natively as well (.github/workflows/build.yml)."""
import io
import os
import stat
import subprocess
import sys
import tarfile
import time
import types
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import studio_launcher as L
from studio import fetch, keys, llm, store


def test_mac_data_folder_is_application_support(monkeypatch):
    assert store.default_home("darwin") == str(Path.home() / "Library" / "Application Support" / "SaracenStudio")
    assert store.default_home("linux").endswith(".saracen-studio")


class FakeKeychain(types.ModuleType):
    def __init__(self):
        super().__init__("keyring")
        self.items = {}

    def get_password(self, service, account):
        return self.items.get((service, account))

    def set_password(self, service, account, value):
        self.items[(service, account)] = value


@pytest.mark.skipif(sys.platform == "win32", reason="Windows seals with DPAPI")
def test_keys_are_sealed_with_a_key_kept_in_the_mac_keychain(tmp_path, monkeypatch):
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path))
    kc = FakeKeychain()
    monkeypatch.setitem(sys.modules, "keyring", kc)
    monkeypatch.setattr(sys, "platform", "darwin")
    keys.put("anthropic", "sk-ant-secret-0123456789")
    raw = (tmp_path / keys.FILE).read_text()
    assert '"kc:' in raw and "sk-ant-secret" not in raw                       # encrypted on disk
    assert keys.get("anthropic") == "sk-ant-secret-0123456789"
    assert len(kc.items) == 1                                                  # one sealing key, made on first use
    kc.items.clear()                                                           # another Mac user, or the key deleted
    assert keys.get("anthropic") == ""


@pytest.mark.skipif(sys.platform == "win32", reason="Windows seals with DPAPI")
def test_without_a_keychain_keys_fall_back_to_an_owner_only_file(tmp_path, monkeypatch):
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path))

    class Locked(FakeKeychain):
        def get_password(self, *a):
            raise RuntimeError("keychain locked")

    monkeypatch.setitem(sys.modules, "keyring", Locked())
    monkeypatch.setattr(sys, "platform", "darwin")
    keys.put("openai", "sk-plain-0123456789")
    assert '"plain:' in (tmp_path / keys.FILE).read_text() and keys.get("openai") == "sk-plain-0123456789"
    assert stat.S_IMODE(os.stat(tmp_path / keys.FILE).st_mode) == 0o600


def test_mac_engine_download_is_the_metal_build():
    e = fetch.ENGINES["darwin"]
    assert e["url"].endswith("-bin-macos-arm64.tar.gz") and e["done_when"] == "llama-server" and len(e["sha256"]) == 64
    assert fetch.ENGINES["win32"]["done_when"] == "llama-server.exe"


def test_mac_engine_unpacks_with_links_and_executable_bits(tmp_path):
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as t:
        def add(name, data=b"", mode=0o755, link=None):
            ti = tarfile.TarInfo(name)
            if link:
                ti.type, ti.linkname = tarfile.SYMTYPE, link
            else:
                ti.size, ti.mode = len(data), mode
            t.addfile(ti, io.BytesIO(data) if not link else None)
        d = tarfile.TarInfo("llama-b1/"); d.type = tarfile.DIRTYPE; d.mode = 0o755; t.addfile(d)
        add("llama-b1/llama-server", b"#!/bin/sh\necho ok\n")
        add("llama-b1/libllama.0.6.0.dylib", b"lib")
        add("llama-b1/libllama.0.dylib", link="libllama.0.6.0.dylib")
        add("llama-b1/LICENSE", b"MIT", mode=0o644)
    archive = tmp_path / "llama-mac.tar.gz.part"
    archive.write_bytes(buf.getvalue())
    out = tmp_path / "llm"
    out.mkdir()
    fetch.unpack(archive, out, "llama-b1/")
    assert (out / "llama-server").is_file() and os.access(out / "llama-server", os.X_OK)
    assert (out / "libllama.0.dylib").is_symlink() and (out / "libllama.0.dylib").read_bytes() == b"lib"
    assert not (out / "llama-b1").exists()


def test_mac_app_never_downloads_into_its_own_bundle(monkeypatch, tmp_path):
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path / "home"))
    monkeypatch.delenv("STUDIO_LLM_DIR", raising=False)
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", str(tmp_path / "Saracen.app" / "Contents" / "MacOS" / "SaracenBridgeStudio"))
    monkeypatch.setattr(sys, "platform", "darwin")
    assert fetch.candidate_dirs() == [tmp_path / "home" / "llm"]


@pytest.mark.skipif(sys.platform == "win32", reason="Windows ties the engine to the Studio with a job object")
def test_an_engine_left_by_a_crashed_studio_is_stopped_on_the_next_start(tmp_path, monkeypatch):
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path))
    fake = tmp_path / "llama-server"
    fake.write_text("#!/bin/sh\nsleep 60\n")
    fake.chmod(0o755)
    proc = subprocess.Popen([str(fake)])
    try:
        (tmp_path / llm.PIDFILE).write_text(str(proc.pid))
        llm._reap_stale()
        assert proc.wait(10) is not None and not (tmp_path / llm.PIDFILE).exists()
    finally:
        if proc.poll() is None:
            proc.kill()


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX process check")
def test_a_reused_process_id_is_never_killed(tmp_path, monkeypatch):
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path))
    other = subprocess.Popen(["sleep", "30"])                     # not an engine: same id, other program
    try:
        (tmp_path / llm.PIDFILE).write_text(str(other.pid))
        llm._reap_stale()
        time.sleep(0.3)
        assert other.poll() is None
    finally:
        other.kill()


def test_mac_window_is_found_inside_the_app(monkeypatch, tmp_path):
    macos = tmp_path / "Saracen Bridge Studio.app" / "Contents" / "MacOS"
    shell = macos.parent / "Helpers" / L.MAC_WINDOW_APP / "Contents" / "MacOS" / "studio-window"
    shell.parent.mkdir(parents=True)
    shell.write_text("")
    monkeypatch.delenv("STUDIO_SHELL", raising=False)
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", str(macos / "SaracenBridgeStudio"))
    monkeypatch.setattr(sys, "platform", "darwin")
    monkeypatch.setattr(L, "SHELL_NAME", "studio-window")
    assert L.find_shell() == str(shell)


def test_mac_opens_other_apps_with_open(tmp_path, monkeypatch):
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path / "home"))
    from studio import server
    c = TestClient(server.app)
    s = c.get("/api/settings").json()
    s["external_apps"]["aiden"]["target"] = "/Applications/AIDEN.app"
    assert c.put("/api/settings", json=s).status_code == 200
    calls = []
    monkeypatch.setattr(server.subprocess, "Popen", lambda args, **kw: calls.append(args))
    monkeypatch.setattr(sys, "platform", "darwin")
    assert c.post("/api/external/aiden/launch").status_code == 200
    assert calls == [["open", "/Applications/AIDEN.app"]]


def test_mac_alert_passes_the_message_as_an_argument(monkeypatch):
    seen = []
    monkeypatch.setattr(sys, "platform", "darwin")
    monkeypatch.setattr(subprocess, "run", lambda args, **kw: seen.append(args))
    L.tell_user('Port "8798" is busy\n\nTry again')
    assert seen and seen[0][0] == "osascript" and seen[0][-1] == 'Port "8798" is busy\n\nTry again'
    assert all('8798' not in a for a in seen[0][:-1])                  # never spliced into the script


@pytest.mark.skipif(sys.platform != "darwin" or not os.environ.get("CI_KEYCHAIN"),
                    reason="the real Keychain: on the Mac build machine only (a throwaway keychain, no prompts)")
def test_the_real_mac_keychain_seals_and_opens_a_key(tmp_path, monkeypatch):
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path))
    keys.put("anthropic", "sk-ant-real-keychain-0123")
    assert '"kc:' in (tmp_path / keys.FILE).read_text() and keys.get("anthropic") == "sk-ant-real-keychain-0123"
