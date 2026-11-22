"""Casting Director (1.1.6): casting suggestions for a broken-down script.

Tim, 27 Oct: "casting director: casting suggesting for a broken down script", in the main menu after Look Book
Analytics.

1. Roles come from the script's breakdown: every character who speaks, with the scenes they are in, their share of
   the script, their dialogue and the shooting days the base stripboard gives them. The size of part is read from
   that share and is the user's to change.
2. The local model reads each principal role where the script brings it in and says its gender, playing age and a
   one-line description. An age the script prints ("MARA (30s)") is taken from the text without the model. Every
   reading is shown for checking and can be corrected.
3. The shortlist comes only from the Saracen Bridge Actor Value Database: actors whose gender and playing-age band
   fit the role. Leads are ranked by composite cast value, other parts by supporting value; an actor whose genres
   include the film's comes first. Budget fit uses the database's own fields (minimum sensible budget, optimal budget
   floor). No name is invented and nobody is attached: a suggestion goes to the package as Wish list.
"""
from __future__ import annotations

import re

from . import budget, llm, refdata, script

SIZES = ("Lead", "Supporting", "Featured")
# "Any" (Rule 1, 27 Oct): a part open to any gender, or one the script doesn't fix, isn't filtered by gender; nor is a
# non-binary part, since the database records only two non-binary actors and casting such a part is the casting
# director's call. "Unknown" from before reads as "Any".
GENDERS = ("Female", "Male", "Non-binary", "Any")
CHILD_RULE = ("Child performer: needs a licence, a chaperone and tutoring, and the hours are limited by age (in England at the "
              "place of performance at most 5 hours under 5, 8 hours aged 5 to 8, 9.5 hours from 9: Children (Performances and "
              "Activities) (England) Regulations 2014, reg. 22). Plan shorter days.")
# the database's playing-age bands, as ages
BANDS = {"Under 18": (0, 17), "18–29": (18, 29), "30–49": (30, 49), "50–69": (50, 69), "70+": (70, 120)}
# Tim's genres to the database's (coarser) genre words: the closest it has. Documentary has none.
GENRE_WORDS = {
    "Action": {"Action", "Action Comedy"}, "Adventure": {"Adventure", "Family"}, "Comedy": {"Comedy", "Action Comedy"},
    "Crime": {"Thriller"}, "Drama": {"Drama", "Prestige Drama"}, "Thriller": {"Thriller"}, "Horror": {"Horror"},
    "Mystery": {"Thriller"}, "Science fiction": {"Science Fiction"}, "Fantasy": {"Fantasy"}, "Romance": {"Romance"},
    "Historical / Period": {"Period", "Prestige Drama"}, "War": {"Prestige Drama", "Action"}, "Western": {"Western"},
    "Musical": {"Musical"}, "Sports": {"Drama"}, "Biographical / Biopic": {"Biography", "Prestige Drama"}, "Documentary": set(),
}
SHORTLIST = 6
SCRIPT_READ_VERSION = 1         # the reading of the script's own wording (1.3.1); raise it to re-read saved scripts
READ_ROLES = 12                 # the principal roles the model reads (leads and supporting first)
INTRO_CHARS = 1400


# ------------------------------------------------------------------------------------------------ roles
def roles(breakdown: dict) -> list[dict]:
    """Every character with dialogue, largest part first: scenes, share of scenes, dialogue blocks, base-case days."""
    scenes = breakdown.get("scenes") or []
    n = len(scenes) or 1
    board = budget.stripboard(breakdown, budget.PAGES_PER_DAY["base"]) if scenes else []
    out = []
    for c in breakdown.get("cast") or []:
        name = c["name"]
        nums = [s.get("number", i + 1) for i, s in enumerate(scenes) if name in (s.get("characters") or [])]
        if not nums:
            continue
        out.append({"name": name, "scenes": len(nums), "share": round(len(nums) / n, 3), "dialogue": c.get("dialogue_blocks") or 0,
                    "first_scene": nums[0], "days": sum(1 for d in board if name in d["cast"])})
    out.sort(key=lambda r: (-r["scenes"], -r["dialogue"], r["name"]))
    for i, r in enumerate(out):
        r["size"] = size_of(r, i)
    return out


