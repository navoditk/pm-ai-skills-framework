"""Extract Tier 4 grading evidence from a real Tier 3 Harbor trial directory.

Bridges live-agent Tier 3 evidence (`trajectory.json`) into the deterministic
Tier 4 domain grader in `graders/finance/portfolio_overview.py`. It parses the
actual `portfolio.summary` / `portfolio.positions` / `benchmark.positions`
logical-tool JSON responses the agent received during the trial, and compares
them against authoritative ground truth fetched live from
`synthetic_data_pipeline.tools` -- not re-typed constants, so the comparison
stays honest if a fixture changes.

Directory layout note: this run's completed trial directories
(`reports/m5/portfolio-overview-tier3-sonnet/.../claude-code/with-skill/trials/<case>__<hash>/`)
place `trajectory.json` and `claude-code.txt` directly in the trial directory,
not under an `agent/` subfolder as Performance Attribution's equivalent
extractor found -- a real, observed layout difference between runs, not a
guess.

Scope, grounded in the actual eval case content (skills/portfolio-overview/evals/evals.json):

- GRADABLE_CASES (15 of 25): cases whose prompt asks for a normal reconciled
  portfolio-overview answer -- summary, composition, benchmark identity, or a
  PM note -- where this grader's checks apply. Requires an actual
  `portfolio.summary` or `portfolio.positions` tool call in the trajectory.
- Of those, POSITION_REQUIRED_CASES (11: portfolio-ov-001, -004, -012, -013,
  -016, -018, -020, -021, -022, -023, -025) are the ones whose prompt or
  assertions actually ask about composition, positions, derivatives, or
  sector classification. The other 4 gradable cases (-002, -003, -017, -019)
  ask only about return/benchmark identity and never mention positions, so
  `expected_position_ids` is left empty for them -- `portfolio_coverage`
  scores as not-applicable (1.0) rather than penalizing an agent for not
  enumerating positions nobody asked about (the same real bug class found on
  Performance Attribution on 2026-08-30).
- portfolio-ov-020 ("compare ABC's AAPL weight to SPX's AAPL weight") is
  gradable and also exercises `benchmark.positions` -- confirmed by reading
  a real trial's trajectory, the agent called `benchmark.positions` even
  though it is not in `portfolio-overview/skill.yaml`'s declared tool list;
  the sandboxed `tool_cli.py` bridge exposes all eight logical tools
  regardless of the skill's declared subset, so this is expected, not a
  violation.
- NOT_GRADABLE_CASES (10: -005, -006 unrelated/general; -007 portfolio not
  found; -008 `omit_derivatives` failure mode; -009 `stale_data` failure
  mode; -010, -011 ambiguous/no-tools; -014, -015 tool-failure; -024
  residual-control refusal-explanation) all test refusal, disclosure, or
  correct handling of deliberately broken/ambiguous/missing data. Correct
  behavior is often to decline, disclose a gap, or ask a clarifying question
  rather than produce a full reconciled answer -- this grader compares
  against *unmodified* authoritative truth and is not designed to judge that
  behavior; forcing these cases through it would penalize the agent for
  behaving correctly.

Usage:
    python skills/portfolio-overview/evals/tier3_trial_extractor.py <trial_dir>

<trial_dir> is a with-skill trial directory, e.g.
reports/m5/portfolio-overview-tier3-sonnet/portfolio-overview/<run_id>/claude-code/with-skill/trials/<case>__<hash>/
"""
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from graders.finance.portfolio_overview import grade  # noqa: E402
from synthetic_data_pipeline.tools import call_tool  # noqa: E402

GRADABLE_CASES = {
    "portfolio-ov-001", "portfolio-ov-002", "portfolio-ov-003", "portfolio-ov-004",
    "portfolio-ov-012", "portfolio-ov-013", "portfolio-ov-016", "portfolio-ov-017",
    "portfolio-ov-018", "portfolio-ov-019", "portfolio-ov-020", "portfolio-ov-021",
    "portfolio-ov-022", "portfolio-ov-023", "portfolio-ov-025",
}

POSITION_REQUIRED_CASES = {
    "portfolio-ov-001", "portfolio-ov-004", "portfolio-ov-012", "portfolio-ov-013",
    "portfolio-ov-016", "portfolio-ov-018", "portfolio-ov-020", "portfolio-ov-021",
    "portfolio-ov-022", "portfolio-ov-023", "portfolio-ov-025",
}

