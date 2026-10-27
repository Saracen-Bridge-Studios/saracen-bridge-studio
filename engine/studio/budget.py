"""Preliminary schedule and budget from a script breakdown (Scheduling & Budgeting, 1.0.4).

Jon's instructions for this tool (sources/t03_schedule_budget SKILL.md) ask for a defensible shooting-day range, a
stripboard logic, cast day-out-of-days, and a budget in standard film-budget logic (above the line, production, post,
other, charges) in lean / base / conservative cases, with every assumption labelled and nothing invented:

- Rates come only from Jon's dated 2026 rate cards (SB Global Production Rate Database v1.2). A role or item the card
  doesn't price for the jurisdiction is a line marked Unknown, never zero.
- Accounts are Jon's controlled chart (SB-COA-1.0, four-digit codes).
- Fees nobody can know from a script (rights, producers, director, principal cast, music, legal) are producer inputs;
  until entered they stay Unknown and the budget stays PRELIMINARY.
- Quantities and durations that his files don't give come from the published sources in ASSUMPTIONS, are labelled,
  and are editable.
"""
from __future__ import annotations

import math
import re
from collections import OrderedDict

from . import refdata

SCENARIOS = ("lean", "base", "conservative")
PAGES_PER_DAY = {"lean": 5.0, "base": 4.0, "conservative": 3.0}
CONTINGENCY = 0.10
MOVE_HOURS = 2                               # a company move costs about 2 hours (SOURCES["moves"])
WEEK = 5                                     # working days per week (5-day weeks)

SOURCES = {
    "pace": ("StudioBinder, 'Film budget planning: how to budget a script breakdown': well-funded independent films shoot "
             "about 4–5 pages a day; Filmustage, 'How to create a shooting schedule for an indie film': most indie schedules "
             "allow 3–5 pages a day"),
    "crew": ("ProVideo Coalition, 'Thinking about crew prep': prep and wrap by role for a 5-week independent feature "
             "(e.g. 1st AD 1 prep day per shoot day; DP 15 days minimum; coordinator and accountant 15 days prep, 2 weeks wrap)"),
    "edit": ("Film Independent, 'Know your crew: post-production producer': a week for the editor's assembly, 10 weeks for "
             "the director's cut (DGA), four to six weeks for sound editing, music and the final mix"),
    "grade": "RedShark News, 'How long does it take to do a colour grade?': a two-hour feature, ten days",
    "moves": ("StudioBinder, 'Stop making these 6 shooting schedule mistakes': a company move often takes 2 hours from strike "
              "to set-up at the next location; Anonymous Production Assistant, 'Company move': more than one company move in a day "
              "is a serious problem"),
    "contingency": ("Vitrina, 'Completion bonds: the producer's insurance policy and the bank's backstop': guarantors usually "
                    "require a 10% contingency; bond fees typically 2–3% of the direct budget"),
}

# ------------------------------------------------------------------------------------------------ crew plan
# (key, Jon's role names by card, count, COA account, prep rule, wrap days, source tag)
# A prep rule is ("per_day", k): k days per shoot day, or ("days", n). "A" marks a planning assumption with no published
# figure (labelled on screen); every other duration is from SOURCES["crew"].
CREW = [
    ("Line producer / UPM", ["Line Producer / UPM", "Production Director / Line Producer", "Production Manager / UPM"], 1, "2001", ("per_day", 1.5), 7.5, "crew"),
    ("Production coordinator", ["Production Coordinator", "Assistant Production Manager / Production Coordinator"], 1, "2013", ("days", 15), 10, "crew"),
    ("Production accountant", ["Production Accountant"], 1, "2010", ("days", 15), 10, "crew"),
    ("1st assistant director", ["1st Assistant Director", "First Assistant Director"], 1, "2005", ("per_day", 1), 1, "crew"),
    ("2nd assistant director", ["2nd Assistant Director", "Second Assistant Director"], 1, "2006", ("days", 12.5), 1, "crew"),
    ("Production assistants", ["Production Assistant / Runner", "Production Assistant"], 2, "2008", ("days", 4), 3, "crew"),
    ("Script supervisor", ["Script Supervisor", "Script Supervisor / Continuity"], 1, "2009", ("days", 3), 2, "crew"),
    ("Director of photography", ["Director of Photography"], 1, "3101", ("days", 15), 0, "crew"),
    ("Camera operator", ["Camera Operator"], 1, "3102", ("days", 2), 0, "A"),
    ("1st assistant camera", ["1st Assistant Camera / Focus Puller", "First Assistant Camera / Focus Puller"], 1, "3104", ("days", 2), 1, "A"),
    ("2nd assistant camera / loader", ["2nd Assistant Camera / Clapper Loader", "2nd Assistant Camera / Loader", "Camera Assistant / Trainee"], 1, "3106", ("days", 2), 1, "crew"),
    ("DIT", ["Digital Imaging Technician"], 1, "3109", ("days", 2), 1, "crew"),
    ("Sound mixer", ["Production Sound Mixer", "Production Sound Mixer / Head of Sound"], 1, "3201", ("days", 1), 0, "A"),
    ("Boom operator", ["1st Assistant Sound / Boom Operator", "Boom Operator", "Sound Assistant / Boom Operator"], 1, "3202", ("days", 0), 0, "A"),
    ("Gaffer", ["Gaffer", "Gaffer / Chief Electrician"], 1, "3001", ("days", 5), 3, "crew"),
    ("Best boy electric", ["Best Boy / Chief Lighting Technician", "Lighting Assistant"], 1, "3002", ("days", 2), 1, "crew"),
    ("Electricians", ["Electrician / Spark", "Set Lighting Technician / Electric", "Electrician / Lighting Technician"], 2, "3003", ("days", 0), 0, "A"),
    ("Key grip", ["Key Grip"], 1, "2901", ("days", 5), 3, "crew"),
    ("Grip", ["Grip", "Grip / Crane Operator"], 1, "2903", ("days", 0), 0, "A"),
    ("Production designer", ["Production Designer", "Production Designer / Art Director"], 1, "2201", ("per_day", 1.5), 5, "crew"),
    ("Art director", ["Art Director", "Art Director / Set Decorator"], 1, "2202", ("per_day", 1.5), 5, "crew"),
    ("Set decorator", ["Set Decorator"], 1, "2401", ("days", 15), 10, "crew"),
    ("Set dressers", ["Set Dresser", "Art Department Coordinator / Set Dresser"], 2, "2405", ("days", 5), 5, "crew"),
    ("Property master", ["Property Master", "Props Master / Props Technician"], 1, "2501", ("days", 15), 10, "crew"),
    ("Standby props", ["Standby Props", "On-Set Props", "Props Assistant"], 1, "2503", ("days", 2), 1, "A"),
    ("Costume designer", ["Costume Designer"], 1, "2701", ("per_day", 1.5), 5, "crew"),
    ("Costume supervisor", ["Costume Supervisor", "Wardrobe Supervisor / Head of Costume"], 1, "2702", ("per_day", 1), 5, "crew"),
    ("Costume standby", ["Costume Standby", "On-Set Costumer", "Costume / Styling Assistant"], 1, "2706", ("days", 2), 1, "A"),
    ("Hair & make-up designer", ["Hair & Make-up Designer", "Head of Make-up"], 1, "2801", ("days", 5), 2, "A"),
    ("Key hair & make-up artist", ["Key Hair & Make-up Artist", "Make-up Artist"], 1, "2802", ("days", 2), 0, "A"),
    ("Location manager", ["Location Manager"], 1, "3402", ("per_day", 1), 5, "crew"),
    ("Location assistant", ["Location Assistant / Marshal", "Location PA / Site Rep", "Key Assistant Location Manager"], 1, "3415", ("days", 5), 2, "A"),
    ("Transport captain", ["Transport Captain / Coordinator"], 1, "3602", ("days", 10), 5, "crew"),
    ("Unit drivers", ["Unit Driver"], 2, "3605", ("days", 0), 0, "A"),
]
# post labour: (key, names, count, account, weeks: "edit" | number, source)
POST_CREW = [
    ("Editor", ["Editor", "Picture Editor"], 1, "5001", "edit", "edit"),
    ("1st assistant editor", ["1st Assistant Editor", "Assistant Picture Editor"], 1, "5002", "edit", "edit"),
    ("Sound editor", ["Sound Editor"], 1, "5201", 5, "edit"),
    ("Re-recording mixer", ["Re-recording Mixer"], 1, "5201", 1, "edit"),
    ("Colourist", ["Colourist", "Colorist"], 1, "5601", 2, "grade"),
]
EDIT_WEEKS_AFTER_WRAP = 11                   # 1 week assembly + 10 weeks director's cut (SOURCES["edit"])

