# 8. Demonstration & Acceptance Plan

## 8.1 Demonstrate good skills and deliberately bad skills

The POC should include controlled defects.

### Defect A — discoverability failure
Make `risk-explanation` description vague.

Expected:
- Tier 1 may pass;
- Tier 3 discoverability falls;
- report recommends description refinement.

### Defect B — deterministic financial failure
Remove derivative exposure handling.

Expected:
- generic narrative may appear reasonable;
- PM reconciliation/coverage grader fails.

### Defect C — duplicate skill
Create `portfolio-risk-review` with highly similar description.

Expected:
- Tier 2 similarity blocks or requires review.

### Defect D — temporal inconsistency
Use portfolio snapshot T and benchmark snapshot T-1.

Expected:
- TemporalConsistencyGrader fails.

### Defect E — unnecessary skill
Create a skill that barely improves the base agent.

Expected:
- high absolute quality may coexist with low Skill Lift;
- certification policy can flag low incremental value.

## 8.2 Framework evaluation matrix

| Defect | Tier 1 | Tier 2 | Tier 3 | PM Tier 4 |
|---|---:|---:|---:|---:|
| Bad structure | expected | | | |
| Duplicate capability | | expected | | |
| Bad routing metadata | | | expected | |
| Wrong finance math | | | maybe | expected |
| Wrong date | | | maybe | expected |
| Prompt injection | expected/possible | | expected | policy |
| No incremental benefit | | | expected | |

## 8.3 Acceptance metrics

Reference implementation:
- 12 skills;
- >=120 starter eval cases;
- >=6 finance graders;
- normalized JSON report;
- readable Markdown report;
- BENCHMARK generation path;
- CI examples;
- Tier 2 local catalog;
- Skill Lift in certification;
- deliberate defect test suite;
- second-repo portability demo.

## 8.4 Executive demonstration

Recommended 15-minute flow:

1. Show the skill library.
2. Add a near-duplicate skill -> similarity finding.
3. Modify a good skill to introduce a date defect.
4. Run fast evaluation -> domain failure.
5. Show with-skill vs without-skill lift.
6. Show normalized certification report.
7. Restore/fix skill and rerun.
8. Show benchmark evidence.
9. Show a second repo consuming the same framework.

This demonstrates quality, governance, incremental value, remediation, and portability in one narrative.
