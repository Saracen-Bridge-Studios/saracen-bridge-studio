"""Per-user storage: settings and run history. Windows: %APPDATA%\\SaracenStudio;
Mac: ~/Library/Application Support/SaracenStudio."""
from __future__ import annotations

import json
import os
import re
import sqlite3
import sys
import threading
import time
from pathlib import Path

DEFAULT_SETTINGS = {
    # provider: auto | ollama | openai | bundled | none (see studio.llm). auto = local Gemma first, then the bundled model.
    "ai_engine": {"provider": "auto", "url": "", "model": "", "api_key": "", "context": 16384, "gpu_layers": 99,
                  # reasoning: quick = thinking off (default), deep = thinking on; each may name its own model
                  "default_mode": "quick",
                  "modes": {"quick": {"model": "", "think": False}, "deep": {"model": "", "think": True}}},
    # the user's own cloud AI (off by default): provider anthropic | openai | gemini; key kept by studio.keys
    "cloud_ai": {"enabled": False, "provider": "anthropic", "model": "", "use_for": {"chat": True, "writing": False}},
    "external_apps": {
        "aiden": {"name": "A.I.D.E.N. (storyboard)", "target": ""},
        "frat": {"name": "F.R.A.T. (visual feedback)", "target": ""},
    },
}


def default_home(platform: str = sys.platform) -> str:
    if platform == "win32":
        return os.path.join(os.environ.get("APPDATA", ""), "SaracenStudio")
    if platform == "darwin":
        return os.path.join(Path.home(), "Library", "Application Support", "SaracenStudio")
    return os.path.join(Path.home(), ".saracen-studio")


def home() -> Path:
    base = os.environ.get("STUDIO_HOME") or default_home()
    p = Path(base)
    p.mkdir(parents=True, exist_ok=True)
    return p


def load_settings() -> dict:
    f = home() / "settings.json"
    s = json.loads(json.dumps(DEFAULT_SETTINGS))
    if f.exists():
        saved = json.loads(f.read_text(encoding="utf-8"))
        for k, v in saved.items():
            if isinstance(v, dict) and isinstance(s.get(k), dict):
                for kk, vv in v.items():
                    s[k][kk] = (s[k].get(kk, {}) | vv) if isinstance(vv, dict) and isinstance(s[k].get(kk), dict) else vv
            else:
                s[k] = v
    for k, v in DEFAULT_SETTINGS["external_apps"].items():      # the apps' display names are ours, not the user's
        if k in s.get("external_apps", {}):
            s["external_apps"][k]["name"] = v["name"]
    return s


def save_settings(s: dict) -> dict:
    (home() / "settings.json").write_text(json.dumps(s, indent=2), encoding="utf-8")
    return s


def _slug(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]+", "-", s).strip("-")[:60] or "run"


def _id(s: str) -> str:
    """A run id as a folder name, exactly as save_run made it. Ids are a 15-character time stamp plus a title of up to
    60, so cutting them to 60 like a title (1.1.0) lost the end of every long one: Tim's "Where the Sparrows Fly",
    20 Oct, read as "Registered with the Writer's Guild of Great Britain" and then couldn't be found ("Internal Server
    Error"). Only the safe characters are kept, so an id can never point outside the runs folder."""
    return re.sub(r"[^A-Za-z0-9_-]+", "-", s)[:120].strip("-") or "run"


_LOCK = threading.Lock()


