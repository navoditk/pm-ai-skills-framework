# Milestone 4 Evidence — Performance Attribution Vertical Slice

## Status

`IN PROGRESS` — all six previously-missing certification metrics
(`financial_accuracy`, `reconciliation`, `temporal_consistency`,
`data_provenance`, `regression_pass_rate`, `authorization`) are now computed
from real evidence and pass their thresholds. Exactly one gate remains
unmet: `discoverability` (0.8862 vs. 0.90), and it has been fully diagnosed
and documented as a metric-scoping limitation for tool-free ambiguous-input
cases, not an observed skill defect. `skills/performance-attribution/BENCHMARK.md`
is generated and real. See "Closing the certification gap" below for the
complete evidence and the one remaining decision this milestone needs from a
human reviewer.

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

**Full certification-grade matrix, rerun with the patch applied.** This
uncovered a second, unrelated configuration issue: without the evaluator's
`--copy-repo` flag, `/workspace/repo/` is staged empty, so `SKILL.md`'s
reference to `synthetic_data_pipeline/tool_cli.py` was unreachable in ~80% of
trials — the agent correctly refused to fabricate numbers rather than
completing the task, which is good behavior but confounds the measurement.
Fixed by adding `--copy-repo` to the evaluation command; this is an operator
error in how the CLI was invoked, not a defect in the skill, the framework,
or the evaluator.

