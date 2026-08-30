"""NVIDIA custom-grader hook for PM Commentary Generation."""

from graders.finance.pm_commentary_generation import grade as grade_evidence


def grade(case, trajectory=None, expected=None):
    """Grade authoritative evidence supplied by a test case or tool trajectory."""
    evidence = trajectory or expected or {}
    result = grade_evidence(evidence)
    return {
        "skill": "pm-commentary-generation",
        "metrics": result["metrics"],
        "score": result["score"],
        "notes": [],
    }
