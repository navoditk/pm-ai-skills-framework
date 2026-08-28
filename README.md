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

## Purpose and usage at a glance

This repository is the central framework for governing an enterprise library of
AI skills. It provides the shared standards, evaluation machinery, reports, and
certification controls that a team needs before publishing a skill for
production use.

It is designed to be consumed by other skill repositories. A consuming team
keeps its own skills and domain content, then adds a small configuration file
and the reusable CI workflow:

```text
my-domain-skills/
├── skills/
│   ├── skill-a/
│   └── skill-b/
├── pmai-skills.yaml
└── .github/workflows/skills-quality.yml
```

The central framework provides:

- the common skill package and metadata standard;
- NVIDIA SkillEvaluator integration through a provider adapter;
- Tier 1 quality/security checks, Tier 2 similarity governance, and Tier 3
  live-agent evaluation;
- normalized reports, benchmark evidence, and certification policy;
- reusable finance graders and CI/CD workflows;
- a central approved-skill similarity catalog.

The consuming repository provides:

- its `SKILL.md` files and `skill.yaml` metadata;
- business owners, domain reviewers, and risk classification;
- positive, negative, adversarial, and regression evaluation cases;
- local fixtures and logical-tool dependencies;
- optional specialist graders for its domain.

Typical usage is:

```bash
pmai-skills validate ./skills
pmai-skills similarity ./skills/my-new-skill
pmai-skills evaluate ./skills/my-new-skill --profile pr
pmai-skills certify ./skills/my-new-skill --profile release
```

The consuming repository should depend on a pinned framework version. It should
not copy the framework implementation, duplicate certification logic, or parse
raw NVIDIA reports. Provider-specific behavior remains behind the framework
adapter, while skills depend on stable logical tool contracts.

Live evaluations still require the consuming environment to provide the
appropriate agent credentials, sandbox, logical tools, and test fixtures. The
framework governs and measures those evaluations; it does not replace the
agent runtime, authorization layer, or enterprise data pipeline.

The repository's local, reproducible example of those logical tools is documented in
[`docs/MILESTONE_3_SYNTHETIC_DATA_PIPELINE.md`](docs/MILESTONE_3_SYNTHETIC_DATA_PIPELINE.md).

The Performance Attribution vertical-slice evidence is documented in
[`docs/MILESTONE_4_PERFORMANCE_ATTRIBUTION.md`](docs/MILESTONE_4_PERFORMANCE_ATTRIBUTION.md).

For the detailed adoption path, see
[`docs/06_ADOPTION_GUIDE.md`](docs/06_ADOPTION_GUIDE.md) and
[`docs/11_QUICKSTART_FOR_CONSUMERS.md`](docs/11_QUICKSTART_FOR_CONSUMERS.md).

For the complete workflow from a new skill to certification, see
[`docs/12_END_TO_END_SKILL_WORKFLOW.md`](docs/12_END_TO_END_SKILL_WORKFLOW.md).


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
12. `docs/12_END_TO_END_SKILL_WORKFLOW.md`
13. `docs/MILESTONE_4_PERFORMANCE_ATTRIBUTION.md`

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
