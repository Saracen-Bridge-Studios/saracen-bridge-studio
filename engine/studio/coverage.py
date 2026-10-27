"""Script coverage writer: Jon's #2 Script Coverage Analysis, run on a local model.

Jon's SKILL.md is the specification and is used verbatim as the model's instructions (house rules plus each
section's brief). The model works in two passes so any script fits any context size:

  1. read   the script in scene-aligned parts; for each part it returns structured notes (beats, characters,
            turning points, tone, dialogue, production demands)
  2. write  the 11 sections from those notes plus the deterministic breakdown facts (pages, scenes, INT/EXT,
            day/night, locations, speaking roles), in four calls

Scores are the model's judgement; the composite is computed here with Jon's weights, never by the model.
Open rules stay visible: how scores map to the verdict and to the 1–100 readiness score is undefined in Jon's
spec (register G-01/G-02), so the model's verdict and readiness are kept as proposals and checked for consistency.
"""
from __future__ import annotations

import json
import re
import time
from datetime import date

from . import llm, refdata, script

WEIGHTS = {"Concept and Hook": .20, "Story and Structure": .20, "Characters": .20, "Dialogue": .10,
           "Tone and Genre Execution": .10, "Production Feasibility": .10, "Commercial Appeal": .10}
SKILL = refdata.app_root() / "sources" / "t02_script_coverage" / "skills" / "instructions" / "SKILL.md"
FORBIDDEN = re.compile(r"\b(chat\s?gpt|openai|language model|\bAI\b|artificial intelligence|automated analysis)", re.I)
URL = re.compile(r"https?://\S+|www\.\S+")


# ---------------------------------------------------------------- Jon's spec

def spec() -> dict:
    """SKILL.md split into house rules and the brief for each numbered section."""
    raw = SKILL.read_text(encoding="utf-8")
    body = raw.split("INSTRUCTIONS", 1)[1] if "INSTRUCTIONS" in raw else raw
    rules = body.split("REPORT STRUCTURE", 1)[0]
    structure = body.split("REPORT STRUCTURE", 1)[1].split("FINAL OUTPUT REQUIREMENTS", 1)[0]
    final_req = body.split("FINAL OUTPUT REQUIREMENTS", 1)[1].split("Static Saracen Bridge Reporting Standard", 1)[0] \
        if "FINAL OUTPUT REQUIREMENTS" in body else ""
    sections = {}
    for m in re.finditer(r"^(\d{1,2})\. ([A-Z][A-Z0-9 \-–&]+)\n(.*?)(?=^\d{1,2}\. [A-Z][A-Z0-9 \-–&]+\n|\Z)", structure, re.M | re.S):
        sections[int(m.group(1))] = (m.group(2).strip(), m.group(3).strip())
    rules = re.sub(r"Do not ask permission.*?\n", "", rules)          # chat-only instruction
    rules = re.sub(r"Maximum report length.*?shorter report\.\n", "", rules, flags=re.S)
    return {"rules": re.sub(r"\n{3,}", "\n\n", rules).strip(), "final": final_req.strip(), "sections": sections}


def _system(sp: dict, extra: str) -> str:
    return (sp["rules"] + "\n\n" + sp["final"] + "\n\n" + extra +
            "\n\nReturn only the JSON object requested. Write plain prose in the strings: no markdown, no bullet symbols, no headings.")


def _brief(sp: dict, *nums: int) -> str:
    return "\n\n".join(f"{n}. {sp['sections'][n][0]}\n{sp['sections'][n][1]}" for n in nums if n in sp["sections"])


# ---------------------------------------------------------------- schemas

def _obj(props: dict, required: list | None = None) -> dict:
    return {"type": "object", "properties": props, "required": required or list(props), "additionalProperties": False}


S, L = {"type": "string"}, lambda n=None, m=None: {"type": "array", "items": {"type": "string"},
                                                     **({"minItems": n} if n else {}), **({"maxItems": m} if m else {})}

NOTES = _obj({"beats": L(1, 10), "characters": {"type": "array", "items": _obj({"name": S, "note": S})},
              "turning_points": L(0, 4), "tone": S, "dialogue": S, "production_demands": L(0, 8)})
STORY = _obj({"concept_sentence": S, "logline": S, "pitch": L(5, 5), "synopsis": L(3, 8)})
CREATIVE = _obj({"concept_and_premise": S, "story_and_structure": S, "characters": S,
                 "casting": {"type": "array", "maxItems": 4, "items": _obj({"role": S, "names": L(1, 3)})},
                 "dialogue": S, "themes_and_tone": S, "worldbuilding": S, "production_feasibility": S})
