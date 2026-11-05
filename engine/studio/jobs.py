"""Background worker: drains the job queue one job at a time (the model is the bottleneck, so one at a time).

Jobs live in library.db, so a queue of thousands survives closing the app or a crash: on start, anything left
'running' goes back to the front of the queue.
"""
from __future__ import annotations

import threading
import traceback

from . import bfiread, brandspot, casting, coverage, elements, lookbook, report, schedreason, store

_lock = threading.Lock()
_thread: threading.Thread | None = None
_stop = threading.Event()
_wake = threading.Event()
POLL = 2.0


def ensure_worker(delay: float = 0) -> None:
    """Start the worker. At launch the Studio passes a delay (1.2.2): a queue left from the last session waits that long,
    so the window has opened before the engine loads (Jon's 8 GB Mac stayed black while it loaded at once). A job
    added from the interface wakes the worker straight away."""
    global _thread
    with _lock:
        if _thread and _thread.is_alive():
            _wake.set()
            return
        store.requeue_interrupted()
        _stop.clear()
        _wake.clear()
        _thread = threading.Thread(target=_loop, args=(delay,), name="studio-jobs", daemon=True)
        _thread.start()


def stop_worker(timeout: float = 10) -> None:
    """Stop after the current job (used on shutdown and between tests)."""
    _stop.set()
    if _thread:
        _thread.join(timeout)


def _loop(delay: float = 0) -> None:
    if delay:
        _wake.wait(delay)
    while not _stop.is_set():
        job = store.claim_job()
        if not job:
            _stop.wait(POLL)
            continue
        try:
            HANDLERS[job["kind"]](job)
            if store.get_job(job["id"])["status"] == "running":
                store.set_job(job["id"], status="done", progress="Done")
        except InterruptedError:
            store.set_job(job["id"], status="cancelled", progress="Cancelled")
        except Exception as e:  # noqa: BLE001 - one bad script must not stop the queue
            store.set_job(job["id"], status="error", error=f"{e.__class__.__name__}: {e}"[:500])
            traceback.print_exc()


def run_coverage(job: dict) -> None:
    from .server import fresh_breakdown                 # coverage is written from the current reading of the script
    fresh_breakdown(job["tool"], job["run_id"])
    rec, folder = store.get_run(job["tool"], job["run_id"])
    name = rec["inputs"]["file"]
    data = (folder / name).read_bytes()
    breakdown = rec["outputs"]["breakdown"]
    jid = job["id"]
    result = coverage.write(name, data, breakdown, store.load_settings(),
                            progress=lambda m: store.set_job(jid, progress=m),
                            cancelled=lambda: store.get_job(jid)["status"] == "cancelled",
                            mode=(job.get("options") or {}).get("mode"))
    docx_name = f"{rec['title'][:60]} - Script Coverage.docx".replace("/", "-").replace("\\", "-")
    files = {"coverage.json": __import__("json").dumps(result, indent=1, ensure_ascii=False).encode("utf-8")}
    try:
        files[docx_name] = report.coverage_docx(result)
    except Exception as e:  # noqa: BLE001 - the coverage itself is kept even if the document fails
        result["checks"].append(f"The Word report could not be built ({e.__class__.__name__}: {e}).")
    store.update_run(job["tool"], job["run_id"], outputs={"coverage": result}, files=files,
                     summary={"verdict": result["verdict"], "composite": result["composite"],
                              "readiness": result["commercial_readiness"], "coverage_stale": False})


def run_lookbook(job: dict) -> None:
    rec, folder = store.get_run(job["tool"], job["run_id"])
    deck = [{"image": (folder / "pages" / p["file"]).read_bytes(), "text": p.get("text", "")} for p in rec["outputs"]["deck"]["pages"]]
    jid = job["id"]
    result = lookbook.write(deck, rec["inputs"].get("info") or {}, store.load_settings(),
                            progress=lambda m: store.set_job(jid, progress=m),
                            cancelled=lambda: store.get_job(jid)["status"] == "cancelled",
                            mode=(job.get("options") or {}).get("mode"))
    docx_name = f"{rec['title'][:60]} - Look Book Analysis.docx".replace("/", "-").replace("\\", "-")
    files = {"lookbook.json": __import__("json").dumps(result, indent=1, ensure_ascii=False).encode("utf-8")}
    try:
        files[docx_name] = report.lookbook_docx(result)
    except Exception as e:  # noqa: BLE001 - the analysis is kept even if the document fails
        result["checks"].append(f"The Word report could not be built ({e.__class__.__name__}: {e}).")
    store.update_run(job["tool"], job["run_id"], outputs={"lookbook": result}, files=files,
                     summary={"verdict": result["verdict"], "score": result["final_score"], "pages": result["pages"]})


