"""BFI Film Cultural Test scorer (rules from Jon's 02_BFI_Summary_of_Cultural_Test_Points, checked 12 Jul 2026).

35 points available, pass mark 18. C1 capped at 4, with C2 adding at most 1.
Golden points rule: a film that takes all 19 points from A4, Section C and Section D must
also take at least 2 points from A1 and/or A2, or all 4 from A3.
"""
from __future__ import annotations

from . import refdata

PASS_MARK = 18


def criteria() -> list[dict]:
    return refdata.rows("SELECT ref, section, criterion, max_points, graduated FROM bfi_cultural_test ORDER BY rowid")


def score(points: dict[str, float]) -> dict:
    """points: criterion ref -> claimed points. Missing refs count as 0. Values are clamped to each maximum."""
    crit = {c["ref"]: c for c in criteria()}
    unknown = sorted(set(points) - set(crit))
    clamped = {ref: max(0.0, min(float(points.get(ref, 0) or 0), c["max_points"])) for ref, c in crit.items()}
    sec = {s: sum(v for r, v in clamped.items() if crit[r]["section"] == s) for s in "ABCD"}
    c1 = sum(clamped[r] for r in ("C1(a)", "C1(b)", "C1(c)"))
    sec["C"] = min(c1, 4) + min(clamped["C2"], 1)
    total = sum(sec.values())
    golden_pool = clamped["A4"] + sec["C"] + sec["D"]
    golden_triggered = golden_pool >= 19
    golden_met = (clamped["A1"] + clamped["A2"] >= 2) or clamped["A3"] >= 4
    golden_fail = golden_triggered and not golden_met
    passed = total >= PASS_MARK and not golden_fail
    notes = []
    if c1 > 4:
        notes.append(f"C1 claims {c1:g} points; capped at 4.")
    if golden_fail:
        notes.append("Golden points rule not met: needs 2+ points from A1/A2 or all 4 from A3.")
    if unknown:
        notes.append(f"Unknown criteria ignored: {', '.join(unknown)}")
    return {"sections": sec, "total": total, "pass_mark": PASS_MARK, "passed": passed,
            "margin": total - PASS_MARK, "golden_rule_failed": golden_fail, "notes": notes, "points": clamped}


def assess(proposed: dict, conservative: dict) -> dict:
    p, c = score(proposed), score(conservative)
    if c["passed"]:
        verdict = "PASS"
    elif p["passed"]:
        verdict = "BORDERLINE"
    else:
        verdict = "FAIL"
    return {"verdict": verdict, "proposed": p, "conservative": c}
