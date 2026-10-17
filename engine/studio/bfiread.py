"""BFI Certification: reading the script for Section A and drafting the answer pack (1.0.8).

Jon's instructions (sources/t07_bfi_certification SKILL.md) and his July 2026 guidance pack set the rules:
- A1 setting: 4 / 3 / 2 / 1 points where at least 75% / 66% / 50% / 25% of the film is set in the UK or an EEA state,
  measured by script pages at interim stage; where it is shot doesn't matter.
- A2 lead characters: 4 points where at least two of the three leads are UK or EEA citizens or residents (or all
  leads, where there are only one or two); 2 for one qualifying first or second lead; 1 for a qualifying third lead.
- A3 subject matter or underlying material: 4 points; underlying material needs chain-of-title evidence.
- A4 original dialogue: 6 / 4 / 2 / 1 where at least 75% / 66% / 50% / 25% of the spoken words are in English, a UK
  indigenous language or an EEA language; stage directions don't count.
- B British creativity, heritage and diversity: up to 4, and a generic case doesn't qualify.
- Never invent facts or award unsupported points; record proposed and conservative points with exact evidence;
  the production company verifies, approves, signs and submits.

So the model reads each scene for where it is set (country, place, the words that show it, stated or inferred), the
languages spoken, and what the scenes say about the leads' nationality and the story's British or European subject.
The Studio does the arithmetic: page shares from the breakdown, spoken words counted from the script itself, the
points from the thresholds above. Proposed points count inferences; conservative points count only what the script
states. Every answer is PENDING until the company reviews it; one that rests on documents a script can't supply
(chain of title) is DO NOT SUBMIT until they are attached.
"""
from __future__ import annotations

import re
from datetime import date

from . import budget, refdata, sceneai

SKILL = refdata.app_root() / "sources" / "t07_bfi_certification" / "skills" / "instructions" / "SKILL.md"
UK = {"united kingdom", "uk", "england", "scotland", "wales", "northern ireland", "great britain", "britain"}
EEA = {"austria", "belgium", "bulgaria", "croatia", "cyprus", "czech republic", "czechia", "denmark", "estonia", "finland", "france",
       "germany", "greece", "hungary", "ireland", "republic of ireland", "italy", "latvia", "lithuania", "luxembourg", "malta",
       "netherlands", "the netherlands", "poland", "portugal", "romania", "slovakia", "slovenia", "spain", "sweden", "iceland",
       "liechtenstein", "norway"}
UK_LANGUAGES = {"english", "welsh", "scottish gaelic", "gaelic", "irish", "irish gaelic", "cornish", "scots", "ulster scots"}
EEA_LANGUAGES = {"bulgarian", "croatian", "czech", "danish", "dutch", "flemish", "estonian", "finnish", "french", "german", "greek",
                 "hungarian", "italian", "latvian", "lithuanian", "maltese", "polish", "portuguese", "romanian", "slovak", "slovenian",
                 "spanish", "swedish", "icelandic", "norwegian", "luxembourgish", "catalan", "basque", "galician"}
UK_EEA_WORDS = {"british", "english", "scottish", "welsh", "northern irish", "irish", "french", "german", "spanish", "italian",
                "portuguese", "dutch", "belgian", "austrian", "swedish", "danish", "finnish", "norwegian", "icelandic", "polish", "czech",
                "slovak", "slovakian", "hungarian", "romanian", "bulgarian", "greek", "croatian", "slovenian", "estonian", "latvian",
                "lithuanian", "maltese", "cypriot", "luxembourgish", "liechtensteiner", "londoner", "parisian"} | UK | EEA
THRESHOLDS_A1 = [(0.75, 4), (0.66, 3), (0.50, 2), (0.25, 1)]
THRESHOLDS_A4 = [(0.75, 6), (0.66, 4), (0.50, 2), (0.25, 1)]
VERDICTS = ["Yes", "No", "Unclear"]


def zone(country: str) -> str:
    c = re.sub(r"[^a-z ]", "", (country or "").lower()).strip()
    return "UK" if c in UK else "EEA" if c in EEA else "Unclear" if c in ("", "unclear", "unknown", "at sea", "sea") else "Other"


def qualifying_language(lang: str) -> bool:
    l = re.sub(r"[^a-z ]", "", (lang or "").lower()).strip()
    return l in UK_LANGUAGES or l in EEA_LANGUAGES


