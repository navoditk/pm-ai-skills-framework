"""NVIDIA custom-grader hook for Market Move Explanation."""

from graders.finance.market_move_explanation import grade as grade_evidence


def grade(case, trajectory=None, expected=None):
    """Grade authoritative evidence supplied by a test case or tool trajectory."""
    evidence = trajectory or expected or {}
    result = grade_evidence(evidence)
    return {
        "skill": "market-move-explanation",
        "metrics": result["metrics"],
        "score": result["score"],
        "notes": [],
    }
