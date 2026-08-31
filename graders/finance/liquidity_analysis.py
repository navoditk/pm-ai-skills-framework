"""Composite deterministic grader for the Liquidity Analysis skill.

Reuses temporal consistency, data provenance, portfolio coverage, and
numeric claim grounding from `graders/finance/` (Milestone 8 exit
criterion). This skill omits `benchmark_consistency` (liquidity risk is
evaluated against the portfolio's own positions, not a benchmark
comparison).

Note: the synthetic data pipeline has no dedicated liquidity classification
field (see `synthetic_data_pipeline/tools.py` TOOL_CONTRACTS) -- eval cases
for this skill must ground liquidity claims in position type, weight
concentration, and currency (proxies genuinely present in
`portfolio.positions`), and the skill must explicitly disclose when no
formal liquidity classification is available rather than fabricate one.
That disclosure requirement is exactly what `data_provenance` and
`numeric_claim_grounding` are designed to catch.
"""

from .data_provenance import grade as data_provenance
from .numeric_claim_grounding import grade as numeric_grounding
from .portfolio_coverage import grade as portfolio_coverage
from .temporal_consistency import grade as temporal_consistency


def grade(evidence: dict) -> dict:
    """Return component metrics for authoritative liquidity-analysis evidence."""
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