def names_uk_eea(text: str) -> str | None:
    """The UK or EEA nationality or country a piece of evidence names, if any ("a French detective" -> "french")."""
    t = (text or "").lower()
    return next((w for w in sorted(UK_EEA_WORDS, key=len, reverse=True) if re.search(rf"\b{re.escape(w)}\b", t)), None)


def points(share: float, table: list) -> int:
    return next((p for t, p in table if share >= t - 1e-9), 0)


# ---------------------------------------------------------------- spoken words, counted from the script

PAREN = re.compile(r"^\(.*\)$")


def dialogue_words(text: str) -> int:
    """Words spoken in a scene: the lines after an all-caps character cue, up to the next blank line, without
    parentheticals ((beat), (in French)). Stage directions and transitions are not dialogue."""
    words, speaking = 0, False
    lines = text.split("\n")
    for i, raw in enumerate(lines):
        ln = raw.strip()
        if not ln:
            speaking = False
            continue
        prev_blank = i == 0 or not lines[i - 1].strip()
        if prev_blank and ln == ln.upper() and re.search(r"[A-Z]", ln) and len(ln) <= 45 and not ln.endswith(":") and i + 1 < len(lines) and lines[i + 1].strip():
            speaking = True
            continue
        if speaking and not PAREN.match(ln):
            words += len(re.findall(r"[\w’']+", ln))
    return words


# ---------------------------------------------------------------- schemas

def _obj(props: dict) -> dict:
    return {"type": "object", "properties": props, "required": list(props), "additionalProperties": False}


S = {"type": "string"}


def scene_schema(scenes: list[dict], leads: list[str]) -> dict:
    return _obj({
        "scenes": {"type": "array", "minItems": len(scenes), "maxItems": len(scenes), "items": _obj({
            "scene": {"type": "integer", "enum": [s["number"] for s in scenes]},
            "country": S, "place": S, "evidence": S, "explicit": {"type": "boolean"},
            "languages": {"type": "array", "maxItems": 4, "items": _obj({"language": S, "share": {"type": "integer", "minimum": 0, "maximum": 100}})}})},
        "leads": {"type": "array", "maxItems": max(1, len(leads)), "items": _obj({
            "name": {"type": "string", "enum": leads or ["NONE"]}, "scene": {"type": "integer", "enum": [s["number"] for s in scenes]},
            "evidence": S, "suggests": {"type": "string", "enum": ["UK or EEA", "Other", "No indication"]}})},
        "subject": S})


def final_schema(leads: list[str]) -> dict:
    pts = lambda m: {"type": "integer", "minimum": 0, "maximum": m}
    return _obj({
        "leads": {"type": "array", "minItems": len(leads), "maxItems": len(leads), "items": _obj({
            "name": {"type": "string", "enum": leads}, "qualifies": {"type": "string", "enum": VERDICTS}, "reason": S})},
        "a3": _obj({"proposed": {"type": "integer", "enum": [0, 4]}, "conservative": {"type": "integer", "enum": [0, 4]}, "reason": S}),
        "b": _obj({"proposed": pts(4), "conservative": pts(4), "reason": S}),
        "answers": _obj({k: S for k in ("A3", "B")})})


# ---------------------------------------------------------------- the run

