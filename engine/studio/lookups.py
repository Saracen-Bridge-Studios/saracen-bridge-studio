"""Read-only searches over Jon's reference data: talent, brands, crew/cast/non-labour rates, programmes."""
from __future__ import annotations

import unicodedata

from . import refdata


def _like(q: str) -> str:
    return f"%{(q or '').strip()}%"


def fold(text: str) -> str:
    """'Timothée' -> 'timothee': search ignores case and accents."""
    return "".join(c for c in unicodedata.normalize("NFKD", text or "") if not unicodedata.combining(c)).casefold()


def _rank(rows: list[dict], key: str, q: str, limit: int) -> list[dict]:
    """Every word typed must appear in the name. Names starting with the query come first, then names with a word
    starting with it, then the rest; alphabetical within each. 'chris' -> Chris Evans … Christopher Walken."""
    want = fold(q).split()
    if not want:
        return rows[:limit]
    whole = " ".join(want)
    hits = []
    for r in rows:
        name = fold(r[key])
        if all(w in name for w in want):
            words = name.replace("-", " ").split()
            tier = 0 if name.startswith(whole) else 1 if any(x.startswith(want[0]) for x in words) else 2
            hits.append((tier, name, r))
    hits.sort(key=lambda h: (h[0], h[1]))
    return [h[2] for h in hits[:limit]]


def actors(q: str = "", limit: int = 50) -> list[dict]:
    rows = refdata.rows("""SELECT actor, commercial_tier, sales_role, primary_market, approx_playing_age,
        primary_genres, confidence, last_reviewed FROM talent_actors ORDER BY actor""")
    return _rank(rows, "actor", q, limit)


def actor(name: str) -> dict | None:
    """One actor's full commercial profile from Jon's Actor DB (no personal contact or representation data is held)."""
    rows = refdata.rows("""SELECT actor, approx_playing_age, primary_market, english_language_fit, commercial_tier,
        sales_role, composite_cast_value, sales_influence_class, lead_carry, supporting_value, international_presales,
        territory_breadth, recent_momentum, awards_prestige, global_theatrical, streaming_platform, benchmark_films,
        indicative_cash_fee_low_usd, indicative_cash_fee_high_usd, minimum_sensible_budget_usd, optimal_budget_floor_usd,
        primary_genres, package_risk_notes, confidence, last_reviewed, primary_source FROM talent_actors WHERE actor = ? LIMIT 1""", name)
    return rows[0] if rows else None


def director(director_id: str) -> dict | None:
    """One director's commercial profile and fee bands from Jon's Director DB. Nationality, representation and
    reputational notes are left out (personal data; register S-10)."""
    rows = refdata.rows("""SELECT d.director_id, d.director_name, d.primary_classification, d.career_stage, d.primary_genre,
        d.secondary_genres, d.proven_minimum_budget_usd, d.proven_maximum_budget_usd, d.preferred_production_model,
        d.primary_working_territories, d.current_trajectory, d.studio_platform_relationships, d.completion_bonding_notes,
        d.overall_data_confidence, d.last_reviewed, f.commercial_tier, f.reference_production_budget, f.fee_low, f.fee_mid,
        f.fee_high, f.indicative_backend_deal_shape, f.fee_status, f.confidence AS fee_confidence, f.source_limitation_note,
        d.next_review_due FROM talent_directors d
        LEFT JOIN talent_director_fees f ON f.director_id = d.director_id WHERE d.director_id = ? LIMIT 1""", director_id)
    return rows[0] if rows else None


def directors(q: str = "", limit: int = 50) -> list[dict]:
    rows = refdata.rows("""SELECT d.director_id, d.director_name, d.career_stage, d.primary_genre,
        f.commercial_tier, f.fee_low, f.fee_mid, f.fee_high, f.confidence FROM talent_directors d
        LEFT JOIN talent_director_fees f ON f.director_id = d.director_id ORDER BY d.director_name""")
    return _rank(rows, "director_name", q, limit)


def brands(q: str = "", category: str = "", limit: int = 120) -> list[dict]:
    return refdata.rows("""SELECT b.brand_id, b.brand_name, b.parent_company, b.category, b.subcategory, b.hq_country,
        b.priority, e.evidence_statement, e.evidence_year FROM brand_accounts b
        LEFT JOIN brand_film_evidence e ON e.brand_id = b.brand_id
        WHERE (b.brand_name LIKE ? OR b.parent_company LIKE ?) AND b.category LIKE ?
        ORDER BY b.brand_name LIMIT ?""", _like(q), _like(q), _like(category), limit)


