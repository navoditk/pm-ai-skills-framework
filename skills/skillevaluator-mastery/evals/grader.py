"""Deterministic grading hook for the skillevaluator-mastery utility skill.

Unlike the PM finance skills, this skill has no numeric domain evidence to
reconcile. Grading instead checks that a response actually names the
grounded facts the case expects (e.g. the correct env var, flag, or metric
definition) rather than fabricating plausible-sounding but wrong details.
"""


def grade(case, trajectory=None, expected=None):
    response_text = ""
    if isinstance(trajectory, dict):
        response_text = str(trajectory.get("response", ""))
    elif isinstance(trajectory, str):
        response_text = trajectory

    assertions = case.get("assertions", []) if isinstance(case, dict) else []
    # Keyword presence is a coarse proxy for "grounded, not fabricated" --
    # real grading of free-text answers belongs to the live judge model
    # (Tier 3), not this offline hook.
    hits = sum(1 for a in assertions if any(tok.lower() in response_text.lower() for tok in a.split()[:3]))
    score = hits / len(assertions) if assertions else 0.0

    return {
        "skill": "skillevaluator-mastery",
        "metrics": {"assertion_keyword_coverage": score},
        "score": score,
        "notes": [],
    }
