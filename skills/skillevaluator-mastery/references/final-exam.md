# Final Exam

Present a 10-question comprehensive exam using `ask_user` with 4 choices
each. Require 80%+ to pass. Vary the selection each time.

## Question Bank

1. What does "Skill Lift" measure? → With-skill score minus without-skill
   score (Tier 3).
2. Which tier is free and offline by default? → Tier 1.
3. Why does Tier 2 need an OpenAI (or compatible) key even for an
   all-Claude Tier 3 run? → Anthropic does not provide an embedding
   provider.
4. What does Tier 4 NOT supply? → Domain-specific correctness judgment —
   only the harness/trajectory to grade.
5. What env var sets a separate judge model? → `SKILL_EVAL_JUDGE_MODEL`.
6. What CLI flag is easy to forget and leaves the sandbox unable to find
   the repo's own tool bridge? → `--copy-repo`.
7. Why should you pin an exact SkillEvaluator commit rather than install
   `@main`? → Real, breaking behavioral differences have occurred between
   versions.
8. What silently happens if Tier 2's embedding provider is missing? →
   It reports "skipped" rather than erroring.
9. What does this repository's `framework/adapters/nvidia_skillevaluator.py`
   do? → Normalizes raw NVIDIA report JSON into a stable internal schema so
   downstream logic never parses vendor-specific fields directly.
10. What SkillEvaluator support level should you expect? → Experimental —
    community-supported, no SLA.
11. What field in `SKILL.md` frontmatter is required for the
    `author_format` check? → `metadata: author: ...`.
12. In this repository's real CI, which job blocks a PR outright vs. stays
    advisory? → `tier1` (and `similarity` on `EXACT_DUPLICATE`) block;
    `tier3-fast`/`domain-graders` are advisory placeholders.
13. Approximately how much did a full 150-trial Tier 3 matrix cost per
    skill in this repository's own runs? → Roughly $15-45 and 30-55 minutes.
14. What real bug did this repository patch locally in the pinned
    evaluator? → A judge token-truncation bug (`max_tokens=1024`, no retry).
15. Why is a Haiku-tier "quick pass" not certification evidence? → A weaker
    agent compresses Skill Lift toward zero on both arms, not because the
    skill itself is worse.

On pass (80%+): Award "SkillEvaluator Architect" title, congratulate
enthusiastically!
On fail: Show which they got wrong, encourage retry, point back to the
relevant module.
