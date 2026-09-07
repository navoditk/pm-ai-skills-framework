# Module 6: Installing & Running SkillEvaluator

Teach these points one at a time, grounded in
`docs/15_SKILLS_AND_SKILLEVALUATOR_REFERENCE.md` §4 and
`docs/13_NVIDIA_EVALUATOR_UPGRADE_POLICY.md`.

## General upstream install

```bash
# Prerequisites: uv (or pip), Python 3.12 or 3.13, git; Docker only for Tier 3
uv tool install --python 3.13 "skillevaluator[all] @ git+https://github.com/NVIDIA/SkillEvaluator.git"

skillevaluator --version
skillevaluator health-check
```

Smaller footprints exist: `skillevaluator` (Tier 1 only), `[security]`
(+ Bandit/pip-audit), `[tier2,tier3]` (+ dedup and live-agent eval).

External security tools install separately to avoid dependency conflicts:

```bash
brew install gitleaks
uv tool install git+https://github.com/NVIDIA/SkillSpector.git
```

## Why pin an exact commit

Installing `@main` is fine for exploration; for anything you intend to
certify against, **pin an exact commit**. SkillEvaluator's own release notes
and this repository's own experience both found real, breaking behavioral
differences worth pinning against.

```bash
uv venv .venv --python 3.13
uv pip install --python .venv/bin/python \
  'skillevaluator[all] @ git+https://github.com/NVIDIA/SkillEvaluator.git@<pinned-sha>'
```

This repository also tracks a local patch for a real judge-truncation bug
found in its pinned version (`patches/skillevaluator-0.2.1-judge-max-tokens.patch`)
— apply it only if your pinned version predates NVIDIA's own upstream fix.

## Per-tier run commands

See Modules 2-4 for the exact Tier 1/2/3 commands and their required
environment variables.

## Quiz (5+ questions, use ask_user with 4 choices each)

Ask about: the install extras, why pinning matters, and how to verify an
install (`--version`, `health-check`).
