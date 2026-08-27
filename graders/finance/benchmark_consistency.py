def grade(expected_benchmark: str, observed_benchmark: str):
    ok = expected_benchmark == observed_benchmark
    return {"metric": "benchmark_consistency", "score": 1.0 if ok else 0.0}
