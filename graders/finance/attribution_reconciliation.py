def grade(expected_total: float, components: list[float], tolerance: float = 1e-6):
    difference = abs(sum(components) - expected_total)
    return {"metric": "reconciliation", "score": 1.0 if difference <= tolerance else 0.0,
            "difference": difference}
