"""Aggregate Tier 4 domain-grader results and hard gates from a completed
Tier 3 run.

Runs `tier3_trial_extractor.grade_trial` against every with-skill trial
directory for the GRADABLE_CASES in an already-completed Tier 3 result
directory, and produces skill-level metric averages plus two organizational
hard gates suitable for feeding into `framework/certification/engine.py`:

- `regression_pass_rate`: fraction of the skill's regression-category eval
  cases (identified from evals.json, currently performance--010, --024,
  --025) whose with-skill attempts all passed the Tier 4 grader. Note this
  measures the numeric/reconciliation dimension of those regression cases
  specifically -- it does not (yet) verify narrative-disclosure assertions
  like "detect reconciliation failure" that some regression cases also
  carry; that would need additional grading logic not built here.
- `authorization`: "pass" if zero non-empty `permission_denials` entries
  appear in any trial's raw agent output (`agent/claude-code.txt`) across
  the entire run -- both arms, all cases, not just the gradable subset.
  This is a complete, deterministic signal already present in every trial's
  output; no new grading logic was needed to compute it.

This makes no live agent or judge calls -- it only reads files already
written to disk by a prior `skillevaluator tier3 evaluate` run, so it costs
no additional API spend.

Usage:
    python skills/performance-attribution/evals/aggregate_tier4.py <tier3_result_dir>

<tier3_result_dir> is the directory containing `_harbor-jobs/` for a Tier 3
run, e.g.
reports/m4/performance-attribution-tier3-sonnet-agent/performance-attribution/<run_id>/
"""
import importlib.util
import json
import re
import statistics
import sys
from pathlib import Path

# `skills/performance-attribution/` contains a hyphen, so it cannot be a
# regular Python package path component; load the sibling module by file
# path instead of via a dotted import.
_extractor_path = Path(__file__).resolve().parent / "tier3_trial_extractor.py"
_spec = importlib.util.spec_from_file_location("tier3_trial_extractor", _extractor_path)
_extractor = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_extractor)
GRADABLE_CASES = _extractor.GRADABLE_CASES
grade_trial = _extractor.grade_trial

METRICS = [
    "reconciliation",
    "benchmark_consistency",
    "temporal_consistency",
    "data_provenance",
    "portfolio_coverage",
    "numeric_claim_grounding",
]


REGRESSION_CASES = {"performance--010", "performance--024", "performance--025"}

_DENIAL_RE = re.compile(r'"permission_denials":\s*(\[[^\]]*\])')


def find_with_skill_trials(result_dir: Path) -> list[Path]:
    jobs_dirs = list(result_dir.glob("_harbor-jobs/*-with"))
    trials = []
    for jobs_dir in jobs_dirs:
        for trial_dir in jobs_dir.iterdir():
            if trial_dir.is_dir() and (trial_dir / "agent" / "trajectory.json").exists():
                trials.append(trial_dir)
    return trials


def compute_authorization(result_dir: Path) -> dict:
    """Scan every trial's raw agent output (both arms) for a denied action.

    Deterministic and complete across the whole run -- not limited to the
    gradable subset, since this is a generic safety signal, not a financial
    one.
    """
    checked = 0
    denials = []
    for jobs_dir in list(result_dir.glob("_harbor-jobs/*-with")) + list(
        result_dir.glob("_harbor-jobs/*-without")
    ):
        for trial_dir in jobs_dir.iterdir():
            txt_path = trial_dir / "agent" / "claude-code.txt"
            if not txt_path.exists():
                continue
            checked += 1
            raw = txt_path.read_text()
            for match in _DENIAL_RE.finditer(raw):
                if match.group(1) != "[]":
                    denials.append(str(trial_dir))
    return {
        "trials_checked": checked,
        "trials_with_denials": denials,
        "status": "pass" if not denials else "fail",
    }


def aggregate(result_dir: Path) -> dict:
    trials = find_with_skill_trials(result_dir)
    graded = []
    skipped = []
    for trial_dir in trials:
        try:
            config = json.loads((trial_dir / "config.json").read_text())
            case_id = config.get("trial_name", trial_dir.name).split("__")[0]
        except (FileNotFoundError, json.JSONDecodeError):
            case_id = trial_dir.name.split("__")[0]

        if case_id not in GRADABLE_CASES:
            continue

        try:
            graded.append(grade_trial(trial_dir))
        except (ValueError, FileNotFoundError, KeyError) as exc:
            skipped.append({"trial_dir": str(trial_dir), "case_id": case_id, "reason": str(exc)})

    per_metric_scores = {m: [] for m in METRICS}
    per_case_pass = {}
    for g in graded:
        for m in METRICS:
            per_metric_scores[m].append(g["result"]["metrics"][m])
        per_case_pass.setdefault(g["case_id"], []).append(g["result"]["passed"])

    metric_averages = {
        m: (statistics.mean(scores) if scores else None)
        for m, scores in per_metric_scores.items()
    }
    overall_scores = [g["result"]["score"] for g in graded]

    cases_all_attempts_passed = sorted(
        cid for cid, passes in per_case_pass.items() if all(passes)
    )
    regression_cases_seen = sorted(REGRESSION_CASES & per_case_pass.keys())
    regression_cases_passed = sorted(REGRESSION_CASES & set(cases_all_attempts_passed))
    regression_pass_rate = (
        len(regression_cases_passed) / len(regression_cases_seen)
        if regression_cases_seen
        else None
    )

    return {
        "result_dir": str(result_dir),
        "gradable_cases_total": len(GRADABLE_CASES),
        "gradable_trials_expected": len(GRADABLE_CASES) * 3,
        "gradable_trials_graded": len(graded),
        "gradable_trials_skipped": len(skipped),
        "skipped": skipped,
        "metric_averages": metric_averages,
        "financial_accuracy": statistics.mean(overall_scores) if overall_scores else None,
        "cases_all_attempts_passed": cases_all_attempts_passed,
        "cases_with_a_failed_attempt": sorted(
            cid for cid, passes in per_case_pass.items() if not all(passes)
        ),
        "regression_cases_seen": regression_cases_seen,
        "regression_cases_passed": regression_cases_passed,
        "regression_pass_rate": regression_pass_rate,
        "authorization": compute_authorization(result_dir),
    }


def main() -> int:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <tier3_result_dir>", file=sys.stderr)
        return 2
    result_dir = Path(sys.argv[1])
    report = aggregate(result_dir)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
