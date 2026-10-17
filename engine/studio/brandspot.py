"""Brand Integration: scene-by-scene opportunity spotting and outreach drafts (1.0.7).

Jon's instructions for this tool (sources/t05_brand_integration SKILL.md) are the specification. From them:
- every opportunity has an ID, the scene and page, the moment, the exact item, a brand category, a placement type
  (background, functional, hero, dialogue, plot-integrated, campaign-integrated), the narrative reason, the creative
  change needed, risks, feasibility, commercial value and outreach-priority scores, a primary target, two
  alternatives and a no-brand fallback; opportunities that need a script change are flagged apart from those already
  in the script;
- targets are ranked and grouped (Anchor Partner, High-Probability Target, Strategic Stretch, In-Kind Supplier,
  Alternative), each with the opportunity IDs it matches, an outreach angle and the next action;
- outreach is draft-only and tied to exact opportunities: subject, first email, one follow-up, a LinkedIn message
  and a call brief, with placeholders where details are withheld;
- never invent partnerships, budgets, contact names or contact details.

So the model reads the script and proposes; the Studio keeps it honest. Brands can only be picked from Jon's brand
database (the answer is constrained to its IDs); a brand the script already names is found by text search, not by
the model; scores are the model's 1-5 judgement and the outreach priority is computed from them; there are no
contact names (Jon's contact sheet is not loaded, register G-17), only each brand's public route from his database;
and cash values stay "to price", because the Studio holds no placement deal data.
"""
from __future__ import annotations

import io
import json
import re
from datetime import date

from . import refdata, sceneai

SKILL = refdata.app_root() / "sources" / "t05_brand_integration" / "skills" / "instructions" / "SKILL.md"
PLACEMENTS = ["background", "functional", "hero", "dialogue", "plot-integrated", "campaign-integrated"]
PLACEMENT_WEIGHT = {p: i for i, p in enumerate(PLACEMENTS)}
GROUPS = ["Anchor Partner", "High-Probability Target", "Strategic Stretch", "In-Kind Supplier", "Alternative"]
RATINGS = ["U", "PG", "12A", "15", "18", "Not decided"]
NO_BRAND = "No brand: keep it unbranded, or use a cleared fictional brand"
OUTREACH_BRANDS = 5
FORBIDDEN = re.compile(r"\b(chat\s?gpt|openai|language model|artificial intelligence)\b", re.I)
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")


# ---------------------------------------------------------------- Jon's brand database

def catalogue() -> list[dict]:
    return refdata.rows("""SELECT b.brand_id, b.brand_name, b.parent_company, b.category, b.subcategory, b.priority,
        b.previous_film_tv_integration, b.strategic_rationale, b.website, b.public_contact_page, b.generic_email,
        b.last_verified, e.evidence_statement, e.evidence_year FROM brand_accounts b
        LEFT JOIN brand_film_evidence e ON e.brand_id = b.brand_id ORDER BY b.brand_id""")


def categories() -> list[str]:
    return [r["category"] for r in refdata.rows("SELECT category, COUNT(*) n FROM brand_accounts GROUP BY category ORDER BY n DESC, category")]


def _rules() -> str:
    """The parts of Jon's SKILL.md that govern reading a script: opportunity mapping and commercial judgement."""
    raw = SKILL.read_text(encoding="utf-8")
    keep = []
    for head in ("SCRIPT-SPECIFIC OPPORTUNITY MAPPING", "COMMERCIAL JUDGEMENT"):
        m = re.search(rf"{head}\n(.*?)(?=\n[A-Z][A-Z \-&]{{6,}}\n|\Z)", raw, re.S)
        if m:
            keep.append(f"{head}\n{m.group(1).strip()}")
    return "\n\n".join(keep)


def _brand_list(brands: list[dict]) -> str:
    return "\n".join(f"{b['brand_id']} {b['brand_name']} ({b['category']}: {b['subcategory']})" for b in brands)


# ---------------------------------------------------------------- schemas

def _obj(props: dict, required: list | None = None) -> dict:
    return {"type": "object", "properties": props, "required": required or list(props), "additionalProperties": False}


S = {"type": "string"}
SCORE = {"type": "integer", "minimum": 1, "maximum": 5}


