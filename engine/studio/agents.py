"""Sales Agents: Jon Chadwick's Sales Agent scoring specification v1.0 (21 Oct 2026), built as he wrote it.

One whole-number sales capability score out of 100 for a sales company, for a specific project and mandate: the
company's base score, reduced where it fits the film's genre less well. The score is deterministic (integer
arithmetic, one round-half-up), every input is kept, and the calculation is shown. It never changes the valuation
engine's outputs (Ask, Expected Close, Take, bankable value, producer receipts): it helps choose a company.

Records (Jon's data contract, adapted to the Studio):
- the company register: tools/sales_agents.json, seeded at dataVersion 2026-10-21; an administrator's edits are
  kept in agents.db with old and new values, editor, time and reason, and each base-score change makes a new data
  version;
- fit assessments: per company, project and genre, the fit level with rationale, evidence and assessor. A fit level
  belongs to a genre, not to its position: SECONDARY is a fit level, whichever of the film's genres it is for;
- approved genre mappings: a company's fit for a genre, approved for reuse on other projects;
- calculation snapshots: kept when a comparison is exported, so an issued result can be told from a current one.
"""
from __future__ import annotations

import csv
import io
import json
import re
import sqlite3
import threading
import time
from pathlib import Path

from . import refdata, store

FORMULA_VERSION = "1.0"
FITS = {"CORE": 100, "SECONDARY": 90, "LIMITED": 75, "OUTSIDE": 60}           # multiplier percentages
FIT_LEVELS = (*FITS, "UNVERIFIED")
FIT_LABEL = {"CORE": "Core", "SECONDARY": "Secondary", "LIMITED": "Limited", "OUTSIDE": "Outside speciality",
             "UNVERIFIED": "Unverified"}
SCOPES = ("INTERNATIONAL_SALES", "DISTRIBUTION")
SCOPE_LABEL = {"INTERNATIONAL_SALES": "International sales", "DISTRIBUTION": "Distribution"}
EVIDENCE_STATUS = ("PROVISIONAL", "VERIFIED")
_LOCK = threading.Lock()


# ------------------------------------------------------------------ genres (Tim's taxonomy, canonical IDs)
def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def genres() -> list[dict]:
    """Tim's 18 genres as canonical IDs ("Science fiction" -> science_fiction), each with its subgenre IDs."""
    data = json.loads((refdata.app_root() / "tools" / "genres.json").read_text(encoding="utf-8"))
    return [{"id": _slug(g["genre"]), "name": g["genre"],
             "subgenres": [{"id": f"{_slug(g['genre'])}.{_slug(s)}", "name": s} for s in g["subgenres"]]} for g in data["genres"]]


def genre_ids() -> set[str]:
    return {g["id"] for g in genres()}


def genre_id(name: str | None) -> str | None:
    """A genre name as the project stores it, or an ID, to its canonical ID; None when it isn't one of the 18."""
    if not name:
        return None
    for g in genres():
        if name in (g["id"], g["name"]) or _slug(name) == g["id"]:
            return g["id"]
    return None


def genre_name(gid: str | None) -> str:
    return next((g["name"] for g in genres() if g["id"] == gid), gid or "")