# ------------------------------------------------------------------------------------------------ non-labour
# (key, account, patterns tried in order over "category item", accepted units, quantity, source tag)
# Quantities: "shoot_days", "loc_int", "loc_ext", "total_weeks", "edit_weeks", "walkies", "catering", or a number (in the
# entry's first unit). A card that prices a week item by the day, or the reverse, is converted at 5 days a week.
NON_LABOUR = [
    ("Camera package", "3193", [r"alexa 35", r"full digital cinema camera", r"high-end cinema camera", r"camera body", r"camera package"], ("day",), "shoot_days", "A"),
    ("Lens package", "3193", [r"lens package", r"lens set"], ("day",), "shoot_days", "A"),
    ("DIT cart", "3192", [r"\bdit\b"], ("day",), "shoot_days", "A"),
    ("Lighting package", "3093", [r"medium lighting/grip", r"led lighting package", r"5-ton grip/electric", r"lighting package"], ("day",), "shoot_days", "A"),
    ("Grip package", "2995", [r"grip truck", r"dolly"], ("day",), "shoot_days", "A"),
    ("Generator", "3091", [r"^(?!.*basecamp).*generator"], ("day",), "shoot_days", "A"),
    ("Sound package", "3293", [r"production sound (equipment )?package"], ("day",), "shoot_days", "A"),
    ("Walkie-talkies (20)", "3292", [r"radio|walkie"], ("unit/week", "unit/day"), "walkies", "A"),
    ("Honeywagon", "3681", [r"honeywagon|toilet|amenities"], ("day",), "shoot_days", "A"),
    ("Make-up / wardrobe trailer", "3681", [r"make-up.*(trailer|truck)|wardrobe.*(trailer|truck)"], ("day",), "shoot_days", "A"),
    ("Production / cast trailer", "3681", [r"motorhome|production office trailer|office vehicle|star wagon"], ("day",), "shoot_days", "A"),
    ("Crew vans (2)", "3605", [r"minibus|passenger van|people carrier"], ("day",), 2, "A"),
    ("Equipment truck", "3681", [r"luton|box truck|3\.5t|cube truck|rigid"], ("day",), "shoot_days", "A"),
    ("Location fees: interiors", "3412", [r"private residential|residential location|residential"], ("day", "shoot day"), "loc_int", "A"),
    ("Location fees: exteriors and permits", "3412", [r"city filming permit|public highway|public street|authority permit"], ("day", "shoot day"), "loc_ext", "A"),
    ("Unit base / parking", "3412", [r"unit base|basecamp|parking / basecamp"], ("day",), "shoot_days", "A"),
    ("Set medic", "2913", [r"medic"], ("day",), "shoot_days", "A"),
    ("Catering", "3410", [r"breakfast and lunch|full shooting-day catering"], ("person/day",), "catering", "A"),
    ("Craft service", "3410", [r"craft"], ("person/day",), "catering", "A"),
    ("Production office", "3712", [r"small production office|production office suite|office suite – small|small unit"], ("week", "day"), "total_weeks", "A"),
    ("Offline edit suite", "5020", [r"offline edit"], ("week", "day"), "edit_weeks", "edit"),
    ("Sound edit room", "5201", [r"sound edit room"], ("week", "day"), 5, "edit"),
    ("Mix stage", "5201", [r"mix stage"], ("day",), 5, "edit"),
    ("Grade suite", "5601", [r"grade"], ("day",), 10, "grade"),
    ("Mastering / QC / DCP", "5780", [r"mastering|dcp|\bqc\b"], ("project", "deliverable"), 1, "A"),
    ("Errors & omissions policy", "7202", [r"errors"], ("policy",), 1, "A"),
]
EXTRA_HEADS = 5                              # director, producers, office on set each day (planning assumption)


# ------------------------------------------------------------------------------------------------ helpers
def _f(v):
    try:
        return None if v in (None, "") else float(v)
    except (TypeError, ValueError):
        return None


def jurisdictions() -> list[dict]:
    rows = refdata.rows("SELECT jurisdiction, local_currency FROM rate_jurisdictions ORDER BY jurisdiction")
    regions = refdata.rows("SELECT jurisdiction, region_production_hub FROM rate_regional_factors ORDER BY CAST(source_row AS INTEGER)")
    return [{"jurisdiction": r["jurisdiction"], "currency": r["local_currency"],
             "regions": [x["region_production_hub"] for x in regions if x["jurisdiction"] == r["jurisdiction"]]} for r in rows]


def labour_rules(jurisdiction: str) -> list[dict]:
    return refdata.rows("""SELECT topic, rule_planning_reference AS rule, budget_treatment AS treatment FROM rate_labour_rules
        WHERE jurisdiction = ? AND (topic LIKE '%insurance%' OR topic LIKE '%holiday%' OR topic LIKE '%pension%' OR topic LIKE '%fringe%'
        OR topic LIKE '%payroll%' OR topic LIKE '%social%' OR topic LIKE '%levy%' OR topic LIKE '%tax%' OR topic LIKE '%contribution%')
        ORDER BY CAST(source_row AS INTEGER)""", jurisdiction)


