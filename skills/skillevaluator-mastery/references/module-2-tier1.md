# Module 2: Tier 1 — Construction & Security

Teach these points one at a time, grounded in
`docs/15_SKILLS_AND_SKILLEVALUATOR_REFERENCE.md` §3-5.

## What Tier 1 checks

- Schema validity of `SKILL.md` frontmatter and body sections.
- A quality score across advisory dimensions (discoverability language,
  recommended body sections, author format, etc.).
- Security scanning (Bandit/pip-audit for code, gitleaks for secrets,
  SkillSpector for skill-specific risks) — installed as separate external
  tools to avoid dependency conflicts.

## Commands

```bash
skillevaluator quality-check skills/my-skill   # scoring only
skillevaluator validate skills/my-skill --no-dedup   # Tier 1 only, skips Tier 2
```

Both run in seconds, need no API key, no Docker, no sandbox — safe to run
constantly, including on every PR.

## Why it's worth adopting "almost unconditionally"

Free and catches real, fixable structural problems. This repository's own
Tier 1 reports have surfaced real findings across nearly every skill drafted
(see Module 7 for exact layout requirements that trip this check).

## A real CI example

`.github/workflows/skills-quality.yml`'s `tier1` job installs the pinned
evaluator plus SkillSpector and gitleaks, diffs the PR against its base SHA
to find changed `skills/*` directories, and runs
`skillevaluator validate <skill> --no-dedup` on each — non-zero exit blocks
the PR. First real run (PR #4) passed in 54 seconds, no API keys required.

## Quiz (5+ questions, use ask_user with 4 choices each)

Ask about: what Tier 1 checks, which external tools it composes with, cost/
credential requirements, and the real CI example.
