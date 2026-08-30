"""Extract Tier 4 grading evidence from a real Tier 3 Harbor trial directory.

This bridges live-agent Tier 3 evidence (trajectory.json, produced by
`skillevaluator tier3 evaluate`) into the deterministic Tier 4 domain grader
in `graders/finance/performance_attribution.py`. It parses the actual
`performance.attribution` / `portfolio.positions` / `risk.factor_exposure`
logical-tool JSON responses the agent received during the trial, and
compares them against authoritative ground truth fetched live from
`synthetic_data_pipeline.tools` -- not re-typed constants, so the
comparison stays honest if a fixture changes.

Scope, grounded in the actual eval case content (skills/performance-attribution/evals/evals.json),
not a guessed heuristic:

- GRADABLE_CASES (14 of 25): cases whose prompt asks for a normal reconciled
  attribution answer, where this financial-accuracy grader's checks apply.
  Requires an actual `performance.attribution` tool call in the trajectory;
  `grade_trial` raises a clear, distinguishable error if that call is
  missing rather than guessing or silently scoring 0.
- Of those, POSITION_REQUIRED_CASES (2: performance--008, --019) are the
  ones whose prompt/assertions actually ask about positions or derivatives.
  The other 12 gradable cases ask only about return/attribution/benchmark/
  date/provenance and never mention positions, so `expected_position_ids`
  is left empty for them -- `portfolio_coverage` then scores as
  not-applicable (1.0) rather than penalizing an agent for not enumerating
  positions nobody asked about. This was a real bug found on 2026-08-30:
  with expected_position_ids always populated, performance--011 (asks only
  for absolute/benchmark/active return) scored `portfolio_coverage: 0.0` on
  all 3 attempts even though the agent behaved correctly.
- performance--023 ("coverage" category) was initially included in
  GRADABLE_CASES but removed after checking its real trajectories: its
  prompt only asks the agent to run `portfolio.positions` and confirm
  coverage, and all 3 real attempts consistently and correctly never called
  `performance.attribution` at all -- there is no relative-return/
  contribution evidence to reconcile for this case. It needs a
  positions-only evidence shape this grader does not model, and is treated
  as not gradable here rather than force-fit or silently miscounted as a
  failure.
- The remaining 11 cases (performance--004, --005, --006, --007, --009,
  --017, --018, --020, --021, --022, --023) test refusal, disclosure, or
  handling of deliberately broken/ambiguous/missing data, or (for --023) use
  a positions-only evidence shape this grader does not model. Correct
  behavior for the refusal/disclosure cases is often to decline, ask a
  clarifying question, or flag a problem rather than produce a full
  reconciled answer -- this grader is not designed to judge that behavior
  and does not attempt to.

Usage:
    python skills/performance-attribution/evals/tier3_trial_extractor.py <trial_dir>

<trial_dir> is a with-skill trial directory under a Tier 3 run's
`_harbor-jobs/<skill>-<agent>-with/<case>__<hash>/` path, containing
`agent/trajectory.json` and `config.json` (for `trial_name`, used to
recover the case id).
"""
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from graders.finance.performance_attribution import grade  # noqa: E402
from synthetic_data_pipeline.tools import call_tool  # noqa: E402

GRADABLE_CASES = {
    "performance--001", "performance--002", "performance--003",
    "performance--008", "performance--010", "performance--011",
    "performance--012", "performance--013", "performance--014",
    "performance--015", "performance--016", "performance--019",
    "performance--024", "performance--025",
}

POSITION_REQUIRED_CASES = {"performance--008", "performance--019"}

NOT_GRADABLE_CASES = {
    "performance--004", "performance--005", "performance--006",
    "performance--007", "performance--009", "performance--017",
    "performance--018", "performance--020", "performance--021",
    "performance--022", "performance--023",
}


def _extract_json_blobs(text: str) -> list[dict]:
    """Pull every JSON object embedded in a tool observation's text."""
    blobs = []
    for line in text.splitlines():
        line = line.strip()
        if not (line.startswith("{") and line.endswith("}")):
            continue
        try:
            blobs.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return blobs


def extract_observed_tool_outputs(trajectory: dict) -> dict:
    """Walk a trajectory and collect the logical-tool JSON responses seen."""
    attribution = None
    positions = None
    factor_exposure = None
    for step in trajectory.get("steps", []):
        observation = step.get("observation") or {}
        for result in observation.get("results") or []:
            content = str(result.get("content", ""))
            for blob in _extract_json_blobs(content):
                if "relative_return" in blob and "contributions" in blob:
                    attribution = blob
                elif "positions" in blob and "coverage" in blob:
                    positions = blob
                elif "exposures" in blob:
                    factor_exposure = blob
    return {
        "attribution": attribution,
        "positions": positions,
        "factor_exposure": factor_exposure,
    }


