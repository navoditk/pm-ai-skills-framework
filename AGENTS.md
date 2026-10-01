# AGENTS.md

Instructions for any coding agent working in this repository: Claude Code,
GitHub Copilot, and Codex all read this file. `CLAUDE.md` imports it and
`.github/copilot-instructions.md` points to it; keep the rules here.

## What this repository is

A governance layer over NVIDIA SkillEvaluator, exercised on twelve
portfolio-management skills. Start with `README.md`; `docs/README.md` indexes
every document by goal, and `docs/10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md` is
the current status.

## Commands

```bash
uv sync --extra dev                              # install, including dev tools
uv run pytest -q                                 # all tests; no network
uv run ruff check . && uv run ruff format --check . --exclude "*.md"
uv run pmai-skills validate skills               # offline framework checks
uv run python scripts/build_curriculum_pages.py  # course site, into public/
```

## Rules

- **Public and synthetic data only.** Skills read the local fixtures in
  `synthetic_data_pipeline/`. No real portfolio data, internal system names,
  or credentials in code, docs, commits, or evaluation cases.
- **No network in tests.** Nothing under `tests/` may call a model, an
  embedding provider, or any other service.
- **Live evaluation costs money; never start it unasked.** Tier 2 needs an
  embedding key, and a full Tier 3 run cost $15-45 per skill. Run Tier 1 and
  the offline checks freely; run `pmai-skills similarity`,
  `pmai-skills evaluate`, or `skillevaluator ... --agent-eval` only when a
  person has asked for that specific run and its cost.
- **Do not commit raw reports.** `reports/` is git-ignored. Tracked evidence
  is each skill's `BENCHMARK.md` and `BENCHMARK.json`; do not link docs to
  files under `reports/` (`tests/test_docs_links.py` fails if you do).
- **Only `framework/adapters/` reads NVIDIA's raw report format.** Everything
  downstream uses the normalized schema, so an evaluator upgrade stays
  contained.
- **The evaluator is pinned** to one commit, installed by
  `.github/workflows/skills-quality.yml` and `docs/MILESTONE_1_SETUP.md`, and
  changed only under `docs/13_NVIDIA_EVALUATOR_UPGRADE_POLICY.md`.
- **Edit the canonical skill, not its loaders.** Skills live in
  `skills/<name>/`. `.claude/skills/` and `.agents/skills/` hold identical
  thin loaders that point back to it; `tests/test_skill_loaders.py` keeps
  them in step.
- **Every skill needs an owner.** CI fails on the `domain-owner-required`
  placeholder.
- **The course site is generated.** Edit the skill's `references/`, docs 15
  and 16, or `site/`; never edit `public/`. Quiz questions are in
  `site/quizzes.yaml`, and every answer must be stated in its module.
- **`ruff format` rewrites Python inside Markdown fences**, which is why CI
  excludes `*.md`. Do not reformat docs as a side effect of a code change.
