"""Sales Estimates: reading an existing sales estimate (1.1.6).

Tim, 22 and 27 Oct: "after sales have an input for existing sales estimates with an ingest button". A sales company's
estimate is a table of territories with figures (ask and take, or high and low, sometimes a floor), as a spreadsheet,
a CSV, a Word table or a PDF. This reads any of those into the workbook's territories so it can sit beside the
Saracen Bridge valuation, territory by territory.

What it reads is shown for checking before it is kept: the territory each row was matched to, the figures and which
column each came from, the currency, whether the figures are in thousands, and every row it couldn't place. Nothing
here feeds the valuation itself: an estimate is a sales company's opinion, not a deal (DEAL_LOG takes deals).
"""
from __future__ import annotations

import csv
import io
import re

# the workbook's territories (Saracen Bridge Sales Valuation Engine v4.1, LISTS) and the names estimates use for them
ALIASES = {
    "USA": ["usa", "us", "u.s.", "u.s.a.", "united states", "north america", "domestic", "us/canada", "us & canada", "north american"],
    "Canada": ["canada", "english canada", "french canada"],
    "UK / Ireland": ["uk", "u.k.", "united kingdom", "uk/ireland", "uk & ireland", "uk and ireland", "great britain", "britain", "ireland", "uk/eire"],
    "Germany": ["germany", "german speaking", "german-speaking", "gsa", "germany/austria", "germany/austria/switzerland"],
    "France": ["france", "french speaking", "french-speaking", "francophone"],
    "Italy": ["italy"], "Spain": ["spain"],
    "Benelux": ["benelux", "netherlands", "holland", "belgium", "luxembourg"],
    "Scandinavia": ["scandinavia", "nordics", "nordic", "nordic countries", "sweden", "norway", "denmark", "finland", "iceland"],
    "Switzerland": ["switzerland"], "Austria": ["austria"], "Poland": ["poland"],
    "Eastern Europe (ex-Poland)": ["eastern europe", "east europe", "cee", "central and eastern europe", "former yugoslavia", "ex-yugoslavia",
                                   "czech republic", "czechia", "slovakia", "hungary", "romania", "bulgaria", "baltics", "baltic states"],
    "CIS": ["cis", "russia", "russia/cis", "ukraine"],
    "Greece": ["greece", "greece/cyprus"], "Portugal": ["portugal"], "Turkey": ["turkey", "türkiye", "turkiye"], "Israel": ["israel"],
    "Middle East (ex-Israel/Turkey)": ["middle east", "mena", "gulf", "gcc", "uae", "middle east/north africa", "arabic speaking", "pan-arab", "pan arab"],
    "South Africa": ["south africa", "southern africa"],
    "Japan": ["japan"], "South Korea": ["south korea", "korea", "s. korea"], "China": ["china", "mainland china", "prc"],
    "Hong Kong": ["hong kong", "hk"], "Taiwan": ["taiwan"], "India": ["india", "indian subcontinent"],
    "Australia / New Zealand": ["australia", "new zealand", "australia/nz", "australia/new zealand", "anz", "aus/nz"],
    "Brazil": ["brazil"], "Mexico": ["mexico"],
    "Rest of Latin America": ["latin america", "latam", "south america", "central america", "rest of latin america", "lat am",
                              "spanish latin america", "argentina", "chile", "colombia", "peru"],
    "Airlines": ["airlines", "airline", "inflight", "in-flight"],
    "Ships / Non-Theatrical": ["ships", "non-theatrical", "non theatrical", "ships/non-theatrical"],
    "Rest of World": ["rest of world", "row", "other", "others", "rest of asia", "southeast asia", "south east asia", "sea", "pan-asia",
                      "pan asia", "indonesia", "malaysia", "singapore", "thailand", "philippines", "vietnam", "pakistan", "africa"],
}
TOTAL = re.compile(r"(?i)^\s*(grand\s+)?total|^\s*worldwide|^\s*world\s*wide|^\s*all territories|^\s*sum\b")
HEAD = {"ask": re.compile(r"(?i)\bask|high|target|top|asking"), "take": re.compile(r"(?i)\btake|low|accept|bottom|walk"),
        "floor": re.compile(r"(?i)\bfloor|minimum|min\b")}
CURRENCY = [("USD", re.compile(r"\$|\bUSD\b|US\s*dollars?", re.I)), ("GBP", re.compile(r"£|\bGBP\b|sterling", re.I)),
            ("EUR", re.compile(r"€|\bEUR\b|euros?", re.I))]
THOUSANDS = re.compile(r"(?i)\(\s*0{3}\s*'?s?\s*\)|in\s+thousands|\$\s*0{3}|\b000s\b|\(k\)|\$k\b|usd\s*k\b|\(\$?\s*000\)")
NUM = re.compile(r"(?<![\w.])[$£€]?\s*(\d{1,3}(?:[,\s]\d{3})+|\d+)(?:\.(\d+))?\s*([kKmM])?(?![\w])")