# ------------------------------------------------------------------ the deterministic score (Jon's reference function)
def score_agent(base_score, score_scope, requested_scope, primary_genre_id, primary_fit, secondary_genre_id=None,
                secondary_fit=None, *, known_genres: set[str] | None = None) -> dict:
    """Jon's scoreAgent, step for step. Integer arithmetic: multipliers as percentages, 70/30 weights, so the
    weighted units have a denominator of 10,000 and the one rounding is floor((numerator + 5000) / 10000)."""
    known = known_genres if known_genres is not None else genre_ids()
    out = {"status": None, "reasonCode": None, "baseScoreUsed": base_score, "scoreScope": score_scope,
           "requestedScope": requested_scope, "primaryGenreId": primary_genre_id, "secondaryGenreId": secondary_genre_id,
           "primaryFit": primary_fit, "secondaryFit": secondary_fit, "weightedMultiplier": None, "rawScore": None,
           "adjustedScore": None, "discountPercent": None, "pointsDeducted": None, "formulaVersion": FORMULA_VERSION}

    def invalid(code):
        return out | {"status": "INVALID_INPUT", "reasonCode": code}

    if type(base_score) is not int or not 0 <= base_score <= 100:          # no coercion: 82.5, "83", True, None fail
        return invalid("BASE_SCORE_INVALID")
    if score_scope not in SCOPES or requested_scope not in SCOPES:
        return invalid("SCOPE_INVALID")
    if not primary_genre_id:
        return invalid("PRIMARY_GENRE_MISSING")
    if primary_genre_id not in known:
        return invalid("PRIMARY_GENRE_UNKNOWN")
    if primary_fit not in FIT_LEVELS:
        return invalid("PRIMARY_FIT_INVALID")
    if secondary_genre_id is None:
        if secondary_fit is not None:
            return invalid("SECONDARY_FIT_WITHOUT_GENRE")
        pw, sw = 100, 0
    else:
        if secondary_genre_id not in known:
            return invalid("SECONDARY_GENRE_UNKNOWN")
        if secondary_genre_id == primary_genre_id:
            return invalid("GENRES_IDENTICAL")
        if secondary_fit not in FIT_LEVELS:
            return invalid("SECONDARY_FIT_INVALID")
        pw, sw = 70, 30
    if score_scope != requested_scope:
        return out | {"status": "SCOPE_MISMATCH", "reasonCode": "SCOPE_MISMATCH"}
    if primary_fit == "UNVERIFIED" or (secondary_genre_id is not None and secondary_fit == "UNVERIFIED"):
        return out | {"status": "NEEDS_REVIEW", "reasonCode": "FIT_UNVERIFIED"}
    m1 = FITS[primary_fit]
    m2 = FITS[secondary_fit] if secondary_genre_id is not None else 0
    units = pw * m1 + sw * m2
    numerator = base_score * units
    adjusted = (numerator + 5000) // 10000
    return out | {"status": "SCORED", "weightedMultiplier": units / 10000, "rawScore": numerator / 10000,
                  "adjustedScore": adjusted, "discountPercent": (10000 - units) / 100, "pointsDeducted": base_score - adjusted}


def explain(r: dict, primary_name: str = "", secondary_name: str = "") -> str:
    """The short explanation shown beside a score, after Jon's example: 'Base 88. Core fit for the primary genre
    (Horror); outside-speciality fit for the secondary genre (Thriller). Weighted discount 12%. Adjusted score 77.'"""
    st = r["status"]
    if st == "SCOPE_MISMATCH":
        return "Score unavailable for this mandate."
    if st == "NEEDS_REVIEW":
        return "Genre fit unverified: assess it to score this company."
    if st == "INVALID_INPUT":
        return f"Can't score: {r['reasonCode'].replace('_', ' ').lower()}."
    adj = lambda f: {"OUTSIDE": "outside-speciality"}.get(f, FIT_LABEL[f].lower())
    fits = f"{adj(r['primaryFit'])} fit for the primary genre{f' ({primary_name})' if primary_name else ''}"
    if r["secondaryGenreId"]:
        fits += f"; {adj(r['secondaryFit'])} fit for the secondary genre{f' ({secondary_name})' if secondary_name else ''}"
    pct = r["discountPercent"]
    pct = int(pct) if float(pct).is_integer() else round(pct, 2)
    return f"Base {r['baseScoreUsed']}. {fits[0].upper() + fits[1:]}. Weighted discount {pct}%. Adjusted score {r['adjustedScore']}."


# ------------------------------------------------------------------ storage
def _seed() -> dict:
    return json.loads((refdata.app_root() / "tools" / "sales_agents.json").read_text(encoding="utf-8"))


