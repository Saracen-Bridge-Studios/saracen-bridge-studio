"""Finance-plan engine: sources and uses, package sizing, double-count control.

Sources carry an `id` and an optional `parent`. A parent (an aggregate package) and its
children must never both count toward the stack. This is the defect found in SHADE v2/v3
(Inputs!B24 summed alongside B25:B26).
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Source:
    id: str
    name: str
    amount: float | None          # None = unknown, never zero
    status: str                   # finance_source_status vocabulary
    cash: bool = True             # in-kind is non-cash
    parent: str | None = None     # id of the aggregate package this sits inside
    is_debt: bool = False


@dataclass
class PlanResult:
    gross_budget: float
    permanent_sources: float
    gap: float                    # positive = shortfall
    debt_pct: float
    errors: list[str] = field(default_factory=list)
    preliminary: list[str] = field(default_factory=list)


def double_count_errors(sources: list[Source]) -> list[str]:
    ids = {s.id for s in sources}
    return [f"'{s.name}' is counted together with its own package '{s.parent}'"
            for s in sources if s.parent and s.parent in ids]


def reconcile(gross_budget: float, sources: list[Source], debt_cap: float = 0.70) -> PlanResult:
    errors = double_count_errors(sources)
    counted = [s for s in sources if s.amount is not None]
    prelim = [f"'{s.name}' amount unknown" for s in sources if s.amount is None]
    total = sum(s.amount for s in counted)
    debt = sum(s.amount for s in counted if s.is_debt)
    debt_pct = debt / gross_budget if gross_budget else 0.0
    if debt_pct > debt_cap:
        errors.append(f"Debt {debt_pct:.1%} of gross exceeds the {debt_cap:.0%} cap")
    return PlanResult(gross_budget, total, gross_budget - total, debt_pct, errors, prelim)


def size_package(gross_budget: float, package_pct: float, incentive_claim: float) -> dict:
    """Aggregate support package (SHADE / Non-Stop pattern, spec §10): facility and in-kind sit inside it."""
    package = gross_budget * package_pct
    facility = min(incentive_claim, package)
    return {"package": package, "facility": facility, "in_kind": max(0.0, package - facility)}


def residual_debt(gross_budget: float, sources: list[Source]) -> float:
    """Senior/gap requirement after every non-debt source, excluding package parents."""
    parents = {s.parent for s in sources if s.parent}
    non_debt = sum(s.amount or 0.0 for s in sources if not s.is_debt and s.id not in parents)
    return max(0.0, gross_budget - non_debt)