def size_of(role: dict, rank: int) -> str:
    """A reading of the size of part from the script alone: the two largest parts in a quarter or more of the scenes are
    leads (any part in 40% or more is too); a part in 8% or more of the scenes, or with 15 or more speeches, is
    supporting; the rest are featured."""
    if role["share"] >= 0.4 or (rank < 2 and role["share"] >= 0.25):
        return "Lead"
    if role["share"] >= 0.08 or role["dialogue"] >= 15:
        return "Supporting"
    return "Featured"


# ------------------------------------------------------------------------------------------------ what the script says
_WORDS = {"teens": (13, 19), "twenties": (20, 29), "thirties": (30, 39), "forties": (40, 49), "fifties": (50, 59),
          "sixties": (60, 69), "seventies": (70, 79), "eighties": (80, 89)}


_AGE_WORD = "|".join(_WORDS)
_STAGE = r"(?:early|mid|late|middle)?[\s-]*"
# what may sit between a name and its age: a surname or two, then a comma, bracket or dash
_AFTER_NAME = r"(?:\s+[A-Z][A-Z'’.-]+){0,2}\s*[,(–—-]\s*"
_TEEN_NAME = re.compile(r"\b(TEEN|TEENAGE|TEENAGED)\b")


def _span(t: str) -> tuple[int, int] | None:
    """An age range from a few words: "34", "30s", "late 40s", "mid-twenties", "teens", "16 years old"."""
    t = t.lower().replace("-", " ").replace("–", " ")
    m = re.fullmatch(r"\s*(\d{1,2})\s*(?:years?\s*old|yrs?|y/?o)?\s*", t)
    if m:
        a = int(m.group(1))
        return (a, a) if 1 <= a <= 100 else None
    span = None
    d = re.search(r"(?<!\d)(\d)0'?s\b", t)
    if d:
        span = (int(d.group(1)) * 10, int(d.group(1)) * 10 + 9)
    else:
        span = next((v for k, v in _WORDS.items() if k in t), None)
        if not span and re.search(r"\bteen(s|age|aged|ager)?\b", t):
            span = _WORDS["teens"]
    if not span:
        return None
    lo, hi = span
    if "early" in t:
        hi = lo + 3
    elif "mid" in t:                                     # "mid" and "middle"
        lo, hi = lo + 3, lo + 6
    elif "late" in t:
        lo = lo + 6
    return lo, hi


def age_from_text(text: str, name: str) -> tuple[int, int] | None:
    """An age the script prints where it brings the character in: "MARA (34)", "MARA OKAFOR (30s)", "MARA (late 40s)",
    "MARA (mid-twenties)", and (1.3.1) "MARA, 34," "MARA, early forties," "MARA - 16 years old", "MARA, a woman in her
    fifties". A part named TEENAGE MARA is in its teens."""
    up = re.escape(name.upper())
    m = re.search(rf"\b{up}\b(?:\s+[A-Z][A-Z'’.-]+){{0,2}},?\s*\(([^)\n]{{1,24}})\)", text)
    if m:
        got = _span(m.group(1))
        if got:
            return got
    m = re.search(rf"\b{up}\b{_AFTER_NAME}([^.\n]{{0,70}})", text)
    if m:
        t = m.group(1)
        # the age comes first after the name, or in "in his/her/their fifties", before any other name in capitals
        t = re.split(r"\b[A-Z][A-Z'’]{2,}\b", t)[0]
        for pat in (rf"^\s*(\d{{1,2}})\s*(?=[,.)–—-]|$)", rf"^\s*(\d{{1,2}})[\s-]*(?:years?[\s-]*old|yrs?|y/?o)\b",
                    rf"^\s*({_STAGE}(?:\d0'?s|{_AGE_WORD}|teens))\b",
                    rf"\bin (?:his|her|their) ({_STAGE}(?:\d0'?s|{_AGE_WORD}|teens))\b",
                    rf"\b(?:aged?|age of) (\d{{1,2}})\b", rf"\b(\d{{1,2}})[\s-]*(?:years?[\s-]*old|yrs?[\s-]*old|y/?o)\b"):
            g = re.search(pat, t, re.I)
            if g:
                got = _span(g.group(1))
                if got:
                    return got
    if _TEEN_NAME.search(name.upper()):
        return _WORDS["teens"]
    return None


