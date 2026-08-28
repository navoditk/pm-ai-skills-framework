import json
from pathlib import Path

from jsonschema import Draft202012Validator

from framework.adapters.nvidia_skillevaluator import parse_nvidia_report
from framework.benchmark.identity import build_benchmark_identity
from framework.schemas.validation import validate_skill_library


def test_all_reference_skill_manifests_match_schema():
    results = validate_skill_library("skills")
    assert len(results) == 13
    assert all(not errors for errors in results.values())


def test_benchmark_identity_is_stable_and_changes_with_context():
    kwargs = {
        "skill_version": "1.0.0",
        "dataset_version": "dataset-1",
        "agent": "codex",
        "model": "model-1",
        "evaluator_version": "0.2.1",
        "grader_version": "1.0.0",
        "fixture_version": "fixture-1",
        "environment": "docker",
    }
    first = build_benchmark_identity(**kwargs)
    second = build_benchmark_identity(**kwargs)
    changed = build_benchmark_identity(**{**kwargs, "model": "model-2"})
    assert first == second
    assert first["fingerprint"] != changed["fingerprint"]


def test_normalized_report_matches_framework_schema():
    report = parse_nvidia_report(
        {"evaluator_version": "0.2.1", "quality_summary": [{"dimensions": {}}]},
        skill_id="pm.test.skill",
        skill_name="Test Skill",
        skill_version="1.0.0",
    )
    schema = json.loads(Path("framework/schemas/evaluation-result.schema.json").read_text(encoding="utf-8"))
    errors = list(Draft202012Validator(schema).iter_errors(report))
    assert errors == []
