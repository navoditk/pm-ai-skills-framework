def grade(expected_ids: set[str], observed_ids: set[str]):
    if not expected_ids:
        return {"metric": "portfolio_coverage", "score": 1.0}
    coverage = len(expected_ids & observed_ids) / len(expected_ids)
    return {"metric": "portfolio_coverage", "score": coverage,
            "missing": sorted(expected_ids - observed_ids)}
