# 10. Development Roadmap & Progress Tracker

This document is the working execution plan for building the reference implementation.

Update this file in every material pull request.

## Scope decision (2026-08-27)

This framework leverages **NVIDIA SkillEvaluator as the evaluation engine**
and stays scoped to **PM/asset-management skill governance** — it is not
being built as a generic, domain-agnostic skills platform. The near-term
priority is therefore governance controls over the growing PM skill library
(deduplication, ownership enforcement, risk-tiered certification cost) ahead
of breadth (more skills) or generality (more domains). See
`docs/01_PROPOSAL.md` §1.5 for the corresponding non-goal and
`docs/13_NVIDIA_EVALUATOR_UPGRADE_POLICY.md` for how the framework stays
insulated from the one external dependency this scope decision leans on
most heavily. This reprioritizes the "Suggested next three PRs" section at
the bottom of this document; milestone numbering below is unchanged.

Statuses:
- `NOT STARTED`
- `IN PROGRESS`
- `BLOCKED`
- `DONE`

---

## Milestone 0 — Blueprint

**Goal:** establish architecture, standards, use cases, and implementation plan.

Status: `DONE`

Deliverables:
- proposal;
- target architecture;
- skill standard;
- evaluation/certification design;
- implementation plan;
- adoption guide;
- GitHub publishing guide;
- demo/acceptance plan;
- reference/resources guide;
- 12 reference skill scaffolds;
- 120 starter eval cases;
- 6 starter finance graders.

Exit criteria:
- repository has sufficient documentation for an engineer to understand why it exists and how it should be built.

---

## Milestone 1 — Development Environment & NVIDIA Smoke Test

Status: `DONE`

Tasks:
- [x] Pin an NVIDIA SkillEvaluator version: 0.2.1 at commit `009aa300be7925c7ba75760592baeb941cc29ba8`.
- [x] Document supported Python version: 3.13 (SkillEvaluator requires `>=3.12,<3.14`).
- [x] Install SkillEvaluator locally with the `all` extra in `.venv/`.
- [x] Install required Tier 1 scanners: SkillSpector 2.9.6 and Gitleaks 8.30.1.
- [x] Validate Docker availability — Docker CLI 29.6.2 and Docker daemon are ready.
- [x] Validate Harbor setup: Harbor 0.13.2 is installed and the Codex agent is recognized.
- [x] Configure one supported Tier 3 agent: Codex CLI 0.150.0.
- [x] Run Tier 1 against `skills/portfolio-overview` — 11/11 checks passed.
- [x] Run Tier 3 smoke test — one controlled with-skill/baseline evaluation completed in Docker with Codex.
- [x] Capture actual raw NVIDIA report structure in `reports/m1/tier1-v296/`.
- [x] Update `framework/adapters/nvidia_skillevaluator.py` to match pinned CLI exactly.

Exit criteria:
- one skill passes an actual NVIDIA Tier 1 run;
- one controlled Tier 3 evaluation completes in sandbox.

Evidence:
- `reports/m1/tier1-v296/`
- `docs/MILESTONE_1_SETUP.md`
- exact evaluator version: `0.2.1` / commit `009aa300be7925c7ba75760592baeb941cc29ba8`

Current evidence and blockers (2026-08-26):

