"""NVIDIA custom-grader hook for Portfolio Overview."""

from graders.finance.portfolio_overview import grade as grade_evidence


def grade(case, trajectory=None, expected=None):
    """Grade authoritative evidence supplied by a test case or tool trajectory.

    The optional ``trajectory`` argument may contain the same keys as
    ``expected``. This keeps the hook usable by the future live evaluator while
    making the deterministic fixture path directly testable today.
    """
    evidence = trajectory or expected or {}
    result = grade_evidence(evidence)
    return {
        "skill": "portfolio-overview",
        "metrics": result["metrics"],
        "score": result["score"],
        "notes": [],
    }
