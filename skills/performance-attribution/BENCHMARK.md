# PM AI Skill Certification Report

**Skill:** Performance Attribution
**Version:** 0.1.0
**Certification:** FAIL

## Generic Metrics
- **security:** 1.0
- **correctness:** 0.992
- **discoverability:** 0.8862
- **effectiveness:** 0.9342
- **efficiency:** 0.8704

## Incremental Value
- **Skill Lift:** +0.1253 (with-skill 0.9362, baseline 0.8109)
- **pass@3:** 0.92 (23/25 cases)

## Domain Metrics
- **financial_accuracy:** 1.0
- **reconciliation:** 1.0
- **benchmark_consistency:** 1.0
- **temporal_consistency:** 1.0
- **data_provenance:** 1.0
- **portfolio_coverage:** 1.0
- **numeric_claim_grounding:** 1.0
- **regression_pass_rate:** 1.0

## Certification Gate Failures
- discoverability: 0.8862 < 0.9

## Findings
- Discoverability (skill_execution) averages 0.8862 across all 75 with-skill trials, narrowly missing the 0.90 floor. This is fully explained by 2 of 25 cases (performance--007, performance--020, the 'ambiguous' category) which explicitly instruct the agent to use no tools and ask a clarifying question instead -- correct behavior per their own assertions, but structurally unable to score above 0 on a generic 'was the skill activated via a tool call' metric. Excluding just those 2 cases (6 of 75 trials), discoverability averages 0.9632, comfortably above the floor. This is a metric-scoping limitation for tool-free ambiguous-case testing, not an observed skill discoverability defect.
- Tier 4 domain grading covered 41 of 42 expected trials across 14 gradable cases (performance--001, performance--002, performance--003, performance--008, performance--010, performance--011, performance--012, performance--013, performance--014, performance--015, performance--016, performance--019, performance--024, performance--025); 1 trial(s) skipped as genuinely not gradable (see aggregate_tier4.py output for reasons), not counted as failures. All gradable trials scored a clean 1.0 across all six deterministic checks.
- Authorization checked all 150 trials across both arms (not just the gradable subset): zero permission denials found.
- Regression cases (performance--010, performance--024, performance--025): 3/3 passed all attempts. This measures the numeric/reconciliation dimension of these cases specifically; it does not yet verify narrative-disclosure assertions some regression cases also carry.
