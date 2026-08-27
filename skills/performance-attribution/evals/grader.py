"""
Starter custom grader hook for Performance Attribution.
Replace/extend with trajectory-aware PM domain grading.
"""
def grade(case, trajectory, expected=None):
    return {
        "skill": "performance-attribution",
        "metrics": {},
        "notes": ["Implement skill-specific domain checks here."]
    }
