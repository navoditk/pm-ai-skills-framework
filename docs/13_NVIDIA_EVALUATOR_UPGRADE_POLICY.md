# 13. NVIDIA SkillEvaluator Upgrade Policy

## 13.1 Why this policy exists

This framework leverages NVIDIA SkillEvaluator as its evaluation engine
rather than building a parallel one. That decision only pays off if a future
NVIDIA release can't silently change what "certified" means for a PM skill.
This document defines how the pinned version is chosen, tested, upgraded, and
rolled back.

This is not a hypothetical concern. Milestone 4 already hit a real
evaluator-compatibility gap: the pinned `0.2.1` Tier 3 execution heuristic
recognizes `bash`, `execute`, `exec_command`, `run_code`, `run`, `shell`, and
`command` as execution evidence, but not Codex's bare `exec` action — so a
skill the agent genuinely read and used still scored `skill_efficiency: 0.08`.
See `docs/MILESTONE_4_PERFORMANCE_ATTRIBUTION.md` for the full trace. That
finding is the seed entry in the compatibility log at 13.6.

## 13.2 Versioning policy

- Exactly one NVIDIA SkillEvaluator version is pinned at a time, recorded as
  both a semantic version and a commit hash (currently `0.2.1` at
  `009aa300be7925c7ba75760592baeb941cc29ba8` — see `docs/MILESTONE_1_SETUP.md`).
- The pin lives in one place (`framework/version.py` plus the developer
  install instructions in `docs/MILESTONE_1_SETUP.md`); nothing else in the
  repository should hardcode a version number.
- The evaluator version is part of the benchmark identity tuple
  (`docs/02_TARGET_ARCHITECTURE.md` §2.5). Upgrading it invalidates prior
  benchmark evidence for re-certification purposes, even if nothing else
  about the skill changed — old evidence stays valid as a historical record,
  but a skill is not "still certified" against a new evaluator version
  without a fresh run.

## 13.3 Upgrade triggers

An upgrade is evaluated, not automatic, and is triggered by one of:

- a security advisory against the pinned version;
- a bugfix the framework actually needs (for example, an execution-heuristic
  fix for the `exec` gap in 13.6);
- a feature required for a planned milestone (for example, an additional
  supported Tier 3 agent);
- the pinned version approaching upstream end-of-support.

Chasing every upstream release is explicitly out of scope — the pin changes
only when one of the above applies.

## 13.4 Upgrade process

1. **Install the candidate version in an isolated dev environment.** Do not
   touch the pinned `.venv` used for current certification work.
2. **Run the adapter/provider test suite unmodified** against the candidate
   (`tests/test_nvidia_skillevaluator.py`, `tests/test_contracts.py`). A
   passing run with zero code changes is the best-case outcome; any failure
   is triaged before proceeding.
3. **Re-run Tier 1 against the reference skill** used in Milestone 1
   (`skills/portfolio-overview`) and diff the raw report structure against
   the baseline captured in `reports/m1/tier1-v296/`. A structural change
   here means `framework/adapters/nvidia_skillevaluator.py`'s parser needs an
   update — nothing downstream of the adapter should need to change.
4. **Re-run one full Tier 3 matrix** (Performance Attribution, the existing
   25-case set) with-skill and baseline, and compare every metric against the
   last certified/diagnostic benchmark
   (`reports/m4/performance-attribution-tier3-normal-timeout/`). Flag any
   metric delta beyond a reviewed tolerance for manual inspection before
   trusting it as a real change rather than an artifact of the upgrade.
5. **Update the adapter only.** If the raw NVIDIA schema changed, update the
   parser in `framework/adapters/nvidia_skillevaluator.py`. The normalized
   output schema (`framework/schemas/evaluation-result.schema.json`) should
   not need to change; if it does, that is a signal worth escalating, since
   it means the normalization boundary didn't hold.
6. **Record the upgrade** in the compatibility log (13.6): old version, new
   version, commit hash, what was tested, what changed, and any newly
   discovered or newly resolved compatibility gaps.
7. **Roll out staged.** New pin runs advisory-only in CI for one release
   cycle before it becomes the version blocking gates depend on, mirroring
   how Tier 3 itself starts advisory (`docs/07_GITHUB_PUBLISHING.md` §7.4).
8. **Keep a rollback path.** The previous pinned version's environment stays
   available until the new pin has run one full certification cycle
   cleanly. If a regression surfaces, roll the pin back and re-open the
   upgrade as blocked pending an upstream fix.

## 13.5 Ownership

Version bumps are approved by the same team that owns the certification
policy (the platform/PM-AI team), not by whoever happens to be working on an
unrelated skill PR. A version bump is a framework-level change and should go
through its own PR, separate from any skill content change, so its test
evidence (13.4 steps 2-4) is reviewable on its own.

## 13.6 Known compatibility issues log

Use this table as the running record of evaluator-specific gaps discovered
during use. Each entry should stay until the upstream fix is confirmed in a
later pinned version.

| Discovered | Evaluator version | Issue | Impact | Status |
|---|---|---|---|---|
| 2026-08-27 | 0.2.1 | Tier 3 execution/efficiency heuristic does not recognize Codex's bare `exec` action as execution evidence (recognizes `bash`, `execute`, `exec_command`, `run_code`, `run`, `shell`, `command`). | `skill_execution` and `skill_efficiency` scores are undercounted for Codex-based Tier 3 runs even when the skill was read and used correctly; blocked Performance Attribution certification. | Mitigated 2026-08-28 by using `claude-code` as the Tier 3 agent instead — its native `Bash`/`Read`/`Skill` tool names are already recognized by the same heuristic, confirmed live (see `docs/MILESTONE_4_PERFORMANCE_ATTRIBUTION.md`). Root cause is still unfixed upstream for Codex specifically; file upstream before Codex is relied on again as a Tier 3 agent. Do not patch the vendored evaluator locally. |
| 2026-08-28 | 0.2.1 | Tier 3 `accuracy`/`goal_accuracy` LLM-judge call intermittently returns a response the evaluator cannot parse as JSON (`"Judge response was not a valid JSON object"`), observed on ~36% of with-skill / ~12% of baseline single-attempt trials against `claude-opus-5` as judge. Not agent-specific — the judge call is separate from the agent under test. | A single-attempt (`n_attempts: 1`) run can fall below full case coverage and have its aggregate score suppressed entirely, even though `skill_execution`/`skill_efficiency` (non-judge metrics) score normally. | Open, low severity — `n_attempts: 3` (the certification default) provides redundancy against a single flaky judge call per case; monitor whether the full 3-attempt matrix still shows uncovered cases. No local workaround planned unless it recurs at `n_attempts: 3`. |

Do not delete resolved rows; mark them `Resolved in <version>` so the log
also serves as upgrade-testing history.
