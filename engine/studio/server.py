"""Local HTTP API + UI. Binds to 127.0.0.1 only; nothing is exposed to the network."""
from __future__ import annotations

import csv
import io
import json
import hashlib
import os
import re
import subprocess
import sys
import threading
import time
import webbrowser
from dataclasses import asdict
from pathlib import Path

from fastapi import Body, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from starlette.concurrency import run_in_threadpool

from . import agents, agreement, assist, bfi, bfiread, brandspot, budget, casting, coverage, estimates, schedreason, sales, fetch, finance, greenlight, incentive, jobs, keys, knowledge, llm, lookbook, lookups, ocr, producerfee, refdata, script, store, termsheet

VERSION = "1.2.4"
UI_DIR = refdata.app_root() / "ui"
CATALOG = json.loads((refdata.app_root() / "tools" / "catalog.json").read_text(encoding="utf-8"))
GENRES = json.loads((refdata.app_root() / "tools" / "genres.json").read_text(encoding="utf-8"))   # Tim's list (1.1.2)

app = FastAPI(title="Saracen Bridge Studio", version=VERSION, docs_url=None, redoc_url=None)


@app.exception_handler(Exception)
async def _unexpected(request, exc: Exception):
    """A fault in the Studio itself says so in plain words, instead of a bare "Internal Server Error" (Tim, 20 Oct:
    Jonny read that as a busy web server and told him to wait for the traffic to drop). The traceback still goes to
    studio.log."""
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=500, content={"detail": (
        f"Something went wrong inside the Studio ({exc.__class__.__name__}). It isn't your file, the internet or your "
        f"account: everything here runs on this computer. Try once more. If it happens again, send studio.log from "
        f"the Studio's data folder ({store.home()}) to whoever looks after your Studio.")})


# ---------- shell ----------
@app.get("/api/health")
def health():
    return {"ok": True, "version": VERSION}


_HEARTBEAT: list[float] = []


def last_heartbeat() -> float | None:
    return _HEARTBEAT[-1] if _HEARTBEAT else None


@app.post("/api/heartbeat")
def heartbeat():
    """The open page checks in; in browser mode the launcher stops the engine when check-ins stop."""
    import time as _t
    _HEARTBEAT[:] = [_t.time()]
    return {"ok": True}


@app.get("/api/catalog")
def catalog():
    return CATALOG


@app.get("/api/settings")
def get_settings():
    return store.load_settings()


@app.put("/api/settings")
def put_settings(s: dict = Body(...)):
    return store.save_settings(s)


@app.get("/api/diagnostics")
def diagnostics():
    """What the installed build carries: used by the smoke test and for support."""
    from . import report
    out = {"version": VERSION}
    try:
        out["coverage_spec_sections"] = len(coverage.spec()["sections"])
    except Exception as e:  # noqa: BLE001
        out["coverage_spec_sections"] = f"error: {e}"
    try:                                     # a full render, so every file the renderer needs is exercised
        sample = json.loads((refdata.app_root() / "tools" / "sample_coverage.json").read_text(encoding="utf-8"))
        out["report_render_bytes"] = len(report.coverage_docx(sample))
        out["report_template"] = True
    except Exception as e:  # noqa: BLE001
        out["report_template"] = f"error: {e}"
    out["actors"] = refdata.rows("SELECT COUNT(*) n FROM talent_actors")[0]["n"]
    try:
        out["knowledge_hits"] = len(knowledge.search("golden points rule cultural test", "bfi"))
    except Exception as e:  # noqa: BLE001
        out["knowledge_hits"] = f"error: {e}"
    specs = {}                                # Jon's instructions each AI feature reads at run time (1.0.7)
    for name, read in (("brand", lambda: brandspot._rules()), ("bfi", lambda: bfiread.SKILL.read_text(encoding="utf-8")),
                       ("finance", lambda: termsheet._rules()), ("coverage", lambda: coverage.SKILL.read_text(encoding="utf-8"))):
        try:
            specs[name] = len(read()) > 200
        except Exception as e:  # noqa: BLE001
            specs[name] = f"error: {e}"
    out["ai_specs"] = specs
    try:                                      # the Room (1.0.8): libsodium, the safety-word list and the live link all bundled
        import room_crypto as rc
        import websockets.sync.client  # noqa: F401
        a, b = rc.Device(), rc.Device()
        key = rc.new_key()
        w = rc.wrap_key(key, "s_check", 1, b.public(), a)
        ok = rc.unwrap_key(w, b) == key and len(rc.WORDS) == 2048
        from .room import host as _h
        import room_hub.app  # noqa: F401 - hosting: the hub and its phone app are bundled (1.1.0)
        from pathlib import Path as _P
        app_static = _P(room_hub.app.__file__).with_name("static") / "index.html"
        out["room"] = {"crypto": ok, "words": len(rc.WORDS), "hub": app_static.exists(), "meetings": bool(_h._livekit_bin()),
                       "host": _h.status()}
    except Exception as e:  # noqa: BLE001
        out["room"] = {"crypto": f"error: {e}"}
    out["bundled_model"] =(lambda f: f[1].name if f else None)(llm.bundled_files())
    out["ai"] = llm.status(store.load_settings())
    return out


@app.get("/api/ai/status")
def ai_status():
    s = store.load_settings()
    out = llm.status(s)
    c = llm.cloud_status(s)
    out["cloud"] = {k: c[k] for k in ("enabled", "provider", "model", "active")} | {"name": llm.CLOUD[c["provider"]]["name"],
                                                                              "has_key": bool(c["keys"].get(c["provider"]))}
    eng, _ = llm.resolve(s, use="writing")
    out["vision"], out["vision_reason"] = llm.can_see(eng)
    _resume_download_once()
    d = fetch.status()
    out["download"] = {k: d.get(k) for k in ("state", "active", "model", "model_name", "done_bytes", "total_bytes")}
    if not out.get("connected") and d["active"]:
        pct = int(100 * (d.get("done_bytes") or 0) / max(d.get("total_bytes") or 1, 1))
        out["reason"] = f"{d['model_name']} is downloading ({pct}%). Writing tools switch on when it's done."
    return out


_RESUMED = threading.Event()


def _resume_download_once():
    """A download the installer asked for (llm/wanted.json), or one cut short, carries on when the Studio opens."""
    if not _RESUMED.is_set():
        _RESUMED.set()
        if llm.bundled_files() or llm.located_models():
            return                    # 1.2.4: a model is already here; an old download must not take over the card
        try:
            fetch.resume_if_wanted()
        except Exception:  # noqa: BLE001 - shown on the Settings page instead
            pass


@app.get("/api/ai/download")
def ai_download_status():
    _resume_download_once()
    out = fetch.status()
    out["located"] = _located()
    return out


def _located() -> dict | None:
    """The model the Studio will run when it isn't one it downloaded itself (chosen in Settings, or found in Downloads)."""
    files = llm.bundled_files()
    m = files[1] if files else (llm.chosen_model() or next(iter(llm.located_models()), None))
    if not m or m.parent == llm.bundled_dir() / "models":
        return None
    return {"path": str(m), "name": m.stem, "chosen": m == llm.chosen_model(), "vision": bool(llm.projector_for(m))}


@app.post("/api/ai/locate")
def ai_locate(body: dict = Body(default={})):
    """Point the Studio at a model file anywhere on this computer (1.2.2): {"path": ...}, or no path to open the
    system's Open dialog here, or {"clear": true} to go back to finding it by itself."""
    from . import picker
    s = store.load_settings()
    eng = s.setdefault("ai_engine", {})
    if body.get("clear"):
        eng.pop("model_path", None)
        store.save_settings(s)
        return {"cleared": True, "located": _located()}
    path = str(body.get("path") or "").strip()
    if not path:
        try:
            path = picker.choose_file("Choose the Gemma model file (.gguf)") or ""
        except (RuntimeError, OSError, subprocess.SubprocessError) as e:
            raise HTTPException(400, str(e)) from e
        if not path:
            return {"cancelled": True}
    p = Path(path).expanduser()
    if not p.is_file():
        raise HTTPException(400, f"There's no file at {p}.")
    if p.suffix.lower() != ".gguf":
        raise HTTPException(400, "That isn't a model file: Gemma's file ends in .gguf.")
    if "mmproj" in p.name.lower():
        raise HTTPException(400, "That's Gemma's vision add-on (mmproj). Choose the model itself; the add-on is found beside it.")
    if p.stat().st_size < llm.MIN_MODEL_BYTES:
        raise HTTPException(400, "That file is too small to be a Gemma model, or it hasn't finished downloading.")
    eng["model_path"] = str(p)
    store.save_settings(s)
    return {"path": str(p), "name": p.stem, "located": _located(), "engine_installed": not fetch.missing("engine"),
            "vision": bool(llm.projector_for(p))}


