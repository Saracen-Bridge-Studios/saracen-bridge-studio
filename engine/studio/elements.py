"""Scheduling & Budgeting: element tagging from the script (1.0.8).

Jon's instructions for this tool (sources/t03_schedule_budget SKILL.md) ask the script analysis to quantify, among
other things: background and special-skill cast, child cast, stunts, fights and intimacy, weapons, vehicles, animals,
crowds, water and aerial work, costume and hair/make-up needs, props, practical effects and VFX, special equipment,
music and playback, and to log assumptions. The reader counts scenes, cast and locations; this pass has the model tag
each scene's production elements, the way a breakdown sheet does, so the budget can price them.

What the model gives is a reading, not a count: every tag is listed by scene for checking, the budget lines it drives
say so, and the producer's own figures (background a day, VFX shots, any line's amount) still override it.
"""
from __future__ import annotations

from . import sceneai

FIELDS = {   # key: (label, kind)
    "background": ("Background artists", "count"),
    "stunts": ("Stunts and fights", "list"),
    "stunt_performers": ("Stunt performers", "count"),
    "vehicles": ("Picture vehicles", "list"),
    "weapons": ("Weapons", "list"),
    "animals": ("Animals", "list"),
    "sfx": ("Practical effects", "list"),
    "vfx": ("Visual effects", "list"),
    "vfx_shots": ("VFX shots (estimate)", "count"),
    "props": ("Key props", "list"),
    "wardrobe": ("Costume needs", "list"),
    "makeup": ("Special make-up and hair", "list"),
    "special_equipment": ("Special equipment", "list"),
    "minors": ("Child performers", "list"),
    "intimacy": ("Intimacy", "flag"),
    "water": ("Water work", "flag"),
    "music": ("Music and playback", "list"),
}
LISTS = [k for k, (_, kind) in FIELDS.items() if kind == "list"]
# Background is asked as a band, not a number: tested 15 Oct, Gemma 4 E2B answered 500 or 1000 extras for every scene
# of the Night Ferry fixture, kitchen included, when asked for a count. Each band is planned at the figure shown.
BACKGROUND = {"none": 0, "1-10": 6, "11-30": 20, "31-100": 60, "over 100": 150}
TOKENS_PER_SCENE = 320          # measured 15 Oct: Gemma 4 E2B wrote 3,527 tokens tagging the fixture's 14 scenes (~250 each)


def _obj(props: dict) -> dict:
    return {"type": "object", "properties": props, "required": list(props), "additionalProperties": False}


def schema(scenes: list[dict]) -> dict:
    lst = {"type": "array", "maxItems": 8, "items": {"type": "string"}}
    item = {"scene": {"type": "integer", "enum": [s["number"] for s in scenes]},
            "background": {"type": "string", "enum": list(BACKGROUND)},
            "stunt_performers": {"type": "integer", "minimum": 0, "maximum": 100},
            "vfx_shots": {"type": "integer", "minimum": 0, "maximum": 200},
            "intimacy": {"type": "boolean"}, "water": {"type": "boolean"}}
    item.update({k: lst for k in LISTS})
    item["notes"] = {"type": "string"}
    return _obj({"scenes": {"type": "array", "minItems": len(scenes), "maxItems": len(scenes), "items": _obj(item)}})


SYSTEM = ("You are an experienced 1st assistant director and line producer making a script breakdown, as Saracen Bridge's "
          "scheduling and budgeting instructions require: quantify the material drivers of schedule and cost, and separate what "
          "the script says from what you infer.\n\n"
          "TASK: For every scene shown, fill in its breakdown sheet. Use only what the scene describes or clearly requires; "
          "leave a list empty and a count at 0 when the scene has none. Short items, a few words each.\n"
          "background: how many background artists (extras) the scene needs on camera, as a band: none (only the speaking cast, "
          "the usual case indoors), 1-10, 11-30, 31-100 or over 100. Only count people the scene describes or plainly needs.\n"
          "stunts: stunts, fights, falls, dangerous driving, anything needing a stunt coordinator.\n"
          "stunt_performers: how many stunt performers or doubles those stunts need (0 if no stunts).\n"
          "vehicles: picture vehicles seen or driven on screen (not crew transport).\n"
          "weapons: firearms, knives, any weapon handled or fired.\n"
          "animals: animals on screen.\n"
          "sfx: practical special effects on set: rain, wind, smoke, fire, explosions, bullet hits, breakaways.\n"
          "vfx: visual effects needed in post: digital environments, set extensions, screen replacements, muzzle flashes, removals.\n"
          "vfx_shots: your estimate of the number of VFX shots in the scene (0 if none).\n"
          "props: props the action depends on (not set dressing).\n"
          "wardrobe: special costume needs: period, uniforms, multiples, wet-downs, blood.\n"
          "makeup: special make-up and hair: wounds, blood, prosthetics, ageing, wigs.\n"
          "special_equipment: crane, drone or aerial unit, camera car or tracking vehicle, steadicam, underwater, marine or boat work.\n"
          "minors: child performers (characters under 16), named or described.\n"
          "intimacy: true if the scene has nudity or simulated sex. water: true if performers or cameras work in or on water.\n"
          "music: songs or music performed or played back on camera.\n"
          "notes: anything else that drives cost or time (night exterior in rain, crowd control, a big set). Empty if nothing.\n"
          "Plain text in the strings; no markdown.")


