"""Sales Estimates: Jon's Sales Valuation Engine v4.1, run as Jon built it (1.0.5).

The engine is his workbook (sources/t04_sales_agent/.../Saracen_Bridge_Sales_Valuation_Engine_v4_1_Integrated_Imports.xlsx,
21,759 formulas). The Studio does not re-implement his model: it writes the project's inputs into the workbook's input
cells and evaluates his formulas as written (studio.xlcalc, an evaluator for exactly the functions he uses), then reads
CONTROLLED_OUTPUT, his "single approved interface". The filled workbook can be downloaded and opened in Excel, where
the same numbers recalculate.

His rules carried through unchanged: values come only from verified deal evidence (DEAL_LOG) or public buyer-economics
proxies (PUBLIC_PROXY_ANCHORS), or from an analyst's documented worldwide anchor allocated by his territory weights;
the budget fallback stays off; proxy values are capped at grade B; everything is in USD.
"""
from __future__ import annotations

import datetime as dt

from . import refdata

WORKBOOK = (refdata.app_root() / "sources" / "t04_sales_agent" / "skills" / "instructions" / "references"
            / "Saracen_Bridge_Sales_Valuation_Engine_v4_1_Integrated_Imports.xlsx")

# PROJECT_INTAKE rows (column B), in Jon's order
INTAKE = [("title", 6, "Title"), ("genre", 7, "Genre"), ("subgenre", 8, "Subgenre"), ("tone", 9, "Tone"),
          ("logline", 10, "Logline / synopsis"), ("script_status", 11, "Script status"), ("budget", 12, "Exact production budget"),
          ("budget_currency", 13, "Budget currency"), ("language", 14, "Original language"), ("country", 15, "Country of origin"),
          ("coproduction", 16, "Co-production status"), ("rating", 17, "Intended rating"), ("runtime", 18, "Expected runtime (minutes)"),
          ("director", 19, "Named director"), ("director_attachment", 20, "Director attachment status"),
          ("cast_summary", 21, "Principal cast summary"), ("cast_attachment", 22, "Cast attachment status"),
          ("producer", 23, "Lead producer / production company"), ("sales_stage", 24, "Sales stage"),
          ("production_status", 25, "Production status"), ("delivery_date", 26, "Anticipated delivery date"),
          ("release_model", 27, "Release model"), ("festival", 28, "Festival strategy"), ("sales_feedback", 29, "Known sales feedback"),
          ("audience", 30, "Target audience"), ("hook", 31, "Commercial hook"), ("ip", 32, "Underlying IP / source material"),
          ("scale", 33, "Expected production value / scale"), ("rights_summary", 34, "Rights availability summary")]
OPTIONAL = {"festival", "sales_feedback", "ip"}
NUMERIC = {"budget", "runtime"}

# attachment ladder as the workbook names it (ACTOR_IMPORT G / DIRECTOR_IMPORT E weights)
ATTACHMENT = ["Wish list", "Informal interest", "Availability confirmed", "Offer submitted", "Letter of intent",
              "Conditional agreement", "Signed agreement", "Pay-or-play"]
PACKAGE_FACTORS = [("producer", 21, "Producer / company"), ("script", 22, "Script and commercial hook"),
                   ("production_value", 23, "Production value"), ("rating", 24, "Rating / audience"),
                   ("language", 25, "Language / cultural exportability"), ("stage", 26, "Stage / delivery risk")]
SELECTION_FACTORS = ["genre", "cast", "director", "language", "budget", "stage", "rights"]


def _wb(data_only=False):
    import openpyxl
    return openpyxl.load_workbook(WORKBOOK, data_only=data_only)


def lists() -> dict:
    """The workbook's controlled lists (LISTS sheet), territories and currencies, for the screens."""
    wb = _wb()
    ws = wb["LISTS"]
    out = {}
    for c in range(1, ws.max_column + 1):
        vals = [ws.cell(r, c).value for r in range(1, ws.max_row + 1)]
        vals = [v for v in vals if v not in (None, "")]
        if vals:
            out[str(vals[0])] = [str(v) for v in vals[1:]]
    out["territories"] = [wb["RIGHTS_REGISTER"].cell(r, 1).value for r in range(5, 38)]
    out["attachment"] = ATTACHMENT
    return out


