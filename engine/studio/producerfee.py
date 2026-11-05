"""Producer-fee allowance (1.2.0): how much of a producer or executive-producer fee can count as qualifying expenditure
for a film incentive, route by route, from Saracen Bridge's table (tools/producer_fees.json, sources checked
21 October 2026; scripts/build_producer_fees.py has the source and the Rule 1 check).

Saracen Bridge's method: work out the eligible producer fee first, then express it as a share of the worldwide budget;
where the cap is shared with other ATL costs or overheads, subtract those first; a contractual fee can exceed the
eligible amount, and the excess stays out of the incentive calculation. As everywhere in the Studio, an unknown input
stays unknown: a route that needs a figure nobody has entered, or a residency nobody has confirmed, gives no eligible
amount rather than a guess, and says what it needs. "Confirm" routes are never treated as uncapped.

Inputs (all amounts in the route's currency):
    fees              [{role, amount, resident: yes/no/unknown, paid_as: salary/loan-out/company/unknown, related: bool}]
    worldwide_budget  the film's total budget (production cost)
    local_spend       qualifying spend in the route's jurisdiction
    local_budget      the jurisdiction's budget, where the rule uses it (Hungary); defaults to local_spend
    bc                B+C: production plus post-production costs (Canada)
    other_atl         other qualifying ATL costs that share the pool
    overheads         production/corporate overheads that share the pool (Ireland, Yukon)
    documentary       bool
    incentive_rate    the route's rate, where the rule turns on it (Nova Scotia)
"""
from __future__ import annotations

import json
from functools import lru_cache

from . import refdata

STATUS_LABEL = {"rule": "Rule", "benchmark": "Benchmark, not a maximum", "actual": "Actual qualifying services",
                "confirm": "Confirm", "zero": "Not eligible", "unavailable": "Not available"}


@lru_cache(maxsize=1)
def table() -> dict:
    return json.loads((refdata.app_root() / "tools" / "producer_fees.json").read_text(encoding="utf-8"))


def routes() -> list[dict]:
    return table()["routes"]


def route(route_id: str) -> dict | None:
    return next((r for r in routes() if r["id"] == route_id), None)


def for_programme(programme_id: str) -> dict | None:
    """The producer-fee route for an incentive programme in the Studio's incentive list, if the table covers it."""
    return next((r for r in routes() if programme_id in r["programmes"]), None)


def summary() -> list[dict]:
    """The routes for a picker: no rule internals."""
    return [{k: r[k] for k in ("id", "area", "country", "regions", "route", "status", "currency", "programmes")}
            | {"status_label": STATUS_LABEL[r["status"]]} for r in routes()]


def _n(v):
    if v in (None, ""):
        return None
    return float(v)


def _base(name: str, ctx: dict, fees_total: float):
    """A rule's base, or None if it needs a figure nobody has entered."""
    wb, ls = _n(ctx.get("worldwide_budget")), _n(ctx.get("local_spend"))
    if name == "worldwide_budget":
        return wb
    if name == "local_spend":
        return ls
    if name == "local_budget":
        lb = _n(ctx.get("local_budget"))
        return lb if lb is not None else ls
    if name == "bc":
        return _n(ctx.get("bc"))
    if name == "production_costs_ex_fee":
        return None if wb is None else wb - fees_total
    if name == "local_spend_ex_fee":
        return None if ls is None else ls - fees_total
    if name == "other_qualified_costs":
        # New York: 40% of all other qualified production costs, i.e. the qualifying spend less the ATL that shares the pool
        return None if ls is None else ls - fees_total - (_n(ctx.get("other_atl")) or 0.0)
    raise ValueError(name)


BASE_LABEL = {"worldwide_budget": "the worldwide budget", "local_spend": "the local qualifying spend",
              "local_budget": "the local budget", "bc": "B+C (production plus post-production costs)",
              "production_costs_ex_fee": "production costs excluding the producer fee",
              "local_spend_ex_fee": "the service producer's production costs excluding its fee",
              "other_qualified_costs": "all other qualified production costs"}