# Gender from the script's own wording (1.3.1). Tim, 18 Nov: casting was "not picking up the gender and age from the
# original": until the AI had read the roles, every part showed "Open to any gender". The script nearly always says:
# in the part's name (MRS HALE, GIRLFRIEND), in the words it brings the character in with ("a nervous Scotsman", "a
# calm Scots woman"), or in the first he or she after the name. Anything else stays open, and every reading is the
# user's to correct.
_F_NAME = {"MRS", "MISS", "MS", "LADY", "QUEEN", "PRINCESS", "MADAM", "MADAME", "MUM", "MOM", "MUMMY", "MOMMY", "MOTHER", "GRANDMA", "GRANDMOTHER",
           "GRAN", "NAN", "NANA", "AUNT", "AUNTIE", "SISTER", "WIFE", "GIRLFRIEND", "GIRL", "WOMAN", "WAITRESS", "BARMAID", "ACTRESS",
           "HOSTESS", "NUN", "BRIDE", "WIDOW", "DAUGHTER", "SCHOOLGIRL", "POLICEWOMAN", "DUCHESS", "COUNTESS", "MAID", "LASS"}
_M_NAME = {"MR", "SIR", "LORD", "KING", "PRINCE", "DAD", "DADDY", "FATHER", "GRANDPA", "GRANDFATHER", "GRANDAD", "GRANDDAD", "UNCLE", "BROTHER",
           "HUSBAND", "BOYFRIEND", "BOY", "MAN", "WAITER", "BARMAN", "ACTOR", "MONK", "GROOM", "WIDOWER", "SON", "SCHOOLBOY",
           "POLICEMAN", "DUKE", "COUNT", "LAD", "GUY", "BLOKE", "GENTLEMAN"}
_F_WORD = (r"woman|girl|lady|mother|mum|mom|wife|daughter|sister|aunt|grandmother|grandma|girlfriend|actress|waitress|queen|"
           r"princess|nun|widow|bride|schoolgirl|heroine|matriarch|lass|madam|(?:scots|english|irish|welsh|french|dutch|business|police|"
           r"sales|noble|gentle|country|sports|states|council|chair|spokes|camera|stunt|trans )woman")
_M_WORD = (r"man|boy|guy|father|dad|husband|son|brother|uncle|grandfather|grandpa|boyfriend|king|prince|monk|widower|groom|"
           r"schoolboy|lad|bloke|gentleman|patriarch|(?:scots|english|irish|welsh|french|dutch|business|police|fire|sales|noble|"
           r"country|sports|states|council|chair|spokes|camera|stunt|door|bar|milk|post|mail|clergy|fisher|con|hit|gun|trans )man")
_G_WORD = re.compile(rf"\b(?:(?P<f>{_F_WORD})|(?P<m>{_M_WORD}))\b", re.I)
_G_PRON = re.compile(r"\b(?:(?P<f>she|her|hers|herself)|(?P<m>he|him|his|himself))\b", re.I)


