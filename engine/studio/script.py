"""Screenplay intake: Fountain, Final Draft (.fdx), PDF and plain text -> scene index + cast summary.

Deterministic and offline. This is the shared script reader for Coverage, Schedule & Budget,
Brand Integration and BFI (register R-04). Page counts are exact for PDF and estimated
(56 lines per page) for text formats.
"""
from __future__ import annotations

import io
import math
import re
from pathlib import Path
import xml.etree.ElementTree as ET
from collections import OrderedDict

# "INT. ", "INT " and (Tim's "Ultimate Feature" draft, 15 Oct: 150 headings, 12 read) "INT: " / "EXT.: "
HEADING = re.compile(r"^(?:\.(?!\.)|(INT\.?/EXT|EXT\.?/INT|I/E|INT|EXT|EST)(?:\.?:|[\.\s]))\s*(.*)$", re.I)
CUE = re.compile(r"^([A-Z0-9][A-Z0-9 .'\-#&]{0,40}?)(\s*\((?:V\.O\.|O\.S\.|O\.C\.|CONT'D|CONT’D|CONTD|PRE-LAP|[^)]{1,20})\))*\s*\^?$")
NOT_CUES = {"FADE IN", "FADE OUT", "CUT TO", "THE END", "CONTINUED", "MORE", "DISSOLVE TO", "SMASH CUT TO",
            "MATCH CUT TO", "INTERCUT", "BACK TO SCENE", "TITLE", "SUPER", "MONTAGE", "END MONTAGE", "LATER"}
TIMES = ("NIGHT", "DAY", "DAWN", "DUSK", "MORNING", "EVENING", "AFTERNOON", "CONTINUOUS", "LATER", "SUNSET", "SUNRISE",
         "SAME TIME", "RESUMING", "SIMULTANEOUS", "MAGIC HOUR")


# Bump when reading changes, so scripts already in the Library are read again (13 Oct: WEREWOLF, 133 scenes read as 1).
PARSER_VERSION = 6                                        # 4: scanned PDFs read by OCR (1.0.6); 5: registration lines aren't titles (1.1.1); 6: Windows line endings (1.2.0)

SCENE_NO = r"[A-Z]?\d{1,4}[A-Z]{0,3}"


def _unnumber(s: str) -> str:
    """Production drafts print the scene number at both margins and revision asterisks on the right:
    '12A   INT. RESTAURANT - NIGHT     12A *'. Return the bare heading when the middle is one; otherwise s unchanged.
    (13 Oct: Tim's 100-page Final Draft PDF read as 0 scenes because every heading started with its number.)"""
    t = re.sub(r"(\s+\*+)+\s*$", "", s.strip())
    m = re.match(rf"^({SCENE_NO})\.?\s+(.+)$", t)
    if not m:
        return s
    rest = m.group(2)
    # some PDFs put the right-margin number first, glued to the heading: "1      1EXT. DEEP FOREST - NIGHT"
    # (Tim's WEREWOLF draft, 13 Oct: 135 scenes read as 1)
    rest = re.sub(rf"^{SCENE_NO}\.?\s*(?=(?:INT|EXT|I/E|EST)\b)", "", rest, flags=re.I)
    if not HEADING.match(rest):
        return s
    return re.sub(rf"\s+{SCENE_NO}\.?$", "", rest).strip()


def _split_heading(text: str) -> dict:
    t = text.strip()
    m = HEADING.match(t)
    prefix = (m.group(1) or "").upper().replace(".", "") if m else ""
    rest = (m.group(2) if m else t).strip()
    ie = "INT/EXT" if "/" in prefix else ("INT" if prefix == "INT" else "EXT" if prefix == "EXT" else prefix or "")
    loc, tod = rest, ""
    parts = re.split(r"\s+[-–—]\s+", rest)
    if len(parts) > 1 and any(w in parts[-1].upper() for w in TIMES):
        loc, tod = " - ".join(parts[:-1]), parts[-1].upper()
    loc = loc.replace("\u2019", "'").replace("\u2018", "'")     # EMILY’S and EMILY'S are one location
    return {"heading": t.lstrip(".").strip(), "int_ext": ie, "location": loc.strip().upper(), "time_of_day": tod}