- `.venv/bin/skillevaluator validate skills/portfolio-overview --no-dedup -r json,markdown,html -o reports/m1/tier1-v296` exits `0`; all 11 Tier 1 checks pass.
- `.venv/bin/skillevaluator tier3 validate skills/portfolio-overview --json` exits `0` after adding the required `schema_version: 1` to the reference eval config.
- `.venv/bin/skillevaluator doctor --agents codex --env-mode docker` passes the OpenAI provider, Codex agent, and Docker checks when credentials are loaded transiently from `/Users/navoditkaushik/GitHub/credentials/keys.rtf` and `OPENAI_BASE_URL=https://api.openai.com/v1` is set.
- The Tier 3 run entered `agent-runtime-preflight` and completed successfully, then entered the real Codex with-skill/baseline execution for 10 cases. It remained there for more than six minutes without a result and was stopped.
- Root cause diagnosis: the retained Codex trace shows it searched for the required `portfolio.summary`/`portfolio.positions` interface and found only the skill metadata; `codex mcp list` reported no configured servers. The sandbox has no Agentic Data Pipeline implementation or fixtures yet, so the first portfolio task cannot complete its required data/tool calls. This is a missing logical-tool access/fixture issue, not an evaluator credential issue.
- The dedicated tool-free smoke evaluation completed in sandbox under `reports/m1/tier3-smoke/m1-tier3-smoke/20260827_045941_96225_9034b0be87e5/`, including with-skill and baseline reports.
- Smoke report caveat: the run completed but returned overall with-skill score `0.6667` and exit `1` against the configured `0.80` threshold. The exact response and goal were correct; SkillEvaluator reported weak skill-execution/efficiency evidence because Codex read the skill with `sed`, which the evaluator did not recognize as skill-use evidence, and the fixture prohibited external tools. This is a smoke-fixture/evaluator-observability issue, not an access failure.
- Milestone 1 exit criteria are satisfied: the reference skill passed Tier 1 and a controlled Tier 3 evaluation completed in a sandbox. Milestone 2 remains untouched.

---

## Milestone 2 — Normalized Framework Contracts

Status: `DONE`

Tasks:
- [x] Finalize `skill.schema.json` with explicit framework manifest requirements and supported risk levels.
- [x] Validate all 12 reference `skill.yaml` files (plus the Milestone 1 smoke manifest).
- [x] Finalize normalized evaluation-result schema with framework/source identity and stable result sections.
- [x] Implement NVIDIA Tier 1/Tier 3 output parser in `framework/adapters/nvidia_skillevaluator.py`.
- [x] Implement benchmark identity/fingerprint in `framework/benchmark/identity.py`.
- [x] Implement provider abstraction tests for exact pinned CLI invocations and normalized output.
- [x] Add framework version field to adapter and normalized output: `0.1.0`.

Exit criteria:
- downstream certification code consumes normalized PM AI results only;
- no downstream code parses NVIDIA raw schema directly.

Evidence (2026-08-26):

- `tests/test_contracts.py` validates all skill manifests, benchmark fingerprint behavior, and normalized-result schema compliance.
- `tests/test_nvidia_skillevaluator.py` validates the provider commands and Tier 3 report normalization.
- Test suite: `9 passed`; changed-file Ruff checks and `git diff --check` pass.
- The NVIDIA parser accepts the actual Tier 1 report captured in `reports/m1/tier1-v296/` and Tier 3 report captured in `reports/m1/tier3-smoke/`.
- Milestone 3 is complete; see the evidence below.

---

## Milestone 3 — Synthetic Agentic Data Pipeline

Status: `DONE`

Tasks:
- [x] Define logical tool interfaces.
- [x] Add deterministic portfolio fixtures.
- [x] Add benchmark fixture.
- [x] Add attribution fixture.
- [x] Add factor-risk fixture.
- [x] Add scenario fixture.
- [x] Add market-data fixture.
- [x] Add controlled failure modes.
- [x] Add stale/mismatched-date fixtures.
- [x] Add derivative position fixture.

Exit criteria:
- all reference skill evaluations can run without production systems.

Evidence (2026-08-26):

- `tests/test_synthetic_pipeline.py` proves the eight stable logical tools, cross-source date consistency, attribution
  reconciliation, scenario and market lookups, and machine-readable failure cases.
- `.venv/bin/python -m pytest -q tests/test_synthetic_pipeline.py` passes `8` tests; the full suite passes `17` tests.
- `synthetic_data_pipeline/fixtures/` contains deterministic portfolio, SPX benchmark, scenario, and market-history
  data, including the `ES_FUT` derivative position.
- `docs/MILESTONE_3_SYNTHETIC_DATA_PIPELINE.md` provides the reproducible setup, expected output, and evidence map.
- Exit criterion is satisfied: the data/tool layer is local and deterministic, so reference skill evaluations no longer
  require production systems for their data calls.
- Milestone 4 is not started.

---

## Milestone 4 — First Vertical Slice: Performance Attribution

Status: `IN PROGRESS`

