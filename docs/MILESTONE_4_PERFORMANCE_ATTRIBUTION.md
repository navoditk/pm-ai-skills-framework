# Milestone 4 Evidence — Performance Attribution Vertical Slice

## Status

`IN PROGRESS` — the Codex execution-efficiency blocker documented below has
been root-caused to a Codex-specific trajectory format and resolved by
switching the Tier 3 agent to `claude-code`. Live confirmation is complete at
smoke scale and at full-skill scale (single attempt); the full 3-attempt
certification-grade matrix is running as of 2026-08-28 and this document will
be updated with its result. See "Resolution: switching Tier 3 agent to
claude-code" below.

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

## Resolution: switching Tier 3 agent to claude-code

The root cause identified above — the pinned evaluator's execution/efficiency
heuristic not recognizing Codex's bare `exec` trajectory action — is specific
to Codex, not a limitation of the evaluator or of this skill. This was
confirmed two ways:

**Static confirmation.** `claude-code` is a first-class supported Harbor agent
in this exact pinned SkillEvaluator version
(`skillevaluator/tier3/harbor/__init__.py`:
`LOCAL_HARBOR_AGENTS = frozenset({"claude-code", "codex", "opencode"})`).
Claude Code's Harbor integration
(`harbor/agents/installed/claude_code.py`) sources each trajectory step's
`function_name` directly from the Claude API's native `tool_use` block name —
its built-in tools are literally named `Bash` and `Read`, which the
evaluator's execution/read hint sets already recognize case-insensitively
(`skillevaluator/tier3/harbor/templates/eval.py`:
`_EXECUTION_TOOL_HINTS`/`_BEHAVIOR_EXEC_TOOLS` include `bash`;
`_READ_TOOL_HINTS` includes `read`). Codex's shell tool, by contrast, reports
itself as `exec` — absent from both hint sets — which is why the evaluator's
own source code carries a comment specifically calling out Codex's shell-based
file reads as a special case requiring extra handling.

**Live confirmation.** Two real runs against the pinned `0.2.1` evaluator with
`claude-code` as the Tier 3 agent (credentials: `anthropic` provider,
`claude-opus-5`):

1. *Smoke fixture* (`skills/m1-tier3-smoke`, the same fixture that first
   surfaced the Codex bug in Milestone 1) —
   `reports/m4/claude-code-smoke-validation/`: skill execution **1.00**
   ("Activated via Skill tool: m1-tier3-smoke"), efficiency **1.00**
   ("1/1 productive calls, 100%"), overall Skill Lift **+0.58**
   (1.00 with-skill vs. 0.42 baseline), exit 0. Claude Code has a native
   `Skill` tool the evaluator recognizes directly — an even cleaner signal
   than the `Bash`/`Read` name match the static analysis predicted.
2. *Full Performance Attribution case set, single attempt*
   (`reports/m4/performance-attribution-tier3-claude-code-quick/`): across all
   25 with-skill trials, `skill_execution` and `skill_efficiency` are
   populated and vary meaningfully by case (mostly 0.83-1.0, matching real
   skill-use quality per case) — nothing like Codex's flat `0.08` floor. Two
   trials scored `skill_execution: 0.0`, plausibly intentional
   non-activation/negative cases in the eval set rather than a new defect
   (not yet confirmed against `evals.json` case categories).

This run also surfaced a second, unrelated issue: 9 of 25 with-skill trials
and 3 of 25 baseline trials failed with `"Judge response was not a valid JSON
object"` on the `accuracy`/`goal_accuracy` dimensions specifically (an
LLM-judge call, distinct from the deterministic execution/efficiency
verifier).

**This second issue turned out not to be self-healing at `n_attempts: 3` as
first hoped.** A full 150-trial certification-grade run
(`reports/m4/performance-attribution-tier3-claude-code-final/`) still failed
on both arms (`execution_status: "failed"`, `overall_score: null`), with 19 of
75 with-skill attempts and 18 of 75 baseline attempts hitting the same judge
error — including two cases (`performance--008`, `performance--014`) that lost
**all 3** attempts. Root cause, confirmed by reading the pinned evaluator's
source: `judge_accuracy` and `_judge_goal_accuracy_custom`
(`skillevaluator/tier3/harbor/templates/eval.py`) call the judge LLM with the
library default `max_tokens=1024` and no retry. A substantive financial
answer's 5-criterion judge reasoning routinely exceeds 1024 tokens before the
closing JSON brace, truncating the response. This is not random: the
evaluator's own `judge_behavior_check`, in the same file, already had this
exact failure mode fixed (`BEHAVIOR_JUDGE_MAX_TOKENS = 4096` plus a retry,
with a code comment describing the identical truncation symptom) — the fix
was simply never extended to the other two judges, which is why cases with
longer expected judge reasoning failed consistently rather than randomly.

**Fix applied:** `patches/skillevaluator-0.2.1-judge-max-tokens.patch` raises
both judges to the same `max_tokens=4096` budget and adds the same one-retry
pattern already proven for `judge_behavior_check`. Verified to apply cleanly
and reproduce the live fix exactly. See `docs/13_NVIDIA_EVALUATOR_UPGRADE_POLICY.md`
§13.6 for the full writeup and upstream-fix tracking; `docs/MILESTONE_1_SETUP.md`
now includes the patch step as part of the reproducible install.

**Full certification-grade matrix, rerun with the patch applied.** Result
pending — this document will be updated with the completed Skill Lift table,
pass-threshold count, and certification verdict once it finishes.

**Items 1-3 of "Recommended next-session work" above (patching the pinned
evaluator's execution-action allowlist) are no longer necessary** — the
compatibility gap is avoided by agent choice, not by modifying the evaluator.
The gap itself remains logged as a known issue for Codex specifically in
`docs/13_NVIDIA_EVALUATOR_UPGRADE_POLICY.md` §13.6, since a future milestone
or a different consuming repository may still want to use Codex as a Tier 3
agent.

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

With the execution-heuristic blocker resolved by switching to `claude-code`
(see above), the remaining work to close out Milestone 4 is: let the running
3-attempt matrix finish, normalize its output through the PM AI adapter, apply
`policies/certification.yaml`, and generate `BENCHMARK.md`.

Milestone 5 must not begin until this evidence and certification path is complete.