def _db() -> sqlite3.Connection:
    con = sqlite3.connect(store.home() / "agents.db", timeout=30)
    con.row_factory = sqlite3.Row
    con.executescript("""
        CREATE TABLE IF NOT EXISTS edits (id INTEGER PRIMARY KEY AUTOINCREMENT, agent_id TEXT, field TEXT, old TEXT, new TEXT,
            editor TEXT, at TEXT, reason TEXT, data_version TEXT);
        CREATE TABLE IF NOT EXISTS fits (id INTEGER PRIMARY KEY AUTOINCREMENT, agent_id TEXT, project_id TEXT, genre_id TEXT,
            fit TEXT, rationale TEXT, evidence TEXT, evidence_status TEXT, assessed_by TEXT, assessed_at TEXT,
            mandate TEXT, version INTEGER);
        CREATE TABLE IF NOT EXISTS mappings (id INTEGER PRIMARY KEY AUTOINCREMENT, agent_id TEXT, genre_id TEXT, fit TEXT,
            rationale TEXT, evidence TEXT, approved_by TEXT, approved_at TEXT, active INTEGER DEFAULT 1);
        CREATE TABLE IF NOT EXISTS snapshots (id INTEGER PRIMARY KEY AUTOINCREMENT, project_id TEXT, created_at TEXT, payload TEXT);
        CREATE INDEX IF NOT EXISTS fits_key ON fits(agent_id, project_id, genre_id, id);
    """)
    return con


def _now() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")


EDITABLE = {"baseScore", "specialityText", "scoreScope", "displayName"}


def register() -> dict:
    """The current register: the seed with every recorded edit applied, and the data version in force."""
    seed = _seed()
    agents = {a["agentId"]: dict(a) for a in seed["agents"]}
    version = seed["dataVersion"]
    with _LOCK:
        con = _db()
        rows = con.execute("SELECT * FROM edits ORDER BY id").fetchall()
        con.close()
    for e in rows:
        a = agents.get(e["agent_id"])
        if a is None:
            continue
        val = json.loads(e["new"])
        a[e["field"]] = val
        if e["field"] == "baseScore":
            a["baseScoreStatus"] = "PROVISIONAL"
        a["reviewedAt"] = e["at"][:10]
        version = e["data_version"] or version
    return {"dataVersion": version, "formulaVersion": FORMULA_VERSION, "agents": list(agents.values()),
            "edits": len(rows), "seedVersion": seed["dataVersion"]}


def agent(agent_id: str) -> dict | None:
    return next((a for a in register()["agents"] if a["agentId"] == agent_id), None)


def resolve_name(name: str) -> dict | None:
    """A company name or alias to its record ("Saban" -> Saban Films); never a fuzzy guess."""
    n = (name or "").strip().lower()
    for a in register()["agents"]:
        if n in [a["agentId"].lower(), a["displayName"].lower(), *[x.lower() for x in a.get("aliases") or []]]:
            return a
    return None


def edit(agent_id: str, changes: dict, editor: str, reason: str) -> dict:
    """An administrator's edit: old and new values, editor, time and reason kept; a base-score change makes a new
    data version (the formula version only changes with the policy)."""
    if not (editor or "").strip() or not (reason or "").strip():
        raise ValueError("Give your name and a reason for the change.")
    a = agent(agent_id)
    if not a:
        raise KeyError(agent_id)
    changes = {k: v for k, v in changes.items() if k in EDITABLE and v != a.get(k)}
    if "baseScore" in changes:
        b = changes["baseScore"]
        if b is not None and (type(b) is not int or not 0 <= b <= 100):
            raise ValueError("A base score is a whole number from 0 to 100, or empty for unrated.")
    if "scoreScope" in changes and changes["scoreScope"] not in SCOPES:
        raise ValueError("Scope is international sales or distribution.")
    if not changes:
        return a
    version = register()["dataVersion"]
    if "baseScore" in changes:
        day = time.strftime("%Y-%m-%d")
        n = int(version.split(".")[1]) + 1 if version.startswith(day + ".") else 1
        version = f"{day}.{n}"
    with _LOCK:
        con = _db()
        for k, v in changes.items():
            con.execute("INSERT INTO edits (agent_id, field, old, new, editor, at, reason, data_version) VALUES (?,?,?,?,?,?,?,?)",
                        (agent_id, k, json.dumps(a.get(k)), json.dumps(v), editor.strip(), _now(), reason.strip(), version))
        con.commit()
        con.close()
    return agent(agent_id)


def history() -> list[dict]:
    with _LOCK:
        con = _db()
        rows = [dict(r) | {"old": json.loads(r["old"]), "new": json.loads(r["new"])}
                for r in con.execute("SELECT * FROM edits ORDER BY id DESC").fetchall()]
        con.close()
    return rows


