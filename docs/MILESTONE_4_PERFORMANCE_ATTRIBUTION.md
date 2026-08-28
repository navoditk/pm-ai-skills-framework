# Milestone 4 Evidence — Performance Attribution Vertical Slice

## Status

`IN PROGRESS` — implementation, static evaluation, and a complete live Tier 3
matrix are complete; certification remains open because the agent did not meet
the evaluator's execution-efficiency threshold.

## What this milestone is meant to prove

One complete financial skill should move through the framework: a user asks why
a portfolio differed from its benchmark, the agent uses approved data, finance
graders verify the answer, and the framework retains a reproducible certification
and benchmark record.

## Completed evidence

### Skill package

`skills/performance-attribution/` now contains the refined instructions, explicit
logical-tool dependencies, 25 evaluation cases, Harbor configuration, and a
custom grader hook.

The 25 cases cover activation, non-activation, ambiguity, missing and stale data,
tool failure, benchmark/date checks, provenance, numeric grounding, derivatives,
coverage, reconciliation, and regression behavior.

### Deterministic domain grading

[`graders/finance/performance_attribution.py`](../graders/finance/performance_attribution.py)
combines six checks:

- attribution reconciliation;
- benchmark consistency;
- temporal consistency;
- data provenance;
- portfolio coverage;
- numeric claim grounding.

The authoritative `ABC` fixture passes all six checks, including the `ES_FUT`
derivative position and the -0.21% relative-return reconciliation.

### Tier 1

Run from the repository root:

```bash
.venv/bin/skillevaluator validate skills/performance-attribution \
  --no-dedup -r json,markdown,html \
  -o reports/m4/performance-attribution-tier1
```

Result: **11/11 checks passed**. The raw JSON, Markdown, HTML, and generated
benchmark output are retained in
[`reports/m4/performance-attribution-tier1/`](../reports/m4/performance-attribution-tier1/).

### Tier 2

Run with an embedding provider configured:

```bash
.venv/bin/skillevaluator similarity-check skills/performance-attribution \
  --save-catalog catalogs/performance-attribution-catalog.json \
  -r cli,json,markdown -o reports/m4/performance-attribution-tier2
```

Result: **3 checks passed**. The similarity report is retained in
[`reports/m4/performance-attribution-tier2/`](../reports/m4/performance-attribution-tier2/).

### Tier 3 live matrix

The synthetic pipeline is now exposed to the Harbor sandbox through the staged
CLI adapter at [`synthetic_data_pipeline/tool_cli.py`](../synthetic_data_pipeline/tool_cli.py).
The full 25-case with-skill/baseline matrix completed with Docker and credential
validation successful. Reproducible artifacts are retained under
[`reports/m4/performance-attribution-tier3-normal-timeout/`](../reports/m4/performance-attribution-tier3-normal-timeout/).

The evaluator produced these headline results:

| Measure | With skill | Baseline | Lift |
| --- | ---: | ---: | ---: |
| Overall | 0.7565 | 0.7462 | +0.0103 |
| Goal accuracy | 0.9832 | 0.9492 | +0.0340 |
| Behavior check | 0.9920 | 0.9760 | +0.0160 |
| Skill execution | 0.50 | 0.48 | +0.02 |
| Skill efficiency | 0.08 | 0.08 | +0.00 |

This is useful evidence, but it is not a certification pass: only 2 of 25
with-skill cases met the configured 0.80 pass threshold, and efficiency was
below the configured minimum. The evaluator specifically reported little
evidence that the agent read or explicitly executed `SKILL.md`. The result is
therefore a valid diagnostic Tier 3 run, not a certified benchmark.

An explicit-injection rerun using `--include-skills` and group workspace mode
completed successfully under
[`reports/m4/performance-attribution-tier3-explicit-skill-group/`](../reports/m4/performance-attribution-tier3-explicit-skill-group/),
but produced the same execution signal. The runtime fix then added a
with-skill-only `/workspace/AGENTS.md` bootstrap through Harbor's pre-agent
setup healthcheck, while the baseline removes that file.

The bootstrap matrix completed end to end under
[`reports/m4/performance-attribution-tier3-bootstrap-concurrent/`](../reports/m4/performance-attribution-tier3-bootstrap-concurrent/).
Its detailed trajectory evidence confirms that the agent read the skill first
and used the attribution tools. However, the pinned evaluator's generic
execution/efficiency summary still reports no skill read and scores efficiency
at `0.08`. The Codex trajectory records the tool as `exec`, while the bundled
heuristic recognizes `bash`, `execute`, `exec_command`, `run_code`, `run`,
`shell`, and `command`, but not the bare `exec` wrapper. This is the remaining
evaluator-compatibility blocker.

## Handoff blocker for the next session

The remaining blocker is specifically a compatibility gap between the pinned
NVIDIA SkillEvaluator `0.2.1` Harbor verifier and Codex's trajectory format.

### Confirmed facts

- Credentials are valid; Docker preflight and model validation pass.
- The synthetic data interface is callable through
  `synthetic_data_pipeline/tool_cli.py`.
- The with-skill bootstrap creates `/workspace/AGENTS.md`, and the detailed
  trajectory shows Codex reading `/workspace/skills/performance-attribution/SKILL.md` first.
- The detailed trajectory also shows successful attribution tool calls and
  correct reconciled answers.
- The evaluator summary still reports `skill_execution: 0.50` and
  `skill_efficiency: 0.08`, with the reason that no `SKILL.md` was read.

### Root cause

The verifier's routing and efficiency logic recognizes execution actions such
as `bash`, `execute`, `exec_command`, `run_code`, `run`, `shell`, and `command`,
but not Codex's bare `exec` action. Codex's nested `tools.exec_command(...)`
calls therefore appear in the trajectory but are not counted consistently by
the generic execution/efficiency metrics.

### Recommended next-session work

1. Inspect the pinned evaluator implementation at
   `.venv/lib/python3.13/site-packages/skillevaluator/tier3/harbor/templates/eval.py`.
2. Add `exec` to the evaluator's execution-action compatibility set, or apply
   the equivalent upstream evaluator upgrade/patch.
3. Add a regression test proving that a Codex `function_name: "exec"` call
   containing `cat /workspace/skills/performance-attribution/SKILL.md` counts
   as both a skill read and a productive execution call.
4. Rerun the full matrix using the existing bootstrap configuration and retain
   the report under a new timestamped directory.
5. Run the certification profile with three attempts, normalize the result,
   apply `policies/certification.yaml`, and generate `BENCHMARK.md` only after
   the generic metrics are trustworthy.

Do not lower certification thresholds or infer success from the final response
marker. The current diagnostic evidence is retained under
`reports/m4/performance-attribution-tier3-bootstrap-concurrent/`.

### Local tests

```bash
.venv/bin/pytest -q
```

Result: **18 passed**.

## Remaining certification work

The original Tier 3 stall was investigated. It was caused by the container not
having a callable synthetic data interface, not by missing credentials. The
staged CLI adapter resolves that access issue, and the normal-timeout matrix now
completes end to end.

Before certification, the skill activation/execution contract needs to be
strengthened and rerun. The remaining required evidence is a passing repeated
Tier 3 matrix, normalized PM AI output, `BENCHMARK.md`, and a certification
verdict. The earlier stalled diagnostic artifacts remain under
[`reports/m4/performance-attribution-tier3/`](../reports/m4/performance-attribution-tier3/).

Milestone 5 must not begin until this evidence and certification path is complete.