def film_facts(rec: dict) -> dict:
    """What the Studio already knows about the film: the logline from its coverage, if written."""
    sha = (rec.get("inputs") or {}).get("sha256")
    for tool in ("coverage", rec.get("tool")):
        hit = store.find_by_hash(tool, sha) if sha and tool else None
        if hit:
            cov = (store.get_run(tool, hit["id"])[0].get("outputs") or {}).get("coverage") or {}
            story = (cov.get("sections") or {}).get("story") or {}
            creative = (cov.get("sections") or {}).get("creative") or {}
            if story.get("logline"):
                return {"logline": story["logline"], "genre": (creative.get("themes_and_tone") or "").split(". ")[0]}
    return {}


def run_brandspot(job: dict) -> None:
    from .server import fresh_breakdown                 # spotting reads the current reading of the script
    fresh_breakdown(job["tool"], job["run_id"])
    rec, folder = store.get_run(job["tool"], job["run_id"])
    name = rec["inputs"]["file"]
    data = (folder / name).read_bytes()
    jid = job["id"]
    opts = job.get("options") or {}
    result = brandspot.spot(name, data, rec["outputs"]["breakdown"], store.load_settings(), options=opts.get("brand") or {},
                            film=film_facts(rec), targets=[b["brand_id"] for b in rec["outputs"].get("brand_targets") or []],
                            progress=lambda m: store.set_job(jid, progress=m),
                            cancelled=lambda: store.get_job(jid)["status"] == "cancelled", mode=opts.get("mode"))
    store.update_run(job["tool"], job["run_id"], outputs={"brand_spotting": result},
                     summary={"opportunities": len(result["opportunities"]), "brands_matched": len(result["targets"])})


def run_elements(job: dict) -> None:
    from .server import fresh_breakdown
    fresh_breakdown(job["tool"], job["run_id"])
    rec, folder = store.get_run(job["tool"], job["run_id"])
    name = rec["inputs"]["file"]
    data = (folder / name).read_bytes()
    jid = job["id"]
    result = elements.tag(name, data, rec["outputs"]["breakdown"], store.load_settings(),
                          progress=lambda m: store.set_job(jid, progress=m),
                          cancelled=lambda: store.get_job(jid)["status"] == "cancelled", mode=(job.get("options") or {}).get("mode"))
    result["date"] = __import__("datetime").date.today().isoformat()
    store.update_run(job["tool"], job["run_id"], outputs={"elements": result},
                     summary={"elements_tagged": sum(1 for s in result["scenes"] if s["tagged"])})


def run_bfiread(job: dict) -> None:
    from .server import fresh_breakdown
    fresh_breakdown(job["tool"], job["run_id"])
    rec, folder = store.get_run(job["tool"], job["run_id"])
    name = rec["inputs"]["file"]
    data = (folder / name).read_bytes()
    jid = job["id"]
    result = bfiread.read(name, data, rec["outputs"]["breakdown"], store.load_settings(),
                          progress=lambda m: store.set_job(jid, progress=m),
                          cancelled=lambda: store.get_job(jid)["status"] == "cancelled", mode=(job.get("options") or {}).get("mode"))
    store.update_run(job["tool"], job["run_id"], outputs={"bfi_read": result},
                     summary={"bfi_a": sum(c["proposed"] for k, c in result["criteria"].items() if k.startswith("A"))})


def run_casting(job: dict) -> None:
    from .server import fresh_breakdown
    fresh_breakdown(job["tool"], job["run_id"])
    rec, folder = store.get_run(job["tool"], job["run_id"])
    name = rec["inputs"]["file"]
    jid = job["id"]
    result = casting.read_roles(name, (folder / name).read_bytes(), rec["outputs"]["breakdown"], store.load_settings(),
                                mode=(job.get("options") or {}).get("mode"), progress=lambda m: store.set_job(jid, progress=m),
                                cancelled=lambda: store.get_job(jid)["status"] == "cancelled")
    result["date"] = __import__("datetime").date.today().isoformat()
    store.update_run(job["tool"], job["run_id"], outputs={"casting_read": result}, summary={"roles_read": len(result["roles"])})


def run_schedreason(job: dict) -> None:
    from .server import fresh_breakdown
    fresh_breakdown(job["tool"], job["run_id"])
    rec, _ = store.get_run(job["tool"], job["run_id"])
    jid, opts = job["id"], job.get("options") or {}
    result = schedreason.reason(rec["outputs"]["breakdown"], store.load_settings(), pages_per_day=opts.get("pages_per_day"),
                                elements=rec["outputs"].get("elements"), mode=opts.get("mode") or "deep",
                                progress=lambda m: store.set_job(jid, progress=m), cancelled=lambda: store.get_job(jid)["status"] == "cancelled")
    store.update_run(job["tool"], job["run_id"], outputs={"schedule_reasoned": result},
                     summary={"reasoned_days": len(result["days"])})


HANDLERS = {"coverage": run_coverage, "lookbook": run_lookbook, "brandspot": run_brandspot, "elements": run_elements, "bfiread": run_bfiread,
            "casting": run_casting, "schedreason": run_schedreason}
