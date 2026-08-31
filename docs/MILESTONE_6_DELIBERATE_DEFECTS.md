# Milestone 6 — Deliberate Defect Demonstration

Status: `DONE`

Per the [2026-08-30 scope decision](10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md#scope-decision-2026-08-30),
this milestone runs entirely on Tier 1 static checks, Tier 2 similarity
checks, and the Milestone 8 grader unit tests — no live-agent (Tier 3)
spend, since the goal is demonstrating *how the evaluator catches defects*,
not measuring a live agent's behavior again. Every defect variant below is
a synthetic, deliberately broken copy of a real skill, built in the session
scratchpad and never merged into `skills/`.

## Summary

| # | Defect | Method | Result |
| - | ------ | ------ | ------ |
| 1 | Vague skill description | Tier 1 `quality-check` | **Caught** — new finding, discoverability 85→80 |
| 2 | Duplicate risk skill | Tier 2 `similarity-check` | **Caught** — HIGH_SIMILARITY, score 0.9468, would block merge |
| 3 | Missing derivatives | `portfolio_coverage` grader unit test | **Caught** — existing test, confirmed passing |
| 4 | Mismatched dates | `temporal_consistency` grader unit test | **Caught** — existing test, confirmed passing |
| 5 | Weak/no-value skill | Tier 1 `quality-check` (proxy only) | **Caught, accepted 2026-08-31** — quality dropped 87.2→79.5; see caveat below: this is a proxy, not a live Skill Lift measurement, and was accepted as sufficient rather than confirmed live |
| 6 | Unauthorized data source | `data_provenance` grader unit test | **Caught** — existing test, confirmed passing |

## 1. Vague skill description → discoverability degradation

**Variant:** copy of `skills/portfolio-overview`, description replaced with
`"Helps with portfolio stuff."` and the `## Use when` / `## Do not use when`
trigger sections deleted, keeping everything else (procedure, domain rules,
output format) unchanged.

**Command:**
```
.venv/bin/skillevaluator quality-check <variant> -r cli
```

**Result:**

| | Baseline (real skill) | Vague variant |
| --- | ---: | ---: |
| Overall | 87.2 (B) | 86.0 (B) |
| Discoverability | 85 | 80 |

A new finding fired on the variant that did not fire on the baseline:
`[QUALITY-MEDIUM] Description contains vague words` (check:
`quality_discoverability`, fix: "Be specific about what this skill does").

**Honest caveat:** the numeric movement is real but modest (5 points on one
sub-dimension). Tier 1's discoverability check is a keyword/structure
heuristic — it does not simulate an agent actually choosing between skills.
The certification-grade signal for discoverability is Tier 3's
`skill_execution` metric (a live measurement of whether the agent picks the
right tool/skill for the task), which is what Milestone 4 and Milestone 5
actually gate on. This Tier 1 result shows the static proxy moves in the
right direction, not that it fully substitutes for the live metric.

## 2. Duplicate risk skill → Tier 2 detection

**Variant:** copy of `skills/risk-explanation`, renamed to `risk-review` in
`SKILL.md` and `skill.yaml`, content otherwise byte-identical.

**Command run** (needs `SKILL_EVAL_EMBEDDING_PROVIDER=openai` +
`OPENAI_API_KEY` — a live but much smaller-cost API call than the Sonnet
agent/judge spend used elsewhere; embedding calls price in fractions of a
cent, not per-agent-turn):
```
.venv/bin/skillevaluator similarity-check <dir-containing-both-skills> \
  --type skill -r cli,json -o /tmp/m6-dedup-check
```

**Result (2026-08-30, real):**

```
[SIMILARITY-HIGH] 'risk-explanation' and 'risk-review' are HIGH_SIMILARITY
(score: 0.9468) in risk-explanation
overall_passed: false
```

Caught cleanly — `0.9468` clears the `0.75` similarity threshold in
`policies/similarity.yaml` by a wide margin, and `overall_passed: false`
means this would block a merge under the blocking-Tier-2-gate policy
already documented in this project's "Suggested next three PRs" (PR 1).
The classification landed as `HIGH_SIMILARITY` rather than
`EXACT_DUPLICATE` because the two `SKILL.md` files differ by their `name:`
field (`risk-explanation` vs `risk-review`) — an exact byte-for-byte copy
with no changes at all would likely score even higher and classify as
`EXACT_DUPLICATE`.

## 3. Missing derivatives → portfolio coverage failure

Already demonstrated by
`test_portfolio_overview_domain_grader_detects_missing_derivative_coverage`
in `tests/test_graders.py` — `expected_position_ids` includes a derivative
(`ES_FUT`) that `observed_position_ids` omits; the composite grader scores
`portfolio_coverage < 1.0` and `passed is False`. Re-confirmed passing on
2026-08-30.

## 4. Mismatched dates → temporal failure

Already demonstrated by `test_temporal_detects_mismatch` in
`tests/test_graders.py` — a requested as-of date of `2026-08-25` against
observed dates `["2026-08-25", "2026-08-22"]` scores `0.0`. Re-confirmed
passing on 2026-08-30.

## 5. Weak/no-value skill → low Skill Lift

**Variant:** a minimal skill (`weak-portfolio-helper`) with no procedure,
no domain rules, no grounding requirement, and no instruction to use the
Agentic Data Pipeline tools at all — just "answer the user's portfolio
question as best you can using your own knowledge and judgment."

**Result (Tier 1 proxy only):**

| | Baseline (real skill) | Weak variant |
| --- | ---: | ---: |
| Overall | 87.2 (B) | 79.5 (C) |
| Correctness | 85 | 70 |
| Reliability | 85 | 75 |

**This is not a Skill Lift measurement.** Skill Lift is defined as
`with-skill score − without-skill (baseline) score` from a live Tier 3
matrix (see `docs/04_EVALUATION_AND_CERTIFICATION.md`) — it requires
actually running an agent with and without the weak skill attached and
comparing real task performance. A Tier 1 quality score is a static proxy
for "is this skill well-specified," not a measurement of whether it changes
agent behavior. The two can diverge: a skill can read well but add no real
lift (this happened for real on Performance Attribution's
`skill_execution` dimension, where lift was only +0.0009 despite an overall
lift of +0.1253 — see `docs/MILESTONE_4_PERFORMANCE_ATTRIBUTION.md`).

**Also worth flagging:** 79.5 still clears Tier 1 validate's default
`--min-score 70` gate. A weak/no-value skill would pass Tier 1 on its own —
it takes the live Tier 3 Skill Lift measurement to actually catch it. This
is a real argument for why the certification pipeline keeps Tier 3 rather
than relying on Tier 1 quality scoring alone.

**Decision (2026-08-31):** a human reviewer chose to close this defect on
the Tier 1 proxy evidence above rather than spend the ~$1-3 / ~10-12 minute
live A/B run that would confirm it with a real Skill Lift number. The
quality-score drop (87.2→79.5, driven by concrete Correctness and
Reliability findings, not a vague heuristic) is accepted as sufficient
evidence that the framework catches a structurally weak skill — with the
explicit caveat, documented above, that Tier 1 alone would not have blocked
this skill under Tier 1's own default `--min-score 70` gate. This is a
known gap in this specific piece of evidence, not a claim that Tier 1 and
Tier 3 are interchangeable in general — Milestones 4 and 5 both required a
real live Tier 3 matrix precisely because a Tier 1 proxy is not equivalent
to a live measurement.

## 6. Unauthorized data source → provenance failure

Already demonstrated by
`test_risk_explanation_domain_grader_detects_unauthorized_source` in
`tests/test_graders.py` — `observed_sources` includes `web_search` outside
`allowed_sources`; the composite grader scores `data_provenance == 0.0` and
`passed is False`. Re-confirmed passing on 2026-08-30.

## Exit criteria status

- framework catches all deliberately introduced defects: **5 of 6 caught
  directly** (vague description, duplicate skill, missing derivatives,
  mismatched dates, unauthorized source); **1 caught via a Tier 1 proxy,
  accepted 2026-08-31 rather than confirmed with a live Skill Lift
  measurement** (weak/no-value skill — see the decision note above). MET.
- reports clearly explain failure mode: yes for all six — each finding
  above names the specific check, the metric it moved, and why. MET.

## Status

`DONE` — closed 2026-08-31 on the evidence above. The one item that stayed
a proxy rather than a live measurement (weak/no-value skill's Skill Lift)
is documented as an accepted limitation, not a gap silently dropped.
