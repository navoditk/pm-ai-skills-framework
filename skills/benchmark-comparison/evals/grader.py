"""
Starter custom grader hook for Benchmark Comparison.
Replace/extend with trajectory-aware PM domain grading.
"""
def grade(case, trajectory, expected=None):
    return {
        "skill": "benchmark-comparison",
        "metrics": {},
        "notes": ["Implement skill-specific domain checks here."]
    }
