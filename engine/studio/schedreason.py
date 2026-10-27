"""Scheduling & Budgeting: a reasoned shooting order (1.1.6).

Tim, 27 Oct: "deep reasoning on schedule". The stripboard the budget builds is mechanical: day scenes, then night
scenes, grouped by site, packed to the pace. A 1st AD reasons further: block each actor's scenes so they aren't held
for days between them, finish a site before moving, shoot weather-exposed exteriors early with cover sets nearby,
keep child performers to day work, and give stunts, water and intimacy their preparation.

This pass gives the model the scene list (number, day or night, interior or exterior, site and set, length in eighths,
cast, and the production elements tagged) and the first-pass board, and asks it to reason out a better order, with
the change and the reason for each. Deep reasoning (thinking on) is the default for this pass.

Rule 1 (27 Oct): a language model alone is not a reliable scheduler (SCHEDBench, 2026: across models, 15% of
natural-language scheduling answers were feasible; the best model 56%), and the core of the problem, ordering scenes
so actors aren't paid to wait, is the talent scheduling problem (Cheng, Diamond & Lin 1993), NP-hard, solved exactly
only to about 32 scenes (Qin et al., arXiv 1401.5869). So the Studio first optimises the order itself (optimise: local search
for fewest shooting days, then fewest company moves, then fewest days actors are held), and the model reasons from
that board, for what the arithmetic can't see: weather cover, child, stunt and water days, the order of the story.

The answer is checked, not trusted. Every scene must appear once: a missing scene is put back on a day with the same
site and day or night where there's room, and the repair is listed. A day that mixes day and night work is split. A
day over the pace is flagged. Both boards are measured the same way (shooting days, company moves, cast hold days,
days over the pace), and the user chooses which one the budget uses.
"""
from __future__ import annotations

import time
from collections import OrderedDict

from . import budget, llm

OVER = 1.25                     # a day may run to 125% of the pace before it is flagged


def _flags(tag: dict | None) -> list[str]:
    if not tag:
        return []
    out = [k for k in ("stunts", "minors", "animals", "vfx", "sfx", "weapons", "vehicles") if tag.get(k)]
    out += [k for k in ("water", "intimacy") if tag.get(k)]
    if tag.get("background") in ("31-100", "over 100"):
        out.append(f"crowd {tag['background']}")
    return out


def scene_lines(breakdown: dict, elements: dict | None = None) -> list[str]:
    tags = {s["scene"]: s for s in (elements or {}).get("scenes") or [] if s.get("tagged")}
    lens = budget.scene_eighths(breakdown)
    out = []
    for i, s in enumerate(breakdown.get("scenes") or []):
        n = s.get("number", i + 1)
        parts = [f"S{n}", "NIGHT" if budget._night(s.get("time_of_day")) else "DAY", s.get("int_ext") or "INT",
                 f"site {budget.site(s)} / {(s.get('location') or s.get('heading') or '').upper()}", budget._eighths(lens[i]) + " pages",
                 "cast: " + (", ".join(s.get("characters") or []) or "none")]
        fl = _flags(tags.get(n))
        if fl:
            parts.append("elements: " + ", ".join(fl))
        out.append(" | ".join(parts))
    return out


def _schema(numbers: list[int], max_days: int) -> dict:
    day = {"type": "object", "additionalProperties": False, "required": ["scenes", "note"],
           "properties": {"scenes": {"type": "array", "minItems": 1, "items": {"type": "integer", "enum": numbers}},
                          "note": {"type": "string"}}}
    change = {"type": "object", "additionalProperties": False, "required": ["change", "reason"],
              "properties": {"change": {"type": "string"}, "reason": {"type": "string"}}}
    return {"type": "object", "additionalProperties": False, "required": ["days", "changes", "risks"],
            "properties": {"days": {"type": "array", "minItems": 1, "maxItems": max_days, "items": day},
                           "changes": {"type": "array", "maxItems": 12, "items": change},
                           "risks": {"type": "array", "maxItems": 8, "items": {"type": "string"}}}}