def fx_rates(overrides: dict | None = None) -> dict:
    """USD per unit for the workbook's currencies: Jon's ECB reference table (the incentive model, 25 Aug 2026) where it
    has the currency, then anything the user enters. Jon's FX_RATES sheet ships with GBP as a '1' identity rate although
    reporting is USD (register S-65); it is replaced here."""
    out = {"USD": 1.0}
    for cur in ("EUR", "GBP", "AUD", "CAD"):
        try:
            out[cur] = refdata.fx_usd_per_unit(cur)
        except KeyError:
            pass
    for k, v in (overrides or {}).items():
        try:
            if v not in (None, ""):
                out[k.upper()] = float(v)
        except (TypeError, ValueError):
            pass
    return out


def _date(v):
    if v in (None, ""):
        return None
    if isinstance(v, (dt.date, dt.datetime)):
        return v if isinstance(v, dt.datetime) else dt.datetime(v.year, v.month, v.day)
    try:
        return dt.datetime.fromisoformat(str(v)[:10])
    except ValueError:
        return None


def _num(v):
    try:
        return None if v in (None, "") else float(v)
    except (TypeError, ValueError):
        return None


def actor_record(name: str) -> dict | None:
    """Jon's Actor Value Database row mapped to ACTOR_IMPORT's columns. The 0–5 scores are his 0–100 scores / 20;
    his database rates confidence High / Medium / Low, read as grades A / B / C (register S-65)."""
    r = refdata.rows("""SELECT actor, commercial_tier, composite_cast_value, primary_market, territory_breadth, lead_carry,
        supporting_value, recent_momentum, confidence, last_reviewed, package_risk_notes FROM talent_actors WHERE actor = ?""", name)
    if not r:
        return None
    r = r[0]
    five = lambda v: None if _num(v) is None else round(_num(v) / 20, 2)
    return {"tier": r["commercial_tier"], "score": _num(r["composite_cast_value"]), "territory": r["primary_market"],
            "territory_score": five(r["territory_breadth"]), "lead_value": five(r["lead_carry"]), "supporting_value": five(r["supporting_value"]),
            "momentum": five(r["recent_momentum"]), "confidence": {"High": "A", "Medium": "B", "Low": "C"}.get(r["confidence"] or "", "D"),
            "reviewed": str(r["last_reviewed"] or "")[:10], "risk": r["package_risk_notes"] or ""}


def director_record(name: str) -> dict | None:
    """Jon's Director Value Database row mapped to DIRECTOR_IMPORT's columns (methodology core score 0–100; 0–10
    sub-scores / 2; confidence index 80+ A, 60+ B, 40+ C, else D)."""
    r = refdata.rows("""SELECT s.director_name, s.final_tier, s.methodology_core_score_100, s.adjusted_sales_10, s.adjusted_commercial_10,
        s.execution_confidence_10, s.confidence_index_100, s.last_reviewed, s.genre_authority, d.primary_working_territories,
        d.completion_bonding_notes FROM talent_director_scorecard s JOIN talent_directors d ON d.director_id = s.director_id
        WHERE s.director_name = ?""", name)
    if not r:
        return None
    r = r[0]
    half = lambda v: None if _num(v) is None else round(_num(v) / 2, 2)
    ci = _num(r["confidence_index_100"]) or 0
    return {"tier": r["final_tier"], "score": _num(r["methodology_core_score_100"]), "territory": r["primary_working_territories"] or "",
            "territory_score": half(r["adjusted_sales_10"]), "genre_fit": half(r["genre_authority"]), "budget_fit": None,
            "delivery": half(r["execution_confidence_10"]), "momentum": half(r["adjusted_commercial_10"]),
            "confidence": "A" if ci >= 80 else "B" if ci >= 60 else "C" if ci >= 40 else "D",
            "reviewed": str(r["last_reviewed"] or "")[:10], "risk": r["completion_bonding_notes"] or ""}