MARKET = _obj({"target_demographic": S, "audience_profile": S, "release_pathway": S, "sales_agent_tier": S,
               "distributor_suitability": S,
               "comparables": {"type": "array", "minItems": 2, "maxItems": 6,
                               "items": _obj({"title": S, "year": {"type": "integer", "minimum": 1960, "maximum": 2030}, "relevance": S})},
               "awards_festival_potential": S,
               "current_market_fit": S, "risks": L(3, 10)})
DEVELOP = _obj({"rewrite_priorities": L(3, 3), "development_notes": L(5, 10), "character_notes": S, "dialogue_notes": S,
                "structure_notes": S, "commercial_notes": S, "strengths": L(3, 8), "weaknesses": L(3, 8),
                "budget_band": S, "budget_pressure_points": L(2, 8), "risk_if_budget_too_low": S,
                "risk_if_budget_too_high": S, "to_justify_higher_budget": S, "cost_control_opportunities": L(2, 6)})
VERDICT = _obj({"scores": _obj({k: {"type": "integer", "minimum": 1, "maximum": 10} for k in WEIGHTS}),
                "score_reasons": _obj({k: S for k in WEIGHTS}),
                "verdict": {"type": "string", "enum": ["Recommend", "Consider", "Pass"]},
                "commercial_readiness": {"type": "integer", "minimum": 1, "maximum": 100},
                "overall_assessment": S, "commercial_potential": S, "major_strengths": L(2, 4), "primary_issues": L(2, 4),
                "reason_for_verdict": S, "development_priority": S, "best_next_step": S})


# ---------------------------------------------------------------- the run

def facts(b: dict) -> str:
    top = ", ".join(f"{c['name']} ({c['dialogue_blocks']} speeches, {c['scene_count']} scenes)" for c in b["cast"][:8])
    return (f"VERIFIED BREAKDOWN FACTS (counted from the script, not estimates):\n"
            f"Title: {b['title']}\nPages: {'about ' if b.get('pages_estimated') else ''}{b['pages']}\n"
            f"Scenes: {b['scene_count']} (INT {b['int']}, EXT {b['ext']}; DAY {b['day']}, NIGHT {b['night']})\n"
            f"Distinct locations: {len(b['locations'])}: {', '.join(b['locations'][:25])}{' …' if len(b['locations']) > 25 else ''}\n"
            f"Speaking roles: {b['speaking_roles']}. Largest parts: {top}")


def _notes_text(notes: list[dict]) -> str:
    out = []
    for i, n in enumerate(notes, 1):
        out.append(f"PART {i}\nBeats: " + " | ".join(n["beats"]) +
                   ("\nTurning points: " + " | ".join(n["turning_points"]) if n["turning_points"] else "") +
                   "\nCharacters: " + "; ".join(f"{c['name']}: {c['note']}" for c in n["characters"]) +
                   f"\nTone: {n['tone']}\nDialogue: {n['dialogue']}" +
                   ("\nProduction demands: " + "; ".join(n["production_demands"]) if n["production_demands"] else ""))
    return "\n\n".join(out)