def spot_schema(scenes: list[dict], brand_ids: list[str], cats: list[str]) -> dict:
    return _obj({"opportunities": {"type": "array", "maxItems": max_opportunities(scenes), "items": _obj({
        "scene": {"type": "integer", "enum": [s["number"] for s in scenes]},
        "moment": S, "item": S,
        "category": {"type": "string", "enum": cats},
        "placement": {"type": "string", "enum": PLACEMENTS},
        "in_script": {"type": "boolean"},
        "narrative_reason": S, "creative_change": S, "risks": S,
        "brands": {"type": "array", "maxItems": 3, "items": {"type": "string", "enum": brand_ids}},
        "feasibility": SCORE, "value": SCORE})}})


def max_opportunities(scenes: list[dict]) -> int:
    return max(4, min(20, round(1.5 * len(scenes))))


TOKENS_PER_OPPORTUNITY = 190                 # measured 15 Oct: Gemma 4 E2B wrote 2,875 tokens for 18 opportunities (~160 each)


def strategy_schema(ids: list[str]) -> dict:
    return _obj({"targets": {"type": "array", "minItems": len(ids), "maxItems": len(ids), "items": _obj({
        "brand_id": {"type": "string", "enum": ids}, "group": {"type": "string", "enum": GROUPS},
        "outreach_angle": S, "next_action": S})}})


OUTREACH = _obj({"subject": S, "email": S, "follow_up": S, "linkedin": S,
                 "call_brief": {"type": "array", "minItems": 3, "maxItems": 5, "items": S}})


# ---------------------------------------------------------------- the run

def _named(scenes: list[dict], brands: list[dict]) -> list[dict]:
    """Brands from Jon's database that the script itself names, scene by scene (found by text, not by the model)."""
    out = []
    for b in brands:
        names = {b["brand_name"]} | ({b["parent_company"]} if b.get("parent_company") and len(b["parent_company"]) > 3 else set())
        rx = re.compile(r"\b(" + "|".join(re.escape(n) for n in sorted(names, key=len, reverse=True)) + r")\b")
        hits = [s["number"] for s in scenes if rx.search(s["text"]) or rx.search(s["heading"])]
        if hits:
            out.append({"brand_id": b["brand_id"], "brand_name": b["brand_name"], "category": b["category"], "scenes": hits})
    return out


def _fill(chosen: list[str], category: str, by_id: dict, preferred: list[str], avoid: set) -> list[str]:
    """Primary target and two alternatives: the model's picks from Jon's database first, then that category's brands
    in Jon's order of preference (this film's targets, his High priority, previous film/TV work)."""
    # a pick from another category is dropped: tested 15 Oct with Gemma 4 E2B, which put Audi on a teapot
    out = [b for b in dict.fromkeys(chosen) if b in by_id and by_id[b]["category"] == category and category not in avoid]
    # "Other" in Jon's database is a mix (DHL, Boeing, Airbus): never filled automatically (E2B put a handgun with DHL)
    pool = sorted((b for b in by_id.values() if b["category"] == category and b["brand_id"] not in out and category not in avoid
                   and category != "Other"),
                  key=lambda b: (b["brand_id"] not in preferred, b["priority"] != "High",
                                 (b["previous_film_tv_integration"] or "") != "Yes", b["brand_name"]))
    out += [b["brand_id"] for b in pool]
    return out[:3]


def priority(feasibility: int, value: int, brand: dict | None) -> float:
    """Outreach priority, 1-5: feasibility and commercial value weigh 40% each, Jon's brand priority 20%."""
    return round(0.4 * feasibility + 0.4 * value + 0.2 * (5 if brand and brand.get("priority") == "High" else 3), 1)