def writes(project: dict) -> dict:
    """Every input cell the project sets, as {"SHEET!A1": value}: blue input cells only, never a formula."""
    w: dict = {}
    put = lambda sheet, coord, v: w.__setitem__(f"{sheet}!{coord}", v)
    p = project or {}
    put("CONTROL_PANEL", "B6", p.get("project_id") or "SB-STUDIO")
    put("CONTROL_PANEL", "B8", _date(p.get("valuation_date")) or dt.datetime.combine(dt.date.today(), dt.time()))
    if p.get("report") in ("Producer-facing", "Lender-facing"):
        put("CONTROL_PANEL", "B20", p["report"])
    intake = p.get("intake") or {}
    for key, row, _ in INTAKE:
        v = intake.get(key)
        if v not in (None, ""):
            put("PROJECT_INTAKE", f"B{row}", _num(v) if key in NUMERIC else _date(v) if key == "delivery_date" and _date(v) else str(v))
    fx = fx_rates(p.get("fx"))
    for r, cur in enumerate(FX_ORDER, 5):
        if cur in fx and cur != "USD":
            put("FX_RATES", f"C{r}", fx[cur])
    for i, a in enumerate((p.get("actors") or [])[:99]):
        rec = actor_record(a.get("name", "")) or {}
        lead = str(a.get("billing") or "") in ("1", "2") or (a.get("role_type") or "").lower() in ("lead", "co-lead")
        vals = {"C": a.get("name"), "D": a.get("role") or "", "E": str(a.get("billing") or ""), "F": a.get("attachment") or "Wish list",
                "H": rec.get("tier"), "I": rec.get("score"), "J": rec.get("territory"), "K": rec.get("territory_score"),
                "L": _num(a.get("genre_fit")), "M": rec.get("lead_value") if lead else rec.get("supporting_value"),
                "N": rec.get("momentum"), "O": rec.get("confidence"), "P": rec.get("reviewed"), "Q": rec.get("risk"),
                "R": "Saracen_Bridge_Actor_Value_Database_v2_2" if rec else "Not in Jon's database: provisional"}
        for c, v in vals.items():
            if v not in (None, ""):
                put("ACTOR_IMPORT", f"{c}{9 + i}", v)
    for i, d in enumerate((p.get("directors") or [])[:49]):
        rec = director_record(d.get("name", "")) or {}
        vals = {"C": d.get("name"), "D": d.get("attachment") or "Wish list", "F": rec.get("tier"), "G": rec.get("score"),
                "H": rec.get("territory"), "I": rec.get("territory_score"), "J": rec.get("genre_fit"), "K": _num(d.get("budget_fit")),
                "L": rec.get("delivery"), "M": rec.get("momentum"), "N": rec.get("confidence"), "O": rec.get("reviewed"), "P": rec.get("risk"),
                "Q": "Saracen_Bridge_Director_Value_Database_V4_3" if rec else "Not in Jon's database: provisional"}
        for c, v in vals.items():
            if v not in (None, ""):
                put("DIRECTOR_IMPORT", f"{c}{10 + i}", v)
    rights = p.get("rights") or {}
    for r, t in enumerate(TERRITORIES, 5):
        x = rights.get(t) or {}
        for key, col in (("include", "B"), ("available", "C"), ("status", "D"), ("package", "E"), ("exclusivity", "G"),
                         ("offer_currency", "H"), ("offer_amount", "I"), ("buyer", "L"), ("bankable", "M"), ("evidence", "N"), ("notes", "O")):
            if x.get(key) not in (None, ""):
                put("RIGHTS_REGISTER", f"{col}{r}", _num(x[key]) if key == "offer_amount" else x[key])
    from openpyxl.utils import get_column_letter as L
    for i, f in enumerate((p.get("films") or [])[:500]):
        for c, key in enumerate(FILM_COLS, 1):
            v = f.get(key)
            if v not in (None, ""):
                put("FILM_MASTER", f"{L(c)}{5 + i}", _num(v) if key in ("year", "budget", "runtime") else v)
    deals = (p.get("deals") or [])[:500]
    for i, d in enumerate(deals):
        for c, key in DEAL_COLS.items():
            v = d.get(key)
            if v not in (None, ""):
                put("DEAL_LOG", f"{L(c)}{5 + i}", _date(v) if key in ("date", "verified_on") else
                    _num(v) if key in ("term", "amount", "rights_factor", "term_factor", "payment_factor") else v)
    proxies = (p.get("proxies") or [])[:500]
    for i, x in enumerate(proxies):
        for c, key in PROXY_COLS.items():
            v = x.get(key)
            if v not in (None, ""):
                put("PUBLIC_PROXY_ANCHORS", f"{L(c)}{5 + i}", _date(v) if key == "date" else
                    v if key in ("id", "film_id", "territory", "category", "include", "source", "note") else _num(v))
    factors = p.get("factors") or {}
    _select(put, "COMPARABLE_SELECTION", COMPARABLE_SLOTS, deals, factors, id_col="C", factor_cols="JKLMNOP", include_col="T")
    _select(put, "PROXY_SELECTION", PROXY_SLOTS, [x for x in proxies if x.get("territory") != "Global"], factors,
            id_col="C", factor_cols="IJKLMNO", include_col="S")
    anchor = p.get("anchor") or {}
    if _num(anchor.get("usd")) is not None:
        put("PROXY_ASSUMPTIONS", "B8", _num(anchor["usd"]))
        put("PROXY_ASSUMPTIONS", "E8", anchor.get("note") or "Analyst public-comparable anchor (Studio entry)")
    for key, row, _ in PACKAGE_FACTORS:
        v = _num((p.get("package_factors") or {}).get(key))
        if v is not None:
            put("PROXY_ASSUMPTIONS", f"B{row}", v)
    fin = p.get("finance") or {}
    for key, cell in (("soft", "B10"), ("equity", "B11"), ("other", "B12")):
        v = _num(fin.get(key))
        if v is not None:
            put("FINANCE_SUMMARY", cell, v)
    return w