def _factors(jurisdiction: str, region: str | None) -> dict:
    rows = refdata.rows("SELECT * FROM rate_regional_factors WHERE jurisdiction = ? ORDER BY CAST(source_row AS INTEGER)", jurisdiction)
    row = next((r for r in rows if r["region_production_hub"] == region), rows[0] if rows else None)
    keys = ("labour", "accommodation", "locations", "equipment", "transport", "catering")
    out = {k: (_f(row[k]) or 1.0) if row else 1.0 for k in keys}
    out["region"] = row["region_production_hub"] if row else ""
    return out


def _eighths(e: int) -> str:
    whole, part = divmod(int(e), 8)
    return f"{whole} {part}/8" if whole and part else f"{whole}" if whole else f"{part}/8"


# ------------------------------------------------------------------------------------------------ schedule
def site(scene: dict) -> str:
    """Where the unit is: 'JOHN'S HOUSE - KITCHEN' and 'JOHN'S HOUSE - HALL' are one site (moving between sets there is
    not a company move); the time of day is already split off by the script reader."""
    loc = (scene.get("location") or scene.get("heading") or "UNKNOWN").upper()
    return re.split(r"\s+[-–—/]\s+|\s*,\s*|\s*\(", loc, maxsplit=1)[0].strip() or loc


def _night(tod: str) -> bool:
    t = (tod or "").upper()
    return any(w in t for w in ("NIGHT", "EVENING", "DUSK"))


def scene_eighths(breakdown: dict) -> list[int]:
    """Each scene's length in eighths of a page, from its share of the script's lines and the page count."""
    scenes = breakdown.get("scenes") or []
    total = sum(max(1, s.get("lines") or 0) for s in scenes) or 1
    pages = breakdown.get("pages") or max(1, math.ceil(total / 56))
    return [max(1, round(max(1, s.get("lines") or 0) / total * pages * 8)) for s in scenes]


def stripboard(breakdown: dict, pages_per_day: float) -> list[dict]:
    """Day scenes, then night scenes, each in site and set order, packed into shooting days of pages_per_day pages.
    A day never mixes day and night work (turnaround). A scene that runs past the end of a day carries on the next day,
    as a 1st AD splits scenes to fill days, so the day count follows the pace. The company moves this implies are
    counted and warned about (see build); they are what a real schedule would trade days against."""
    scenes = breakdown.get("scenes") or []
    lens = scene_eighths(breakdown)
    cap = max(1, round(pages_per_day * 8))
    # day work first, then night work; within each, by site and set, so a day's second site is a true company move
    order = sorted(range(len(scenes)), key=lambda i: (_night(scenes[i].get("time_of_day")),
                                                      site(scenes[i]), (scenes[i].get("location") or "").upper(),
                                                      scenes[i].get("int_ext") or "", i))
    days, cur = [], None
    for i in order:
        s, e = scenes[i], lens[i]
        night = _night(s.get("time_of_day"))
        loc = site(s)
        while e > 0:
            if cur is None or cur["night"] != night or cur["eighths"] >= cap:
                cur = {"night": night, "eighths": 0, "scenes": [], "sites": OrderedDict(), "locations": OrderedDict(), "cast": OrderedDict()}
                days.append(cur)
            take = min(e, cap - cur["eighths"])
            cur["eighths"] += take
            e -= take
            if not cur["scenes"] or cur["scenes"][-1] != s.get("number", i + 1):
                cur["scenes"].append(s.get("number", i + 1))
            cur["sites"].setdefault(loc, set()).add(s.get("int_ext") or "")
            cur["locations"][(s.get("location") or s.get("heading") or "UNKNOWN").upper()] = True
            for ch in s.get("characters") or []:
                cur["cast"][ch] = True
    out = []
    for n, d in enumerate(days, 1):
        ie = [" ".join(sorted(v)) for v in d["sites"].values()]
        out.append({"day": n, "scenes": d["scenes"], "eighths": d["eighths"], "pages": _eighths(d["eighths"]),
                    "night": d["night"], "sites": list(d["sites"]), "locations": list(d["locations"]), "moves": max(0, len(d["sites"]) - 1),
                    "int_locations": sum(1 for x in ie if "EXT" not in x),
                    "ext_locations": sum(1 for x in ie if "EXT" in x), "cast": list(d["cast"])})
    return out


def day_out_of_days(breakdown: dict, board: list[dict]) -> list[dict]:
    cast = [c["name"] for c in breakdown.get("cast") or []]
    out = []
    for name in cast:
        days = [d["day"] for d in board if name in d["cast"]]
        if not days:
            continue
        span = days[-1] - days[0] + 1
        out.append({"name": name, "work_days": len(days), "first": days[0], "last": days[-1], "hold_days": span - len(days),
                    "days": days, "dialogue_blocks": next((c["dialogue_blocks"] for c in breakdown["cast"] if c["name"] == name), 0)})
    return out


# ------------------------------------------------------------------------------------------------ rates
class Card:
    """Jon's rate card for one jurisdiction: crew by role, non-labour by item, cast."""

    def __init__(self, jurisdiction: str):
        self.j = jurisdiction
        self.crew = refdata.rows("""SELECT * FROM rate_crew WHERE jurisdiction = ? ORDER BY
            CASE WHEN production_type LIKE 'Feature%' THEN 0 ELSE 1 END, CAST(source_row AS INTEGER)""", jurisdiction)
        self.items = refdata.rows("SELECT * FROM rate_non_labour WHERE jurisdiction = ? ORDER BY CAST(source_row AS INTEGER)", jurisdiction)
        self.cast = refdata.rows("SELECT * FROM rate_cast WHERE jurisdiction = ? ORDER BY CAST(source_row AS INTEGER)", jurisdiction)
        cur = refdata.rows("SELECT local_currency FROM rate_jurisdictions WHERE jurisdiction = ?", jurisdiction)
        self.currency = cur[0]["local_currency"] if cur else ""

    def role(self, names: list[str]) -> dict | None:
        for n in names:
            for r in self.crew:
                if r["english_budget_role"] == n:
                    return r
        return None

    def week(self, r: dict, tier: int, scenario: str) -> tuple[float | None, str]:
        """Weekly rate for a role, and its basis. None means negotiated or not priced."""
        tiers = [_f(r[f"tier_{i}_week"]) for i in range(1, 5)]
        if any(tiers):
            for t in [tier] + [x for x in (tier - 1, tier - 2, tier - 3, tier + 1, tier + 2) if 1 <= x <= 4]:
                if tiers[t - 1]:
                    return tiers[t - 1], f"tier {t} week" + ("" if t == tier else f" (tier {tier} not on the card)")
            return None, "negotiated"
        band = {"lean": "market_low_day", "base": "market_base_day", "conservative": "market_high_day"}[scenario]
        day = _f(r[band]) or _f(r["market_base_day"]) or _f(r["official_day"])
        if day:
            return day * WEEK, band.replace("_", " ").replace("day", "day × 5")
        wk = _f(r["official_week"])
        return (wk, "official week") if wk else (None, "negotiated")

    def item(self, patterns: list[str], units: tuple) -> dict | None:
        for p in patterns:
            rx = re.compile(p, re.I)
            for r in self.items:
                if rx.search(f"{r['category']} {r['item']}") and (r["unit"] or "").lower() in units:
                    return r
        return None

    def pct(self, pattern: str) -> dict | None:
        rx = re.compile(pattern, re.I)
        return next((r for r in self.items if rx.search(r["item"] or "") and "%" in (r["unit"] or "")), None)

    def day_player(self) -> dict | None:
        return next((r for r in self.cast if re.search(r"day player", r["english_role"] or "", re.I) and (r["unit"] or "") == "day"
                     and r["currency"] == self.currency), None)

    def background(self) -> dict | None:
        for p in (r"standard day", r"extra – feature|extra - feature|background|supporting artist"):
            r = next((x for x in self.cast if re.search(p, x["english_role"] or "", re.I) and re.search(r"supporting artist|extra|background", f"{x['category']} {x['english_role']}", re.I)), None)
            if r:
                return r
        return None


