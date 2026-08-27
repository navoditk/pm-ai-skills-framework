# 5. Detailed Implementation Plan

## Phase 0 — Repository bootstrap

1. Create the repository from this blueprint.
2. Add Python packaging and lint/test tooling.
3. Install NVIDIA SkillEvaluator in a developer environment.
4. Configure a supported Tier 3 agent.
5. Verify Docker/Harbor readiness.
6. Add CI secrets only in the CI environment.

Output:
- repository builds;
- Tier 1 runs locally;
- Tier 3 smoke test succeeds.

## Phase 1 — Contracts

Implement:
- `skill.schema.json`;
- normalized `evaluation-result.schema.json`;
- `pmai-skills.yaml`;
- certification policy;
- similarity policy;
- provider adapter interface.

Output:
- one framework API independent of NVIDIA output.

## Phase 2 — Synthetic Agentic Data Pipeline

Create deterministic mock logical tools:
- portfolios;
- positions;
- benchmarks;
- performance attribution;
- factor exposure;
- scenarios;
- market history.

Use fixed fixtures so eval results are repeatable.

Output:
- reference tasks can run without production systems.

## Phase 3 — First three skills

Build:
1. Portfolio Overview
2. Performance Attribution
3. Risk Explanation

For each:
- write SKILL.md;
- write skill.yaml;
- add 10 evals;
- add deterministic tests;
- run Tier 1;
- run Tier 2;
- run Tier 3;
- add PM graders.

## Phase 4 — Complete 12-skill library

Implement the remaining nine skills and add the full similarity catalog.

Target:
- at least 120 starter evaluation cases.

## Phase 5 — Finance grader library

Implement and unit test:
1. AttributionReconciliationGrader
2. TemporalConsistencyGrader
3. BenchmarkConsistencyGrader
4. PortfolioCoverageGrader
5. DataProvenanceGrader
6. NumericClaimGroundingGrader

Then extend to:
- currency;
- duration;
- risk contribution;
- factor exposure;
- scenario consistency.

## Phase 6 — CI/CD

Create progressive workflows:

### On commit / lightweight PR
- schema;
- unit tests;
- NVIDIA Tier 1.

### PR
- Tier 1;
- candidate-vs-catalog Tier 2;
- fast Tier 3 subset;
- PM graders;
- normalized report artifact.

### Release
- full Tier 2;
- full Tier 3;
- baseline retained;
- multi-attempt;
- regression;
- adversarial;
- certification;
- BENCHMARK generation.

### Nightly
- full catalog;
- model qualification;
- similarity drift;
- large regression suites.

## Phase 7 — Improvement engine

Normalize failures into structured objects.

Cluster failures by:
- grader;
- trajectory;
- semantic failure description.

Generate:
- failure summary;
- likely root cause;
- proposed skill improvement;
- proposed new tests.

Human review remains required before automated suggestions change a certified skill.

## Phase 8 — Portability proof

Create a second sample repository such as:

```text
fixed-income-research-skills/
```

It should adopt the central framework through:
- package dependency;
- one config;
- reusable CI workflow;
- local skills/evals only.

Acceptance criterion:
No fork or copy of framework implementation.

## Phase 9 — Registry integration

Publish certified metadata:
- skill ID/version;
- owner;
- digest;
- dependency graph;
- benchmark URI;
- certification state;
- expiration/rebenchmark requirement.

## Phase 10 — Production feedback

Use trace/telemetry data to identify:
- routing misses;
- failures;
- tool errors;
- drift;
- cost;
- latency.

Convert reviewed production failures into regression cases.
