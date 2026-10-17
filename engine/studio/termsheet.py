"""Finance Plan: reading term sheets into the plan (1.0.8).

Jon's Finance Plan Modeller instructions (sources/fpm_finance_plan_modeller SKILL.md) set the controls this follows:
keep committed, conditional, targeted and speculative sources separate; do not assume transferability, lender
acceptance, advance rate, timing, fees or haircut; unknown values stay unconfirmed and keep the result PRELIMINARY,
never zero; and never count a receivable and the loan secured against it as two permanent sources.

The model reads the term sheet and lists each instrument in it with its terms and the words that show how binding it
is. The Studio then checks it against the document: an amount that doesn't appear in the text is flagged and the
source treated as an assumption; a source is never shown as more committed than the document's own words allow
("non-binding", "letter of intent", "subject to contract", "conditions precedent"). The user reviews every line
before it goes into the plan.
"""
from __future__ import annotations

import io
import re

from . import llm, refdata

SKILL = refdata.app_root() / "sources" / "fpm_finance_plan_modeller" / "skills" / "instructions" / "SKILL.md"
STATUSES = ["Confirmed cash", "Signed but conditional", "Draft / conditional", "LOI / non-binding", "User instruction / to document",
            "Assumption only", "Missing"]
INSTRUMENTS = ["Equity", "Convertible loan note", "Senior debt", "Gap / mezzanine debt", "Tax credit or incentive loan",
               "Pre-sale / minimum guarantee", "Soft money / grant", "In-kind / services", "Deferment", "Other"]
DEBT = {"Senior debt", "Gap / mezzanine debt", "Tax credit or incentive loan", "Convertible loan note"}
NON_CASH = {"In-kind / services", "Deferment"}
MAX_CHARS = 60000


def text_of(filename: str, data: bytes) -> str:
    name = filename.lower()
    if name.endswith(".pdf"):
        from pypdf import PdfReader
        pages = [(p.extract_text() or "") for p in PdfReader(io.BytesIO(data)).pages]
        from . import ocr
        if ocr.is_scanned(pages) and ocr.available():
            pages = ocr.pdf_pages(data, filename)
        return "\n\n".join(pages).strip()
    if name.endswith(".docx"):
        import docx
        d = docx.Document(io.BytesIO(data))
        parts = [p.text for p in d.paragraphs if p.text.strip()]
        for t in d.tables:
            for r in t.rows:
                parts.append(" | ".join(dict.fromkeys(c.text.strip() for c in r.cells)))
        return "\n".join(parts).strip()
    if name.endswith((".txt", ".md")):
        return data.decode("utf-8", errors="replace").strip()
    raise ValueError("Use a PDF, Word (.docx) or text file.")


# ---------------------------------------------------------------- amounts in the document

NUM = re.compile(r"(?<![\w.])(\d{1,3}(?:[,\s]\d{3})+|\d+(?:\.\d+)?)\s*(million|mn|m|k|thousand|bn|billion)?\b", re.I)
SCALE = {"million": 1e6, "mn": 1e6, "m": 1e6, "k": 1e3, "thousand": 1e3, "bn": 1e9, "billion": 1e9}


def amounts_in(text: str) -> set[float]:
    out = set()
    for m in NUM.finditer(text):
        try:
            v = float(re.sub(r"[,\s]", "", m.group(1)))
        except ValueError:
            continue
        out.add(v * SCALE.get((m.group(2) or "").lower(), 1))
    return out


def in_document(amount: float | None, found: set[float]) -> bool:
    return amount is not None and any(abs(amount - v) <= max(1.0, abs(amount) * 0.005) for v in found)


def binding_cap(text: str) -> str | None:
    """The most committed status the document's own words allow."""
    t = text.lower()
    if re.search(r"non[- ]binding|letter of intent|\bloi\b|indicative (?:terms|offer)|expression of interest", t):
        return "LOI / non-binding"
    if re.search(r"subject to contract|\bdraft\b|for discussion|heads of terms", t):
        return "Draft / conditional"
    if re.search(r"conditions? precedent|subject to|conditional (?:up)?on", t):
        return "Signed but conditional"
    return None


def cap(status: str, limit: str | None) -> str:
    if not limit or status not in STATUSES[:4]:
        return status
    return STATUSES[max(STATUSES.index(status), STATUSES.index(limit))]


# ---------------------------------------------------------------- the read

def _obj(props: dict) -> dict:
    return {"type": "object", "properties": props, "required": list(props), "additionalProperties": False}


