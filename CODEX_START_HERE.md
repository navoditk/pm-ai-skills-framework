# PM AI Skills Framework — Codex Start Here

Use this file as the entry point when beginning implementation with Codex CLI.

## First read

Before changing code, read these files in order:

1. `README.md`
2. `docs/01_PROPOSAL.md`
3. `docs/02_TARGET_ARCHITECTURE.md`
4. `docs/03_SKILL_STANDARD.md`
5. `docs/04_EVALUATION_AND_CERTIFICATION.md`
6. `docs/05_IMPLEMENTATION_PLAN.md`
7. `docs/09_REFERENCES_AND_RESOURCES.md`
8. `docs/10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md`
9. `docs/13_NVIDIA_EVALUATOR_UPGRADE_POLICY.md`

The development tracker in `docs/10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md`
is the authoritative source for implementation order and current status.

## Architecture constraint

Keep these concerns separate:

```text
Skills -> Logical tools -> Agentic Data Pipeline -> Enterprise data / analytics
```

The Agentic Data Pipeline exposes stable logical capabilities such as:

```text
portfolio.positions
performance.attribution
risk.factor_exposure
benchmark.positions
market.price_history
```

Skills must not depend directly on physical data implementations.

## Evaluation architecture

```text
NVIDIA SkillEvaluator
    +-- Tier 1: quality/security
    +-- Tier 2: semantic deduplication
    +-- Tier 3: live-agent evaluation / Skill Lift / pass@k
            |
            v
PM AI Domain Graders
            |
            v
Certification Engine
            |
            v
BENCHMARK evidence + Registry
```

NVIDIA is a provider implementation, not the organization-level API contract.
Do not expose raw NVIDIA output structures outside `framework/adapters/`.

## First Codex mission

Implement **Milestone 1 only** from
`docs/10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md`.

Goals:

1. Determine and pin the NVIDIA SkillEvaluator version.
2. Document installation requirements.
3. Verify Tier 1 prerequisites.
4. Verify Docker.
5. Verify Harbor / Tier 3 prerequisites.
6. Configure Codex as the first supported Tier 3 agent.
7. Run NVIDIA Tier 1 against one reference skill.
8. Capture actual NVIDIA CLI/report behavior.
9. Update `framework/adapters/nvidia_skillevaluator.py` to match the pinned version.
10. Add unit tests.
11. Update the progress tracker with completed tasks, blockers, evidence, and next steps.

Do not begin Milestone 2 until Milestone 1 exit criteria are satisfied.

## Suggested first Codex prompt

```text
Read CODEX_START_HERE.md and all documents listed in its "First read" section.

Implement Milestone 1 only from
docs/10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md.

Constraints:
- Do not redesign the target architecture.
- Keep NVIDIA SkillEvaluator behind framework/adapters/.
- Do not expose NVIDIA-specific outputs to downstream code.
- Do not begin Milestone 2.
- Prefer small, testable changes.
- Verify actual NVIDIA CLI behavior against the pinned version.
- Run all relevant tests.
- Update the progress tracker with commands, versions, evidence, blockers,
  completed tasks, and next steps.
- Summarize changed files and remaining risks before stopping.

The desired output is one clean pull-request-sized Milestone 1 implementation.
```

## Recommended PR sequence

1. Pin and integrate real SkillEvaluator.
2. Finalize normalized framework contracts.
3. Complete the synthetic Agentic Data Pipeline.
4. Build Performance Attribution end-to-end.
5. Add Portfolio Overview and Risk Explanation.
6. Demonstrate deliberate defects and remediation.
7. Expand to all 12 skills.
8. Complete finance graders.
9. Harden CI/CD.
10. Demonstrate adoption from a second repository.

## Development rules

- Keep changes PR-sized.
- Update tests with every functional change.
- Update the progress tracker every material PR.
- Never commit credentials.
- Never bypass certification hard gates.
- Prefer deterministic finance graders over LLM judgment.
- Preserve with-skill and without-skill baselines for certification.
- Treat benchmark output as generated evidence.
- Avoid provider lock-in.
- Keep skill instructions separate from authorization logic.
- Convert reviewed production defects into regression cases.
- Never change the pinned NVIDIA SkillEvaluator version outside the process
  in `docs/13_NVIDIA_EVALUATOR_UPGRADE_POLICY.md`.
- Do not add domain-agnostic abstractions in the name of future portability;
  this framework is scoped to PM/asset-management (`docs/01_PROPOSAL.md` §1.5).