def fill(project: dict):
    """Jon's workbook with the project's inputs written into its input cells, for Excel."""
    wb = _wb()
    for addr, v in writes(project).items():
        sheet, coord = addr.split("!")
        wb[sheet][coord] = v
    return wb


def _select(put, sheet: str, slots_by_territory: dict, records: list[dict], factors: dict, *, id_col, factor_cols, include_col):
    """Each record goes into the next free slot of its territory's block (10 per territory), with its adjustment
    factors (default 1, as the workbook ships)."""
    free = {t: list(rows) for t, rows in slots_by_territory.items()}
    for rec in records:
        rows = free.get(rec.get("territory"))
        if not rows:
            continue                           # no block for that territory, or all 10 slots used (reported in flags)
        r = rows.pop(0)
        put(sheet, f"{id_col}{r}", rec.get("id"))
        f = factors.get(rec.get("id")) or {}
        for col, key in zip(factor_cols, SELECTION_FACTORS):
            v = _num(f.get(key))
            if v is not None:
                put(sheet, f"{col}{r}", v)
        if f.get("include") in ("Y", "N"):
            put(sheet, f"{include_col}{r}", f["include"])


def _layout():
    """Territory order, FX order and selection blocks, read once from Jon's workbook."""
    wb = _wb()
    terr = [wb["RIGHTS_REGISTER"].cell(r, 1).value for r in range(5, 38)]
    fxo = [wb["FX_RATES"].cell(r, 1).value for r in range(5, 26)]
    blocks = {}
    for name in ("COMPARABLE_SELECTION", "PROXY_SELECTION"):
        b: dict = {}
        ws = wb[name]
        for r in range(5, ws.max_row + 1):
            t = ws.cell(r, 1).value
            if t:
                b.setdefault(t, []).append(r)
        blocks[name] = b
    return terr, fxo, blocks["COMPARABLE_SELECTION"], blocks["PROXY_SELECTION"]


