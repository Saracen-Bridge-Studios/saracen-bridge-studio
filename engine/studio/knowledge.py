"""Jon's documents as a local search index, so Ask Jonny answers from Saracen Bridge's own methods and names its source.

Built from sources/ (Jon's GPT instructions, references and shared standards: Markdown and Word) into
data/knowledge.db (SQLite FTS5, BM25). Built at packaging time by scripts/build_knowledge.py; if the file is missing
it is built on first use into the user's data folder. Behaviour captures (sources/captures) and fill-in templates are
left out: they are one project's outputs, not method.
"""
from __future__ import annotations

import hashlib
import re
import sqlite3
import threading
from pathlib import Path

from . import refdata, store

DB_NAME = "knowledge.db"
CHUNK = 1600                     # characters per chunk: a section small enough to quote, big enough to make sense
TOOL_OF = {                      # source folder -> Studio tool (shared standards apply to every tool)
    "shared": "all", "t01_look_book": "lookbook", "t02_script_coverage": "coverage", "t03_schedule_budget": "schedule",
    "t04_sales_agent": "sales", "t05_brand_integration": "brand", "t06_location_incentive": "incentives",
    "t07_bfi_certification": "bfi", "t08_film_finance_greenlight": "greenlight", "t09_film_finance_dataroom": "greenlight",
    "fpm_finance_plan_modeller": "finance", "t10_agreement_builder": "agreement",
}
TOOL_NAME = {"lookbook": "Look Book Analytics", "coverage": "Script Coverage", "schedule": "Scheduling & Budgeting",
             "sales": "Sales Estimates", "brand": "Brand Integration", "incentives": "Location & Incentives",
             "bfi": "BFI Certification", "greenlight": "Greenlight & Closing", "finance": "Finance Plan",
             "agreement": "Term Sheet Builder", "all": "Saracen Bridge"}
SKIP_NAMES = ("Master_Report_Template", "TKE_SB_Static_Master")
# Words that put a question in another tool's territory. On a tool's page, another tool's documents are offered only when
# the question uses one of these (Tim, 13 Oct: "walk me through Finance Plan" came back with two BFI AVEC guides).
TOOL_WORDS = {"lookbook": ("look book", "lookbook", "deck", "pitch deck"), "coverage": ("coverage", "screenplay", "script"),
              "schedule": ("schedule", "scheduling", "budget", "crew", "rate card", "day out of days"),
              "sales": ("sales", "territory", "territories", "presale", "pre-sale", "actor", "director", "cast", "minimum guarantee"),
              "brand": ("brand", "placement", "sponsor"), "incentives": ("incentive", "rebate", "tax credit", "location", "gmot"),
              "bfi": ("bfi", "cultural test", "avec", "iftc", "certification", "british film"),
              "greenlight": ("greenlight", "green light", "closing", "data room", "bankab"),
              "finance": ("finance plan", "gap", "debt", "equity", "cashflow", "cash flow", "waterfall", "recoup"),
              "agreement": ("term sheet", "agreement", "contract")}
STOP = set("""a an and are as at be by can could do does for from had has have how i if in into is it its me my of on or
our should so than that the their them then there these this to was we what when where which who why will with would you
your about any all also just get got need want work works working use using tell show explain please""".split())

_LOCK = threading.Lock()


def sources_root() -> Path:
    return refdata.app_root() / "sources"


SKILL_LABEL = {"t08_film_finance_greenlight": "Greenlight", "t09_film_finance_dataroom": "Data Room",
               "t10_agreement_builder": "Term Sheet Builder"}


def _title(path: Path, tool: str, folder: str = "") -> str:
    stem = path.stem
    if stem.upper() == "SKILL":
        return f"{SKILL_LABEL.get(folder) or TOOL_NAME.get(tool, 'Saracen Bridge')}: Saracen Bridge GPT instructions"
    stem = re.sub(r"[-_ ]?(?:jan|feb|mar|apr|may|jun|jul|july|aug|sep|oct|nov|dec)[a-z]*[-_ ]?20\d\d$", "", stem, flags=re.I)
    return re.sub(r"\s+", " ", stem.replace("_", " ").replace("-", " ")).strip()


def _sections_md(text: str):
    """(heading path, body) per Markdown section, splitting on #, ##, ### and ####."""
    text = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.S)       # YAML front matter
    heads, body = [], []
    for line in text.splitlines():
        m = re.match(r"^(#{1,4})\s+(.*\S)\s*$", line)
        if m:
            if any(b.strip() for b in body):
                yield " / ".join(h for _, h in heads), "\n".join(body).strip()
            body = []
            lvl = len(m.group(1))
            heads = [h for h in heads if h[0] < lvl] + [(lvl, m.group(2).strip("# ").strip())]
        else:
            body.append(line)
    if any(b.strip() for b in body):
        yield " / ".join(h for _, h in heads), "\n".join(body).strip()


def _sections_docx(path: Path):
    from docx import Document
    from docx.table import Table
    from docx.text.paragraph import Paragraph
    doc = Document(str(path))
    heads, body = [], []
    for child in doc.element.body.iterchildren():
        tag = child.tag.rsplit("}", 1)[-1]
        if tag == "p":
            p = Paragraph(child, doc)
            t = p.text.strip()
            if not t:
                continue
            style = (p.style.name if p.style is not None else "") or ""
            m = re.match(r"Heading (\d)", style)
            if m or style == "Title":
                if body:
                    yield " / ".join(h for _, h in heads), "\n".join(body)
                body = []
                lvl = int(m.group(1)) if m else 0
                heads = [h for h in heads if h[0] < lvl] + [(lvl, t)]
            else:
                body.append(t)
        elif tag == "tbl":
            for row in Table(child, doc).rows:
                cells, seen = [], set()
                for c in row.cells:                                   # merged cells repeat: keep each once
                    ct = c.text.strip()
                    if ct and ct not in seen:
                        seen.add(ct)
                        cells.append(ct)
                if cells:
                    body.append(" | ".join(cells))
    if body:
        yield " / ".join(h for _, h in heads), "\n".join(body)


