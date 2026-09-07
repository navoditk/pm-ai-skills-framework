# Module 1: What SkillEvaluator Is, and Why

Teach these points one at a time, grounded in
`docs/15_SKILLS_AND_SKILLEVALUATOR_REFERENCE.md` §1.

## The core idea

NVIDIA SkillEvaluator is an open-source, multi-tier framework for evaluating
AI agent artifacts — starting with agent skills — through deterministic
quality gates, semantic overlap detection, synthetic evaluation-dataset
generation, and live agent evaluation that measures how a skill actually
changes agent behavior.

Sources: [NVIDIA docs](https://docs.nvidia.com/skills/skillevaluator),
[GitHub](https://github.com/NVIDIA/SkillEvaluator),
[NVIDIA technical blog](https://developer.nvidia.com/blog/evaluating-ai-agent-skill-performance-with-nvidia-skillevaluator/).

## Support level

**Experimental** — community-supported on a best-effort basis through GitHub
Issues, no SLA. This matters: this repository found and worked around real
bugs in it (see Module 8) — exactly what "Experimental" should lead you to
expect.

## The four tiers, one line each

| Tier | Question it answers | Cost |
|---|---|---|
| Tier 1 | Is the skill well-formed and safe? | Free, offline, seconds |
| Tier 2 | Is it a near-duplicate of something that already exists? | Needs an embedding provider |
| Tier 3 | Does having the skill change agent behavior for the better, and by how much ("Skill Lift")? | Needs Docker, agent + judge credentials, real time/money |
| Tier 4 | Is the agent's answer, with the skill, actually *correct* for this domain? | Bring-your-own grader; SkillEvaluator supplies the harness, not domain judgment |

## What it explicitly does NOT do

It does not build skills for you, does not run your production agent, does
not manage credentials or a data pipeline, and does not by itself decide
certification policy — that is what this repository's own
`framework/certification/engine.py` and `policies/certification.yaml` add on
top. See `docs/02_TARGET_ARCHITECTURE.md`.

## Quiz (5+ questions, use ask_user with 4 choices each)

Ask about: which tier answers which question, the support level, what it
does NOT do, and the free-vs-costly split across tiers.
