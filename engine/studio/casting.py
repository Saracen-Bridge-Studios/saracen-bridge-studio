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


def age_from_text(text: str, name: str) -> tuple[int, int] | None:
    """An age printed beside the character's name where it first appears: "MARA (34)", "MARA OKAFOR (30s)",
    "MARA (late 40s)", "MARA (mid-twenties)"."""
    # the name as the script prints it on entry (capitals), perhaps with a surname: "MARA OKAFOR (34)"
    m = re.search(rf"\b{re.escape(name.upper())}\b(?:\s+[A-Z][A-Z'\u2019.-]+){{0,2}},?\s*\(([^)\n]{{1,24}})\)", text)
    if not m:
        return None
    t = m.group(1).lower().replace("-", " ")
    if re.fullmatch(r"\s*(\d{1,2})\s*", t):
        a = int(t)
        return (a, a) if 1 <= a <= 100 else None
    span = None
    d = re.search(r"(\d)0'?s", t)
    if d:
        span = (int(d.group(1)) * 10, int(d.group(1)) * 10 + 9)
    else:
        w = next((v for k, v in _WORDS.items() if k in t), None)
        span = w
    if not span:
        return None
    lo, hi = span
    if "early" in t:
        hi = lo + 3
    elif "mid" in t:
        lo, hi = lo + 3, lo + 6
    elif "late" in t:
        lo = lo + 6
    return lo, hi


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


def script_ages(filename: str, data: bytes, breakdown: dict) -> dict:
    """Without the model: the ages the script prints beside its principal roles."""
    rs = [r for r in roles(breakdown) if r["size"] != "Featured"][:READ_ROLES]
    found = intros(filename, data, [r["name"] for r in rs])
    out = {}
    for r in rs:
        it = found.get(r["name"])
        age = age_from_text(it["text"], r["name"]) if it else None
        if age:
            out[r["name"]] = {"gender": "Any", "age_low": age[0], "age_high": age[1], "stated": True, "description": "",
                              "qualities": [], "source": "script", "age_from": "script", "first_scene": it["scene"], "first_page": it["page"]}
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


def shortlist(cast: list[dict], *, genre: str | None = None, budget_usd: float | None = None, n: int = SHORTLIST) -> list[dict]:
    """For each role (with its reading merged in), up to n actors from the database, largest part first. An actor is
    suggested for one role only (the larger)."""
    rows = refdata.rows(f"SELECT {_COLS} FROM talent_actors")
    want = GENRE_WORDS.get(genre or "", set())
    used: set[str] = set()
    out = []
    for r in cast:
        g, lo, hi = r.get("gender") if r.get("gender") in GENDERS else "Any", r.get("age_low"), r.get("age_high")
        bands = _bands(lo, hi)
        lead = r.get("size") == "Lead"
        key = "composite_cast_value" if lead else "supporting_value"
        considered, over_budget, picks = 0, 0, []
        for a in rows:
            if a["actor"] in used or a["approx_playing_age"] not in bands:
                continue
            if g in ("Female", "Male") and a["gender"] != g:
                continue
            considered += 1
            floor = _num(a["minimum_sensible_budget_usd"])
            if budget_usd and floor and floor > budget_usd:
                over_budget += 1
                continue
            match = bool(want & _words(a["primary_genres"]))
            picks.append((not match, -(_num(a[key]) or 0), a["actor"], a, match))
        picks.sort(key=lambda t: t[:3])
        chosen = []
        for _, _, name, a, match in picks[:n]:
            used.add(name)
            optimal = _num(a["optimal_budget_floor_usd"])
            why = [f"{a['gender']}, playing age {a['approx_playing_age']}"]
            if match:
                why.append(f"works in {a['primary_genres']}")
            if budget_usd:
                why.append("budget at or above the optimal floor" if optimal and budget_usd >= optimal
                           else f"budget fits (minimum {money(a['minimum_sensible_budget_usd'])}; optimal from {money(optimal)})")
            chosen.append({"actor": name, "tier": a["commercial_tier"], "sales_role": a["sales_role"],
                           "value": _num(a[key]), "value_basis": "composite cast value" if lead else "supporting value",
                           "fee_low": _num(a["indicative_cash_fee_low_usd"]), "fee_high": _num(a["indicative_cash_fee_high_usd"]),
                           "min_budget": _num(a["minimum_sensible_budget_usd"]), "optimal_floor": optimal,
                           "genres": a["primary_genres"], "genre_match": match, "confidence": a["confidence"],
                           "market": a["primary_market"], "reviewed": str(a["last_reviewed"] or "")[:10], "why": why})
        out.append(dict(r, shortlist=chosen, considered=considered, over_budget=over_budget,
                        filters={"gender": g if g in ("Female", "Male") else None, "bands": sorted(bands, key=lambda b: BANDS[b][0])},
                        flags=[CHILD_RULE] if hi and hi < 18 and (lo or hi) else []))
    return out


def suggest(breakdown: dict, reading: dict | None, *, genre=None, budget_usd=None, edits: dict | None = None) -> dict:
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
    return {"roles": shortlist(principal, genre=genre, budget_usd=budget_usd),
            "featured": [{k: c[k] for k in ("name", "scenes", "share", "dialogue", "days", "first_scene", "size")} for c in featured],
            "genre": genre, "budget_usd": budget_usd, "database": "Saracen_Bridge_Actor_Value_Database_v2_2",
            "actors": refdata.rows("SELECT COUNT(*) AS n FROM talent_actors")[0]["n"]}