def gender_from_text(text: str, name: str) -> tuple[str, str] | None:
    """(gender, how) from the part's name or the words where the script brings the character in; None when it doesn't
    say. how is "name", "words" or "pronoun"."""
    words = [w.strip(".") for w in name.upper().split()]
    for w in words:                                       # MRS HALE, TEENAGE GIRL, GIRLFRIEND
        if w in _F_NAME:
            return "Female", "name"
        if w in _M_NAME:
            return "Male", "name"
    m = re.search(rf"\b{re.escape(name.upper())}\b", text) or re.search(rf"\b{re.escape(name)}\b", text, re.I)
    if not m:
        return None
    after = text[m.end():m.end() + 260]
    sur = re.match(r"(?:\s+[A-Z][A-Z'\u2019.-]+){0,2}", after).end()                       # a surname is part of this name
    nxt = re.search(r"\b[A-Z][A-Z'\u2019]{2,}\b(?:\s+[A-Z][A-Z'\u2019.-]+)*\s*[,(]", after[sur + 1:])   # the next character brought in
    if nxt:
        after = after[:sur + 1 + nxt.start()]
    parts = re.split(r"(?<=[.!?])\s+", after, maxsplit=2)
    intro = parts[0][:160]                                # the rest of the sentence that names them
    g = re.search(rf"\bin (?:(?P<f>her)|(?P<m>his)) {_STAGE}(?:\d0'?s|{_AGE_WORD}|teens)\b", intro, re.I)   # "in her fifties"
    if g:
        return ("Female" if g.group("f") else "Male"), "words"
    # the description set beside the name: "DAVIE (20s), a nervous Scotsman with boyish looks, ..."
    a = re.match(r"(?:\s+[A-Z][A-Z'\u2019.-]+){0,2}\s*(?:\([^)\n]{0,24}\))?\s*[,\u2013\u2014-]\s*(?:[^,;.\n]{0,24}?\d[^,;.\n]{0,14}[,\u2013\u2014-]\s*)?"
                 r"((?:an?|the)\s[^,;.\n]{2,90})", intro)
    if a:
        g = _G_WORD.search(a.group(1))
        if g:
            return ("Female" if g.group("f") else "Male"), "words"
    # the next sentence opens on them ("She nods.", "His coat is soaked."), and nobody else is in the sentence that names them
    rest = re.sub(r"^(?:\s+[A-Z][A-Z'\u2019.-]+){0,2}", "", intro)             # past a surname: SARAH OKAFOR, 31, ...
    named = re.search(r"\b[A-Z][A-Z'\u2019]{2,}\b", rest)
    # their own things in the sentence that names them ("... a toolbag over her shoulder", "steadies himself"): only when
    # nobody else is named there and every he or she in it points the same way
    if not named:
        own = [("f" if x.group("f") or x.group("fs") else "m") for x in re.finditer(
            r"\b(?:(?:over|in|on|under|with|from|into|at|behind|around|across|through|to|of|by)\s+(?:(?P<f>her)|(?P<m>his))\s+(?!own\b)[a-z]|(?P<fs>herself)|(?P<ms>himself))", rest)]
        every = {("f" if x.group("f") else "m") for x in _G_PRON.finditer(rest)}
        if own and len(every) == 1:
            return ("Female" if every == {"f"} else "Male"), "pronoun"
    alone = not _G_PRON.search(rest) and not named
    if len(parts) > 1 and alone:
        g = re.match(r"(?:(?P<f>She|Her)|(?P<m>He|His))\b", parts[1])
        if g:
            return ("Female" if g.group("f") else "Male"), "pronoun"
    return None


def intros(filename: str, data: bytes, names: list[str]) -> dict[str, dict]:
    """For each name, the scene where the script first shows the character, cut to the passage around the name."""
    out = {}
    for sc in script.scene_texts(filename, data):
        text = sc["text"]
        for name in names:
            if name in out:
                continue
            m = re.search(rf"\b{re.escape(name)}\b", text, re.I)
            if m:
                start = max(0, m.start() - 200)
                out[name] = {"scene": sc["number"], "page": sc["page"], "heading": sc["heading"], "text": text[start:start + INTRO_CHARS]}
        if len(out) == len(names):
            break
    return out


# ------------------------------------------------------------------------------------------------ the model's reading
SYSTEM = ("You are an experienced casting director breaking down a screenplay for Saracen Bridge. For each role you are "
          "shown where the script first brings the character in. Say the character's gender and playing age, and describe "
          "the part in one plain sentence a casting director would put on a breakdown (who they are, what the part needs). "
          "Base everything on the text. Where the script doesn't say, infer from the scene and mark stated as false; if you "
          "script leaves the gender open or you cannot tell, say Any. Never name or suggest an actor.")


def _schema(names: list[str]) -> dict:
    role = {"type": "object", "additionalProperties": False,
            "required": ["name", "gender", "age_low", "age_high", "stated", "description", "qualities"],
            "properties": {"name": {"type": "string", "enum": names}, "gender": {"type": "string", "enum": list(GENDERS)},
                           "age_low": {"type": "integer", "minimum": 0, "maximum": 100},
                           "age_high": {"type": "integer", "minimum": 0, "maximum": 100}, "stated": {"type": "boolean"},
                           "description": {"type": "string"},
                           "qualities": {"type": "array", "maxItems": 5, "items": {"type": "string"}}}}
    return {"type": "object", "additionalProperties": False, "required": ["roles"],
            "properties": {"roles": {"type": "array", "minItems": len(names), "maxItems": len(names), "items": role}}}


