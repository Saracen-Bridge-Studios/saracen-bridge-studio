"""A Studio hosting a test production for the iPhone app's UI test (and for screenshots), then standing in for the
executive: checks and approves the test phone when it asks to join, as Jon would on a call.

    python ios/ci/studio_for_tests.py STUDIO_URL invite     -> starts a production, seeds it, prints an invite link
    python ios/ci/studio_for_tests.py STUDIO_URL approve NAME [SECONDS]
        -> waits for NAME's phone, checks its safety words, approves it, then puts NAME on today's call sheet

The Studio must be running (studio_launcher.py --headless --port PORT). Uses only the Studio's own Room API.
"""
import json
import sys
import time
import urllib.request


def call(base, method, path, body=None):
    req = urllib.request.Request(base + path, method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=60).read())


def space(view, name):
    return next(s["id"] for s in view["spaces"] if s["name"] == name)


def invite(base):
    call(base, "POST", "/api/room/host", {"name": "Jon Saracen", "production": "SHADE"})
    for _ in range(30):
        try:
            v = call(base, "GET", "/api/room/view")
            if v.get("production"):
                break
        except Exception:  # noqa: BLE001 - the hub is starting
            pass
        time.sleep(1)
    prod = v["production"]
    office = space(v, "Production office")
    cast = space(v, "Cast")
    call(base, "POST", "/api/room/note", {"spaces": [office, cast], "title": "Day 12 call sheet v3", "status": "Open", "pinned": True,
                                          "body": "Unit call 06:30. Weather cover moved to Stage B."})
    call(base, "POST", "/api/room/note", {"spaces": [office], "title": "Recce: quarry location, Thursday", "status": "Open",
                                          "body": "Keys only. Vans leave base 07:00; bring permits."})
    call(base, "POST", "/api/room/note", {"spaces": [office], "title": "Spanish incentive confirmed", "status": "Decision",
                                          "body": "Gross benefit at gate PRELIMINARY. Finance plan updated."})
    call(base, "POST", "/api/room/message", {"space": office, "text": "Morning all. Call sheet v3 is on the board; weather cover moved to Stage B."})
    call(base, "POST", "/api/room/message", {"space": office, "text": "Recce vans leave base at 07:00 on Thursday."})
    link = call(base, "POST", "/api/room/invite", {"production": prod, "tier": "producer", "name": "UI Test Phone", "role": "Line producer"})["link"]
    print(link)


def approve(base, name, seconds=600):
    v = call(base, "GET", "/api/room/view")
    prod = v["production"]
    end = time.time() + float(seconds)
    while time.time() < end:
        pend = [x for x in call(base, "GET", f"/api/room/access?production={prod}")["pending"] if x["name"] == name]
        if pend:
            dev = pend[0]["device"]
            call(base, "POST", f"/api/room/pending/{dev}/check", {})
            time.sleep(8)                                   # the phone shows its words (the UI test takes a picture)
            call(base, "POST", f"/api/room/pending/{dev}/approve", {})
            print("approved", name, flush=True)
            time.sleep(3)
            v = call(base, "GET", "/api/room/view")
            me = next((p["user"] for p in v.get("people", []) if p["name"] == name), None)
            if me:
                call(base, "POST", "/api/room/callsheets", {
                    "production": prod, "day": "Day 12", "date": time.strftime("%Y-%m-%d"), "unit_call": "06:30",
                    "location": "Quarry, Northfield", "weather_cover": "Stage B", "hospital": "St Mary's, Northfield",
                    "scenes": [{"no": "14", "slug": "EXT. QUARRY - DAY", "pages": "2"}, {"no": "15", "slug": "EXT. QUARRY ROAD - DAY", "pages": "1 3/8"}],
                    "rows": [{"user": me, "call": "06:00", "pickup": "05:20", "pickup_address": "12 Harbour Row", "driver": "Dan"}]})
                print("call sheet posted", flush=True)
            return
        time.sleep(2)
    print("no phone asked to join", flush=True)


if __name__ == "__main__":
    base, what = sys.argv[1].rstrip("/"), sys.argv[2]
    if what == "invite":
        invite(base)
    else:
        approve(base, sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else 600)
