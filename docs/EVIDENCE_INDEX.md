# Evidence index

The repository versions compact benchmark conclusions and normalized benchmark
records. Large raw NVIDIA reports are intentionally excluded from Git because
they contain long generated trajectories.

Tracked evidence:

- [`Performance Attribution benchmark`](../skills/performance-attribution/BENCHMARK.md)
- [`Performance Attribution JSON`](../skills/performance-attribution/BENCHMARK.json)
- [`Portfolio Overview benchmark`](../skills/portfolio-overview/BENCHMARK.md)
- [`Portfolio Overview JSON`](../skills/portfolio-overview/BENCHMARK.json)
- [`Sample report`](../examples/sample-certification-report.md)

Raw reports may exist locally under `reports/`, but a clean checkout should use
the tracked benchmark records and should not assume those directories exist.

Current live-evaluation handoff (2026-09-03/04): Risk Explanation has no
finalized Tier 3 evidence. The first capped run reached 100 observed arms out
of 162 and was stopped at an estimated $30; its interrupted per-trial
artifacts were not finalized. A fresh one-attempt pass then stopped during
Claude Code runtime preflight after 71.843 seconds. The retained failure
record is [`result.json`](../reports/m5/risk-explanation-tier3-additional30/risk-explanation/20260904_020127_36122_6b9e96234e14/result.json).
The pinned evaluator exposes neither reliable cost telemetry nor case-level
resume; do not infer certification from either attempt.
