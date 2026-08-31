"""NVIDIA custom-grader hook for Exposure Analysis."""

from graders.finance.exposure_analysis import grade as grade_evidence


def grade(case, trajectory=None, expected=None):
    """Grade authoritative evidence supplied by a test case or tool trajectory."""
    evidence = trajectory or expected or {}
    result = grade_evidence(evidence)
    return {
        "skill": "exposure-analysis",
        "metrics": result["metrics"],
        "score": result["score"],
        "notes": [],
    }
