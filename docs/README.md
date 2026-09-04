# Documentation map

This page is the reader-oriented entry point for the PM AI Skills Quality &
Certification Framework. The numbered documents provide a deliberate sequence;
use the routes below to find the shortest path for your goal.

## Pick your path

### New to the repository or SkillEvaluator

1. [First tutorial](00_TUTORIAL.md)
2. [Executive summary and walkthrough](14_EXECUTIVE_SUMMARY_AND_WALKTHROUGH.md)
3. [Skills and SkillEvaluator reference](15_SKILLS_AND_SKILLEVALUATOR_REFERENCE.md)

### Understanding the design

1. [Proposal](01_PROPOSAL.md)
2. [Target architecture](02_TARGET_ARCHITECTURE.md)
3. [Skill standard](03_SKILL_STANDARD.md)
4. [Evaluation and certification](04_EVALUATION_AND_CERTIFICATION.md)
5. [Implementation plan](05_IMPLEMENTATION_PLAN.md)

### Authoring, evaluating, or certifying a skill

1. [Skill standard](03_SKILL_STANDARD.md)
2. [End-to-end skill workflow](12_END_TO_END_SKILL_WORKFLOW.md)
3. [Evaluation and certification](04_EVALUATION_AND_CERTIFICATION.md)
4. [NVIDIA evaluator upgrade policy](13_NVIDIA_EVALUATOR_UPGRADE_POLICY.md)

### Adopting the framework in another repository

1. [Quickstart for consumers](11_QUICKSTART_FOR_CONSUMERS.md)
2. [Adoption guide](06_ADOPTION_GUIDE.md)
3. [GitHub publishing](07_GITHUB_PUBLISHING.md)

### Reviewing evidence, status, and limitations

1. [Executive summary and walkthrough](14_EXECUTIVE_SUMMARY_AND_WALKTHROUGH.md)
2. [Development roadmap and progress](10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md)
3. [Evidence index](EVIDENCE_INDEX.md)
4. [Demo and acceptance plan](08_DEMO_AND_ACCEPTANCE_PLAN.md)

## Documentation roles

| Document group | Purpose |
|---|---|
| `00_TUTORIAL.md` | First local run without provider credentials |
| `01` through `05` | Canonical purpose, architecture, standards, evaluation model, and implementation plan |
| `06` through `08` | Adoption, publishing, and acceptance |
| `09` and `15` | External reading and SkillEvaluator-specific reference |
| `10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md` | Canonical current status, scope decisions, blockers, and next work |
| `11` through `13` | Consumer workflow, operational workflow, and evaluator-version policy |
| `14_EXECUTIVE_SUMMARY_AND_WALKTHROUGH.md` | Standalone explanation of verified outcomes, tradeoffs, and limitations |
| `MILESTONE_*.md` | Detailed historical implementation and experiment records |
| `EVIDENCE_INDEX.md` | Tracked benchmark evidence and explicit caveats |

## Reading rules

- The root [README](../README.md) is the project narrative and high-level
  reference, not a replacement for the numbered implementation documents.
- Read `10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md` for the current state rather
  than inferring status from older milestone records.
- Read `EVIDENCE_INDEX.md` before interpreting benchmark results as a
  certification decision.
- Milestone documents retain useful detail, but support rather than supersede
  the roadmap and evidence index.

## Related repository material

- [Reference skills](../skills/)
- [Framework implementation](../framework/)
- [Deterministic PM graders](../graders/)
- [Synthetic data pipeline](../synthetic_data_pipeline/)
- [Policies](../policies/)
- [Local reports](../reports/)
- [Contributing](../CONTRIBUTING.md)