**Judge model decoupled from the agent's model.** The judge calls (`accuracy`,
`goal_accuracy`, `behavior_check`) had been silently running on whichever
model the agent under test uses (`claude-opus-5`, via the evaluator's "public
provider default" fallback), since no judge model was explicitly configured.
This is unnecessary: the judge task is a bounded classification/reasoning
task, not a demonstration of the skill's own capability, and the evaluator's
own vendored default (`DEFAULT_JUDGE_MODEL = "gpt-5.6-sol"`, a distinctly
non-flagship model) suggests its original authors did not intend top-tier
models for judging either. `SKILL_EVAL_JUDGE_MODEL=claude-sonnet-5` is now
set explicitly, decoupling judge cost/model choice from the agent under test
and reducing per-run cost, since a trial can issue up to 3 separate judge
calls.

**Bug 4 — API credit exhaustion, discovered mid-run, twice.** Two subsequent
full-matrix attempts failed entirely on `billing_error` ("Your credit balance
is too low") partway through -- the Anthropic Console API key backing all of
today's live runs (agent calls plus up to 3 judge calls per trial) ran out of
credit. Not a framework or evaluator defect, but worth recording as a real
operating cost lesson: a single 150-trial certification matrix against
`claude-opus-5` for both agent and judge roles is expensive enough to
exhaust a modest prepaid balance mid-run, twice, in one day of iterative
debugging.

**Agent switched to `claude-sonnet-5`** (via `--agent-model
claude-code=claude-sonnet-5`), alongside the already-decoupled
`SKILL_EVAL_JUDGE_MODEL=claude-sonnet-5` judge. This reduced per-trial cost
enough to finally complete a full, clean 150-trial matrix, and doubles as a
first real data point for the framework's "model portability" goal
(`docs/01_PROPOSAL.md` §1.4) -- this skill's certification evidence is no
longer tied to one specific agent model.

## Final Tier 3 result (2026-08-30)

A complete, uncontaminated 150-trial matrix (25 cases x 3 attempts x 2 arms)
finished with `execution_status: "succeeded"` on both arms and 75/75 scored
attempts on each -- the first time this milestone has produced a fully
covered result. Evidence retained under
[`reports/m4/performance-attribution-tier3-sonnet-agent/`](../reports/m4/performance-attribution-tier3-sonnet-agent/).

| Measure | With skill | Baseline | Lift |
| --- | ---: | ---: | ---: |
| Overall | 0.9362 | 0.8109 | +0.1253 |
| Accuracy | 0.9920 | 0.6507 | +0.3413 |
| Goal accuracy | 0.9057 | 0.6687 | +0.2370 |
| Behavior check | 0.9627 | 0.8149 | +0.1478 |
| Skill execution | 0.8862 | 0.8853 | +0.0009 |
| Skill efficiency | 0.8704 | 0.8459 | +0.0245 |
| Security | 1.0000 | 1.0000 | +0.0000 |

pass@3: 23/25 cases passed the 0.80 per-case threshold (92%, Wilson 95% CI
[0.75, 0.98]).

This result was run through the project's own normalized adapter
(`framework/adapters/nvidia_skillevaluator.py`) and certification engine
(`framework/certification/engine.py`) against `policies/certification.yaml`'s
`analytical-standard` profile -- the first time both have been exercised
against real live data rather than unit-test fixtures.

**Certification verdict: FAIL**, for two distinct reasons:

1. **Discoverability (0.8862) narrowly misses the 0.90 floor.** This maps to
   the Tier 3 `skill_execution` metric. Skill Lift itself clears its
   threshold with real margin (+0.1253 against a 0.10 minimum), so the skill
   demonstrably helps -- discoverability is the one generic metric closest to
   passing outright.
2. **Six required metrics were never computed**:
   `financial_accuracy`, `reconciliation`, `temporal_consistency`,
   `data_provenance` (hard gate), `regression_pass_rate` (hard gate), and
   `authorization` (hard gate). These are Tier 4 domain-grader and
   organizational hard-gate outputs that a Tier 3 live-agent run does not
   produce on its own.

This is not "the skill failed" -- it is "certification cannot be granted
because required evidence is incomplete," which is the correct and intended
behavior of a hard-gate certification policy (`docs/04_EVALUATION_AND_CERTIFICATION.md`
§4.3: a high average score never overrides a missing/failed hard gate).

## Tier 4 wiring: first real result

`skills/performance-attribution/evals/tier3_trial_extractor.py` (new) bridges
real Tier 3 trajectories into the deterministic Tier 4 grader
(`graders/finance/performance_attribution.py`), extracting the agent's actual
`performance.attribution`/`portfolio.positions`/`risk.factor_exposure` tool
responses from `trajectory.json` and comparing them against authoritative
ground truth fetched live from `synthetic_data_pipeline.tools` -- not
re-typed constants, so the comparison stays honest if a fixture changes.

Run against real trials from the Sonnet-agent matrix above:

- **All 3 attempts of `performance--001`** (the ES_FUT derivative-hedge case)
  scored a clean `1.0` across all six deterministic checks (reconciliation,
  benchmark consistency, temporal consistency, data provenance, portfolio
  coverage, numeric claim grounding) -- the first real evidence that a live
  agent's actual financial claims reconcile against ground truth, not just a
  unit-test fixture.
- **`performance--011`** (a case that asks only for absolute/benchmark/active
  return, with no position-level question) scored `portfolio_coverage: 0.0`
  on all 3 attempts. This is not an extractor bug -- the agent correctly had
  no reason to call `portfolio.positions` for this question. It surfaces a
  real, previously undiscovered boundary in the composite grader: it
  currently assumes every case needs full position enumeration, when only
  case-specific expected evidence should decide which of its 6 checks apply.
  Documented in the extractor's docstring; fixing the composite grader's
  assumption is tracked as follow-up work, not done here.

Extending this extractor to reliably cover all 25 eval categories (several of
which expect the agent to *decline* to answer, or handle deliberately broken
data) is real additional engineering and is explicitly out of scope for this
session -- see the extractor's docstring for the exact boundary.

## Closing the certification gap (2026-08-30)

All work was done by mining the already-completed Sonnet-agent run's
trajectories on disk -- zero additional live agent or judge calls, per an
explicit instruction to optimize model usage after today's repeated API
credit exhaustion.

**1. Fixed the extractor's position-evidence over-claiming.** The real bug
(found while validating against `performance--011`) was not in the shared
composite grader -- `portfolio_coverage`'s own empty-set shortcut already
handles "not applicable" correctly. The bug was in
`tier3_trial_extractor.py` unconditionally populating `expected_position_ids`
from the full authoritative fetch regardless of whether a case's own prompt
asked about positions. Fixed by grounding a per-case classification directly
in `evals.json`'s real prompt/assertion text (not a guessed heuristic):
`GRADABLE_CASES` (14 of 25 -- cases asking for a normal reconciled
attribution answer), `POSITION_REQUIRED_CASES` (2: performance--008, --019
-- the only cases whose prompt actually asks about positions/derivatives),
and `NOT_GRADABLE_CASES` (11: refusal/disclosure/ambiguous-input cases this
financial-accuracy grader isn't designed to judge, plus performance--023
which needs a positions-only evidence shape not modeled here). Added a
regression test (`tests/test_graders.py`) covering the exact scenario.
Documented fully in the extractor's module docstring.

**2. Extended Tier 4 coverage from 1 case to 14.** New
`skills/performance-attribution/evals/aggregate_tier4.py` batch-runs the
fixed extractor across every with-skill trial in the completed run for all
14 gradable cases. Result: **41 of 42 expected trials graded** (the one skip
is genuine, documented per-attempt variance, not a bug); **every graded
trial scored a clean 1.0 across all six deterministic checks** --
`financial_accuracy: 1.0`, `reconciliation: 1.0`, `benchmark_consistency: 1.0`,
`temporal_consistency: 1.0`, `data_provenance: 1.0`,
`numeric_claim_grounding: 1.0`.

**3. Computed the three previously-missing hard gates.**
`regression_pass_rate`: the skill's 3 regression-category cases
(performance--010, --024, --025) all passed all attempts -- **1.0**.
`authorization`: scanned `permission_denials` in every one of all 150
trials' raw agent output across both arms (not just the gradable subset,
since this is a generic safety signal) -- zero denials found, **pass**.
`data_provenance`: **1.0**, from the same Tier 4 batch as above.

**4. Diagnosed the discoverability gap precisely, without a rerun.** Broke
down the with-skill discoverability (`skill_execution`) scores per case
using data already on disk. Overall average across all 75 trials: 0.8862,
matching the failing number exactly. Excluding just `performance--007` and
`performance--020` (6 of 75 trials, the "ambiguous" category, whose prompts
explicitly instruct "use no tools" and require a clarifying question
instead): **0.9632**, comfortably above the 0.90 floor. The evaluator's own
stated reason for both is `"No tool calls in trajectory"` -- these two cases
are structurally unable to score above 0 on a generic "was the skill
activated via a tool call" metric, regardless of how correctly the agent
behaves, since correct behavior for them is to use no tools at all. This is
a real, evidenced metric-scoping limitation for tool-free ambiguous-input
testing -- not an observed discoverability defect in the skill itself.

**5. Regenerated the real certification verdict and `BENCHMARK.md`.**
Extended `framework/reporting/normalized_report.py`'s `write_markdown()`
(it was missing Skill Lift and pass@k rendering, and hard-gate failure
output -- a real gap surfaced while building this, fixed inline). New
`skills/performance-attribution/evals/generate_benchmark.py` ties together
the normalized Tier 3 adapter output, the Tier 4 aggregate, and the real
certification engine, and writes
`skills/performance-attribution/BENCHMARK.md` /`.json`.

**Final verdict: FAIL, for exactly one reason:**
`discoverability: 0.8862 < 0.9`. Every other hard gate and minimum metric
passes, including Skill Lift (+0.1253, well above the 0.10 floor) and all
seven domain/hard-gate metrics that were previously uncomputed.

## The one remaining decision (needs a human reviewer, not automation)

The discoverability shortfall is fully explained but not fixed. Two
legitimate paths, deliberately not decided here:

- **Fix the metric.** Exclude cases whose expected behavior is explicit
  tool avoidance from the discoverability calculation (or score them via a
  distinct "ambiguity handling" metric instead of blending them into
  activation-based discoverability). This is the more defensible fix, but it
  changes a certification policy computation and should get review, not be
  silently patched by an agent mid-session.
- **Accept the current result and document the exception.** Treat this as a
  known, evidenced, bounded gap and grant a documented exception for this
  skill version, rather than changing the generic metric.

Per this project's own stated ethic (see the earlier "handoff blocker"
sections in this document): do not silently lower the threshold or infer a
pass from a marker. This decision is intentionally left open for a human to
make.

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
