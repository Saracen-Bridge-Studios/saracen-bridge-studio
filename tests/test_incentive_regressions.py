"""Jon's own Stage 2 v1.1 Audit Regression suite (R01–R12), run against the code engine."""
import pytest

from studio import incentive, refdata

EXPECTED = {r["test_id"]: r for r in refdata.rows("SELECT * FROM inc_audit_regression")}


def test_suite_present():
    assert len(EXPECTED) == 12


def test_r01_spain_tiered_eur6m():
    r = incentive.calculate("ESP-NAT-FOR", 6_000_000, project_cost=10_000_000, eligibility="Eligible")
    assert r.gross_benefit == pytest.approx(EXPECTED["R01"]["expected"], abs=1)
    assert r.gate == "PASS"


def test_r02_r03_uk_iftc_gross_and_net():
    r = incentive.calculate("GBR-IFTC", 6_000_000, project_cost=10_000_000, eligibility="Eligible")
    assert r.gross_benefit == pytest.approx(EXPECTED["R02"]["expected"], abs=1)
    assert r.net_after_tax == pytest.approx(EXPECTED["R03"]["expected"], abs=1)


def test_r04_czech_base_cap_not_benefit_cap():
    r = incentive.calculate("CZE-PROD", 600_000_000, eligibility="Eligible")
    assert r.eligible_base == 450_000_000
    assert r.gross_benefit == pytest.approx(EXPECTED["R04"]["expected"], abs=1)


def test_r05_enhancement_without_parent_fails():
    r = incentive.calculate("CAN-BC-PSTC-DAVE", 1_000_000, eligibility="Eligible")
    assert r.gate == EXPECTED["R05"]["expected"] == "FAIL"


def test_r05_enhancement_with_parent_passes_gate():
    r = incentive.calculate("CAN-BC-PSTC-DAVE", 1_000_000, eligibility="Eligible",
                            selected={"CAN-BC-PSTC-DAVE", "CAN-BC-PSTC"})
    assert r.gate != "FAIL"


def test_r06_alternative_elections_fail_together():
    both = {"CAN-MB-ALL", "CAN-MB-LAB"}
    for pid in both:
        assert incentive.calculate(pid, 1_000_000, eligibility="Eligible", selected=both).gate == "FAIL"


def test_r07_unknown_stays_preliminary():
    r = incentive.calculate("ESP-NAT-FOR", 6_000_000, project_cost=None, eligibility="Unknown")
    assert r.gate == EXPECTED["R07"]["expected"] == "PRELIMINARY"
    assert incentive.calculate("ESP-NAT-FOR", None, eligibility="Eligible").gross_benefit is None


@pytest.mark.parametrize("tid,statuses", [("R08", {"Closed"}), ("R09", {"Limited", "Time-limited"})])
def test_r08_r09_default_selector_excludes(tid, statuses):
    n = sum(1 for r in incentive.default_selectable() if r["availability_status"] in statuses)
    assert n == EXPECTED[tid]["expected"] == 0


def test_r10_default_selector_excludes_test_records():
    assert not [r for r in incentive.default_selectable() if r["programme_id"].startswith("TEST")]


def test_r11_gbp_cross_rate():
    assert refdata.fx_usd_per_unit("GBP") == pytest.approx(EXPECTED["R11"]["expected"], abs=1e-9)


def test_r12_live_programme_rules():
    assert len(incentive.live_programmes()) == EXPECTED["R12"]["expected"] == 76