def spot(filename: str, data: bytes, breakdown: dict, settings: dict, *, options: dict | None = None,
         film: dict | None = None, targets: list[str] | None = None, progress=lambda m: None,
         cancelled=lambda: False, mode: str | None = None) -> dict:
    opts = options or {}
    avoid = {c for c in opts.get("avoid") or [] if c}
    rating = opts.get("rating") or "Not decided"
    reading = sceneai.Reading(filename, data, breakdown, settings, mode, progress, cancelled, share=0.3)
    brands = catalogue()
    by_id = {b["brand_id"]: b for b in brands}
    usable = [b for b in brands if b["category"] not in avoid]
    cats = [c for c in categories() if c not in avoid] or ["Other"]
    preferred = [t for t in targets or [] if t in by_id]
    system = (f"You are a senior brand partnership strategist working to Saracen Bridge Analytics standards.\n\n{_rules()}\n\n"
              "TASK: Read these scenes of a screenplay and list the brand integration opportunities they genuinely support. "
              "One opportunity per distinct moment and item; none for a scene that offers nothing natural. For each: the scene "
              "number shown in its [SCENE n, page p] label; the moment in one short sentence; the exact item (prop, vehicle, "
              "wardrobe, device, venue, food, drink, service or behaviour); the category; the placement type; in_script true if "
              "the item or behaviour is already in the scene as written, false if the scene would have to change; the narrative "
              "reason it fits; the creative change needed ('None' if none); brand safety, rating, regional, exclusivity or "
              "editorial risks ('None evident' if none); up to three brands from the BRAND DATABASE below, best first, by their "
              "IDs (an empty list if none fits); feasibility (1-5: how easily it can be done without harming the story) and "
              "commercial value (1-5: how valuable it is to a brand). Avoid forced placements that damage the story. Keep "
              "every string short: under 20 words.\n\n"
              + (f"Brand categories to avoid for this film: {', '.join(sorted(avoid))}.\n" if avoid else "")
              + f"Intended rating: {rating}.\n"
              + ("Brands already targeted for this film (prefer them where they fit): "
                 + ", ".join(by_id[t]["brand_name"] for t in preferred) + ".\n" if preferred else "")
              + "\nBRAND DATABASE (ID, name, category: subcategory):\n" + _brand_list(usable)
              + "\n\nWrite plain sentences in the strings: no markdown, no bullet symbols.")
    intro = f"FILM: {breakdown.get('title') or 'Untitled'}."
    groups = reading.over_scenes(system, intro, lambda sc: spot_schema(sc, [b["brand_id"] for b in usable], cats),
                                 lambda sc: 400 + TOKENS_PER_OPPORTUNITY * max_opportunities(sc), label="Spotting in scenes")
    named = _named(reading.scenes, brands)
    scene_of = {s["number"]: s for s in reading.scenes}
    opps = []
    for shown, ans in groups:
        allowed = {s["number"] for s in shown}
        for o in ans.get("opportunities") or []:
            if o.get("scene") not in allowed or o.get("category") in avoid:
                continue
            o = dict(o)
            picks = _fill(o.get("brands") or [], o["category"], by_id, preferred, avoid)
            for nb in named:                                   # a brand the scene names is the obvious primary
                if o["scene"] in nb["scenes"] and nb["category"] == o["category"] and nb["category"] not in avoid:
                    picks = [nb["brand_id"]] + [p for p in picks if p != nb["brand_id"]][:2]
            sc = scene_of[o["scene"]]
            o.update(scene_heading=sc["heading"], page=sc["page"], page_estimated=sc.get("page_estimated", False),
                     targets=picks, fallback=NO_BRAND,
                     feasibility=max(1, min(5, int(o.get("feasibility") or 1))), value=max(1, min(5, int(o.get("value") or 1))))
            o["priority"] = priority(o["feasibility"], o["value"], by_id.get(picks[0]) if picks else None)
            o["source"] = "read by the model"
            o.pop("brands", None)
            opps.append(o)
    for nb in named:                                   # a brand the script names is always on the register, for clearance
        if nb["category"] in avoid:
            continue
        for n in nb["scenes"]:
            if any(o["scene"] == n and o["targets"][:1] == [nb["brand_id"]] for o in opps):
                continue
            sc = scene_of[n]
            sentence = next((x.strip() for x in re.split(r"(?<=[.!?])\s+|\n", sc["text"]) if nb["brand_name"] in x), nb["brand_name"])
            picks = _fill([nb["brand_id"]], nb["category"], by_id, preferred, avoid)
            opps.append({"scene": n, "moment": " ".join(sentence.split()[:25]), "item": f"{nb['brand_name']} (named in the script)",
                         "category": nb["category"], "placement": "functional", "in_script": True,
                         "narrative_reason": "The script names the brand in this scene.", "creative_change": "None",
                         "risks": "Clearance: the script names the brand. Agree it with the brand or replace it.",
                         "feasibility": 5, "value": 3, "scene_heading": sc["heading"], "page": sc["page"],
                         "page_estimated": sc.get("page_estimated", False), "targets": picks, "fallback": NO_BRAND,
                         "priority": priority(5, 3, by_id.get(nb["brand_id"])), "source": "named in the script"})
    opps.sort(key=lambda o: (o["scene"], -o["priority"]))
    for i, o in enumerate(opps, 1):
        o["id"] = f"BI-{i:03d}"
    targets_out = _targets(opps, by_id, preferred)
    film = film or {}
    if targets_out:
        progress("Ranking target brands")
        top = targets_out[:12]
        ans = reading.ask(system.split("TASK:")[0] + _strategy_task(), _strategy_input(top, opps, by_id, film, breakdown),
                          strategy_schema([t["brand_id"] for t in top]), 2500)
        for t in ans.get("targets") or []:
            row = next((x for x in top if x["brand_id"] == t["brand_id"]), None)
            if row:
                row.update(group=t["group"], outreach_angle=t["outreach_angle"], next_action=t["next_action"])
    outreach = []
    for t in targets_out[:OUTREACH_BRANDS]:
        progress(f"Drafting outreach to {t['brand_name']}")
        draft = reading.ask(_outreach_system(), _outreach_input(t, opps, by_id, film, breakdown, opts), OUTREACH, 1800, temperature=0.4)
        outreach.append({"brand_id": t["brand_id"], "brand_name": t["brand_name"], "opportunity_ids": t["opportunity_ids"],
                         "route": t["route"], "status": "Draft: not sent", **draft})
    res = {"title": breakdown.get("title") or "", "date": date.today().isoformat(),
           "options": {"avoid": sorted(avoid), "rating": rating, "withhold_title": bool(opts.get("withhold_title"))},
           "opportunities": opps, "targets": targets_out, "outreach": outreach, "named_in_script": named,
           "scenes_read": len(reading.scenes), "scenes_with_opportunities": len({o["scene"] for o in opps}),
           "made_with": reading.made_with()}
    res["checks"] = checks(res)
    return res