def _band(r: dict, scenario: str, lo="low", base="base", hi="high") -> float | None:
    key = {"lean": lo, "base": base, "conservative": hi}[scenario]
    return _f(r.get(key)) or _f(r.get(base))


# ------------------------------------------------------------------------------------------------ budget
COA = None


def _coa() -> dict:
    global COA
    if COA is None:
        COA = {r["account_code"]: r for r in refdata.rows("SELECT * FROM coa_accounts WHERE record_type = 'Account'")}
        COA.update({"7900": {"phase": "Charges", "category_code": "7900", "category_name": "COMPLETION BOND", "account_name": "COMPLETION BOND"},
                    "7901": {"phase": "Charges", "category_code": "7901", "category_name": "CONTINGENCY", "account_name": "CONTINGENCY"},
                    "7999": {"phase": "Charges", "category_code": "7999", "category_name": "FRINGES", "account_name": "FRINGES ON CREW PAYROLL"}})
    return COA


def _line(code: str, desc: str, amount: float | None, *, status: str, qty=None, unit="", rate=None, basis="", source="", note="",
          payroll=False) -> dict:
    a = _coa().get(code, {})
    return {"account": code, "account_name": a.get("account_name", ""), "category": a.get("category_code", code[:2] + "00"),
            "category_name": a.get("category_name", ""), "phase": a.get("phase", "Other"), "description": desc,
            "qty": qty, "unit": unit, "rate": rate, "amount": None if amount is None else round(amount, 2), "status": status,
            "basis": basis, "source": source, "note": note, "payroll": payroll}


def _prep_days(rule: tuple, shoot_days: int) -> float:
    kind, v = rule
    return v * shoot_days if kind == "per_day" else v


def build(breakdown: dict, *, jurisdiction: str = "United Kingdom", region: str | None = None, tier: int = 2,
          pages_per_day: dict | None = None, inputs: dict | None = None, elements: dict | None = None) -> dict:
    """Schedule, day-out-of-days and a lean/base/conservative budget for one script. elements: the script's element
    tagging (elements.tag), when it has been done; it adds the lines stunts, effects, vehicles and the rest drive."""
    inputs = inputs or {}
    tags = {s["scene"]: s for s in (elements or {}).get("scenes") or [] if s.get("tagged")}
    ppd = {s: float((pages_per_day or {}).get(s) or PAGES_PER_DAY[s]) for s in SCENARIOS}
    tier = min(4, max(1, int(tier or 2)))
    card = Card(jurisdiction)
    fac = _factors(jurisdiction, region)
    boards = {s: stripboard(breakdown, ppd[s]) for s in SCENARIOS}
    dood = day_out_of_days(breakdown, boards["base"])
    out = {"jurisdiction": jurisdiction, "region": fac["region"], "currency": card.currency, "tier": tier, "pages_per_day": ppd,
           "pages": breakdown.get("pages"), "scene_count": breakdown.get("scene_count"),
           "schedule": {s: {"shoot_days": len(boards[s]), "moves": sum(d["moves"] for d in boards[s]),
                            "night_days": sum(1 for d in boards[s] if d["night"])} for s in SCENARIOS},
           "stripboard": boards["base"], "dood": dood, "budget": {}, "warnings": [], "assumptions": [], "sources": SOURCES,
           "labour_rules": labour_rules(jurisdiction)}
    if not breakdown.get("scenes"):
        out["warnings"].append("The script has no scenes to schedule. Read it again, or check it isn't a scanned PDF.")
    busy = [d for d in boards["base"] if d["moves"] >= 2]
    if busy:
        sites = len({site(s) for s in breakdown["scenes"]})
        pages = breakdown.get("pages") or 0
        out["warnings"].append(
            f"Location-heavy: {sites} sites in {pages} page{'' if pages == 1 else 's'}, so {len(busy)} of {len(boards['base'])} base-case days "
            f"have two or more company moves (about {MOVE_HOURS} hours each). Expect more days than the pace gives, or plan to "
            "combine or cheat locations; the conservative case allows for some of this.")
    for s in SCENARIOS:
        out["budget"][s] = _budget(breakdown, boards[s], dood if s == "base" else day_out_of_days(breakdown, boards[s]),
                                   card, fac, tier, s, inputs, tags)
    out["assumptions"] = _assumptions(ppd, tier, card, fac, inputs)
    if tags:
        out["elements"] = {"tagged": len(tags), "scenes": breakdown.get("scene_count"), "made": (elements.get("made_with") or {}).get("model", ""),
                           "date": elements.get("date", "")}
        out["assumptions"].append(
            f"Element lines (stunts, effects, vehicles, weapons, animals, special make-up, child performers, intimacy, special equipment) "
            f"come from the AI element tagging of {len(tags)} scenes: each counts the shooting days in this case's stripboard on which "
            "the element works. Background artists and VFX shots use the tagging only where no producer figure is entered. "
            "Check the tags on the Elements sheet before relying on them.")
    return out


