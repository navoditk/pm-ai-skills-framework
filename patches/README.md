# Local evaluator patches

Tracked, minimal patches against the pinned NVIDIA SkillEvaluator install,
applied on top of `.venv/` (which is gitignored — the vendored package itself
is never committed, only the diff). Governed by
[`docs/13_NVIDIA_EVALUATOR_UPGRADE_POLICY.md`](../docs/13_NVIDIA_EVALUATOR_UPGRADE_POLICY.md);
each patch here should have a matching row in that document's compatibility
log, and should be re-evaluated (likely dropped) on the next evaluator
version bump if the fix has landed upstream.

## skillevaluator-0.2.1-judge-max-tokens.patch

**Target:** `skillevaluator/tier3/harbor/templates/eval.py`, pinned version
`0.2.1` (commit `009aa300be7925c7ba75760592baeb941cc29ba8`).

**What it fixes:** `judge_accuracy` and `_judge_goal_accuracy_custom` called
the judge LLM with the library's default `max_tokens=1024` and no retry. For
a substantive answer (e.g. a financial-attribution explanation), the judge's
5-criterion reasoning routinely exceeds 1024 tokens before it reaches the
closing JSON brace, so the response gets cut off and is rejected as invalid
JSON — observed live as `"Judge response was not a valid JSON object"` on
roughly a quarter of judge calls during Milestone 4's Performance Attribution
Tier 3 runs, occasionally consuming all 3 attempts for a given case. The
evaluator's own source already fixed this exact failure mode for
`judge_behavior_check` (see the `BEHAVIOR_JUDGE_MAX_TOKENS = 4096` comment in
the same file); this patch applies the same fix (bigger token budget + one
retry) to the two judges that never received it.

**Apply after installing the pinned SkillEvaluator version:**

```bash
patch -p1 -d .venv/lib/python3.13/site-packages < patches/skillevaluator-0.2.1-judge-max-tokens.patch
```

**Status:** local workaround pending an upstream fix. Do not treat this as
permanent — re-check on every SkillEvaluator version bump per
`docs/13_NVIDIA_EVALUATOR_UPGRADE_POLICY.md`, and drop it once the equivalent
fix ships upstream.