# ------------------------------------------------------------------ fit assessments and approved mappings
def assess(agent_id: str, project_id: str, gid: str, fit: str, rationale: str, evidence: str, assessed_by: str,
           evidence_status: str = "PROVISIONAL", mandate: str = "", save_mapping: bool = False) -> dict:
    """Record a fit for one company, project and genre. A scored fit needs a short rationale and a source or internal
    evidence reference; OUTSIDE needs its rationale above all (it is a positive finding, not missing evidence)."""
    if not agent(agent_id):
        raise KeyError(agent_id)
    if gid not in genre_ids():
        raise ValueError("Unknown genre.")
    if fit not in FIT_LEVELS:
        raise ValueError("Fit is Core, Secondary, Limited, Outside speciality or Unverified.")
    if evidence_status not in EVIDENCE_STATUS:
        raise ValueError("Evidence status is provisional or verified.")
    if not (assessed_by or "").strip():
        raise ValueError("Give the assessor's name.")
    if fit != "UNVERIFIED" and (not (rationale or "").strip() or not (evidence or "").strip()):
        raise ValueError("A fit needs a short rationale and a source or internal evidence reference.")
    with _LOCK:
        con = _db()
        prev = con.execute("SELECT MAX(version) v FROM fits WHERE agent_id=? AND project_id=? AND genre_id=?",
                           (agent_id, project_id, gid)).fetchone()["v"] or 0
        con.execute("INSERT INTO fits (agent_id, project_id, genre_id, fit, rationale, evidence, evidence_status, assessed_by,"
                    " assessed_at, mandate, version) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (agent_id, project_id, gid, fit, (rationale or "").strip(), (evidence or "").strip(), evidence_status,
                     assessed_by.strip(), _now(), mandate, prev + 1))
        if save_mapping and fit != "UNVERIFIED":
            con.execute("UPDATE mappings SET active=0 WHERE agent_id=? AND genre_id=?", (agent_id, gid))
            con.execute("INSERT INTO mappings (agent_id, genre_id, fit, rationale, evidence, approved_by, approved_at) VALUES (?,?,?,?,?,?,?)",
                        (agent_id, gid, fit, rationale.strip(), evidence.strip(), assessed_by.strip(), _now()))
        con.commit()
        con.close()
    return current_fit(agent_id, project_id, gid)


def current_fit(agent_id: str, project_id: str, gid: str | None) -> dict:
    """This project's latest assessment for the company and genre; else an exact approved mapping for that genre
    (provisional); else Unverified. Never a substring match, and an unlisted genre is never assumed Outside."""
    if not gid:
        return {"fit": None}
    with _LOCK:
        con = _db()
        r = con.execute("SELECT * FROM fits WHERE agent_id=? AND project_id=? AND genre_id=? ORDER BY id DESC LIMIT 1",
                        (agent_id, project_id, gid)).fetchone()
        m = None if r else con.execute("SELECT * FROM mappings WHERE agent_id=? AND genre_id=? AND active=1 ORDER BY id DESC LIMIT 1",
                                       (agent_id, gid)).fetchone()
        con.close()
    if r:
        return {"fit": r["fit"], "rationale": r["rationale"], "evidence": r["evidence"], "evidenceStatus": r["evidence_status"],
                "assessedBy": r["assessed_by"], "assessedAt": r["assessed_at"], "assessmentVersion": r["version"], "from": "assessment"}
    if m:
        return {"fit": m["fit"], "rationale": m["rationale"], "evidence": m["evidence"], "evidenceStatus": "PROVISIONAL",
                "assessedBy": m["approved_by"], "assessedAt": m["approved_at"], "assessmentVersion": 0, "from": "approved mapping"}
    return {"fit": "UNVERIFIED", "from": "none"}


# ------------------------------------------------------------------ projects and the comparison
def project(project_id: str) -> dict:
    """A Sales Estimates valuation as the project: its title and its two scoring genres."""
    rec, _ = store.get_run("sales", project_id)
    intake = (rec.get("inputs") or {}).get("intake") or {}
    p, s = genre_id(intake.get("genre")), genre_id(intake.get("secondary_genre"))
    return {"projectId": project_id, "title": rec.get("title") or "", "primaryGenreId": p,
            "secondaryGenreId": s if s and s != p else None, "primaryGenre": intake.get("genre") or "",
            "secondaryGenre": intake.get("secondary_genre") or "", "subgenre": intake.get("subgenre") or "",
            "logline": intake.get("logline") or ""}