def _budget(breakdown: dict, board: list[dict], dood: list[dict], card: Card, fac: dict, tier: int, scenario: str, inputs: dict,
            tags: dict | None = None) -> dict:
    lines: list[dict] = []
    tags = tags or {}
    days = len(board)
    shoot_weeks = days / WEEK
    fees = inputs.get("fees") or {}
    # ---- above the line: producer inputs
    for code, key, label in (("1101", "script", "Script and rights"), ("1201", "producers", "Producers"),
                             ("1301", "director", "Director"), ("1420", "casting", "Casting director")):
        v = _f(fees.get(key))
        lines.append(_line(code, label, v, status="input" if v is not None else "unknown", basis="producer input",
                           note="" if v is not None else "Enter the agreed or proposed fee."))
    # ---- cast: day-out-of-days x fee
    cast_in = inputs.get("cast") or {}
    dp = card.day_player()
    threshold = int(inputs.get("day_player_max_days") or 3)
    for c in dood:
        fee = cast_in.get(c["name"]) or {}
        amt, basis = _f(fee.get("amount")), fee.get("basis") or "flat"
        if amt is not None:
            total = amt * (c["work_days"] if basis == "day" else math.ceil(c["work_days"] / WEEK) if basis == "week" else 1)
            lines.append(_line("1401", c["name"], total, status="input", qty=c["work_days"], unit="days worked",
                               rate=amt, basis=f"producer input ({basis})"))
        elif dp and c["work_days"] <= threshold:
            rate = _band(dp, scenario, "planning_low", "planning_base", "planning_high")
            lines.append(_line("1401", c["name"], rate * c["work_days"] if rate else None, status="benchmark" if rate else "unknown",
                               qty=c["work_days"], unit="day", rate=rate, basis=f"day player, rate card ({dp['english_role']})",
                               source=dp.get("source_file") or ""))
        else:
            lines.append(_line("1401", c["name"], None, status="unknown", qty=c["work_days"], unit="days worked",
                               note="Enter the fee (flat, per day or per week)."))
    bg = _f(inputs.get("background_per_day"))
    bg_days = sum(max([(tags.get(n) or {}).get("background") or 0 for n in d["scenes"]] or [0]) for d in board) if tags else 0
    if bg is None and bg_days:                            # from the element tagging: each day's largest crowd
        bg = bg_days / max(1, days)
    if bg:
        r = card.background()
        rate = (_band(r, scenario, "planning_low", "planning_base", "planning_high") or _f(r.get("published_minimum"))) if r else None
        mult = 10 if r and (r.get("unit") or "").lower() == "hour" else 1
        tagged = inputs.get("background_per_day") in (None, "")
        lines.append(_line("2102", "Background artists (from the script read)" if tagged else f"Background artists ({bg:.0f} a day)",
                           rate * mult * bg * days if rate else None,
                           status="benchmark" if rate else "unknown", qty=round(bg * days, 2), unit="person-days", rate=rate * mult if rate else None,
                           basis=f"rate card: {r['english_role']}" if r else "", payroll=True,
                           note="each shooting day's largest crowd in the element tagging; enter a figure a day to replace it" if tagged else ""))
    elif bg == 0:                                         # the producer says none (before 1.0.8 this stayed Unknown)
        lines.append(_line("2102", "Background artists (none)", 0.0, status="input", basis="producer input"))
    else:
        lines.append(_line("2102", "Background artists", None, status="unknown", note="Enter how many a day (0 if none)."))
    # ---- crew
    crew_in = {c.get("key"): c for c in inputs.get("crew") or []}
    heads, max_prep, max_wrap = 0, 0.0, 0.0
    for key, names, count, code, prep_rule, wrap, src in CREW:
        o = crew_in.get(key) or {}
        if o.get("include") is False:
            continue
        n = int(o.get("count") if o.get("count") not in (None, "") else count)
        if n <= 0:
            continue
        prep = _f(o.get("prep_days")) if o.get("prep_days") not in (None, "") else _prep_days(prep_rule, days)
        wrp = _f(o.get("wrap_days")) if o.get("wrap_days") not in (None, "") else wrap
        weeks = (prep + days + wrp) / WEEK
        heads += n
        max_prep, max_wrap = max(max_prep, prep), max(max_wrap, wrp)
        fee = _f(o.get("weekly"))
        r = card.role(names)
        if fee is not None:
            rate, basis, status = fee, "producer input (week)", "input"
        elif r:
            rate, basis = card.week(r, tier, scenario)
            status = "benchmark" if rate else "unknown"
        else:
            rate, basis, status = None, f"not on the Saracen Bridge {card.j} card", "unknown"
        rate = rate * fac["labour"] if rate and status == "benchmark" else rate
        lines.append(_line(code, f"{key}{f' × {n}' if n > 1 else ''}", rate * weeks * n if rate else None, status=status,
                           qty=round(weeks * n, 2), unit="weeks", rate=round(rate, 2) if rate else None, basis=basis,
                           source=(r or {}).get("source_file", "") if status == "benchmark" else "",
                           note=f"prep {prep:g} + shoot {days} + wrap {wrp:g} days" + ("" if status != "unknown" else
                                "; negotiated: enter the weekly fee" if r else "; no rate: enter the weekly fee"), payroll=True))
    # ---- post labour
    edit_weeks = shoot_weeks + EDIT_WEEKS_AFTER_WRAP
    for key, names, count, code, wk, src in POST_CREW:
        weeks = edit_weeks if wk == "edit" else wk
        r = card.role(names)
        rate, basis = card.week(r, tier, scenario) if r else (None, f"not on the Saracen Bridge {card.j} card")
        lines.append(_line(code, key, rate * fac["labour"] * weeks * count if rate else None, status="benchmark" if rate else "unknown",
                           qty=round(weeks, 2), unit="weeks", rate=round(rate * fac["labour"], 2) if rate else None, basis=basis,
                           source=(r or {}).get("source_file", "") if rate else "", payroll=True,
                           note=f"{SOURCES[src].split(':')[0]}" if rate else "negotiated or not on the card: enter the fee"))
    # ---- non-labour
    cast_per_day = sum(len(d["cast"]) for d in board) / max(1, days)
    persons = heads + cast_per_day + (bg or 0) + EXTRA_HEADS
    qty_of = {"shoot_days": days, "loc_int": sum(d["int_locations"] for d in board), "loc_ext": sum(d["ext_locations"] for d in board),
              "total_weeks": (max_prep + days + max_wrap) / WEEK, "edit_weeks": edit_weeks, "catering": persons * days}
    for key, code, pats, units, q, src in NON_LABOUR:
        r = card.item(pats, units)
        if key == "Lens package" and (not r or "lens" in (card.item(NON_LABOUR[0][2], ("day",)) or {}).get("item", "").lower()):
            continue                                      # the camera package already includes lenses
        if key == "Grip package" and "grip" in (card.item(NON_LABOUR[3][2], ("day",)) or {}).get("item", "").lower():
            continue                                      # lighting and grip priced as one package
        if key == "Catering" and not r:
            parts = [card.item([p], ("person",)) for p in (r"breakfast", r"hot (lunch|meal)")]
            if all(parts):
                rate = sum(_band(p, scenario) for p in parts)
                lines.append(_line(code, key, rate * fac["catering"] * qty_of["catering"], status="benchmark", qty=round(qty_of["catering"]),
                                   unit="person-days", rate=round(rate * fac["catering"], 2), basis="breakfast + hot lunch, rate card",
                                   source=parts[0]["source_file"], note=f"{heads} crew + {cast_per_day:.1f} cast + {int(bg or 0)} background + {EXTRA_HEADS} others a day"))
                continue
        if q == "walkies":
            qty = 20 * (days if r and "day" in (r["unit"] or "") else math.ceil(days / WEEK))
        elif isinstance(q, str):
            qty = qty_of[q]
        else:
            qty = q * (days if key.startswith("Crew vans") else 1)
        if not r:
            lines.append(_line(code, key, None, status="unknown", qty=round(qty, 2), note=f"not on the Saracen Bridge {card.j} card: quote"))
            continue
        if units[0] == "week" and (r["unit"] or "").lower() in ("day", "shoot day"):
            qty *= WEEK
        elif units[0] == "day" and (r["unit"] or "").lower() == "week":
            qty /= WEEK
        rate = _band(r, scenario)
        f = fac.get((r["regional_factor_type"] or "").lower(), 1.0) if r["regional_factor_type"] not in (None, "None") else 1.0
        lines.append(_line(code, key, rate * f * qty if rate else None, status="benchmark" if rate else "unknown", qty=round(qty, 2),
                           unit=r["unit"], rate=round(rate * f, 2) if rate else None, basis=f"rate card: {r['item']}",
                           source=r["source_file"] or "", note=SOURCES[src].split(":")[0] if src != "A" else ""))
    # ---- VFX, music, travel, legal: producer inputs
    vfx = inputs.get("vfx_shots")
    if vfx in (None, "") and tags:
        est = sum((t.get("vfx_shots") or 0) for t in tags.values())
        vfx = est if est or not any(t.get("vfx") for t in tags.values()) else None
    if vfx in (None, ""):
        lines.append(_line("4641", "VFX shots", None, status="unknown", note="Enter the shot count (0 if none)."))
    elif int(vfx) > 0:
        r = card.item([r"standard vfx|2d compositing|routine"], ("shot",))
        rate = _band(r, scenario) if r else None
        lines.append(_line("4641", f"VFX shots ({int(vfx)})", rate * int(vfx) if rate else None, status="benchmark" if rate else "unknown",
                           qty=int(vfx), unit="shot", rate=rate, basis=f"rate card: {r['item']}" if r else "", source=(r or {}).get("source_file", "")))
    lines += _element_lines(board, tags, card, fac, tier, scenario)
    for code, key, label in (("5101", "music", "Music: composer and licences"), ("3901", "travel", "Travel and accommodation"),
                             ("7005", "legal", "Legal, accounting and audit")):
        v = _f(fees.get(key))
        lines.append(_line(code, label, v, status="input" if v is not None else "unknown", basis="producer input",
                           note="" if v is not None else "Enter an allowance (0 if none)."))
    # ---- producer overrides: any line's amount, keyed "account|description"
    over = inputs.get("overrides") or {}
    for l in lines:
        v = _f(over.get(f"{l['account']}|{l['description']}"))
        if v is not None:
            l.update(amount=round(v, 2), status="input", basis="producer input", note="")
    # ---- charges
    payroll = sum(l["amount"] or 0 for l in lines if l["payroll"] and l["amount"])
    fr = _f(inputs.get("fringe_pct"))
    lines.append(_line("7999", "Fringes on crew payroll", payroll * fr / 100 if fr is not None else None,
                       status="input" if fr is not None else "unknown", qty=round(payroll, 2), unit="payroll", rate=fr,
                       basis=f"{fr:g}% producer input" if fr is not None else "",
                       note="" if fr is not None else "Enter the payroll load % (employer taxes, holiday, pension) for this jurisdiction."))
    known_direct = sum(l["amount"] or 0 for l in lines if l["phase"] in ("Above the Line", "Production", "Post Production", "Other") or l["account"] == "7999")
    ins = card.pct(r"production (package|insurance)|insurance package")
    if ins:
        rate = _band(ins, scenario)
        lines.append(_line("7201", "Production insurance package", known_direct * rate, status="benchmark", qty=round(known_direct, 2),
                           unit="% of known direct cost", rate=rate, basis=f"rate card: {ins['item']}", source=ins["source_file"] or ""))
    else:
        lines.append(_line("7201", "Production insurance package", None, status="unknown", note=f"not on the Saracen Bridge {card.j} card: quote"))
    base = sum(l["amount"] or 0 for l in lines if l["phase"] in ("Above the Line", "Production", "Post Production", "Other") or l["account"] == "7999")
    bond = card.pct(r"completion bond")
    if bond:
        rate = _band(bond, scenario)
        lines.append(_line("7900", "Completion bond fee", base * rate, status="benchmark", qty=round(base, 2), unit="% of direct cost",
                           rate=rate, basis=f"rate card: {bond['item']}", source=bond["source_file"] or ""))
    lines.append(_line("7901", "Contingency (10%)", base * CONTINGENCY, status="benchmark", qty=round(base, 2), unit="% of direct cost",
                       rate=CONTINGENCY, basis="10% of direct cost", note=SOURCES["contingency"].split(":")[0]))
    # ---- totals
    phases = OrderedDict((p, {"known": 0.0, "unknown": 0}) for p in ("Above the Line", "Production", "Post Production", "Other", "Charges"))
    cats: dict = OrderedDict()
    for l in sorted(lines, key=lambda x: (x["account"], x["description"])):
        ph = phases.setdefault(l["phase"], {"known": 0.0, "unknown": 0})
        c = cats.setdefault(l["category"], {"category": l["category"], "name": l["category_name"], "phase": l["phase"], "known": 0.0, "unknown": 0})
        if l["amount"] is None:
            ph["unknown"] += 1
            c["unknown"] += 1
        else:
            ph["known"] += l["amount"]
            c["known"] += l["amount"]
    unknown = [l for l in lines if l["amount"] is None]
    total = sum(p["known"] for p in phases.values())
    return {"shoot_days": days, "lines": lines, "phases": phases, "categories": list(cats.values()), "known_total": round(total, 2),
            "unknown_lines": len(unknown), "status": "PRELIMINARY" if unknown else "COMPLETE (rate-card)",
            "headcount": heads, "edit_weeks": round(edit_weeks, 2)}


