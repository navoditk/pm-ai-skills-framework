def grade(allowed_sources: set[str], observed_sources: set[str]):
    unapproved = observed_sources - allowed_sources
    return {"metric": "data_provenance", "score": 1.0 if not unapproved else 0.0,
            "unapproved_sources": sorted(unapproved)}