@app.post("/api/ai/download")
def ai_download_start(body: dict = Body(...)):
    """Download (or resume) Gemma: {"model": "12b" | "e4b"}. Carries on from the last byte if interrupted."""
    try:
        return fetch.start(str(body.get("model", "")))
    except ValueError as e:
        raise HTTPException(400, str(e)) from e


@app.post("/api/ai/download/pause")
def ai_download_pause():
    return fetch.pause()


@app.get("/api/cloud")
def cloud_get():
    return llm.cloud_status(store.load_settings())


@app.put("/api/cloud")
def cloud_put(body: dict = Body(...)):
    """Switch the user's cloud AI on or off, pick provider and model, save or clear a key. The key never comes back."""
    s = store.load_settings()
    c = s.setdefault("cloud_ai", {})
    prov = body.get("provider", c.get("provider", "anthropic"))
    if prov not in llm.CLOUD:
        raise HTTPException(400, "Unknown cloud provider.")
    if isinstance(body.get("key"), str) and body["key"].strip():
        keys.put(prov, body["key"])
    if body.get("clear_key"):
        keys.put(prov, "")
    if prov != c.get("provider"):
        c["model"] = ""
    c["provider"] = prov
    for k in ("enabled", "model"):
        if k in body:
            c[k] = body[k]
    if isinstance(body.get("use_for"), dict):
        c["use_for"] = {**c.get("use_for", {}), **{u: bool(v) for u, v in body["use_for"].items() if u in ("chat", "writing")}}
    if c.get("enabled") and not keys.get(prov):
        c["enabled"] = False
        store.save_settings(s)
        raise HTTPException(409, f"Paste your {llm.CLOUD[prov]['name']} API key first.")
    store.save_settings(s)
    return llm.cloud_status(s)


@app.get("/api/cloud/models")
def cloud_models(provider: str):
    if provider not in llm.CLOUD:
        raise HTTPException(400, "Unknown cloud provider.")
    key = keys.get(provider)
    if not key:
        raise HTTPException(409, f"Paste your {llm.CLOUD[provider]['name']} API key first.")
    try:
        return {"models": llm.cloud_models(provider, key)}
    except llm.EngineError as e:
        raise HTTPException(502, f"{llm.CLOUD[provider]['name']} did not list models: {e}") from e


@app.post("/api/cloud/test")
def cloud_test():
    import time as _t
    s = store.load_settings()
    c = llm.cloud_status(s)
    key = keys.get(c["provider"])
    if not key:
        raise HTTPException(409, f"Paste your {llm.CLOUD[c['provider']]['name']} API key first.")
    p = c["provider"]
    engine = llm.Engine("anthropic" if p == "anthropic" else "cloud", llm.CLOUD[p]["url"], c["model"], key, p)
    t0 = _t.time()
    try:
        reply = llm.chat(engine, "Reply in five words or fewer.", "Say that the Saracen Bridge Studio cloud link is ready.",
                         settings=s, max_tokens=40, temperature=0)
    except llm.EngineError as e:
        raise HTTPException(502, f"{llm.CLOUD[p]['name']} did not answer: {e}") from e
    return {"ok": True, "reply": reply, "seconds": round(_t.time() - t0, 1), "engine": engine.describe()}


CONTEXT_FULL = ("The local engine ran out of room for this conversation. Start a new chat with the bin at the top and "
                "ask again; if a coverage or look book job is running, it may help to wait for it to finish.")


def _context_full(e: Exception) -> bool:
    t = str(e).lower()
    return "context size" in t or "exceeds the available context" in t or "context length" in t


@app.post("/api/assist/chat")
def assist_chat(body: dict = Body(...)):
    """Ask Jonny (named Jon until 1.0.7). Streams plain text; text after a NUL marker is an error that came mid-answer. X-Sources lists the
    sections of Jon's documents put in front of the model."""
    s = store.load_settings()
    engine = llm.cloud_engine(s, "chat")
    if not engine:
        engine, why = llm.resolve(s, use="")
        if not engine:
            raise HTTPException(409, why)
    msgs = assist.clean_history(body.get("messages") or [])
    if not msgs:
        raise HTTPException(400, "Ask a question first.")
    question = msgs[-1]["content"] if msgs[-1]["role"] == "user" else ""
    topic = ((body.get("page") or {}).get("title") or "").split("/")[-1]       # "Production / BFI Certification" -> the tool
    refs = knowledge.search(f"{question} {topic}", assist.page_tool(body.get("page")), k=5, question=question) if body.get("documents", True) else []
    ctx = 200_000 if engine.is_cloud else int(s["ai_engine"].get("context", 16384))
    system, msgs, refs = assist.fit(CATALOG, body.get("page"), True, refs, msgs, ctx - assist.CHAT_TOKENS - 512)
    from urllib.parse import quote
    sources = quote(json.dumps([{"title": r["title"], "heading": r["heading"]} for r in refs], ensure_ascii=False))

    def gen():
        said = False
        try:
            try:
                for piece in llm.stream(engine, system, msgs, settings=s, max_tokens=assist.CHAT_TOKENS):
                    said = True
                    yield piece
            except llm.EngineError as e:
                if said or not _context_full(e):
                    raise
                # the engine had no room (e.g. another program's request in the same slot): once more, question only
                yield from llm.stream(engine, system, msgs[-1:], settings=s, max_tokens=assist.CHAT_TOKENS)
        except llm.EngineError as e:
            yield "\u0000" + (CONTEXT_FULL if _context_full(e) else str(e))
        except Exception as e:  # noqa: BLE001 - the page shows it rather than a broken stream
            yield f"\u0000{e.__class__.__name__}: {e}"
    return StreamingResponse(gen(), media_type="text/plain; charset=utf-8",
                             headers={"X-Engine": engine.describe().encode("ascii", "replace").decode(), "X-Cloud": "1" if engine.is_cloud else "0", "X-Sources": sources,
                                      "Cache-Control": "no-store", "X-Accel-Buffering": "no"})


@app.post("/api/ai/test")
def ai_test(body: dict = Body(default={})):
    """Load the engine and get a one-line reply: proves the model really runs on this computer."""
    import time as _t
    settings = store.load_settings()
    engine, why = llm.resolve(settings, body.get("mode"))
    if not engine:
        raise HTTPException(409, why)
    t0 = _t.time()
    try:
        reply = llm.chat(engine, "Reply in five words or fewer.", "Say that the Saracen Bridge Studio engine is ready.",
                         settings=settings, max_tokens=24, temperature=0, think=False)
    except llm.EngineError as e:
        raise HTTPException(502, f"The engine did not answer: {e}") from e
    return {"ok": True, "reply": reply, "seconds": round(_t.time() - t0, 1), "engine": engine.describe()}


@app.post("/api/open-url")
def open_url(body: dict = Body(...)):
    """Web links from the page (e.g. "Get a Claude key") open in the default browser, not inside the Studio window."""
    url = str(body.get("url", ""))
    if not url.startswith(("https://", "http://")) or any(c in url for c in "\r\n\x00\"<>"):
        raise HTTPException(400, "Only web links open from here.")
    webbrowser.open(url)
    return {"opened": url}


@app.post("/api/external/{app_id}/launch")
def launch(app_id: str):
    apps = store.load_settings()["external_apps"]
    if app_id not in apps:
        raise HTTPException(404, "Unknown app")
    target = apps[app_id]["target"].strip()
    if not target:
        raise HTTPException(409, f"{apps[app_id]['name']} is not set up on this machine. Add its address or program path in Settings.")
    if target.startswith(("http://", "https://")):
        webbrowser.open(target)
    elif sys.platform == "win32":
        os.startfile(target)  # noqa: S606 - user-configured local program
    elif sys.platform == "darwin":
        subprocess.Popen(["open", target])          # an .app, or a program or file the user chose
    else:
        subprocess.Popen([target])
    return {"launched": target}


# ---------- history ----------
@app.get("/api/runs")
def runs(tool: str | None = None, q: str = "", limit: int = 200, offset: int = 0):
    refresh_library_once()
    return store.list_runs(tool, q, min(max(limit, 1), 1000), max(offset, 0))


