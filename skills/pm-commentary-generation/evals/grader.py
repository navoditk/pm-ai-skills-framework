"""
Starter custom grader hook for PM Commentary Generation.
Replace/extend with trajectory-aware PM domain grading.
"""
def grade(case, trajectory, expected=None):
    return {
        "skill": "pm-commentary-generation",
        "metrics": {},
        "notes": ["Implement skill-specific domain checks here."]
    }