def build_evidence(trajectory: dict, case_id: str, requested_as_of: str) -> dict:
    """Build the Tier 4 grader's evidence dict from one real trial."""
    observed = extract_observed_tool_outputs(trajectory)
    attribution = observed["attribution"]
    positions = observed["positions"]
    factor_exposure = observed["factor_exposure"]

    if attribution is None:
        raise ValueError(
            "No performance.attribution tool response found in trajectory; "
            "this extractor only handles trials where the agent actually "
            "called the attribution tool."
        )

    portfolio_id = attribution["portfolio_id"]
    authoritative = call_tool("performance.attribution", portfolio_id=portfolio_id)
    authoritative_positions = call_tool("portfolio.positions", portfolio_id=portfolio_id)

    observed_as_of = [attribution.get("as_of")]
    observed_sources = [attribution.get("source")]
    allowed_sources = [authoritative.get("source"), authoritative_positions.get("source")]
    observed_position_ids = []
    if positions is not None:
        observed_as_of.append(positions.get("as_of"))
        observed_sources.append(positions.get("source"))
        observed_position_ids = [p["id"] for p in positions.get("positions", [])]
    if factor_exposure is not None:
        observed_as_of.append(factor_exposure.get("as_of"))
        observed_sources.append(factor_exposure.get("source"))
        # The agent may legitimately cite risk.factor_exposure as supporting
        # evidence; only fetch its authoritative source when actually seen,
        # so allowed_sources reflects tools this trial really touched.
        authoritative_factor_exposure = call_tool(
            "risk.factor_exposure", portfolio_id=portfolio_id
        )
        allowed_sources.append(authoritative_factor_exposure.get("source"))

    observed_contributions = list(attribution.get("contributions", {}).values())
    authoritative_contributions = list(authoritative.get("contributions", {}).values())

    claims = [attribution.get("relative_return"), *observed_contributions]
    authoritative_values = [
        authoritative.get("relative_return"),
        *authoritative_contributions,
    ]

    # Only require position-level enumeration for cases whose own prompt
    # actually asks about positions/derivatives/coverage. See module
    # docstring: POSITION_REQUIRED_CASES is grounded in evals.json content,
    # not inferred.
    expected_position_ids = (
        [p["id"] for p in authoritative_positions.get("positions", [])]
        if case_id in POSITION_REQUIRED_CASES
        else []
    )

    return {
        "relative_return": attribution.get("relative_return"),
        "contributions": observed_contributions,
        "expected_benchmark": authoritative.get("benchmark"),
        "observed_benchmark": attribution.get("benchmark"),
        "requested_as_of": requested_as_of,
        "observed_as_of_values": [v for v in observed_as_of if v is not None],
        "allowed_sources": [s for s in allowed_sources if s is not None],
        "observed_sources": [s for s in observed_sources if s is not None],
        "expected_position_ids": expected_position_ids,
        "observed_position_ids": observed_position_ids,
        "claims": [c for c in claims if c is not None],
        "authoritative_values": [v for v in authoritative_values if v is not None],
    }


def grade_trial(trial_dir: Path) -> dict:
    """Extract evidence and grade one trial directory. Raises on non-gradable cases."""
    trajectory_path = trial_dir / "agent" / "trajectory.json"
    config_path = trial_dir / "config.json"
    if not trajectory_path.exists():
        raise FileNotFoundError(f"No trajectory.json found at {trajectory_path}")

    config = json.loads(config_path.read_text()) if config_path.exists() else {}
    trial_name = config.get("trial_name", trial_dir.name)
    case_id = trial_name.split("__")[0]

    if case_id in NOT_GRADABLE_CASES:
        raise ValueError(
            f"{case_id} is not gradable by this financial-accuracy grader "
            "(it tests refusal/disclosure behavior, not a reconciled "
            "attribution answer) -- see module docstring."
        )
    if case_id not in GRADABLE_CASES:
        raise ValueError(f"{case_id} is not in the known GRADABLE_CASES set.")

    # All 25 eval cases reference the single ABC/SPX fixture snapshot dated
    # 2026-08-25 (synthetic_data_pipeline/fixtures/portfolio_abc.json);
    # evals.json does not carry a separate structured date field per case.
    requested_as_of = "2026-08-25"

    trajectory = json.loads(trajectory_path.read_text())
    evidence = build_evidence(trajectory, case_id, requested_as_of)
    result = grade(evidence)
    return {
        "trial_dir": str(trial_dir),
        "case_id": case_id,
        "trial_name": trial_name,
        "evidence": evidence,
        "result": result,
    }


def main() -> int:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <trial_dir>", file=sys.stderr)
        return 2
    trial_dir = Path(sys.argv[1])
    output = grade_trial(trial_dir)
    print(json.dumps(output, indent=2))
    return 0 if output["result"]["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