BREAKDOWN_KEYS = ("format", "pages", "pages_estimated", "scene_count", "speaking_roles", "int", "ext", "day", "night")


def fresh_breakdown(tool: str, run_id: str) -> dict:
    """A script read by an older version of the reader is read again when it is next opened, re-dropped or written
    up, so a fix to the reader reaches scripts already in the Library (13 Oct: Tim's WEREWOLF draft showed 1 scene,
    not 133). A title the reader made up is replaced too; one the user gave is kept."""
    rec, folder = store.get_run(tool, run_id)
    b = rec.get("outputs", {}).get("breakdown")
    if not isinstance(b, dict) or b.get("parser", 1) >= script.PARSER_VERSION:
        return rec
    name = (rec.get("inputs") or {}).get("file", "")
    f = folder / Path(name).name
    if not name or not f.is_file():
        return rec
    try:
        res = script.parse(name, f.read_bytes())
    except Exception:  # noqa: BLE001 - keep the old reading rather than lose the run
        return rec
    summary = {k: res[k] for k in BREAKDOWN_KEYS} | {"locations": len(res["locations"])}
    title = res["title"] if rec.get("title") in (b.get("title"), script.clean_title(b.get("title") or "")) else None
    if "coverage" in rec.get("outputs", {}) and res["scene_count"] != b.get("scene_count"):
        summary["coverage_stale"] = True                  # written from the old reading: offer to write it again
    return store.update_run(tool, run_id, outputs={"breakdown": res}, summary=summary, title=title)


_REFRESHED = set()


def refresh_library_once():
    """Once per start, in the background: scripts read by an older reader are read again, so the Library list
    shows their corrected titles and counts without each one being opened first."""
    home = str(store.home())
    if home in _REFRESHED:
        return
    _REFRESHED.add(home)

    def work():
        for tool in ("coverage", "schedule", "brand", "bfi"):
            try:
                runs = store.list_runs(tool, limit=100000)["runs"]
            except Exception:  # noqa: BLE001 - best effort; opening a run refreshes it anyway
                continue
            for r in runs:
                try:                                  # one unreadable run no longer stops the rest (1.1.1)
                    fresh_breakdown(tool, r["id"])
                except Exception:  # noqa: BLE001
                    pass
    import threading
    threading.Thread(target=work, name="studio-reread", daemon=True).start()


@app.get("/api/runs/{tool}/{run_id}")
def run_detail(tool: str, run_id: str):
    return fresh_breakdown(tool, run_id)


# ---------- schedule & budget (1.0.4) ----------
@app.get("/api/tools/schedule/budget/options")
def budget_options():
    return {"jurisdictions": budget.jurisdictions(), "pages_per_day": budget.PAGES_PER_DAY, "sources": budget.SOURCES,
            "crew": [{"key": k, "count": n, "account": code, "prep": list(prep), "wrap": wrap, "assumed": src == "A"}
                     for k, _, n, code, prep, wrap, src in budget.CREW]}


@app.post("/api/tools/schedule/budget")
def budget_build(body: dict = Body(...)):
    """Schedule, day-out-of-days and a lean / base / conservative budget for a script already in the Library. The
    result is saved on that script's Library item, so the budget is there when it is opened again."""
    tool, run_id = body.get("tool") or "schedule", body.get("run_id")
    if not run_id:
        raise HTTPException(400, "Pick a script first.")
    try:
        rec = fresh_breakdown(tool, run_id)
    except (FileNotFoundError, KeyError) as e:
        raise HTTPException(404, "That script is no longer in the Library.") from e
    b = (rec.get("outputs") or {}).get("breakdown")
    if not isinstance(b, dict) or not b.get("scenes"):
        raise HTTPException(400, "This item has no script breakdown to schedule.")
    known = {j["jurisdiction"] for j in budget.jurisdictions()}
    if body.get("jurisdiction") not in known:
        raise HTTPException(400, f"Pick a jurisdiction from the list ({len(known)} have the Saracen Bridge rate cards).")
    use = body.get("use_order") or ("reasoned" if body.get("use_reasoned") else "first")
    outs = rec.get("outputs") or {}
    reasoned = outs.get("schedule_reasoned") if use == "reasoned" else outs.get("schedule_optimised") if use == "optimised" else None
    if reasoned and reasoned.get("scene_count") != len(b["scenes"]):
        reasoned = None                       # the script was read again since: the order no longer fits it
    if reasoned and use == "optimised":
        reasoned = {"order": reasoned["order"], "date": reasoned.get("date")}
    res = budget.build(b, jurisdiction=body["jurisdiction"], region=body.get("region"), tier=body.get("tier") or 2,
                       pages_per_day=body.get("pages_per_day"), inputs=body.get("inputs") or {},
                       elements=(rec.get("outputs") or {}).get("elements") if body.get("use_elements", True) else None,
                       reasoned=reasoned)
    res["settings"] = {k: body.get(k) for k in ("jurisdiction", "region", "tier", "pages_per_day", "inputs")}
    res["settings"]["use_order"] = use if reasoned else "first"
    res["settings"]["use_reasoned"] = bool(reasoned) and use == "reasoned"
    res["built"] = time.strftime("%Y-%m-%d %H:%M:%S")
    base = res["budget"]["base"]
    store.update_run(tool, run_id, outputs={"budget": res},
                     summary={"budget_total": base["known_total"], "budget_currency": res["currency"], "shoot_days": base["shoot_days"],
                              "budget_unknown": base["unknown_lines"]})
    return res


