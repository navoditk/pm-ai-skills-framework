# PM AI Skills Quality & Certification Framework

A hands-on reference project for building **familiarity with the NVIDIA SkillEvaluator framework** — how it works, how it is used, and how an AI skill's performance is actually measured — using a realistic portfolio-management skill library as the vehicle rather than a toy example.

The design uses **NVIDIA SkillEvaluator as the evaluation engine** and layers a thin, PM-specific governance model on top: ownership enforcement, catalog-based duplicate detection, deterministic finance grading, risk-tiered certification rigor, and benchmark evidence. This is deliberately **not** a generic, domain-agnostic agent framework — see [Scope](#scope) below.

## New here? Start with the interactive SkillEvaluator trainer

Before reading any of the design docs below, get hands-on familiarity with
NVIDIA SkillEvaluator itself using this repository's own
[`skillevaluator-mastery`](skills/skillevaluator-mastery/) agent skill — an
interactive trainer with guided lessons, quizzes, scenario challenges, and a
final exam covering all four evaluation tiers.

**Ways to access the curriculum:**
- 🌐 **Public Web Curriculum (GitHub Pages)**: [https://navoditk.github.io/pm-ai-skills-framework/](https://navoditk.github.io/pm-ai-skills-framework/) — full interactive web version with dark mode, sidebar navigation, and module quizzes.
- 📄 **Standalone Single-File HTML Artifact**: [skillevaluator-mastery-standalone.html](https://navoditk.github.io/pm-ai-skills-framework/skillevaluator-mastery-standalone.html) — self-contained, offline-viewable HTML artifact containing the entire curriculum, re-compiled and published automatically on every push/merge to `main`.
- 🤖 **Interactive Copilot Agent Skill**: Auto-discovered inside a repository checkout via `.github/skills/skillevaluator-mastery/SKILL.md`. Just say **`skillevalexpert`** in your session to start. (To use globally or in another repo, copy `skills/skillevaluator-mastery/` to `.github/skills/`, `.claude/skills/`, `.agents/skills/`, or `~/.copilot/skills/`).
- 📖 **Self-Paced Markdown Walkthrough**: [`docs/16_SKILLEVALUATOR_MASTERY.md`](docs/16_SKILLEVALUATOR_MASTERY.md).

Once you're comfortable with what SkillEvaluator does and how its tiers
work, move on to this framework's own design and evidence below.

## Is this a good fit for your PM AI use case?

This is a governance layer on top of NVIDIA SkillEvaluator, not a
replacement for your agent runtime, data pipeline, or model choice
(see [Adopting this framework](#adopting-this-framework-for-another-team)). Quick self-check before you
invest time:

| Signal | Likely a fit | Likely not (yet) |
|---|---|---|
| Skill count & duplication risk | Multiple teams building similar PM/finance skills independently | A single small team, one skill, low duplication risk |
| Risk tolerance | You need graded rigor (informational vs. decision-support) before production | Everything ships from demo/manual review today, and that's acceptable |
| Domain-correctness needs | Generic LLM-judge scoring can't catch your failure modes (e.g. reconciliation errors, stale dates, missing derivatives coverage) — see [`graders/finance/`](graders/finance/) for real examples | Generic quality/security scoring (Tier 1) is already enough for your bar |
| Budget for live evaluation | You can afford Tier 3's real cost — **$15-45 and 30-55 minutes per skill** for a full certification-depth matrix (see [Module 4](docs/16_SKILLEVALUATOR_MASTERY.md)) | You need a free/instant signal only — use Tier 1 alone, it's free and offline |
| Tolerance for "Experimental" tooling | You can budget time to read vendor source and work around real bugs (four found and documented here — see [Key findings](#key-findings-and-takeaways)) | You need a fully supported, SLA-backed evaluation product |
| Production readiness today | You're prototyping governance and want a real, evidence-backed reference implementation | You need a turnkey, production-hardened registry/remediation pipeline today — several pieces here are deliberately descoped (see [Scope](#scope)) |

If most of the left column applies, read on. If not, the
[`skillevaluator-mastery`](skills/skillevaluator-mastery/) skill and
[`docs/15_SKILLS_AND_SKILLEVALUATOR_REFERENCE.md`](docs/15_SKILLS_AND_SKILLEVALUATOR_REFERENCE.md)
are still worth it purely to evaluate NVIDIA SkillEvaluator on its own
merits, independent of this repository's PM-specific layer.

## Start with your goal

The repository contains a detailed implementation history as well as the
current framework. Choose the shortest reading path for your purpose:

| If you want to... | Start here |
|---|---|
| Run the local, no-credential path | [First tutorial](docs/00_TUTORIAL.md) |
| Understand the framework's purpose and boundaries | [Executive summary](docs/14_EXECUTIVE_SUMMARY_AND_WALKTHROUGH.md) |
| Understand the design | [Proposal](docs/01_PROPOSAL.md) and [target architecture](docs/02_TARGET_ARCHITECTURE.md) |
| Author, evaluate, or certify a skill | [Skill standard](docs/03_SKILL_STANDARD.md), [evaluation model](docs/04_EVALUATION_AND_CERTIFICATION.md), and [end-to-end workflow](docs/12_END_TO_END_SKILL_WORKFLOW.md) |
| Adopt the framework in another repository | [Consumer quickstart](docs/11_QUICKSTART_FOR_CONSUMERS.md) and [adoption guide](docs/06_ADOPTION_GUIDE.md) |
| Review outcomes, evidence, and open work | [Roadmap and progress](docs/10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md) and [evidence index](docs/EVIDENCE_INDEX.md) |
| Learn NVIDIA SkillEvaluator itself | [Skills and SkillEvaluator reference](docs/15_SKILLS_AND_SKILLEVALUATOR_REFERENCE.md) and the [from-scratch mastery tutorial](docs/16_SKILLEVALUATOR_MASTERY.md) (paired with the interactive [`skillevaluator-mastery`](skills/skillevaluator-mastery/) agent skill) |

See the reader-oriented [documentation map](docs/README.md) for the complete
guide. The root README remains the project narrative; detailed milestone
records, benchmarks, and operating instructions remain in their existing
canonical documents.

## Goals, upfront

**The primary goal, reaffirmed 2026-08-30, is learning-focused:** build real, hands-on familiarity with the NVIDIA SkillEvaluator framework — how its four evaluation tiers work, how to wire it into a real skill's development loop, and how to read and trust (or distrust) the numbers it produces. Everything below is in service of that goal, using a PM/asset-management skill library as a realistic, non-trivial domain to exercise it against — not because shipping that library into production is the point.

Within that frame, the concrete engineering goals, in priority order:

1. **Stop duplicate/near-duplicate skills from entering the library.** Every new skill is checked against a central catalog before merge (Tier 2 semantic similarity), so two teams don't independently build "explain portfolio performance" under different names.
2. **Make skill quality measurable and comparable**, using NVIDIA SkillEvaluator's Tier 1 (construction/security) and Tier 3 (live-agent, with-skill vs. without-skill) evaluation, rather than relying on demos or subjective review.
3. **Catch financially wrong answers that generic evaluation can't see** — reconciliation errors, stale/mismatched dates, missing derivatives coverage — via deterministic PM domain graders (Tier 4).
4. **Scale certification rigor to actual risk**, so an informational skill and a decision-support skill aren't held to the same (or held to an insufficiently strict) bar.
5. **Enforce ownership before evaluation**, so every skill has a named business owner and domain reviewer prior to certification — no owner, no certification.
6. **Insulate PM certification logic from NVIDIA's release cadence**, so upgrading the underlying evaluator doesn't silently change what "certified" means (see [`docs/13_NVIDIA_EVALUATOR_UPGRADE_POLICY.md`](docs/13_NVIDIA_EVALUATOR_UPGRADE_POLICY.md)).
7. **Produce auditable benchmark evidence** — a `BENCHMARK.md` and normalized JSON record tied to an exact skill version, dataset, agent, model, and evaluator version — before a skill is trusted in production.

**What this means in practice:** the project deliberately stops short of production-scale work that wouldn't teach anything new about the framework itself — see [Key findings and takeaways](#key-findings-and-takeaways) below and [`docs/10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md`](docs/10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md)'s "Scope decision (2026-08-30)" for exactly what was descoped and why.

## Scope

This framework governs **PM/asset-management skills specifically**, used as the domain for the learning goal above. It is not intended to become a catch-all, multi-domain skills platform, and — per the 2026-08-30 decision — it is not being pushed to full production scale (a complete 12-skill certified catalog, a production CI pipeline, a remediation engine, a live skill registry) purely for its own sake. The value it demonstrates — a central duplicate-detection catalog, a shared certification vocabulary, reusable finance graders, and a real evaluation-to-certification pipeline — depends on going deep on a few real skills rather than wide across many. See [`docs/01_PROPOSAL.md`](docs/01_PROPOSAL.md) §1.5 for explicit non-goals and [`docs/10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md`](docs/10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md) for the full re-scope reasoning.

## Key findings and takeaways

For anyone new to this repo, this is the headline: two real skills have been taken end-to-end through the full pipeline (live agent, live judge, real Docker sandbox, real certification policy) — not demoed, not simulated. Both came back an honest **FAIL**, for precisely diagnosed reasons, which is itself the point: a governance layer that always says "pass" isn't doing anything.

- **Performance Attribution** (Milestone 4): a complete 150-trial matrix scored **Skill Lift +0.1253**, real. Getting there surfaced **four distinct real bugs** — an agent-compatibility gap in the evaluator's execution-heuristic, a judge token-truncation bug found by reading the evaluator's own source, a missing CLI flag (this project's own operator error), and API credit exhaustion mid-run, twice. Final certification: **FAIL for exactly one well-evidenced reason** — discoverability narrowly missing its 0.90 floor, diagnosed as a metric-scoping artifact (two "ambiguous input" cases are structurally unable to score high on a tool-use metric because *not* using a tool is their correct behavior), not an actual skill defect. Full trail: [`docs/MILESTONE_4_PERFORMANCE_ATTRIBUTION.md`](docs/MILESTONE_4_PERFORMANCE_ATTRIBUTION.md).
- **Portfolio Overview** (Milestone 5): a second complete 150-trial matrix scored **Skill Lift +0.1316**, real. Certification: **FAIL for the same single reason as Performance Attribution** — discoverability (0.8942 here vs 0.8862 there), independently corroborated by NVIDIA's own report recommending the same fix Milestone 4 had already diagnosed. The run also surfaced a **certification policy-profile gap** — one minimum metric (`reconciliation`) was specific to Performance Attribution's own grader and silently failed every other skill in the catalog regardless of quality, found by actually running the real pipeline twice rather than auditing the policy file in the abstract — **resolved 2026-08-31** by dropping it from the universal minimum metrics. Evidence: [`skills/portfolio-overview/BENCHMARK.md`](skills/portfolio-overview/BENCHMARK.md).
- **Milestone 6** (deliberate defects, `DONE`): 5 of 6 intentionally-introduced defects (vague description, duplicate skill, missing derivatives, mismatched dates, unauthorized data source) are caught and confirmed with real evidence — Tier 1 quality scoring, Tier 2 embedding similarity, and grader regression tests. The sixth (a weak/no-value skill's Skill Lift) was accepted on a Tier 1 proxy rather than a live measurement, a deliberate human-reviewer call, not a silently dropped gap. Full trail: [`docs/MILESTONE_6_DELIBERATE_DEFECTS.md`](docs/MILESTONE_6_DELIBERATE_DEFECTS.md).
- **Milestone 9** (CI/CD, `DONE`): two real GitHub Actions jobs now gate a PR — `tier1` blocks on Tier 1 validation failure and, as of 2026-08-31, a real ownership-enforcement check (`framework/certification/check_ownership.py`) that fails on the literal `domain-owner-required` placeholder; `similarity` (real as of 2026-08-31, live as of 2026-09-01 with `OPENAI_API_KEY` configured as a repo secret) applies this project's own `policies/similarity.yaml` governance actions against the central catalog, blocking only on `EXACT_DUPLICATE`. All 13 skills carry real ownership values. A working demonstration of "invalid or duplicate skills can't merge," not a full production pipeline — `tier3-fast` and `domain-graders` remain documented placeholders.
- **Zero-cost follow-ups completed 2026-08-31 through 2026-09-01**: dropped the `reconciliation` policy gap, added the ownership gate above, prepared (but not yet live-confirmed) a discoverability fix by adding unforced-preamble eval-case twins to all three flagship skills, and expanded all 9 structurally-complete skills' eval suites from 10 to 25 real, fixture-grounded cases each — **300 cases across the 12 PM skills, plus six flagship twins and one smoke case**. Then, 2026-09-01: built the real central similarity catalog and wired the `similarity` CI job above; replaced the single flat certification profile with five real risk-tiered profiles (`policies/certification.yaml`, resolved by `framework/certification/profile_resolver.py` from a skill's `risk_level`); built a lightweight skill registry (`catalogs/skill-registry.json`) that now auto-regenerates on every merge to `main`; assigned an owner/SLA to the `HIGH_SIMILARITY` review action; root-caused why an attempted discoverability-confirmation rerun ran the full case set instead of a trimmed one (the pinned evaluator never reads `skill.yaml`'s `dataset:` field — see `docs/13_NVIDIA_EVALUATOR_UPGRADE_POLICY.md` §13.6); and did a documentation consistency pass (fixed stale status claims, removed two orphaned bootstrap docs). None of this spent any live API budget beyond the fractions of a cent for embedding calls.
- **One finding remains open for human review** — the recurring discoverability metric-scoping shortfall; a partial fix is prepared but not yet confirmed with a live rerun (now unblocked in principle by the dataset-routing root-cause above, but a live rerun is still a real-cost decision). See [`docs/10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md`](docs/10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md)'s "Open policy decisions pending human review."
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
| 5 | Three-skill vertical slice | `IN PROGRESS` | 2 of 3 skills have finalized full certification evidence (both real `FAIL`); Risk Explanation has a quick pass plus two non-finalized live attempts blocked by runtime preflight |
| 6 | Deliberate defect demonstration | `DONE` | 5 of 6 defects caught directly; 1 accepted on proxy evidence |
| 7 | Complete 12-skill library | `IN PROGRESS` | Right-sized to structural completion for 9 skills; blocked from fully closing only by Milestone 5 |
| 8 | Finance grader library | `DONE` | Required graders built, reused across all 12 skills |
| 9 | CI/CD | `DONE` | Real Tier 1 + Tier 2 similarity PR gates, right-sized from an 11-task pipeline |
| 10 | Remediation engine | `DESCOPED` | Beyond the learning-focused goal; documented as a future extension |
| 11 | Cross-repository portability | `DESCOPED` | Same reasoning as Milestone 10 |
| 12 | Registry & production model | `DESCOPED` | Same reasoning as Milestone 10 |

## Next steps

- **Run Risk Explanation's full live Tier 3 certification matrix** — refined to standard and quick-pass validated, but the 2026-09-03/04 attempts did not produce certification evidence: the first was manually capped after 100 observed arms at an estimated $30, and the second stopped during Claude Code runtime preflight after 72 seconds. The full run remains the only thing blocking Milestones 5 and 7 from closing. The pinned CLI has no case-level resume or reliable cost telemetry; use an explicit budget and retain Harbor jobs before trying again.
- **Confirm the discoverability fix with a live rerun** — the unforced-preamble eval-case twins are prepared (zero cost) but not yet verified against a real Tier 3 matrix. See [`docs/10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md`](docs/10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md)'s "Open policy decisions pending human review."
- **Optional, lower priority:** decide whether any of the 9 structurally-complete skills (now at full 25-case depth, ready to go) warrant full live Tier 3 certification depth later, and whether Milestone 9's CI gate should ever be extended toward the `tier3-fast`/`domain-graders` jobs it still leaves as documented placeholders (the `similarity` job is no longer one of them — see above) — both are deliberately not being pursued now per the 2026-08-30 scope decision, not accidentally incomplete.

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

## Adopting this framework (for another team)

This repository is designed to be **consumed by**, not forked into, other
skill repositories. A consuming team keeps its own skills and domain
content, adds a small `pmai-skills.yaml` config and the reusable CI
workflow, and depends on a pinned framework version rather than copying
implementation or parsing raw NVIDIA reports directly:

```text
my-domain-skills/
├── skills/
├── pmai-skills.yaml
└── .github/workflows/skills-quality.yml
```

The day-to-day interface is a thin wrapper around the pinned `skillevaluator` CLI:

```bash
# Install the framework CLI locally
pip install -e .   # or: uv pip install -e .

# 1. Zero-cost offline mode (no Docker or API keys required, completes in seconds)
pmai-skills validate ./skills                                # Validate package structure & schema
pmai-skills certify ./skills/performance-attribution \
  --profile release --metrics reports/m5/.../metrics.json     # Apply certification policy to benchmark metrics

# 2. Live / Credentialed mode
pmai-skills similarity ./skills/my-new-skill                  # Check catalog duplicates (requires OPENAI_API_KEY)
pmai-skills evaluate ./skills/my-new-skill --profile pr       # Run live Tier 3 evaluation (requires Docker & LLM API keys)
```

**Current status:** `pmai-skills` exists for package validation, ownership
checks, evaluator invocation, report normalization, similarity governance,
and certification decisions — it is not yet published as an installable
central package. It is intentionally a thin pass-through: PM manifest/
ownership checks, output normalization, and certification policy, nothing
more; it should not reimplement flags or behavior NVIDIA already provides.

Full adoption path: [`docs/11_QUICKSTART_FOR_CONSUMERS.md`](docs/11_QUICKSTART_FOR_CONSUMERS.md)
and [`docs/06_ADOPTION_GUIDE.md`](docs/06_ADOPTION_GUIDE.md). Full skill
lifecycle from draft to certification:
[`docs/12_END_TO_END_SKILL_WORKFLOW.md`](docs/12_END_TO_END_SKILL_WORKFLOW.md).

## Architecture, in one picture

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

Two boundaries carry most of the design's weight: skills call stable
**Agentic Data Pipeline** logical capabilities (never a physical database or
vendor API directly), and nothing outside `framework/adapters/` parses
NVIDIA's raw report format — everything downstream consumes a normalized PM
AI result schema instead, so an evaluator version bump is a contained,
testable event rather than a library-wide breaking change.

Full layer-by-layer detail, the evaluation-provider abstraction, benchmark
identity rules, governance model, and a core-terms glossary:
[`docs/02_TARGET_ARCHITECTURE.md`](docs/02_TARGET_ARCHITECTURE.md). Narrative
walkthrough of the same diagram with real evidence:
[`docs/14_EXECUTIVE_SUMMARY_AND_WALKTHROUGH.md`](docs/14_EXECUTIVE_SUMMARY_AND_WALKTHROUGH.md).
NVIDIA version-pinning policy (currently `0.2.1` /
`009aa300be7925c7ba75760592baeb941cc29ba8`) and the governed upgrade
process: [`docs/13_NVIDIA_EVALUATOR_UPGRADE_POLICY.md`](docs/13_NVIDIA_EVALUATOR_UPGRADE_POLICY.md).

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
├── .github/skills/          # Copilot project-skill loaders (see trainer above)
└── .github/workflows/
```

## Current status & production-adoption caveats

Two skills (Performance Attribution, Portfolio Overview) have been taken
all the way through the real pipeline with genuine evidence on disk; the
remaining nine reference skills are structurally complete but not yet run
through a live Tier 3 matrix, and several production-scale pieces
(a remediation engine, cross-repo portability, a full production registry)
remain intentionally unbuilt per the 2026-08-30 scope decision (see
[Scope](#scope)). Actually adopting this in a production organization would
still require approved internal tool/data connectors (this repo uses a
synthetic, local pipeline instead — see
[`docs/MILESTONE_3_SYNTHETIC_DATA_PIPELINE.md`](docs/MILESTONE_3_SYNTHETIC_DATA_PIPELINE.md)),
chosen model/agent credentials, environment-specific security controls,
organization-specific ownership metadata, and CI secret configuration.

Full current status, per-milestone detail, and what's still genuinely
undecided: [`docs/10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md`](docs/10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md).

## Where to go next

- Full reader-oriented documentation map, grouped by goal:
  [`docs/README.md`](docs/README.md)
- Tracked benchmark evidence and explicit caveats:
  [`docs/EVIDENCE_INDEX.md`](docs/EVIDENCE_INDEX.md)
- Curated external references (NVIDIA, Anthropic/Agent Skills, OpenAI,
  Microsoft, AWS, LangSmith, Google):
  [`docs/09_REFERENCES_AND_RESOURCES.md`](docs/09_REFERENCES_AND_RESOURCES.md)