def _key(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^\w/&'\- ]+", " ", s.lower())).strip()


_LOOKUP = {a: t for t, names in ALIASES.items() for a in names} | {t.lower(): t for t in ALIASES}


def territory(text: str) -> str | None:
    """The workbook territory a label means, or None. Longest alias first, so "Rest of Latin America" beats "Latin America"."""
    k = _key(text)
    if not k:
        return None
    if k in _LOOKUP:
        return _LOOKUP[k]
    for a in sorted(_LOOKUP, key=len, reverse=True):
        if len(a) > 2 and re.search(rf"(?<![\w]){re.escape(a)}(?![\w])", k):
            return _LOOKUP[a]
    return None


def covers(text: str) -> set[str]:
    """Every workbook territory a label names ("Germany / Austria" names two)."""
    k = _key(text)
    return {t for a, t in _LOOKUP.items() if len(a) > 2 and re.search(rf"(?<![\w]){re.escape(a)}(?![\w])", k)}


def numbers(cells: list[str]) -> list[tuple[int, float]]:
    """(column, value) for each figure in a row. 1.2m and 150k are expanded; a range "100-150" gives both ends."""
    out = []
    for i, c in enumerate(cells):
        for m in NUM.finditer(str(c or "")):
            whole = int(re.sub(r"[,\s]", "", m.group(1)))
            v = whole + (float("0." + m.group(2)) if m.group(2) else 0)
            mult = {"k": 1e3, "m": 1e6}.get((m.group(3) or "").lower(), 1)
            out.append((i, v * mult))
    return out


# ------------------------------------------------------------------------------------------------ rows from a file
def _rows_xlsx(data: bytes) -> list[list[str]]:
    import openpyxl
    wb = openpyxl.load_workbook(io.BytesIO(data), data_only=True, read_only=True)
    out = []
    for ws in wb.worksheets:
        for row in ws.iter_rows(values_only=True):
            cells = ["" if v is None else (f"{v:.0f}" if isinstance(v, float) and v.is_integer() else str(v)) for v in row]
            if any(c.strip() for c in cells):
                out.append(cells)
    return out


def _rows_csv(data: bytes) -> list[list[str]]:
    text = data.decode("utf-8-sig", errors="replace")
    try:
        dialect = csv.Sniffer().sniff(text[:4000], delimiters=",;\t|")
    except csv.Error:
        dialect = csv.excel
    return [r for r in csv.reader(io.StringIO(text), dialect) if any(c.strip() for c in r)]


def _rows_docx(data: bytes) -> list[list[str]]:
    import docx
    d = docx.Document(io.BytesIO(data))
    out = []
    for t in d.tables:
        for r in t.rows:
            cells = [c.text.strip() for c in r.cells]
            if any(cells):
                out.append(cells)
    out += [_split(p.text) for p in d.paragraphs if p.text.strip()]
    return out


def _split(line: str) -> list[str]:
    return [c.strip() for c in re.split(r"\s{2,}|\t|\s\|\s", line.strip()) if c.strip()]


def _rows_pdf(data: bytes) -> list[list[str]]:
    from pypdf import PdfReader
    out = []
    for page in PdfReader(io.BytesIO(data)).pages:
        for line in (page.extract_text(extraction_mode="layout") or "").splitlines():
            if line.strip():
                out.append(_split(line))
    return out


def rows_of(filename: str, data: bytes) -> list[list[str]]:
    n = filename.lower()
    if n.endswith((".xlsx", ".xlsm")):
        return _rows_xlsx(data)
    if n.endswith((".csv", ".tsv", ".txt")):
        return _rows_csv(data)
    if n.endswith(".docx"):
        return _rows_docx(data)
    if n.endswith(".pdf"):
        return _rows_pdf(data)
    raise ValueError("Send the estimate as a spreadsheet (.xlsx), CSV, Word (.docx) or PDF.")


# ------------------------------------------------------------------------------------------------ reading
def read(filename: str, data: bytes) -> dict:
    rows = rows_of(filename, data)
    if not rows:
        raise ValueError("The file has no table to read. If it is a scanned PDF, send the spreadsheet instead.")
    text = "\n".join(" ".join(r) for r in rows)
    currency = next((c for c, rx in CURRENCY if rx.search(text)), None)
    thousands = bool(THOUSANDS.search(text))
    cols: dict[str, int] = {}
    out, unplaced, stated_total = [], [], None
    for r in rows:
        label_cells = [c for c in r if c and not NUM.fullmatch(c.strip())]
        # a header row names the columns: Ask / Take / Floor (or High / Low)
        hits = {k: i for i, c in enumerate(r) for k, rx in HEAD.items() if c and rx.search(c) and not numbers([c])}
        if len(hits) >= 2 or (hits and not numbers(r)):
            cols = hits
            continue
        nums = numbers(r)
        if not nums:
            continue
        first = next((c for c in r if c.strip()), "")
        if TOTAL.search(first):
            stated_total = {"ask": max(v for _, v in nums), "take": min(v for _, v in nums), "as_written": " ".join(r)}
            continue
        terr = None
        for c in label_cells:
            terr = territory(c)
            if terr:
                break
        if not terr:
            if any(re.search(r"[A-Za-z]{3}", c) for c in label_cells):
                unplaced.append(" · ".join(c for c in r if c.strip())[:160])
            continue
        by_col = {k: next((v for i, v in nums if i == col), None) for k, col in cols.items()}
        if by_col.get("ask") is not None or by_col.get("take") is not None:
            ask, take, floor = by_col.get("ask"), by_col.get("take"), by_col.get("floor")
            how = "by column heading"
        else:
            vals = sorted({v for _, v in nums}, reverse=True)
            ask, take, floor = vals[0], (vals[1] if len(vals) > 1 else None), (vals[2] if len(vals) > 2 else None)
            how = "larger figure as ask" if len(vals) > 1 else "one figure"
        label = " ".join(c for c in label_cells if territory(c) == terr) or label_cells[0]
        out.append({"territory": terr, "as_written": label.strip()[:80], "ask": ask, "take": take, "floor": floor, "how": how,
                    "also": sorted(covers(label) - {terr})})
    # figures well under ten thousand in a film estimate are in thousands, whether or not it says so
    biggest = max([x["ask"] or 0 for x in out] or [0])
    if not thousands and out and biggest < 10_000:
        thousands, note = True, "The figures are all under 10,000, so they are read as thousands. Untick if they are whole amounts."
    else:
        note = "The estimate says its figures are in thousands." if thousands else ""
    if thousands:
        for x in out:
            for k in ("ask", "take", "floor"):
                if x[k] is not None:
                    x[k] *= 1000
        if stated_total:
            stated_total = {k: (v * 1000 if isinstance(v, (int, float)) else v) for k, v in stated_total.items()}
    merged: dict[str, dict] = {}
    for x in out:                              # two rows for one territory (e.g. Sweden and Norway): added together
        m = merged.get(x["territory"])
        if m:
            for k in ("ask", "take", "floor"):
                m[k] = (m[k] or 0) + (x[k] or 0) if (m[k] is not None or x[k] is not None) else None
            m["as_written"] += f" + {x['as_written']}"
        else:
            merged[x["territory"]] = dict(x)
    rows_out = list(merged.values())
    total = {k: sum(x[k] or 0 for x in rows_out) for k in ("ask", "take")}
    return {"file": filename, "rows": rows_out, "currency": currency or "USD", "currency_stated": bool(currency),
            "thousands": thousands, "note": note, "unplaced": unplaced[:30], "stated_total": stated_total, "total": total,
            "checks": _checks(rows_out, stated_total, total)}


def _checks(rows, stated, total) -> list[str]:
    out = []
    if not rows:
        out.append("No territory was recognised. Check the file is a territory-by-territory estimate.")
    if stated and stated.get("ask") and abs(stated["ask"] - total["ask"]) > max(1, 0.01 * stated["ask"]):
        out.append(f"The estimate's own total ask ({stated['ask']:,.0f}) differs from the rows read ({total['ask']:,.0f}): check for a row left out.")
    for x in rows:
        if x.get("also"):
            out.append(f"“{x['as_written']}” names more than one territory; read as {x['territory']} "
                       f"(also {', '.join(x['also'])}). Split the figure if the estimate means both.")
    bad = [x["territory"] for x in rows if x["ask"] is not None and x["take"] is not None and x["take"] > x["ask"]]
    if bad:
        out.append("Take above ask in " + ", ".join(bad) + ".")
    return out


def compare(estimate: dict, valuation: dict, usd_per_unit: float = 1.0) -> list[dict]:
    """The estimate beside the Saracen Bridge valuation, territory by territory, in USD."""
    ours = {t["territory"]: t for t in (valuation or {}).get("territories") or []}
    out = []
    for x in estimate.get("rows") or []:
        v = ours.get(x["territory"]) or {}
        ask = x["ask"] * usd_per_unit if x.get("ask") is not None else None
        take = x["take"] * usd_per_unit if x.get("take") is not None else None
        out.append({"territory": x["territory"], "their_ask": ask, "their_take": take, "our_ask": v.get("ask"), "our_take": v.get("take"),
                    "diff_ask": (ask / v["ask"] - 1) if ask and v.get("ask") else None})
    return out
