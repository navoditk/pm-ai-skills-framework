"""NVIDIA custom-grader hook for Scenario Analysis."""

from graders.finance.scenario_analysis import grade as grade_evidence


def grade(case, trajectory=None, expected=None):
    """Grade authoritative evidence supplied by a test case or tool trajectory."""
    evidence = trajectory or expected or {}
    result = grade_evidence(evidence)
    return {
        "skill": "scenario-analysis",
        "metrics": result["metrics"],
        "score": result["score"],
        "notes": [],
    }
