"""Incentive engine: a code port of Jon's audited Stage 2 v1.1 controls.

Rules come from the Programme Rules table, never from headline rates. Unknown inputs are
`None`, never zero, and force PRELIMINARY (02 Shared Protocol, FPM control 6).
"""
from __future__ import annotations

from dataclasses import dataclass, field

from . import refdata

LIVE_STATUSES = {"Active"}
FAIL_STATUSES = {"Closed", "Test only"}


@dataclass
class ComponentResult:
    programme_id: str
    gate: str = "PASS"                       # PASS / PRELIMINARY / FAIL
    reasons: list[str] = field(default_factory=list)
    qualifying_spend: float | None = None
    eligible_base: float | None = None
    gross_benefit: float | None = None       # after benefit cap
    tax_effect: float | None = None
    net_after_tax: float | None = None
    currency: str | None = None

    def _downgrade(self, gate: str, reason: str) -> None:
        order = {"PASS": 0, "PRELIMINARY": 1, "FAIL": 2}
        if order[gate] > order[self.gate]:
            self.gate = gate
        self.reasons.append(reason)


def _num(v):
    return None if v in (None, "") else float(v)


def default_selectable(rules: list[dict] | None = None) -> list[dict]:
    """Programmes offered by default: selectable, Active, not TEST (regressions R08–R10)."""
    rules = rules if rules is not None else refdata.all_programme_rules()
    return [r for r in rules
            if r["selectable"] == "Yes" and r["availability_status"] in LIVE_STATUSES
            and not str(r["programme_id"]).startswith("TEST")]


def live_programmes(rules: list[dict] | None = None) -> list[dict]:
    rules = rules if rules is not None else refdata.all_programme_rules()
    return [r for r in rules if not str(r["programme_id"]).startswith("TEST")]


def calculate(programme_id: str, qualifying_spend: float | None, *,
              project_cost: float | None = None,
              eligibility: str = "Unknown",
              selected: set[str] | None = None) -> ComponentResult:
    rule = refdata.programme_rule(programme_id)
    res = ComponentResult(programme_id, qualifying_spend=qualifying_spend,
                          currency=rule["programme_currency"])
    selected = selected or {programme_id}

    # Availability gates
    status = rule["availability_status"]
    if status in FAIL_STATUSES:
        res._downgrade("FAIL", f"Programme status is {status}")
    elif status not in LIVE_STATUSES:
        res._downgrade("PRELIMINARY", f"Programme status is {status}; written confirmation of capacity required")

    # Eligibility (Unknown is not Eligible)
    if eligibility == "Excluded":
        res._downgrade("FAIL", "Spend marked Excluded")
    elif eligibility != "Eligible":
        res._downgrade("PRELIMINARY", f"Eligibility is {eligibility}")

    # Dependency and election gates (R05, R06)
    parent = rule["parent_programme"]
    if parent and parent not in selected:
        res._downgrade("FAIL", f"Enhancement requires parent programme {parent}")
    group = rule["election_group"]
    if group:
        peers = [r["programme_id"] for r in refdata.all_programme_rules()
                 if r["election_group"] == group and r["programme_id"] in selected]
        if len(peers) > 1:
            res._downgrade("FAIL", f"Alternative elections selected together: {', '.join(sorted(peers))}")

    if qualifying_spend is None:
        res._downgrade("PRELIMINARY", "Qualifying spend unknown")
        return res

    # Threshold gates
    min_spend, min_cost, max_cost = (_num(rule[k]) for k in
                                     ("minimum_programme_spend", "minimum_project_cost", "maximum_project_cost"))
    if min_spend is not None and qualifying_spend < min_spend:
        res._downgrade("FAIL", f"Qualifying spend below minimum {min_spend:,.0f}")
    if min_cost is not None or max_cost is not None:
        if project_cost is None:
            res._downgrade("PRELIMINARY", "Project cost unknown; cost thresholds untested")
        else:
            if min_cost is not None and project_cost < min_cost:
                res._downgrade("FAIL", f"Project cost below minimum {min_cost:,.0f}")
            if max_cost is not None and project_cost > max_cost:
                res._downgrade("FAIL", f"Project cost above maximum {max_cost:,.0f}")

    # Eligible-base caps (distinct from benefit caps: R04)
    base = qualifying_spend
    cap_abs = _num(rule["eligible_base_cap"])
    if cap_abs is not None:
        base = min(base, cap_abs)
    cap_pct = _num(rule["base_cap_project_cost"])
    if cap_pct is not None:
        if project_cost is None:
            res._downgrade("PRELIMINARY", f"Base capped at {cap_pct:.0%} of project cost, which is unknown")
        else:
            base = min(base, cap_pct * project_cost)
    res.eligible_base = base

    # Rate logic
    method = rule["calculation_method"]
    r1, r2, t1 = _num(rule["rate_1"]), _num(rule["rate_2"]), _num(rule["tier_1_threshold"])
    if method == "Tiered" and None not in (r1, r2, t1):
        gross = min(base, t1) * r1 + max(base - t1, 0.0) * r2
    elif method in ("Flat", "Enhancement") and r1 is not None:
        gross = base * r1
    else:
        res._downgrade("PRELIMINARY", f"Calculation method '{method}' needs a manual award")
        return res

    benefit_cap = _num(rule["benefit_cap"])
    if benefit_cap is not None:
        gross = min(gross, benefit_cap)
    res.gross_benefit = gross

    if rule["taxable_credit"] == "Yes":
        rate = _num(rule["illustrative_tax_rate"])
        if rate is None:
            res._downgrade("PRELIMINARY", "Taxable credit with unknown tax rate")
        else:
            res.tax_effect = gross * rate
            res.net_after_tax = gross - res.tax_effect
    else:
        res.tax_effect, res.net_after_tax = 0.0, gross

    if res.gate == "FAIL":
        res.reasons.append("Failed hard gate: controlled programme value is zero")
    return res