def compare(project_id: str | None, requested_scope: str = "INTERNATIONAL_SALES") -> dict:
    """Every company scored for one project and mandate. Scored companies rank by adjusted score, then base score,
    then name; unscored ones are listed apart with their reason, and a company scored for another mandate is never
    ranked in this one."""
    reg = register()
    proj = project(project_id) if project_id else None
    known = genre_ids()
    rows = []
    for a in reg["agents"]:
        base = {"agentId": a["agentId"], "displayName": a["displayName"], "specialityText": a["specialityText"],
                "baseScore": a["baseScore"], "scoreScope": a["scoreScope"], "baseScoreStatus": a["baseScoreStatus"],
                "estimateAccuracyScore": a.get("estimateAccuracyScore"), "trustworthinessScore": a.get("trustworthinessScore"),
                "sourceUrls": a.get("sourceUrls") or []}
        if not proj:
            rows.append(base | {"result": None})
            continue
        pf = current_fit(a["agentId"], project_id, proj["primaryGenreId"])
        sf = current_fit(a["agentId"], project_id, proj["secondaryGenreId"]) if proj["secondaryGenreId"] else {"fit": None}
        if a["baseScore"] is None:
            res = {"status": "INVALID_INPUT", "reasonCode": "BASE_SCORE_UNRATED", "adjustedScore": None}
        else:
            res = score_agent(a["baseScore"], a["scoreScope"], requested_scope, proj["primaryGenreId"], pf["fit"],
                              proj["secondaryGenreId"], sf["fit"] if proj["secondaryGenreId"] else None, known_genres=known)
        res = res | {"dataVersion": reg["dataVersion"], "calculatedAt": _now(),
                     "assessmentVersion": [pf.get("assessmentVersion"), sf.get("assessmentVersion")]}
        provisional = a["baseScoreStatus"] == "PROVISIONAL" or "PROVISIONAL" in (pf.get("evidenceStatus"), sf.get("evidenceStatus"))
        rows.append(base | {"primary": pf, "secondary": sf, "result": res, "provisional": provisional,
                            "explanation": explain(res, genre_name(proj["primaryGenreId"]), genre_name(proj["secondaryGenreId"]))})
    if proj:
        scored = [r for r in rows if r["result"]["status"] == "SCORED"]
        scored.sort(key=lambda r: (-r["result"]["adjustedScore"], -r["result"]["baseScoreUsed"], r["displayName"].lower()))
        other = [r for r in rows if r["result"]["status"] != "SCORED"]
        other.sort(key=lambda r: ({"NEEDS_REVIEW": 0, "INVALID_INPUT": 1, "SCOPE_MISMATCH": 2}.get(r["result"]["status"], 3), r["displayName"].lower()))
    else:
        scored, other = [], sorted(rows, key=lambda r: (-(r["baseScore"] if r["baseScore"] is not None else -1), r["displayName"].lower()))
    return {"project": proj, "requestedScope": requested_scope, "dataVersion": reg["dataVersion"],
            "formulaVersion": FORMULA_VERSION, "scored": scored, "unscored": other}


def snapshot(project_id: str, requested_scope: str) -> dict:
    """Keep this comparison as issued (an export keeps one), so it can later be told from the current result."""
    c = compare(project_id, requested_scope)
    with _LOCK:
        con = _db()
        cur = con.execute("INSERT INTO snapshots (project_id, created_at, payload) VALUES (?,?,?)",
                          (project_id, _now(), json.dumps(c, ensure_ascii=False)))
        con.commit()
        sid = cur.lastrowid
        con.close()
    return c | {"snapshotId": sid}


