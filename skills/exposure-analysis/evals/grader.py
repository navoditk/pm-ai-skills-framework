"""
Starter custom grader hook for Exposure Analysis.
Replace/extend with trajectory-aware PM domain grading.
"""
def grade(case, trajectory, expected=None):
    return {
        "skill": "exposure-analysis",
        "metrics": {},
        "notes": ["Implement skill-specific domain checks here."]
    }
