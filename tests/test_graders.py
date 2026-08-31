from graders.finance.attribution_reconciliation import grade as recon
from graders.finance.benchmark_comparison import grade as benchmark_comparison_grade
from graders.finance.benchmark_consistency import grade as benchmark
from graders.finance.concentration_analysis import grade as concentration_analysis_grade
from graders.finance.exposure_analysis import grade as exposure_analysis_grade
from graders.finance.liquidity_analysis import grade as liquidity_analysis_grade
from graders.finance.market_move_explanation import grade as market_move_explanation_grade
from graders.finance.performance_attribution import grade as attribution_grade
from graders.finance.pm_commentary_generation import grade as pm_commentary_generation_grade
from graders.finance.portfolio_change_analysis import grade as portfolio_change_analysis_grade
from graders.finance.portfolio_overview import grade as portfolio_overview_grade
from graders.finance.position_investigation import grade as position_investigation_grade
from graders.finance.risk_explanation import grade as risk_explanation_grade
from graders.finance.scenario_analysis import grade as scenario_analysis_grade
from graders.finance.temporal_consistency import grade as temporal


def test_reconciliation_passes():
    r = recon(-0.0021, [-0.0012, -0.0005, -0.0003, -0.0001], tolerance=1e-9)
    assert r["score"] == 1.0

def test_temporal_detects_mismatch():
    r = temporal("2026-08-25", ["2026-08-25", "2026-08-22"])
    assert r["score"] == 0.0

def test_benchmark():
    assert benchmark("SPX", "SPX")["score"] == 1.0


def test_performance_attribution_domain_grader_passes_authoritative_evidence():
    result = attribution_grade(
        {
            "relative_return": -0.0021,
            "contributions": [-0.0012, -0.0005, -0.0003, -0.0001],
            "expected_benchmark": "SPX",
            "observed_benchmark": "SPX",
            "requested_as_of": "2026-08-25",
            "observed_as_of_values": ["2026-08-25", "2026-08-25"],
            "allowed_sources": ["synthetic.attribution"],
            "observed_sources": ["synthetic.attribution"],
            "expected_position_ids": ["AAPL", "MSFT", "JPM", "ES_FUT"],
            "observed_position_ids": ["AAPL", "MSFT", "JPM", "ES_FUT"],
            "claims": [-0.0021, -0.0012],
            "authoritative_values": [-0.0021, -0.0012],
        }
    )
    assert result["score"] == 1.0
    assert all(value == 1.0 for value in result["metrics"].values())


def test_performance_attribution_domain_grader_treats_no_positions_expected_as_not_applicable():
    """Regression test for a real bug found 2026-08-30: a case whose prompt
    never asks about positions (e.g. "show ABC's absolute return, benchmark
    return, and active return") should not be penalized on portfolio_coverage
    just because the agent correctly never enumerated positions either.
    """
    result = attribution_grade(
        {
            "relative_return": -0.0021,
            "contributions": [-0.0012, -0.0005, -0.0003, -0.0001],
            "expected_benchmark": "SPX",
            "observed_benchmark": "SPX",
            "requested_as_of": "2026-08-25",
            "observed_as_of_values": ["2026-08-25"],
            "allowed_sources": ["synthetic.attribution"],
            "observed_sources": ["synthetic.attribution"],
            "expected_position_ids": [],
            "observed_position_ids": [],
            "claims": [-0.0021, -0.0012],
            "authoritative_values": [-0.0021, -0.0012],
        }
    )
    assert result["metrics"]["portfolio_coverage"] == 1.0
    assert result["score"] == 1.0


def test_portfolio_overview_domain_grader_passes_authoritative_evidence():
    """Proves benchmark_consistency/temporal_consistency/data_provenance/
    portfolio_coverage/numeric_claim_grounding are genuinely reusable across
    skills (Milestone 8 exit criterion), not bespoke to performance-attribution.
    """
    result = portfolio_overview_grade(
        {
            "expected_benchmark": "SPX",
            "observed_benchmark": "SPX",
            "requested_as_of": "2026-08-25",
            "observed_as_of_values": ["2026-08-25", "2026-08-25"],
            "allowed_sources": ["synthetic.portfolio"],
            "observed_sources": ["synthetic.portfolio"],
            "expected_position_ids": ["AAPL", "MSFT", "JPM", "ES_FUT"],
            "observed_position_ids": ["AAPL", "MSFT", "JPM", "ES_FUT"],
            "claims": [0.0042, 0.0063],
            "authoritative_values": [0.0042, 0.0063],
        }
    )
    assert result["score"] == 1.0
    assert all(value == 1.0 for value in result["metrics"].values())