def _index() -> sqlite3.Connection:
    """Library index (library.db) beside the run folders. The folders are the record; the index makes thousands of
    runs searchable without reading every run.json. Rebuilt from the folders if it is missing."""
    path = home() / "library.db"
    fresh = not path.exists()
    con = sqlite3.connect(path, check_same_thread=False)
    con.row_factory = sqlite3.Row
    con.execute("""CREATE TABLE IF NOT EXISTS runs (tool TEXT, id TEXT, title TEXT, created TEXT, files TEXT,
                   sha256 TEXT, summary TEXT, PRIMARY KEY (tool, id))""")
    con.execute("CREATE INDEX IF NOT EXISTS runs_created ON runs(created)")
    con.execute("CREATE INDEX IF NOT EXISTS runs_sha ON runs(tool, sha256)")
    con.execute("""CREATE TABLE IF NOT EXISTS jobs (id INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT, tool TEXT,
                   run_id TEXT, title TEXT, status TEXT, progress TEXT, error TEXT, created TEXT, started TEXT, finished TEXT,
                   options TEXT DEFAULT '{}')""")
    if "options" not in [r[1] for r in con.execute("PRAGMA table_info(jobs)")]:
        con.execute("ALTER TABLE jobs ADD COLUMN options TEXT DEFAULT '{}'")
    con.execute("CREATE INDEX IF NOT EXISTS jobs_status ON jobs(status, id)")
    if str(path) not in _TITLES_CLEANED:
        _TITLES_CLEANED.add(str(path))
        _clean_titles(con)
        con.execute("""UPDATE jobs SET status='retried' WHERE status IN ('error','cancelled') AND EXISTS (SELECT 1 FROM jobs
                       later WHERE later.kind = jobs.kind AND later.tool = jobs.tool AND later.run_id = jobs.run_id
                       AND later.id > jobs.id)""")
        con.commit()
    if fresh:
        root = home() / "runs"
        for f in (root.glob("*/*/run.json") if root.exists() else []):
            rec = json.loads(f.read_text(encoding="utf-8"))
            con.execute("INSERT OR REPLACE INTO runs VALUES (?,?,?,?,?,?,?)", _index_row(rec))
        con.commit()
    return con


_TITLES_CLEANED: set[str] = set()


def index_run(rec: dict) -> None:
    """Add one run (its run.json) to the Library index: used when a Library is imported (web mode, 1.3.0)."""
    con = _index()
    con.execute("INSERT OR REPLACE INTO runs VALUES (?,?,?,?,?,?,?)", _index_row(rec))
    con.commit()
    con.close()


def _clean_titles(con: sqlite3.Connection):
    """Once per start: titles saved before the title fix (13 Oct) get the cleaned form, in the index, the queue and the
    run's own record, so the Library shows "SNOWSTORM", not "S N O W S T O R M"."""
    from .script import clean_title
    for tool, rid, title in con.execute("SELECT tool, id, title FROM runs").fetchall():
        new = clean_title(title)
        if not new or new == title:
            continue
        con.execute("UPDATE runs SET title = ? WHERE tool = ? AND id = ?", (new, tool, rid))
        con.execute("UPDATE jobs SET title = ? WHERE tool = ? AND run_id = ?", (new, tool, rid))
        f = home() / "runs" / _slug(tool) / _id(rid) / "run.json"
        try:
            rec = json.loads(f.read_text(encoding="utf-8"))
            rec["title"] = new
            if isinstance(rec.get("outputs", {}).get("breakdown"), dict):
                rec["outputs"]["breakdown"]["title"] = new
            f.write_text(json.dumps(rec, indent=1, default=str), encoding="utf-8")
        except (OSError, ValueError):
            pass                                          # the index still shows the clean title
    con.commit()


def _index_row(rec: dict) -> tuple:
    return (rec["tool"], rec["id"], rec["title"], rec["created"], json.dumps(rec.get("files", [])),
            rec.get("inputs", {}).get("sha256"), json.dumps(rec.get("summary") or {}))


def save_run(tool: str, title: str, inputs: dict, outputs: dict, files: dict[str, bytes] | None = None,
             summary: dict | None = None) -> dict:
    stamp = time.strftime("%Y%m%d-%H%M%S")
    parent = home() / "runs" / _slug(tool)
    parent.mkdir(parents=True, exist_ok=True)
    with _LOCK:
        base, n = f"{stamp}_{_slug(title)}", 1
        while True:                      # same title in the same second must never overwrite an earlier run
            d = parent / (base if n == 1 else f"{base}-{n}")
            try:
                d.mkdir()
                break
            except FileExistsError:
                n += 1
    rec = {"tool": tool, "title": title, "created": time.strftime("%Y-%m-%d %H:%M:%S"), "id": d.name,
           "inputs": inputs, "outputs": outputs, "files": sorted((files or {}).keys()), "summary": summary or {}}
    for name, data in (files or {}).items():
        (d / Path(name).name).write_bytes(data)
    (d / "run.json").write_text(json.dumps(rec, indent=1, default=str), encoding="utf-8")
    with _LOCK:
        con = _index()
        con.execute("INSERT OR REPLACE INTO runs VALUES (?,?,?,?,?,?,?)", _index_row(rec))
        con.commit()
        con.close()
    return rec