@app.get("/api/runs/{tool}/{run_id}/budget.xlsx")
def budget_xlsx(tool: str, run_id: str):
    rec, _ = store.get_run(tool, run_id)
    res = (rec.get("outputs") or {}).get("budget")
    if not res:
        raise HTTPException(404, "No budget has been built for this script yet.")
    data = budget.workbook(rec.get("title") or "Budget", res, (rec.get("outputs") or {}).get("elements") if res.get("elements") else None)
    name = re.sub(r"[^\w\- ]+", "", rec.get("title") or "Budget").strip() or "Budget"
    return Response(data, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": f'attachment; filename="{name} - Schedule and Budget.xlsx"'})


@app.get("/api/runs/{tool}/{run_id}/files/{name:path}")
def run_file(tool: str, run_id: str, name: str, inline: bool = False):
    _, d = store.get_run(tool, run_id)
    parts = [x for x in name.replace("\\", "/").split("/") if x and x not in (".", "..")]
    f = d.joinpath(*parts) if parts else d / "_"
    if not f.is_file() or d.resolve() not in f.resolve().parents:
        raise HTTPException(404)
    return FileResponse(f, filename=None if inline else f.name)


# ---------- scripts (coverage / schedule / brand intake) ----------
@app.post("/api/tools/script/intake")
async def script_intake(tool: str = Form("coverage"), files: list[UploadFile] = File(...)):
    out = []
    keys = BREAKDOWN_KEYS
    for f in files:
        data = await f.read()
        sha = hashlib.sha256(data).hexdigest()
        seen = store.find_by_hash(tool, sha)
        if seen:                 # the same file again: skip it, so a re-dropped folder resumes where it stopped
            rec = await run_in_threadpool(fresh_breakdown, tool, seen["id"])
            out.append({"file": f.filename, "run_id": seen["id"], "title": rec["title"], "duplicate": True, **rec["summary"]})
            continue
        try:                     # off the event loop: a scanned script is read by OCR page by page (1.0.6)
            res = await run_in_threadpool(script.parse, f.filename, data)
        except Exception as e:  # malformed file: report, continue the batch
            out.append({"file": f.filename, "error": f"Could not read this file: {e.__class__.__name__}"})
            continue
        summary = {k: res[k] for k in keys} | {"locations": len(res["locations"])}
        outputs = {"breakdown": res}
        if tool == "brand":      # the brands on the shortlist become this script's targets (changeable on the script's page)
            outputs["brand_targets"] = lookups.brands_by_id(store.load_shortlist())
            summary["brand_targets"] = len(outputs["brand_targets"])
        rec = store.save_run(tool, res["title"], {"file": f.filename, "bytes": len(data), "sha256": sha},
                             outputs, {f.filename: data}, summary=summary)
        out.append({"file": f.filename, "run_id": rec["id"], "title": res["title"], "duplicate": False,
                    "warnings": res["warnings"], **summary})
    return out


@app.get("/api/tools/script/ocr")
def script_ocr_progress():
    """Scanned scripts being read by OCR now, for the progress line while a drop is being read."""
    return {"available": ocr.available(), "reading": ocr.progress()}


# ---------- look books ----------
LB_FIELDS = ("title", "format", "logline", "synopsis", "cast", "director", "budget", "comparables", "notes", "opinion")


@app.post("/api/tools/lookbook/intake")
async def lookbook_intake(files: list[UploadFile] = File(...), title: str = Form(""), format: str = Form(""),
                          logline: str = Form(""), synopsis: str = Form(""), cast: str = Form(""), director: str = Form(""),
                          budget: str = Form(""), comparables: str = Form(""), notes: str = Form(""), opinion: str = Form("")):
    """One deck (a PDF, or images in page order) -> one Library item with its pages as images, ready to analyse."""
    got = [(f.filename or "deck", await f.read()) for f in files]
    got.sort(key=lambda x: x[0].lower()) if all(n.lower().endswith(lookbook.IMAGE_TYPES) for n, _ in got) else None
    sha = hashlib.sha256(b"".join(hashlib.sha256(d).digest() for _, d in got)).hexdigest()
    seen = store.find_by_hash("lookbook", sha)
    if seen:
        return {"run_id": seen["id"], "title": seen["title"], "duplicate": True, **seen["summary"]}
    try:
        deck = lookbook.pages(got)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    except Exception as e:  # noqa: BLE001 - a damaged file: say so plainly
        raise HTTPException(400, f"Could not read the deck ({e.__class__.__name__}).") from e
    info = {k: v.strip() for k, v in zip(LB_FIELDS, (title, format, logline, synopsis, cast, director, budget, comparables, notes, opinion)) if v.strip()}
    name = info.get("title") or script.title_from_filename(os.path.splitext(got[0][0])[0])
    info["title"] = name
    pages = [{"file": f"p{i:02d}.jpg", "text": p["text"]} for i, p in enumerate(deck, 1)]
    rec = store.save_run("lookbook", name, {"files": [n for n, _ in got], "sha256": sha, "info": info},
                         {"deck": {"pages": pages}}, dict(got), summary={"pages": len(deck)})
    _, folder = store.get_run("lookbook", rec["id"])
    (folder / "pages").mkdir(exist_ok=True)
    for meta, p in zip(pages, deck):
        (folder / "pages" / meta["file"]).write_bytes(p["image"])
    return {"run_id": rec["id"], "title": name, "duplicate": False, "pages": len(deck)}


@app.post("/api/tools/lookbook/analyse")
def lookbook_analyse(body: dict = Body(...)):
    settings = store.load_settings()
    mode = llm.mode_settings(settings, body.get("mode"))["mode"]
    engine, why = llm.resolve(settings, mode)
    if not engine:
        raise HTTPException(409, why)
    ok, why = llm.can_see(engine)
    if not ok:
        raise HTTPException(409, why)
    queued = []
    for rid in body.get("run_ids") or []:
        rec, _ = store.get_run("lookbook", rid)
        if isinstance(body.get("info"), dict):            # details added or corrected before analysing
            rec["inputs"]["info"] = {**rec["inputs"].get("info", {}), **{k: str(v).strip() for k, v in body["info"].items() if k in LB_FIELDS}}
            store.update_inputs("lookbook", rid, rec["inputs"])
        queued.append(store.enqueue("lookbook", "lookbook", rid, rec["title"], {"mode": mode}))
    jobs.ensure_worker()
    return {"queued": len(queued), "jobs": queued, "engine": engine.describe(), "mode": mode}


COVERAGE_WEIGHTS = coverage.WEIGHTS


@app.post("/api/tools/coverage/write")
def coverage_write(body: dict = Body(...)):
    """Queue coverage for scripts already in the Library. `run_ids`, or `missing: true` for every script without it."""
    tool = body.get("tool", "coverage")
    if body.get("missing"):
        ids = [r["id"] for r in store.list_runs(tool, limit=100000)["runs"] if "verdict" not in r["summary"]]
    else:
        ids = body.get("run_ids") or []
    settings = store.load_settings()
    mode = llm.mode_settings(settings, body.get("mode"))["mode"]
    engine, why = llm.resolve(settings, mode)
    if not engine:
        raise HTTPException(409, why)
    queued, gone = [], 0
    for rid in dict.fromkeys(ids):                    # the same script twice in one drop is queued once
        try:
            rec, _ = store.get_run(tool, rid)
        except FileNotFoundError:
            gone += 1
            continue
        if "breakdown" not in rec.get("outputs", {}):
            continue
        queued.append(store.enqueue("coverage", tool, rid, rec["title"], {"mode": mode}))
    if gone and not queued:
        raise HTTPException(404, "That script is no longer in the Library. Drop it in again.")
    jobs.ensure_worker()
    return {"queued": len(queued), "jobs": queued, "engine": engine.describe(), "mode": mode}


# ---------- schedule: element tagging (1.0.8) ----------
@app.post("/api/tools/schedule/elements")
def elements_tag(body: dict = Body(...)):
    """Queue element tagging for scripts in the Library (Scheduling & Budgeting)."""
    tool, ids = body.get("tool") or "schedule", body.get("run_ids") or []
    if not ids:
        raise HTTPException(400, "Pick a script first.")
    settings = store.load_settings()
    mode = llm.mode_settings(settings, body.get("mode"))["mode"]
    engine, why = llm.resolve(settings, mode)
    if not engine:
        raise HTTPException(409, why)
    queued = []
    for rid in ids:
        try:
            rec, _ = store.get_run(tool, rid)
        except FileNotFoundError as e:
            raise HTTPException(404, "That script is no longer in the Library.") from e
        if "breakdown" not in rec.get("outputs", {}):
            raise HTTPException(400, "This item has no script to read.")
        queued.append(store.enqueue("elements", tool, rid, rec["title"], {"mode": mode}))
    jobs.ensure_worker()
    return {"queued": len(queued), "jobs": queued, "engine": engine.describe(), "mode": mode}


# ---------- schedule: the optimised and the reasoned shooting order (1.1.6) ----------
@app.post("/api/tools/schedule/optimise")
def schedule_optimise(body: dict = Body(...)):
    """The Studio's own shooting order, by arithmetic (no AI): saved with the script."""
    tool, rid = body.get("tool") or "schedule", body.get("run_id")
    try:
        rec = fresh_breakdown(tool, rid)
    except (FileNotFoundError, KeyError, TypeError) as e:
        raise HTTPException(404, "That script is no longer in the Library.") from e
    b = (rec.get("outputs") or {}).get("breakdown") or {}
    if not b.get("scenes"):
        raise HTTPException(400, "This item has no script breakdown to schedule.")
    res = schedreason.optimise(b, sales._num(body.get("pages_per_day")) or None)
    store.update_run(tool, rid, outputs={"schedule_optimised": res})
    return res



@app.post("/api/tools/schedule/reason")
def schedule_reason(body: dict = Body(...)):
    """Queue the model's reasoned shooting order for a script (Deep reasoning unless Quick is asked for)."""
    tool, rid = body.get("tool") or "schedule", body.get("run_id")
    if not rid:
        raise HTTPException(400, "Pick a script first.")
    try:
        rec = fresh_breakdown(tool, rid)
    except (FileNotFoundError, KeyError) as e:
        raise HTTPException(404, "That script is no longer in the Library.") from e
    if not ((rec.get("outputs") or {}).get("breakdown") or {}).get("scenes"):
        raise HTTPException(400, "This item has no script breakdown to schedule.")
    settings = store.load_settings()
    mode = llm.mode_settings(settings, body.get("mode") or "deep")["mode"]
    engine, why = llm.resolve(settings, mode)
    if not engine:
        raise HTTPException(409, why)
    ppd = sales._num(body.get("pages_per_day")) or None
    job = store.enqueue("schedreason", tool, rid, rec["title"], {"mode": mode, "pages_per_day": ppd})
    jobs.ensure_worker()
    return {"queued": 1, "jobs": [job], "engine": engine.describe(), "mode": mode}


# ---------- Casting Director (1.1.6) ----------
def _casting_run(tool: str, run_id: str):
    if tool not in SCRIPT_TOOLS:
        raise HTTPException(404, "Unknown tool")
    try:
        fresh_breakdown(tool, run_id)
        rec, folder = store.get_run(tool, run_id)
    except FileNotFoundError as e:
        raise HTTPException(404, "That script is no longer in the Library. Drop it in again.") from e
    if not (rec.get("outputs", {}).get("breakdown") or {}).get("scenes"):
        raise HTTPException(400, "This item has no script breakdown to cast from.")
    return rec, folder


def _casting_prefill(rec: dict) -> dict:
    """The film's genre and budget (USD) from the latest Sales Estimates valuation with the same title, if there is one."""
    title = (rec.get("title") or "").strip().lower()
    for r in store.list_runs(tool="sales", limit=200)["runs"]:
        if (r.get("title") or "").strip().lower() != title:
            continue
        try:
            v, _ = store.get_run("sales", r["id"])
        except FileNotFoundError:
            continue
        intake = (v.get("inputs") or {}).get("intake") or {}
        out = {"from": r["title"]}
        if intake.get("genre"):
            out["genre"] = intake["genre"]
        amt, cur = sales._num(intake.get("budget")), intake.get("budget_currency") or "USD"
        rate = sales.fx_rates().get(cur)
        if amt and rate:
            out["budget_usd"] = round(amt * rate)
        return out
    return {}


@app.get("/api/casting/{tool}/{run_id}")
def casting_get(tool: str, run_id: str):
    """The script's roles, each with its reading and a shortlist from the Saracen Bridge actor database."""
    rec, folder = _casting_run(tool, run_id)
    out = rec["outputs"]
    read = out.get("casting_read") or {}
    reading = read.get("roles")
    if reading is None:                       # before the model has read the roles: the ages the script prints
        try:
            reading = casting.script_ages(rec["inputs"]["file"], (folder / rec["inputs"]["file"]).read_bytes(), out["breakdown"])
        except Exception:  # noqa: BLE001 - a script that can't be re-read still gets its roles
            reading = {}
    saved = out.get("casting") or {}
    pre = _casting_prefill(rec) if not saved else {}
    genre = saved.get("genre", pre.get("genre"))
    budget_usd = saved.get("budget_usd", pre.get("budget_usd"))
    res = casting.suggest(out["breakdown"], reading, genre=genre or None, budget_usd=budget_usd or None, edits=saved.get("edits"))
    res.update(title=rec["title"], prefill_from=pre.get("from"), read={k: read.get(k) for k in ("mode", "engine", "date", "seconds")} if read else None)
    return res


@app.put("/api/casting/{tool}/{run_id}")
def casting_put(tool: str, run_id: str, body: dict = Body(...)):
    """Keep the film's genre and budget for casting, and any correction to a role's reading or size of part."""
    rec, _ = _casting_run(tool, run_id)
    saved = dict(rec["outputs"].get("casting") or {})
    if "genre" in body:
        saved["genre"] = body["genre"] if body["genre"] in casting.GENRE_WORDS else None
    if "budget_usd" in body:
        b = sales._num(body["budget_usd"])
        saved["budget_usd"] = b if b and b > 0 else None
    edits = dict(saved.get("edits") or {})
    for name, e in (body.get("edits") or {}).items():
        clean = {}
        if e.get("gender") in casting.GENDERS or e.get("gender") == "Unknown":
            clean["gender"] = "Any" if e["gender"] == "Unknown" else e["gender"]
        if e.get("size") in casting.SIZES:
            clean["size"] = e["size"]
        for k in ("age_low", "age_high"):
            if e.get(k) not in (None, ""):
                clean[k] = max(0, min(100, int(float(e[k]))))
        if str(e.get("description") or "").strip():
            clean["description"] = str(e["description"]).strip()[:400]
        if clean:
            edits[name] = {**edits.get(name, {}), **clean}
        elif name in edits and e.get("reset"):
            edits.pop(name)
    saved["edits"] = edits
    store.update_run(tool, run_id, outputs={"casting": saved})
    return casting_get(tool, run_id)


@app.post("/api/casting/{tool}/{run_id}/read")
def casting_read(tool: str, run_id: str, body: dict = Body(default={})):
    """Queue the model's reading of the principal roles (gender, playing age, a one-line description)."""
    rec, _ = _casting_run(tool, run_id)
    settings = store.load_settings()
    mode = llm.mode_settings(settings, (body or {}).get("mode"))["mode"]
    engine, why = llm.resolve(settings, mode)
    if not engine:
        raise HTTPException(409, why)
    job = store.enqueue("casting", tool, run_id, rec["title"], {"mode": mode})
    jobs.ensure_worker()
    return {"queued": 1, "jobs": [job], "engine": engine.describe(), "mode": mode}


# ---------- brand: scene-by-scene opportunities (1.0.7) ----------
@app.get("/api/tools/brand/spot/options")
def brand_spot_options():
    return {"categories": brandspot.categories(), "ratings": brandspot.RATINGS, "placements": brandspot.PLACEMENTS,
            "groups": brandspot.GROUPS}


@app.post("/api/tools/brand/spot")
def brand_spot(body: dict = Body(...)):
    """Queue scene-by-scene opportunity spotting for brand scripts in the Library."""
    ids = body.get("run_ids") or []
    if not ids:
        raise HTTPException(400, "Pick a script first.")
    settings = store.load_settings()
    mode = llm.mode_settings(settings, body.get("mode"))["mode"]
    engine, why = llm.resolve(settings, mode)
    if not engine:
        raise HTTPException(409, why)
    raw = body.get("options") or {}
    cats = set(brandspot.categories())
    opts = {"avoid": sorted(c for c in raw.get("avoid") or [] if c in cats),
            "rating": raw.get("rating") if raw.get("rating") in brandspot.RATINGS else "Not decided",
            "withhold_title": bool(raw.get("withhold_title"))}
    queued = []
    for rid in ids:
        try:
            rec, _ = store.get_run("brand", rid)
        except FileNotFoundError as e:
            raise HTTPException(404, "That script is no longer in the Library.") from e
        if "breakdown" not in rec.get("outputs", {}):
            raise HTTPException(400, "This item has no script to read.")
        queued.append(store.enqueue("brandspot", "brand", rid, rec["title"], {"mode": mode, "brand": opts}))
    jobs.ensure_worker()
    return {"queued": len(queued), "jobs": queued, "engine": engine.describe(), "mode": mode}


@app.get("/api/runs/brand/{run_id}/opportunities.xlsx")
def brand_spot_xlsx(run_id: str):
    try:
        rec, _ = store.get_run("brand", run_id)
    except FileNotFoundError as e:
        raise HTTPException(404, "That script is no longer in the Library.") from e
    res = (rec.get("outputs") or {}).get("brand_spotting")
    if not res:
        raise HTTPException(404, "No opportunities have been spotted for this script yet.")
    name = re.sub(r"[^\w\- ]+", "", rec.get("title") or "Brand").strip() or "Brand"
    return Response(brandspot.workbook(res), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": f'attachment; filename="{name} - Brand Opportunities.xlsx"'})


@app.get("/api/jobs")
def jobs_list(kind: str | None = None, limit: int = 200):
    jobs.ensure_worker()
    return store.list_jobs(kind, min(max(limit, 1), 2000))


@app.post("/api/jobs/{job_id}/cancel")
def job_cancel(job_id: int):
    j = store.cancel_job(job_id)
    if not j:
        raise HTTPException(404, "No such job")
    return j


@app.post("/api/jobs/retry")
def jobs_retry(body: dict = Body(default={})):
    """Re-queue failed (and optionally cancelled) jobs."""
    statuses = ["error"] + (["cancelled"] if body.get("cancelled") else [])
    n = 0
    for j in store.list_jobs(body.get("kind"), 100000)["jobs"]:
        if j["status"] in statuses:
            store.enqueue(j["kind"], j["tool"], j["run_id"], j["title"], json.loads(j.get("options") or "{}"))
            n += 1
    jobs.ensure_worker()
    return {"requeued": n}


@app.post("/api/jobs/clear")
def jobs_clear(body: dict = Body(default={})):
    """Clear failed jobs off the queue: one (id) or all of a kind. done=true also clears a finished one."""
    jid = body.get("id")
    statuses = ("error", "cancelled", "done") if (jid is not None and body.get("done")) else ("error", "cancelled")
    return {"cleared": store.clear_jobs(body.get("kind"), int(jid) if jid is not None else None, statuses)}


@app.get("/api/tools/coverage/weights")
def coverage_weights():
    return COVERAGE_WEIGHTS


@app.post("/api/tools/coverage/score")
def coverage_score(scores: dict = Body(...)):
    missing = [k for k in COVERAGE_WEIGHTS if scores.get(k) in (None, "")]
    if missing:
        return {"composite": None, "missing": missing}
    rows = [{"category": k, "score": float(scores[k]), "weight": w, "weighted": float(scores[k]) * w} for k, w in COVERAGE_WEIGHTS.items()]
    return {"rows": rows, "composite": round(sum(r["weighted"] for r in rows), 2), "missing": [],
            "note": "Commercial Readiness (1–100) and the Recommend/Consider/Pass cut-offs are not defined in the Saracen Bridge spec (register G-02)."}


# ---------- incentives ----------
@app.get("/api/tools/incentives/programmes")
def incentive_programmes(country: str = "", all: bool = False):
    return lookups.programmes(country, include_unavailable=all)


@app.get("/api/tools/incentives/producer-fees")
def producer_fee_routes():
    """Saracen Bridge's producer-fee allowance table (1.2.0): the routes and the method notes."""
    t = producerfee.table()
    return {"routes": producerfee.summary(), "notes": t["notes"], "checked": t["checked"], "source": t["source"]}


@app.post("/api/tools/incentives/producer-fee")
def producer_fee_check(body: dict = Body(...)):
    try:
        return producerfee.assess(body.get("route", ""), body)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e


def _route_fees(r: dict, pf: dict | None) -> dict | None:
    """The producer-fee allowance for one incentive route, from the page's fees and the route's own figures."""
    if not pf or not (pf.get("fees") and any(f.get("amount") not in (None, "") for f in pf["fees"])):
        return None
    route = producerfee.for_programme(r["programme_id"])
    if not route:
        return {"route": None, "status": "uncovered", "status_label": "Not in Saracen Bridge's producer-fee table"}
    rule = refdata.programme_rule(r["programme_id"])
    ctx = dict(pf, local_spend=r.get("qualifying_spend"),
               worldwide_budget=r.get("project_cost") if r.get("project_cost") is not None else pf.get("worldwide_budget"),
               incentive_rate=rule.get("rate_1"))
    out = producerfee.assess(route["id"], ctx)
    out["currency"] = rule["programme_currency"]          # the route's figures are in the programme's currency
    return out


@app.post("/api/tools/incentives/calc")
def incentive_calc(body: dict = Body(...)):
    routes = body.get("routes", [])
    selected = {r["programme_id"] for r in routes}
    results = []
    unknown = [r.get("programme_id") for r in routes if not refdata.has_programme(r.get("programme_id"))]
    if unknown:
        raise HTTPException(400, f"Unknown programme: {', '.join(map(str, unknown))}. Pick it from the list.")
    pf = body.get("producer_fees") or None
    for r in routes:
        fees = _route_fees(r, pf)
        spend, note = r.get("qualifying_spend"), None
        if r.get("fees_in_spend") and fees and spend is not None:
            if fees.get("excluded") is not None:
                spend = max(spend - fees["excluded"], 0.0)
                if fees["excluded"]:
                    note = (f"Producer and EP fees above the allowance ({fees['excluded']:,.0f}) are kept out of the "
                            f"qualifying spend (Saracen Bridge producer-fee table).")
        res = incentive.calculate(r["programme_id"], spend, project_cost=r.get("project_cost"),
                                  eligibility=r.get("eligibility", "Unknown"), selected=selected)
        if note:
            res.reasons.append(note)
        if r.get("fees_in_spend") and fees and fees.get("excluded") is None:
            res._downgrade("PRELIMINARY", "Producer and EP fees are in the spend, but their allowance isn't settled: "
                           + ("; ".join(fees.get("needs", []) + fees.get("confirm", [])) or fees.get("status_label", "")))
        rule = refdata.programme_rule(r["programme_id"])
        results.append(asdict(res) | {"programme_name": rule["programme_name"], "jurisdiction": rule["jurisdiction"],
                                      "last_verified": rule["last_verified"], "official_source": rule["official_source"],
                                      "producer_fee": fees})
    if body.get("save", True) and results:
        store.save_run("incentives", body.get("title") or ", ".join(sorted(selected)), body, {"results": results})
    return results


# ---------- BFI ----------
@app.get("/api/tools/bfi/criteria")
def bfi_criteria():
    return bfi.criteria()


SCRIPT_TOOLS = ("coverage", "schedule", "brand")


@app.post("/api/tools/bfi/read")
def bfi_read(body: dict = Body(...)):
    """Queue the Section A script read for a script in the Library (1.0.8)."""
    tool, rid = body.get("tool"), body.get("run_id")
    if tool not in SCRIPT_TOOLS or not rid:
        raise HTTPException(400, "Pick a script from the Library first.")
    try:
        rec, _ = store.get_run(tool, rid)
    except FileNotFoundError as e:
        raise HTTPException(404, "That script is no longer in the Library.") from e
    if "breakdown" not in rec.get("outputs", {}):
        raise HTTPException(400, "This item has no script to read.")
    settings = store.load_settings()
    mode = llm.mode_settings(settings, body.get("mode"))["mode"]
    engine, why = llm.resolve(settings, mode)
    if not engine:
        raise HTTPException(409, why)
    job = store.enqueue("bfiread", tool, rid, rec["title"], {"mode": mode})
    jobs.ensure_worker()
    return {"queued": 1, "jobs": [job], "engine": engine.describe(), "mode": mode}


@app.get("/api/runs/{tool}/{run_id}/bfi_pack.xlsx")
def bfi_pack_xlsx(tool: str, run_id: str):
    try:
        rec, _ = store.get_run(tool, run_id)
    except FileNotFoundError as e:
        raise HTTPException(404, "That script is no longer in the Library.") from e
    res = (rec.get("outputs") or {}).get("bfi_read")
    if not res:
        raise HTTPException(404, "This script hasn't been read for the Cultural Test yet.")
    name = re.sub(r"[^\w\- ]+", "", rec.get("title") or "BFI").strip() or "BFI"
    return Response(bfiread.workbook(res), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": f'attachment; filename="{name} - BFI Section A Answer Pack.xlsx"'})


@app.post("/api/tools/bfi/assess")
def bfi_assess(body: dict = Body(...)):
    res = bfi.assess(body.get("proposed", {}), body.get("conservative", {}))
    if body.get("save", True):
        store.save_run("bfi", body.get("title") or "Cultural Test", body, res)
    return res


# ---------- finance ----------
@app.post("/api/tools/finance/plan")
def finance_plan(body: dict = Body(...)):
    gross = float(body["gross_budget"])
    sources = [finance.Source(s.get("id") or f"s{i}", s["name"], None if s.get("amount") in (None, "") else float(s["amount"]),
                              s.get("status", "Missing"), cash=s.get("cash", True), parent=s.get("parent") or None,
                              is_debt=s.get("is_debt", False)) for i, s in enumerate(body.get("sources", []))]
    dc = finance.double_count_errors(sources)
    clean = [s for s in sources if s.id not in {x.parent for x in sources if x.parent}] if dc else sources
    debt = finance.residual_debt(gross, clean)
    plan = finance.reconcile(gross, clean)
    bankable = sum(s.amount or 0 for s in clean if s.status == "Confirmed cash")
    out = {"gross_budget": gross, "currency": body.get("currency", ""), "sources_total": plan.permanent_sources,
           "gap": plan.gap, "residual_debt_needed": debt, "debt_pct": plan.debt_pct, "bankable": bankable,
           "double_count": dc, "errors": plan.errors, "preliminary": plan.preliminary}
    if body.get("save", True):
        store.save_run("finance", body.get("title") or "Finance plan", body, out)
    return out


@app.post("/api/tools/finance/termsheet")
def finance_termsheet(file: UploadFile = File(...), mode: str = Form("")):
    """Read a term sheet into proposed finance-plan sources (1.0.8). Runs off the event loop (a plain def)."""
    data = file.file.read()
    settings = store.load_settings()
    try:
        res = termsheet.read(file.filename or "term sheet", data, settings, mode or None)
    except llm.EngineError as e:
        raise HTTPException(409, str(e)) from e
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    rec = store.save_run("finance", f"Term sheet: {Path(file.filename or 'term sheet').stem}"[:80],
                         {"file": file.filename, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()},
                         {"termsheet": res}, {file.filename or "termsheet": data},
                         summary={"instruments": len(res["rows"])})
    return res | {"run_id": rec["id"]}


@app.get("/api/tools/finance/example")
def finance_example():
    return json.loads((refdata.app_root() / "projects" / "shade_finance_example.json").read_text(encoding="utf-8"))


# ---------- greenlight ----------
@app.post("/api/tools/greenlight/decide")
def greenlight_decide(b: dict = Body(...)):
    res = greenlight.decide(float(b["overall"]), float(b["finance"]), float(b["legal"]), float(b["bond_insurance"]),
                            float(b["production_delivery"]), critical_blockers=int(b.get("critical_blockers", 0)),
                            funding_gap=bool(b.get("funding_gap")), signoffs_approved=bool(b.get("signoffs_approved")),
                            ready_gates_outstanding=int(b.get("ready_gates_outstanding", 0)),
                            cures_owned_and_timed=bool(b.get("cures_owned_and_timed")))
    if b.get("save", True):
        store.save_run("greenlight", b.get("title") or "Greenlight decision", b, res)
    return res


# ---------- agreement ----------
@app.get("/api/tools/agreement/blank")
def agreement_blank():
    return FileResponse(agreement.BLANK_WORKBOOK, filename="TKE_SB_Project_Input_Workbook.xlsx")


@app.post("/api/tools/agreement/build")
async def agreement_build(file: UploadFile = File(...), draft_name: str = Form("Term_Sheet_DRAFT_01"),
                          include_proposed: bool = Form(False)):
    data = await file.read()
    res = agreement.build(data, draft_name, include_proposed)
    if not res["ok"]:
        return {"ok": False, "error": res["error"], "problems": res.get("problems", []), "validation": res.get("validation", "")}
    r = res["result"]
    summary = {"technical_validation_passed": r.get("technical_validation_passed"), "errors": r.get("errors", []),
               "warnings": r.get("warnings", []), "population": r.get("population")}
    rec = store.save_run("agreement", draft_name, {"file": file.filename, "include_proposed": include_proposed}, summary, res["files"])
    return {"ok": True, "run_id": rec["id"], "files": rec["files"], **summary}


# ---------- sales: an existing sales estimate, read and set beside the valuation (1.1.6) ----------
@app.post("/api/tools/sales/estimate/read")
async def sales_estimate_read(file: UploadFile = File(...)):
    """Read a sales company's estimate (spreadsheet, CSV, Word or PDF) into the workbook's territories, for checking."""
    data = await file.read()
    try:
        return estimates.read(file.filename or "estimate", data)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    except Exception as e:  # noqa: BLE001 - a file we can't parse is the user's to see, not a server fault
        raise HTTPException(400, f"Couldn't read {file.filename}: {e.__class__.__name__}. Send it as a spreadsheet or CSV.") from e


def _estimate_view(rec: dict) -> dict:
    est = (rec.get("outputs") or {}).get("existing_estimate")
    if not est:
        return {"estimate": None, "comparison": []}
    rate = sales.fx_rates().get(est.get("currency") or "USD") or 1.0
    return {"estimate": est, "comparison": estimates.compare(est, (rec.get("outputs") or {}).get("valuation") or {}, rate), "usd_per_unit": rate}


@app.get("/api/tools/sales/{run_id}/estimate")
def sales_estimate_get(run_id: str):
    try:
        rec, _ = store.get_run("sales", run_id)
    except FileNotFoundError as e:
        raise HTTPException(404, "That valuation is no longer in the Library.") from e
    return _estimate_view(rec)


@app.put("/api/tools/sales/{run_id}/estimate")
def sales_estimate_put(run_id: str, body: dict = Body(...)):
    """Keep the estimate (as checked) with the valuation; null removes it."""
    try:
        store.get_run("sales", run_id)
    except FileNotFoundError as e:
        raise HTTPException(404, "Value the film first, then add the existing estimate to it.") from e
    est = body.get("estimate")
    if est:
        rows = [{"territory": x["territory"], "as_written": str(x.get("as_written") or "")[:80],
                 **{k: sales._num(x.get(k)) for k in ("ask", "take", "floor")}} for x in est.get("rows") or [] if x.get("territory")]
        est = {"file": str(est.get("file") or "")[:200], "company": str(est.get("company") or "")[:120], "date": str(est.get("date") or "")[:10],
               "currency": est.get("currency") if est.get("currency") in sales.fx_rates() else "USD", "rows": rows,
               "total": {k: sum(x[k] or 0 for x in rows) for k in ("ask", "take")}, "added": time.strftime("%Y-%m-%d")}
    store.update_run("sales", run_id, outputs={"existing_estimate": est or None})
    rec, _ = store.get_run("sales", run_id)
    return _estimate_view(rec)


# ---------- sales valuation: Jon's engine (1.0.5) ----------
_SALES_WARM = threading.Event()


def _warm_sales():
    if not _SALES_WARM.is_set():
        _SALES_WARM.set()
        threading.Thread(target=lambda: sales.evaluate({}), daemon=True, name="sales-warm").start()


@app.get("/api/tools/sales/engine/options")
def sales_options():
    """Jon's lists and the engine's input fields. Also starts compiling his workbook in the background, so the first
    valuation doesn't wait for it."""
    _warm_sales()
    lists = sales.lists()
    return {"lists": lists, "intake": [{"key": k, "label": label, "required": k not in sales.OPTIONAL, "numeric": k in sales.NUMERIC}
                                       for k, _, label in sales.INTAKE if k not in sales.HIDDEN],
            "choices": sales.CHOICES,
            "attachment": sales.ATTACHMENT, "package_factors": [{"key": k, "label": label} for k, _, label in sales.PACKAGE_FACTORS],
            "selection_factors": sales.SELECTION_FACTORS, "fx": sales.fx_rates(), "territories": lists["territories"],
            "genres": GENRES["genres"]}


@app.get("/api/tools/sales/engine/prefill")
def sales_prefill(tool: str, run_id: str):
    """Intake fields a script already in the Library can give: its title; from a schedule-and-budget, the budget; and
    from its coverage (Tim, 22 Oct), the logline and synopsis, taken from this item or the same script's coverage."""
    rec, _ = store.get_run(tool, run_id)
    out = {"title": rec.get("title") or ""}
    bud = (rec.get("outputs") or {}).get("budget")
    if bud:
        out["budget"] = round(bud["budget"]["base"]["known_total"])
        out["budget_currency"] = bud.get("currency") or ""
    cov = (rec.get("outputs") or {}).get("coverage")
    sha = (rec.get("inputs") or {}).get("sha256")
    if not cov and sha:                                    # the same file, read with coverage under another tool
        for t in ("coverage", "brand", "schedule"):
            seen = store.find_by_hash(t, sha)
            if seen:
                other, _ = store.get_run(t, seen["id"])
                cov = (other.get("outputs") or {}).get("coverage")
                if cov:
                    break
    story = ((cov or {}).get("sections") or {}).get("story") or {}
    synopsis = story.get("synopsis") or []
    synopsis = "\n\n".join(synopsis) if isinstance(synopsis, list) else str(synopsis)
    if story.get("logline") or synopsis:
        out["logline"] = "\n\n".join(x for x in (story.get("logline") or "", synopsis) if x)
        out["logline_from"] = "coverage"
    return out


@app.post("/api/tools/sales/value")
def sales_value(body: dict = Body(...)):
    """Run Jon's Sales Valuation Engine on a project and save it in the Library (a new item, or the one given)."""
    project = body.get("project") or {}
    title = ((project.get("intake") or {}).get("title") or "").strip() or "Untitled valuation"
    try:
        res = sales.evaluate(project)
    except FileNotFoundError as e:
        raise HTTPException(500, "The Saracen Bridge Sales Valuation Engine workbook is missing from this installation. Reinstall the Studio.") from e
    summary = {"ask": res["summary"]["ask"], "expected": res["summary"]["expected"], "take": res["summary"]["take"],
               "net_producer_receipts": res["summary"]["net_producer_receipts"],
               "valued": sum(1 for t in res["territories"] if t["status"] == "Complete")}
    run_id = body.get("run_id")
    if run_id:
        try:
            store.update_inputs("sales", run_id, project)
            store.update_run("sales", run_id, outputs={"valuation": res}, summary=summary, title=title)
        except (FileNotFoundError, KeyError):
            run_id = None
    if not run_id:
        run_id = store.save_run("sales", title, project, {"valuation": res}, summary=summary)["id"]
    return {"run_id": run_id, "title": title, **res}


@app.get("/api/runs/sales/{run_id}/engine.xlsx")
def sales_workbook(run_id: str):
    rec, _ = store.get_run("sales", run_id)
    data = sales.workbook_bytes(rec.get("inputs") or {})
    name = re.sub(r"[^\w\- ]+", "", rec.get("title") or "Valuation").strip() or "Valuation"
    return Response(data, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    headers={"Content-Disposition": f'attachment; filename="{name} - Sales Valuation Engine v4.1.xlsx"'})


# ---------- lookups ----------
@app.get("/api/lookup/actors")
def lk_actors(q: str = "", limit: int = 50):
    return lookups.actors(q, max(1, min(limit, 200)))


@app.get("/api/lookup/directors")
def lk_directors(q: str = "", limit: int = 50):
    return lookups.directors(q, max(1, min(limit, 200)))


@app.get("/api/lookup/actor")
def lk_actor(name: str):
    r = lookups.actor(name)
    if not r:
        raise HTTPException(404, "Not in the actor database.")
    return r


@app.get("/api/lookup/director")
def lk_director(id: str):
    r = lookups.director(id)
    if not r:
        raise HTTPException(404, "Not in the director database.")
    return r


@app.get("/api/brand/shortlist")
def brand_shortlist():
    return {"brands": lookups.brands_by_id(store.load_shortlist())}


@app.put("/api/brand/shortlist")
def brand_shortlist_save(body: dict = Body(...)):
    ids = store.save_shortlist([str(i) for i in (body.get("ids") or [])])
    return {"brands": lookups.brands_by_id(ids)}


BRAND_CSV = (("brand_name", "Brand"), ("parent_company", "Parent company"), ("category", "Category"), ("subcategory", "Subcategory"),
             ("hq_country", "HQ"), ("priority", "Priority"), ("evidence_statement", "Film-placement evidence"), ("evidence_year", "Evidence year"))


@app.get("/api/brand/shortlist.csv")
def brand_shortlist_csv(run: str = ""):
    """The shortlist (or one script's brand targets) as a spreadsheet-ready CSV."""
    if run:
        rec, _ = store.get_run("brand", run)
        rows = rec.get("outputs", {}).get("brand_targets") or []
        name = f"Brand targets - {rec['title']}"
    else:
        rows, name = lookups.brands_by_id(store.load_shortlist()), "Brand shortlist"
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow([h for _, h in BRAND_CSV])
    for r in rows:
        w.writerow([r.get(k, "") if r.get(k) is not None else "" for k, _ in BRAND_CSV])
    safe = re.sub(r"[^A-Za-z0-9 ._-]+", "", name).strip() or "Brand shortlist"
    return Response("\ufeff" + buf.getvalue(), media_type="text/csv; charset=utf-8",
                    headers={"Content-Disposition": f'attachment; filename="{safe}.csv"'})


@app.put("/api/runs/brand/{run_id}/targets")
def brand_targets(run_id: str, body: dict = Body(...)):
    """The brands aimed at for this script (from the shortlist)."""
    store.get_run("brand", run_id)
    rows = lookups.brands_by_id([str(i) for i in (body.get("ids") or [])])
    rec = store.update_run("brand", run_id, outputs={"brand_targets": rows}, summary={"brand_targets": len(rows)})
    return {"brand_targets": rec["outputs"]["brand_targets"]}


@app.get("/api/lookup/brands")
def lk_brands(q: str = "", category: str = ""):
    return lookups.brands(q, category)


@app.get("/api/lookup/rates")
def lk_rates(jurisdiction: str = "United Kingdom", q: str = "", production_type: str = ""):
    return {"jurisdictions": lookups.rate_jurisdictions(), **lookups.crew_rates(jurisdiction, q, production_type)}


@app.get("/api/reference")
def reference():
    return refdata.rows("SELECT table_name, row_count, sheet, source_file FROM _provenance ORDER BY table_name")


# ---------- UI ----------
@app.get("/favicon.ico", status_code=204)
def favicon():
    return Response(status_code=204)


# ---------- sales agents: Jon's scoring specification v1.0 (22 Oct 2026) ----------
@app.get("/api/agents")
def agents_register():
    return agents.register() | {"genres": [{"id": g["id"], "name": g["name"]} for g in agents.genres()],
                                "fits": agents.FIT_LEVELS, "fit_labels": agents.FIT_LABEL, "scopes": agents.SCOPE_LABEL}


@app.get("/api/agents/history")
def agents_history():
    return agents.history()


@app.put("/api/agents/{agent_id}")
def agents_edit(agent_id: str, body: dict = Body(...)):
    try:
        return agents.edit(agent_id, {k: body[k] for k in agents.EDITABLE if k in body}, body.get("editor") or "", body.get("reason") or "")
    except KeyError as e:
        raise HTTPException(404, "No such company in the register.") from e
    except ValueError as e:
        raise HTTPException(400, str(e)) from e


def _project_or_404(project: str | None):
    if not project:
        return None
    try:
        store.get_run("sales", project)
    except FileNotFoundError as e:
        raise HTTPException(404, "That valuation is no longer in the Library.") from e
    return project


@app.get("/api/agents/compare")
def agents_compare(project: str | None = None, scope: str = "INTERNATIONAL_SALES"):
    if scope not in agents.SCOPES:
        raise HTTPException(400, "Mandate is international sales or distribution.")
    return agents.compare(_project_or_404(project), scope)


@app.get("/api/agents/compare.csv")
def agents_compare_csv(project: str | None = None, scope: str = "INTERNATIONAL_SALES"):
    c = agents.snapshot(_project_or_404(project), scope) if project else agents.compare(None, scope)
    name = re.sub(r"[^\w\- ]+", "", ((c.get("project") or {}).get("title") or "Sales agents")).strip() or "Sales agents"
    return Response(agents.csv_bytes(c), media_type="text/csv",
                    headers={"Content-Disposition": f'attachment; filename="{name} - Sales agents.csv"'})


@app.post("/api/agents/fit")
def agents_fit(body: dict = Body(...)):
    _project_or_404(body.get("project"))
    try:
        return agents.assess(body.get("agent") or "", body["project"], body.get("genre") or "", body.get("fit") or "",
                             body.get("rationale") or "", body.get("evidence") or "", body.get("assessor") or "",
                             body.get("evidence_status") or "PROVISIONAL", body.get("mandate") or "", bool(body.get("save_mapping")))
    except KeyError as e:
        raise HTTPException(404, "No such company in the register.") from e
    except ValueError as e:
        raise HTTPException(400, str(e)) from e


@app.put("/api/agents/project/{project}")
def agents_project_genres(project: str, body: dict = Body(...)):
    """The project's two scoring genres, set from the Sales Agents page: they are the valuation's own (Jon: one
    classification for every company; changing it is a new revision and every result is recalculated)."""
    _project_or_404(project)
    p, s = agents.genre_id(body.get("primary")), agents.genre_id(body.get("secondary")) if body.get("secondary") else None
    if not p:
        raise HTTPException(400, "Choose the primary genre.")
    if s == p:
        raise HTTPException(400, "The secondary genre must differ from the primary.")
    rec, _ = store.get_run("sales", project)
    inputs = rec.get("inputs") or {}
    intake = inputs.setdefault("intake", {})
    intake["genre"], intake["secondary_genre"] = agents.genre_name(p), agents.genre_name(s) if s else None
    if intake.get("subgenre") and intake["subgenre"] not in next(g["subgenres"] for g in GENRES["genres"] if g["genre"] == intake["genre"]):
        intake["subgenre"] = None
    store.update_inputs("sales", project, inputs)
    return agents.project(project)


@app.post("/api/agents/suggest")
def agents_suggest(body: dict = Body(...)):
    project = _project_or_404(body.get("project"))
    if not project:
        raise HTTPException(400, "Choose a valuation first.")
    settings = store.load_settings()
    mode = llm.mode_settings(settings, body.get("mode"))["mode"]
    engine, why = llm.resolve(settings, mode)
    if not engine:
        raise HTTPException(409, why)
    try:
        done = agents.suggest(project, engine, settings)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    except llm.EngineError as e:
        raise HTTPException(502, f"The AI engine couldn't assess the fits: {e}") from e
    return {"assessed": len(done), "fits": done}


from .room.routes import router as _room_router   # noqa: E402 - the Room (1.0.8)
app.include_router(_room_router)


@app.on_event("startup")
def _room_host_autostart():
    """If this computer hosts a Room (whoever starts a project hosts it), bring it up so the team can connect (1.1.0)."""
    from .room import host as _room_host
    threading.Thread(target=_room_host.autostart, daemon=True, name="room-host-start").start()


@app.get("/")
def index():
    return FileResponse(UI_DIR / "index.html")


app.mount("/ui", StaticFiles(directory=UI_DIR), name="ui")
