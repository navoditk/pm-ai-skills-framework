"""Composite deterministic grader for the Concentration Analysis skill.

Reuses the full generic finance grader set from `graders/finance/` --
benchmark consistency, temporal consistency, data provenance, portfolio
coverage, numeric claim grounding -- since material concentration is
inherently relative to the assigned benchmark's own weights (Milestone 8
exit criterion).
"""

from .benchmark_consistency import grade as benchmark_consistency
from .data_provenance import grade as data_provenance
from .numeric_claim_grounding import grade as numeric_grounding
from .portfolio_coverage import grade as portfolio_coverage
from .temporal_consistency import grade as temporal_consistency


def grade(evidence: dict) -> dict:
    """Return component metrics for authoritative concentration-analysis evidence."""
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