# ------------------------------------------------------------------------------------------------ elements (1.0.8)
# (element, account, description, crew roles on Jon's card (day rate = week / 5), non-labour item patterns, quantity)
# quantity: "days" (shooting days the element works), "performer_days" (each day's most stunt performers),
# "item_days" (each day's distinct items). No role or item on the card: an Unknown line with its quantity, to quote.
EQUIPMENT = [
    ("drone", r"drone|aerial|helicopter", "2606", "Drone / aerial unit", [r"drone"]),
    ("crane", r"crane|jib", "2991", "Crane", [r"technocrane|telescopic crane", r"crane / jib|jib / small crane"]),
    ("steadicam", r"steadicam|gimbal", "3112", "Steadicam", [r"steadicam"]),
    ("camera car", r"camera car|tracking vehicle|low.?loader|process trailer", "2603", "Camera car / tracking vehicle", [r"camera car|tracking"]),
    ("boat", r"boat|marine|underwater|water", "2605", "Safety / camera boat", [r"safety / camera boat|support vessel|workboat"]),
]
ELEMENT_LINES = [
    ("stunts", "1410", "Stunt coordinator", ["Stunt Coordinator"], None, "days"),
    ("stunt_performers", "1411", "Stunt performers", ["Stunt Performer"], None, "performer_days"),
    ("sfx", "3301", "Special effects supervisor", ["Special Effects Supervisor"], None, "days"),
    ("sfx", "3303", "Special effects technician", ["Senior SFX Technician", "SFX Technician"], None, "days"),
    ("vehicles", "2602", "Picture vehicles", [], None, "item_days"),
    ("vehicles", "2608", "Picture vehicle mechanic", ["Picture Vehicle Mechanic"], None, "days"),
    ("weapons", "2505", "Armourer / firearms specialist", [], None, "days"),
    ("animals", "2622", "Animal trainer / wrangler", [], None, "days"),
    ("animals", "2623", "Animals", [], None, "item_days"),
    ("makeup", "2803", "Special make-up / prosthetics artist", ["Prosthetics Artist"], None, "days"),
    ("minors", "1413", "Chaperone and tutor for child performers", [], None, "days"),
    ("intimacy", "2914", "Intimacy coordinator", [], None, "days"),
]


