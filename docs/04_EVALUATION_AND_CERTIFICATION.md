# 4. Evaluation, Scoring & Certification

## 4.1 Four-tier model

### Tier 1 — Generic quality/security
NVIDIA SkillEvaluator plus PM manifest checks.

### Tier 2 — Catalog hygiene
NVIDIA intra-skill context optimization and inter-skill similarity.

Suggested governance:
- EXACT_DUPLICATE: block.
- HIGH_SIMILARITY: block pending architecture review.
- SIMILAR: advisory + justification.
- LOOSELY_RELATED: informational.

### Tier 3 — Live behavior
Retain the baseline arm for certification:
- agent with skill;
- same agent without skill.

Measure:
- Security;
- Correctness;
- Discoverability, only across cases where skill activation is applicable;
- Effectiveness;
- Efficiency;
- Skill Lift;
- pass@k.

### Tier 4 — Asset-management domain grading
Run deterministic graders wherever authoritative truth exists.

## 4.2 Starter scorecard

```text
GENERIC
Security
Correctness
Discoverability
Effectiveness
Efficiency

INCREMENTAL VALUE
Skill Lift
pass@1
pass@3

DOMAIN
Financial Accuracy
Reconciliation
Temporal Consistency
Benchmark Consistency
Data Provenance
Portfolio Coverage
Authorization Compliance
Numeric Grounding
```

## 4.2a Risk-tiered certification rigor

**Implemented 2026-09-01**: `policies/certification.yaml` carries one profile
per risk level (`informational-standard`, `low-standard`,
`analytical-standard`, `decision-support-standard`, `action-standard`) plus
a `risk_level_profiles` mapping, resolved by
`framework/certification/profile_resolver.py` from a skill's own
`classification.risk_level` rather than every caller hardcoding
`analytical-standard`. Both flagship skills'
`evals/generate_benchmark.py` scripts now go through the resolver;
regenerating their `BENCHMARK.json` against already-collected trial data
(no new API cost) produced byte-identical certification verdicts, since both
are `risk_level: analytical` -- the resolver is a pure refactor for them,
not a behavior change. `decision-support-standard` and `action-standard`
promote the Tier 4 finance-grader metrics from a weighted `minimum_metric`
into a `hard_gate`, matching the "required, hard gate" cells in the table
below; `action-standard` additionally hard-gates on a
`human_review_required` metric that no automated collector in this repo
produces, so an `action`-risk skill cannot self-certify from Tier 1-4
evidence alone by design -- a human must record that outcome first. No
skill in this repo currently carries `risk_level: decision-support` or
`action`; all 12 real reference skills are `analytical`. See
`tests/test_certification_profiles.py` for the resolver's test coverage.

Not every skill should cost the same to certify. Certification rigor scales
with the `classification.risk_level` value already required in
`skill.yaml` / `framework/schemas/skill.schema.json`
(`informational`, `low`, `analytical`, `decision-support`, `action`):

| risk_level | Tier 1 / Tier 2 | Tier 3 | Tier 4 finance graders |
|---|---|---|---|
| informational | required, blocking | 1 attempt, reduced case set | optional |
| low | required, blocking | 1 attempt, full case set | recommended |
| analytical | required, blocking | 1-3 attempts, full case set | required |
| decision-support | required, blocking | 3 attempts, full case set | required, hard gate |
| action | required, blocking | 3+ attempts, full case set, trajectory reviewed by a human | required, hard gate |

Tier 1 and Tier 2 stay blocking at every risk level — construction/security
quality and catalog deduplication are cheap to run and their value does not
scale with a skill's downstream risk. What scales is Tier 3 attempt count and
case coverage, and whether Tier 4 finance grading is a hard gate or merely
recommended.

This is also a cost-control mechanism: a growing skill library cannot afford
to run the most expensive Tier 3 matrix (multiple attempts, full case set,
live-agent sandbox) against every new skill by default. Most new PM skills
(a summary or commentary skill, for example) belong at `informational` or
`low` and should never trigger the same evaluation cost as
`performance-attribution`.

## 4.2b Deduplication as the first-line governance mechanism

Before any Tier 3/4 cost is spent, Tier 2 similarity against the central
approved-skill catalog (`catalogs/skill-catalog.json`) is the cheapest and
highest-leverage control against the duplication problem this framework
exists to solve (`docs/01_PROPOSAL.md` §1.1). `EXACT_DUPLICATE` and
`HIGH_SIMILARITY` findings should block merge before a candidate skill
consumes any live-agent evaluation budget at all — catching a near-duplicate
at PR time is far cheaper than discovering it after both skills reach
production.

## 4.3 Hard gates versus weighted metrics

Hard gates:
- security pass;
- authorization pass;
- data provenance threshold;
- regression suite threshold;
- required ownership metadata.

Weighted metrics can produce a composite score but may never override a hard-gate failure.

## 4.4 Example certification policy

See `policies/certification.yaml`.

## 4.5 Eval categories

Each skill should have:
- explicit positive;
- implicit positive;
- contextual positive;
- negative;
- missing-data;
- stale-data;
- ambiguous-input;
- tool-failure;
- adversarial;
- regression.

**Discoverability eligibility policy.** A case that explicitly requires the
agent to ask a clarifying question and use no tools tests safe ambiguity
handling, not skill activation. Such `ambiguous` cases are excluded from the
discoverability denominator and remain subject to correctness and applicable
domain checks. Certification consumes the case-filtered
`discoverability_eligible` metric, while the provider-wide raw
`discoverability` score remains diagnostic evidence. The policy is implemented
by `framework/certification/metric_eligibility.py` and enforced by
`policies/certification.yaml`; `tests/test_certification_profiles.py` covers
both the exclusion and the certification decision.

## 4.6 Skill Lift

Skill Lift answers:
> Does the skill earn its place in the catalog?

A high absolute score with negligible lift may indicate the base agent already performs the capability adequately.

Do not skip the baseline in certification runs.

## 4.7 pass@k

Use repeated attempts for nondeterministic behavior.

For higher-risk skills track:
- pass@1;
- pass@3 or higher;
- variance across attempts.

## 4.8 Finance grader priority

Deterministic truth has precedence:

```text
official analytical output
> deterministic calculation
> authoritative reference data
> expert rubric
> LLM judge
```

## 4.9 Remediation report

Every failed certification should answer:
- what failed;
- how often;
- which cases;
- likely common root cause;
- suggested instruction/tool-contract change;
- recommended new regression cases;
- expected metrics affected.

## 4.10 Benchmark evidence

Generate `BENCHMARK.md` plus machine-readable JSON.

Never hand-edit benchmark evidence.

A benchmark should record:
- skill version;
- agent/model;
- dataset fingerprint;
- evaluator version;
- grader versions;
- run timestamp;
- environment;
- metrics;
- final certification verdict.
