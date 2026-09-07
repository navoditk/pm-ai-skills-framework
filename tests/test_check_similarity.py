"""Broader Tier 2 coverage for this repo's similarity governance layer.

NVIDIA SkillEvaluator's Tier 2 (`similarity-check`) requires a real
embedding-provider API call (SKILL_EVAL_EMBEDDING_PROVIDER + a key) and is
therefore deliberately NOT invoked live here. Instead, these tests mock
`subprocess.run` and drive framework/certification/check_similarity.py's
governance logic (classify_findings + policies/similarity.yaml action
mapping) directly against a wide range of report shapes. This increases
Tier 2 breadth without spending money or requiring credentials.
"""
import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from framework.certification import check_similarity as cs


def _report(results):
    return {"results": results}


def _finding(classification, score=None, message="similarity finding"):
    return {
        "message": message,
        "metadata": {"classification": classification, "score": score},
    }


# --- classify_findings: parsing breadth ------------------------------------


def test_classify_findings_returns_empty_for_no_results():
    assert cs.classify_findings({"results": []}) == []


def test_classify_findings_returns_empty_when_results_key_missing():
    assert cs.classify_findings({}) == []


def test_classify_findings_ignores_findings_without_classification():
    report = _report([{"findings": [{"message": "no metadata"}]}])
    assert cs.classify_findings(report) == []


def test_classify_findings_ignores_findings_with_null_metadata():
    report = _report([{"findings": [{"message": "null metadata", "metadata": None}]}])
    assert cs.classify_findings(report) == []


def test_classify_findings_extracts_single_finding():
    report = _report([{"findings": [_finding("EXACT_DUPLICATE", score=1.0)]}])
    findings = cs.classify_findings(report)
    assert findings == [
        {"classification": "EXACT_DUPLICATE", "message": "similarity finding", "score": 1.0}
    ]


def test_classify_findings_extracts_across_multiple_results_and_findings():
    report = _report(
        [
            {"findings": [_finding("HIGH_SIMILARITY", score=0.9468, message="near dup of skill-a")]},
            {
                "findings": [
                    _finding("SIMILAR", score=0.7, message="overlaps skill-b"),
                    _finding("DISTINCT", score=0.1, message="unrelated to skill-c"),
                ]
            },
        ]
    )
    findings = cs.classify_findings(report)
    assert [f["classification"] for f in findings] == ["HIGH_SIMILARITY", "SIMILAR", "DISTINCT"]
    assert findings[0]["score"] == 0.9468


# --- load_governance: real policy file breadth -----------------------------


def test_load_governance_matches_real_policy_file():
    governance = cs.load_governance()
    assert governance["EXACT_DUPLICATE"]["action"] == "block"
    assert governance["HIGH_SIMILARITY"]["action"] == "architecture_review"
    assert governance["SIMILAR"]["action"] == "advisory_with_justification"
    assert governance["LOOSELY_RELATED"]["action"] == "informational"
    assert governance["DISTINCT"]["action"] == "pass"


# --- run_similarity_check: subprocess invocation and failure handling -----


def _mock_run_writing_report(report):
    def _run(args, capture_output, text):
        # Emulate skillevaluator writing its own report file into the -o dir.
        output_dir = Path(args[args.index("-o") + 1])
        (output_dir / "skillevaluator-similarity.json").write_text(json.dumps(report))

        class _Completed:
            stdout = ""
            stderr = ""

        return _Completed()

    return _run


def test_run_similarity_check_invokes_expected_cli_args(tmp_path):
    skill_dir = tmp_path / "skills" / "some-skill"
    skill_dir.mkdir(parents=True)
    report = _report([])
    with patch("framework.certification.check_similarity.subprocess.run") as run:
        run.side_effect = _mock_run_writing_report(report)
        result = cs.run_similarity_check(skill_dir)

    assert result == report
    args = run.call_args.args[0]
    assert args[0] == "skillevaluator"
    assert args[1] == "similarity-check"
    assert args[2] == str(skill_dir)
    assert "--catalog" in args
    assert str(cs.CATALOG_PATH) in args
    assert "-r" in args and "json" in args


def test_run_similarity_check_raises_when_no_report_produced(tmp_path):
    skill_dir = tmp_path / "skills" / "some-skill"
    skill_dir.mkdir(parents=True)

    class _Completed:
        stdout = "some CLI output"
        stderr = ""

    with (
        patch("framework.certification.check_similarity.subprocess.run", return_value=_Completed()),
        pytest.raises(RuntimeError, match="no report"),
    ):
        cs.run_similarity_check(skill_dir)


# --- main(): governance action breadth per classification ------------------


@pytest.mark.parametrize(
    "classification,should_block",
    [
        ("EXACT_DUPLICATE", True),
        ("HIGH_SIMILARITY", False),
        ("SIMILAR", False),
        ("LOOSELY_RELATED", False),
        ("DISTINCT", False),
        ("SOME_UNKNOWN_FUTURE_CLASSIFICATION", False),
    ],
)
def test_main_blocks_only_on_exact_duplicate(tmp_path, capsys, classification, should_block):
    skill_dir = tmp_path / "skills" / "candidate-skill"
    skill_dir.mkdir(parents=True)
    report = _report([{"findings": [_finding(classification)]}])
    with (
        patch.object(sys, "argv", ["check_similarity.py", str(skill_dir)]),
        patch("framework.certification.check_similarity.run_similarity_check", return_value=report),
    ):
        exit_code = cs.main()

    out = capsys.readouterr().out
    assert (exit_code == 1) is should_block
    if should_block:
        assert "BLOCK" in out
    else:
        assert "[SIMILARITY-" in out


def test_main_passes_with_no_findings(tmp_path, capsys):
    skill_dir = tmp_path / "skills" / "clean-skill"
    skill_dir.mkdir(parents=True)
    with (
        patch.object(sys, "argv", ["check_similarity.py", str(skill_dir)]),
        patch("framework.certification.check_similarity.run_similarity_check", return_value=_report([])),
    ):
        exit_code = cs.main()

    assert exit_code == 0
    assert "[OK]" in capsys.readouterr().out


def test_main_blocks_if_any_of_multiple_skills_is_exact_duplicate(tmp_path, capsys):
    clean_dir = tmp_path / "skills" / "clean-skill"
    dup_dir = tmp_path / "skills" / "dup-skill"
    clean_dir.mkdir(parents=True)
    dup_dir.mkdir(parents=True)

    reports = {
        str(clean_dir): _report([]),
        str(dup_dir): _report([{"findings": [_finding("EXACT_DUPLICATE")]}]),
    }

    def fake_check(skill_dir):
        return reports[str(skill_dir)]

    with (
        patch.object(sys, "argv", ["check_similarity.py", str(clean_dir), str(dup_dir)]),
        patch("framework.certification.check_similarity.run_similarity_check", side_effect=fake_check),
    ):
        exit_code = cs.main()

    assert exit_code == 1
    out = capsys.readouterr().out
    assert f"[OK] {clean_dir}" in out
    assert "BLOCK" in out


def test_main_requires_at_least_one_skill_argument(capsys):
    with patch.object(sys, "argv", ["check_similarity.py"]):
        exit_code = cs.main()
    assert exit_code == 2
    assert "Usage" in capsys.readouterr().err
