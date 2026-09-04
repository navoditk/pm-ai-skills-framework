"""Validation helpers for PM AI skill manifests."""

import json
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

SCHEMA_PATH = Path(__file__).with_name("skill.schema.json")


def load_skill_manifest(path: str | Path) -> dict[str, Any]:
    """Load a YAML skill manifest and reject non-object documents."""
    manifest = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise TypeError(f"Skill manifest must be a YAML object: {path}")
    return manifest


def validate_skill_manifest(path: str | Path) -> list[str]:
    """Return deterministic, human-readable schema errors for one manifest."""
    validator = Draft202012Validator(json.loads(SCHEMA_PATH.read_text(encoding="utf-8")))
    errors = sorted(validator.iter_errors(load_skill_manifest(path)), key=lambda error: list(error.path))
    return [f"{path}: {error.message}" for error in errors]


def validate_skill_library(skills_root: str | Path) -> dict[str, list[str]]:
    """Validate every skill.yaml directly beneath a skills directory."""
    root = Path(skills_root)
    return {
        str(path): validate_skill_manifest(path)
        for path in sorted(root.glob("*/skill.yaml"))
    }


def validate_skill_package(skill_dir: str | Path) -> list[str]:
    """Validate the PM package contract, including required evaluator files."""
    root = Path(skill_dir)
    required = ("SKILL.md", "skill.yaml", "evals/EVAL.md", "evals/evals.json", "evals/config.yml")
    errors = [f"{root}: missing required file {name}" for name in required if not (root / name).is_file()]
    manifest = root / "skill.yaml"
    if manifest.is_file():
        errors.extend(validate_skill_manifest(manifest))
    return errors
