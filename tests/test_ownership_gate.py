import textwrap

from framework.certification.check_ownership import check_skill, REQUIRED_FIELDS


def _write_skill_yaml(tmp_path, domain_reviewer):
    skill_dir = tmp_path / "some-skill"
    skill_dir.mkdir()
    (skill_dir / "skill.yaml").write_text(
        textwrap.dedent(
            f"""\
            schema_version: 1
            skill:
              id: pm.some.skill
              name: Some Skill
              version: 0.1.0

            ownership:
              business: portfolio-management
              engineering: pm-ai
              domain_reviewer: {domain_reviewer}
            """
        )
    )
    return skill_dir


def test_ownership_gate_passes_with_real_reviewer(tmp_path):
    skill_dir = _write_skill_yaml(tmp_path, "portfolio-management")
    assert check_skill(skill_dir) == []


def test_ownership_gate_fails_on_placeholder(tmp_path):
    skill_dir = _write_skill_yaml(tmp_path, "domain-owner-required")
    violations = check_skill(skill_dir)
    assert len(violations) == 1
    assert "domain_reviewer" in violations[0]


def test_ownership_gate_fails_on_missing_ownership_block(tmp_path):
    skill_dir = tmp_path / "no-ownership-skill"
    skill_dir.mkdir()
    (skill_dir / "skill.yaml").write_text(
        "schema_version: 1\nskill:\n  id: pm.x\n  name: X\n  version: 0.1.0\n"
    )
    violations = check_skill(skill_dir)
    assert len(violations) == len(REQUIRED_FIELDS)


def test_ownership_gate_skips_missing_skill_yaml(tmp_path):
    skill_dir = tmp_path / "no-yaml-skill"
    skill_dir.mkdir()
    assert check_skill(skill_dir) == []


def test_all_real_skills_pass_ownership_gate():
    from pathlib import Path

    repo_root = Path(__file__).resolve().parents[1]
    skill_dirs = sorted(p.parent for p in (repo_root / "skills").glob("*/skill.yaml"))
    assert skill_dirs, "expected at least one skill with a skill.yaml"
    all_violations = []
    for d in skill_dirs:
        all_violations.extend(check_skill(d))
    assert all_violations == [], f"real skills should pass: {all_violations}"
