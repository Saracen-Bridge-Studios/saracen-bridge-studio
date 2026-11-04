"""The demo Studio kit for Apple's reviewers (packaging/demo): the paste-in server file matches its script, the review
page carries the invite, and a Studio run as a public server puts its https address in invites and meeting tokens."""
import importlib.util
import os
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "packaging" / "demo"


def _load(name):
    spec = importlib.util.spec_from_file_location(name, DEMO / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_cloud_init_is_built_from_setup_sh():
    assert (DEMO / "cloud-init.yaml").read_text() == _load("make_cloud_init").build(), "run make_cloud_init.py"
    d = yaml.safe_load((DEMO / "cloud-init.yaml").read_text())
    script = next(f for f in d["write_files"] if f["path"] == "/root/saracen-demo-setup.sh")["content"]
    assert script == (DEMO / "setup.sh").read_text()
    assert "8799" not in script.replace("Never port 8799", "")


def test_review_page_has_the_invite_the_app_link_and_a_qr_code(tmp_path):
    keeper = _load("demo_keeper")
    link = "https://demo.example/app/#join=TOKEN123"
    keeper.write_page(tmp_path, link)
    page = (tmp_path / "index.html").read_text()
    assert link in page
    assert "saracenbridge://join?invite=https%3A%2F%2Fdemo.example%2Fapp%2F%23join%3DTOKEN123" in page
    assert (tmp_path / "qrcode-generator.js").exists() and "createSvgTag" in page
    assert "made-up production" in page


def test_a_public_studio_names_its_own_https_address(monkeypatch):
    from studio.room import host
    monkeypatch.setenv("ROOM_PUBLIC_BASE", "https://demo.example/")
    assert host.address() == "https://demo.example"
    monkeypatch.delenv("ROOM_PUBLIC_BASE")
    assert host.address().startswith("http://") and host.address().endswith(":8710")