FILM_COLS = ["id", "title", "year", "genre", "subgenre", "tone", "budget_currency", "budget", "language", "country", "rating",
             "runtime", "director", "cast", "cast_tier", "sales_agent", "stage_at_sale", "release_model", "festival",
             "box_office", "streaming", "source", "notes"]
DEAL_COLS = {1: "id", 2: "film_id", 4: "territory", 5: "date", 6: "stage", 7: "buyer", 8: "agent", 9: "package", 10: "term",
             11: "exclusivity", 12: "currency", 13: "amount", 16: "rights_factor", 17: "term_factor", 18: "payment_factor",
             20: "evidence_type", 21: "grade", 23: "source", 24: "verified_by", 25: "verified_on", 26: "notes"}
PROXY_COLS = {1: "id", 2: "film_id", 4: "territory", 5: "date", 6: "category", 7: "box_office_usd", 8: "rental_rate",
              9: "ancillary_usd", 10: "pa_usd", 11: "overhead_usd", 12: "margin", 15: "rights_factor", 16: "relevance",
              17: "source_weight", 20: "include", 21: "source", 22: "note"}
try:
    TERRITORIES, FX_ORDER, COMPARABLE_SLOTS, PROXY_SLOTS = _layout()
except Exception:  # noqa: BLE001 - the workbook missing from a broken install: the API says so
    TERRITORIES, FX_ORDER, COMPARABLE_SLOTS, PROXY_SLOTS = [], [], {}, {}


_ENGINE = {"book": None, "base": None, "set": set()}
_LOCK = __import__("threading").Lock()


def _engine():
    """Jon's workbook parsed once and kept in memory; each valuation writes its inputs and re-evaluates."""
    if _ENGINE["book"] is None:
        from . import xlcalc
        import openpyxl
        book = xlcalc.Book(openpyxl.load_workbook(WORKBOOK))
        _ENGINE["book"], _ENGINE["base"] = book, {sh: dict(cells) for sh, cells in book.cells.items()}
    return _ENGINE["book"]


def _base_value(addr: str):
    from openpyxl.utils import column_index_from_string
    from . import xlcalc
    sheet, coord = addr.split("!")
    m = xlcalc.REF_RX.match(coord)
    return _ENGINE["base"][sheet].get((int(m.group("r1")), column_index_from_string(m.group("c1"))))


