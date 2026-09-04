"""Tier 2 governance gate: run `skillevaluator similarity-check` for one or
more changed skills against the central catalog, then apply THIS project's
own governance actions from policies/similarity.yaml -- not the raw
skillevaluator exit code.

Why not just use the CLI's exit code: skillevaluator's own `overall_passed`
goes false on a HIGH_SIMILARITY finding, not just EXACT_DUPLICATE (confirmed
empirically in Milestone 6 -- see docs/MILESTONE_6_DELIBERATE_DEFECTS.md,
which measured a real HIGH_SIMILARITY score of 0.9468 and observed
`overall_passed: false`). policies/similarity.yaml deliberately treats those
two findings differently: EXACT_DUPLICATE blocks a merge,
HIGH_SIMILARITY routes to architecture_review (advisory, non-blocking). This
script is the layer that makes that distinction, matching
docs/02_TARGET_ARCHITECTURE.md Section 2.7's governance model.

Usage:
    python framework/certification/check_similarity.py skills/my-skill [skills/other-skill ...]

Requires SKILL_EVAL_EMBEDDING_PROVIDER (and the matching provider key) to be
set in the environment -- this makes a real embedding API call per skill
checked, priced in fractions of a cent, not free like Tier 1.

Exits non-zero only on an EXACT_DUPLICATE finding for a checked skill.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = REPO_ROOT / "catalogs" / "skill-catalog.json"
POLICY_PATH = REPO_ROOT / "policies" / "similarity.yaml"


def load_governance() -> dict:
    policy = yaml.safe_load(POLICY_PATH.read_text())
    return policy["governance"]


def run_similarity_check(skill_dir: Path) -> dict:
    """Invoke the real CLI for one skill against the central catalog."""
    # Use an isolated directory so stale reports cannot be mistaken for a
    # successful current run and parallel invocations cannot overwrite one
    # another.
    with tempfile.TemporaryDirectory(prefix="pmai-similarity-") as output_dir:
        result = subprocess.run(
            [
                "skillevaluator", "similarity-check", str(skill_dir),
                "--type", "skill",
                "--catalog", str(CATALOG_PATH),
                "-r", "json",
                "-o", output_dir,
            ],
            capture_output=True,
            text=True,
        )
        # skillevaluator writes its own JSON report file rather than printing
        # clean JSON to stdout -- read the report back rather than parsing stdout.
        report_path = Path(output_dir) / "skillevaluator-similarity.json"
        if not report_path.exists():
            print(result.stdout)
            print(result.stderr, file=sys.stderr)
            raise RuntimeError(f"similarity-check produced no report for {skill_dir}")
        return json.loads(report_path.read_text())


def classify_findings(report: dict) -> list[dict]:
    findings = []
    for r in report.get("results", []):
        for f in r.get("findings", []):
            classification = (f.get("metadata") or {}).get("classification")
            if classification:
                findings.append({
                    "classification": classification,
                    "message": f.get("message"),
                    "score": (f.get("metadata") or {}).get("score"),
                })
    return findings


def main() -> int:
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <skill-dir> [<skill-dir> ...]", file=sys.stderr)
        return 2

    governance = load_governance()
    blocking = False

    for arg in sys.argv[1:]:
        skill_dir = Path(arg)
        report = run_similarity_check(skill_dir)
        findings = classify_findings(report)
        if not findings:
            print(f"[OK] {skill_dir}: no similarity findings against the catalog.")
            continue
        for f in findings:
            action = governance.get(f["classification"], {}).get("action", "informational")
            tag = "BLOCK" if action == "block" else action.upper()
            print(f"[SIMILARITY-{tag}] {skill_dir}: {f['message']} (action: {action})")
            if action == "block":
                blocking = True

    if blocking:
        print("\nOne or more changed skills are EXACT_DUPLICATE matches against "
              "the catalog -- blocked per policies/similarity.yaml.")
        return 1

    print("\n[OK] similarity governance check passed (no blocking findings).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