def read(filename: str, data: bytes, breakdown: dict, settings: dict, *, progress=lambda m: None, cancelled=lambda: False,
         mode: str | None = None) -> dict:
    reading = sceneai.Reading(filename, data, breakdown, settings, mode, progress, cancelled, share=0.4)
    leads = [c["name"] for c in (breakdown.get("cast") or [])[:3]]
    rules = SKILL.read_text(encoding="utf-8")
    core = re.search(r"CORE CONTROLS\n(.*?)(?=\n1\. APPLICANT)", rules, re.S)
    system = ("You are a UK Film Certification Executive at Saracen Bridge Analytics preparing BFI Cultural Test evidence. "
              "Use UK English. " + (core.group(1).strip() if core else "Never invent facts or award unsupported points.") + "\n\n"
              "TASK: For every scene shown, record: country, the country where the scene's story is set (as the script states or "
              "clearly implies; 'Unclear' if it can't be told; 'At sea' only if no country applies); place, the town, region or "
              "location; evidence, the few words from the scene that show it (a heading, a sign, a line); explicit, true if the "
              "scene states the place, false if you infer it from earlier scenes or context; languages, the languages spoken in "
              "the scene's dialogue with each one's share of the spoken words in percent (empty if nobody speaks; a line marked "
              "'(in French)' is French). Then, for the lead characters named below, anything in these scenes that shows their "
              "nationality, citizenship or where they live, with the scene number (leave the list empty if nothing does). Then "
              "subject: one or two sentences on anything in these scenes that ties the story to the UK or Europe (places, "
              "history, institutions, culture, real events); empty if nothing.\n"
              f"Lead characters: {', '.join(leads) or 'none'}.\nPlain text in the strings; no markdown.")
    groups = reading.over_scenes(system, f"FILM: {breakdown.get('title') or 'Untitled'}.", lambda sc: scene_schema(sc, leads),
                                 lambda sc: 700 + 110 * len(sc), label="Reading scenes")
    eighths = dict(zip([s["number"] for s in breakdown["scenes"]], budget.scene_eighths(breakdown)))
    scenes, lead_notes, subject = {}, [], []
    for shown, ans in groups:
        allowed = {s["number"] for s in shown}
        for row in ans.get("scenes") or []:
            if row.get("scene") in allowed and row["scene"] not in scenes:
                scenes[row["scene"]] = row
        for l in ans.get("leads") or []:
            if l.get("name") in leads and l.get("scene") in allowed and l.get("suggests") != "No indication" and (l.get("evidence") or "").strip():
                lead_notes.append(l)
        if (ans.get("subject") or "").strip():
            subject.append(f"Scenes {shown[0]['number']}–{shown[-1]['number']}: {ans['subject'].strip()}")
    rows = []
    for s in reading.scenes:
        r = scenes.get(s["number"]) or {}
        z = zone(r.get("country", ""))
        words = dialogue_words(s["text"])
        langs = [x for x in r.get("languages") or [] if (x.get("language") or "").strip() and x.get("share")]
        if words and not langs:
            langs = [{"language": "English", "share": 100}]          # written in English, nothing marked otherwise
        total = sum(x["share"] for x in langs) or 100
        qual = sum(x["share"] for x in langs if qualifying_language(x["language"])) / total if langs else 1.0
        rows.append({"scene": s["number"], "heading": s["heading"], "page": s["page"], "page_estimated": s.get("page_estimated", False),
                     "eighths": eighths.get(s["number"], 1), "country": r.get("country") or "Unclear", "zone": z,
                     "place": r.get("place") or "", "evidence": r.get("evidence") or "", "explicit": bool(r.get("explicit")),
                     "read": bool(r), "words": words, "languages": langs, "qualifying_words": round(words * qual)})
    a1 = _a1(rows)
    a4 = _a4(rows)
    progress("Drafting the answers")
    final = reading.ask(system.split("TASK:")[0] + _final_task(), _final_input(breakdown, leads, a1, a4, lead_notes, subject, rows),
                        final_schema(leads) if leads else final_schema(["NONE"]), 3000)
    a2 = _a2(leads, final.get("leads") or [], lead_notes)
    a3 = final.get("a3") or {"proposed": 0, "conservative": 0, "reason": ""}
    b = final.get("b") or {"proposed": 0, "conservative": 0, "reason": ""}
    b["conservative"] = min(b.get("conservative") or 0, b.get("proposed") or 0)
    a3["conservative"] = min(a3.get("conservative") or 0, a3.get("proposed") or 0)
    criteria = {"A1": a1, "A2": a2, "A3": {"proposed": a3["proposed"], "conservative": a3["conservative"], "reason": a3["reason"]},
                "A4": a4, "B": {"proposed": b["proposed"], "conservative": b["conservative"], "reason": b["reason"]}}
    res = {"title": breakdown.get("title") or "", "date": date.today().isoformat(), "leads": leads, "scenes": rows,
           "criteria": criteria, "subject": subject, "lead_evidence": lead_notes,
           "answer_pack": _pack(criteria, _answers(criteria, final.get("answers") or {}, rows), rows, a2), "made_with": reading.made_with()}
    res["checks"] = _checks(res)
    return res


def _share(rows: list[dict], test) -> float:
    total = sum(r["eighths"] for r in rows) or 1
    return sum(r["eighths"] for r in rows if test(r)) / total


def _a1(rows: list[dict]) -> dict:
    prop = _share(rows, lambda r: r["zone"] in ("UK", "EEA"))
    cons = _share(rows, lambda r: r["zone"] in ("UK", "EEA") and r["explicit"])
    by = {}
    for r in rows:
        by.setdefault(r["zone"], 0)
        by[r["zone"]] += r["eighths"]
    return {"proposed": points(prop, THRESHOLDS_A1), "conservative": points(cons, THRESHOLDS_A1), "share_proposed": round(prop, 4),
            "share_conservative": round(cons, 4), "eighths_by_zone": by,
            "reason": f"{prop:.0%} of the script by length is set in the UK or an EEA state ({cons:.0%} where the script states it)."}