SYSTEM = ("You are an experienced 1st assistant director scheduling an independent feature for Saracen Bridge. You are "
          "given every scene and a starting stripboard the Studio has already optimised by arithmetic (fewest days, then company "
          "moves, then days actors are held). Reason out the shooting order a real production would use, changing the board "
          "only where it helps:\n"
          "- Every scene exactly once. Don't split scenes.\n"
          "- About {pace} pages a shooting day; never more than {most} pages in one day.\n"
          "- Never put day and night scenes on the same shooting day. Group the night work into runs, and note the "
          "turnaround the crew needs after a night run.\n"
          "- At most one company move a day (a move is a second site in a day); finish a site before leaving it.\n"
          "- Block each principal actor's scenes together so they work consecutive days and are not held between them; the "
          "leads matter most, then actors with few scenes (fewest days on the books).\n"
          "- Weather-exposed exteriors early, with interior scenes at the same site as cover.\n"
          "- Child performers in day scenes, on shorter days (in England a child aged 5 to 8 may be at the place of performance "
          "8 hours a day, 9 to school-leaving age 9.5 hours, under 5 only 5 hours). Stunts, water work and intimacy not on the "
          "first day, with time to prepare.\n"
          "Return the days in shooting order with a short note for each, the main changes from the first pass with the reason "
          "for each, and the risks the schedule still carries. Base everything on the scene list; invent nothing.")


def _board(breakdown: dict, days: list[list[int]]) -> list[dict]:
    """A stripboard (budget.stripboard's shape) from days of whole scenes."""
    scenes = breakdown.get("scenes") or []
    lens = budget.scene_eighths(breakdown)
    by_n = {s.get("number", i + 1): (s, lens[i]) for i, s in enumerate(scenes)}
    out = []
    for k, nums in enumerate(days, 1):
        sites, locs, cast, e, night = OrderedDict(), OrderedDict(), OrderedDict(), 0, False
        for n in nums:
            s, ln = by_n[n]
            e += ln
            night = night or budget._night(s.get("time_of_day"))
            sites.setdefault(budget.site(s), set()).add(s.get("int_ext") or "")
            locs[(s.get("location") or s.get("heading") or "UNKNOWN").upper()] = True
            for ch in s.get("characters") or []:
                cast[ch] = True
        ie = [" ".join(sorted(v)) for v in sites.values()]
        out.append({"day": k, "scenes": list(nums), "eighths": e, "pages": budget._eighths(e), "night": night,
                    "sites": list(sites), "locations": list(locs), "moves": max(0, len(sites) - 1),
                    "int_locations": sum(1 for x in ie if "EXT" not in x), "ext_locations": sum(1 for x in ie if "EXT" in x),
                    "cast": list(cast)})
    return out


def metrics(breakdown: dict, board: list[dict], pages_per_day: float) -> dict:
    cap = round(pages_per_day * 8)
    dood = budget.day_out_of_days(breakdown, board)
    return {"days": len(board), "moves": sum(d["moves"] for d in board),
            "hold_days": sum(c["hold_days"] for c in dood),
            "lead_hold_days": sum(c["hold_days"] for c in sorted(dood, key=lambda c: -c["work_days"])[:2]),
            "over_pace": sum(1 for d in board if d["eighths"] > cap * OVER), "night_days": sum(1 for d in board if d["night"])}


def repair(breakdown: dict, days: list[list[int]], pages_per_day: float) -> tuple[list[list[int]], list[str]]:
    """The model's days made whole: unknown and repeated scenes dropped, missing ones put back, mixed days split."""
    scenes = breakdown.get("scenes") or []
    lens = budget.scene_eighths(breakdown)
    info = {s.get("number", i + 1): (budget._night(s.get("time_of_day")), budget.site(s), lens[i]) for i, s in enumerate(scenes)}
    cap = round(pages_per_day * 8)
    notes, seen, out = [], set(), []
    for nums in days:
        keep = []
        for n in nums:
            if n not in info:
                continue
            if n in seen:
                notes.append(f"Scene {n} appeared twice; kept the first.")
                continue
            seen.add(n)
            keep.append(n)
        if not keep:
            continue
        dn = [n for n in keep if not info[n][0]], [n for n in keep if info[n][0]]
        if dn[0] and dn[1]:
            notes.append(f"A day mixed day and night scenes ({', '.join(map(str, keep))}); split into a day and a night.")
            out += [dn[0], dn[1]]
        else:
            out.append(keep)
    for n in [n for n in info if n not in seen]:
        night, st, ln = info[n]
        size = lambda d: sum(info[x][2] for x in d)
        fits = [d for d in out if info[d[0]][0] == night and size(d) + ln <= cap * OVER]
        best = next((d for d in fits if any(info[x][1] == st for x in d)), fits[0] if fits else None)
        if best is not None:
            best.append(n)
            notes.append(f"Scene {n} was left out; added to the day with {'the same site' if any(info[x][1] == st for x in best[:-1]) else 'room'}.")
        else:
            out.append([n])
            notes.append(f"Scene {n} was left out; given a day of its own at the end.")
    return out, notes


