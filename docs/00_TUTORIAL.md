# Tutorial: Your First SkillEvaluator Run

This is the local, no-credentials path through the repository. It teaches the
relationship between a skill package, evaluation cases, deterministic graders,
and certification policy before introducing expensive live-agent evaluation.

## 1. Set up the checkout

```bash
uv sync --extra dev
uv run pmai-skills --help
uv run pytest -q
```

This path does not call NVIDIA, an embedding provider, Docker, or a live model.

## 2. Inspect a skill

Open these files together:

```text
skills/portfolio-overview/SKILL.md
skills/portfolio-overview/skill.yaml
skills/portfolio-overview/evals/evals.json
skills/portfolio-overview/evals/grader.py
graders/finance/portfolio_overview.py
```

The first file teaches the agent, the manifest describes ownership and risk,
the dataset defines cases, and the grader checks domain evidence.

## 3. Use the synthetic logical tools

```bash
uv run python synthetic_data_pipeline/tool_cli.py portfolio.summary --portfolio-id ABC
uv run python synthetic_data_pipeline/tool_cli.py portfolio.positions --portfolio-id ABC
```

Notice the `as_of`, `source`, `fixture_version`, and derivative coverage fields.
Those metadata fields are what domain graders use to catch plausible but unsafe
answers.

## 4. Run the offline framework checks

```bash
uv run pmai-skills validate skills/portfolio-overview
uv run pmai-skills validate skills
```

Add `--tier1` only after installing the pinned NVIDIA evaluator. Tier 1 is free
and offline but depends on that external binary.

## 5. Read a deliberate failure

```bash
uv run pytest -q tests/test_synthetic_pipeline.py tests/test_graders.py
```

The synthetic pipeline can omit derivatives or return stale data. A good skill
reports the limitation; it does not silently fill in missing data.

## 6. Understand the four tiers

- Tier 1: package quality and security.
- Tier 2: semantic overlap with the approved catalog.
- Tier 3: live with-skill versus without-skill agent behavior.
- Tier 4: project-owned domain truth checks, such as reconciliation and dates.

Only Tier 3 needs live agent/judge credentials and Docker. Tier 2 needs an
embedding provider. See the real Tier 3 lessons and costs in
[`docs/15_SKILLS_AND_SKILLEVALUATOR_REFERENCE.md`](15_SKILLS_AND_SKILLEVALUATOR_REFERENCE.md).

## 7. Continue to a live run

Install the exact evaluator version described in
[`docs/13_NVIDIA_EVALUATOR_UPGRADE_POLICY.md`](13_NVIDIA_EVALUATOR_UPGRADE_POLICY.md),
then use:

```bash
uv run pmai-skills evaluate skills/portfolio-overview --profile pr
```

Record the agent, judge, model, dataset, fixture, evaluator version, cost, and
environment. A score without that identity is not durable evidence.