def brands_by_id(ids: list[str]) -> list[dict]:
    """The given brands, in the order given (a shortlist keeps the order brands were picked in); unknown ids are dropped."""
    ids = [str(i) for i in ids if i][:500]
    if not ids:
        return []
    found = {r["brand_id"]: r for r in refdata.rows(f"""SELECT b.brand_id, b.brand_name, b.parent_company, b.category, b.subcategory,
        b.hq_country, b.priority, e.evidence_statement, e.evidence_year FROM brand_accounts b
        LEFT JOIN brand_film_evidence e ON e.brand_id = b.brand_id
        WHERE b.brand_id IN ({",".join("?" * len(ids))})""", *ids)}
    return [found[i] for i in dict.fromkeys(ids) if i in found]


def rate_jurisdictions() -> list[str]:
    return [r["jurisdiction"] for r in refdata.rows("SELECT DISTINCT jurisdiction FROM rate_crew ORDER BY 1")]


def crew_rates(jurisdiction: str, q: str = "", production_type: str = "", limit: int = 400) -> dict:
    """Jon's rate cards come in two shapes: Spain has an official minimum plus market low/base/high bands; the other
    jurisdictions use four experience tiers. Both are returned as four day columns plus a week figure, labelled."""
    raw = refdata.rows("""SELECT production_type, department, english_budget_role, local_official_role, rate_status, currency,
        tier_1_day, tier_2_day, tier_3_day, tier_4_day, tier_1_week, official_day, official_week,
        market_low_day, market_base_day, market_high_day, validation_status, notes, source
        FROM rate_crew WHERE jurisdiction = ? AND production_type LIKE ?
        AND (english_budget_role LIKE ? OR department LIKE ? OR local_official_role LIKE ?)
        ORDER BY source_row LIMIT ?""", jurisdiction, production_type or "%", _like(q), _like(q), _like(q), limit)
    types = [r["production_type"] for r in refdata.rows(
        "SELECT DISTINCT production_type FROM rate_crew WHERE jurisdiction = ? ORDER BY MIN(source_row) OVER (PARTITION BY production_type)", jurisdiction)]
    official = any(r["official_day"] is not None for r in raw)
    out = []
    for r in raw:
        if official:
            day, week = [r["official_day"], r["market_low_day"], r["market_base_day"], r["market_high_day"]], r["official_week"]
        else:
            day, week = [r["tier_1_day"], r["tier_2_day"], r["tier_3_day"], r["tier_4_day"]], r["tier_1_week"]
        negotiated = "negotiat" in (r["rate_status"] or "").lower() and not any(day) and not week
        if negotiated:              # Jon's cards hold 0 for negotiated roles; 0 is not a rate
            day, week = [None] * 4, None
        out.append({"negotiated": negotiated, "role": r["english_budget_role"], "local_role": r["local_official_role"], "department": r["department"],
                    "production_type": r["production_type"], "currency": r["currency"],
                    "d1": day[0], "d2": day[1], "d3": day[2], "d4": day[3], "week": week,
                    "rate_status": r["rate_status"], "validation_status": r["validation_status"],
                    "notes": r["notes"], "source": r["source"]})
    labels = (["Official min / day", "Market low / day", "Market base / day", "Market high / day", "Official / week"] if official
              else ["Tier 1 / day", "Tier 2 / day", "Tier 3 / day", "Tier 4 / day", "Tier 1 / week"])
    return {"basis": "official_plus_market" if official else "four_tier", "labels": labels, "types": types, "rows": out}


def programmes(country: str = "", include_unavailable: bool = False) -> list[dict]:
    rows = refdata.rows("""SELECT programme_id, programme_name, jurisdiction, workstream, programme_currency, instrument,
        selectable, availability_status, calculation_method, rate_base, last_verified FROM inc_programme_rules
        WHERE programme_id NOT LIKE 'TEST%' AND (jurisdiction LIKE ? OR programme_id LIKE ?) ORDER BY programme_id""",
                        _like(country), _like(country))
    return rows if include_unavailable else [r for r in rows if r["availability_status"] == "Active"]
