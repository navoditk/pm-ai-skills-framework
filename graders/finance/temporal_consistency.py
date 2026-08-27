def grade(requested_as_of: str, observed_as_of_values: list[str]):
    ok = bool(observed_as_of_values) and all(x == requested_as_of for x in observed_as_of_values)
    return {"metric": "temporal_consistency", "score": 1.0 if ok else 0.0,
            "observed": observed_as_of_values}
