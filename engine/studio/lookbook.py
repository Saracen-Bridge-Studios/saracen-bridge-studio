"""Look Book Analytics: Jon's #1 Look Book Sales Tool Analysis, run on a local model that can see.

Jon's SKILL.md is the specification (house rules plus a brief for each of his 16 sections). The model works in two
passes, like coverage:

  1. look   at each page of the deck as an image (with the page's own text), and note what it shows, what it
            says, how well it sells, and what is wrong with it
  2. write  Jon's 16 sections from those page notes plus what the user told us (logline, attachments, budget, their
            own view of the deck), in six calls

Scores are the model's judgement; the average of the 13 category scores is computed here. How the scores map to
Jon's four verdicts is not defined in his spec, so the verdict stays the model's proposal and is checked for
consistency (register G-01). Gemma reads images with its vision add-on (llm.projector_for); cloud engines can too.
"""
from __future__ import annotations

import io
import json
import re
import time
from datetime import date

from . import llm, refdata
from .coverage import FORBIDDEN, URL, _known_actor, _norm

SKILL = refdata.app_root() / "sources" / "t01_look_book" / "skills" / "instructions" / "SKILL.md"
MAX_PAGES = 60
LONG_SIDE = 1024                 # pixels: enough to judge layout and type, small enough to keep each page quick
CATEGORIES = ["Story clarity", "Visual tone", "Character sell", "Design quality", "Genre positioning", "Audience clarity",
              "Castability", "Director appeal", "Comparable strength", "Budget / scale clarity", "Sales-agent usefulness",
              "Distributor usefulness", "Overall market presentation"]
VERDICTS = {"Strong": "Strong: ready to circulate",
            "Good with Revisions": "Good with revisions: commercially usable but needs refinement",
            "Needs Work": "Needs Work: not ready for sales-agent or distributor circulation",
            "Not Yet Sales-Ready": "Not Yet Sales-Ready: requires substantial repositioning"}
IMAGE_TYPES = (".png", ".jpg", ".jpeg", ".webp")


# ---------------------------------------------------------------- Jon's spec

def spec() -> dict:
    raw = SKILL.read_text(encoding="utf-8")
    raw = re.sub(r"^---\n.*?\n---\n", "", raw, flags=re.S).replace("GPT-generated suggestions", "Suggestions (not attached)").replace("GPT-generated", "suggested, not attached")
    intro = raw.split("REPORT TITLE", 1)[0]
    intro = re.sub(r"^.*?INSTRUCTIONS TO GPT\s*", "", intro, flags=re.S)
    intro = re.sub(r"“?Whenever a report is requested.*?blank document\.”?\s*", "", intro, flags=re.S)   # the Studio builds the document
    body = raw.split("REPORT TITLE", 1)[1]
    structure, _, tail = body.partition("STYLE RULES")
    style = tail.split("STATIC SARACEN BRIDGE REPORTING STANDARD", 1)[0]
    style = re.sub(r"Before reviewing, ask the user.*?\n", "", style)        # asked in the Studio's form instead
    sections = {}
    for m in re.finditer(r"^(\d{1,2})\. ([A-Z][A-Z0-9 /\-–&]+)\n(.*?)(?=^\d{1,2}\. [A-Z][A-Z0-9 /\-–&]+\n|\Z)", structure, re.M | re.S):
        sections[int(m.group(1))] = (m.group(2).strip(), m.group(3).strip())
    rules = re.sub(r"\n{3,}", "\n\n", intro.strip() + "\n\nSTYLE RULES\n" + style.strip())
    return {"rules": rules, "sections": sections}


def _system(sp: dict, task: str) -> str:
    return (sp["rules"] + "\n\n" + task + "\n\nReturn only the JSON object requested. Write plain prose in the strings: "
            "no markdown, no bullet symbols, no headings. Never mention AI, ChatGPT or how this analysis was made.")


def _brief(sp: dict, *nums: int) -> str:
    return "\n\n".join(f"{n}. {sp['sections'][n][0]}\n{sp['sections'][n][1]}" for n in nums if n in sp["sections"])


# ---------------------------------------------------------------- schemas

def _obj(props: dict, required: list | None = None) -> dict:
    return {"type": "object", "properties": props, "required": required or list(props), "additionalProperties": False}