def read_roles(filename: str, data: bytes, breakdown: dict, settings: dict, mode: str | None = None,
               progress=lambda m: None, cancelled=lambda: False) -> dict:
    """The model's reading of the principal roles (largest parts first, up to READ_ROLES), in groups of four."""
    ms = llm.mode_settings(settings, mode)
    engine, why = llm.resolve(settings, ms["mode"])
    if not engine:
        raise llm.EngineError(why)
    think = bool(ms["think"])
    rs = [r for r in roles(breakdown) if r["size"] != "Featured"][:READ_ROLES] or roles(breakdown)[:4]
    found = intros(filename, data, [r["name"] for r in rs])
    out, t0 = {}, __import__("time").time()
    groups = [rs[i:i + 4] for i in range(0, len(rs), 4)]
    for k, group in enumerate(groups, 1):
        if cancelled():
            raise InterruptedError("Cancelled")
        progress(f"Reading roles {min(len(rs), (k - 1) * 4 + 1)}–{min(len(rs), k * 4)} of {len(rs)}")
        names = [r["name"] for r in group]
        parts = []
        for r in group:
            it = found.get(r["name"])
            where = f"first seen in scene {it['scene']}, page {it['page']}: {it['heading']}" if it else "no introduction found"
            parts.append(f"ROLE: {r['name']} ({r['size'].lower()} part, in {r['scenes']} scenes, {r['dialogue']} speeches; {where})\n"
                         + (it["text"] if it else ""))
        extra = 3000 if think else 0
        ans = llm.chat(engine, SYSTEM, "\n\n---\n\n".join(parts), schema=_schema(names), settings=settings,
                       max_tokens=260 * len(names) + extra, temperature=0.2, think=think, think_budget=extra or None)
        for x in (ans or {}).get("roles") or []:
            if x.get("name") in names:
                lo, hi = sorted((int(x.get("age_low") or 0), int(x.get("age_high") or 0)))
                out[x["name"]] = {"gender": x.get("gender") if x.get("gender") in GENDERS else "Any", "age_low": lo, "age_high": hi,
                                  "stated": bool(x.get("stated")), "description": str(x.get("description") or "").strip()[:400],
                                  "qualities": [str(q)[:40] for q in (x.get("qualities") or [])][:5], "source": "model"}
    for r in rs:                               # an age printed in the script beats the model's reading
        it = found.get(r["name"])
        age = age_from_text(it["text"], r["name"]) if it else None
        if age:
            cur = out.setdefault(r["name"], {"gender": "Any", "description": "", "qualities": [], "source": "script"})
            cur.update(age_low=age[0], age_high=age[1], stated=True, age_from="script")
        if it and r["name"] in out:
            out[r["name"]].update(first_scene=it["scene"], first_page=it["page"])
    return {"roles": out, "mode": ms["mode"], "engine": engine.describe(), "seconds": round(__import__("time").time() - t0)}


_YOUNGER = re.compile(r"^(?:TEENAGE|TEENAGED|TEEN|YOUNG|YOUNGER|LITTLE|OLD|OLDER|ADULT)\s+")


def script_reading(filename: str, data: bytes, breakdown: dict) -> dict:
    """Without the model: what the script itself says about every speaking part, principal or featured (1.3.1): an age
    printed where the character comes in, and the gender its name or wording gives. Parts it says nothing about are
    left out."""
    rs = roles(breakdown)
    found = intros(filename, data, [r["name"] for r in rs])
    out = {}
    for r in sorted(rs, key=lambda r: bool(_YOUNGER.match(r["name"].upper()))):      # MIRREN before TEENAGE MIRREN
        it = found.get(r["name"])
        text = it["text"] if it else ""
        age = age_from_text(text, r["name"])
        gen = gender_from_text(text, r["name"])
        base = _YOUNGER.sub("", r["name"].upper()).strip()
        if not gen and base != r["name"].upper() and out.get(base, {}).get("gender") in ("Female", "Male"):
            gen = (out[base]["gender"], f"the same person as {base}")       # TEENAGE MIRREN is MIRREN
        if not age and not gen:
            continue
        rd = {"gender": gen[0] if gen else "Any", "description": "", "qualities": [], "source": "script", "stated": bool(age)}
        if age:
            rd.update(age_low=age[0], age_high=age[1], age_from="script")
        if gen:
            rd["gender_from"] = gen[1]
        if it:
            rd.update(first_scene=it["scene"], first_page=it["page"])
        out[r["name"]] = rd
    return out


