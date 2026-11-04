"""The demo Studio's keeper: a made-up production that Apple's reviewers (and anyone checking the iPhone app) can join.

Runs beside a headless Studio on a public server (see README.md). It:
  - hosts THE LIGHTHOUSE KEEPER on first run and fills its board, chat and call sheet with invented content;
  - keeps one unused invite open for the next reviewer device and writes it to the review page (index.html in
    REVIEW_DIR), with the link, an "Open in the Saracen Bridge app" button and a QR code;
  - stands in for the executive: when a device asks to join, it checks the safety words and approves it, then puts
    that person on today's call sheet. Only this demo Room works this way; a real production's executive always
    checks the three words with the person on a call.

Nothing real is in it: no script, no real production, no real person.

    python packaging/demo/demo_keeper.py [--studio http://127.0.0.1:8796] [--review-dir /srv/review]
"""
from __future__ import annotations

import argparse
import html
import json
import shutil
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
QR_JS = HERE.parent.parent / "ui" / "vendor" / "qrcode-generator.js"
REVIEW_NAME = "App Review"


def call(base: str, method: str, path: str, body=None):
    req = urllib.request.Request(base + path, method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=60).read())


def wait_for(base: str):
    for _ in range(300):
        try:
            if call(base, "GET", "/api/health").get("ok"):
                return
        except Exception:  # noqa: BLE001 - the Studio is starting
            pass
        time.sleep(1)
    raise SystemExit("The Studio didn't start.")


def view(base: str) -> dict | None:
    try:
        v = call(base, "GET", "/api/room/view")
        return v if v.get("production") else None
    except Exception:  # noqa: BLE001 - not hosting yet
        return None


def space(v: dict, name: str) -> str:
    return next(s["id"] for s in v["spaces"] if s["name"] == name)


def seed(base: str) -> dict:
    call(base, "POST", "/api/room/host", {"name": "Alex Morgan", "production": "The Lighthouse Keeper"})
    v = None
    for _ in range(60):
        v = view(base)
        if v:
            break
        time.sleep(1)
    office, cast = space(v, "Production office"), space(v, "Cast")
    notes = [([office, cast], "Day 12 call sheet v3", "Open", True, "Unit call 06:30. Weather cover moved to Stage B."),
             ([office], "Recce: harbour wall, Thursday", "Open", False, "Keys only. Vans leave base 07:00; bring the harbour master's permit."),
             ([office], "Night shoot moved to Friday", "Decision", False, "Tide tables suit Friday. Catering and transport told.")]
    for spaces, title, status, pinned, body in notes:
        call(base, "POST", "/api/room/note", {"spaces": spaces, "title": title, "status": status, "pinned": pinned, "body": body})
    for sid, text in [(office, "Morning all. Call sheet v3 is on the board; weather cover moved to Stage B."),
                      (office, "Recce vans leave base at 07:00 on Thursday."),
                      (cast, "Sides for scenes 14 and 15 are in your day. Pickups are on the call sheet.")]:
        call(base, "POST", "/api/room/message", {"space": sid, "text": text})
    return view(base)