def test_portfolio_overview_domain_grader_detects_missing_derivative_coverage():
    result = portfolio_overview_grade(
        {
            "expected_benchmark": "SPX",
            "observed_benchmark": "SPX",
            "requested_as_of": "2026-08-25",
            "observed_as_of_values": ["2026-08-25"],
            "allowed_sources": ["synthetic.portfolio"],
            "observed_sources": ["synthetic.portfolio"],
            "expected_position_ids": ["AAPL", "MSFT", "JPM", "ES_FUT"],
            "observed_position_ids": ["AAPL", "MSFT", "JPM"],
            "claims": [0.0042],
            "authoritative_values": [0.0042],
        }
    )
    assert result["metrics"]["portfolio_coverage"] < 1.0
    assert result["passed"] is False


def test_risk_explanation_domain_grader_passes_authoritative_evidence():
    result = risk_explanation_grade(
        {
            "requested_as_of": "2026-08-25",
            "observed_as_of_values": ["2026-08-25"],
            "allowed_sources": ["synthetic.factor_risk"],
            "observed_sources": ["synthetic.factor_risk"],
            "expected_position_ids": [],
            "observed_position_ids": [],
            "claims": [0.18, 0.82, -0.04],
            "authoritative_values": [0.18, 0.82, -0.04],
        }
    )
    assert result["score"] == 1.0
    assert all(value == 1.0 for value in result["metrics"].values())


def test_risk_explanation_domain_grader_detects_unauthorized_source():
    result = risk_explanation_grade(
        {
            "requested_as_of": "2026-08-25",
            "observed_as_of_values": ["2026-08-25"],
            "allowed_sources": ["synthetic.factor_risk"],
            "observed_sources": ["synthetic.factor_risk", "web_search"],
            "expected_position_ids": [],
            "observed_position_ids": [],
            "claims": [0.18],
            "authoritative_values": [0.18],
        }
    )
    assert result["metrics"]["data_provenance"] == 0.0
    assert result["passed"] is False


# Milestone 7 structural completion (2026-08-30): one passing-evidence test per
# remaining skill, proving each composite grader wires the shared Milestone 8
# building blocks correctly, same pattern as the three vertical-slice skills
# above.


def test_exposure_analysis_domain_grader_passes_authoritative_evidence():
    result = exposure_analysis_grade(
        {
            "requested_as_of": "2026-08-25",
            "observed_as_of_values": ["2026-08-25"],
            "allowed_sources": ["synthetic.exposure"],
            "observed_sources": ["synthetic.exposure"],
            "expected_position_ids": ["AAPL", "MSFT", "JPM", "ES_FUT"],
            "observed_position_ids": ["AAPL", "MSFT", "JPM", "ES_FUT"],
            "claims": [0.18, 0.82],
            "authoritative_values": [0.18, 0.82],
        }
    )
    assert result["score"] == 1.0
    assert all(value == 1.0 for value in result["metrics"].values())


def test_benchmark_comparison_domain_grader_detects_benchmark_mismatch():
    result = benchmark_comparison_grade(
        {
            "expected_benchmark": "SPX",
            "observed_benchmark": "RUSSELL2000",
            "requested_as_of": "2026-08-25",
            "observed_as_of_values": ["2026-08-25"],
            "allowed_sources": ["synthetic.portfolio", "synthetic.benchmark"],
            "observed_sources": ["synthetic.portfolio", "synthetic.benchmark"],
            "expected_position_ids": ["AAPL", "MSFT"],
            "observed_position_ids": ["AAPL", "MSFT"],
            "claims": [0.0042],
            "authoritative_values": [0.0042],
        }
    )
    assert result["metrics"]["benchmark_consistency"] == 0.0
    assert result["passed"] is False


def test_position_investigation_domain_grader_passes_authoritative_evidence():
    result = position_investigation_grade(
        {
            "requested_as_of": "2026-08-25",
            "observed_as_of_values": ["2026-08-25"],
            "allowed_sources": ["synthetic.market", "synthetic.portfolio"],
            "observed_sources": ["synthetic.market", "synthetic.portfolio"],
            "claims": [0.12],
            "authoritative_values": [0.12],
        }
    )
    assert result["score"] == 1.0
    assert all(value == 1.0 for value in result["metrics"].values())


