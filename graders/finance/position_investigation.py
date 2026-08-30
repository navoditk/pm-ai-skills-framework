"""Composite deterministic grader for the Position Investigation skill.

Reuses temporal consistency, data provenance, and numeric claim grounding
from `graders/finance/` (Milestone 8 exit criterion). This skill omits
`benchmark_consistency` (a single-position investigation is not a benchmark
comparison) and `portfolio_coverage` (the unit under evaluation is one
position's identifiers/context, not the full portfolio composition set).
"""

from .data_provenance import grade as data_provenance
from .numeric_claim_grounding import grade as numeric_grounding
from .temporal_consistency import grade as temporal_consistency


def grade(evidence: dict) -> dict:
    """Return component metrics for authoritative position-investigation evidence."""
    metrics = {
        "temporal_consistency": temporal_consistency(
            evidence.get("requested_as_of"), evidence.get("observed_as_of_values", [])
        )["score"],
        "data_provenance": data_provenance(
            set(evidence.get("allowed_sources", [])),
            set(evidence.get("observed_sources", [])),
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