def write(filename: str, data: bytes, breakdown: dict, settings: dict, progress=lambda msg: None,
          cancelled=lambda: False, chunk_chars: int | None = None, mode: str | None = None) -> dict:
    ms = llm.mode_settings(settings, mode)
    engine, why = llm.resolve(settings, ms["mode"])
    if not engine:
        raise llm.EngineError(why)
    think = bool(ms["think"])
    extra = 6000 if think else 0          # thinking spends tokens before the answer starts
    sp = spec()
    ctx = int(settings.get("ai_engine", {}).get("context", 16384))
    # a part of the script plus instructions must fit the context: ~3.5 characters per token, half the window
    size = chunk_chars or max(4000, min(24000, int(ctx * 3.5 * 0.5)))
    parts = script.chunks(script.text(filename, data), size)
    if not parts:
        raise ValueError("The script has no readable text (a scanned PDF needs OCR).")
    t0 = time.time()
    call = lambda system, user, schema, tokens: llm.chat(engine, system, user, schema=schema, settings=settings,
                                                          max_tokens=tokens + extra, temperature=0.3, think=think,
                                                          think_budget=extra or None)
    notes = []
    read_sys = _system(sp, "TASK: You are reading one part of a screenplay in order to write coverage later. "
                           "Record what happens and what it reveals, factually and briefly.")
    for i, part in enumerate(parts, 1):
        if cancelled():
            raise InterruptedError("Cancelled")
        progress(f"Reading part {i} of {len(parts)}")
        notes.append(call(read_sys, f"SCREENPLAY PART {i} OF {len(parts)}\n\n{part}", NOTES, 1200))
    base = facts(breakdown) + "\n\nREADING NOTES, IN SCRIPT ORDER:\n\n" + _notes_text(notes)
    out = {}
    steps = [("story", STORY, _brief(sp, 2, 3) + "\nAlso give the one-sentence concept for the Executive Summary.", 1800),
             ("creative", CREATIVE, _brief(sp, 4), 2600),
             ("market", MARKET, _brief(sp, 5, 6), 2000),
             ("develop", DEVELOP, _brief(sp, 7, 8, 9), 2600)]
    for key, schema, brief, tokens in steps:
        if cancelled():
            raise InterruptedError("Cancelled")
        progress(f"Writing {key}")
        out[key] = call(_system(sp, "TASK: Write these sections of the coverage report.\n\n" + brief), base, schema, tokens)
    progress("Scoring")
    summary = (f"\n\nDRAFT ASSESSMENT SO FAR:\nConcept: {out['creative']['concept_and_premise']}\n"
               f"Story: {out['creative']['story_and_structure']}\nCharacters: {out['creative']['characters']}\n"
               f"Dialogue: {out['creative']['dialogue']}\nFeasibility: {out['creative']['production_feasibility']}\n"
               f"Market fit: {out['market']['current_market_fit']}\nRisks: " + " | ".join(out["market"]["risks"]))
    out["verdict"] = call(_system(sp, "TASK: Score and conclude.\n\n" + _brief(sp, 10, 1, 11)),
                          base + summary, VERDICT, 1600)
    res = finish(out, breakdown, engine, len(parts), time.time() - t0)
    res["made_with"]["mode"] = ms["mode"]
    return res


_ACTORS: set | None = None


def _norm(name: str) -> str:
    return re.sub(r"[^a-z]", "", name.lower().replace("’", "'"))


def _known_actor(name: str) -> bool:
    global _ACTORS
    if _ACTORS is None:
        _ACTORS = {_norm(r["actor"]) for r in refdata.rows("SELECT actor FROM talent_actors")}
    return _norm(name) in _ACTORS


def comparable_text(c) -> str:
    return f"{c['title']} ({c['year']}): {c['relevance']}" if isinstance(c, dict) else str(c)


def finish(out: dict, breakdown: dict, engine, parts: int, seconds: float) -> dict:
    v = out["verdict"]
    scores = {k: max(1, min(10, int(v["scores"].get(k, 0) or 1))) for k in WEIGHTS}
    composite = round(sum(scores[k] * w for k, w in WEIGHTS.items()), 2)
    checks = []
    readiness = max(1, min(100, int(v.get("commercial_readiness") or 1)))
    if abs(readiness - composite * 10) > 15:
        checks.append(f"Commercial Readiness {readiness} differs from composite × 10 ({composite * 10:.0f}). "
                      "The Saracen Bridge rule linking them is open (register G-01).")
    names = [n for c in out.get("creative", {}).get("casting", []) for n in c.get("names", [])]
    unknown = [n for n in dict.fromkeys(names) if not _known_actor(n)]
    if unknown:
        checks.append("Casting names not in the Saracen Bridge actor database (check the spelling, or that they are real): "
                      + ", ".join(unknown) + ".")
    flat = json.dumps(out, ensure_ascii=False)
    if FORBIDDEN.search(flat):
        checks.append("The text mentions AI, ChatGPT or a language model. Saracen Bridge rules forbid any reference to how the "
                      "report was made: check the mention is about the story itself.")
    if URL.search(flat):
        checks.append("The text contains a web address, which Saracen Bridge rules forbid. Edit before sending.")
    return {"title": breakdown["title"], "date": date.today().isoformat(), "sections": out,
            "scores": scores, "weights": WEIGHTS, "composite": composite, "commercial_readiness": readiness,
            "verdict": v["verdict"], "checks": checks,
            "made_with": {"engine": engine.kind, "model": engine.model, "parts_read": parts, "seconds": round(seconds, 1)}}
