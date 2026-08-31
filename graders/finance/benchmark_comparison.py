"""Composite deterministic grader for the Benchmark Comparison skill.

Reuses the full generic finance grader set from `graders/finance/` --
benchmark consistency, temporal consistency, data provenance, portfolio
coverage, numeric claim grounding -- since this skill's entire purpose is
comparing portfolio positioning against the assigned benchmark (Milestone 8
exit criterion: the same building blocks used by Performance Attribution
and Portfolio Overview are reused here unchanged).
"""

from .benchmark_consistency import grade as benchmark_consistency
from .data_provenance import grade as data_provenance
from .numeric_claim_grounding import grade as numeric_grounding
from .portfolio_coverage import grade as portfolio_coverage
from .temporal_consistency import grade as temporal_consistency


def grade(evidence: dict) -> dict:
    """Return component metrics for authoritative benchmark-comparison evidence."""
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
