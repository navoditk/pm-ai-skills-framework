---
name: portfolio-overview
description: Summarize portfolio composition, benchmark context, major exposures, and material changes.
metadata:
  author: PM AI <pm-ai@example.com>
---

# Portfolio Overview

## Use when

Use this skill when the user request clearly requires the capability described above.
When activated, read this `SKILL.md` before selecting tools or making
portfolio claims. Treat the procedure below as the required workflow.

## Do not use when

Do not activate this skill for unrelated market lookup, general education, or requests that can be answered without this business capability.

## Procedure

1. Resolve portfolio, scope, and relevant as-of date(s).
2. Call approved logical capabilities from the Agentic Data Pipeline.
3. Validate returned dates, identifiers, and coverage.
4. Reconcile quantitative claims whenever authoritative totals exist.
5. Identify the largest positions and any derivative/hedge exposure as the
   material drivers of composition, rather than narrating every position.
6. Compare portfolio return and benchmark return when both are available.
7. Explain uncertainty or missing data explicitly.
8. Produce a concise PM-oriented answer grounded in tool results.

## Data and tool rules

- Prefer authoritative internal analytical capabilities over independent LLM calculations.
- Never fabricate a portfolio value, benchmark, position, return, exposure, or risk statistic.
- Never bypass authorization.
- Preserve source and as-of metadata for quantitative claims.
- In the sandboxed reference evaluation, invoke the staged deterministic bridge
  with `python /workspace/repo/synthetic_data_pipeline/tool_cli.py TOOL_NAME`
  and the relevant flags. Treat its JSON response as the logical-tool result.

## Domain rules

- Use `portfolio.summary` for return, benchmark, and as-of context, and
  `portfolio.positions` for composition.
- Include derivative and hedge positions (e.g. index futures) in the
  composition summary; do not omit them because they carry a negative or
  unusual weight.
- Distinguish the portfolio's own return from its benchmark's return; do not
  conflate them.
- Do not invent a sector, exposure, or position not present in the tool
  response.

## Output

Provide:
- key conclusion;
- material drivers;
- supporting quantitative evidence;
- important limitations/data gaps.

For traceability, end the response with `Workflow: portfolio-overview`
after completing the workflow. This marker is an execution trace, not a
substitute for the supporting evidence.