def _a4(rows: list[dict]) -> dict:
    words = sum(r["words"] for r in rows)
    q = sum(r["qualifying_words"] for r in rows)
    share = q / words if words else 0.0
    langs: dict[str, int] = {}
    for r in rows:
        for x in r["languages"]:
            langs[x["language"]] = langs.get(x["language"], 0) + round(r["words"] * x["share"] / (sum(y["share"] for y in r["languages"]) or 100))
    p = points(share, THRESHOLDS_A4)
    return {"proposed": p, "conservative": p, "share": round(share, 4), "words": words, "qualifying_words": q,
            "by_language": dict(sorted(langs.items(), key=lambda kv: -kv[1])),
            "reason": f"{q:,} of {words:,} spoken words ({share:.0%}) are in English, a UK indigenous language or an EEA language "
                      "(counted from the dialogue in the script; parentheticals and stage directions excluded)."}


def _a2(leads: list[str], verdicts: list[dict], notes: list[dict]) -> dict:
    """Proposed: the model's Yes, or evidence naming a UK or EEA nationality or country (tested 15 Oct: Gemma 4 E2B judged
    "a French detective" not to qualify). Conservative: only evidence that names one."""
    v = {x["name"]: dict(x) for x in verdicts if x.get("name") in leads}
    evidence = {n: [x for x in notes if x["name"] == n] for n in leads}
    named = {n: next((w for w in (names_uk_eea(x["evidence"]) for x in evidence[n]) if w), None) for n in leads}
    for n in leads:
        if named[n] and (v.get(n) or {}).get("qualifies") != "Yes":
            v[n] = {"name": n, "qualifies": "Yes", "reason": f"The script describes {n} as {named[n].title()}, which is UK or EEA. "
                    + ((v.get(n) or {}).get("reason") or "")}

    def score(qualifies) -> int:
        q = [qualifies(n) for n in leads]
        if not leads:
            return 0
        if sum(q) >= 2 or (len(leads) <= 2 and all(q)):
            return 4
        if any(q[:2]):
            return 2
        return 1 if len(q) > 2 and q[2] else 0
    prop = score(lambda n: (v.get(n) or {}).get("qualifies") == "Yes")
    cons = score(lambda n: bool(named[n]))
    return {"proposed": prop, "conservative": cons,
            "leads": [{"name": n, "rank": i + 1, "qualifies": (v.get(n) or {}).get("qualifies", "Unclear"), "reason": (v.get(n) or {}).get("reason", ""),
                       "named": named[n], "evidence": [{"scene": x["scene"], "text": x["evidence"], "suggests": x["suggests"]} for x in evidence[n]]}
                      for i, n in enumerate(leads)],
            "reason": "Leads are the three largest speaking parts in the script; confirm them by story prominence, pages and working days."}


def _final_task() -> str:
    return ("TASK: Using the evidence below, which the Studio has counted from the script: (1) for each lead character, "
            "whether the script shows them to be a UK or EEA citizen or resident (Yes, No or Unclear) and why, citing scenes; "
            "(2) A3: 4 points if the story or subject relates to the UK or an EEA state (proposed), and conservative 4 only if "
            "that is plain from the script itself; underlying material by a UK or EEA author needs chain of title, which a "
            "script can't show; (3) B, British creativity, heritage and diversity: proposed and conservative points (0-4) and a "
            "specific case from this film, or 0 where the case would be generic; (4) a proposed answer for A3 and for B in "
            "precise, factual application language, citing scene numbers. Don't state points in the answers (the Studio adds "
            "them). Do not exaggerate, and do not claim facts the evidence doesn't show.")


def _final_input(breakdown: dict, leads: list[str], a1: dict, a4: dict, notes: list[dict], subject: list[str], rows: list[dict]) -> str:
    places = {}
    for r in rows:
        key = f"{r['country']} ({r['zone']})"
        places.setdefault(key, []).append(r["scene"])
    lines = [f"FILM: {breakdown.get('title')}; {breakdown.get('scene_count')} scenes, {breakdown.get('pages')} pages.",
             f"A1 SETTING: {a1['reason']} Scenes by country: " + "; ".join(f"{k}: scenes {', '.join(map(str, v[:15]))}{' …' if len(v) > 15 else ''}" for k, v in places.items()),
             f"A4 LANGUAGE: {a4['reason']} Words by language: " + ", ".join(f"{k} {v:,}" for k, v in a4["by_language"].items()),
             f"LEADS (largest speaking parts, in order): {', '.join(leads) or 'none'}.",
             "EVIDENCE ABOUT THE LEADS:"] + [f"- {x['name']}, scene {x['scene']}: {x['evidence']} (suggests {x['suggests']})" for x in notes[:40]] + \
            ["SUBJECT NOTES:"] + [f"- {x}" for x in subject[:30]]
    return "\n".join(lines)