def csv_bytes(c: dict) -> bytes:
    """The comparison as a spreadsheet: nulls stay blank or Unrated, never zero."""
    buf = io.StringIO()
    w = csv.writer(buf)
    p = c.get("project") or {}
    w.writerow(["Project", p.get("title", ""), "Mandate", SCOPE_LABEL.get(c["requestedScope"], c["requestedScope"]),
                "Data version", c["dataVersion"], "Formula version", c["formulaVersion"]])
    w.writerow([])
    w.writerow(["Rank", "Company", "Genre speciality", "Base score", "Primary fit", "Secondary fit", "Genre discount %",
                "Adjusted sales score", "Status", "Estimate accuracy", "Trustworthiness", "Explanation", "Provisional"])
    for i, r in enumerate(c["scored"] + c["unscored"], 1):
        res = r.get("result") or {}
        scored = res.get("status") == "SCORED"
        w.writerow([i if scored else "", r["displayName"], r["specialityText"], "" if r["baseScore"] is None else r["baseScore"],
                    FIT_LABEL.get((r.get("primary") or {}).get("fit") or "", ""), FIT_LABEL.get((r.get("secondary") or {}).get("fit") or "", ""),
                    res.get("discountPercent") if scored else "", res.get("adjustedScore") if scored else "",
                    res.get("status") or "", "Unrated" if r.get("estimateAccuracyScore") is None else r["estimateAccuracyScore"],
                    "Unrated" if r.get("trustworthinessScore") is None else r["trustworthinessScore"],
                    r.get("explanation", ""), "Yes" if r.get("provisional") else ""])
    return buf.getvalue().encode("utf-8-sig")


# ------------------------------------------------------------------ AI suggestions (provisional, attributed)
SUGGEST_SCHEMA = {"type": "object", "properties": {"fits": {"type": "array", "items": {"type": "object", "properties": {
    "agentId": {"type": "string"}, "genreId": {"type": "string"}, "fit": {"type": "string", "enum": list(FIT_LEVELS)},
    "rationale": {"type": "string"}}, "required": ["agentId", "genreId", "fit", "rationale"]}}}, "required": ["fits"]}


def suggest(project_id: str, engine, settings: dict, assessor: str = "Jonny (AI)") -> list[dict]:
    """Ask the AI engine for a provisional fit per company and scoring genre, from the register's speciality text
    (Jon: provisional research context, not a complete matrix). Recorded as PROVISIONAL with the AI as assessor;
    only genres still unassessed for this project are filled; a person can override any with a reason."""
    from . import llm
    proj = project(project_id)
    gids = [g for g in (proj["primaryGenreId"], proj["secondaryGenreId"]) if g]
    if not gids:
        raise ValueError("Give the project a genre first (Sales Estimates, Project).")
    reg = register()["agents"]
    todo = [(a, g) for a in reg for g in gids if current_fit(a["agentId"], project_id, g)["fit"] == "UNVERIFIED"]
    if not todo:
        return []
    system = ("You assess how well international film sales companies fit a film's genre, for Saracen Bridge. Use only "
              "the company's speciality description given. Levels: CORE = principal speciality; SECONDARY = established "
              "experience outside the main speciality; LIMITED = adjacent experience with few direct comparables; OUTSIDE = "
              "the description shows its focus is substantially elsewhere (say why); UNVERIFIED = the description doesn't "
              "speak to this genre. Never treat a genre the description doesn't mention as OUTSIDE: that is UNVERIFIED. "
              "One short rationale per answer, quoting the description.")
    lines = [f"Film: {proj['title']}. Genres to assess: " + ", ".join(f"{g} ({genre_name(g)})" for g in gids) +
             (f". Subgenre: {proj['subgenre']}" if proj["subgenre"] else "") + "."]
    lines += [f"{a['agentId']} {a['displayName']}: {a['specialityText']}" for a in reg]
    lines.append("Answer for every company and every genre listed.")
    out = llm.chat(engine, system, "\n".join(lines), schema=SUGGEST_SCHEMA, settings=settings, max_tokens=6000)
    done = []
    wanted = {(a["agentId"], g) for a, g in todo}
    for f in out.get("fits") or []:
        key = (f.get("agentId"), f.get("genreId"))
        if key not in wanted or f.get("fit") not in FIT_LEVELS:
            continue
        rationale = (f.get("rationale") or "").strip()
        if f["fit"] != "UNVERIFIED" and not rationale:
            continue
        assess(key[0], project_id, key[1], f["fit"], rationale, "Company register speciality text (dataVersion "
               f"{register()['dataVersion']})", assessor, "PROVISIONAL")
        wanted.discard(key)
        done.append({"agentId": key[0], "genreId": key[1], "fit": f["fit"]})
    return done