def find_by_hash(tool: str, sha256: str) -> dict | None:
    with _LOCK:
        con = _index()
        r = con.execute("SELECT * FROM runs WHERE tool = ? AND sha256 = ? LIMIT 1", (tool, sha256)).fetchone()
        con.close()
    return _out(r) if r else None


def _out(r: sqlite3.Row) -> dict:
    d = dict(r)
    d["files"], d["summary"] = json.loads(d["files"] or "[]"), json.loads(d["summary"] or "{}")
    d.pop("sha256", None)
    return d


def list_runs(tool: str | None = None, q: str = "", limit: int = 200, offset: int = 0) -> dict:
    where, args = ["title LIKE ?"], [f"%{q.strip()}%"]
    if tool:
        where.append("tool = ?")
        args.append(tool)
    with _LOCK:
        con = _index()
        total = con.execute(f"SELECT COUNT(*) FROM runs WHERE {' AND '.join(where)}", args).fetchone()[0]
        rows = con.execute(f"SELECT * FROM runs WHERE {' AND '.join(where)} ORDER BY created DESC, id DESC LIMIT ? OFFSET ?",
                           args + [limit, offset]).fetchall()
        con.close()
    return {"total": total, "runs": [_out(r) for r in rows]}


def get_run(tool: str, run_id: str) -> tuple[dict, Path]:
    d = home() / "runs" / _slug(tool) / _id(run_id)
    return json.loads((d / "run.json").read_text(encoding="utf-8")), d


def update_run(tool: str, run_id: str, outputs: dict | None = None, files: dict[str, bytes] | None = None,
               summary: dict | None = None, title: str | None = None) -> dict:
    """Add results to an existing run (e.g. coverage written later for an ingested script)."""
    rec, d = get_run(tool, run_id)
    if title:
        rec["title"] = title
        _jobs("UPDATE jobs SET title = ? WHERE tool = ? AND run_id = ?", (title, tool, run_id), write=True)
    rec["outputs"].update(outputs or {})
    for name, data in (files or {}).items():
        (d / Path(name).name).write_bytes(data)
    rec["files"] = sorted(set(rec.get("files", [])) | {Path(n).name for n in (files or {})})
    rec["summary"] = (rec.get("summary") or {}) | (summary or {})
    (d / "run.json").write_text(json.dumps(rec, indent=1, default=str), encoding="utf-8")
    with _LOCK:
        con = _index()
        con.execute("INSERT OR REPLACE INTO runs VALUES (?,?,?,?,?,?,?)", _index_row(rec))
        con.commit()
        con.close()
    return rec


def update_inputs(tool: str, run_id: str, inputs: dict) -> dict:
    rec, d = get_run(tool, run_id)
    rec["inputs"] = inputs
    (d / "run.json").write_text(json.dumps(rec, indent=1, default=str), encoding="utf-8")
    return rec


# ---------------------------------------------------------------- job queue (kept in library.db)

_NOW = lambda: time.strftime("%Y-%m-%d %H:%M:%S")
ACTIVE = ("queued", "running")


def _jobs(sql: str, args=(), one=False, write=False):
    with _LOCK:
        con = _index()
        cur = con.execute(sql, args)
        rows = cur.fetchall()
        last = cur.lastrowid
        if write:
            con.commit()
        con.close()
    if write:
        return last
    rows = [dict(r) for r in rows]
    return (rows[0] if rows else None) if one else rows


def enqueue(kind: str, tool: str, run_id: str, title: str, options: dict | None = None) -> dict:
    """Queue a job unless the same job is already waiting or running."""
    existing = _jobs("SELECT * FROM jobs WHERE kind=? AND tool=? AND run_id=? AND status IN ('queued','running')",
                     (kind, tool, run_id), one=True)
    if existing:
        return existing
    jid = _jobs("INSERT INTO jobs (kind, tool, run_id, title, status, progress, error, created, options) VALUES (?,?,?,?,?,?,?,?,?)",
                (kind, tool, run_id, title, "queued", "", "", _NOW(), json.dumps(options or {})), write=True)
    # the new attempt replaces earlier failed ones for this script, so Failed counts scripts still failing, not attempts
    _jobs("UPDATE jobs SET status='retried' WHERE kind=? AND tool=? AND run_id=? AND status IN ('error','cancelled') AND id < ?",
          (kind, tool, run_id, jid), write=True)
    return get_job(jid)


