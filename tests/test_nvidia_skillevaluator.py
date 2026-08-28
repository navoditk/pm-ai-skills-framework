from unittest.mock import patch

from framework.adapters.nvidia_skillevaluator import (
    NvidiaSkillEvaluatorProvider,
    parse_nvidia_report,
)


def test_validate_uses_pinned_tier1_command():
    provider = NvidiaSkillEvaluatorProvider(executable="skillevaluator-0.2.1")
    with patch("framework.adapters.nvidia_skillevaluator.subprocess.run") as run:
        run.return_value.returncode = 0
        run.return_value.stdout = "{}"
        run.return_value.stderr = ""

        result = provider.validate("skills/portfolio-overview")

    assert run.call_args.args[0] == [
        "skillevaluator-0.2.1",
        "validate",
        "skills/portfolio-overview",
        "--no-dedup",
    ]
    assert result.normalized == {
        "framework_version": "0.1.0",
        "provider": "nvidia-skillevaluator",
        "phase": "validate",
        "evaluator_version": "0.2.1",
        "passed": True,
    }


def test_tier3_uses_codex_docker_command_and_certification_attempts():
    provider = NvidiaSkillEvaluatorProvider(executable="skillevaluator-0.2.1")
    with patch("framework.adapters.nvidia_skillevaluator.subprocess.run") as run:
        run.return_value.returncode = 1
        run.return_value.stdout = ""
        run.return_value.stderr = "Docker daemon is not running"

        result = provider.evaluate("skills/portfolio-overview", "certification")

    assert run.call_args.args[0] == [
        "skillevaluator-0.2.1",
        "tier3",
        "evaluate",
        "skills/portfolio-overview",
        "--agents",
        "codex",
        "--env-mode",
        "docker",
        "--n-attempts",
        "3",
    ]
    assert result.normalized["passed"] is False


def test_parse_tier3_report_normalizes_metrics_and_lift():
    result = parse_nvidia_report(
        {
            "evaluator_version": "0.2.1",
            "dataset_digest": "sha256:abc",
            "agents": {
                "codex": {
                    "model": "gpt-test",
                    "dimensions_with_skill": {
                        "security": {"score": 1.0},
                        "correctness": {"score": 0.9},
                    },
                    "lift": {"overall": {"with_skill": 0.9, "without_skill": 0.5, "delta": 0.4}},
                    "pass_at_k": {"with_skill": {"rate": 1.0}},
                }
            },
        },
        skill_id="pm.test.skill",
        skill_name="Test Skill",
        skill_version="1.0.0",
    )

    assert result["framework_version"] == "0.1.0"
    assert result["source"]["report_type"] == "tier3"
    assert result["generic_metrics"] == {"security": 1.0, "correctness": 0.9}
    assert result["skill_lift"]["delta"] == 0.4
    assert len(result["benchmark_context"]["fingerprint"]) == 64
