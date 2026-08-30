from graders.finance.attribution_reconciliation import grade as recon
from graders.finance.benchmark_consistency import grade as benchmark
from graders.finance.performance_attribution import grade as attribution_grade
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
