"""Small adapter for the pinned NVIDIA SkillEvaluator CLI.

Provider-specific command details stay here.  Downstream code should consume
``ProviderResult.normalized`` and never depend on NVIDIA report structures.
"""
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from framework.benchmark.identity import benchmark_fingerprint
from framework.version import FRAMEWORK_VERSION

from .base import EvaluationProvider, ProviderResult

NVIDIA_SKILLEVALUATOR_VERSION = "0.2.1"


def parse_nvidia_report(
    report: dict[str, Any],
    *,
    skill_id: str,
    skill_name: str,
    skill_version: str,
) -> dict[str, Any]:
    """Convert a Tier 1 or Tier 3 NVIDIA report to the PM AI contract."""
    agents = report.get("agents", {})
    agent_name, agent_data = next(iter(agents.items()), ("unknown", {}))
    agent_data = agent_data if isinstance(agent_data, dict) else {}
    with_skill = agent_data.get("dimensions_with_skill", {})
    lift = agent_data.get("lift", {})
    generic_metrics = {
        name: value.get("score")
        for name, value in with_skill.items()
        if isinstance(value, dict) and isinstance(value.get("score"), (int, float))
    }
    if not generic_metrics and report.get("quality_summary"):
        quality = report["quality_summary"][0]
        dimensions = quality.get("dimensions", {})
        generic_metrics = {
            name: value.get("score", 0) / 100
            for name, value in dimensions.items()
            if isinstance(value, dict) and isinstance(value.get("score"), (int, float))
        }
        security = next(
            (item for item in report.get("results", []) if item.get("validator") == "Security Scan"),
            {},
        )
        generic_metrics["security"] = 1.0 if security.get("passed") else 0.0

    benchmark_context = {
        "agent": agent_name,
        "model": agent_data.get("model", "unknown"),
        "dataset": report.get("dataset_digest") or report.get("dataset_summary", {}),
        "evaluator_version": report.get("evaluator_version", NVIDIA_SKILLEVALUATOR_VERSION),
        "environment": report.get("run_config", {}).get("harbor", {}).get("environment", "unknown"),
    }
    benchmark_context["fingerprint"] = benchmark_fingerprint(benchmark_context)
    return {
        "framework_version": FRAMEWORK_VERSION,
        "source": {
            "provider": "nvidia-skillevaluator",
            "evaluator_version": report.get("evaluator_version", NVIDIA_SKILLEVALUATOR_VERSION),
            "report_type": "tier3" if agents else "tier1",
        },
        "skill": {"id": skill_id, "name": skill_name, "version": skill_version},
        "benchmark_context": benchmark_context,
        "generic_metrics": generic_metrics,
        "skill_lift": lift.get("overall", {}) if isinstance(lift, dict) else {},
        "reliability": agent_data.get("pass_at_k", {}) if isinstance(agent_data, dict) else {},
        "domain_metrics": {},
        "findings": report.get("tier3_feedback", {}).get("conclusions", []),
        "certification": {"status": "UNASSESSED"},
    }


def parse_nvidia_report_file(
    path: str | Path,
    *,
    skill_id: str,
    skill_name: str,
    skill_version: str,
) -> dict[str, Any]:
    """Parse a JSON report file without exposing provider details downstream."""
    import json

    return parse_nvidia_report(
        json.loads(Path(path).read_text(encoding="utf-8")),
        skill_id=skill_id,
        skill_name=skill_name,
        skill_version=skill_version,
    )


class NvidiaSkillEvaluatorProvider(EvaluationProvider):
    """Invoke NVIDIA SkillEvaluator 0.2.1-compatible commands."""

    def __init__(self, executable: str | None = None):
        self.executable = (
            executable
            or os.environ.get("PM_AI_SKILLEVALUATOR_BIN")
            or shutil.which("skillevaluator")
            or "skillevaluator"
        )

    def _run(self, args):
        cp = subprocess.run([self.executable, *args], check=False, text=True, capture_output=True)
        return {"returncode": cp.returncode, "stdout": cp.stdout, "stderr": cp.stderr}

    def validate(self, skill_path: str) -> ProviderResult:
        # Tier 1 is independent of Tier 2.  Explicitly skip deduplication so
        # this method remains keyless and deterministic for the smoke test.
        raw = self._run(["validate", skill_path, "--no-dedup"])
        normalized = {
            "framework_version": FRAMEWORK_VERSION,
            "provider": "nvidia-skillevaluator",
            "phase": "validate",
            "evaluator_version": NVIDIA_SKILLEVALUATOR_VERSION,
            "passed": raw["returncode"] == 0,
        }
        return ProviderResult(raw=raw, normalized=normalized)

    def similarity(self, skill_path: str, catalog_path: str) -> ProviderResult:
        raw = self._run(["similarity-check", skill_path, "--catalog", catalog_path])
        normalized = {
            "framework_version": FRAMEWORK_VERSION,
            "provider": "nvidia-skillevaluator",
            "phase": "similarity",
            "passed": raw["returncode"] == 0,
        }
        return ProviderResult(raw=raw, normalized=normalized)

    def evaluate(self, skill_path: str, profile: str) -> ProviderResult:
        attempts = "3" if profile == "certification" else "1"
        raw = self._run([
            "tier3", "evaluate", skill_path,
            "--agents", "codex",
            "--env-mode", "docker",
            "--n-attempts", attempts
        ])
        normalized = {
            "framework_version": FRAMEWORK_VERSION,
            "provider": "nvidia-skillevaluator",
            "phase": "tier3",
            "profile": profile,
            "evaluator_version": NVIDIA_SKILLEVALUATOR_VERSION,
            "passed": raw["returncode"] == 0,
        }
        return ProviderResult(raw=raw, normalized=normalized)