def _chunks(body: str):
    if len(body) <= CHUNK:
        yield body
        return
    buf = ""
    for para in re.split(r"\n\s*\n|\n(?=[-*•|] )", body):
        if buf and len(buf) + len(para) > CHUNK:
            yield buf.strip()
            buf = ""
        while len(para) > CHUNK:
            yield para[:CHUNK]
            para = para[CHUNK:]
        buf += ("\n" if buf else "") + para
    if buf.strip():
        yield buf.strip()


def documents(root: Path | None = None) -> list[tuple[Path, str]]:
    root = root or sources_root()
    out = []
    for p in sorted(root.rglob("*")):
        if p.suffix.lower() not in (".md", ".docx") or not p.is_file():
            continue
        rel = p.relative_to(root)
        tool = TOOL_OF.get(rel.parts[0])
        if not tool or any(s in p.name for s in SKIP_NAMES):
            continue
        out.append((p, tool))
    return out


def build(dest: Path, root: Path | None = None) -> dict:
    """(Re)build the index at dest. Returns counts."""
    root = root or sources_root()
    tmp = dest.with_suffix(".tmp")
    tmp.unlink(missing_ok=True)
    con = sqlite3.connect(tmp)
    con.execute("CREATE TABLE docs (id INTEGER PRIMARY KEY, title TEXT, tool TEXT, path TEXT, sha256 TEXT)")
    con.execute("CREATE VIRTUAL TABLE chunks USING fts5(title, heading, body, doc UNINDEXED, tool UNINDEXED, seq UNINDEXED, "
                "tokenize = 'porter unicode61 remove_diacritics 2')")
    n_docs = n_chunks = 0
    for path, tool in documents(root):
        try:
            secs = list(_sections_docx(path) if path.suffix.lower() == ".docx" else _sections_md(path.read_text(encoding="utf-8", errors="replace")))
        except Exception:  # noqa: BLE001 - one unreadable file never stops the index
            continue
        title = _title(path, tool, path.relative_to(root).parts[0])
        cur = con.execute("INSERT INTO docs (title, tool, path, sha256) VALUES (?,?,?,?)",
                          (title, tool, str(path.relative_to(root)).replace("\\", "/"), hashlib.sha256(path.read_bytes()).hexdigest()))
        seq = 0
        for heading, body in secs:
            for piece in _chunks(body):
                if len(piece) < 40:
                    continue
                con.execute("INSERT INTO chunks (title, heading, body, doc, tool, seq) VALUES (?,?,?,?,?,?)",
                            (title, heading, piece, cur.lastrowid, tool, seq))
                seq += 1
                n_chunks += 1
        n_docs += 1
    con.commit()
    con.execute("INSERT INTO chunks(chunks) VALUES ('optimize')")
    con.commit()
    con.close()
    tmp.replace(dest)
    return {"docs": n_docs, "chunks": n_chunks}


def _db_path() -> Path:
    shipped = refdata.app_root() / "data" / DB_NAME
    if shipped.exists():
        return shipped
    local = store.home() / DB_NAME
    with _LOCK:
        if not local.exists() and sources_root().exists():
            build(local)
    return local


def _query(text: str) -> str:
    words = [w.strip(".'’-").lower() for w in re.findall(r"[A-Za-z0-9][A-Za-z0-9'’.-]*", text or "")]
    terms = [w for w in dict.fromkeys(words) if len(w) > 1 and w not in STOP][:24]
    return " OR ".join('"' + t.replace('"', "") + '"' for t in terms)


def search(text: str, tool: str | None = None, k: int = 5, question: str | None = None) -> list[dict]:
    """Best sections of Jon's documents for this question. Sections from the page's own tool come first; another
    tool's documents only when the question itself (`question`, else `text`) is about that tool's subject."""
    q = _query(text)
    if not q:
        return []
    if not tool:                                       # off a tool's page, a question that names a tool is about it
        low = (question if question is not None else text).lower()
        tool = next((t for t, name in TOOL_NAME.items() if t != "all" and name.lower() in low), None)
    try:
        con = sqlite3.connect(f"file:{_db_path()}?mode=ro", uri=True)
    except sqlite3.Error:
        return []
    con.row_factory = sqlite3.Row
    sql = ("SELECT title, heading, body, tool, doc, seq, bm25(chunks, 3.0, 2.0, 1.0) AS score FROM chunks "
           "WHERE chunks MATCH ? {where} ORDER BY score LIMIT ?")
    try:
        found = []
        allowed = None
        if tool and tool in TOOL_NAME:
            found += [dict(r) for r in con.execute(sql.format(where="AND tool = ?"), (q, tool, 3))]
            low = (question if question is not None else text).lower()
            allowed = {tool, "all"} | {t for t, words in TOOL_WORDS.items() if any(w in low for w in words)}
        found += [dict(r) for r in con.execute(sql.format(where=""), (q, k * 4))
                  if allowed is None or r["tool"] in allowed]
    except sqlite3.Error:
        return []
    finally:
        con.close()
    out, seen = [], set()
    for r in found:
        key = (r["doc"], r["seq"])
        if key in seen:
            continue
        seen.add(key)
        out.append({"title": r["title"], "heading": r["heading"], "text": r["body"], "tool": r["tool"]})
        if len(out) == k:
            break
    return out
