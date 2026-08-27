def grade(claims: list[float], authoritative_values: list[float], tolerance: float = 1e-6):
    unmatched = []
    for c in claims:
        if not any(abs(c - a) <= tolerance for a in authoritative_values):
            unmatched.append(c)
    score = 1.0 if not claims else (len(claims) - len(unmatched)) / len(claims)
    return {"metric": "numeric_claim_grounding", "score": score, "unmatched": unmatched}
