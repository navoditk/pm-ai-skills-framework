"""
Starter custom grader hook for Risk Explanation.
Replace/extend with trajectory-aware PM domain grading.
"""
def grade(case, trajectory, expected=None):
    return {
        "skill": "risk-explanation",
        "metrics": {},
        "notes": ["Implement skill-specific domain checks here."]
    }