def _cost(breakdown: dict, order: list[int], ppd: float) -> tuple:
    board = budget.stripboard(breakdown, ppd, order=order)
    held = sum(c["hold_days"] for c in budget.day_out_of_days(breakdown, board))
    return (len(board), sum(d["moves"] for d in board), held)


def _blocks(breakdown: dict, order: list[int]) -> list[list[int]]:
    """Runs of consecutive scenes at one site, day or night."""
    info = {s.get("number", i + 1): (budget._night(s.get("time_of_day")), budget.site(s)) for i, s in enumerate(breakdown["scenes"])}
    out = []
    for n in order:
        if out and info[out[-1][-1]] == info[n]:
            out[-1].append(n)
        else:
            out.append([n])
    return out


class _Eval:
    """budget.stripboard's packing and the measures, for one order, without building the board: the optimiser tries
    tens of thousands of orders. Checked against stripboard + metrics in the tests."""

    def __init__(self, breakdown: dict, ppd: float):
        scenes = breakdown.get("scenes") or []
        lens = budget.scene_eighths(breakdown)
        self.cap = max(1, round(ppd * 8))
        self.info = {s.get("number", i + 1): (budget._night(s.get("time_of_day")), budget.site(s), lens[i], tuple(s.get("characters") or []))
                     for i, s in enumerate(scenes)}
        self.cast = {c["name"] for c in breakdown.get("cast") or []}

    def __call__(self, order: list[int]) -> tuple[int, int, int]:
        cap, info = self.cap, self.info
        days = moves = 0
        night = None
        fill = cap
        sites: set = set()
        first: dict = {}
        last: dict = {}
        count: dict = {}
        today: set = set()

        def close():
            nonlocal moves
            if days:
                moves += max(0, len(sites) - 1)
                for ch in today:
                    count[ch] = count.get(ch, 0) + 1
                    first.setdefault(ch, days)
                    last[ch] = days

        for n in order:
            nt, st, e, chars = info[n]
            while e > 0:
                if days == 0 or night != nt or fill >= cap:
                    close()
                    days += 1
                    night, fill, sites, today = nt, 0, set(), set()
                take = min(e, cap - fill)
                fill += take
                e -= take
                sites.add(st)
                today.update(ch for ch in chars if ch in self.cast)
        close()
        held = sum(last[ch] - first[ch] + 1 - count[ch] for ch in count)
        return days, moves, held


def optimise(breakdown: dict, pages_per_day: float | None = None, time_limit: float = 5.0) -> dict:
    """The Studio's own shooting order, by local search from the first pass: fewest shooting days first, then fewest
    company moves, then fewest days actors are held between work days. Moves tried: a site's run of scenes to another
    place, and a scene to another place within its run. Each improvement is kept and the search carries on; it stops
    when a full pass improves nothing, or at the time limit."""
    ppd = float(pages_per_day or budget.PAGES_PER_DAY["base"])
    first = budget.stripboard(breakdown, ppd)
    seen, order = set(), []
    for d in first:                                 # the first pass's order of scenes (a split scene once)
        for n in d["scenes"]:
            if n not in seen:
                seen.add(n)
                order.append(n)
    cost = _Eval(breakdown, ppd)
    best, t0, rounds = cost(order), time.time(), 0
    out_of_time = lambda: time.time() - t0 > time_limit
    improved = True
    while improved and not out_of_time():
        improved, rounds = False, rounds + 1
        i = 0
        while i < len(blocks := _blocks(breakdown, order)) and not out_of_time():     # a site's run to another place
            moved = False
            for j in range(len(blocks) + 1):
                if j in (i, i + 1):
                    continue
                bl = blocks[:i] + blocks[i + 1:]
                bl.insert(j if j < i else j - 1, blocks[i])
                cand = [n for blk in bl for n in blk]
                c = cost(cand)
                if c < best:
                    best, order, improved, moved = c, cand, True, True
                    break
            i += 0 if moved else 1
            if moved and out_of_time():
                break
        for b in _blocks(breakdown, order):         # a scene to another place within its run
            if len(b) < 3 or out_of_time():
                continue
            start = order.index(b[0])
            cur = list(b)
            for a in range(len(cur)):
                for z in range(len(cur)):
                    if a == z:
                        continue
                    nb = cur[:a] + cur[a + 1:]
                    nb.insert(z, cur[a])
                    cand = order[:start] + nb + order[start + len(cur):]
                    c = cost(cand)
                    if c < best:
                        best, order, cur, improved = c, cand, nb, True
    board = budget.stripboard(breakdown, ppd, order=order)
    return {"order": order, "board": board, "pages_per_day": ppd, "measures": metrics(breakdown, board, ppd),
            "first_pass": metrics(breakdown, first, ppd), "seconds": round(time.time() - t0, 2), "rounds": rounds,
            "timed_out": out_of_time(), "date": time.strftime("%Y-%m-%d"), "scene_count": len(breakdown.get("scenes") or [])}


