# PM AI Skills Framework

A governance layer for agent skills, built on
[NVIDIA SkillEvaluator](https://github.com/NVIDIA/SkillEvaluator) and tested
against a library of twelve portfolio-management skills. SkillEvaluator
measures a skill; this repository decides what the measurement means:
who owns the skill, whether it duplicates another, whether its answers are
financially correct, and whether it is good enough to certify at its risk
level.

The project is a learning reference first. It exists to understand how
SkillEvaluator works and how far its numbers can be trusted, using a
realistic domain instead of a toy example. It is not a production platform;
see [Status](#status).

**Learn SkillEvaluator:** take the free
[SkillEvaluator Mastery course](https://navoditk.github.io/pm-ai-skills-framework/)
(eight modules, quizzes, scenarios, and a final exam), or download it as
[one file](https://navoditk.github.io/pm-ai-skills-framework/skillevaluator-mastery-standalone.html).

## What is here

| Part | What it does | Where |
|---|---|---|
| Skill library | Twelve PM skills, each with an eval dataset and grader, plus the course skill and a Tier 3 smoke test | [`skills/`](skills/) |
| Evaluator adapter | Turns raw NVIDIA reports into one stable schema, so an evaluator upgrade cannot change certification logic | [`framework/adapters/`](framework/adapters/) |
| Certification engine | Applies risk-tiered policy to evaluation results | [`framework/certification/`](framework/certification/), [`policies/`](policies/) |
| Finance graders | Deterministic checks generic scoring misses: reconciliation, stale dates, missing derivatives | [`graders/finance/`](graders/finance/) |
| Similarity catalog | Blocks exact duplicates and routes near-duplicates to review | [`catalogs/`](catalogs/), [`policies/similarity.yaml`](policies/similarity.yaml) |
| Synthetic data | Local fixtures standing in for real portfolio systems | [`synthetic_data_pipeline/`](synthetic_data_pipeline/) |
| CLI | `pmai-skills`: validate, similarity, evaluate, report, certify | [`framework/cli/`](framework/cli/) |
| CI gates | Tier 1 validation, ownership, and duplicate detection on every pull request | [`.github/workflows/`](.github/workflows/) |

## Quick start

Everything here runs locally with no API keys, Docker, or network calls.

```bash
uv sync --extra dev
uv run pytest -q
uv run pmai-skills validate skills
uv run python synthetic_data_pipeline/tool_cli.py portfolio.summary --portfolio-id ABC
```

[Tutorial 00](docs/00_TUTORIAL.md) walks through this path in about five
minutes. Adding `--tier1` to `validate` runs NVIDIA's own Tier 1 checks, which
are also free and offline, once the [pinned evaluator](docs/13_NVIDIA_EVALUATOR_UPGRADE_POLICY.md)
is installed. Tier 2 needs an embedding key, and Tier 3 needs Docker and model
credentials, at about $15-45 per skill for a full run.

## How it fits together

```text
Skill source  ->  NVIDIA SkillEvaluator (Tier 1/2/3)  ->  PM domain graders (Tier 4)
                             |                                     |
                             v                                     v
                  normalized adapter output  ---->  certification engine  ->  registry
```

Two boundaries carry most of the design. Skills call logical data
capabilities, never a database or vendor API directly. And nothing outside
`framework/adapters/` reads NVIDIA's raw report format. The full design is in
[target architecture](docs/02_TARGET_ARCHITECTURE.md); the evaluator is
pinned to `0.2.1` (`009aa300`) under the
[upgrade policy](docs/13_NVIDIA_EVALUATOR_UPGRADE_POLICY.md).

## What the evidence shows

- **Two skills went through the full pipeline**, with a live agent, live
  judge, Docker sandbox, and real certification policy. Performance
  Attribution scored a Skill Lift of **+0.1253** and Portfolio Overview
  **+0.1316**, each over 150 trials.
- **Both failed certification, for the same diagnosed reason.**
  Discoverability came in just under its 0.90 floor (0.8862 and 0.8942).
  The cause is metric scoping: cases where the right behavior is *not* to
  call a tool cannot score high on a tool-use metric. A fix is prepared but
  not yet confirmed by a live rerun. No skill has been certified yet, and the
  project reports that plainly.
- **Five of six deliberate defects were caught** by Tier 1 scoring, Tier 2
  similarity, and grader regression tests. The sixth was accepted on proxy
  evidence by a reviewer.
- **Four real problems surfaced on the way:** an agent-compatibility gap in
  the evaluator's tool recognition, a judge token-truncation bug (patched in
  [`patches/`](patches/)), a missing `--copy-repo` flag, and API credit
  exhaustion mid-run.

The [executive summary](docs/14_EXECUTIVE_SUMMARY_AND_WALKTHROUGH.md) is the
cold-readable walkthrough, and the [evidence index](docs/EVIDENCE_INDEX.md)
lists every tracked benchmark record.

## Status

| # | Milestone | Status |
|---|---|---|
| 0-3 | Blueprint, environment, contracts, synthetic data | Done |
| 4 | Performance Attribution, end to end | Evidence complete; certification failed on one diagnosed metric |
| 5 | Three-skill slice | Two of three complete; Risk Explanation's full live run is outstanding |
| 6 | Deliberate defect demonstration | Done |
| 7 | Twelve-skill library | Nine skills structurally complete with 25 eval cases each |
| 8 | Finance grader library | Done |
| 9 | CI/CD gates | Done: Tier 1, ownership, and similarity block pull requests |
| 10-12 | Remediation, portability, production registry | Descoped from the learning goal |

Open work is Risk Explanation's full Tier 3 run and a live rerun to confirm
the discoverability fix; both cost real money, so they wait on a decision.
The [roadmap](docs/10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md) has the full
history, every milestone's evidence, and the scope decisions behind it.

Using this in production would still need approved data connectors in place
of the synthetic pipeline, real credentials and security controls, and your
organization's ownership metadata.

## Is it a fit?

Probably, if several teams build similar finance skills, you need stricter
bars for decision-support skills than for informational ones, generic
LLM-judge scores miss your failure modes, and you can afford Tier 3 runs and
an Experimental-support evaluator. Probably not, if one team owns a handful
of skills and free Tier 1 checks are enough.

To adopt it in another repository, start with the
[consumer quickstart](docs/11_QUICKSTART_FOR_CONSUMERS.md) and the
[adoption guide](docs/06_ADOPTION_GUIDE.md).

## Documentation

The [documentation index](docs/README.md) groups every document by what you
are trying to do. [CONTRIBUTING](CONTRIBUTING.md) covers adding skills,
graders, and docs.