def get_job(jid: int) -> dict | None:
    j = _jobs("SELECT * FROM jobs WHERE id=?", (jid,), one=True)
    if j:
        j["options"] = json.loads(j.get("options") or "{}")
    return j


def list_jobs(kind: str | None = None, limit: int = 200) -> dict:
    where, args = ("WHERE kind=?", (kind,)) if kind else ("", ())
    counts = {r["status"]: r["n"] for r in _jobs(f"SELECT status, COUNT(*) n FROM jobs {where} GROUP BY status", args)}
    jobs = _jobs(f"""SELECT * FROM jobs {where} ORDER BY CASE status WHEN 'running' THEN 0 WHEN 'queued' THEN 1 ELSE 2 END,
                     CASE WHEN status IN ('queued') THEN id END ASC, id DESC LIMIT ?""", args + (limit,))
    for j in jobs:
        if j["status"] == "running":
            j.update(eta(j))
    return {"counts": counts, "jobs": jobs}


# ---------------------------------------------------------------- time left (1.3.1)
# Tim, 18 Nov: "eta on completion for tagging elements and schedule budget". Two honest bases, never a made-up figure:
#   steps    the job says "scenes 72-84 of 134": the time the finished steps took, carried over the steps left
#   history  how long this kind of job, at this reasoning mode, took the last few times on this computer
# Jobs that are all steps (tagging, reading roles) use steps; the others use history, then steps for the part in hand.
STEP_KINDS = ("elements", "casting")
_STEP = re.compile(r"(\d+)(?:\s*[\u2013-]\s*(\d+))?\s+of\s+(\d+)")


def _secs(stamp: str | None) -> float | None:
    try:
        return time.mktime(time.strptime(stamp, "%Y-%m-%d %H:%M:%S")) if stamp else None
    except (TypeError, ValueError):
        return None


def _mode(job: dict) -> str:
    o = job.get("options")
    try:
        o = json.loads(o or "{}") if isinstance(o, str) else (o or {})
    except ValueError:
        o = {}
    return o.get("mode") or ""