def script_ages(filename: str, data: bytes, breakdown: dict) -> dict:
    """Kept for callers from before 1.3.1: the script's own reading of the principal roles."""
    principal = {r["name"] for r in roles(breakdown) if r["size"] != "Featured"}
    return {k: v for k, v in script_reading(filename, data, breakdown).items() if k in principal}


def merge_readings(script_says: dict | None, model_says: dict | None) -> dict:
    """The model's reading over the script's, part by part: the model fills what the script leaves open, an age the
    script prints stays (read_roles already puts it over the model's), and a gender the model left open takes the
    script's."""
    out = {k: dict(v) for k, v in (script_says or {}).items()}
    for name, rd in (model_says or {}).items():
        base = out.get(name) or {}
        cur = dict(rd)
        if cur.get("gender") not in ("Female", "Male", "Non-binary") and base.get("gender") in ("Female", "Male"):
            cur.update(gender=base["gender"], gender_from=base.get("gender_from"))
        if cur.get("age_low") is None and base.get("age_low") is not None:
            cur.update(age_low=base["age_low"], age_high=base["age_high"], age_from="script")
        out[name] = cur
    return out


# ------------------------------------------------------------------------------------------------ the shortlist
_COLS = ("actor, gender, approx_playing_age, commercial_tier, sales_role, composite_cast_value, supporting_value, lead_carry, "
         "primary_genres, indicative_cash_fee_low_usd, indicative_cash_fee_high_usd, minimum_sensible_budget_usd, "
         "optimal_budget_floor_usd, confidence, primary_market, last_reviewed")


def _num(v):
    try:
        return float(v) if v not in (None, "") else None
    except (TypeError, ValueError):
        return None


def _words(genres: str | None) -> set[str]:
    return {t.strip() for t in re.split(r"[,/;]", genres or "") if t.strip()}


def _bands(lo: int | None, hi: int | None) -> set[str]:
    if lo is None or hi is None or (lo == 0 and hi == 0):
        return set(BANDS)
    return {b for b, (a, z) in BANDS.items() if a <= hi and lo <= z}


def money(v) -> str:
    v = _num(v)
    if v is None:
        return "—"
    return f"${v / 1e6:g}m" if v >= 1e6 else f"${v / 1e3:g}k"


# Tier levels (1.3.1). Tim, 18 Nov: "make sure it's using the database to pair best cast to the role and tier level".
# The database grades every actor A+ to C (and Emerging), each with the smallest budget that sensibly carries them.
TIERS = ("A+", "A", "A-", "B+", "B", "B-", "C+", "C", "Emerging")
TIER_GROUPS = {"A": ("A+", "A", "A-"), "B": ("B+", "B", "B-"), "C": ("C+", "C", "Emerging")}
TIER_CHOICES = ("auto", "A", "B", "C")


def _tier_i(t) -> int:
    return TIERS.index(t) if t in TIERS else len(TIERS)


def top_tier(rows: list[dict], budget_usd: float | None) -> str | None:
    """The highest tier the budget sensibly carries: the best-graded actor whose minimum sensible budget it meets."""
    if not budget_usd:
        return None
    ok = [a["commercial_tier"] for a in rows if (_num(a["minimum_sensible_budget_usd"]) or 0) <= budget_usd and a["commercial_tier"] in TIERS]
    return min(ok, key=_tier_i) if ok else None


