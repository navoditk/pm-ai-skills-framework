"""Extract Tier 4 grading evidence from a real Tier 3 Harbor trial directory.

This bridges live-agent Tier 3 evidence (trajectory.json, produced by
`skillevaluator tier3 evaluate`) into the deterministic Tier 4 domain grader
in `graders/finance/performance_attribution.py`. It parses the actual
`performance.attribution` and `portfolio.positions` logical-tool JSON
responses the agent received during the trial, and compares them against the
authoritative ground truth from `synthetic_data_pipeline.tools` -- not
against re-typed constants, so the comparison stays honest if a fixture
changes.

Scope: this handles the `explicit-positive` case shape, where the agent is
expected to call the attribution/positions tools and produce a reconciled
answer. It does not (yet) generalize to the other eval categories in
evals.json (ambiguous-input, tool-failure, missing-data, etc.), which have
different expected behaviors -- for example, correctly declining to answer is
the *right* outcome for a tool-failure case, and this extractor would need
different ground truth per category to grade those correctly. Extending this
to the full 25-case set is tracked as follow-up work, not done here.

Known finding from the first real run (2026-08-30): validated clean (score
1.0, all 6 checks pass) against all 3 attempts of `performance--001`, which
asks about the ES_FUT derivative hedge and so legitimately requires
position-level detail. Running it against `performance--011` (the other
explicit-positive case, which asks only for absolute/benchmark/active
return with no position-level question) scored `portfolio_coverage: 0.0` on
all 3 attempts -- correctly, because the agent had no reason to call
`portfolio.positions` and did not. This is not an extractor bug; it is a
real boundary in `graders/finance/performance_attribution.py`'s composite
grader: it currently assumes every case needs full position enumeration,
when in fact only case-specific expected evidence should decide which of
the 6 component checks apply. Fixing that composite-grader assumption is
tracked as a follow-up, not addressed here.

Usage:
    python skills/performance-attribution/evals/tier3_trial_extractor.py <trial_dir>

<trial_dir> is a with-skill trial directory under a Tier 3 run's
`_harbor-jobs/<skill>-<agent>-with/<case>__<hash>/` path, containing
`agent/trajectory.json`.
"""
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from graders.finance.performance_attribution import grade  # noqa: E402
from synthetic_data_pipeline.tools import call_tool  # noqa: E402

_JSON_OBJECT_RE = re.compile(r"\{.*\}")


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


def build_evidence(trajectory: dict, requested_as_of: str) -> dict:
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

    return {
        "relative_return": attribution.get("relative_return"),
        "contributions": observed_contributions,
        "expected_benchmark": authoritative.get("benchmark"),
        "observed_benchmark": attribution.get("benchmark"),
        "requested_as_of": requested_as_of,
        "observed_as_of_values": [v for v in observed_as_of if v is not None],
        "allowed_sources": [s for s in allowed_sources if s is not None],
        "observed_sources": [s for s in observed_sources if s is not None],
        "expected_position_ids": [
            p["id"] for p in authoritative_positions.get("positions", [])
        ],
        "observed_position_ids": observed_position_ids,
        "claims": [c for c in claims if c is not None],
        "authoritative_values": [v for v in authoritative_values if v is not None],
    }


def main() -> int:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <trial_dir>", file=sys.stderr)
        return 2
    trial_dir = Path(sys.argv[1])
    trajectory_path = trial_dir / "agent" / "trajectory.json"
    if not trajectory_path.exists():
        print(f"No trajectory.json found at {trajectory_path}", file=sys.stderr)
        return 2

    trajectory = json.loads(trajectory_path.read_text())

    config_path = trial_dir / "config.json"
    requested_as_of = "2026-08-25"
    if config_path.exists():
        config = json.loads(config_path.read_text())
        prompt = str(config.get("prompt") or config.get("instruction") or "")
        match = re.search(r"\d{4}-\d{2}-\d{2}", prompt)
        if match:
            requested_as_of = match.group(0)

    evidence = build_evidence(trajectory, requested_as_of)
    result = grade(evidence)

    print(json.dumps({"trial_dir": str(trial_dir), "evidence": evidence, "result": result}, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
