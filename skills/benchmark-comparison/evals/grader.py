"""NVIDIA custom-grader hook for Benchmark Comparison."""

from graders.finance.benchmark_comparison import grade as grade_evidence


def grade(case, trajectory=None, expected=None):
    """Grade authoritative evidence supplied by a test case or tool trajectory."""
    evidence = trajectory or expected or {}
    result = grade_evidence(evidence)
    return {
        "skill": "benchmark-comparison",
        "metrics": result["metrics"],
        "score": result["score"],
        "notes": [],
    }
