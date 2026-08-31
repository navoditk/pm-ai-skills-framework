"""Composite deterministic grader for the Risk Explanation skill.

Reuses the same generic finance graders as
`graders/finance/performance_attribution.py` and
`graders/finance/portfolio_overview.py` -- temporal consistency, data
provenance, portfolio coverage, numeric claim grounding -- proving they are
shared, skill-agnostic building blocks (Milestone 8 exit criterion). This
skill omits `benchmark_consistency`: factor exposure and scenario impact are
evaluated against the portfolio's own authoritative risk output, not a
benchmark comparison.
"""

from .data_provenance import grade as data_provenance
from .numeric_claim_grounding import grade as numeric_grounding
from .portfolio_coverage import grade as portfolio_coverage
from .temporal_consistency import grade as temporal_consistency


def grade(evidence: dict) -> dict:
    """Return component metrics for authoritative risk-explanation evidence."""
    metrics = {
        "temporal_consistency": temporal_consistency(
            evidence.get("requested_as_of"), evidence.get("observed_as_of_values", [])
        )["score"],
        "data_provenance": data_provenance(
            set(evidence.get("allowed_sources", [])),
            set(evidence.get("observed_sources", [])),
        )["score"],
        "portfolio_coverage": portfolio_coverage(
            set(evidence.get("expected_position_ids", [])),
            set(evidence.get("observed_position_ids", [])),
        )["score"],
        "numeric_claim_grounding": numeric_grounding(
            evidence.get("claims", []), evidence.get("authoritative_values", [])
        )["score"],
    }
    return {
        "metrics": metrics,
        "score": sum(metrics.values()) / len(metrics),
        "passed": all(value == 1.0 for value in metrics.values()),
    }