def _targets(opps: list[dict], by_id: dict, preferred: list[str]) -> list[dict]:
    agg: dict[str, dict] = {}
    for o in opps:
        for rank, bid in enumerate(o["targets"]):
            b = by_id[bid]
            a = agg.setdefault(bid, {"brand_id": bid, "brand_name": b["brand_name"], "parent_company": b["parent_company"],
                                     "category": b["category"], "priority": b["priority"],
                                     "previous_film_tv": b["previous_film_tv_integration"], "opportunity_ids": [],
                                     "alternative_on": [], "score": 0.0, "best_placement": "background",
                                     "evidence": b.get("evidence_statement") or "", "route": route(b),
                                     "targeted": bid in preferred})
            if rank == 0:
                a["opportunity_ids"].append(o["id"])
                a["score"] += o["priority"]
                if PLACEMENT_WEIGHT[o["placement"]] > PLACEMENT_WEIGHT[a["best_placement"]]:
                    a["best_placement"] = o["placement"]
            else:
                a["alternative_on"].append(o["id"])
                a["score"] += 0.3 * o["priority"]
    out = sorted(agg.values(), key=lambda a: (-a["score"], a["brand_name"]))
    for i, a in enumerate(out, 1):
        a.update(rank=i, score=round(a["score"], 1), group=a.get("group") or "Alternative", outreach_angle="", next_action="")
    return out


def route(b: dict) -> str:
    """The public way in, from Jon's database: never a named person (his contact sheet is not loaded, register G-17)."""
    parts = [p for p in (b.get("generic_email"), b.get("public_contact_page")) if p and p != "None"]
    return ("Public route: " + " · ".join(parts) + f" (Jon's database, checked {str(b.get('last_verified') or '')[:10]}). "
            "No named contact yet.") if parts else "No public route in Jon's database: research the partnerships team."


def _strategy_task() -> str:
    return ("TASK: Rank these brands as targets for this film. For each, choose its group: Anchor Partner (one or two brands "
            "that could carry a hero or plot-integrated partnership), High-Probability Target (clear fit, history of film "
            "work), Strategic Stretch (high value, harder to land), In-Kind Supplier (product or services rather than cash) "
            "or Alternative. Give a one or two sentence outreach angle tied to the exact opportunity IDs, and the next "
            "practical action. Do not invent partnerships, budgets, contact names or contact details.")


