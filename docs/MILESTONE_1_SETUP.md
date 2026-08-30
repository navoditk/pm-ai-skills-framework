# Milestone 1 — Development Environment & NVIDIA Smoke Test

## Pinned toolchain

- Python: 3.13.15 (isolated in `.venv/`; NVIDIA SkillEvaluator requires `>=3.12,<3.14`)
- NVIDIA SkillEvaluator: 0.2.1
- NVIDIA SkillEvaluator source commit: `009aa300be7925c7ba75760592baeb941cc29ba8`
- Harbor: 0.13.2 (installed by the SkillEvaluator `tier3` extra)
- SkillSpector: 2.9.6 (source commit `29b0dc8c39424e8e31ca055fa027adf8ba8f9650`; compatible with SkillEvaluator 0.2.1)
- Gitleaks: 8.30.1
- Codex CLI: 0.150.0
- Docker CLI: 29.6.2; Docker Desktop daemon must be running for Tier 3
- Provider preflight: OpenAI credential loaded transiently from `/Users/navoditkaushik/GitHub/credentials/keys.rtf`; use `OPENAI_BASE_URL=https://api.openai.com/v1`
- Judge model: `SKILL_EVAL_JUDGE_MODEL=claude-sonnet-5`, set explicitly and
  separately from the Tier 3 agent's model. Without this override, the judge
  silently falls back to whichever model the agent uses (`claude-opus-5` in
  Milestone 4's Claude Code runs) via the evaluator's "public provider
  default" path — the two roles are unrelated and do not need the same model.
  See the Milestone 4 doc for the reasoning.

## Installation

```shell
uv venv .venv --python 3.13
uv pip install --python .venv/bin/python \
  'skillevaluator[all] @ git+https://github.com/NVIDIA/SkillEvaluator.git@009aa300be7925c7ba75760592baeb941cc29ba8'
uv pip install --python .venv/bin/python \
  'git+https://github.com/NVIDIA/SkillSpector.git@29b0dc8c39424e8e31ca055fa027adf8ba8f9650'
brew install gitleaks
patch -p1 -d .venv/lib/python3.13/site-packages < patches/skillevaluator-0.2.1-judge-max-tokens.patch
```

The final `patch` step applies a tracked local fix for a judge-truncation bug
in the pinned evaluator (see `patches/README.md` and
`docs/13_NVIDIA_EVALUATOR_UPGRADE_POLICY.md` §13.6). It must be reapplied any
time `.venv/` is rebuilt, since the vendored package itself is not committed.

## Milestone commands

```shell
.venv/bin/skillevaluator --version
.venv/bin/skillevaluator doctor --agents codex --env-mode docker
.venv/bin/skillevaluator validate skills/portfolio-overview --no-dedup \
  -r json,markdown,html -o reports/m1/tier1
.venv/bin/skillevaluator tier3 validate skills/portfolio-overview --json
.venv/bin/skillevaluator tier3 evaluate skills/portfolio-overview \
  --agents codex --env-mode docker --n-attempts 1
.venv/bin/skillevaluator tier3 evaluate skills/m1-tier3-smoke \
  --agents codex --env-mode docker --n-attempts 1 --n-concurrent 1 \
  --harbor-keep-jobs --results-dir reports/m1/tier3-smoke
```

The evaluator adapter uses these same command forms and keeps the provider
executable configurable through `PM_AI_SKILLEVALUATOR_BIN` for tests and CI.

The tool-free smoke skill exists only to verify Milestone 1 infrastructure. It
does not replace the portfolio behavior evaluation; that evaluation depends on
the synthetic Agentic Data Pipeline planned for Milestone 3.
