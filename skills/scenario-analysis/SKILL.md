---
name: scenario-analysis
description: Explain portfolio behavior under approved deterministic market or risk scenarios.
metadata:
  author: PM AI <pm-ai@example.com>
---

# Scenario Analysis

## Use when

Use this skill when the user request clearly requires the capability described above.

## Do not use when

Do not activate this skill for unrelated market lookup, general education, or requests that can be answered without this business capability.

## Procedure

1. Resolve portfolio, scope, and relevant as-of date(s).
2. Call approved logical capabilities from the Agentic Data Pipeline.
3. Validate returned dates, identifiers, and coverage.
4. Reconcile quantitative claims whenever authoritative totals exist.
5. Identify material results rather than narrating every field.
6. Explain uncertainty or missing data explicitly.
7. Produce a concise PM-oriented answer grounded in tool results.

## Data and tool rules

- Prefer authoritative internal analytical capabilities over independent LLM calculations.
- Never fabricate a portfolio value, benchmark, position, return, exposure, or risk statistic.
- Never bypass authorization.
- Preserve source and as-of metadata for quantitative claims.
- In the sandboxed reference evaluation, invoke the staged deterministic bridge
  with `python /workspace/repo/synthetic_data_pipeline/tool_cli.py TOOL_NAME`
  and the relevant flags. Treat its JSON response as the logical-tool result.

## Domain rules

- Use `risk.scenario` for the scenario impact and `portfolio.positions` when
  the impact needs to be tied to specific holdings.
- Only use scenarios explicitly approved for this evaluation; never invent
  a scenario or extrapolate an unapproved one.
- Never infer a missing scenario result; report it as unavailable instead.

## Output

Provide:
- key conclusion;
- material drivers;
- supporting quantitative evidence;
- important limitations/data gaps.

For traceability, end the response with `Workflow: scenario-analysis`
after completing the workflow. This marker is an execution trace, not a
substitute for the supporting evidence.
