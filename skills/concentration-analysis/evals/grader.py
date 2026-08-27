"""
Starter custom grader hook for Concentration Analysis.
Replace/extend with trajectory-aware PM domain grading.
"""
def grade(case, trajectory, expected=None):
    return {
        "skill": "concentration-analysis",
        "metrics": {},
        "notes": ["Implement skill-specific domain checks here."]
    }