Tasks:
- [x] Refine SKILL.md.
- [x] Validate with NVIDIA Tier 1.
- [x] Create/update Tier 2 catalog.
- [x] Run candidate similarity.
- [x] Complete 10 initial eval cases.
- [x] Expand to >=25 cases.
- [x] Implement attribution reconciliation grader.
- [x] Implement benchmark consistency grader.
- [x] Implement temporal consistency grader.
- [x] Run with-skill baseline.
- [x] Run without-skill baseline.
- [x] Measure Skill Lift.
- [ ] Run repeated attempts (in progress — see 2026-08-28 evidence).
- [ ] Generate normalized report.
- [ ] Generate BENCHMARK.md.
- [ ] Apply certification policy.

Exit criteria:
- one complete skill flows from source -> eval -> certification -> benchmark report.

Evidence (2026-08-27):

- `skills/performance-attribution/` contains the refined package and 25 cases.
- Tier 1 passes 11/11 checks; Tier 2 passes 3 checks.
- `graders/finance/performance_attribution.py` provides six deterministic domain
  checks, with unit coverage in `tests/test_graders.py`.
- The staged CLI adapter now exposes the synthetic pipeline to Harbor, so the
  full 25-case with-skill/baseline Tier 3 matrix completes with Docker and
  credentials validated. Evidence is retained under
  `reports/m4/performance-attribution-tier3-normal-timeout/`.
- The live result is diagnostic rather than certifying: overall lift is +0.0103,
  goal-accuracy lift is +0.0340, but skill efficiency is 0.08 and only 2/25
  with-skill cases pass the 0.80 case threshold. Milestone 4 remains
  `IN PROGRESS`; repeated runs, normalized reporting, `BENCHMARK.md`, and
  certification are not yet complete.
- Explicit skill injection via `--include-skills`, group workspace mode, and
  the with-skill-only `/workspace/AGENTS.md` bootstrap were verified end to
  end. Detailed trajectory evidence shows the required skill read and
  logical-tool workflow; the remaining mismatch is evaluator recognition of
  Codex's bare `exec` action.
- The with-skill-only bootstrap now produces detailed trajectory evidence of
  the required skill read and logical-tool workflow. The pinned evaluator still
  scores execution/efficiency as if no skill was used because its heuristic does
  not recognize Codex's bare `exec` tool wrapper. Milestone 4 remains
  `IN PROGRESS` pending a compatibility shim or upstream evaluator fix, followed
  by a fresh repeated certification run.
- See `docs/MILESTONE_4_PERFORMANCE_ATTRIBUTION.md` for reproduction commands,
  expected results, and the exact unblock requirement.

Evidence (2026-08-28):

- Root-caused the Codex execution/efficiency blocker to Codex's trajectory
  reporting its shell tool as bare `exec`, which is absent from the pinned
  evaluator's execution-action hint set (confirmed by reading
  `skillevaluator/tier3/harbor/templates/eval.py` and
  `harbor/agents/installed/codex.py` directly).
- Confirmed `claude-code` is a first-class supported Tier 3 agent in this same
  pinned evaluator version, and that its native `Bash`/`Read`/`Skill` tool
  names are already recognized by the same heuristic
  (`harbor/agents/installed/claude_code.py`).
- Live-validated the fix: the Milestone 1 smoke fixture scored
  `skill_execution: 1.00`, `skill_efficiency: 1.00`, Skill Lift `+0.58` with
  `claude-code` (`reports/m4/claude-code-smoke-validation/`), versus the
  `0.6667`/failed result Codex produced on the identical fixture in
  Milestone 1.
- Ran the full 25-case Performance Attribution set at `n_attempts: 1` with
  `claude-code`: `skill_execution`/`skill_efficiency` scored normally and
  varied meaningfully by case across all 25 with-skill trials (no more flat
  `0.08` floor). This run also surfaced a separate, lower-severity finding —
  intermittent LLM-judge JSON-parse failures on the `accuracy`/`goal_accuracy`
  dimensions (see `docs/13_NVIDIA_EVALUATOR_UPGRADE_POLICY.md` §13.6) — which
  suppressed the aggregate score at single-attempt coverage but is expected to
  be absorbed by the certification profile's `n_attempts: 3` redundancy.
