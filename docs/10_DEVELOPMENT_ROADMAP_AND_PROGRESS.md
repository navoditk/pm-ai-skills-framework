# 10. Development Roadmap & Progress Tracker

This document is the working execution plan for building the reference implementation.

Update this file in every material pull request.

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

Status: `NOT STARTED`

Tasks:
- [ ] Pin an NVIDIA SkillEvaluator version.
- [ ] Document supported Python version.
- [ ] Install SkillEvaluator locally.
- [ ] Install required Tier 1 scanners.
- [ ] Validate Docker availability.
- [ ] Validate Harbor setup.
- [ ] Configure one supported Tier 3 agent.
- [ ] Run Tier 1 against one reference skill.
- [ ] Run Tier 3 smoke test.
- [ ] Capture actual raw NVIDIA report structure.
- [ ] Update `framework/adapters/nvidia_skillevaluator.py` to match pinned CLI exactly.

Exit criteria:
- one skill passes an actual NVIDIA Tier 1 run;
- one controlled Tier 3 evaluation completes in sandbox.

Evidence:
- `reports/m1/`
- issue/PR link
- exact evaluator version.

---

## Milestone 2 — Normalized Framework Contracts

Status: `NOT STARTED`

Tasks:
- [ ] Finalize `skill.schema.json`.
- [ ] Validate all 12 `skill.yaml` files.
- [ ] Finalize normalized evaluation-result schema.
- [ ] Implement NVIDIA output parser.
- [ ] Implement benchmark identity/fingerprint.
- [ ] Implement provider abstraction tests.
- [ ] Add framework version field to output.

Exit criteria:
- downstream certification code consumes normalized PM AI results only;
- no downstream code parses NVIDIA raw schema directly.

---

## Milestone 3 — Synthetic Agentic Data Pipeline

Status: `NOT STARTED`

Tasks:
- [ ] Define logical tool interfaces.
- [ ] Add deterministic portfolio fixtures.
- [ ] Add benchmark fixture.
- [ ] Add attribution fixture.
- [ ] Add factor-risk fixture.
- [ ] Add scenario fixture.
- [ ] Add market-data fixture.
- [ ] Add controlled failure modes.
- [ ] Add stale/mismatched-date fixtures.
- [ ] Add derivative position fixture.

Exit criteria:
- all reference skill evaluations can run without production systems.

---

## Milestone 4 — First Vertical Slice: Performance Attribution

Status: `NOT STARTED`

Tasks:
- [ ] Refine SKILL.md.
- [ ] Validate with NVIDIA Tier 1.
- [ ] Create/update Tier 2 catalog.
- [ ] Run candidate similarity.
- [ ] Complete 10 initial eval cases.
- [ ] Expand to >=25 cases.
- [ ] Implement attribution reconciliation grader.
- [ ] Implement benchmark consistency grader.
- [ ] Implement temporal consistency grader.
- [ ] Run with-skill baseline.
- [ ] Run without-skill baseline.
- [ ] Measure Skill Lift.
- [ ] Run repeated attempts.
- [ ] Generate normalized report.
- [ ] Generate BENCHMARK.md.
- [ ] Apply certification policy.

Exit criteria:
- one complete skill flows from source -> eval -> certification -> benchmark report.

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
NVIDIA live integration           NOT STARTED
Normalized adapter                SCAFFOLDED
Synthetic data pipeline           SCAFFOLDED
12 skill definitions              SCAFFOLDED
120 starter eval cases            DONE / STARTER QUALITY
Finance graders                   SCAFFOLDED
CI workflow                       SCAFFOLDED
Real Tier 1 benchmark             NOT STARTED
Real Tier 2 catalog               NOT STARTED
Real Tier 3 Skill Lift            NOT STARTED
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

## PR 1 — Pin and integrate real SkillEvaluator
- pin version;
- run Tier 1;
- capture raw reports;
- make adapter real.

## PR 2 — Performance Attribution vertical slice
- synthetic data;
- graders;
- Tier 3;
- Skill Lift;
- BENCHMARK.

## PR 3 — Risk + Portfolio Overview
- prove reuse;
- introduce deliberate defects;
- demonstrate remediation.
