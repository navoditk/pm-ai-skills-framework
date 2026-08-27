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
- Discoverability;
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