def write_page(review_dir: Path, link: str):
    review_dir.mkdir(parents=True, exist_ok=True)
    if QR_JS.exists():
        shutil.copyfile(QR_JS, review_dir / "qrcode-generator.js")
    app_link = "saracenbridge://join?invite=" + urllib.request.quote(link, safe="")
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Saracen Bridge: demo production for App Review</title>
<style>
body {{ margin: 0; background: #07050b; color: #f1ebe0; font: 16px/1.55 -apple-system, system-ui, sans-serif; }}
main {{ max-width: 640px; margin: 0 auto; padding: 32px 20px 48px; }}
h1 {{ font: 600 28px/1.2 Georgia, serif; margin: 0 0 12px; }}
a.btn {{ display: block; text-align: center; padding: 16px; border-radius: 14px; background: linear-gradient(180deg,#fff3c8,#e3ad3a);
  color: #1d1608; font-weight: 650; text-decoration: none; margin: 18px 0; }}
code {{ display: block; word-break: break-all; padding: 12px; border-radius: 10px; background: #191125; color: #ffd873; font-size: 13px; }}
ol li {{ margin-bottom: 8px; }} .muted {{ color: #877f8f; font-size: 14px; }} #qr svg {{ width: 220px; height: 220px; background: #fff; border-radius: 12px; }}
</style></head><body><main>
<h1>Demo production for App Review</h1>
<p>THE LIGHTHOUSE KEEPER is a made-up production. Everything in it is invented. Joining it shows the whole app working:
today's call sheet, the board, chat, files, encrypted huddles, and Report, Block and Delete my account.</p>
<ol>
<li>Install Saracen Bridge on this iPhone or iPad.</li>
<li>Tap <b>Open in the Saracen Bridge app</b> below. (Or copy the link, open the app, tap <b>Join with an invite</b>, then <b>Paste</b>.
On another device, scan the QR code from the app's Join screen.)</li>
<li>Type any name, tick the terms, and tap <b>Join</b>.</li>
<li>This demo approves the device by itself within a few seconds. In a real production, an executive checks three
safety words with the person on a call first.</li>
</ol>
<a class="btn" href="{html.escape(app_link)}">Open in the Saracen Bridge app</a>
<p class="muted">The invite link (single use; this page shows a fresh one after each device joins, so reload it for a second device):</p>
<code>{html.escape(link)}</code>
<p id="qr"></p>
<p class="muted">Updated {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}.</p>
<script src="qrcode-generator.js"></script>
<script>try {{ const q = qrcode(0, "M"); q.addData({json.dumps(link)}); q.make();
document.getElementById("qr").innerHTML = q.createSvgTag({{ cellSize: 6, margin: 3, scalable: true }}); }} catch (e) {{}}</script>
</main></body></html>"""
    tmp = review_dir / "index.html.tmp"
    tmp.write_text(page, encoding="utf-8")
    tmp.replace(review_dir / "index.html")


def open_invite(base: str, v: dict) -> bool:
    """Is there still an unused reviewer invite?"""
    a = call(base, "GET", f"/api/room/access?production={v['production']}")
    return any(i["name"] == REVIEW_NAME and i["status"] == "Not used yet" for i in a["invites"])


def approve_waiting(base: str, v: dict) -> list[str]:
    done = []
    a = call(base, "GET", f"/api/room/access?production={v['production']}")
    for p in a["pending"]:
        dev = p["device"]
        if p.get("problem"):
            print("not approving", dev, p["problem"], file=sys.stderr, flush=True)
        elif p.get("words") and p.get("mine"):
            call(base, "POST", f"/api/room/pending/{dev}/approve", {})
            done.append(dev)
        elif not p.get("checking"):
            call(base, "POST", f"/api/room/pending/{dev}/check", {})   # the words appear once the device reveals its half
    return done


def call_sheet_for_newcomers(base: str, v: dict, seen: set):
    v = view(base) or v
    for person in v.get("people", []):
        u = person["user"]
        if u in seen or person.get("tier") == "executive":
            continue
        seen.add(u)
        call(base, "POST", "/api/room/callsheets", {
            "production": v["production"], "day": "Day 12", "date": time.strftime("%Y-%m-%d"), "unit_call": "06:30",
            "location": "Harbour wall, Porthallow", "weather_cover": "Stage B", "hospital": "Royal Cornwall, Truro",
            "scenes": [{"no": "14", "slug": "EXT. HARBOUR WALL - DAY", "pages": "2"},
                       {"no": "15", "slug": "EXT. LIGHTHOUSE STEPS - DAY", "pages": "1 3/8"}],
            "rows": [{"user": u, "call": "06:00", "pickup": "05:20", "pickup_address": "12 Harbour Row", "driver": "Dan"}]})


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--studio", default="http://127.0.0.1:8796")
    ap.add_argument("--review-dir", default="/srv/review")
    ap.add_argument("--once", action="store_true", help="one pass (tests)")
    a = ap.parse_args(argv)
    base, review_dir = a.studio.rstrip("/"), Path(a.review_dir)
    wait_for(base)
    v = view(base) or seed(base)
    seen = {p["user"] for p in v.get("people", [])}
    while True:
        try:
            v = view(base) or v
            if not open_invite(base, v):
                link = call(base, "POST", "/api/room/invite", {"production": v["production"], "tier": "producer",
                                                               "name": REVIEW_NAME, "role": "App Review"})["link"]
                write_page(review_dir, link)
                print("new reviewer invite:", link, flush=True)
            for dev in approve_waiting(base, v):
                print("approved", dev, flush=True)
            call_sheet_for_newcomers(base, v, seen)
        except Exception as e:  # noqa: BLE001 - keep keeping
            print("keeper:", e, file=sys.stderr, flush=True)
        if a.once:
            return
        time.sleep(3)


if __name__ == "__main__":
    main()