def evaluate(project: dict) -> dict:
    """Write the project's inputs into Jon's workbook and read CONTROLLED_OUTPUT and the controls."""
    with _LOCK:
        xl = _engine()
        new = writes(project)
        for addr in _ENGINE["set"] - set(new):            # inputs the previous project set and this one doesn't
            sheet, coord = addr.split("!")
            xl.set(sheet, coord, _base_value(addr))
        for addr, v in new.items():
            sheet, coord = addr.split("!")
            xl.set(sheet, coord, v)
        _ENGINE["set"] = set(new)
        ev = lambda a: _clean(xl.evaluate(a))
        terr = []
        for r in range(15, 48):
            row = {k: ev(f"CONTROLLED_OUTPUT!{c}{r}") for k, c in (("territory", "E"), ("package", "F"), ("sale_status", "G"),
                   ("method", "H"), ("ask", "I"), ("expected", "J"), ("take", "K"), ("existing", "L"), ("unsold_take", "M"),
                   ("bankable", "N"), ("confidence", "O"), ("evidence_count", "P"), ("rationale", "Q"), ("status", "R"))}
            row["basis"] = ev(f"VALUATION_OUTPUT!T{r - 8}")
            terr.append(row)
        vd = ev("CONTROL_PANEL!B8")
        return {
            "territories": terr,
            "summary": {"ask": ev("CONTROLLED_OUTPUT!A12"), "expected": ev("CONTROLLED_OUTPUT!D12"), "take": ev("CONTROLLED_OUTPUT!G12"),
                        "net_producer_receipts": ev("CONTROLLED_OUTPUT!J12"), "intake_completeness": ev("CONTROLLED_OUTPUT!B7"),
                        "cast_factor": ev("CONTROLLED_OUTPUT!B8"), "director_factor": ev("CONTROLLED_OUTPUT!D8"),
                        "actor_import": ev("CONTROLLED_OUTPUT!D7"), "director_import": ev("CONTROLLED_OUTPUT!F7"),
                        "package_factor": ev("PROXY_ASSUMPTIONS!B27"), "anchor_usd": ev("PROXY_ASSUMPTIONS!B13"),
                        "anchor_basis": ev("PROXY_ASSUMPTIONS!B14"), "report": ev("CONTROL_PANEL!B20"),
                        "valuation_date": (dt.datetime(1899, 12, 30) + dt.timedelta(days=vd)).date().isoformat() if isinstance(vd, (int, float)) else vd},
            "finance": {"budget_usd": ev("FINANCE_SUMMARY!B9"), "requirement_usd": ev("FINANCE_SUMMARY!B13"),
                        "scenarios": [{"scenario": ev(f"FINANCE_SUMMARY!A{r}"), "gross": ev(f"FINANCE_SUMMARY!B{r}"),
                                       "commission": ev(f"FINANCE_SUMMARY!C{r}"), "expenses": ev(f"FINANCE_SUMMARY!D{r}"),
                                       "collection": ev(f"FINANCE_SUMMARY!E{r}"), "net": ev(f"FINANCE_SUMMARY!F{r}"),
                                       "coverage": ev(f"FINANCE_SUMMARY!G{r}")} for r in (18, 19, 20)],
                        "existing_sales": ev("FINANCE_SUMMARY!B24"), "unsold_take": ev("FINANCE_SUMMARY!B25"),
                        "bankable": ev("FINANCE_SUMMARY!B26"), "bankable_coverage": ev("FINANCE_SUMMARY!B27"),
                        "lender_result": ev("FINANCE_SUMMARY!B28")},
            "controls": {"order": ev("VALUATION_OUTPUT!B44"), "fx": ev("VALUATION_OUTPUT!B45"), "selection": ev("VALUATION_OUTPUT!B46")},
            "flags": _flags(project, ev),
        }


def _flags(project: dict, ev) -> list[str]:
    """Rows the workbook marks for review: incomplete imports, deal and proxy control flags, full territory blocks."""
    out = []
    for i, a in enumerate((project.get("actors") or [])[:99]):
        s = ev(f"ACTOR_IMPORT!T{9 + i}")
        if s and s != "Complete":
            out.append(f"Actor {a.get('name')}: {s}")
    for i, d in enumerate((project.get("directors") or [])[:49]):
        s = ev(f"DIRECTOR_IMPORT!S{10 + i}")
        if s and s != "Complete":
            out.append(f"Director {d.get('name')}: {s}")
    for i, x in enumerate((project.get("proxies") or [])[:500]):
        s = ev(f"PUBLIC_PROXY_ANCHORS!W{5 + i}")
        if s and s != "OK":
            out.append(f"Proxy {x.get('id')}: {s}")
    from collections import Counter
    for kind, recs in (("deals", project.get("deals") or []), ("proxies", [x for x in project.get("proxies") or [] if x.get("territory") != "Global"])):
        for t, n in Counter(r.get("territory") for r in recs).items():
            if n > 10:
                out.append(f"{t}: {n} {kind}; the engine uses the first 10.")
    return out


def _clean(v):
    """Excel errors as their code ('#N/A'); whole numbers as ints; NaN as blank."""
    from . import xlcalc
    if isinstance(v, xlcalc.Err):
        return v.code
    if isinstance(v, float):
        if v != v:
            return None
        if v.is_integer() and abs(v) < 1e15:
            return int(v)
    return v


def workbook_bytes(project: dict) -> bytes:
    """The filled workbook, for Excel. Formulas are left in place; Excel recalculates them on open."""
    import io
    wb = fill(project)
    try:
        wb.calculation.fullCalcOnLoad = True
    except AttributeError:
        pass
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()
