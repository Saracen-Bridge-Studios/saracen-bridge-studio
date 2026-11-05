"""Producer-fee allowance (1.2.0): Saracen Bridge's table of how much of a producer or EP fee counts as qualifying
expenditure for an incentive, sources checked 21 October 2026 (tools/producer_fees.json)."""
import importlib.util
import json
from pathlib import Path

import pytest

from studio import producerfee as P
from studio import refdata

ROOT = Path(__file__).resolve().parents[1]


def fee(amount, role="Producer", resident="unknown", paid_as="unknown", related=False):
    return {"role": role, "amount": amount, "resident": resident, "paid_as": paid_as, "related": related}


def test_the_table_is_built_from_its_script_and_links_real_programmes():
    spec = importlib.util.spec_from_file_location("bpf", ROOT / "scripts" / "build_producer_fees.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    assert (ROOT / "tools" / "producer_fees.json").read_text(encoding="utf-8") == m.build(), "run scripts/build_producer_fees.py"
    ids = {p["programme_id"] for p in refdata.all_programme_rules()}
    linked = [p for r in P.routes() for p in r["programmes"]]
    assert set(linked) <= ids and len(linked) == len(set(linked))
    assert P.table()["checked"] == "2026-10-21"
    assert {r["status"] for r in P.routes()} <= set(P.STATUS_LABEL)
    raw = json.dumps(P.table())
    assert "7793" not in raw and "Mobile" not in raw                 # Jon's signature and phone number stay out


def test_jons_hungarian_example():
    # "a €10 million film with a €5 million Hungarian budget has a €200,000 pooled producer-fee ceiling under the 4% rule
    #  — equivalent to 2% of the worldwide budget"
    r = P.assess("HU", {"fees": [fee(300000, "Executive producer")], "worldwide_budget": 10_000_000, "local_budget": 5_000_000})
    assert (r["ceiling"], r["eligible"], r["excluded"], r["share_of_budget"]) == (200000, 200000, 100000, 0.02)


def test_ireland_15_or_10_percent_and_the_unresolved_80_percent_boundary():
    base = {"fees": [fee(2_000_000)], "worldwide_budget": 10_000_000, "overheads": 0}
    assert P.assess("IE-481", base | {"local_spend": 9_000_000})["ceiling"] == 1_500_000
    assert P.assess("IE-481", base | {"local_spend": 7_000_000})["ceiling"] == 1_000_000
    r = P.assess("IE-481", base | {"local_spend": 8_000_000})
    assert r["eligible"] is None and "exactly 80%" in r["confirm"][0]
    # overheads share the same pool
    assert P.assess("IE-481", base | {"local_spend": 9_000_000, "overheads": 600_000})["eligible"] == 900_000


def test_dfff_i_bands():
    one = lambda budget, f: P.assess("DE-DFFF-I", {"fees": [fee(f)], "worldwide_budget": budget})
    assert one(280_000, 40_000)["eligible"] == 15_000
    assert one(450_000, 40_000)["eligible"] == 25_000
    assert one(2_000_000, 200_000)["ceiling"] == pytest.approx(0.05 * 1_800_000)       # 5% excluding the fee itself
    assert one(20_000_000, 900_000)["eligible"] == 250_000


def test_zero_unavailable_and_confirm_routes():
    assert P.assess("US-CA", {"fees": [fee(500_000)]})["eligible"] == 0
    assert P.assess("IT-INTL", {"fees": [fee(500_000)]})["excluded"] == 500_000
    mt = P.assess("US-MT", {"fees": [fee(100_000)]})
    assert mt["eligible"] == 0 and mt["status"] == "unavailable"
    fr = P.assess("FR-TRIP", {"fees": [fee(100_000)]})
    assert fr["eligible"] is None and fr["confirm"]                  # confirm is never uncapped


def test_per_person_rules_in_the_us():
    ga = P.assess("US-GA", {"fees": [fee(800_000, paid_as="salary"), fee(800_000, paid_as="loan-out")]})
    assert ga["eligible"] == 500_000 + 800_000
    sc = P.assess("US-SC", {"fees": [fee(1_000_000), fee(999_999)]})
    assert sc["eligible"] == 999_999                                  # $1m or more: the whole salary is out
    orr = P.assess("US-OR", {"fees": [fee(1_000_000), fee(1_000_001)]})
    assert orr["eligible"] == 1_000_000                               # more than $1m: the whole payment is out
    nc = P.assess("US-NC", {"fees": [fee(1_500_000)]})
    assert nc["eligible"] == 1_000_000
    tx = P.assess("US-TX", {"fees": [fee(1_200_000, resident="yes"), fee(400_000, resident="no")]})
    assert tx["eligible"] == 1_000_000
    held = P.assess("US-TX", {"fees": [fee(400_000)]})
    assert held["eligible"] is None and any("residency" in n for n in held["needs"])


def test_shared_atl_pools():
    ny = P.assess("US-NY", {"fees": [fee(400_000), fee(300_000), fee(200_000)], "local_spend": 5_000_000, "other_atl": 800_000})
    # three producers: only two count; 40% of the other qualified costs (5m - 0.9m - 0.8m), less the other ATL
    assert [x["eligible"] for x in ny["lines"]] == [400_000, 300_000, 0]
    assert ny["ceiling"] == pytest.approx(0.40 * 3_300_000 - 800_000)
    la = P.assess("US-LA", {"fees": [fee(3_500_000)], "local_spend": 10_000_000, "other_atl": 2_000_000})
    assert la["eligible"] == 2_000_000                                # no $3m individual cap any more; 40% pool less ATL
    au = P.assess("AU-PO", {"fees": [fee(3_000_000)], "worldwide_budget": 10_000_000, "other_atl": 0})
    assert au["eligible"] == 2_000_000
    doc = P.assess("AU-PO", {"fees": [fee(3_000_000)], "worldwide_budget": 10_000_000, "documentary": True})
    assert doc["eligible"] == 3_000_000                               # documentaries are exempt
    unknown_atl = P.assess("US-OK", {"fees": [fee(100_000)], "local_spend": 1_000_000})
    assert any("overstated" in x for x in unknown_atl["confirm"])


def test_canada():
    fed = P.assess("CA-FED", {"fees": [fee(900_000)], "bc": 6_000_000})
    assert fed["benchmark"] == 600_000 and fed["eligible"] is None and "support" in fed["confirm"][0]
    ns = P.assess("CA-NS", {"fees": [fee(700_000)], "incentive_rate": 0.25})
    assert ns["eligible"] == 600_000                                  # C$150,000 of incentive ÷ 25%
    assert P.assess("CA-NS", {"fees": [fee(700_000)]})["eligible"] is None
    yt_small = P.assess("CA-YT", {"fees": [fee(200_000)], "worldwide_budget": 450_000, "bc": 300_000, "overheads": 20_000})
    assert yt_small["eligible"] == pytest.approx(0.30 * 300_000 - 20_000)
    yt_big = P.assess("CA-YT", {"fees": [fee(5_000_000)], "worldwide_budget": 40_000_000, "bc": 30_000_000, "overheads": 0})
    assert yt_big["eligible"] == 2_000_000
    sk_doc = P.assess("CA-SK", {"fees": [fee(500_000)], "worldwide_budget": 2_000_000, "bc": 1_500_000, "documentary": True})
    assert sk_doc["eligible"] == pytest.approx(225_000)
    qc = P.assess("CA-QC", {"fees": [fee(300_000, resident="no")]})
    assert qc["eligible"] == 0


def test_malta_spain_navarra():
    mt = P.assess("MT-SVC", {"fees": [fee(150_000)], "local_spend": 400_000})
    assert mt["eligible"] == 80_000                                   # lower of 100,000 or 20% of Malta spend
    atl = P.assess("MT-ATL", {"fees": [fee(150_000)], "local_spend": 4_000_000})
    assert atl["eligible"] is None and any("1,200,000" in b for b in atl["basis"])
    assert P.assess("ES-ICAA", {"fees": [fee(500_000)], "worldwide_budget": 6_000_000})["eligible"] == 300_000
    nav = P.assess("ES-NAV-65", {"fees": [fee(150_000)], "worldwide_budget": 800_000})
    assert nav["eligible"] == 100_000                                 # the higher of 10% (80,000) or 100,000
    assert P.for_programme("ESP-NAV-FOR")["status"] == "confirm"


def test_missing_inputs_say_what_they_need():
    r = P.assess("HU", {"fees": [fee(100_000)]})
    assert r["eligible"] is None and r["needs"]
    assert P.assess("HU", {"fees": []})["needs"] == ["Enter the producer and executive-producer fees."]


# ------------------------------------------------------------------ through the Studio's API
@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("STUDIO_HOME", str(tmp_path / "home"))
    from fastapi.testclient import TestClient
    from studio.server import app
    return TestClient(app)


def test_the_route_list_and_a_check(client):
    t = client.get("/api/tools/incentives/producer-fees").json()
    assert t["checked"] == "2026-10-21" and len(t["routes"]) == len(P.routes()) and "calc" not in t["routes"][0]
    r = client.post("/api/tools/incentives/producer-fee", json={"route": "HU", "fees": [fee(300000)],
                                                                 "worldwide_budget": 10_000_000, "local_budget": 5_000_000}).json()
    assert r["eligible"] == 200_000
    assert client.post("/api/tools/incentives/producer-fee", json={"route": "XX", "fees": []}).status_code == 400


def test_fees_above_the_allowance_stay_out_of_the_incentive_base(client):
    routes = [{"programme_id": "HUN-FILM", "qualifying_spend": 5_000_000, "project_cost": 10_000_000, "eligibility": "Eligible",
               "fees_in_spend": True},
              {"programme_id": "HUN-FILM", "qualifying_spend": 5_000_000, "project_cost": 10_000_000, "eligibility": "Eligible"}]
    pf = {"fees": [fee(300_000, "Executive producer")]}
    with_fees, without = client.post("/api/tools/incentives/calc", json={"routes": routes, "producer_fees": pf, "save": False}).json()
    assert with_fees["producer_fee"]["eligible"] == 200_000 and with_fees["producer_fee"]["excluded"] == 100_000
    assert with_fees["qualifying_spend"] == 4_900_000                      # 100,000 of the fee kept out
    assert any("kept out of the qualifying spend" in x for x in with_fees["reasons"])
    assert without["qualifying_spend"] == 5_000_000                        # fees not in that spend: untouched
    assert with_fees["gross_benefit"] < without["gross_benefit"]


def test_unsettled_allowance_makes_the_route_preliminary(client):
    routes = [{"programme_id": "FRA-TRIP", "qualifying_spend": 5_000_000, "project_cost": 10_000_000, "eligibility": "Eligible",
               "fees_in_spend": True}]
    res = client.post("/api/tools/incentives/calc", json={"routes": routes, "producer_fees": {"fees": [fee(200_000)]},
                                                          "save": False}).json()[0]
    assert res["gate"] == "PRELIMINARY" and res["producer_fee"]["status"] == "confirm"
    assert any("allowance isn't settled" in x for x in res["reasons"])
    bel = client.post("/api/tools/incentives/calc", json={"routes": [dict(routes[0], programme_id="BEL-TAX-SHELTER")],
                                                          "producer_fees": {"fees": [fee(200_000)]}, "save": False}).json()[0]
    assert bel["producer_fee"]["status"] == "uncovered"


def test_a_route_shows_its_programmes_currency(client):
    res = client.post("/api/tools/incentives/calc", json={"routes": [{"programme_id": "HUN-FILM", "qualifying_spend": 5_000_000,
        "project_cost": 10_000_000, "eligibility": "Eligible", "fees_in_spend": True}], "producer_fees": {"fees": [fee(300_000)]},
        "save": False}).json()[0]
    assert res["producer_fee"]["currency"] == res["currency"] == "HUF"
