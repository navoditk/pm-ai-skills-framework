---
name: risk-explanation
description: Explain the material sources and changes in portfolio risk using authoritative risk analytics.
metadata:
  author: PM AI <pm-ai@example.com>
---

# Risk Explanation

## Use when

Use this skill when the user request clearly requires the capability described above.
When activated, read this `SKILL.md` before selecting tools or making
risk claims. Treat the procedure below as the required workflow.

## Do not use when

Do not activate this skill for unrelated market lookup, general education, or requests that can be answered without this business capability.

## Procedure

1. Resolve portfolio, scope, and relevant as-of date(s).
2. Call approved logical capabilities from the Agentic Data Pipeline.
3. Validate returned dates, identifiers, and coverage.
4. Identify the largest factor exposures or scenario impacts as the material
   drivers, rather than narrating every field.
5. Include derivative and hedge positions when assessing exposure.
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

- Use `risk.factor_exposure` for factor-level risk and `risk.scenario` for
  stress-scenario impact; use `portfolio.positions` when exposure needs to be
  tied to specific holdings.
- Include derivative-equivalent exposure when derivatives are present in the
  portfolio's positions.
- Distinguish gross exposure (sum of position weights) from net exposure
  (positions netted against hedges) when both are relevant.
- Never infer a missing official factor exposure or scenario result; report
  it as unavailable instead.

## Output

Provide:
- key conclusion;
- material drivers;
- supporting quantitative evidence;
- important limitations/data gaps.

For traceability, end the response with `Workflow: risk-explanation`
after completing the workflow. This marker is an execution trace, not a
substitute for the supporting evidence.