def _cue_name(line: str) -> str | None:
    s = line.strip()
    if not s or len(s) > 45 or s != s.upper() or not re.search(r"[A-Z]", s):
        return None
    if HEADING.match(s) or s.endswith("TO:") or s.endswith(":"):
        return None
    m = CUE.match(s.lstrip("@"))
    if not m:
        return None
    name = m.group(1).strip()
    if name in NOT_CUES or name.replace(" ", "").isdigit():
        return None
    return name


def _is_heading(s: str, forced: bool) -> bool:
    """A scene heading line. A leading "." forces one only in Fountain, and only before some text: in a PDF a wrapped
    line can start with "." (".45 calibre", or a lone full stop), which read as an empty scene (1.0.6)."""
    if s.startswith("."):
        return forced and bool(re.match(r"^\.(?!\.)\s*\w", s))
    return bool(HEADING.match(s)) and s.upper() == s


def _from_lines(lines: list[str], forced: bool = False) -> list[dict]:
    """Generic screenplay text -> scenes, using blank-line structure and all-caps character cues."""
    scenes, cur = [], None
    for i, raw in enumerate(lines):
        line = raw.rstrip()
        s = _unnumber(line.strip())
        if not s:
            continue
        if _is_heading(s, forced):
            cur = _split_heading(s) | {"characters": OrderedDict(), "lines": 0, "start": i}
            scenes.append(cur)
            continue
        if cur is None:
            continue
        cur["lines"] += 1
        prev_blank = i == 0 or not lines[i - 1].strip()
        nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
        name = _cue_name(s)
        if name and prev_blank and nxt and not HEADING.match(nxt):
            cur["characters"][name] = cur["characters"].get(name, 0) + 1
    return scenes


def _text(data: bytes) -> str:
    """Screenplay text as the parsers expect it: UTF-8 (a Windows byte-order mark dropped) with \n line endings.
    A .fountain saved on Windows ends its lines with \r\n, which hid the blank line after the title page, so the
    whole script was taken for a title page and read as no scenes (1.2.0)."""
    return data.decode("utf-8-sig", errors="replace").replace("\r\n", "\n").replace("\r", "\n")


def parse_fountain(text: str) -> dict:
    title = ""
    body = text
    head = text.split("\n\n", 1)
    if head and re.match(r"^\s*Title\s*:", head[0], re.I | re.M):
        m = re.search(r"^\s*Title\s*:\s*(.+)$", head[0], re.I | re.M)
        title = m.group(1).strip() if m else ""
        body = head[1] if len(head) > 1 else ""
    lines = _fountain_lines(body)
    return _summarise(title, _from_lines(lines, forced=True), est_pages=len(lines) / 56, fmt="Fountain")


def _fountain_lines(body: str) -> list[str]:
    body = re.sub(r"/\*.*?\*/", "", body, flags=re.S)      # boneyard
    body = re.sub(r"\[\[.*?\]\]", "", body, flags=re.S)    # notes
    return body.splitlines()