def tag(filename: str, data: bytes, breakdown: dict, settings: dict, *, progress=lambda m: None, cancelled=lambda: False,
        mode: str | None = None) -> dict:
    reading = sceneai.Reading(filename, data, breakdown, settings, mode, progress, cancelled, share=0.3)
    groups = reading.over_scenes(SYSTEM, f"FILM: {breakdown.get('title') or 'Untitled'}.", schema, lambda sc: 400 + TOKENS_PER_SCENE * len(sc),
                                 label="Tagging scenes")
    by_scene: dict[int, dict] = {}
    for shown, ans in groups:
        allowed = {s["number"] for s in shown}
        for row in ans.get("scenes") or []:
            n = row.get("scene")
            if n not in allowed:
                continue
            cur = by_scene.setdefault(n, {k: ([] if kind == "list" else False if kind == "flag" else 0) for k, (_, kind) in FIELDS.items()} | {"notes": ""})
            row = dict(row)
            row["background"] = BACKGROUND.get(str(row.get("background")), 0)
            if not row.get("stunts"):                       # performers only where there is a stunt to perform
                row["stunt_performers"] = 0
            if not row.get("vfx"):
                row["vfx_shots"] = 0
            for k, (_, kind) in FIELDS.items():              # a long scene split in two is tagged twice: merge
                v = row.get(k)
                if kind == "list":
                    cur[k] = list(dict.fromkeys(cur[k] + [str(x).strip() for x in v or [] if str(x).strip()]))
                elif kind == "count":
                    cur[k] = max(cur[k], max(0, int(v or 0)))
                else:
                    cur[k] = cur[k] or bool(v)
            cur["notes"] = " ".join(x for x in (cur["notes"], (row.get("notes") or "").strip()) if x)
    scenes = []
    for s in reading.scenes:
        tags = by_scene.get(s["number"])
        scenes.append({"scene": s["number"], "heading": s["heading"], "page": s["page"], "page_estimated": s.get("page_estimated", False),
                       "tagged": tags is not None, **(tags or {k: ([] if kind == "list" else False if kind == "flag" else 0)
                                                           for k, (_, kind) in FIELDS.items()} | {"notes": ""})})
    res = {"title": breakdown.get("title") or "", "scenes": scenes, "summary": summary(scenes), "made_with": reading.made_with()}
    missing = [s["scene"] for s in scenes if not s["tagged"]]
    res["checks"] = ([f"{len(missing)} scene(s) came back without tags ({', '.join(map(str, missing[:12]))}): tag again or check them by hand."]
                     if missing else [])
    crowd = [s for s in scenes if s["tagged"] and s["background"] >= 60]
    if len(crowd) > 0.5 * max(1, sum(1 for s in scenes if s["tagged"])):
        res["checks"].append(f"Crowds of 31 or more in {len(crowd)} of {len(scenes)} scenes: that looks overstated. Check the Elements sheet, "
                             "or enter background a day yourself, before relying on the background line.")
    return res


def summary(scenes: list[dict]) -> dict:
    """Per element: the scenes it appears in; for lists, each distinct item with its scenes."""
    out = {}
    for k, (label, kind) in FIELDS.items():
        if kind == "list":
            items: dict[str, dict] = {}
            for s in scenes:
                for x in s[k]:
                    key = x.lower()
                    items.setdefault(key, {"item": x, "scenes": []})["scenes"].append(s["scene"])
            out[k] = {"label": label, "scenes": sorted({n for i in items.values() for n in i["scenes"]}),
                      "items": sorted(items.values(), key=lambda i: (-len(i["scenes"]), i["item"].lower()))}
        elif kind == "count":
            hit = [s for s in scenes if s[k]]
            out[k] = {"label": label, "scenes": [s["scene"] for s in hit], "total": sum(s[k] for s in hit), "max": max([s[k] for s in hit] or [0])}
        else:
            out[k] = {"label": label, "scenes": [s["scene"] for s in scenes if s[k]]}
    return out


def by_scene(res: dict | None) -> dict[int, dict]:
    return {s["scene"]: s for s in (res or {}).get("scenes") or [] if s.get("tagged")}
