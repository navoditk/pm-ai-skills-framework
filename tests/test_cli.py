import json

from framework.cli.main import main


def test_validate_library_command_passes(monkeypatch):
    monkeypatch.setattr("sys.argv", ["pmai-skills", "validate", "skills"])
    assert main() == 0


def test_init_creates_complete_scaffold(tmp_path, monkeypatch):
    target = tmp_path / "new-skill"
    monkeypatch.setattr("sys.argv", ["pmai-skills", "init", str(target)])
    assert main() == 0
    for relative in ("SKILL.md", "skill.yaml", "evals/EVAL.md", "evals/evals.json", "evals/config.yml"):
        assert (target / relative).is_file()


def test_certify_applies_resolved_policy(tmp_path, monkeypatch, capsys):
    source = tmp_path / "skill"
    source.mkdir()
    (source / "skill.yaml").write_text(
        "classification:\n  risk_level: informational\nskill:\n  id: pm.test\n"
    )
    metrics = tmp_path / "metrics.json"
    metrics.write_text(json.dumps({
        "security": "pass", "authorization": "pass", "correctness": 0.95,
        "discoverability_eligible": 0.90, "effectiveness": 0.90, "skill_lift_overall": 0.10,
    }))
    monkeypatch.setattr("sys.argv", ["pmai-skills", "certify", str(source), "--profile", "release", "--metrics", str(metrics)])
    assert main() == 0
    assert '"status": "PASS"' in capsys.readouterr().out