def _entry(a: dict, lead: bool, budget_usd: float | None, want: set) -> dict:
    key = "composite_cast_value" if lead else "supporting_value"
    optimal, floor = _num(a["optimal_budget_floor_usd"]), _num(a["minimum_sensible_budget_usd"])
    match = bool(want & _words(a["primary_genres"]))
    why = [f"{a['gender']}, playing age {a['approx_playing_age']}", f"tier {a['commercial_tier']}"]
    if match:
        why.append(f"works in {a['primary_genres']}")
    fit = None
    if budget_usd:
        if floor and floor > budget_usd:
            fit = "over"
            why.append(f"needs a bigger budget (minimum {money(floor)})")
        elif optimal and budget_usd >= optimal:
            fit = "within"
            why.append("budget at or above the optimal floor")
        else:
            fit = "stretch"
            why.append(f"budget fits (minimum {money(floor)}; optimal from {money(optimal)})")
    return {"actor": a["actor"], "tier": a["commercial_tier"], "sales_role": a["sales_role"],
            "value": _num(a[key]), "value_basis": "composite cast value" if lead else "supporting value",
            "fee_low": _num(a["indicative_cash_fee_low_usd"]), "fee_high": _num(a["indicative_cash_fee_high_usd"]),
            "min_budget": floor, "optimal_floor": optimal, "genres": a["primary_genres"], "genre_match": match,
            "confidence": a["confidence"], "market": a["primary_market"], "reviewed": str(a["last_reviewed"] or "")[:10],
            "tier_fit": fit, "why": why}


def shortlist(cast: list[dict], *, genre: str | None = None, budget_usd: float | None = None, n: int = SHORTLIST,
              tier_lead: str = "auto", tier_support: str = "auto") -> list[dict]:
    """For each role (with its reading merged in), up to n actors from the database, largest part first. An actor is
    suggested for one role only (the larger).

    Pairing: gender and playing-age band first; then the tier level. On "auto" with a budget, leads take the highest
    tier the budget carries and below, best composite cast value first; supporting parts start one tier below that,
    best supporting value first, so the leads outrank the support. A chosen level (A, B or C) keeps to that level's
    tiers. Without a budget there is nothing to grade against and every tier is open. The film's genre comes first
    within the level."""
    rows = refdata.rows(f"SELECT {_COLS} FROM talent_actors")
    want = GENRE_WORDS.get(genre or "", set())
    top = top_tier(rows, budget_usd)
    used: set[str] = set()
    out = []
    for r in cast:
        g, lo, hi = r.get("gender") if r.get("gender") in GENDERS else "Any", r.get("age_low"), r.get("age_high")
        bands = _bands(lo, hi)
        lead = r.get("size") == "Lead"
        key = "composite_cast_value" if lead else "supporting_value"
        choice = (tier_lead if lead else tier_support)
        choice = choice if choice in TIER_CHOICES else "auto"
        if choice != "auto":
            allowed, basis = set(TIER_GROUPS[choice]), f"tier level {choice} ({', '.join(TIER_GROUPS[choice])})"
        elif top:
            start = _tier_i(top) + (0 if lead else 1)
            allowed = set(TIERS[min(start, len(TIERS) - 1):])
            basis = (f"tier {top} and below: the highest the budget carries" if lead
                     else f"tier {TIERS[min(start, len(TIERS) - 1)]} and below: one below the leads' top tier")
        else:
            allowed, basis = set(TIERS), "every tier (no budget set)"

        def fits(pool: set) -> tuple[list, int, int]:
            """Picks from the pool's tiers; considered and over-budget count everyone who fits the part's gender and age
            (on auto, in any tier, so the names the budget leaves out are still counted)."""
            considered, over, picks = 0, 0, []
            for a in rows:
                if a["actor"] in used or a["approx_playing_age"] not in bands:
                    continue
                if g in ("Female", "Male") and a["gender"] != g:
                    continue
                in_pool = a["commercial_tier"] in pool
                if not in_pool and choice != "auto":
                    continue
                considered += 1
                floor = _num(a["minimum_sensible_budget_usd"])
                if budget_usd and floor and floor > budget_usd:
                    over += 1
                    continue
                if not in_pool:
                    continue
                match = bool(want & _words(a["primary_genres"]))
                picks.append((not match, -(_num(a[key]) or 0), a["actor"], a))
            picks.sort(key=lambda t: t[:3])
            return picks, considered, over

        picks, considered, over_budget = fits(allowed)
        if choice == "auto" and top and not lead and len(picks) < n:        # too few a tier down: open the leads' tier too
            allowed = set(TIERS[_tier_i(top):])
            basis = f"tier {top} and below (too few fit one tier down)"
            picks, considered, over_budget = fits(allowed)
        chosen = []
        for _, _, name, a in picks[:n]:
            used.add(name)
            chosen.append(_entry(a, lead, budget_usd, want))
        out.append(dict(r, shortlist=chosen, considered=considered, over_budget=over_budget,
                        filters={"gender": g if g in ("Female", "Male") else None, "bands": sorted(bands, key=lambda b: BANDS[b][0]),
                                 "tiers": [t for t in TIERS if t in allowed], "tier_choice": choice, "tier_basis": basis},
                        flags=[CHILD_RULE] if hi and hi < 18 and (lo or hi) else []))
    return out