def reason(breakdown: dict, settings: dict, *, pages_per_day: float | None = None, elements: dict | None = None,
           mode: str | None = "deep", progress=lambda m: None, cancelled=lambda: False) -> dict:
    """The model's reasoned order, checked and measured against the first pass."""
    ms = llm.mode_settings(settings, mode)
    engine, why = llm.resolve(settings, ms["mode"])
    if not engine:
        raise llm.EngineError(why)
    if not breakdown.get("scenes"):
        raise ValueError("The script has no scenes to schedule.")
    ppd = float(pages_per_day or budget.PAGES_PER_DAY["base"])
    first = budget.stripboard(breakdown, ppd)
    progress("Optimising the order (fewest days, then moves, then actors held)")
    opt = optimise(breakdown, ppd)
    start = opt["board"]
    numbers = [s.get("number", i + 1) for i, s in enumerate(breakdown["scenes"])]
    lines = scene_lines(breakdown, elements)
    board_text = "\n".join(f"Day {d['day']} ({'night' if d['night'] else 'day'}, {d['pages']} pages): scenes "
                           + ", ".join(map(str, d["scenes"])) for d in start)
    m = opt["measures"]
    user = (f"SCENES ({len(lines)}):\n" + "\n".join(lines) + f"\n\nSTARTING STRIPBOARD ({len(start)} days at {ppd:g} pages a day), "
            f"already optimised for fewest days, company moves ({m['moves']}) and days actors are held ({m['hold_days']}). Improve it "
            "only where a real production would, and say why:\n" + board_text)
    think = bool(ms["think"])
    extra = 6000 if think else 0
    progress("Reasoning out the shooting order" + (" (thinking first)" if think else ""))
    if cancelled():
        raise InterruptedError("Cancelled")
    t0 = time.time()
    ans = llm.chat(engine, SYSTEM.format(pace=f"{ppd:g}", most=f"{ppd * OVER:g}"), user,
                   schema=_schema(numbers, max(len(first) * 2, len(first) + 10)), settings=settings,
                   max_tokens=1200 + 14 * len(numbers) + 60 * len(first) + extra, temperature=0.2, think=think,
                   think_budget=extra or None) or {}
    progress("Checking the order")
    days, notes = repair(breakdown, [list(d.get("scenes") or []) for d in ans.get("days") or []], ppd)
    board = _board(breakdown, days)
    day_notes = [str(d.get("note") or "").strip() for d in ans.get("days") or []]
    for k, d in enumerate(board):
        d["note"] = day_notes[k] if k < len(day_notes) and not notes else ""
    return {"days": days, "board": board, "changes": [{"change": str(c.get("change") or ""), "reason": str(c.get("reason") or "")}
                                                      for c in ans.get("changes") or []],
            "risks": [str(r) for r in ans.get("risks") or []], "repairs": notes, "pages_per_day": ppd,
            "measures": {"reasoned": metrics(breakdown, board, ppd), "first_pass": metrics(breakdown, first, ppd), "optimised": opt["measures"]},
            "optimised": opt,
            "mode": ms["mode"], "engine": engine.describe(), "seconds": round(time.time() - t0),
            "scene_count": len(numbers), "date": time.strftime("%Y-%m-%d")}
