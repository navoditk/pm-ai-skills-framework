"""Broader Tier 1 coverage for this repo's own local, keyless pre-checks.

These tests do not shell out to the real `skillevaluator` CLI (that would
require the pinned binary and is exercised separately in
tests/test_nvidia_skillevaluator.py via mocked subprocess calls). Instead
they exercise framework/schemas/validation.py -- the structural/schema layer
that mirrors what NVIDIA SkillEvaluator's Tier 1 `validate` command checks
(required package files + skill.yaml schema shape) -- against a wide range
of malformed and edge-case skill packages. This increases Tier 1 breadth
without needing the external binary, Docker, or any API key.
"""
import textwrap

import pytest

from framework.schemas.validation import (
    validate_skill_manifest,
    validate_skill_package,
)

VALID_MANIFEST = textwrap.dedent(
    """\
    schema_version: 1
    skill:
      id: pm.test.skill
      name: Test Skill
      version: 0.1.0

    ownership:
      business: portfolio-management
      engineering: pm-ai
      domain_reviewer: portfolio-management

    classification:
      domain: portfolio-management
      risk_level: analytical

    dependencies:
      tools: []

    evaluation:
      dataset: evals/evals.json

    certification:
      policy_profile: analytical-standard
    """
)


def _write_manifest(tmp_path, text):
    path = tmp_path / "skill.yaml"
    path.write_text(text)
    return path


def _write_full_package(tmp_path, manifest_text=VALID_MANIFEST):
    skill_dir = tmp_path / "some-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("# Test Skill\n")
    (skill_dir / "skill.yaml").write_text(manifest_text)
    evals = skill_dir / "evals"
    evals.mkdir()
    (evals / "EVAL.md").write_text("# Eval guidance\n")
    (evals / "evals.json").write_text('{"skill_name": "some-skill", "evals": []}')
    (evals / "config.yml").write_text("provider: mock\n")
    return skill_dir


# --- validate_skill_manifest: schema breadth -------------------------------


def test_valid_manifest_has_no_errors(tmp_path):
    path = _write_manifest(tmp_path, VALID_MANIFEST)
    assert validate_skill_manifest(path) == []


@pytest.mark.parametrize(
    "mutation,expected_fragment",
    [
        ("schema_version: 1", "schema_version: 2"),
        ("id: pm.test.skill", "id: Pm.Test.Skill"),  # pattern requires lowercase
        ("version: 0.1.0", "version: 1.0"),  # pattern requires semver
        ("risk_level: analytical", "risk_level: reckless"),  # not in enum
    ],
)
def test_manifest_rejects_malformed_field(tmp_path, mutation, expected_fragment):
    broken = VALID_MANIFEST.replace(mutation, expected_fragment)
    path = _write_manifest(tmp_path, broken)
    errors = validate_skill_manifest(path)
    assert errors, f"expected a schema error after replacing {mutation!r}"


@pytest.mark.parametrize(
    "top_level_key",
    ["ownership", "classification", "dependencies", "evaluation", "certification"],
)
def test_manifest_rejects_missing_required_top_level_block(tmp_path, top_level_key):
    lines = VALID_MANIFEST.splitlines()
    # Drop the block for the given top-level key (its header line through
    # the next blank line or EOF).
    kept = []
    skipping = False
    for line in lines:
        if line == f"{top_level_key}:":
            skipping = True
            continue
        if skipping and (line == "" or not line.startswith((" ", "\t"))):
            skipping = False
        if not skipping:
            kept.append(line)
    broken = "\n".join(kept) + "\n"
    path = _write_manifest(tmp_path, broken)
    errors = validate_skill_manifest(path)
    assert any(top_level_key in error for error in errors), errors


def test_manifest_rejects_non_object_document(tmp_path):
    path = tmp_path / "skill.yaml"
    path.write_text("- just\n- a\n- list\n")
    with pytest.raises(TypeError):
        validate_skill_manifest(path)


def test_manifest_reports_multiple_errors_independently(tmp_path):
    broken = VALID_MANIFEST.replace("schema_version: 1", "schema_version: 2").replace(
        "risk_level: analytical", "risk_level: reckless"
    )
    path = _write_manifest(tmp_path, broken)
    errors = validate_skill_manifest(path)
    assert len(errors) >= 2


# --- validate_skill_package: full package contract breadth -----------------


def test_full_package_passes_with_all_required_files(tmp_path):
    skill_dir = _write_full_package(tmp_path)
    assert validate_skill_package(skill_dir) == []


@pytest.mark.parametrize(
    "missing_relative_path",
    ["SKILL.md", "skill.yaml", "evals/EVAL.md", "evals/evals.json", "evals/config.yml"],
)
def test_package_flags_each_missing_required_file_independently(tmp_path, missing_relative_path):
    skill_dir = _write_full_package(tmp_path)
    (skill_dir / missing_relative_path).unlink()
    errors = validate_skill_package(skill_dir)
    assert any(missing_relative_path in error for error in errors)


def test_package_reports_all_missing_files_at_once(tmp_path):
    skill_dir = tmp_path / "empty-skill"
    skill_dir.mkdir()
    errors = validate_skill_package(skill_dir)
    # SKILL.md, skill.yaml, evals/EVAL.md, evals/evals.json, evals/config.yml
    assert len(errors) == 5


def test_package_combines_missing_files_and_schema_errors(tmp_path):
    skill_dir = tmp_path / "half-built-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("# WIP\n")
    (skill_dir / "skill.yaml").write_text(
        VALID_MANIFEST.replace("risk_level: analytical", "risk_level: reckless")
    )
    errors = validate_skill_package(skill_dir)
    # Missing evals/* files plus the invalid risk_level enum value.
    assert len(errors) >= 4
    assert any("evals/EVAL.md" in e for e in errors)
    assert any("evals/evals.json" in e for e in errors)
    assert any("evals/config.yml" in e for e in errors)


def test_package_skips_schema_check_when_manifest_itself_is_missing(tmp_path):
    skill_dir = tmp_path / "no-manifest-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("# No manifest\n")
    errors = validate_skill_package(skill_dir)
    assert any("skill.yaml" in e for e in errors)
    # Only the missing-file errors should be present -- no schema errors can
    # be produced for a manifest that does not exist.
    assert len(errors) == 4