def _film_facts(film: dict, breakdown: dict, opts: dict | None = None) -> str:
    title = "[Project title]" if (opts or {}).get("withhold_title") else (breakdown.get("title") or "[Project title]")
    bits = [f"Title: {title}", f"Logline: {film.get('logline') or '[Logline]'}"]
    if film.get("genre"):
        bits.append(f"Genre and tone: {film['genre']}")
    bits.append(f"Scenes: {breakdown.get('scene_count')}; pages: {breakdown.get('pages')}")
    return "\n".join(bits)


def _strategy_input(top: list[dict], opps: list[dict], by_id: dict, film: dict, breakdown: dict) -> str:
    by = {o["id"]: o for o in opps}
    lines = [_film_facts(film, breakdown), "", "CANDIDATE BRANDS (from the opportunity register):"]
    for t in top:
        b = by_id[t["brand_id"]]
        ops = "; ".join(f"{i} scene {by[i]['scene']}: {by[i]['item']} ({by[i]['placement']})" for i in t["opportunity_ids"][:6])
        lines.append(f"{t['brand_id']} {t['brand_name']} ({t['category']}), Jon's priority {b['priority']}, previous film/TV work: "
                     f"{b['previous_film_tv_integration']}. Primary on: {ops or 'none'}. Alternative on: {', '.join(t['alternative_on'][:6]) or 'none'}. "
                     f"Evidence: {b.get('evidence_statement') or 'none recorded'}")
    return "\n".join(lines)


def _outreach_system() -> str:
    raw = SKILL.read_text(encoding="utf-8")
    m = re.search(r"OUTREACH\n(.*?)(?=\n[A-Z][A-Z \-&]{6,}\n|\Z)", raw, re.S)
    return ("You are a senior brand partnership strategist working to Saracen Bridge Analytics standards.\n\n"
            + (f"OUTREACH\n{m.group(1).strip()}\n\n" if m else "")
            + "TASK: Draft outreach to one brand about this film's exact opportunities: a subject line; a concise first email "
              "(under 150 words); one follow-up (under 80 words); a LinkedIn message (under 300 characters); and a call brief of "
              "three to five short points. Refer to the opportunities by what happens on screen. Use placeholders in square "
              "brackets for anything not given: [Contact name], [Your name], [Company], [Release window], [Budget]. Never invent "
              "names, figures, dates, cast, distributors or email addresses. Plain text, no markdown.")


def _outreach_input(t: dict, opps: list[dict], by_id: dict, film: dict, breakdown: dict, opts: dict) -> str:
    b = by_id[t["brand_id"]]
    by = {o["id"]: o for o in opps}
    lines = [_film_facts(film, breakdown, opts), "",
             f"BRAND: {b['brand_name']} ({b['parent_company']}), {b['category']}: {b['subcategory']}.",
             f"Why this brand (Jon's notes): {b.get('strategic_rationale') or 'none'}",
             f"Angle: {t.get('outreach_angle') or 'fit with the scenes below'}", "", "OPPORTUNITIES:"]
    for i in t["opportunity_ids"][:5] or t["alternative_on"][:3]:
        o = by[i]
        lines.append(f"{i}: scene {o['scene']}, page {o['page']}. {o['moment']} Item: {o['item']}. Placement: {o['placement']}. "
                     f"Why it fits: {o['narrative_reason']}")
    return "\n".join(lines)


def checks(res: dict) -> list[str]:
    out = []
    flat = json.dumps({k: res[k] for k in ("opportunities", "targets", "outreach")}, ensure_ascii=False)
    if FORBIDDEN.search(flat):
        out.append("The text mentions ChatGPT, OpenAI or AI: Jon's rules forbid any reference to how it was made. Edit before sending.")
    for d in res["outreach"]:
        found = [e for e in EMAIL.findall(" ".join(str(d.get(k, "")) for k in ("email", "follow_up", "linkedin")))]
        if found:
            out.append(f"The draft to {d['brand_name']} contains an email address ({', '.join(found)}): check it is real before use.")
    if not res["opportunities"]:
        out.append("No opportunities found. Check the script reads as scenes, or relax the categories to avoid.")
    if res["named_in_script"]:
        out.append("The script already names " + ", ".join(f"{n['brand_name']} (scene {', '.join(map(str, n['scenes'][:4]))})"
                                                         for n in res["named_in_script"]) +
                   ": clear each with the brand or replace it, whatever the deal.")
    return out


