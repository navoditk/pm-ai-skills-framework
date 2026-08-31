# PM AI Skills Quality & Certification Framework

A hands-on reference project for building **familiarity with the NVIDIA SkillEvaluator framework** — how it works, how it is used, and how an AI skill's performance is actually measured — using a realistic portfolio-management skill library as the vehicle rather than a toy example.

The design uses **NVIDIA SkillEvaluator as the evaluation engine** and layers a thin, PM-specific governance model on top: ownership enforcement, catalog-based duplicate detection, deterministic finance grading, risk-tiered certification rigor, and benchmark evidence. This is deliberately **not** a generic, domain-agnostic agent framework — see [Scope](#scope) below.

## Goals, upfront

**The primary goal, reaffirmed 2026-08-30, is learning-focused:** build real, hands-on familiarity with the NVIDIA SkillEvaluator framework — how its four evaluation tiers work, how to wire it into a real skill's development loop, and how to read and trust (or distrust) the numbers it produces. Everything below is in service of that goal, using a PM/asset-management skill library as a realistic, non-trivial domain to exercise it against — not because shipping that library into production is the point.

Within that frame, the concrete engineering goals, in priority order:

1. **Stop duplicate/near-duplicate skills from entering the library.** Every new skill is checked against a central catalog before merge (Tier 2 semantic similarity), so two teams don't independently build "explain portfolio performance" under different names.
2. **Make skill quality measurable and comparable**, using NVIDIA SkillEvaluator's Tier 1 (construction/security) and Tier 3 (live-agent, with-skill vs. without-skill) evaluation, rather than relying on demos or subjective review.
3. **Catch financially wrong answers that generic evaluation can't see** — reconciliation errors, stale/mismatched dates, missing derivatives coverage — via deterministic PM domain graders (Tier 4).
4. **Scale certification rigor to actual risk**, so an informational skill and a decision-support skill aren't held to the same (or held to an insufficiently strict) bar.
5. **Enforce ownership before evaluation**, so every skill has a named business owner and domain reviewer prior to certification — no owner, no certification.
6. **Insulate PM certification logic from NVIDIA's release cadence**, so upgrading the underlying evaluator doesn't silently change what "certified" means (see [NVIDIA upgrade policy](#nvidia-skillevaluator-upgrade-policy)).
7. **Produce auditable benchmark evidence** — a `BENCHMARK.md` and normalized JSON record tied to an exact skill version, dataset, agent, model, and evaluator version — before a skill is trusted in production.

**What this means in practice:** the project deliberately stops short of production-scale work that wouldn't teach anything new about the framework itself — see [Key findings and takeaways](#key-findings-and-takeaways) below and [`docs/10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md`](docs/10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md)'s "Scope decision (2026-08-30)" for exactly what was descoped and why.

## Scope

This framework governs **PM/asset-management skills specifically**, used as the domain for the learning goal above. It is not intended to become a catch-all, multi-domain skills platform, and — per the 2026-08-30 decision — it is not being pushed to full production scale (a complete 12-skill certified catalog, a production CI pipeline, a remediation engine, a live skill registry) purely for its own sake. The value it demonstrates — a central duplicate-detection catalog, a shared certification vocabulary, reusable finance graders, and a real evaluation-to-certification pipeline — depends on going deep on a few real skills rather than wide across many. See [`docs/01_PROPOSAL.md`](docs/01_PROPOSAL.md) §1.5 for explicit non-goals and [`docs/10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md`](docs/10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md) for the full re-scope reasoning.

## Key findings and takeaways

For anyone new to this repo, this is the headline: two real skills have been taken end-to-end through the full pipeline (live agent, live judge, real Docker sandbox, real certification policy) — not demoed, not simulated. Both came back an honest **FAIL**, for precisely diagnosed reasons, which is itself the point: a governance layer that always says "pass" isn't doing anything.

- **Performance Attribution** (Milestone 4): a complete 150-trial matrix scored **Skill Lift +0.1253**, real. Getting there surfaced **four distinct real bugs** — an agent-compatibility gap in the evaluator's execution-heuristic, a judge token-truncation bug found by reading the evaluator's own source, a missing CLI flag (this project's own operator error), and API credit exhaustion mid-run, twice. Final certification: **FAIL for exactly one well-evidenced reason** — discoverability narrowly missing its 0.90 floor, diagnosed as a metric-scoping artifact (two "ambiguous input" cases are structurally unable to score high on a tool-use metric because *not* using a tool is their correct behavior), not an actual skill defect. Full trail: [`docs/MILESTONE_4_PERFORMANCE_ATTRIBUTION.md`](docs/MILESTONE_4_PERFORMANCE_ATTRIBUTION.md).
- **Portfolio Overview** (Milestone 5): a second complete 150-trial matrix scored **Skill Lift +0.1316**, real. Certification: **FAIL for two reasons** — the *same* discoverability shortfall (0.8942 this time), independently corroborated by NVIDIA's own report recommending the same fix Milestone 4 had already diagnosed — plus a **newly discovered certification policy-profile gap**: one minimum metric (`reconciliation`) is specific to Performance Attribution's own grader and silently fails every other skill in the catalog regardless of quality. Found by actually running the real pipeline twice, not by auditing the policy file in the abstract. Evidence: [`skills/portfolio-overview/BENCHMARK.md`](skills/portfolio-overview/BENCHMARK.md).
- **Milestone 6** (deliberate defects, `DONE`): 5 of 6 intentionally-introduced defects (vague description, duplicate skill, missing derivatives, mismatched dates, unauthorized data source) are caught and confirmed with real evidence — Tier 1 quality scoring, Tier 2 embedding similarity, and grader regression tests. The sixth (a weak/no-value skill's Skill Lift) was accepted on a Tier 1 proxy rather than a live measurement, a deliberate human-reviewer call, not a silently dropped gap. Full trail: [`docs/MILESTONE_6_DELIBERATE_DEFECTS.md`](docs/MILESTONE_6_DELIBERATE_DEFECTS.md).
- **Milestone 9** (CI/CD, `DONE`): one real GitHub Actions job now blocks a PR when a changed skill fails Tier 1 validation — a working demonstration of "invalid skills can't merge," not a full production pipeline.
- **Two findings remain deliberately open for human review, not silently resolved** — the reconciliation policy gap and the recurring discoverability metric-scoping issue. See [`docs/10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md`](docs/10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md)'s "Open policy decisions pending human review."
- **No skill in this catalog has cleared certification outright yet.** That is reported plainly rather than smoothed over — see [`docs/14_EXECUTIVE_SUMMARY_AND_WALKTHROUGH.md`](docs/14_EXECUTIVE_SUMMARY_AND_WALKTHROUGH.md) for the complete, cold-readable walkthrough with an honest pros/cons assessment.
- **New to agent skills or SkillEvaluator itself?** Start with [`docs/15_SKILLS_AND_SKILLEVALUATOR_REFERENCE.md`](docs/15_SKILLS_AND_SKILLEVALUATOR_REFERENCE.md) — a one-stop guide covering what they are, whether they're worth adopting, exact install/run steps, repo layout requirements, CI/CD integration, and curated external resources.

## What was attempted — milestones at a glance

Full detail and evidence for every row lives in
[`docs/10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md`](docs/10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md).

| # | Milestone | Status | Note |
|---|---|---|---|
| 0 | Blueprint | `DONE` | Design docs, 12 skill scaffolds, starter graders |
| 1 | Dev environment & NVIDIA smoke test | `DONE` | Pinned version, real Tier 1 + one controlled Tier 3 run |
| 2 | Normalized framework contracts | `DONE` | Vendor-adapter boundary, test-covered |
| 3 | Synthetic Agentic Data Pipeline | `DONE` | Deterministic local fixtures, no production systems touched |
| 4 | Performance Attribution vertical slice | `IN PROGRESS` | Engineering complete; real certification `FAIL` for one diagnosed reason, left open for review |
| 5 | Three-skill vertical slice | `IN PROGRESS` | 2 of 3 skills fully certified (both real `FAIL`); Risk Explanation refined but not yet run through full Tier 3 |
| 6 | Deliberate defect demonstration | `DONE` | 5 of 6 defects caught directly; 1 accepted on proxy evidence |
| 7 | Complete 12-skill library | `IN PROGRESS` | Right-sized to structural completion for 9 skills; blocked from fully closing only by Milestone 5 |
| 8 | Finance grader library | `DONE` | Required graders built, reused across all 12 skills |
| 9 | CI/CD | `DONE` | Real Tier 1 PR gate, right-sized from an 11-task pipeline |
| 10 | Remediation engine | `DESCOPED` | Beyond the learning-focused goal; documented as a future extension |
| 11 | Cross-repository portability | `DESCOPED` | Same reasoning as Milestone 10 |
| 12 | Registry & production model | `DESCOPED` | Same reasoning as Milestone 10 |

## Next steps

- **Run Risk Explanation's full live Tier 3 certification matrix** — refined to standard and quick-pass validated already; the full run is the only thing blocking Milestones 5 and 7 from closing. Deferred pending budget, same cost profile as the two completed runs (~$15-45, ~30-55 minutes).
- **Resolve the two open policy decisions**, tracked in [`docs/10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md`](docs/10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md)'s "Open policy decisions pending human review": whether `analytical-standard`'s `reconciliation` minimum metric should be dropped or scoped to a narrower profile, and whether the recurring discoverability metric-scoping shortfall should be accepted as a documented limitation or fixed at the eval-case level.
- **Optional, lower priority:** decide whether any of the 9 structurally-complete skills warrant full live Tier 3 certification depth later, and whether Milestone 9's CI gate should ever be extended toward the Tier 2/Tier 3 jobs it currently leaves as documented placeholders — both are deliberately not being pursued now per the 2026-08-30 scope decision, not accidentally incomplete.

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

Target usage — the intended day-to-day interface once `framework/cli/` is
implemented as a thin wrapper around the pinned `skillevaluator` CLI — is:

```bash
pmai-skills validate ./skills
pmai-skills similarity ./skills/my-new-skill
pmai-skills evaluate ./skills/my-new-skill --profile pr
pmai-skills certify ./skills/my-new-skill --profile release
```

**Current status:** this CLI does not exist yet. All Milestone 1 and Milestone 4
work was run directly against the pinned `skillevaluator` binary
(`.venv/bin/skillevaluator ...`); see [`docs/10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md`](docs/10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md)
for exactly what is implemented versus planned. `pmai-skills` is intentionally
scoped to stay a thin pass-through — it should add PM manifest/ownership
checks, normalize output, and apply certification policy, and nothing more.
It should not reimplement flags or behavior NVIDIA already provides.

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

See [`docs/11_QUICKSTART_FOR_CONSUMERS.md`](docs/11_QUICKSTART_FOR_CONSUMERS.md).

## Project tracking

The authoritative staged implementation plan and current status live in:

[`docs/10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md`](docs/10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md)

Update that file in every material implementation PR.

## External references

The curated source list for NVIDIA, Anthropic/Agent Skills, OpenAI, Microsoft, OpenTelemetry, AWS, LangSmith and Google lives in:

[`docs/09_REFERENCES_AND_RESOURCES.md`](docs/09_REFERENCES_AND_RESOURCES.md)


## Architecture at a glance

```text
PM / Research experience  ->  Agent / Orchestrator  ->  Skill Runtime + Policy Layer
                                                              |
                                                              v
                                            Agentic Data Pipeline (logical tool contracts)
                                                              |
====================  skills engineering plane runs alongside, not inline  ====================
                                                              |
                                                              v
        Skill source  ->  NVIDIA SkillEvaluator (Tier 1/2/3)  ->  PM domain graders (Tier 4)
                                     |                                     |
                                     v                                     v
                          normalized adapter output  ---->  certification engine  ->  registry
```

Two boundaries matter most:

- **The Agentic Data Pipeline boundary** — skills call stable logical capabilities
  (`portfolio.positions`, `performance.attribution`), never a physical database or
  vendor API directly. This is what lets a skill's certification evidence stay
  valid across infrastructure changes.
- **The NVIDIA adapter boundary** — nothing outside `framework/adapters/`
  parses NVIDIA's raw report format. Everything downstream (certification,
  reporting, registry) consumes a normalized PM AI result schema instead. This
  is what makes NVIDIA version upgrades a contained, testable event instead of
  a library-wide breaking change — see
  [NVIDIA SkillEvaluator upgrade policy](#nvidia-skillevaluator-upgrade-policy).

For the full architecture — every layer's responsibility, the evaluation
provider abstraction, and benchmark identity rules — see
[`docs/02_TARGET_ARCHITECTURE.md`](docs/02_TARGET_ARCHITECTURE.md).

## NVIDIA SkillEvaluator upgrade policy

The framework depends on one external evaluation engine, pinned to an exact
version and commit (currently `0.2.1` /
`009aa300be7925c7ba75760592baeb941cc29ba8` — see
[`docs/MILESTONE_1_SETUP.md`](docs/MILESTONE_1_SETUP.md)). Upgrading that dependency is a governed event,
not a routine `pip install --upgrade`:

- version bumps run through a staged compatibility test (adapter tests, a
  Tier 1 reference run, and a full Tier 3 matrix compared against the last
  certified benchmark) before becoming the new pin;
- the normalized result schema is expected to stay stable across evaluator
  versions; only `framework/adapters/nvidia_skillevaluator.py` should need to
  change;
- known evaluator-compatibility gaps (for example, the Tier 3 execution
  heuristic not recognizing Codex's `exec` action — see
  [`docs/MILESTONE_4_PERFORMANCE_ATTRIBUTION.md`](docs/MILESTONE_4_PERFORMANCE_ATTRIBUTION.md)) are logged and tracked
  upstream rather than patched around locally.

Full process, triggers, rollback plan, and the compatibility-issue log live in
[`docs/13_NVIDIA_EVALUATOR_UPGRADE_POLICY.md`](docs/13_NVIDIA_EVALUATOR_UPGRADE_POLICY.md).

## Core architectural terms

- **Agentic Data Pipeline** — governed logical access layer exposing portfolio, risk, benchmark, market, research, and analytical capabilities to agents through stable tool contracts.
- **Skill** — reusable agent instructions plus optional scripts and reference materials.
- **SkillEvaluator Adapter** — wrapper around NVIDIA SkillEvaluator. NVIDIA is an engine, not the organization-level API contract.
- **Domain Grader** — deterministic or rubric-based evaluator validating asset-management correctness.
- **Certification Policy** — threshold and hard-gate rules determining whether a particular skill version may be published.
- **Skill Registry** — catalog of approved skills, versions, owners, dependencies, quality results, and certification state.
- **Benchmark Evidence** — immutable evaluation evidence associated with a specific skill/model/agent/eval/grader/environment combination.

## Reference use cases

The blueprint defines 12 representative skills, at two different depths per
the 2026-08-30 right-sizing decision — see
[Key findings and takeaways](#key-findings-and-takeaways) above:

**Full certification depth** (25 real eval cases each, live Sonnet Tier 3
matrix run, real `BENCHMARK.md`):

1. Portfolio Overview — certified run complete, real FAIL (two diagnosed reasons)
2. Performance Attribution — certified run complete, real FAIL (one diagnosed reason)
3. Risk Explanation — refined to standard, quick-pass validated, full certification deferred

**Structurally complete** (real composite grader, correct tool declarations,
Tier 1 passing 11/11, 10 starter eval cases each — not yet run through a
live Tier 3 matrix):

4. Exposure Analysis
5. Benchmark Comparison
6. Position Investigation
7. Scenario Analysis
8. Market Move Explanation
9. Liquidity Analysis
10. Portfolio Change Analysis
11. Concentration Analysis
12. PM Commentary Generation

## Start here

Read these documents in order:

1. [`docs/01_PROPOSAL.md`](docs/01_PROPOSAL.md)
2. [`docs/02_TARGET_ARCHITECTURE.md`](docs/02_TARGET_ARCHITECTURE.md)
3. [`docs/03_SKILL_STANDARD.md`](docs/03_SKILL_STANDARD.md)
4. [`docs/04_EVALUATION_AND_CERTIFICATION.md`](docs/04_EVALUATION_AND_CERTIFICATION.md)
5. [`docs/05_IMPLEMENTATION_PLAN.md`](docs/05_IMPLEMENTATION_PLAN.md)
6. [`docs/06_ADOPTION_GUIDE.md`](docs/06_ADOPTION_GUIDE.md)
7. [`docs/07_GITHUB_PUBLISHING.md`](docs/07_GITHUB_PUBLISHING.md)
8. [`docs/08_DEMO_AND_ACCEPTANCE_PLAN.md`](docs/08_DEMO_AND_ACCEPTANCE_PLAN.md)
9. [`docs/09_REFERENCES_AND_RESOURCES.md`](docs/09_REFERENCES_AND_RESOURCES.md)
10. [`docs/10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md`](docs/10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md)
11. [`docs/11_QUICKSTART_FOR_CONSUMERS.md`](docs/11_QUICKSTART_FOR_CONSUMERS.md)
12. [`docs/12_END_TO_END_SKILL_WORKFLOW.md`](docs/12_END_TO_END_SKILL_WORKFLOW.md)
13. [`docs/13_NVIDIA_EVALUATOR_UPGRADE_POLICY.md`](docs/13_NVIDIA_EVALUATOR_UPGRADE_POLICY.md)
14. [`docs/14_EXECUTIVE_SUMMARY_AND_WALKTHROUGH.md`](docs/14_EXECUTIVE_SUMMARY_AND_WALKTHROUGH.md) — a standalone, cold-read
    summary covering goals, architecture, milestone status, and an honest
    pros/cons assessment
15. [`docs/15_SKILLS_AND_SKILLEVALUATOR_REFERENCE.md`](docs/15_SKILLS_AND_SKILLEVALUATOR_REFERENCE.md) — one-stop reference:
    what agent skills and SkillEvaluator are, feasibility, install/run
    steps, layout requirements, CI/CD integration, and curated external
    resources (standards, other vendors' approaches, tutorials, a podcast)
16. [`docs/MILESTONE_4_PERFORMANCE_ATTRIBUTION.md`](docs/MILESTONE_4_PERFORMANCE_ATTRIBUTION.md)
17. [`docs/MILESTONE_6_DELIBERATE_DEFECTS.md`](docs/MILESTONE_6_DELIBERATE_DEFECTS.md) — six synthetic broken-skill
    variants and how the framework catches each one

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

This package started as an implementation blueprint and scaffold, but two
skills (Performance Attribution, Portfolio Overview) have since been taken
all the way through the real pipeline — live agent, live judge, real Docker
sandbox, real certification policy — with genuine evidence on disk (`docs/
MILESTONE_4_PERFORMANCE_ATTRIBUTION.md`, `skills/portfolio-overview/
BENCHMARK.md`). The remaining nine reference skills are structurally
complete but have not been run through a live Tier 3 matrix, and several
production-scale pieces remain intentionally unbuilt per the 2026-08-30
scope decision (a remediation engine, cross-repo portability, a production
skill registry — see [`docs/10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md`](docs/10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md)).
Actually adopting this in a production organization would still require:

- approved internal tool/data connectors (this repo uses a synthetic, local
  data pipeline instead — see [`docs/MILESTONE_3_SYNTHETIC_DATA_PIPELINE.md`](docs/MILESTONE_3_SYNTHETIC_DATA_PIPELINE.md));
- chosen model/agent credentials;
- environment-specific security controls;
- organization-specific ownership metadata;
- CI secret configuration;
- registry implementation or artifact repository integration (deliberately
  descoped here — see Milestone 12).