def search(q: str, role: dict | None = None, *, genre: str | None = None, budget_usd: float | None = None, limit: int = 12) -> list[dict]:
    """Manual search of the actor database by name (1.3.1): anyone in it, whatever the shortlist's filters, each shown
    with how they fit this role (gender, playing age, budget), so the user can put their own choice forward."""
    words = [w for w in re.split(r"\s+", (q or "").strip().lower()) if w]
    if not words:
        return []
    rows = refdata.rows(f"SELECT {_COLS} FROM talent_actors")
    want = GENRE_WORDS.get(genre or "", set())
    role = role or {}
    lead = role.get("size") == "Lead"
    g = role.get("gender") if role.get("gender") in GENDERS else "Any"
    bands = _bands(role.get("age_low"), role.get("age_high"))
    hits = []
    for a in rows:
        name = (a["actor"] or "").lower()
        parts = name.split()
        if not all(any(p.startswith(w) for p in parts) or w in name for w in words):
            continue
        rank = 0 if all(any(p.startswith(w) for p in parts) for w in words) else 1
        e = _entry(a, lead, budget_usd, want)
        e["fits"] = {"gender": g not in ("Female", "Male") or a["gender"] == g, "age": a["approx_playing_age"] in bands,
                     "budget": e["tier_fit"] != "over"}
        e["gender"], e["playing_age"] = a["gender"], a["approx_playing_age"]
        hits.append((rank, name, e))
    hits.sort(key=lambda t: t[:2])
    return [e for _, _, e in hits[:max(1, min(limit, 50))]]


def suggest(breakdown: dict, reading: dict | None, *, genre=None, budget_usd=None, edits: dict | None = None,
            tier_lead: str = "auto", tier_support: str = "auto") -> dict:
    """Roles, each with its reading (the user's corrections over the model's over the script's) and shortlist."""
    reading, edits = reading or {}, edits or {}
    cast = []
    for r in roles(breakdown):
        rd = dict(reading.get(r["name"]) or {})
        ed = edits.get(r["name"]) or {}
        rd.update({k: v for k, v in ed.items() if k in ("gender", "age_low", "age_high", "description") and v not in (None, "")})
        if any(k in ed for k in ("gender", "age_low", "age_high", "description")):
            rd["edited"] = True
        size = ed.get("size") if ed.get("size") in SIZES else r["size"]
        g = rd.get("gender")
        cast.append(dict(r, size=size, read=rd or None, gender=g if g in GENDERS else "Any",
                         age_low=rd.get("age_low"), age_high=rd.get("age_high")))
    principal = [c for c in cast if c["size"] != "Featured"]
    featured = [c for c in cast if c["size"] == "Featured"]
    rows = refdata.rows(f"SELECT {_COLS} FROM talent_actors")
    return {"roles": shortlist(principal, genre=genre, budget_usd=budget_usd, tier_lead=tier_lead, tier_support=tier_support),
            "featured": [{k: c.get(k) for k in ("name", "scenes", "share", "dialogue", "days", "first_scene", "size", "gender", "age_low", "age_high")}
                         for c in featured],
            "genre": genre, "budget_usd": budget_usd, "database": "Saracen_Bridge_Actor_Value_Database_v2_2",
            "tier_lead": tier_lead if tier_lead in TIER_CHOICES else "auto",
            "tier_support": tier_support if tier_support in TIER_CHOICES else "auto",
            "top_tier": top_tier(rows, budget_usd), "tier_groups": {k: list(v) for k, v in TIER_GROUPS.items()},
            "actors": refdata.rows("SELECT COUNT(*) AS n FROM talent_actors")[0]["n"]}
