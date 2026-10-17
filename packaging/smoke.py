"""Smoke test a running Saracen Bridge Studio (packaged or not). Standard library only.

    python packaging/smoke.py http://127.0.0.1:8798 [https://room.example.com]

The optional second address is a Room hub (1.0.8) to health-check. Never point this at port 8799.

Checks every layer the installer must carry: UI, catalog, reference database, engine figures against Jon's
workbooks, script intake for all three formats, and the agreement builder's bundled master.
Exits non-zero on the first failure.
"""
from __future__ import annotations

import json
import sys
import time
import urllib.request
import uuid
from pathlib import Path

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8798").rstrip("/")
if any(":8799" in a for a in sys.argv[1:]):
    sys.exit("8799 is A.I.D.E.N.'s port on this machine: smoke tests use 8798.")
FIX = Path(__file__).resolve().parent.parent / "tests" / "fixtures"


def call(path, body=None, form=None, raw=False):
    data, headers = None, {}
    if body is not None:
        data, headers = json.dumps(body).encode(), {"Content-Type": "application/json"}
    if form is not None:
        b = uuid.uuid4().hex
        parts = []
        for name, value in form:
            if isinstance(value, tuple):
                fn, content = value
                parts.append(f'--{b}\r\nContent-Disposition: form-data; name="{name}"; filename="{fn}"\r\n'
                             f"Content-Type: application/octet-stream\r\n\r\n".encode() + content + b"\r\n")
            else:
                parts.append(f'--{b}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode())
        data, headers = b"".join(parts) + f"--{b}--\r\n".encode(), {"Content-Type": f"multipart/form-data; boundary={b}"}
    with urllib.request.urlopen(urllib.request.Request(BASE + path, data=data, headers=headers), timeout=60) as r:
        out = r.read()
    return out if raw else json.loads(out)


def check(label, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + label + (f"  ({detail})" if detail else ""))
    if not ok:
        sys.exit(1)


for _ in range(60):                                  # wait up to 60 s for the app to come up
    try:
        call("/api/health")
        break
    except Exception:
        time.sleep(1)

h = call("/api/health")
check("health", h.get("ok") is True, h.get("version"))
check("ui served", b"Saracen Bridge Studio" in call("/", raw=True) and len(call("/ui/studio.js", raw=True)) > 10_000)
ids = [t["id"] for t in call("/api/catalog")["tools"]]
check("catalog has 12 tools incl. A.I.D.E.N. and F.R.A.T.", len(ids) == 12 and "aiden" in ids and "frat" in ids, ",".join(ids))
check("reference database", len(call("/api/tools/incentives/programmes")) == 69)

ex = call("/api/tools/finance/example")
fin = call("/api/tools/finance/plan", ex)
check("finance plan matches Jon's SHADE workbook", abs(fin["residual_debt_needed"] - 3_168_657.42) < 0.01, fin["residual_debt_needed"])
inc = call("/api/tools/incentives/calc", {"routes": [{"programme_id": "ESP-NAT-FOR", "qualifying_spend": 6_000_000,
                                                      "project_cost": 10_000_000, "eligibility": "Eligible"}]})
check("incentive engine matches Jon's regression R01", abs(inc[0]["gross_benefit"] - 1_550_000) < 0.01, inc[0]["gross_benefit"])

files = [("tool", "coverage")] + [("files", (n, (FIX / n).read_bytes())) for n in ("sample.fountain", "sample.fdx", "sample.pdf")]
res = {r["file"]: r for r in call("/api/tools/script/intake", form=files)}
check("script intake: Fountain", res["sample.fountain"].get("scene_count") == 4, res["sample.fountain"])
check("script intake: Final Draft", res["sample.fdx"].get("scene_count") == 2, res["sample.fdx"])
check("script intake: PDF", res["sample.pdf"].get("scene_count") == 4, res["sample.pdf"])
check("library index", call("/api/runs?tool=coverage")["total"] >= 3)
blank = call("/api/tools/agreement/blank", raw=True)
check("agreement builder master bundled", len(blank) > 10_000)
built = call("/api/tools/agreement/build", form=[("draft_name", "SMOKE_DRAFT_01"), ("file", ("inputs.xlsx", blank))])
check("agreement builder runs Jon's workflow", "ok" in built and (built["ok"] or built.get("error")),
      "built" if built.get("ok") else built.get("error"))
diag = call("/api/diagnostics")
check("coverage writer carries Jon's 11-section spec", diag["coverage_spec_sections"] == 11, diag["coverage_spec_sections"])
check("coverage Word report renders on Jon's template", diag["report_template"] is True and diag.get("report_render_bytes", 0) > 100_000,
      diag.get("report_render_bytes") or diag["report_template"])
check("Jon's documents searchable", diag.get("knowledge_hits", 0) >= 3, diag.get("knowledge_hits"))
check("actor database for casting checks", diag["actors"] == 1004, diag["actors"])
check("0.4 brand and assistant served", len(call("/ui/brand/marks.js", raw=True)) > 30_000 and b"askToggle" in call("/ui/studio.js", raw=True))
check("1.0.3 Library shows saved results, not raw data", b"RESULT_VIEWS" in call("/ui/studio.js", raw=True))
sched = call("/api/tools/script/intake", form=[("tool", "schedule"), ("files", ("smoke.fountain", (FIX / "sample.fountain").read_bytes()))])[0]
bud = call("/api/tools/schedule/budget", {"run_id": sched["run_id"], "jurisdiction": "United Kingdom", "inputs": {"vfx_shots": 0}})
xl = call(f"/api/runs/schedule/{sched['run_id']}/budget.xlsx", raw=True)
check("1.0.4 schedule and budget from Jon's rate cards, with the workbook", bud["schedule"]["base"]["shoot_days"] >= 1
      and bud["budget"]["base"]["known_total"] > 0 and bud["currency"] == "GBP" and xl[:2] == b"PK",
      f"{bud['schedule']['base']['shoot_days']} days, GBP {bud['budget']['base']['known_total']:,.0f} priced")
proj = {"valuation_date": "2026-10-15", "intake": {"title": "Smoke Valuation", "budget": 5000000, "budget_currency": "USD"},
        "films": [{"id": "F1", "title": "Comp"}], "anchor": {"usd": 8000000, "note": "smoke"},
        "deals": [{"id": "D1", "film_id": "F1", "territory": "USA", "date": "2025-06-01", "currency": "USD", "amount": 2000000, "grade": "B", "package": "All rights"}]}
val = call("/api/tools/sales/value", {"project": proj})
usa = val["territories"][0]
wbk = call(f"/api/runs/sales/{val['run_id']}/engine.xlsx", raw=True)
check("1.0.5 Jon's Sales Valuation Engine runs, deal evidence first, workbook downloads",
      usa["territory"] == "USA" and usa["basis"] == "Verified transaction model" and val["summary"]["expected"] > 0
      and val["controls"]["order"] == "PASS" and wbk[:2] == b"PK", f"USA Expected Close {usa['expected']:,.0f}; total {val['summary']['expected']:,.0f}")
scan = call("/api/tools/script/intake", form=[("tool", "coverage"), ("files", ("smoke_scanned.pdf", (FIX / "sample_scanned.pdf").read_bytes()))])[0]
check("1.0.6 a scanned script is read by OCR", scan.get("scene_count") == 4 and scan.get("speaking_roles") == 3 and "OCR" in (scan.get("format") or ""),
      f"{scan.get('scene_count')} scenes, {scan.get('speaking_roles')} roles, {scan.get('format')}")
def status_of(path, body=None, form=None):
    try:
        call(path, body, form)
        return 200
    except urllib.error.HTTPError as e:
        return e.code


import urllib.error  # noqa: E402
opts = call("/api/tools/brand/spot/options")
brandrun = call("/api/tools/script/intake", form=[("tool", "brand"), ("files", ("smoke_ferry.fountain", (FIX / "night_ferry.fountain").read_bytes()))])[0]
connected = bool(call("/api/diagnostics")["ai"].get("connected"))
codes = [status_of("/api/tools/brand/spot", {"run_ids": [brandrun["run_id"]]}), status_of("/api/tools/schedule/elements", {"run_ids": [sched["run_id"]]}),
         status_of("/api/tools/bfi/read", {"tool": "brand", "run_id": brandrun["run_id"]}),
         status_of("/api/tools/finance/termsheet", form=[("file", ("smoke_ts.docx", (FIX / "sample_term_sheet.docx").read_bytes()))])]
js = call("/ui/studio.js", raw=True)
specs = call("/api/diagnostics")["ai_specs"]
check("1.0.7 Jon's instructions for every AI feature are installed", all(v is True for v in specs.values()), specs)
check("1.0.7 the assistant is Jonny and its answers don't flash", b'"Ask Jonny"' in js and b"jonny-reveal" in js and b"caret 1s steps" not in call("/ui/studio.css", raw=True))
check("1.0.7 AI tools: brand spotting, element tagging, BFI read, term sheets (queued with an engine, a plain 409 without)",
      len(opts["categories"]) == 12 and brandrun["scene_count"] == 14 and all(c == (200 if connected else 409) for c in codes)
      and all(f in js for f in (b"brandSpot", b"elementsBox", b"bfiReader", b"termsheetView", b"jobWatch", b"pkgBar")),
      f"engine {'connected' if connected else 'not connected'}: {codes}")
check("Jon served", b"jonSvg" in call("/ui/studio.js", raw=True) and b"coachStart" in call("/ui/studio.js", raw=True))
lb = call("/api/tools/lookbook/intake", form=[("files", ("deck.pdf", (FIX / "sample.pdf").read_bytes()))])
img = call(f"/api/runs/lookbook/{lb['run_id']}/files/pages/p01.jpg?inline=1", raw=True)
check("look book pages render (pdfium)", lb.get("pages", 0) >= 1 and img[:2] == b"\xff\xd8", lb.get("pages"))
names = [a["actor"] for a in call("/api/lookup/actors?q=chris&limit=12")]
prof = call("/api/lookup/actor?name=Chris%20Evans")
check("name finder narrows and fills a profile", names[:2] == ["Chris Evans", "Chris Hemsworth"] and prof.get("indicative_cash_fee_high_usd", 0) > 0,
      ", ".join(names[:4]))
cl = call("/api/cloud")
check("cloud AI off by default, no key", cl["enabled"] is False and not any(cl["keys"].values()), cl["provider"])
check("AI engine status answers", "connected" in diag["ai"], diag["ai"].get("description") or diag["ai"].get("reason"))
dl = call("/api/ai/download")
check("Gemma download ready to resume", set(dl["options"]) == {"12b", "e4b"} and "state" in dl,
      f"{dl['state']}, wanted {dl.get('wanted') or 'none'}")
room = call("/api/diagnostics").get("room", {})
check("1.0.8 the Room's encryption is bundled (libsodium, safety words, live link)", room.get("crypto") is True, room)
check("1.1.0 this Studio can host its own productions (the Room's hub, phone app and meetings server are bundled)",
      room.get("hub") is True and room.get("meetings") is True, {k: room.get(k) for k in ("hub", "meetings")})
rs = call("/api/room/state")
check("1.0.8 the Room answers before it's set up", isinstance(rs.get("status"), str) and "hub" in rs, rs.get("status"))
idx = call("/", raw=True)
rjs, mjs = call("/ui/room.js", raw=True), call("/ui/room-meet.js", raw=True)
lk = call("/ui/vendor/livekit-client.umd.js", raw=True)
check("1.0.8 Room pages, call sheets and meetings served",
      all(s in idx for s in (b"room.js", b"room-callsheet.js", b"room-meet.js", b"livekit-client.umd.js"))
      and b"roomRoute" in rjs and b"callsheetStrip" in call("/ui/room-callsheet.js", raw=True) and len(lk) > 200_000)
check("1.0.8 voice: the mic picker finds the system default, follows it and asks kindly first",
      all(s in mjs for s in (b"micLabel", b"enumerateDevices", b"devicechange", b"micConsent", b"noiseSuppression", b"echoCancellation",
                             b'"Microphone"', b'"automatic"')))
HUB = (sys.argv[2] if len(sys.argv) > 2 else "").rstrip("/")
if HUB:                                               # a Room hub to check (the deploy kit's, or a test hub on the LAN)
    with urllib.request.urlopen(HUB + "/api/health", timeout=30) as r:
        hh = json.loads(r.read())
    with urllib.request.urlopen(HUB + "/app/", timeout=30) as r:
        app_html = r.read()
    check("1.0.8 the Room hub answers and serves the phone app", hh.get("ok") is True and b"manifest.webmanifest" in app_html,
          f"{HUB}: {hh.get('version')}")
else:
    print("SKIP 1.0.8 Room hub health (give the hub's address as a second argument to check it)")
print("SMOKE OK")