def _element_lines(board: list[dict], tags: dict, card: Card, fac: dict, tier: int, scenario: str) -> list[dict]:
    if not tags:
        return []
    out = []

    def days_with(test) -> list[dict]:
        return [d for d in board if any(test(tags.get(n) or {}) for n in d["scenes"])]

    def scenes_with(test) -> list[int]:
        return sorted(n for n, t in tags.items() if test(t))

    def add(code, desc, qty, unit, roles, patterns, why):
        rate, basis, src = None, "", ""
        r = card.role(roles) if roles else None
        if r:
            wk, b = card.week(r, tier, scenario)
            if wk:
                rate, basis, src = wk / WEEK * fac["labour"], f"rate card: {r['english_budget_role']} ({b} ÷ 5)", r.get("source_file") or ""
        if rate is None and roles in (["Stunt Performer"], ["Stunt Coordinator"]):      # some cards price stunts as cast
            rx = r"stunt (performer|actor)" if roles == ["Stunt Performer"] else r"stunt co-?ordinator$"
            c = next((x for x in card.cast if re.search(rx, x["english_role"] or "", re.I) and (x["unit"] or "") == "day"
                      and x["currency"] == card.currency), None)
            if c and _band(c, scenario, "planning_low", "planning_base", "planning_high"):
                rate, basis, src = _band(c, scenario, "planning_low", "planning_base", "planning_high"), f"rate card: {c['english_role']}", c.get("source_file") or ""
        if rate is None and patterns:
            it = card.item(patterns, ("day",))
            if it and _band(it, scenario):
                f = fac.get((it["regional_factor_type"] or "").lower(), 1.0) if it["regional_factor_type"] not in (None, "None") else 1.0
                rate, basis, src = _band(it, scenario) * f, f"rate card: {it['item']}", it.get("source_file") or ""
        l = _line(code, desc, rate * qty if rate is not None else None, status="benchmark" if rate is not None else "unknown",
                  qty=qty, unit=unit, rate=round(rate, 2) if rate is not None else None, basis=basis, source=src,
                  note=why + ("" if rate is not None else f"; negotiated on the Saracen Bridge {card.j} card: enter the fee" if r
                              else f"; not on the Saracen Bridge {card.j} card: quote"), payroll=bool(roles) and rate is not None and not patterns)
        l["driver"] = "elements"
        out.append(l)

    for key, code, desc, roles, patterns, kind in ELEMENT_LINES:
        test = (lambda t, k=key: bool(t.get(k)))
        hit = days_with(test)
        if not hit:
            continue
        sc = scenes_with(test)
        why = f"from the script read: {len(hit)} shooting day(s), scenes {', '.join(map(str, sc[:10]))}{' …' if len(sc) > 10 else ''}"
        if kind == "days":
            add(code, desc, len(hit), "days", roles, patterns, why)
        elif kind == "performer_days":
            qty = sum(max((tags.get(n) or {}).get("stunt_performers") or 0 for n in d["scenes"]) for d in hit)
            if qty:
                add(code, desc, qty, "performer-days", roles, patterns, why)
        else:
            qty = sum(len({x.lower() for n in d["scenes"] for x in (tags.get(n) or {}).get(key) or []}) for d in hit)
            add(code, desc, qty, f"{'vehicle' if key == 'vehicles' else 'animal'}-days", roles, patterns, why)
    for name, rx, code, desc, patterns in EQUIPMENT:
        pat = re.compile(rx, re.I)
        test = (lambda t, p=pat: any(p.search(x) for x in t.get("special_equipment") or []))
        hit = days_with(test)
        if hit:
            sc = scenes_with(test)
            add(code, desc, len(hit), "days", [], patterns, f"from the script read: {len(hit)} shooting day(s), scenes {', '.join(map(str, sc[:10]))}")
    return out


def _assumptions(ppd: dict, tier: int, card: Card, fac: dict, inputs: dict) -> list[str]:
    a = [f"Shooting pace {ppd['lean']:g} / {ppd['base']:g} / {ppd['conservative']:g} pages a day (lean / base / conservative). "
         f"Source: {SOURCES['pace']}.",
         "Shooting days follow the pace: day scenes then night scenes, grouped by site (sets at one site are not a company "
         "move), never mixing day and night work in one day, splitting a scene across days where it runs over. Company "
         f"moves are counted and flagged; each costs about {MOVE_HOURS} hours ({SOURCES['moves']}).",
         "Scene length is its share of the script's lines times the page count, in eighths.",
         f"Crew rates: the Saracen Bridge {card.j} 2026 rate card, " + (f"experience tier {tier}" if any(_f(r["tier_1_week"]) for r in card.crew)
                                                         else "market low / base / high day rates × 5 by case") +
         f", × the {fac['region'] or 'default'} labour factor {fac['labour']:g}. Negotiated roles stay Unknown until a fee is entered.",
         f"Crew plan, prep and wrap: {SOURCES['crew']}. Counts and the roles marked as planning assumptions are editable.",
         f"Post: editor and assistant for the shoot plus {EDIT_WEEKS_AFTER_WRAP} weeks. Source: {SOURCES['edit']}. Grade 10 days: {SOURCES['grade']}.",
         "Non-labour: the Saracen Bridge rate card low / base / high by case, × the region's factor for that cost type.",
         f"Contingency 10% of direct cost; completion bond and insurance at the card's rates. Source: {SOURCES['contingency']}.",
         f"Catering headcount: crew plan + cast called that day + background + {EXTRA_HEADS} others (director, producers, office).",
         "Incentives are not netted off here: take the qualifying spend to Location & Incentives.",
         "Script-only analysis is never production-grade (Saracen Bridge instructions): confirm with a line producer, production accountant and payroll company."]
    return a


