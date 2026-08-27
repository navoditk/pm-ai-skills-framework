"""
Starter custom grader hook for Position Investigation.
Replace/extend with trajectory-aware PM domain grading.
"""
def grade(case, trajectory, expected=None):
    return {
        "skill": "position-investigation",
        "metrics": {},
        "notes": ["Implement skill-specific domain checks here."]
    }