S, I = {"type": "string"}, lambda lo, hi: {"type": "integer", "minimum": lo, "maximum": hi}
L = lambda n=None, m=None: {"type": "array", "items": {"type": "string"}, **({"minItems": n} if n else {}), **({"maxItems": m} if m else {})}

Sx = lambda n: {"type": "string", "maxLength": n}      # bounded: a small model can otherwise loop inside one string
PAGE = _obj({"role": Sx(40), "shows": Sx(400), "words": Sx(300), "visual_score": I(1, 10), "sells": Sx(300),
             "issues": {"type": "array", "maxItems": 4, "items": Sx(200)}})
SNAPSHOT = _obj({"format": S, "genre": S, "tone": S, "core_proposition": S, "primary_audience": S, "market_lane": S,
                 "immediate_impression": S, "main_strength": S, "main_weakness": S,
                 "current_proposition": S, "improved_proposition": S, "commercial_hook": S,
                 "current_logline": S, "logline_review": S, "revised_logline": S})
CAST = _obj({"character": S, "function": S, "emotional_hook": S, "casting_appeal": S, "actor_type": S,
             "status": {"type": "string", "enum": ["Attached", "Wish list", "Suggested"]}, "names": L(0, 3)})
STORY = _obj({"story_sell": S, "clear": L(0, 6), "unclear": L(0, 6), "move_earlier": L(0, 4),
              "characters": {"type": "array", "minItems": 1, "maxItems": 6, "items": CAST},
              "director_named": S, "director_assessment": S,
              "director_suggestions": {"type": "array", "maxItems": 3, "items": _obj({"name": S, "why": S})}})
VISUAL = _obj({"visual_tone": S, "sells_visually": S, "tone_matches_story": S, "cinematic_or_generic": S,
               "shows_finished_film": S, "castable_and_directable": S, "design_presentation": S,
               "strongest_pages": {"type": "array", "maxItems": 3, "items": _obj({"page": I(1, MAX_PAGES), "why": S})},
               "weakest_pages": {"type": "array", "maxItems": 3, "items": _obj({"page": I(1, MAX_PAGES), "why": S})},
               "cut_simplify_redesign": L(1, 8)})
MARKET = _obj({"primary_genre": S, "secondary_genre": S, "audience": S, "buyers": S, "theatrical_potential": S,
               "streamer_broadcaster_potential": S, "international_appeal": S, "positioning_verdict": S,
               "comparables_assessment": S,
               "better_comparables": {"type": "array", "maxItems": 5, "items": _obj({"title": S, "year": I(1950, 2030), "why": S})},
               "budget_summary": S, "scale_signals": L(3, 8),
               "budget_feel": {"type": "string", "enum": ["Low", "Mid", "Premium"]},
               "sales_usefulness": S, "sales_tool_usefulness_score": I(0, 100)})
REBUILD = _obj({"slides": {"type": "array", "minItems": 12, "maxItems": 15,
                           "items": _obj({"slide": I(1, 15), "title": S, "purpose": S, "content": S, "visual_direction": S})},
                "must_fix": L(1, 6), "should_improve": L(1, 6), "optional_enhancement": L(0, 5)})
SCORES = _obj({"scores": _obj({k: I(0, 100) for k in CATEGORIES}),
               "final_score": I(0, 100), "verdict": {"type": "string", "enum": list(VERDICTS)}, "verdict_reason": S})


# ---------------------------------------------------------------- the deck as page images

def _jpeg(img) -> bytes:
    img = img.convert("RGB")
    w, h = img.size
    k = LONG_SIDE / max(w, h)
    if k < 1:
        from PIL import Image
        img = img.resize((max(1, int(w * k)), max(1, int(h * k))), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=84, optimize=True)
    return buf.getvalue()


