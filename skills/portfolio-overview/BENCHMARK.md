# PM AI Skill Certification Report

**Skill:** Portfolio Overview
**Version:** 0.1.0
**Certification:** FAIL

## Generic Metrics
- **security:** 1.0
- **correctness:** 0.976
- **discoverability:** 0.8942
- **effectiveness:** 0.9653
- **efficiency:** 0.858

## Incremental Value
- **Skill Lift:** +0.1316 (with-skill 0.9432, baseline 0.8115)
- **pass@3:** 0.92 (23/25 cases)

## Domain Metrics
- **financial_accuracy:** 1.0
- **benchmark_consistency:** 1.0
- **temporal_consistency:** 1.0
- **data_provenance:** 1.0
- **portfolio_coverage:** 1.0
- **numeric_claim_grounding:** 1.0
- **regression_pass_rate:** 1.0

## Certification Gate Failures
- discoverability: 0.8942 < 0.9
- reconciliation: None < 0.99

## Findings
- Discoverability (skill_execution) averages 0.8942 across all 75 with-skill trials, narrowly missing the 0.90 floor -- the same single gate, and a very similar shortfall, as Performance Attribution's real certification result (0.8862 there vs 0.8942 here). This recurring pattern across two independently built skills is itself evidence: NVIDIA's own Tier 3 report for this run independently recommends 'Add copies of portfolio-ov-001 and portfolio-ov-025 without the forced cat SKILL.md preamble to measure genuine discoverability' -- corroborating the Milestone 4 diagnosis that this is a metric-scoping artifact from the pre_agent_setup bootstrap script forcing a SKILL.md read, not an observed skill discoverability defect.
- Tier 4 domain grading covered 45 of 45 expected trials across 15 gradable cases (portfolio-ov-001, portfolio-ov-002, portfolio-ov-003, portfolio-ov-004, portfolio-ov-012, portfolio-ov-013, portfolio-ov-016, portfolio-ov-017, portfolio-ov-018, portfolio-ov-019, portfolio-ov-020, portfolio-ov-021, portfolio-ov-022, portfolio-ov-023, portfolio-ov-025); 0 trial(s) skipped as genuinely not gradable (see aggregate_tier4.py output for reasons), not counted as failures. All gradable trials scored a clean 1.0 across all five deterministic checks.
- Authorization checked all 150 trials across both arms (not just the gradable subset): zero permission denials found.
- Regression cases (portfolio-ov-016, portfolio-ov-017, portfolio-ov-018, portfolio-ov-025): 4/4 passed all attempts.
- The analytical-standard profile's 'reconciliation: 0.99' minimum metric structurally cannot be met by this skill: reconciliation checks return-component math specific to Performance Attribution's attribution_reconciliation grader, and Portfolio Overview has no return-component reconciliation to check (see graders/finance/portfolio_overview.py's module docstring, which already documents this omission). framework/certification/engine.py treats any minimum_metric absent from a skill's metrics dict as an automatic failure, so every non-attribution skill certified against analytical-standard will show this same failure regardless of actual quality. This is a policy-profile design gap, not a Portfolio Overview defect -- left open for a human reviewer to decide whether analytical-standard should drop 'reconciliation' as a universal minimum metric, or whether a narrower profile should exist for skills without a reconciliation grader.
