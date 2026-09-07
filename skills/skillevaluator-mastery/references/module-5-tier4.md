# Module 5: Tier 4 — Domain Graders

Teach these points one at a time, grounded in
`docs/15_SKILLS_AND_SKILLEVALUATOR_REFERENCE.md` §7 and Milestone 8
(`docs/10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md`).

## What Tier 4 is

SkillEvaluator supplies the harness (a Tier 3 trajectory to grade against),
not the domain judgment. You write `evals/grader.py` per skill; real domain
logic should live in a shared, reusable module, not duplicated per skill.

## This repository's pattern

```python
from graders.finance.my_skill import grade as grade_evidence

def grade(case, trajectory=None, expected=None):
    evidence = trajectory or expected or {}
    result = grade_evidence(evidence)
    return {"skill": "my-skill", "metrics": result["metrics"],
            "score": result["score"], "notes": []}
```

Composed from generic building blocks in `graders/finance/*.py`, reused
across all 12+ PM skills — reusability across skills was made an explicit
exit criterion in Milestone 8.

## A free, post-hoc extraction pipeline

This repository built `skills/*/evals/{tier3_trial_extractor,aggregate_tier4,
generate_benchmark}.py` — a pipeline that mines **already-completed** Tier 3
trial data on disk to compute domain-specific correctness metrics and hard
gates (e.g. regression pass rate, authorization/permission-denial scanning)
**without any new API calls**, because Tier 4 itself is bring-your-own-grader
and SkillEvaluator doesn't do this for you.

## A real observed quirk to defend against

Directory layouts can differ between runs of the same tool — this project
observed two different completed-trial directory structures across
otherwise-identical `skillevaluator validate --agent-eval` invocations. Any
custom post-hoc analysis script needs to defend against that, not assume a
fixed layout.

## Quiz (5+ questions, use ask_user with 4 choices each)

Ask about: what Tier 4 does NOT supply, the shared-grader pattern, the
free extraction-pipeline idea, and the directory-layout quirk.
