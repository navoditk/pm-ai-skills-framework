"""NVIDIA custom-grader hook for Position Investigation."""

from graders.finance.position_investigation import grade as grade_evidence


def grade(case, trajectory=None, expected=None):
    """Grade authoritative evidence supplied by a test case or tool trajectory."""
    evidence = trajectory or expected or {}
    result = grade_evidence(evidence)
    return {
        "skill": "position-investigation",
        "metrics": result["metrics"],
        "score": result["score"],
        "notes": [],
    }
