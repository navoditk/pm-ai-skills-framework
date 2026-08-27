# PM AI Skills Quality & Certification Framework

Reference blueprint for building, testing, evaluating, certifying, and governing an enterprise AI skills library for portfolio management and broader asset-management use cases.

The design uses **NVIDIA SkillEvaluator as a pluggable generic evaluation engine** and layers asset-management-specific contracts, deterministic finance graders, certification rules, reporting, CI/CD, and portability on top.

## Why this repository exists

A large asset-management organization can quickly accumulate hundreds of agent skills. Without a common engineering framework, those skills tend to become:

- duplicated;
- inconsistently structured;
- difficult to discover;
- weakly tested;
- dependent on particular agents or models;
- hard to compare;
- difficult to certify for production;
- hard to improve after failures.

This repository defines a repeatable answer:

**Skill specification -> validation -> deduplication -> live evaluation -> domain grading -> certification -> benchmark evidence -> registry -> production feedback -> regression tests.**


## The purpose in one sentence

**Make every enterprise agent skill measurable, comparable, testable, governable, and portable before it is allowed into a production skills library.**

## How another team uses this

A consuming asset-management repository should not fork this project. The target operating model is:

```text
Your Repository
  ├── skills/
  ├── pmai-skills.yaml
  └── reusable GitHub workflow
          |
          v
Central PM AI Skills Framework
          |
          +--> NVIDIA SkillEvaluator
          +--> organization graders
          +--> certification policy
          +--> central similarity catalog
```

See `docs/11_QUICKSTART_FOR_CONSUMERS.md`.

## Project tracking

The authoritative staged implementation plan and current status live in:

`docs/10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md`

Update that file in every material implementation PR.

## External references

The curated source list for NVIDIA, Anthropic/Agent Skills, OpenAI, Microsoft, OpenTelemetry, AWS, LangSmith and Google lives in:

`docs/09_REFERENCES_AND_RESOURCES.md`


## Core architectural terms

- **Agentic Data Pipeline** — governed logical access layer exposing portfolio, risk, benchmark, market, research, and analytical capabilities to agents through stable tool contracts.
- **Skill** — reusable agent instructions plus optional scripts and reference materials.
- **SkillEvaluator Adapter** — wrapper around NVIDIA SkillEvaluator. NVIDIA is an engine, not the organization-level API contract.
- **Domain Grader** — deterministic or rubric-based evaluator validating asset-management correctness.
- **Certification Policy** — threshold and hard-gate rules determining whether a particular skill version may be published.
- **Skill Registry** — catalog of approved skills, versions, owners, dependencies, quality results, and certification state.
- **Benchmark Evidence** — immutable evaluation evidence associated with a specific skill/model/agent/eval/grader/environment combination.

## Reference use cases

The blueprint defines 12 representative skills:

1. Portfolio Overview
2. Performance Attribution
3. Risk Explanation
4. Exposure Analysis
5. Benchmark Comparison
6. Position Investigation
7. Scenario Analysis
8. Market Move Explanation
9. Liquidity Analysis
10. Portfolio Change Analysis
11. Concentration Analysis
12. PM Commentary Generation

Each skill contains a standard package and 10 starter evaluation cases.

## Start here

Read these documents in order:

1. `docs/01_PROPOSAL.md`
2. `docs/02_TARGET_ARCHITECTURE.md`
3. `docs/03_SKILL_STANDARD.md`
4. `docs/04_EVALUATION_AND_CERTIFICATION.md`
5. `docs/05_IMPLEMENTATION_PLAN.md`
6. `docs/06_ADOPTION_GUIDE.md`
7. `docs/07_GITHUB_PUBLISHING.md`
8. `docs/08_DEMO_AND_ACCEPTANCE_PLAN.md`
9. `docs/09_REFERENCES_AND_RESOURCES.md`
10. `docs/10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md`
11. `docs/11_QUICKSTART_FOR_CONSUMERS.md`

## Repository layout

```text
pm-ai-skills-framework/
├── docs/
├── framework/
│   ├── adapters/
│   ├── certification/
│   ├── cli/
│   ├── reporting/
│   └── schemas/
├── graders/
│   ├── common/
│   └── finance/
├── policies/
├── synthetic_data_pipeline/
├── skills/
├── catalogs/
├── tests/
├── examples/
└── .github/workflows/
```

## Important implementation principle

Application repositories should depend on **PM AI contracts**, not directly on NVIDIA result formats.

```text
Consuming Repository
        |
        v
PM AI Skills Framework API
        |
        +--> NVIDIA SkillEvaluator
        +--> PM deterministic graders
        +--> future evaluator providers
```

This protects the organization from vendor lock-in while still leveraging NVIDIA's validation, semantic deduplication, live-agent evaluation, Skill Lift, pass@k, sandboxes, and reporting.

## Blueprint status

This package is an implementation blueprint and scaffold. It intentionally contains runnable-looking interfaces, schemas, test cases, policies, and CI examples, but production integration will require:

- approved internal tool/data connectors;
- chosen model/agent credentials;
- environment-specific security controls;
- organization-specific ownership metadata;
- CI secret configuration;
- registry implementation or artifact repository integration.
