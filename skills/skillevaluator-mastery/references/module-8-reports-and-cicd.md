# Module 8: Reading Reports, CI/CD, and Real Bugs

Teach these points one at a time, grounded in
`docs/15_SKILLS_AND_SKILLEVALUATOR_REFERENCE.md` §2, §6-7 and
`framework/adapters/nvidia_skillevaluator.py`.

## Two different report shapes to know

- **Raw NVIDIA JSON** — Tier 3 ("agent-eval") reports carry `agents` (agent
  name → `dimensions_with_skill`, `lift`, `pass_at_k`); Tier 1-only reports
  instead carry `quality_summary` (per-dimension scores) and a `results`
  list including a "Security Scan" validator entry.
- **This repository's normalized contract** — produced by
  `framework/adapters/nvidia_skillevaluator.py`'s `parse_nvidia_report`,
  which converts either raw shape into a stable internal schema
  (`generic_metrics`, `skill_lift`, `reliability`, `findings`,
  `certification: {status: "UNASSESSED"}`). Downstream certification logic
  never touches vendor-specific fields directly — this is what makes a
  future evaluator version bump a contained, testable event instead of a
  library-wide breaking change.

**Never conflate the two** — if asked "what does the report look like,"
clarify which one is meant.

## CI/CD integration this repository actually runs

`.github/workflows/skills-quality.yml`:
- `tier1` — blocks a PR on Tier 1 validation failure across changed skills;
  also runs a real ownership-enforcement check
  (`framework/certification/check_ownership.py`) that fails on the literal
  `domain-owner-required` placeholder. No API keys required.
- `similarity` — real as of this repo's own history, applies
  `policies/similarity.yaml` governance actions against the central
  catalog, blocking only on `EXACT_DUPLICATE`.
- `tier3-fast`, `domain-graders` — documented placeholders, not fully built;
  this repository's own recommendation is to keep Tier 3 **advisory, not
  blocking**, on every PR (too slow/expensive to gate routine merges) and
  reserve blocking Tier 3 for an explicit release/certification workflow.

## Real bugs this repository found and worked around

1. An agent-compatibility gap in the evaluator's Tier 3 execution heuristic
   (a shell tool self-reporting as `exec`, a string the recognized-tool-name
   list didn't include).
2. A judge token-truncation bug (`max_tokens=1024`, no retry) in the
   evaluator's own judge code, found by reading its vendored source —
   patched locally, tracked in `patches/`.
3. A missing `--copy-repo` CLI flag (an operator error, not an evaluator
   bug) that left the sandbox unable to find the repo's own tool bridge.
4. API credit exhaustion mid-run — an operating-cost lesson, not a bug.

**Lesson:** at "Experimental" support level, budget time to read the
evaluator's own source when something looks wrong rather than assuming the
skill under test is broken.

## Quiz (5+ questions, use ask_user with 4 choices each)

Ask about: the two report shapes, why the normalized adapter exists, which
CI job is blocking vs. advisory, and at least one of the four real bugs.
