"""Greenlight decision hierarchy, from the Film Finance Analyst (data-room) SKILL.md, verbatim rules.

Scores are percentages (0-100). A score never neutralises an absolute blocker.
"""
from __future__ import annotations

DECISIONS = ("GREENLIGHT READY", "CONDITIONAL GREENLIGHT",
             "HOLD – MATERIAL CLOSING BLOCKERS", "DEVELOPMENT / NOT YET CLOSABLE")


def decide(overall: float, finance: float, legal: float, bond_insurance: float, production_delivery: float, *,
           critical_blockers: int, funding_gap: bool, signoffs_approved: bool,
           ready_gates_outstanding: int = 0, cures_owned_and_timed: bool = False) -> dict:
    reasons = []
    if overall < 55:
        return {"decision": DECISIONS[3], "reasons": ["Overall score below 55%."]}
    if critical_blockers > 0 or funding_gap:
        if critical_blockers:
            reasons.append(f"{critical_blockers} critical closing blocker(s).")
        if funding_gap:
            reasons.append("Funding gap remains.")
        return {"decision": DECISIONS[2], "reasons": reasons}
    if overall < 80:
        return {"decision": DECISIONS[2], "reasons": ["Overall score 55–79%."]}
    full = (overall >= 90 and finance >= 90 and legal >= 85 and bond_insurance >= 90
            and production_delivery >= 85 and signoffs_approved and ready_gates_outstanding == 0)
    if full:
        return {"decision": DECISIONS[0], "reasons": ["All thresholds met, no blockers, no gap, sign-offs approved."]}
    if cures_owned_and_timed:
        short = [n for n, v, t in (("overall", overall, 90), ("finance", finance, 90), ("legal", legal, 85),
                                   ("bond & insurance", bond_insurance, 90), ("production & delivery", production_delivery, 85)) if v < t]
        if short:
            reasons.append("Below greenlight threshold: " + ", ".join(short) + ".")
        if not signoffs_approved:
            reasons.append("Professional sign-offs outstanding.")
        if ready_gates_outstanding:
            reasons.append(f"{ready_gates_outstanding} Ready gate(s) outstanding with owned, time-bound cures.")
        return {"decision": DECISIONS[1], "reasons": reasons}
    return {"decision": DECISIONS[2], "reasons": ["Outstanding conditions lack a finite, owned, time-bound cure plan."]}
