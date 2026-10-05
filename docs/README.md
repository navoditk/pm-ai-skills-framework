# Documentation

Every document in this repository, grouped by what you are trying to do. New
here? Read the [project README](../README.md), then
[Tutorial 00](00_TUTORIAL.md). To learn SkillEvaluator itself, the
[course site](https://navoditk.github.io/pm-ai-skills-framework/) is the
quickest route.

Documents are numbered in the order they were written, not the order to read
them.

## Learn SkillEvaluator

| Document | What it is for |
|---|---|
| [SkillEvaluator Mastery course](https://navoditk.github.io/pm-ai-skills-framework/) | Eight modules with quizzes, troubleshooting scenarios, and a final exam, in the browser |
| [The Skills Ledger](https://navoditk.github.io/pm-ai-skills-framework/skills-ledger.html) | A ten-slide crash course: why skill governance matters and what the real runs found |
| [16. Mastery tutorial](16_SKILLEVALUATOR_MASTERY.md) | Scaffold a toy skill, run each tier, break it on purpose, and read a real report |
| [15. Skills and SkillEvaluator reference](15_SKILLS_AND_SKILLEVALUATOR_REFERENCE.md) | Every command, setting, cost, and finding in one place |
| [`skillevaluator-mastery` skill](../skills/skillevaluator-mastery/) | The same course as an agent skill; say `skillevalexpert` to Claude Code, Codex, or GitHub Copilot in this checkout |

## Try the framework

| Document | What it is for |
|---|---|
| [00. Tutorial](00_TUTORIAL.md) | The local path, with no credentials, Docker, or network |
| [12. End-to-end skill workflow](12_END_TO_END_SKILL_WORKFLOW.md) | One skill from draft to certification decision |

## Understand the design

| Document | What it is for |
|---|---|
| [14. Executive summary](14_EXECUTIVE_SUMMARY_AND_WALKTHROUGH.md) | The whole project in one document, with an honest assessment |
| [01. Proposal](01_PROPOSAL.md) | The problem, the goals, and the explicit non-goals |
| [02. Target architecture](02_TARGET_ARCHITECTURE.md) | The layers, the evaluator boundary, the governance model, and a glossary |
| [13. Evaluator upgrade policy](13_NVIDIA_EVALUATOR_UPGRADE_POLICY.md) | Why SkillEvaluator is pinned, the local patch, and how upgrades are governed |

## Write and certify a skill

| Document | What it is for |
|---|---|
| [03. Skill standard](03_SKILL_STANDARD.md) | Package layout, frontmatter, manifest, and ownership rules |
| [04. Evaluation and certification](04_EVALUATION_AND_CERTIFICATION.md) | Risk levels, policy profiles, and metric thresholds |
| [Sample certification report](../examples/sample-certification-report.md) | What a certification decision looks like |

## Adopt it elsewhere

| Document | What it is for |
|---|---|
| [11. Consumer quickstart](11_QUICKSTART_FOR_CONSUMERS.md) | Setting up `pmai-skills.yaml` and the CI workflow in another repository |
| [06. Adoption guide](06_ADOPTION_GUIDE.md) | Rolling the framework out across teams |

## Status and evidence

| Document | What it is for |
|---|---|
| [10. Roadmap and progress](10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md) | The canonical status: every milestone, its evidence, and the scope decisions |
| [Evidence index](EVIDENCE_INDEX.md) | Every tracked benchmark record, and how to read it before drawing conclusions |
| [Milestone 1: setup](MILESTONE_1_SETUP.md) | Installing and pinning the evaluator, and the first Tier 1 and Tier 3 runs |
| [Milestone 3: synthetic data](MILESTONE_3_SYNTHETIC_DATA_PIPELINE.md) | The local fixtures that stand in for portfolio systems |
| [Milestone 4: Performance Attribution](MILESTONE_4_PERFORMANCE_ATTRIBUTION.md) | The first full live evaluation, including the four problems it surfaced |
| [Milestone 6: deliberate defects](MILESTONE_6_DELIBERATE_DEFECTS.md) | Six planted defects and which checks caught them |

Raw evaluator reports stay under `reports/` in the checkout that produced
them and are not committed. The tracked records are each skill's
`BENCHMARK.md` and normalized JSON, listed in the evidence index.

## Further reading

| Document | What it is for |
|---|---|
| [09. References and resources](09_REFERENCES_AND_RESOURCES.md) | External standards, vendor documentation, and papers that informed the design |

## History

These were written for the original blueprint, before the framework was
built. They are kept for the record; the roadmap is the current source.

| Document | What it was for |
|---|---|
| [05. Implementation plan](05_IMPLEMENTATION_PLAN.md) | The planned phases, superseded by the milestones in the roadmap |
| [07. GitHub publishing](07_GITHUB_PUBLISHING.md) | Steps for first publishing the blueprint repository |
| [08. Demo and acceptance plan](08_DEMO_AND_ACCEPTANCE_PLAN.md) | The planned defect demonstration, carried out as Milestone 6 |