# ---------------------------------------------------------------- workbook

def workbook(res: dict) -> bytes:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    wb = Workbook()
    head_font, head_fill = Font(name="Arial", bold=True, color="FFFFFF"), PatternFill("solid", fgColor="1F1F1F")
    body = Font(name="Arial", size=10)
    name = lambda bid: next((t["brand_name"] for t in res["targets"] if t["brand_id"] == bid), bid)

    def sheet(ws, headers, rows, widths):
        ws.append(headers)
        for c in ws[1]:
            c.font, c.fill, c.alignment = head_font, head_fill, Alignment(wrap_text=True, vertical="top")
        for r in rows:
            ws.append(r)
        for row in ws.iter_rows(min_row=2):
            for c in row:
                c.font, c.alignment = body, Alignment(wrap_text=True, vertical="top")
        for i, w in enumerate(widths, 1):
            ws.column_dimensions[ws.cell(1, i).column_letter].width = w
        ws.freeze_panes = "B2"

    ws = wb.active
    ws.title = "Opportunity Register"
    sheet(ws, ["ID", "Scene", "Page", "Heading", "Moment", "Item", "Category", "Placement", "Already in script", "Creative change",
               "Narrative reason", "Primary target", "Alternative 1", "Alternative 2", "No-brand fallback", "Feasibility (1-5)",
               "Commercial value (1-5)", "Outreach priority (1-5)", "Risks", "Estimated value (GBP)"],
          [[o["id"], o["scene"], f"~{o['page']}" if o.get("page_estimated") else o["page"], o["scene_heading"], o["moment"], o["item"],
            o["category"], o["placement"], "Yes" if o["in_script"] else "No: needs a script change", o["creative_change"],
            o["narrative_reason"]] + [name(t) for t in o["targets"]] + [""] * (3 - len(o["targets"])) +
           [o["fallback"], o["feasibility"], o["value"], o["priority"], o["risks"], "To price: no placement deal data in the Studio"]
           for o in res["opportunities"]],
          [9, 7, 6, 30, 40, 24, 20, 16, 16, 30, 36, 18, 18, 18, 28, 11, 11, 11, 32, 22])
    sheet(wb.create_sheet("Target Brands"),
          ["Rank", "Brand", "Parent company", "Category", "Group", "Primary on", "Alternative on", "Score", "Outreach angle",
           "Next action", "Contact route", "Film/TV evidence (Jon's database)"],
          [[t["rank"], t["brand_name"], t["parent_company"], t["category"], t["group"], ", ".join(t["opportunity_ids"]),
            ", ".join(t["alternative_on"]), t["score"], t["outreach_angle"], t["next_action"], t["route"], t["evidence"]]
           for t in res["targets"]],
          [6, 20, 24, 20, 20, 22, 22, 8, 44, 36, 44, 44])
    sheet(wb.create_sheet("Outreach Drafts"),
          ["Brand", "Opportunities", "Status", "Route", "Subject", "First email", "Follow-up", "LinkedIn message", "Call brief"],
          [[d["brand_name"], ", ".join(d["opportunity_ids"]), d["status"], d["route"], d["subject"], d["email"], d["follow_up"],
            d["linkedin"], "\n".join(f"- {x}" for x in d["call_brief"])] for d in res["outreach"]],
          [18, 18, 14, 36, 34, 70, 50, 44, 50])
    notes = wb.create_sheet("Notes")
    notes.append(["Brand opportunities: " + res["title"]])
    notes["A1"].font = Font(name="Arial", bold=True, size=12)
    mw = res["made_with"]
    for line in [f"Read {res['scenes_read']} scenes on {res['date']} ({mw['model']}, {mw['mode']} reasoning).",
                 "Brands come only from Jon's brand database; cash values are to be priced; outreach is draft-only and has not been sent.",
                 "No named contacts: Jon's contact sheet is not loaded. Use each brand's public route until a contact is verified.",
                 f"Categories avoided: {', '.join(res['options']['avoid']) or 'none'}. Intended rating: {res['options']['rating']}."] + \
                [f"Check: {c}" for c in res["checks"]]:
        notes.append([line])
    for row in notes.iter_rows(min_row=2):
        row[0].font = body
    notes.column_dimensions["A"].width = 130
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()