POINTS_CLAIM = re.compile(r"^\s*(proposed|conservative)?[:\s]*\d+\s*points?\.?\s*", re.I)


def _answers(c: dict, answers: dict, rows: list[dict]) -> dict:
    """A1, A2 and A4 are written from the Studio's own counts; A3 and B are the model's, without any points it claims."""
    by_country: dict[str, list[int]] = {}
    for r in rows:
        by_country.setdefault(r["country"] if r["zone"] != "Unclear" else "not stated", []).append(r["scene"])
    a1, a4 = c["A1"], c["A4"]
    sc = lambda ns: ", ".join(map(str, ns[:15])) + (" …" if len(ns) > 15 else "")
    out = {
        "A1": (f"{a1['share_proposed']:.0%} of the film, measured by script length, is set in the UK or an EEA state. By country: "
               + "; ".join(f"{k}: scenes {sc(v)}" for k, v in by_country.items()) + ". Setting is where the story takes place, not where it is filmed."),
        "A2": "The three lead characters, by speaking part, are " + ", ".join(l["name"] for l in c["A2"]["leads"]) + ". "
              + " ".join(f"{l['name']}: {l['qualifies']}. {l['reason']}".strip() for l in c["A2"]["leads"]),
        "A4": (f"{a4['share']:.0%} of the original dialogue ({a4['qualifying_words']:,} of {a4['words']:,} spoken words, counted from the "
               "shooting script) is in English, a UK indigenous language or an EEA language. By language: "
               + ", ".join(f"{k} {v:,}" for k, v in a4["by_language"].items()) + "."),
    }
    for k in ("A3", "B"):
        out[k] = POINTS_CLAIM.sub("", (answers.get(k) or "").strip())
    return out


def _pack(c: dict, answers: dict, rows: list[dict], a2: dict) -> list[dict]:
    crit = {r["ref"]: r for r in refdata.rows("SELECT ref, criterion, max_points FROM bfi_cultural_test")}
    uk = [r["scene"] for r in rows if r["zone"] in ("UK", "EEA")]
    other = [r["scene"] for r in rows if r["zone"] == "Other"]
    refs = {"A1": f"Shooting script: scenes set in the UK/EEA {', '.join(map(str, uk[:20]))}{' …' if len(uk) > 20 else ''}"
                  + (f"; elsewhere {', '.join(map(str, other[:12]))}" if other else "") + ". Script-page setting analysis (Studio).",
            "A2": "; ".join(f"{l['name']}: " + (", ".join(f"scene {e['scene']}" for e in l["evidence"][:4]) or "no scene states it") for l in a2["leads"]),
            "A3": "Shooting script; chain of title if relying on underlying material.",
            "A4": "Shooting script: dialogue word count by language (Studio).",
            "B": "Shooting script; supporting statement."}
    assumptions = {"A1": "Lengths are each scene's share of the script; final certification uses screen minutes.",
                   "A2": "Leads taken as the three largest speaking parts; nationality as the script shows it.",
                   "A3": "Underlying material and its author's nationality are not in the script.",
                   "A4": "Words counted from the script version read; narration counts, stage directions don't.",
                   "B": "A case specific to the film; generic statements do not qualify."}
    out = []
    for ref in ("A1", "A2", "A3", "A4", "B"):
        cc = c[ref]
        # never READY from a script read alone; a claim the script itself can't support waits for its documents
        status = "DO NOT SUBMIT" if cc["proposed"] and not cc["conservative"] else "PENDING"
        out.append({"ref": ref, "question": f"[Paste the exact BFI portal question for {ref}: {crit.get(ref, {}).get('criterion', '')}]",
                    "answer": (answers.get(ref) or "").strip(), "points_proposed": cc["proposed"], "points_conservative": cc["conservative"],
                    "max": crit.get(ref, {}).get("max_points"), "document": "Shooting script (version read by the Studio)",
                    "reference": refs[ref], "assumptions": assumptions[ref], "approval": "Film production company (certification lead)",
                    "status": status})
    return out