def test_scenario_analysis_domain_grader_passes_authoritative_evidence():
    result = scenario_analysis_grade(
        {
            "requested_as_of": "2026-08-25",
            "observed_as_of_values": ["2026-08-25"],
            "allowed_sources": ["synthetic.scenario"],
            "observed_sources": ["synthetic.scenario"],
            "expected_position_ids": ["AAPL", "MSFT", "JPM", "ES_FUT"],
            "observed_position_ids": ["AAPL", "MSFT", "JPM", "ES_FUT"],
            "claims": [-0.012, -0.082],
            "authoritative_values": [-0.012, -0.082],
        }
    )
    assert result["score"] == 1.0
    assert all(value == 1.0 for value in result["metrics"].values())


def test_market_move_explanation_domain_grader_detects_stale_price_date():
    result = market_move_explanation_grade(
        {
            "requested_as_of": "2026-08-25",
            "observed_as_of_values": ["2026-08-20"],
            "allowed_sources": ["synthetic.market"],
            "observed_sources": ["synthetic.market"],
            "claims": [101.5],
            "authoritative_values": [101.5],
        }
    )
    assert result["metrics"]["temporal_consistency"] == 0.0
    assert result["passed"] is False


def test_liquidity_analysis_domain_grader_passes_authoritative_evidence():
    result = liquidity_analysis_grade(
        {
            "requested_as_of": "2026-08-25",
            "observed_as_of_values": ["2026-08-25"],
            "allowed_sources": ["synthetic.portfolio"],
            "observed_sources": ["synthetic.portfolio"],
            "expected_position_ids": ["AAPL", "MSFT", "JPM", "ES_FUT"],
            "observed_position_ids": ["AAPL", "MSFT", "JPM", "ES_FUT"],
            "claims": [-0.05],
            "authoritative_values": [-0.05],
        }
    )
    assert result["score"] == 1.0
    assert all(value == 1.0 for value in result["metrics"].values())


def test_portfolio_change_analysis_domain_grader_detects_conflated_dates():
    """A change-analysis answer that reuses one date for both snapshots
    instead of the two distinct as-of dates it was given should fail
    temporal_consistency."""
    result = portfolio_change_analysis_grade(
        {
            "requested_as_of": "2026-08-25",
            "observed_as_of_values": ["2026-07-25"],
            "allowed_sources": ["synthetic.portfolio"],
            "observed_sources": ["synthetic.portfolio"],
            "expected_position_ids": ["AAPL", "MSFT"],
            "observed_position_ids": ["AAPL", "MSFT"],
            "claims": [0.0042],
            "authoritative_values": [0.0042],
        }
    )
    assert result["metrics"]["temporal_consistency"] == 0.0
    assert result["passed"] is False


def test_concentration_analysis_domain_grader_passes_authoritative_evidence():
    result = concentration_analysis_grade(
        {
            "expected_benchmark": "SPX",
            "observed_benchmark": "SPX",
            "requested_as_of": "2026-08-25",
            "observed_as_of_values": ["2026-08-25"],
            "allowed_sources": ["synthetic.portfolio", "synthetic.benchmark"],
            "observed_sources": ["synthetic.portfolio", "synthetic.benchmark"],
            "expected_position_ids": ["AAPL", "MSFT", "JPM", "ES_FUT"],
            "observed_position_ids": ["AAPL", "MSFT", "JPM", "ES_FUT"],
            "claims": [0.12],
            "authoritative_values": [0.12],
        }
    )
    assert result["score"] == 1.0
    assert all(value == 1.0 for value in result["metrics"].values())


def test_pm_commentary_generation_domain_grader_detects_fabricated_claim():
    result = pm_commentary_generation_grade(
        {
            "expected_benchmark": "SPX",
            "observed_benchmark": "SPX",
            "requested_as_of": "2026-08-25",
            "observed_as_of_values": ["2026-08-25"],
            "allowed_sources": ["synthetic.portfolio"],
            "observed_sources": ["synthetic.portfolio"],
            "expected_position_ids": ["AAPL", "MSFT"],
            "observed_position_ids": ["AAPL", "MSFT"],
            "claims": [0.0099],
            "authoritative_values": [0.0042],
        }
    )
    assert result["metrics"]["numeric_claim_grounding"] < 1.0
    assert result["passed"] is False