def pages(files: list[tuple[str, bytes]]) -> list[dict]:
    """[(filename, bytes)] -> [{"image": jpeg, "text": page text}] in deck order. A PDF deck, or one image per page."""
    from PIL import Image
    out = []
    for name, data in files:
        low = name.lower()
        if low.endswith(".pdf"):
            import pypdfium2 as pdfium
            pdf = pdfium.PdfDocument(data)
            try:
                for i in range(len(pdf)):
                    if len(out) >= MAX_PAGES:
                        break
                    page = pdf[i]
                    w, h = page.get_size()
                    scale = min(4.0, LONG_SIDE / max(w, h, 1))
                    img = page.render(scale=scale).to_pil()
                    tp = page.get_textpage()
                    text = tp.get_text_range() or ""
                    tp.close()
                    page.close()
                    out.append({"image": _jpeg(img), "text": re.sub(r"\s+", " ", text).strip()[:1500]})
            finally:
                pdf.close()
        elif low.endswith(IMAGE_TYPES):
            out.append({"image": _jpeg(Image.open(io.BytesIO(data))), "text": ""})
        elif low.endswith((".pptx", ".key", ".ppt")):
            raise ValueError(f"{name}: export the deck to PDF first (File → Save as PDF) and add the PDF.")
        else:
            raise ValueError(f"{name}: a look book must be a PDF or images (PNG, JPG).")
    if not out:
        raise ValueError("No pages found in the deck.")
    return out[:MAX_PAGES]


# ---------------------------------------------------------------- the run

def context(info: dict) -> str:
    """What the user told us about the project: attachments are only what is stated here."""
    rows = [("Project title", info.get("title")), ("Format", info.get("format")), ("Logline (as supplied)", info.get("logline")),
            ("Synopsis or treatment notes", info.get("synopsis")), ("Attached cast (confirmed)", info.get("cast")),
            ("Attached director (confirmed)", info.get("director")), ("Budget", info.get("budget")),
            ("Comparables supplied", info.get("comparables")), ("Sales or market notes", info.get("notes"))]
    lines = [f"{k}: {v.strip()}" for k, v in rows if v and str(v).strip()]
    out = "PROJECT INFORMATION SUPPLIED BY THE USER (anything not listed here is not stated; no cast or director is attached unless listed):\n" + ("\n".join(lines) or "None supplied.")
    if (info.get("opinion") or "").strip():
        out += f"\n\nTHE USER'S OWN VIEW OF THE DECK (use it to guide tone and focus, not to soften the scores):\n{info['opinion'].strip()}"
    return out


def _page_notes(notes: list[dict]) -> str:
    return "\n".join(f"PAGE {i}: [{n['role']}] shows {n['shows']} | words: {n['words']} | visual {n['visual_score']}/10 | "
                     f"sells: {n['sells']}" + (f" | issues: {'; '.join(n['issues'])}" if n["issues"] else "")
                     for i, n in enumerate(notes, 1))


def write(deck: list[dict], info: dict, settings: dict, progress=lambda m: None, cancelled=lambda: False,
          mode: str | None = None) -> dict:
    ms = llm.mode_settings(settings, mode)
    engine, why = llm.resolve(settings, ms["mode"])
    if not engine:
        raise llm.EngineError(why)
    ok, why = llm.can_see(engine)
    if not ok:
        raise llm.EngineError(why)
    think = bool(ms["think"])
    extra = 6000 if think else 0
    sp = spec()
    t0 = time.time()
    # Deep mode thinks within a budget: short per page (a deck can run to 60 pages), the full allowance for the sections
    room = lambda images: (min(extra, 1024) if images else extra)
    call = lambda system, user, schema, tokens, images=None: llm.chat(
        engine, system, user, schema=schema, settings=settings, max_tokens=tokens + room(images), temperature=0.3, think=think,
        images=images, think_budget=room(images) or None)
    look_sys = _system(sp, "TASK: You are looking at one page of a film or TV look book, as an image, to review it as a sales "
                           "tool later. Record what the page is for (cover, logline, character, tone, comps...), what it shows, "
                           "what its words say, how well it sells, and what is wrong with it. Score its visual quality "
                           "strictly, out of 10, against a premium cinematic look book.")
    ctx = context(info)
    notes = []
    for i, p in enumerate(deck, 1):
        if cancelled():
            raise InterruptedError("Cancelled")
        progress(f"Looking at page {i} of {len(deck)}")
        words = f"\n\nTEXT ON THE PAGE (extracted):\n{p['text']}" if p.get("text") else ""
        notes.append(call(look_sys, f"{ctx}\n\nPAGE {i} OF {len(deck)}.{words}", PAGE, 700, [p["image"]]))
    base = f"{ctx}\n\nTHE LOOK BOOK, PAGE BY PAGE ({len(deck)} pages):\n{_page_notes(notes)}"
    out = {}
    steps = [("snapshot", SNAPSHOT, _brief(sp, 1, 2, 3) + "\n(Scores and the verdict come later: do not give them here.)", 1600),
             ("story", STORY, _brief(sp, 4, 5, 6), 2400),
             ("visual", VISUAL, _brief(sp, 7, 8), 2000),
             ("market", MARKET, _brief(sp, 9, 10, 11, 12), 2200),
             ("rebuild", REBUILD, _brief(sp, 13, 14), 2800)]
    for key, schema, brief, tokens in steps:
        if cancelled():
            raise InterruptedError("Cancelled")
        progress(f"Writing {key}")
        out[key] = call(_system(sp, "TASK: Write these sections of the look book analysis.\n\n" + brief), base, schema, tokens)
    progress("Scoring")
    draft = (f"\n\nDRAFT ASSESSMENT SO FAR:\nImpression: {out['snapshot']['immediate_impression']}\n"
             f"Story sell: {out['story']['story_sell']}\nVisual tone: {out['visual']['visual_tone']}\n"
             f"Design: {out['visual']['design_presentation']}\nPositioning: {out['market']['positioning_verdict']}\n"
             f"Sales usefulness: {out['market']['sales_usefulness']} ({out['market']['sales_tool_usefulness_score']}/100)\n"
             f"Must fix: " + " | ".join(out["rebuild"]["must_fix"]))
    out["scores"] = call(_system(sp, "TASK: Score and conclude.\n\n" + _brief(sp, 15, 16)), base + draft, SCORES, 1100)
    res = finish(out, notes, info, engine, time.time() - t0)
    res["made_with"]["mode"] = ms["mode"]
    return res