def _checks(res: dict) -> list[str]:
    out = []
    unread = [r["scene"] for r in res["scenes"] if not r["read"]]
    if unread:
        out.append(f"{len(unread)} scene(s) came back without a reading ({', '.join(map(str, unread[:12]))}): they count as Unclear.")
    unclear = [r["scene"] for r in res["scenes"] if r["zone"] == "Unclear"]
    if unclear:
        out.append(f"Setting unclear in {len(unclear)} scene(s): check them before relying on A1.")
    if not res["leads"]:
        out.append("No speaking parts found, so A2 can't be assessed from the script.")
    out.append("Script-only reading: interim stage at best. The company must verify every answer, attach the evidence and approve before anything is submitted.")
    return out


# ---------------------------------------------------------------- workbook (Jon's answer pack columns)

def workbook(res: dict) -> bytes:
    import io
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    wb = Workbook()
    hf, fill, body = Font(name="Arial", bold=True, color="FFFFFF"), PatternFill("solid", fgColor="1F1F1F"), Font(name="Arial", size=10)

    def sheet(ws, headers, rows, widths):
        ws.append(headers)
        for c in ws[1]:
            c.font, c.fill, c.alignment = hf, fill, Alignment(wrap_text=True, vertical="top")
        for r in rows:
            ws.append(r)
        for row in ws.iter_rows(min_row=2):
            for c in row:
                c.font, c.alignment = body, Alignment(wrap_text=True, vertical="top")
        for i, w in enumerate(widths, 1):
            ws.column_dimensions[ws.cell(1, i).column_letter].width = w
        ws.freeze_panes = "A2"

    ws = wb.active
    ws.title = "Answer Pack"
    sheet(ws, ["Ref", "BFI Question", "Proposed Answer", "Points Claimed (proposed)", "Points (conservative)", "Max", "Supporting Document",
               "Exact Reference", "Assumptions", "Approval Required", "Status"],
          [[p["ref"], p["question"], p["answer"], p["points_proposed"], p["points_conservative"], p["max"], p["document"], p["reference"],
            p["assumptions"], p["approval"], p["status"]] for p in res["answer_pack"]],
          [6, 34, 70, 12, 12, 6, 26, 44, 40, 26, 14])
    sheet(wb.create_sheet("A1 Setting analysis"), ["Scene", "Page", "Heading", "Length (eighths)", "Country", "UK / EEA / other",
                                                   "Stated in the script", "Place", "Evidence"],
          [[r["scene"], f"~{r['page']}" if r.get("page_estimated") else r["page"], r["heading"], r["eighths"], r["country"], r["zone"],
            "Yes" if r["explicit"] else "Inferred", r["place"], r["evidence"]] for r in res["scenes"]],
          [7, 6, 34, 10, 16, 12, 12, 26, 50])
    sheet(wb.create_sheet("A4 Dialogue count"), ["Scene", "Spoken words", "Languages (share of the scene's words)", "Qualifying words"],
          [[r["scene"], r["words"], "; ".join(f"{x['language']} {x['share']}%" for x in r["languages"]), r["qualifying_words"]] for r in res["scenes"]],
          [7, 12, 50, 14])
    a2 = res["criteria"]["A2"]
    sheet(wb.create_sheet("A2 Leads"), ["Rank", "Character", "UK or EEA citizen or resident", "Reason", "Evidence (scene: text)"],
          [[l["rank"], l["name"], l["qualifies"], l["reason"], "\n".join(f"{e['scene']}: {e['text']}" for e in l["evidence"])] for l in a2["leads"]],
          [6, 22, 16, 50, 60])
    n = wb.create_sheet("Notes")
    mw = res["made_with"]
    for line in [f"BFI Cultural Test, Section A and B evidence: {res['title']}",
                 f"Read {mw['scenes']} scenes on {res['date']} ({mw['model']}, {mw['mode']} reasoning).",
                 "Scores: A1 by script length (interim basis); A4 by spoken words counted from the script; A2, A3 and B as judged from the script.",
                 "Proposed counts inferences; conservative counts only what the script states. No answer is READY: the company verifies, approves and submits."] + \
                [f"Check: {c}" for c in res["checks"]] + [f"Subject notes: {x}" for x in res["subject"]]:
        n.append([line])
    n["A1"].font = Font(name="Arial", bold=True, size=12)
    for row in n.iter_rows(min_row=2):
        row[0].font = body
    n.column_dimensions["A"].width = 140
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()
