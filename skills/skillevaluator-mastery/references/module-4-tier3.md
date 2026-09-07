# Module 4: Tier 3 — Live-Agent Evaluation & Skill Lift

Teach these points one at a time, grounded in
`docs/15_SKILLS_AND_SKILLEVALUATOR_REFERENCE.md` §2-4 and
`docs/MILESTONE_4_PERFORMANCE_ATTRIBUTION.md`.

## The core mechanic

Run the same eval cases twice — once with the skill loaded, once without —
against a live agent and a live judge model, in a sandbox (Docker/Harbor).
**Skill Lift** = with-skill score minus without-skill score. This is the
central number Tier 3 produces.

## Real numbers from this repository

| Skill | Trials | Skill Lift |
|---|---|---|
| Performance Attribution | 150 (75/75 both arms) | +0.1253 |
| Portfolio Overview | 150 (75/75 both arms) | +0.1316 |

A full 25-case × 3-attempt × 2-arm matrix against `claude-sonnet-5` as both
agent and judge took **30-55 minutes and roughly $15-45** per skill. A
cheap Haiku-tier "quick pass" ran in ~12 minutes for ~$1-3 — useful for
validating wiring, **not** a substitute for certification-grade evidence
(a weaker agent compresses Skill Lift toward zero on both arms).

## Requirements easy to forget

- Docker (or another sandbox), the agent's own credentials.
- A **separate** judge-model credential and `SKILL_EVAL_JUDGE_MODEL`
  override — otherwise the judge silently falls back to the agent's own
  model, coupling judge cost to agent cost for no reason.
- `--copy-repo` — without it, the sandbox can't find the repo's own tool
  bridge (a real operator-error bug this project hit).

## Command shape

```bash
SKILL_EVAL_LLM_PROVIDER=anthropic ANTHROPIC_API_KEY=... \
SKILL_EVAL_JUDGE_MODEL=claude-sonnet-5 \
  skillevaluator validate skills/my-skill \
  --agent-eval -a claude-code --agent-model claude-code=claude-sonnet-5 \
  --env-mode docker --copy-repo \
  --results-dir reports/my-skill-tier3 -r cli,json,markdown
```

## Metrics beyond Skill Lift

`pass_at_k` (reliability across repeated attempts) and per-dimension
`dimensions_with_skill` scores (e.g. discoverability, tool-use correctness)
also appear in the raw report — see Module 8 for the report shape.

## Quiz (5+ questions, use ask_user with 4 choices each)

Ask about: the definition of Skill Lift, real cost/time figures from this
repo, the three easy-to-forget requirements, and why a Haiku quick-pass
isn't certification evidence.
