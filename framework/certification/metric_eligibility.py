"""Define which evaluation cases may contribute to certification metrics."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any


DISCOVERABILITY_EXCLUDED_CATEGORIES = frozenset({"ambiguous"})


def eligible_discoverability_case_ids(
    evaluations: Iterable[Mapping[str, Any]],
) -> set[str]:
    """Return cases where skill activation is an applicable expectation.

    Ambiguous-reference cases deliberately require one clarifying question and
    prohibit tools. They test safe ambiguity handling, not skill activation.
    """
    return {
        evaluation["id"]
        for evaluation in evaluations
        if evaluation.get("category") not in DISCOVERABILITY_EXCLUDED_CATEGORIES
    }


def eligible_discoverability_score(
    evaluations: Iterable[Mapping[str, Any]],
    case_scores: Mapping[str, float],
) -> float:
    """Average activation scores only across cases where activation applies."""
    eligible_ids = eligible_discoverability_case_ids(evaluations)
    scores = [case_scores[case_id] for case_id in eligible_ids if case_id in case_scores]
    if not scores:
        raise ValueError("No discoverability scores were supplied for eligible cases")
    return sum(scores) / len(scores)
