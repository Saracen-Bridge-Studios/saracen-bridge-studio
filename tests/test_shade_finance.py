"""SHADE (real project) known-answer tests.

Oracle: the original SHADE v2 workbook recalculated by LibreOffice (data/oracle). The engine
must reproduce the workbook's correct figures and catch the double count the workbook contains.
"""
from pathlib import Path

import openpyxl
import pytest

from studio import finance, incentive

ORACLE = Path(__file__).resolve().parents[1] / "data" / "oracle" / "SHADE_Spain_Finance_Model_NonStop_50pct_Guarantee_v2.xlsx"


@pytest.fixture(scope="module")
def wb():
    return openpyxl.load_workbook(ORACLE, data_only=True)


def test_spanish_incentive_matches_workbook(wb):
    eligible_base = wb["Tax Incentive"]["B7"].value
    gross = wb["Inputs"]["B13"].value
    r = incentive.calculate("ESP-NAT-FOR", eligible_base, project_cost=gross, eligibility="Eligible")
    assert r.gross_benefit == pytest.approx(wb["Tax Incentive"]["B14"].value, abs=0.01)   # €1,617,019.86


def _shade_sources(wb):
    inp = wb["Inputs"]
    pkg = finance.size_package(inp["B13"].value, 0.5, wb["Tax Incentive"]["B14"].value)
    return inp["B13"].value, pkg, [
        finance.Source("mg", "LevelK MG", inp["B23"].value, "Draft / conditional"),
        finance.Source("facility", "Non-Stop incentive facility", pkg["facility"], "User instruction / to document", parent="nonstop"),
        finance.Source("inkind", "Non-Stop in-kind deferred equity", pkg["in_kind"], "User instruction / to document", cash=False, parent="nonstop"),
    ]


def test_package_sizing_matches_workbook(wb):
    _, pkg, _ = _shade_sources(wb)
    assert pkg["package"] == pytest.approx(wb["Inputs"]["B24"].value, abs=0.01)
    assert pkg["facility"] == pytest.approx(wb["Inputs"]["B25"].value, abs=0.01)
    assert pkg["in_kind"] == pytest.approx(wb["Inputs"]["B26"].value, abs=0.01)


def test_correct_residual_debt(wb):
    gross, _, sources = _shade_sources(wb)
    assert finance.residual_debt(gross, sources) == pytest.approx(3_168_657.42, abs=0.01)


def test_workbook_debt_cell_is_wrong(wb):
    """Inputs!B29 shows €0 because B24 (package total) is summed with its components."""
    assert wb["Inputs"]["B29"].value == 0


def test_double_count_is_caught(wb):
    gross, pkg, sources = _shade_sources(wb)
    bad = sources + [finance.Source("nonstop", "Non-Stop package total", pkg["package"], "User instruction / to document")]
    assert finance.double_count_errors(bad), "engine must flag a package counted with its components"
    assert not finance.double_count_errors(sources)


def test_plan_reconciles_with_debt(wb):
    gross, _, sources = _shade_sources(wb)
    debt = finance.residual_debt(gross, sources)
    plan = finance.reconcile(gross, sources + [finance.Source("senior", "Senior / gap debt", debt, "Missing", is_debt=True)])
    assert plan.gap == pytest.approx(0, abs=0.01)
    assert plan.debt_pct == pytest.approx(0.3533, abs=0.0001)
    assert not plan.errors