S = {"type": "string"}
SCHEMA = _obj({
    "instruments": {"type": "array", "maxItems": 12, "items": _obj({
        "provider": S, "recipient": S, "instrument": {"type": "string", "enum": INSTRUMENTS},
        "amount": {"type": ["number", "null"]}, "currency": S, "amount_words": S,
        "status": {"type": "string", "enum": STATUSES[:6]}, "status_words": S,
        "interest": S, "fees": S, "term": S, "security": S, "recoupment": S,
        "conditions": {"type": "array", "maxItems": 10, "items": S}, "key_dates": {"type": "array", "maxItems": 8, "items": S}})},
    "parties": S, "governing_law": S, "notes": {"type": "array", "maxItems": 8, "items": S}})


def _rules() -> str:
    raw = SKILL.read_text(encoding="utf-8")
    m = re.search(r"FINANCE CONTROLS\n(.*?)(?=\nREQUIRED OUTPUT)", raw, re.S)
    return m.group(1).strip() if m else ""


def read(filename: str, data: bytes, settings: dict, mode: str | None = None) -> dict:
    text = text_of(filename, data)
    if len(text) < 80:
        raise ValueError("No readable text in that file.")
    ms = llm.mode_settings(settings, mode)
    engine, why = llm.resolve(settings, ms["mode"])
    if not engine:
        raise llm.EngineError(why)
    think = bool(ms["think"])
    system = ("You are Saracen Bridge Financial Modeller reading a film finance term sheet. Use UK English. Apply these controls:\n"
              + _rules() + "\n\nTASK: List every financing instrument the document offers or describes: the provider (the lender, investor, "
              "buyer or fund that puts the money in; never the borrower or producer receiving it), the recipient, what kind it is, "
              "the amount and currency exactly as written (amount null if the document gives none; amount_words the words it is "
              "written in), how binding it is (status) with the exact words that show it (status_words: 'non-binding', 'subject to "
              "contract', 'executed', 'conditions precedent'), and interest, fees, term, security, recoupment position, conditions "
              "precedent and key dates as stated ('Not stated' where the document is silent). Never fill a gap with a typical "
              "market figure. Plain text, no markdown.")
    body = text[:MAX_CHARS]
    out = llm.chat(engine, system, f"TERM SHEET ({filename}):\n\n{body}", schema=SCHEMA, settings=settings,
                   max_tokens=3000 + (3000 if think else 0), temperature=0.1, think=think, think_budget=3000 if think else None)
    found = amounts_in(text)
    limit = binding_cap(text)
    rows, checks = [], []
    for i, ins in enumerate(out.get("instruments") or []):
        amt = ins.get("amount")
        ok = amt is None or in_document(float(amt), found)
        status = cap(ins.get("status") or "Assumption only", limit)
        if amt is not None and not ok:
            checks.append(f"{ins.get('provider') or 'An instrument'}: the amount {amt:,.0f} doesn't appear in the document as read. "
                          "Treated as an assumption; check the figure.")
            status = "Assumption only"
        if status != ins.get("status"):
            ins["status_note"] = f"Shown as {status}: the document says {ins.get('status_words') or 'it is conditional'}."
        rows.append({"id": f"ts{i + 1}", "name": f"{ins.get('provider') or 'Unnamed provider'}: {ins.get('instrument')}",
                     "amount": None if amt is None else float(amt), "currency": (ins.get("currency") or "").upper()[:3],
                     "status": status, "cash": ins.get("instrument") not in NON_CASH, "is_debt": ins.get("instrument") in DEBT,
                     "amount_in_document": ok, "terms": ins})
    if limit:
        checks.append(f"The document's own words limit every source to {limit} or less committed.")
    if any(r["amount"] is None for r in rows):
        checks.append("At least one instrument has no amount in the document: it stays Unknown in the plan, never zero.")
    if len({r["currency"] for r in rows if r["currency"]}) > 1:
        checks.append("More than one currency: convert at a dated rate before adding them to one plan.")
    if not rows:
        checks.append("No financing instrument found in this document.")
    return {"file": filename, "characters": len(text), "truncated": len(text) > MAX_CHARS, "parties": out.get("parties") or "",
            "governing_law": out.get("governing_law") or "", "notes": out.get("notes") or [], "rows": rows, "checks": checks,
            "made_with": {"engine": engine.kind, "model": engine.model, "mode": ms["mode"]}}
