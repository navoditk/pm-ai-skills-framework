# Module 3: Tier 2 — Semantic Similarity / Deduplication

Teach these points one at a time, grounded in
`docs/15_SKILLS_AND_SKILLEVALUATOR_REFERENCE.md` §3, §6.

## What it does

Embeds a candidate skill's description/content and compares it against a
central catalog to catch near-duplicate skills before merge (e.g. two teams
independently building "explain portfolio performance" under different
names).

## The gotcha: embedding provider

Tier 2 needs a working embedding provider, and **Anthropic does not provide
one**. You need `SKILL_EVAL_EMBEDDING_PROVIDER=openai` (or `nv_build` / an
OpenAI-compatible endpoint) plus that provider's key — even if Tier 3's agent
is entirely Claude-based. If this is missing, Tier 2 **silently reports
"skipped" rather than erroring** — a real trap this project actually hit.

## Command

```bash
SKILL_EVAL_EMBEDDING_PROVIDER=openai OPENAI_API_KEY=... \
  skillevaluator similarity-check skills/ --type skill
```

## This repository's governance layer on top

Tier 2 alone gives a similarity score. This repository's own
`framework/certification/check_similarity.py` and `policies/similarity.yaml`
turn that score into governance *actions* — e.g. `EXACT_DUPLICATE` blocks a
PR, `HIGH_SIMILARITY` routes to an advisory `architecture_review` with an
assigned owner/SLA, rather than blocking outright. This is this repository's
own addition, not a SkillEvaluator feature.

## Quiz (5+ questions, use ask_user with 4 choices each)

Ask about: the embedding-provider requirement, the silent-skip failure mode,
the required env vars, and the distinction between Tier 2's raw score and
this repo's governance actions on top of it.