def _known_director(name: str) -> bool:
    return any(_norm(r["director_name"]) == _norm(name) for r in refdata.rows("SELECT director_name FROM talent_directors"))


def finish(out: dict, notes: list[dict], info: dict, engine, seconds: float) -> dict:
    sc = out["scores"]
    scores = {k: max(0, min(100, int(sc["scores"].get(k, 0) or 0))) for k in CATEGORIES}
    average = round(sum(scores.values()) / len(scores), 1)
    final = max(0, min(100, int(sc.get("final_score") or 0)))
    checks = []
    if abs(final - average) > 12:
        checks.append(f"The final score ({final}) is more than 12 points from the average of the 13 scores ({average}). "
                      "The Saracen Bridge rule linking them is not written down (register G-01).")
    attached = (info.get("cast") or "") + " " + (info.get("director") or "")
    for c in out["story"]["characters"]:
        if c["status"] == "Attached" and not any(_norm(n) and _norm(n) in _norm(attached) for n in c["names"] or [""]):
            checks.append(f"{c['character']}: marked as attached, but no attachment was supplied. Saracen Bridge rule: never imply attachment.")
            c["status"] = "Suggested"
    unknown = [n for c in out["story"]["characters"] for n in c["names"] if c["status"] != "Attached" and not _known_actor(n)]
    if unknown:
        checks.append("Cast suggestions not in the Saracen Bridge actor database (check they are real and the spelling): " + ", ".join(dict.fromkeys(unknown)) + ".")
    dirs = [d["name"] for d in out["story"]["director_suggestions"] if not _known_director(d["name"])]
    if dirs:
        checks.append("Director suggestions not in the Saracen Bridge director database (check they are real): " + ", ".join(dirs) + ".")
    flat = json.dumps(out, ensure_ascii=False)
    if FORBIDDEN.search(flat):
        checks.append("The text mentions AI, ChatGPT or a language model. Saracen Bridge rules forbid any reference to how the report was made.")
    if URL.search(flat):
        checks.append("The text contains a web address, which Saracen Bridge rules forbid. Edit before sending.")
    n = len(notes)
    for key in ("strongest_pages", "weakest_pages"):
        out["visual"][key] = [p for p in out["visual"][key] if 1 <= p["page"] <= n]
    return {"title": info.get("title") or "Untitled look book", "date": date.today().isoformat(), "pages": n,
            "page_notes": notes, "sections": out, "scores": scores, "average": average, "final_score": final,
            "verdict": sc["verdict"], "verdict_text": VERDICTS[sc["verdict"]], "checks": checks,
            "made_with": {"engine": engine.kind, "model": engine.model, "pages_read": n, "seconds": round(seconds, 1)}}
