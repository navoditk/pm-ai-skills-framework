"""Composite deterministic grader for the Portfolio Overview skill.

Reuses the same generic finance graders as
`graders/finance/performance_attribution.py` -- benchmark consistency,
temporal consistency, data provenance, portfolio coverage, numeric claim
grounding -- proving they are shared, skill-agnostic building blocks rather
than bespoke per-skill code (Milestone 8 exit criterion). This skill does
not do return-component reconciliation, so it omits
`attribution_reconciliation`, which is specific to attribution's
sector-contribution math.
"""

from .benchmark_consistency import grade as benchmark_consistency
from .data_provenance import grade as data_provenance
from .numeric_claim_grounding import grade as numeric_grounding
from .portfolio_coverage import grade as portfolio_coverage
from .temporal_consistency import grade as temporal_consistency


def grade(evidence: dict) -> dict:
    """Return component metrics for authoritative portfolio overview evidence."""
    metrics = {
        "benchmark_consistency": benchmark_consistency(
            evidence.get("expected_benchmark"), evidence.get("observed_benchmark")
        )["score"],
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