def parse_fdx(data: bytes) -> dict:
    root = ET.fromstring(data)
    title = ""
    tp = root.find(".//TitlePage")
    if tp is not None:
        texts = ["".join(t.itertext()).strip() for t in tp.iter("Paragraph")]
        title = next((t for t in texts if t), "")
    scenes, cur, nlines = [], None, 0
    for p in root.iter("Paragraph"):
        if tp is not None and p in list(tp.iter("Paragraph")):
            continue
        kind = p.get("Type", "")
        text = "".join(t.text or "" for t in p.iter("Text")).strip()
        if not text:
            continue
        nlines += max(1, len(text) // 60)
        if kind == "Scene Heading":
            cur = _split_heading(text) | {"characters": OrderedDict(), "lines": 0}
            scenes.append(cur)
        elif cur is not None:
            cur["lines"] += 1
            if kind == "Character":
                name = _cue_name(text.upper()) or text.upper().split("(")[0].strip()
                cur["characters"][name] = cur["characters"].get(name, 0) + 1
    return _summarise(title, scenes, est_pages=nlines / 56, fmt="Final Draft")


def _pdf_pages(data: bytes) -> list[str]:
    from pypdf import PdfReader
    return [(page.extract_text(extraction_mode="layout") or "") for page in PdfReader(io.BytesIO(data)).pages]


def _pdf_source(data: bytes, name: str = "") -> tuple[list[str], list[int], list[str], bool]:
    """The lines the PDF reader works from, the PDF page of each line, the page texts, and whether it was scanned.
    The breakdown and the scene texts given to the model both come from here, so their scene numbers agree."""
    from . import ocr
    pages = _pdf_pages(data)
    scanned = ocr.is_scanned(pages)
    if scanned and ocr.available():                        # 1.0.6: a scanned script is read by OCR (register S-12)
        pages = ocr.pdf_pages(data, name)
    lines, page_of = [], []
    for n, txt in enumerate(pages, 1):
        for ln in txt.splitlines() + [""]:
            lines.append(ln)
            page_of.append(n)
    return lines, page_of, pages, scanned


def parse_pdf(data: bytes, name: str = "") -> dict:
    from . import ocr
    lines, _, pages, scanned = _pdf_source(data, name)
    res = _summarise(_pick_title(lines), _from_lines(lines), est_pages=None, fmt="PDF (scanned, read by OCR)" if scanned and ocr.available() else "PDF")
    res["pages"] = len(pages)
    res["pages_estimated"] = False
    res["ocr"] = bool(scanned and ocr.available())
    if res["ocr"]:
        res["warnings"].append("Scanned PDF, read by OCR: check character names and scene headings against the script.")
    if not res["scenes"]:
        res["warnings"].append("No scene headings found. The PDF may be scanned (image only) and OCR isn't available in this copy."
                               if scanned and not ocr.available() else "No scene headings found in this PDF.")
    return res


def parse(filename: str, data: bytes) -> dict:
    name = filename.lower()
    if name.endswith(".fdx"):
        res = parse_fdx(data)
    elif name.endswith(".pdf"):
        res = parse_pdf(data, filename)
    else:
        res = parse_fountain(_text(data))
    res["title"] = clean_title(re.sub(r"^\s*title\s*:\s*", "", res["title"] or "", flags=re.I)) or title_from_filename(Path(filename).stem)
    res["parser"] = PARSER_VERSION
    return res


CREDIT = re.compile(r"(?i)^(?:(?:written|created|directed|produced|screenplay|teleplay|story|adapted|developed)\b.*|"
                    r"b\s*y|.*\bb\s*y\s*$|based (?:on|upon)\b.*|an? .{0,30}(?:film|production|presentation)\b.*)$")
NOT_TITLE = re.compile(r"(?i)\b(?:draft|final|edit|revis\w*|version|copyright|all rights|confidential|contact|"
                       r"regist(?:ered|ration)|writers?'?s?'? guild|wga|wggb|"
                       r"www\.|@|page \d)\b|\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}|^\(?\d[\d .()+-]{6,}$|^\d+\.?$|©")


SCRIPT_STARTS = re.compile(r"(?i)^(?:fade in|fade up|open on|cold open|black screen|over black)\b")   # page 1 of the script


def _pick_title(lines: list[str]) -> str:
    """The title from the title page, or "" when the page has none in its text (a logo, say). Credits, dates and
    draft notes are skipped, and so is the name after a credit (Tim's WEREWOLF draft, 13 Oct: the "title" read
    "Written and Created b y", and the name below it is the writer's)."""
    after_credit = False
    for raw in lines[:60]:
        t = re.sub(r"\s{2,}", " ", raw).strip()
        if not t:
            continue
        if HEADING.match(_unnumber(t)) or HEADING.match(t) or SCRIPT_STARTS.match(t):
            break                                          # the script has started: no title page
        if CREDIT.match(t):
            after_credit = True
            continue
        if NOT_TITLE.search(t) or len(t) > 70:
            continue
        if after_credit:
            after_credit = False                           # the credited person's name
            continue
        return t
    return ""


def title_from_filename(stem: str) -> str:
    """'WEREWOLF Script 28-08-26' -> 'WEREWOLF'; 'Ultimate Feature - FINAL Sept 2026' -> 'Ultimate Feature';
    'Known Associate - MF - 04.26.26 (1)' -> 'Known Associate - MF'; 'Where the Sparrows Fly - Script - 250926' ->
    'Where the Sparrows Fly'. A title that is only a year ('1917') is kept."""
    t = re.sub(r"\(\d{1,3}\)", " ", stem)                                         # browser copy markers "(1)"
    t = re.sub(r"\d{1,4}[-_.]\d{1,2}[-_.]\d{1,4}(?:[-_.]\d{1,3})?", " ", t).replace("_", " ")   # dates, "04-26-23-1"
    t = re.sub(r"(?i)\b(?:script|screenplay|shooting|draft|final|revised|rev\d*|v\d+(?:\.\d+)*|copy)\b", " ", t)
    t = re.sub(r"(?i)\b(?:jan|feb|mar|apr|may|jun|jul|aug|sept?|oct|nov|dec)[a-z]*\.?\s+(?:19|20)\d\d\b", " ", t)   # "Sept 2026"
    t = re.sub(r"\b(?:\d{6}|\d{8})\b", " ", t)                                  # unseparated dates, "250926", "20260925"
    t = re.sub(r"(?:\s*[-–—]\s*){2,}", " - ", t)                                   # "Fly - Script - 250926" left "Fly - - "
    tidy = lambda x: re.sub(r"(?:\s*[-–—_.,(]\s*)+$", "", re.sub(r"\s{2,}", " ", x).strip(" -–—_.,()")).strip()
    keep = tidy(t)
    t = tidy(re.sub(r"\b(?:19|20)\d\d\s*$", " ", keep))                             # a trailing year, unless that's the title
    return t or keep or stem


def clean_title(t: str) -> str:
    """Undo title-page typography that PDF text extraction mangles (Tim's Library, 13 Oct): letter-spaced
    "S N O W S T O R M" (words split by wider gaps) and shadow-printed "ASSASSINATIONASSASSINATION"."""
    t = (t or "").strip()
    if re.fullmatch(r"\S(?: +\S){2,}", t):                   # every token a single character: letter-spacing
        t = " ".join(w.replace(" ", "") for w in re.split(r" {2,}", t))
    t = re.sub(r"\s+", " ", t)
    m = re.fullmatch(r"(.{3,})\1", t)                     # the same text twice, end to end (not "Bora Bora")
    return m.group(1) if m else t


def _summarise(title: str, scenes: list[dict], est_pages: float | None, fmt: str) -> dict:
    chars: dict[str, dict] = {}
    for n, sc in enumerate(scenes, 1):
        sc["number"] = n
        for name, blocks in sc["characters"].items():
            c = chars.setdefault(name, {"name": name, "dialogue_blocks": 0, "scenes": [], "first_scene": n})
            c["dialogue_blocks"] += blocks
            c["scenes"].append(n)
        sc["characters"] = list(sc["characters"].keys())
    cast = sorted(chars.values(), key=lambda c: (-c["dialogue_blocks"], c["first_scene"]))
    for c in cast:
        c["scene_count"] = len(c.pop("scenes"))
    count = lambda key, val: sum(1 for s in scenes if val in s[key])
    return {
        "format": fmt, "title": title,
        "pages": max(1, math.ceil(est_pages)) if est_pages is not None else None, "pages_estimated": est_pages is not None,
        "scene_count": len(scenes),
        "int": count("int_ext", "INT"), "ext": count("int_ext", "EXT"),
        "day": sum(1 for s in scenes if "DAY" in s["time_of_day"] or s["time_of_day"] in ("MORNING", "AFTERNOON", "DAWN")),
        "night": sum(1 for s in scenes if "NIGHT" in s["time_of_day"] or s["time_of_day"] in ("EVENING", "DUSK")),
        "locations": sorted({s["location"] for s in scenes if s["location"]}),
        "speaking_roles": len(cast), "cast": cast,
        "scenes": [{k: s[k] for k in ("number", "heading", "int_ext", "location", "time_of_day", "characters", "lines")} for s in scenes],
        "warnings": [],
    }


# ---------------------------------------------------------------- full text for the model

def _fountain_body(text: str) -> str:
    head = text.split("\n\n", 1)
    body = head[1] if head and re.match(r"^\s*Title\s*:", head[0], re.I | re.M) and len(head) > 1 else text
    body = re.sub(r"/\*.*?\*/", "", body, flags=re.S)
    return re.sub(r"\[\[.*?\]\]", "", body, flags=re.S)


def text(filename: str, data: bytes) -> str:
    """The screenplay as plain text (title page removed), one scene heading per line, for the model to read."""
    name = filename.lower()
    if name.endswith(".fdx"):
        root = ET.fromstring(data)
        tp = root.find(".//TitlePage")
        skip = set(map(id, tp.iter("Paragraph"))) if tp is not None else set()
        out = []
        for p in root.iter("Paragraph"):
            if id(p) in skip:
                continue
            t = "".join(x.text or "" for x in p.iter("Text")).strip()
            if not t:
                continue
            kind = p.get("Type", "")
            out.append(t.upper() if kind in ("Scene Heading", "Character", "Transition") else t)
            out.append("")
        return "\n".join(out).strip()
    if name.endswith(".pdf"):
        from . import ocr
        pages = _pdf_pages(data)
        if ocr.is_scanned(pages) and ocr.available():
            pages = ocr.pdf_pages(data, filename)
        lines = [re.sub(r"[ \t]{2,}", " ", l).strip() for l in "\n".join(pages).splitlines()]
        out, blank = [], False
        for l in lines:
            if re.fullmatch(r"\d+\.?|\(?CONTINUED\)?:?|CONT(?:'|’)?D", l, re.I):   # page numbers, continueds
                continue
            if not l:
                if not blank:
                    out.append("")
                blank = True
                continue
            out.append(_unnumber(l))
            blank = False
        return "\n".join(out).strip()
    return _fountain_body(_text(data)).strip()


def chunks(screenplay: str, max_chars: int = 12000) -> list[str]:
    """Split at scene headings into pieces no longer than max_chars (a single overlong scene is split by paragraph)."""
    scenes, cur = [], []
    for line in screenplay.splitlines():
        s = line.strip()
        if s and HEADING.match(s) and (s.upper() == s or s.startswith(".")) and cur:
            scenes.append("\n".join(cur))
            cur = []
        cur.append(line)
    if cur:
        scenes.append("\n".join(cur))
    pieces, buf = [], ""
    for sc in scenes:
        parts = [sc] if len(sc) <= max_chars else re.split(r"(?<=\n\n)", sc)
        for part in parts:
            if buf and len(buf) + len(part) > max_chars:
                pieces.append(buf.strip())
                buf = ""
            while len(part) > max_chars:                # pathological paragraph
                pieces.append(part[:max_chars])
                part = part[max_chars:]
            buf += ("\n" if buf else "") + part
    if buf.strip():
        pieces.append(buf.strip())
    return pieces


# ---------------------------------------------------------------- scene texts for the model (1.0.7)

PAGE_NO = re.compile(r"^\s*(\d{1,3})\.?\s*$")
JUNK = re.compile(r"\d+\.?|\(?CONTINUED\)?:?|CONT(?:'|’)?D|\(?MORE\)?", re.I)


def _printed_page_numbers(pages: list[str]) -> list[int | None]:
    """The page number printed on each PDF page (top or bottom line "12."), or None (title pages, unnumbered pages)."""
    out = []
    for txt in pages:
        ls = [ln for ln in txt.splitlines() if ln.strip()]
        found = None
        for ln in ls[:3] + ls[-3:]:
            m = PAGE_NO.match(ln) or re.match(r"^\s*\S.*?\s{3,}(\d{1,3})\.\s*$", ln)   # alone, or at the right margin
            if m:
                found = int(m.group(1))
                break
        out.append(found)
    return out


def _clean(lines: list[str]) -> str:
    out, blank = [], False
    for raw in lines:
        ln = re.sub(r"[ \t]{2,}", " ", raw).strip()
        if ln and JUNK.fullmatch(ln):
            continue
        if not ln:
            if out and not blank:
                out.append("")
            blank = True
            continue
        out.append(_unnumber(ln))
        blank = False
    return "\n".join(out).strip()


def scene_texts(filename: str, data: bytes) -> list[dict]:
    """Every scene with its number (as in the breakdown), heading, page and text, for reading by the model.
    Page is the number printed on the PDF page where the scene starts (else the PDF page); for Final Draft and Fountain
    it is estimated at 56 lines a page."""
    name = filename.lower()
    out = []
    if name.endswith(".fdx"):
        root = ET.fromstring(data)
        tp = root.find(".//TitlePage")
        skip = set(map(id, tp.iter("Paragraph"))) if tp is not None else set()
        nlines, cur = 0, None
        for p in root.iter("Paragraph"):
            if id(p) in skip:
                continue
            t = "".join(x.text or "" for x in p.iter("Text")).strip()
            if not t:
                continue
            kind = p.get("Type", "")
            if kind == "Scene Heading":
                cur = {"number": len(out) + 1, "heading": _split_heading(t)["heading"], "page": int(nlines / 56) + 1,
                       "page_estimated": True, "lines": []}
                out.append(cur)
            elif cur is not None:
                cur["lines"] += [t.upper() if kind in ("Character", "Transition") else t, ""]
            nlines += max(1, len(t) // 60)
        for sc in out:
            sc["text"] = _clean(sc.pop("lines"))
        return out
    if name.endswith(".pdf"):
        lines, page_of, pages, _ = _pdf_source(data, filename)
        scenes = _from_lines(lines)
        printed = _printed_page_numbers(pages)
        page = lambda i: printed[page_of[i] - 1] or page_of[i]
        estimated = False
    else:
        text = _text(data)
        head = text.split("\n\n", 1)
        body = head[1] if head and re.match(r"^\s*Title\s*:", head[0], re.I | re.M) and len(head) > 1 else text
        lines = _fountain_lines(body)
        scenes = _from_lines(lines, forced=True)
        page = lambda i: int(i / 56) + 1
        estimated = True
    for n, sc in enumerate(scenes, 1):
        end = scenes[n]["start"] if n < len(scenes) else len(lines)
        out.append({"number": n, "heading": sc["heading"], "page": page(sc["start"]), "page_estimated": estimated,
                    "text": _clean(lines[sc["start"] + 1:end])})
    return out


def scene_batches(scenes: list[dict], max_chars: int) -> list[list[tuple[dict, str]]]:
    """Consecutive scenes grouped so each group's text fits max_chars; a scene longer than that is split in pieces.
    Each item is (scene, labelled text)."""
    groups, cur, size = [], [], 0
    for sc in scenes:
        label = f"[SCENE {sc['number']}, page {sc['page']}] {sc['heading']}"
        body = sc["text"]
        pieces = [body[i:i + max_chars - 200] for i in range(0, max(1, len(body)), max_chars - 200)] or [""]
        for k, piece in enumerate(pieces):
            item = (label + (" (continued)" if k else "")) + "\n" + piece
            if cur and size + len(item) > max_chars:
                groups.append(cur)
                cur, size = [], 0
            cur.append((sc, item))
            size += len(item) + 2
    if cur:
        groups.append(cur)
    return groups