NOT_GRADABLE_CASES = {
    "portfolio-ov-005", "portfolio-ov-006", "portfolio-ov-007", "portfolio-ov-008",
    "portfolio-ov-009", "portfolio-ov-010", "portfolio-ov-011", "portfolio-ov-014",
    "portfolio-ov-015", "portfolio-ov-024",
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
    """Walk a trajectory and collect the logical-tool JSON responses seen.

    Distinguished by shape, not call order: `portfolio.summary` has `return`
    and `benchmark` but no `positions`; `portfolio.positions` has `positions`
    + `coverage` + `portfolio_id`; `benchmark.positions` has `positions` +
    `benchmark_id` but no `portfolio_id`/`coverage`.
    """
    summary = None
    positions = None
    benchmark_positions = None
    for step in trajectory.get("steps", []):
        observation = step.get("observation") or {}
        for result in observation.get("results") or []:
            content = str(result.get("content", ""))
            for blob in _extract_json_blobs(content):
                if "return" in blob and "benchmark" in blob and "portfolio_id" in blob:
                    summary = blob
                elif "positions" in blob and "coverage" in blob and "portfolio_id" in blob:
                    positions = blob
                elif "positions" in blob and "benchmark_id" in blob:
                    benchmark_positions = blob
    return {"summary": summary, "positions": positions, "benchmark_positions": benchmark_positions}


def build_evidence(trajectory: dict, case_id: str, requested_as_of: str) -> dict:
    """Build the Tier 4 grader's evidence dict from one real trial."""
    observed = extract_observed_tool_outputs(trajectory)
    summary = observed["summary"]
    positions = observed["positions"]
    benchmark_positions = observed["benchmark_positions"]

    if summary is None and positions is None:
        raise ValueError(
            "No portfolio.summary or portfolio.positions tool response found "
            "in trajectory; this extractor only handles trials where the "
            "agent actually called one of these tools."
        )

    portfolio_id = (summary or positions)["portfolio_id"]
    authoritative_summary = call_tool("portfolio.summary", portfolio_id=portfolio_id)
    authoritative_positions = call_tool("portfolio.positions", portfolio_id=portfolio_id)

    observed_as_of: list[str] = []
    observed_sources: list[str] = []
    allowed_sources = [authoritative_summary.get("source"), authoritative_positions.get("source")]
    claims: list[float] = []
    authoritative_values: list[float] = []
    expected_benchmark = None
    observed_benchmark = None

    if summary is not None:
        observed_as_of.append(summary.get("as_of"))
        observed_sources.append(summary.get("source"))
        expected_benchmark = authoritative_summary.get("benchmark")
        observed_benchmark = summary.get("benchmark")
        claims.append(summary.get("return"))
        authoritative_values.append(authoritative_summary.get("return"))

    observed_position_ids: list[str] = []
    if positions is not None:
        observed_as_of.append(positions.get("as_of"))
        observed_sources.append(positions.get("source"))
        observed_position_ids = [p["id"] for p in positions.get("positions", [])]
        claims.extend(p.get("weight") for p in positions.get("positions", []))
        authoritative_values.extend(
            p.get("weight") for p in authoritative_positions.get("positions", [])
        )

    if benchmark_positions is not None:
        observed_as_of.append(benchmark_positions.get("as_of"))
        observed_sources.append(benchmark_positions.get("source"))
        authoritative_benchmark_positions = call_tool(
            "benchmark.positions", benchmark_id=benchmark_positions.get("benchmark_id")
        )
        allowed_sources.append(authoritative_benchmark_positions.get("source"))
        claims.extend(p.get("weight") for p in benchmark_positions.get("positions", []))
        authoritative_values.extend(
            p.get("weight") for p in authoritative_benchmark_positions.get("positions", [])
        )

    # Only require position-level enumeration for cases whose own prompt
    # actually asks about composition/positions/derivatives. See module
    # docstring: POSITION_REQUIRED_CASES is grounded in evals.json content.
    expected_position_ids = (
        [p["id"] for p in authoritative_positions.get("positions", [])]
        if case_id in POSITION_REQUIRED_CASES
        else []
    )

    return {
        "expected_benchmark": expected_benchmark,
        "observed_benchmark": observed_benchmark,
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
    trajectory_path = trial_dir / "trajectory.json"
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
            "portfolio-overview answer) -- see module docstring."
        )
    if case_id not in GRADABLE_CASES:
        raise ValueError(f"{case_id} is not in the known GRADABLE_CASES set.")

    # All 25 eval cases reference the single ABC/SPX fixture snapshot dated
    # 2026-08-25 (synthetic_data_pipeline/fixtures/portfolio_abc.json).
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
