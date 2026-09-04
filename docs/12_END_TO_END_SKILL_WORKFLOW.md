# End-to-End Skill Workflow

This is the canonical walkthrough for taking a new agent skill from an idea to
an evidence-backed production decision. It connects the architecture, consumer
quickstart, evaluation rules, and milestone evidence into one path.

## The goal in plain language

A skill is a reusable set of instructions that helps an AI agent perform a job,
such as explaining portfolio performance. This framework answers five practical
questions before the skill is approved:

1. Is the package complete and safe?
2. Is it meaningfully different from skills we already have?
3. Does it help the agent perform the task?
4. Are its financial answers supported by authoritative data?
5. Can another team reproduce and trust the result?

## End-to-end flow

```text
Skill idea
   |
   v
Package SKILL.md + skill.yaml + eval cases
   |
   v
Validate structure and security (Tier 1)
   |
   v
Check similarity with the approved catalog (Tier 2)
   |
   v
Run the agent with and without the skill (Tier 3)
   |
   v
Check financial truth with deterministic domain graders (Tier 4)
   |
   v
Normalize results + retain benchmark evidence
   |
   v
Apply certification policy
   |---------------------------|
   v                           v
Certified and publish       Remediate, add regression case, rerun
```

## Step 0 — Define ownership and scope

The consuming repository owns the skill, its evaluation cases, business owner,
risk classification, and any local fixtures. The central framework owns the
schemas, provider adapter, common graders, certification policy, and reporting
format. The agent runtime and data pipeline remain separate systems.

See [`docs/02_TARGET_ARCHITECTURE.md`](02_TARGET_ARCHITECTURE.md) for these
responsibility boundaries.

## Step 1 — Package the skill

Create a directory containing:

```text
skills/my-new-skill/
├── SKILL.md
├── skill.yaml
└── evals/
    ├── EVAL.md
    └── evals.json
```

The instructions describe when and how the agent should use the skill. The
manifest gives it an identity, owner, risk classification, version, and logical
tool dependencies. The evaluation cases define what a good response looks like.

See [`docs/03_SKILL_STANDARD.md`](03_SKILL_STANDARD.md).

## Step 2 — Make data access portable

Skills refer to logical capabilities such as `portfolio.positions` and
`performance.attribution`; they do not hard-code a database or vendor API.
During development, use the deterministic fixtures and tools in
[`synthetic_data_pipeline/`](../synthetic_data_pipeline/). In production, an
authorized data-pipeline implementation can provide the same contracts.

The current fixture setup and expected outputs are documented in
[`docs/MILESTONE_3_SYNTHETIC_DATA_PIPELINE.md`](MILESTONE_3_SYNTHETIC_DATA_PIPELINE.md).

## Step 3 — Run the quality and security gate

Run the framework validation for the skill:

```bash
uv run pmai-skills validate ./skills/my-new-skill
```

Tier 1 checks package structure, metadata, instruction quality, and security
signals. A failure here is fixed before spending time on live-agent evaluation.
The repository's real Tier 1 evidence is in
[`reports/m1/tier1-v296/`](../reports/m1/tier1-v296/) and
[`docs/MILESTONE_1_SETUP.md`](MILESTONE_1_SETUP.md).

## Step 4 — Check catalog similarity

```bash
uv run pmai-skills similarity ./skills/my-new-skill
```

The candidate is compared with approved skills. Exact duplicates are blocked;
high similarity requires review; looser relationships are recorded as advice.
This prevents multiple teams from publishing different names for the same
capability.

## Step 5 — Run the live agent evaluation

```bash
uv run pmai-skills evaluate ./skills/my-new-skill --profile pr
```

The evaluator runs the same cases in two arms:

- with the skill available;
- without the skill available (the baseline).

The comparison shows whether the skill earns its place. Review correctness,
security, discoverability, effectiveness, efficiency, Skill Lift, and pass@k.
The evaluator runs in a sandbox with the configured agent, credentials, logical
tools, and fixtures. Credentials are supplied through the environment and are
never committed to the repository.

## Step 6 — Apply domain truth checks

For financial skills, deterministic graders check claims against known truth.
Typical checks include attribution reconciliation, benchmark and date
consistency, portfolio coverage, provenance, authorization, and numeric
grounding. Deterministic analytical output takes precedence over a subjective
LLM judgment.

See [`docs/04_EVALUATION_AND_CERTIFICATION.md`](04_EVALUATION_AND_CERTIFICATION.md).

## Step 7 — Normalize and retain evidence

The provider adapter converts evaluator-specific output into the framework's
stable result schema. Retain the raw report alongside normalized JSON,
Markdown/HTML summaries, and benchmark metadata. A benchmark is only valid for
the exact combination of skill version, data/fixture version, agent, model,
evaluator, grader, and execution environment.

## Step 8 — Certify or remediate

For a release candidate, run the full profile:

```bash
uv run pmai-skills certify ./skills/my-new-skill --profile release --metrics normalized-metrics.json
```

Certification applies hard gates (for example security, authorization,
provenance, regression, and ownership) plus weighted quality metrics. If a gate
fails, record the failure, improve the skill or tool contract, add a regression
case, and rerun the affected stages. Do not treat a high average score as a
replacement for a failed hard gate.

## Step 9 — Publish and operate

After certification, publish the skill version, digest, owner, dependencies,
benchmark location, certification state, and expiration/rebenchmark rule. In
production, use telemetry to find routing misses, tool failures, drift, cost,
and latency; convert reviewed failures into regression cases.

## What is implemented today

Milestones 1–3 establish the foundation for this workflow:

- Milestone 1 proved the local NVIDIA Tier 1 path and completed a controlled
  Tier 3 sandbox smoke test.
- Milestone 2 created stable framework schemas and provider normalization so
  downstream code does not depend on NVIDIA's raw report format.
- Milestone 3 created deterministic logical tools and fixtures so reference
  evaluations can run without production data systems.

Milestones 4–9 have since added two live benchmark attempts, reusable finance
graders, deliberate-defect evidence, ownership and similarity governance, and a
lightweight registry. The framework CLI now covers the implemented offline
checks, evaluator invocation, report normalization, and policy decision. Tier 3
and domain-grader CI remain advisory/documented placeholders.

## Related documents

- [Target architecture](02_TARGET_ARCHITECTURE.md)
- [Evaluation and certification](04_EVALUATION_AND_CERTIFICATION.md)
- [Consumer quickstart](11_QUICKSTART_FOR_CONSUMERS.md)
- [Development roadmap](10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md)