def assess(route_id: str, ctx: dict) -> dict:
    r = route(route_id)
    if not r:
        raise ValueError(f"Unknown producer-fee route: {route_id}")
    c = r["calc"]
    fees = [dict(f, amount=_n(f.get("amount"))) for f in (ctx.get("fees") or []) if _n(f.get("amount"))]
    total = sum(f["amount"] for f in fees)
    wb = _n(ctx.get("worldwide_budget"))
    out = {"route": r["id"], "country": r["country"], "regions": r["regions"], "name": r["route"], "status": r["status"],
           "status_label": STATUS_LABEL[r["status"]], "currency": r["currency"], "total_fees": total, "eligible": None,
           "excluded": None, "ceiling": None, "benchmark": None, "share_of_budget": None, "lines": [], "basis": [],
           "needs": [], "confirm": [], "allowance": r["allowance"], "apply": r["apply"], "source": r["source"],
           "checked": table()["checked"]}
    if not fees:
        out["needs"].append("Enter the producer and executive-producer fees.")
        return out

    def finish(eligible):
        out["eligible"] = eligible
        if eligible is not None:
            out["excluded"] = total - eligible
            if wb:
                out["share_of_budget"] = eligible / wb
        return out

    status = r["status"]
    if status == "zero":
        out["lines"] = [{"role": f.get("role") or "Producer", "amount": f["amount"], "eligible": 0.0,
                         "why": "not eligible under this route"} for f in fees]
        out["basis"].append(r["allowance"])
        return finish(0.0)
    if status == "unavailable":
        out["basis"].append(r["allowance"])
        out["confirm"].append("No award is currently available on this route.")
        return finish(0.0)

    # ---- each person's fee: residency, who is paid, per-person caps and exclusions
    held = False
    lines = []
    nc_cap = None
    if c.get("incentive_cap_per_person"):
        rate = _n(ctx.get("incentive_rate"))
        if rate:
            nc_cap = c["incentive_cap_per_person"] / rate
            out["basis"].append(f"Fee ceiling per person: {c['incentive_cap_per_person']:,.0f} of incentive ÷ "
                                f"{rate:.0%} = {nc_cap:,.0f}.")
        else:
            out["needs"].append("The route's incentive rate (the fee ceiling is the per-person incentive cap divided by it).")
    for f in fees:
        amt, why, ok = f["amount"], [], f["amount"]
        resident, paid = (f.get("resident") or "unknown"), (f.get("paid_as") or "unknown")
        if c.get("residents_only"):
            if resident == "no":
                ok, why = 0.0, ["non-resident: not eligible"]
            elif resident != "yes":
                ok, held = None, True
                why = ["residency not confirmed"]
        if ok and c.get("individuals_only") and paid == "company":
            ok, why = 0.0, why + ["a production-company fee is excluded as such"]
        if ok and c.get("exclude_at_or_above") and amt >= c["exclude_at_or_above"]:
            ok, why = 0.0, why + [f"{c['exclude_at_or_above']:,.0f} or more: the whole payment is excluded"]
        if ok and c.get("exclude_above") and amt > c["exclude_above"]:
            ok, why = 0.0, why + [f"more than {c['exclude_above']:,.0f}: the whole payment is excluded"]
        if ok and c.get("salary_cap_per_person"):
            cap = c["salary_cap_per_person"]
            if paid == "salary" and amt > cap:
                ok, why = cap, why + [f"W-2 salary capped at {cap:,.0f}"]
            elif paid in ("loan-out", "company"):
                why.append("loan-out: the salary cap doesn't apply")
            elif paid == "unknown" and amt > cap:
                ok, why = cap, why + [f"capped at {cap:,.0f} unless paid through a loan-out (how is this person paid?)"]
                out["confirm"].append("How each producer is paid (W-2 salary or loan-out) changes the cap.")
        if ok and c.get("per_person_cap") and amt > c["per_person_cap"]:
            ok, why = min(ok, c["per_person_cap"]), why + [f"first {c['per_person_cap']:,.0f} per person"]
        if ok and nc_cap is not None and ok > nc_cap:
            ok, why = nc_cap, why + [f"capped at {nc_cap:,.0f}"]
        elif ok and c.get("incentive_cap_per_person") and nc_cap is None:
            ok, held = None, True
        lines.append({"role": f.get("role") or "Producer", "amount": amt, "eligible": ok, "why": "; ".join(why),
                      "related": bool(f.get("related"))})
    if c.get("max_people") and len([x for x in lines if x["eligible"]]) > c["max_people"]:
        keep = sorted([x for x in lines if x["eligible"]], key=lambda x: -x["eligible"])[:c["max_people"]]
        for x in lines:
            if x["eligible"] and x not in keep:
                x["eligible"], x["why"] = 0.0, "; ".join(filter(None, [x["why"], f"only {c['max_people']} producers' fees count"]))
    out["lines"] = lines

    if status == "confirm":
        out["confirm"].append(r["allowance"])
        if c.get("options"):
            for o in c["options"]:
                v = o.get("amount")
                if v is None:
                    b = _base(o["base"], ctx, total)
                    v = None if b is None else o["pct"] * b
                out["basis"].append(f"{o['label']}: " + (f"{v:,.0f}." if v is not None else f"needs {BASE_LABEL[o['base']]}."))
        if c.get("benchmark"):
            b = _base(c["benchmark"]["base"], ctx, total)
            if b is not None:
                out["benchmark"] = c["benchmark"]["pct"] * b
                out["basis"].append(f"Federal reference: {c['benchmark']['pct']:.0%} of B+C = {out['benchmark']:,.0f}.")
        return finish(None)
    if held:
        out["needs"].append("Confirm each producer's residency (or how they're paid) for this route.")
        return finish(None)
    after_person = sum(x["eligible"] for x in lines)

    if status == "actual":
        out["basis"].append(r["allowance"])
        out["confirm"].append("No fixed ceiling: only the qualifying services actually performed count; the incentive "
                              "accountant allocates them.")
        if c.get("since"):
            out["basis"].append(f"Applies to productions starting from {c['since']}; earlier starts keep the former cap.")
        return finish(None) if after_person else finish(0.0)

    if status == "benchmark":
        b = _base(c["benchmark"]["base"], ctx, total)
        if b is None:
            out["needs"].append(f"Enter {BASE_LABEL[c['benchmark']['base']]} to see the reference.")
            return finish(None)
        ref = c["benchmark"]["pct"] * b
        out["benchmark"] = ref
        out["basis"].append(f"Reference: {c['benchmark']['pct']:.0%} of {BASE_LABEL[c['benchmark']['base']]} = {ref:,.0f}. "
                            "Not a maximum.")
        if after_person > ref:
            out["confirm"].append(f"The fees are {after_person - ref:,.0f} above the reference: higher fees need support.")
        return finish(None)

    # ---- the ceiling for the whole pot
    ceiling = None
    shares = c.get("shares_with", [])
    shared = sum(_n(ctx.get(k)) or 0.0 for k in shares)
    missing_shared = [k for k in shares if _n(ctx.get(k)) is None]
    if c.get("ireland"):
        ls = _n(ctx.get("local_spend"))
        if wb is None or ls is None:
            out["needs"].append("Enter the worldwide budget and the Irish eligible expenditure.")
            return finish(None)
        share = ls / wb if wb else 0.0
        if abs(share - 0.80) < 1e-9:
            out["confirm"].append("Eligible expenditure is exactly 80% of the global budget: the guidance doesn't say "
                                  "whether 10% or 15% applies.")
            return finish(None)
        pct = 0.15 if share > 0.80 else 0.10
        ceiling = pct * wb
        out["basis"].append(f"Eligible expenditure is {share:.1%} of the global budget, so {pct:.0%} of it: {ceiling:,.0f}, "
                            "shared with co-producer and EP fees and overheads.")
    elif c.get("bands"):
        if wb is None:
            out["needs"].append("Enter the worldwide budget (total production cost).")
            return finish(None)
        for b in c["bands"]:
            if "up_to" in b:
                if wb <= b["up_to"]:
                    ceiling = b["cap"]
                    out["basis"].append(f"Budget up to {b['up_to']:,.0f}: up to {b['cap']:,.0f}.")
                    break
            else:
                base = _base(b["base"], ctx, total)
                ceiling = min(b["pct"] * base, b["cap"])
                out["basis"].append(f"{b['pct']:.0%} of {BASE_LABEL[b['base']]} ({base:,.0f}), at most {b['cap']:,.0f}: "
                                    f"{ceiling:,.0f}.")
    elif c.get("lower_of") or c.get("higher_of"):
        vals = []
        for o in c.get("lower_of") or c.get("higher_of"):
            if "amount" in o:
                vals.append(o["amount"])
            else:
                b = _base(o["base"], ctx, total)
                if b is None:
                    out["needs"].append(f"Enter {BASE_LABEL[o['base']]}.")
                    return finish(None)
                vals.append(o["pct"] * b)
        ceiling = min(vals) if c.get("lower_of") else max(vals)
        out["basis"].append(f"The {'lower' if c.get('lower_of') else 'higher'} of {' and '.join(f'{v:,.0f}' for v in vals)}: "
                            f"{ceiling:,.0f}" + (", limited to the actual fee." if c.get("higher_of") else "."))
    elif c.get("pool"):
        p = c["pool"]
        if c.get("documentary_exempt") and ctx.get("documentary"):
            out["basis"].append("Documentaries are exempt from this cap.")
            ceiling = None
        else:
            base = _base(p["base"], ctx, total)
            if base is None:
                out["needs"].append(f"Enter {BASE_LABEL[p['base']]}.")
                return finish(None)
            pct = p["pct"]
            if p.get("documentary_pct") and ctx.get("documentary") and (wb is not None and wb < p["documentary_budget_under"]):
                pct = p["documentary_pct"]
            if p.get("small_budget") is not None:
                if wb is None:
                    out["needs"].append("Enter the worldwide budget.")
                    return finish(None)
                if wb <= p["small_budget"]:
                    pct = p["small_pct"]
            ceiling = pct * base
            if p.get("cap") is not None and (p.get("small_budget") is None or wb > p["small_budget"]):
                ceiling = min(ceiling, p["cap"])
            out["basis"].append(f"{pct:.0%} of {BASE_LABEL[p['base']]} ({base:,.0f})"
                                + (f", at most {p['cap']:,.0f}" if p.get("cap") is not None else "") + f": {ceiling:,.0f}.")
    if ceiling is not None and shares:
        if shared:
            out["basis"].append(f"Less what shares the pool ({shared:,.0f}): {max(ceiling - shared, 0.0):,.0f} left for "
                                "producer fees.")
        ceiling = max(ceiling - shared, 0.0)
        if missing_shared:
            label = {"other_atl": "other qualifying ATL costs", "overheads": "overheads"}
            out["confirm"].append("The pool is shared with " + " and ".join(label[k] for k in missing_shared)
                                  + ": enter them, or the allowance is overstated.")
    out["ceiling"] = ceiling
    eligible = after_person if ceiling is None else min(after_person, ceiling)
    if c.get("related_pool"):
        rel = sum(x["eligible"] for x in lines if x["related"])
        b = _base(c["related_pool"]["base"], ctx, total)
        if rel and b is not None:
            rc = c["related_pool"]["pct"] * b
            if rel > rc:
                eligible -= rel - rc
                out["basis"].append(f"Related-party ATL limited to {c['related_pool']['pct']:.0%} of "
                                    f"{BASE_LABEL[c['related_pool']['base']]}: {rc:,.0f}.")
    return finish(max(eligible, 0.0))