def usual_seconds(kind: str, mode: str = "") -> float | None:
    """The middle duration of the last few finished jobs of this kind (same reasoning mode when there are any)."""
    rows = _jobs("SELECT started, finished, options FROM jobs WHERE kind=? AND status='done' AND started IS NOT NULL "
                 "AND finished IS NOT NULL ORDER BY id DESC LIMIT 24", (kind,))
    took = [(_mode(r), (_secs(r["finished"]) or 0) - (_secs(r["started"]) or 0)) for r in rows]
    took = [(m, t) for m, t in took if t > 0]
    same = [t for m, t in took if m == mode][:8] or [t for _, t in took][:8]
    if not same:
        return None
    same.sort()
    return same[len(same) // 2]


def eta(job: dict, now: float | None = None) -> dict:
    """Time left for a running job: {"elapsed_seconds", "eta_seconds" (None when it can't be said), "eta_basis"}."""
    start = _secs(job.get("started"))
    if start is None:
        return {"elapsed_seconds": None, "eta_seconds": None, "eta_basis": None}
    elapsed = max(0.0, (now if now is not None else time.time()) - start)
    steps = None
    m = _STEP.search(job.get("progress") or "")
    if m:
        first, total = int(m.group(1)), int(m.group(3))
        done = first - 1                                   # "72-84 of 134": 71 are finished, 72 to 84 are in hand
        if total > 0 and 0 < done < total and elapsed > 0:
            steps = elapsed / done * (total - done)
    usual = usual_seconds(job.get("kind") or "", _mode(job))
    left, basis = None, None
    if job.get("kind") in STEP_KINDS:
        if steps is not None:
            left, basis = steps, "steps"
        elif usual and usual > elapsed:
            left, basis = usual - elapsed, "history"
    elif usual:
        left, basis = (usual - elapsed, "history") if usual > elapsed else (None, "over")
    elif steps is not None:
        left, basis = steps, "steps"
    return {"elapsed_seconds": round(elapsed), "eta_seconds": None if left is None else max(5, round(left)), "eta_basis": basis}


def active_jobs() -> dict:
    """Every job that is running or waiting, of every kind, oldest first: what the AI is busy with (1.3.1)."""
    jobs = _jobs("SELECT * FROM jobs WHERE status IN ('queued','running') ORDER BY CASE status WHEN 'running' THEN 0 ELSE 1 END, id")
    for j in jobs:
        if j["status"] == "running":
            j.update(eta(j))
    return {"jobs": jobs, "running": sum(1 for j in jobs if j["status"] == "running"),
            "queued": sum(1 for j in jobs if j["status"] == "queued")}


def cancel_all() -> int:
    """Stop all: every running and waiting job, of every kind, is cancelled. Scripts and finished work are untouched."""
    n = len(_jobs("SELECT id FROM jobs WHERE status IN ('queued','running')"))
    _jobs("UPDATE jobs SET status='cancelled', finished=? WHERE status IN ('queued','running')", (_NOW(),), write=True)
    return n


def clear_history() -> int:
    """Take every finished job (done, failed, cancelled, replaced) off the lists. Running and waiting ones stay."""
    n = len(_jobs("SELECT id FROM jobs WHERE status IN ('done','error','cancelled','retried')"))
    _jobs("UPDATE jobs SET status='cleared' WHERE status IN ('done','error','cancelled','retried')", write=True)
    return n


def claim_job() -> dict | None:
    """Take the oldest queued job and mark it running (one worker, so no race beyond the lock)."""
    with _LOCK:
        con = _index()
        row = con.execute("SELECT * FROM jobs WHERE status='queued' ORDER BY id LIMIT 1").fetchone()
        if row:
            con.execute("UPDATE jobs SET status='running', started=?, progress='Starting', error='' WHERE id=?", (_NOW(), row["id"]))
            con.commit()
        con.close()
    return get_job(row["id"]) if row else None


def set_job(jid: int, **fields) -> None:
    if fields.get("status") in ("done", "error", "cancelled"):
        fields.setdefault("finished", _NOW())
    cols = ", ".join(f"{k}=?" for k in fields)
    _jobs(f"UPDATE jobs SET {cols} WHERE id=?", tuple(fields.values()) + (jid,), write=True)


def cancel_job(jid: int) -> dict | None:
    _jobs("UPDATE jobs SET status='cancelled', finished=? WHERE id=? AND status IN ('queued','running')", (_NOW(), jid), write=True)
    return get_job(jid)


def clear_jobs(kind: str | None = None, job_id: int | None = None, statuses: tuple = ("error", "cancelled")) -> int:
    """Take finished jobs off the queue list (Tim, 13 Oct: failed ones he doesn't need to see). Nothing else changes:
    the script and any coverage stay in the Library, and the script can be queued again."""
    marks = ",".join("?" * len(statuses))
    where, args = f"status IN ({marks})", list(statuses)
    if job_id is not None:
        where += " AND id=?"; args.append(job_id)
    if kind:
        where += " AND kind=?"; args.append(kind)
    n = len(_jobs(f"SELECT id FROM jobs WHERE {where}", tuple(args)))
    _jobs(f"UPDATE jobs SET status='cleared' WHERE {where}", tuple(args), write=True)
    return n


def load_shortlist() -> list[str]:
    f = home() / "brand_shortlist.json"
    try:
        ids = json.loads(f.read_text(encoding="utf-8"))
        return [str(i) for i in ids] if isinstance(ids, list) else []
    except (OSError, ValueError):
        return []


def save_shortlist(ids: list[str]) -> list[str]:
    ids = list(dict.fromkeys(str(i) for i in ids if i))[:500]
    f = home() / "brand_shortlist.json"
    f.write_text(json.dumps(ids), encoding="utf-8")
    return ids


def requeue_interrupted() -> int:
    """After a crash or restart, jobs left 'running' go back to the front of the queue."""
    n = len(_jobs("SELECT id FROM jobs WHERE status='running'"))
    _jobs("UPDATE jobs SET status='queued', progress='Resumed after restart' WHERE status='running'", write=True)
    return n


# ---------------------------------------------------------------- removing from the Library (1.3.1)
# Tim, 18 Nov: "delete history and projects option". Removing is two steps, so a slip can be put right: Remove moves
# the item's folder out of the Library into removed/ (it leaves every list, and any AI work on it stops); the Removed
# list can put it back, or delete it for good.

def _removed_root() -> Path:
    return home() / "removed"


def remove_run(tool: str, run_id: str) -> dict:
    """Move one Library item to removed/. Its waiting or running jobs are cancelled; its finished ones leave the lists."""
    src = home() / "runs" / _slug(tool) / _id(run_id)
    rec = json.loads((src / "run.json").read_text(encoding="utf-8"))        # FileNotFoundError when it isn't there
    parent = _removed_root() / _slug(tool)
    parent.mkdir(parents=True, exist_ok=True)
    with _LOCK:
        dst, n = parent / src.name, 1
        while dst.exists():
            n += 1
            dst = parent / f"{src.name}-{n}"
        src.rename(dst)
        (dst / "removed.json").write_text(json.dumps({"removed": _NOW(), "tool": tool, "id": run_id}), encoding="utf-8")
        con = _index()
        con.execute("DELETE FROM runs WHERE tool = ? AND id = ?", (tool, run_id))
        # finished jobs leave the lists; a waiting or running one is cancelled (the worker stops at "cancelled")
        con.execute("UPDATE jobs SET status='cleared' WHERE tool=? AND run_id=? AND status NOT IN ('queued','running')", (tool, run_id))
        con.execute("UPDATE jobs SET status='cancelled', finished=? WHERE tool=? AND run_id=? AND status IN ('queued','running')",
                    (_NOW(), tool, run_id))
        con.commit()
        con.close()
    return {"tool": tool, "id": run_id, "title": rec.get("title"), "key": f"{_slug(tool)}/{dst.name}"}


def list_removed() -> list[dict]:
    out = []
    root = _removed_root()
    for f in sorted(root.glob("*/*/run.json")) if root.exists() else []:
        try:
            rec = json.loads(f.read_text(encoding="utf-8"))
            meta = json.loads((f.parent / "removed.json").read_text(encoding="utf-8")) if (f.parent / "removed.json").exists() else {}
        except (OSError, ValueError):
            continue
        out.append({"key": f"{f.parent.parent.name}/{f.parent.name}", "tool": rec.get("tool"), "id": rec.get("id"),
                    "title": rec.get("title"), "created": rec.get("created"), "removed": meta.get("removed"),
                    "files": len(rec.get("files") or [])})
    out.sort(key=lambda r: r.get("removed") or "", reverse=True)
    return out


def _removed_dir(key: str) -> Path:
    tool, _, name = str(key).partition("/")
    d = _removed_root() / _slug(tool) / _id(name)
    if not (d / "run.json").is_file():
        raise FileNotFoundError(key)
    return d


def restore_run(key: str) -> dict:
    """Put a removed item back in the Library, under its own id (or with a number added if that id has been taken)."""
    d = _removed_dir(key)
    rec = json.loads((d / "run.json").read_text(encoding="utf-8"))
    parent = home() / "runs" / _slug(rec["tool"])
    parent.mkdir(parents=True, exist_ok=True)
    with _LOCK:
        dst, n = parent / _id(rec["id"]), 1
        while dst.exists():
            n += 1
            dst = parent / f"{_id(rec['id'])}-{n}"
        d.rename(dst)
        try:
            (dst / "removed.json").unlink()
        except OSError:
            pass
        if dst.name != rec["id"]:
            rec["id"] = dst.name
            (dst / "run.json").write_text(json.dumps(rec, indent=1, default=str), encoding="utf-8")
        con = _index()
        con.execute("INSERT OR REPLACE INTO runs VALUES (?,?,?,?,?,?,?)", _index_row(rec))
        con.commit()
        con.close()
    return {"tool": rec["tool"], "id": rec["id"], "title": rec.get("title")}


def delete_removed(key: str | None = None) -> int:
    """Delete removed items for good: one (key) or all of them. This is the only place the Studio erases saved work."""
    import shutil
    dirs = [_removed_dir(key)] if key else [f.parent for f in _removed_root().glob("*/*/run.json")] if _removed_root().exists() else []
    for d in dirs:
        shutil.rmtree(d)
    return len(dirs)