# ------------------------------------------------------------------------------------------------ workbook
def workbook(title: str, res: dict, elements: dict | None = None) -> bytes:
    """The schedule and budget as an Excel workbook: top sheet (formulas over the detail), detail in all three cases,
    stripboard, day-out-of-days, assumptions and sources. Unknown lines are left blank and marked Unknown."""
    import io
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    cur = res.get("currency") or ""
    money = '#,##0;(#,##0);"-"'
    head_font, bold = Font(name="Arial", bold=True, color="FFFFFF"), Font(name="Arial", bold=True)
    head_fill = PatternFill("solid", fgColor="1F2A44")
    plain = Font(name="Arial")
    wb = Workbook()

    def sheet(ws, headers, widths):
        ws.append(headers)
        for i, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = w
            c = ws.cell(row=ws.max_row, column=i)
            c.font, c.fill, c.alignment = head_font, head_fill, Alignment(vertical="center", wrap_text=True)
        ws.freeze_panes = f"A{ws.max_row + 1}"           # a string: a cell object would start the data a row lower

    # detail: one row per line, amounts for the three cases
    det = wb.active
    det.title = "Budget detail"
    sheet(det, ["Account", "Account name", "Category", "Category name", "Phase", "Description", "Qty (base)", "Unit", f"Rate (base, {cur})",
                f"Lean ({cur})", f"Base ({cur})", f"Conservative ({cur})", "Status", "Basis", "Note", "Source"],
          [9, 26, 9, 24, 14, 34, 11, 14, 14, 15, 15, 15, 12, 34, 40, 34])
    by = {s: {(l["account"], l["description"]): l for l in res["budget"][s]["lines"]} for s in SCENARIOS}
    keys = list(by["base"]) + [k for s in ("lean", "conservative") for k in by[s] if k not in by["base"]]
    seen = set()
    for k in keys:
        if k in seen:
            continue
        seen.add(k)
        l = by["base"].get(k) or by["lean"].get(k) or by["conservative"].get(k)
        amt = [by[s].get(k, {}).get("amount") for s in SCENARIOS]
        det.append([l["account"], l["account_name"], l["category"], l["category_name"], l["phase"], l["description"], l["qty"], l["unit"],
                    l["rate"], *amt, {"benchmark": "Rate card", "input": "Producer input", "unknown": "Unknown"}.get(l["status"], l["status"]),
                    l["basis"], l["note"], l["source"]])
    last = det.max_row
    for row in det.iter_rows(min_row=2, max_row=last):
        for c in row:
            c.font = plain
        for c in row[8:12]:
            c.number_format = money
    det.append([])
    det.append(["", "", "", "", "", "Total of priced lines", "", "", ""] +
               [f"=SUM({col}2:{col}{last})" for col in ("J", "K", "L")])
    for c in det[det.max_row]:
        c.font = bold
        c.number_format = money

    # top sheet: categories, SUMIFS over the detail
    top = wb.create_sheet("Top sheet", 0)
    top.append([f"{title}: preliminary schedule and budget"])
    top["A1"].font = Font(name="Arial", bold=True, size=14)
    b = res["budget"]
    meta = [("Jurisdiction", f"{res['jurisdiction']} · {res.get('region') or ''}"), ("Currency", cur),
            ("Crew experience tier", res.get("tier")), ("Shooting days (lean / base / conservative)",
             " / ".join(str(res["schedule"][s]["shoot_days"]) for s in SCENARIOS)),
            ("Pages a day (lean / base / conservative)", " / ".join(f"{res['pages_per_day'][s]:g}" for s in SCENARIOS)),
            ("Status", f"{b['base']['status']}: {b['base']['unknown_lines']} lines still to price"), ("Built", res.get("built", ""))]
    for k, v in meta:
        top.append([k, v])
        top.cell(row=top.max_row, column=1).font = bold
    top.append([])
    sheet(top, ["Category", "Name", "Phase", f"Lean ({cur})", f"Base ({cur})", f"Conservative ({cur})", "Unknown lines (base)"],
          [44, 34, 16, 18, 18, 18, 14])
    top.freeze_panes = None
    first = top.max_row + 1
    for c in b["base"]["categories"]:
        r = top.max_row + 1
        top.append([c["category"], c["name"], c["phase"]] +
                   [f"=SUMIFS('Budget detail'!{col}:{col},'Budget detail'!C:C,A{r})" for col in ("J", "K", "L")] + [c["unknown"]])
        for cell in top[r]:
            cell.font = plain
        for cell in top[r][3:6]:
            cell.number_format = money
    lastc = top.max_row
    top.append(["Total of priced lines", "", ""] + [f"=SUM({col}{first}:{col}{lastc})" for col in ("D", "E", "F")] + [f"=SUM(G{first}:G{lastc})"])
    for cell in top[top.max_row]:
        cell.font = bold
        cell.number_format = money
    top.append([])
    top.append(["Unknown lines are not zero: the budget is PRELIMINARY until each is priced (the Saracen Bridge chart of accounts, SB-COA-1.0)."])
    top.append(["Incentives are not netted off: take the qualifying spend to Location & Incentives."])

    # stripboard and day-out-of-days (base case)
    sb = wb.create_sheet("Stripboard (base)")
    sheet(sb, ["Day", "Day / night", "Pages", "Scenes", "Locations", "Company moves", "Cast"], [7, 11, 9, 24, 50, 10, 60])
    for d in res["stripboard"]:
        sb.append([d["day"], "Night" if d["night"] else "Day", d["pages"], ", ".join(map(str, d["scenes"])), "; ".join(d["locations"]),
                   d["moves"], ", ".join(d["cast"])])
    dd = wb.create_sheet("Day out of days")
    sheet(dd, ["Character", "Work days", "First day", "Last day", "Hold days", "Days"], [28, 10, 10, 10, 10, 60])
    for c in res["dood"]:
        dd.append([c["name"], c["work_days"], c["first"], c["last"], c["hold_days"], ", ".join(map(str, c["days"]))])
    asm = wb.create_sheet("Assumptions and sources")
    sheet(asm, ["Assumption or source"], [160])
    for a in res.get("assumptions", []):
        asm.append([a])
    asm.append([])
    for k, v in (res.get("sources") or {}).items():
        asm.append([f"{k}: {v}"])
    if res.get("labour_rules"):
        asm.append([])
        asm.append([f"Payroll rules on the Saracen Bridge {res['jurisdiction']} card (for the fringe %):"])
        for r in res["labour_rules"]:
            asm.append([f"{r['topic']}: {r['rule'] or ''} {r['treatment'] or ''}".strip()])
    sheets = [sb, dd, asm]
    if elements and elements.get("scenes"):              # 1.0.8: the element tagging the element lines come from
        from . import elements as el_mod
        el_ws = wb.create_sheet("Elements", 3)
        cols = [k for k in el_mod.FIELDS]
        sheet(el_ws, ["Scene", "Page", "Heading"] + [el_mod.FIELDS[k][0] for k in cols] + ["Notes"],
              [7, 6, 34] + [9 if el_mod.FIELDS[k][1] != "list" else 26 for k in cols] + [40])
        for sc in elements["scenes"]:
            el_ws.append([sc["scene"], f"~{sc['page']}" if sc.get("page_estimated") else sc["page"], sc["heading"]] +
                         [("; ".join(sc.get(k) or []) if el_mod.FIELDS[k][1] == "list" else ("Yes" if sc.get(k) else "")
                           if el_mod.FIELDS[k][1] == "flag" else (sc.get(k) or "")) for k in cols] + [sc.get("notes") or ("" if sc.get("tagged") else "not tagged")])
        sheets.append(el_ws)
    for ws in sheets:
        for row in ws.iter_rows(min_row=2):
            for c in row:
                c.font = plain
                if ws.title == "Elements":
                    c.alignment = Alignment(wrap_text=True, vertical="top")
    out = io.BytesIO()
    wb.save(out)
    return out.getvalue()
