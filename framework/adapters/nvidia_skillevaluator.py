"""
Thin provider adapter.

Do not leak raw NVIDIA output into downstream certification/reporting code.
Exact CLI flags should be pinned and verified against the installed
SkillEvaluator version during implementation.
"""
import json
import subprocess
from pathlib import Path
from .base import EvaluationProvider, ProviderResult

class NvidiaSkillEvaluatorProvider(EvaluationProvider):
    def _run(self, args):
        cp = subprocess.run(args, check=False, text=True, capture_output=True)
        return {"returncode": cp.returncode, "stdout": cp.stdout, "stderr": cp.stderr}

    def validate(self, skill_path: str) -> ProviderResult:
        raw = self._run(["skillevaluator", "validate", skill_path])
        normalized = {
            "provider": "nvidia-skillevaluator",
            "phase": "validate",
            "passed": raw["returncode"] == 0,
        }
        return ProviderResult(raw=raw, normalized=normalized)

    def similarity(self, skill_path: str, catalog_path: str) -> ProviderResult:
        raw = self._run([
            "skillevaluator", "similarity-check", skill_path,
            "--catalog", catalog_path
        ])
        normalized = {
            "provider": "nvidia-skillevaluator",
            "phase": "similarity",
            "passed": raw["returncode"] == 0,
        }
        return ProviderResult(raw=raw, normalized=normalized)

    def evaluate(self, skill_path: str, profile: str) -> ProviderResult:
        attempts = "3" if profile == "certification" else "1"
        raw = self._run([
            "skillevaluator", "tier3", "evaluate", skill_path,
            "--env-mode", "docker",
            "--n-attempts", attempts
        ])
        normalized = {
            "provider": "nvidia-skillevaluator",
            "phase": "tier3",
            "profile": profile,
            "passed": raw["returncode"] == 0,
        }
        return ProviderResult(raw=raw, normalized=normalized)
