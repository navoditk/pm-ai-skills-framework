"""Deterministic benchmark identity for evaluation evidence."""

import hashlib
import json
from typing import Any


def benchmark_fingerprint(context: dict[str, Any]) -> str:
    """Hash the complete benchmark context using canonical JSON."""
    payload = json.dumps(context, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def build_benchmark_identity(
    *,
    skill_version: str,
    dataset_version: str,
    agent: str,
    model: str,
    evaluator_version: str,
    grader_version: str,
    fixture_version: str,
    environment: str,
) -> dict[str, Any]:
    """Build the stable identity tuple required for benchmark evidence."""
    context = {
        "skill_version": skill_version,
        "dataset_version": dataset_version,
        "agent": agent,
        "model": model,
        "evaluator_version": evaluator_version,
        "grader_version": grader_version,
        "fixture_version": fixture_version,
        "environment": environment,
    }
    return {"context": context, "fingerprint": benchmark_fingerprint(context)}