- Started the full 3-attempt, 150-trial certification-grade matrix
  (`reports/m4/performance-attribution-tier3-claude-code-final/`); result
  pending as of this update. Remaining Milestone 4 tasks (normalized report,
  `BENCHMARK.md`, certification verdict) are blocked only on that run
  finishing, not on any further code or evaluator changes.

---

## Milestone 5 — Three-Skill Vertical Slice

Status: `NOT STARTED`

Skills:
1. Portfolio Overview
2. Performance Attribution
3. Risk Explanation

Tasks:
- [ ] Complete all three end-to-end.
- [ ] Demonstrate different grader types.
- [ ] Demonstrate routing/discoverability.
- [ ] Demonstrate derivatives handling.
- [ ] Demonstrate data/date failure detection.

Exit criteria:
- common framework works for multiple skill patterns without bespoke pipeline code.

---

## Milestone 6 — Deliberate Defect Demonstration

Status: `NOT STARTED`

Introduce controlled variants:

- [ ] vague skill description -> discoverability degradation;
- [ ] duplicate risk skill -> Tier 2 detection;
- [ ] missing derivatives -> portfolio coverage failure;
- [ ] mismatched dates -> temporal failure;
- [ ] weak/no-value skill -> low Skill Lift;
- [ ] unapproved data source -> provenance failure.

Exit criteria:
- framework catches all deliberately introduced defects;
- reports clearly explain failure mode.

---

## Milestone 7 — Complete 12-Skill Library

Status: `NOT STARTED`

Tasks:
- [ ] Portfolio Overview
- [ ] Performance Attribution
- [ ] Risk Explanation
- [ ] Exposure Analysis
- [ ] Benchmark Comparison
- [ ] Position Investigation
- [ ] Scenario Analysis
- [ ] Market Move Explanation
- [ ] Liquidity Analysis
- [ ] Portfolio Change Analysis
- [ ] Concentration Analysis
- [ ] PM Commentary Generation

Target:
- >=25 cases per skill for initial POC;
- total >=300 cases.

Exit criteria:
- all 12 receive standardized benchmark reports.

---

## Milestone 8 — Finance Grader Library

Status: `NOT STARTED`

Required:
- [ ] Attribution reconciliation
- [ ] Temporal consistency
- [ ] Benchmark consistency
- [ ] Portfolio coverage
- [ ] Data provenance
- [ ] Numeric claim grounding

Extensions:
- [ ] Currency consistency
- [ ] Factor exposure
- [ ] Duration consistency
- [ ] Risk contribution
- [ ] Scenario consistency
- [ ] Derivative exposure normalization

Exit criteria:
- graders packaged independently and reusable across skills/repos.

---

## Milestone 9 — CI/CD

Status: `NOT STARTED`

Tasks:
- [ ] Tier 1 required PR gate.
- [ ] Schema required PR gate.
- [ ] Unit-test required gate.
- [ ] Tier 2 candidate-vs-catalog gate.
- [ ] Fast Tier 3 PR evaluation.
- [ ] Domain grader PR results.
- [ ] Full release certification workflow.
- [ ] Nightly full-catalog workflow.
- [ ] GitHub artifact upload.
- [ ] PR comment summary.
- [ ] Benchmark freshness check.

Exit criteria:
- invalid or materially regressed skills cannot merge under defined policy.

---

## Milestone 10 — Remediation Engine

Status: `NOT STARTED`

Tasks:
- [ ] Normalize individual failures.
- [ ] Cluster repeated failures.
- [ ] Generate root-cause hypotheses.
- [ ] Identify affected SKILL.md sections.
- [ ] Recommend new regression tests.
- [ ] Recommend relevant graders.
- [ ] Generate human-readable improvement report.

Exit criteria:
- failed evaluations generate actionable guidance rather than a score alone.

---

## Milestone 11 — Cross-Repository Portability

Status: `NOT STARTED`

Create second repo:
`fixed-income-research-skills`

Tasks:
- [ ] Consume central framework package.
- [ ] Add one `pmai-skills.yaml`.
- [ ] Use reusable CI workflow.
- [ ] Add 2–3 local skills.
- [ ] Add local eval cases.
- [ ] Run central similarity catalog.
- [ ] Run certification.
- [ ] Generate same normalized reports.

Exit criteria:
- second repo does not copy/fork framework implementation;
- adoption requires configuration plus skill/eval content only.

---

## Milestone 12 — Registry & Production Model

Status: `NOT STARTED`

Tasks:
- [ ] Define registry API.
- [ ] Store certified version/digest.
- [ ] Store owner/dependencies.
- [ ] Store benchmark location.
- [ ] Define stale-certification rules.
- [ ] Add signed artifact design.
- [ ] Define runtime resolver.
- [ ] Add production telemetry contract.

Exit criteria:
- certified skills can be discovered and resolved by agent runtimes.

---

# Current project status

```text
Blueprint / Design                DONE
NVIDIA live integration           DONE (Tier 1 and controlled Tier 3 complete)
Normalized adapter                DONE (Milestone 2)
Synthetic data pipeline           DONE (Milestone 3)
12 skill definitions              SCAFFOLDED
120 starter eval cases            DONE / STARTER QUALITY
Finance graders                   SCAFFOLDED
CI workflow                       SCAFFOLDED
Real Tier 1 benchmark             DONE (portfolio-overview; 11/11 checks)
Real Tier 2 catalog               NOT STARTED
Real Tier 3 Skill Lift            IN PROGRESS (execution-heuristic blocker resolved via claude-code agent; full 3-attempt certification matrix running)
Cross-repo demonstration          NOT STARTED
```

---

# Progress update convention

Every PR should update:

1. milestone status;
2. tasks completed;
3. new blockers;
4. benchmark/eval evidence;
5. next three implementation tasks.

Recommended commit/PR labels:
- `framework`
- `skill`
- `eval`
- `grader`
- `ci`
- `docs`
- `benchmark`
- `bug/regression`
- `adoption`

---

# Suggested next three PRs

Reprioritized per the governance-first scope decision above. These are
deliberately cheaper and less dependent on the open Milestone 4 Tier 3
blocker than continuing to chase certification on Performance Attribution
alone — they deliver real duplication/ownership control immediately, and
don't require the NVIDIA execution-heuristic gap to be resolved first.

## PR 1 — Central catalog and blocking Tier 2 gate
- create one org-wide `catalogs/skill-catalog.json` (the current
  `catalogs/performance-attribution-catalog.json` is skill-scoped, not
  central);
- wire the `similarity` job in `.github/workflows/skills-quality.yml` to run
  for real instead of the current `echo` placeholder;
- make `EXACT_DUPLICATE` and `HIGH_SIMILARITY` (`policies/similarity.yaml`)
  actually block merge;
- assign an owner and SLA for the `architecture_review` action on
  `HIGH_SIMILARITY` findings.

## PR 2 — Ownership gate and risk-tiered certification profiles
- add a Tier 1 / schema check that fails CI on the literal placeholder
  `domain_reviewer: domain-owner-required` (present today in all 12
  reference `skill.yaml` files — this rule is already documented in
  `docs/03_SKILL_STANDARD.md` §3.8 but not enforced);
- add certification profiles for each `risk_level` per
  `docs/04_EVALUATION_AND_CERTIFICATION.md` §4.2a, instead of the single flat
  `analytical-standard` profile every skill currently points at.

## PR 3 — Performance Attribution vertical slice (unblocked)
- file the Codex `exec` execution-heuristic gap upstream with NVIDIA
  (`docs/13_NVIDIA_EVALUATOR_UPGRADE_POLICY.md` §13.6);
- keep Tier 3 advisory-only in CI until resolved;
- once resolved (or upstream-acknowledged with a workaround), rerun the full
  25-case matrix, measure Skill Lift, generate `BENCHMARK.md`, and apply the
  new risk-tiered certification profile from PR 2.

## Following PR — Lightweight registry
- generate a simple index (skill id, owner, risk_level, certification state,
  last benchmark date) from `catalogs/skill-catalog.json` and certification
  results, regenerated on every merge — pulled forward from Milestone 12
  because it is the artifact that actually prevents duplicate skill-building,
  not just detects it after the fact.
