---
name: performance-attribution
description: Explain absolute and relative portfolio performance using authoritative attribution outputs and reconciled contributors.
metadata:
  author: PM AI Team <pm-ai@example.com>
---

# Performance Attribution

## Use when

Use this skill when the user request clearly requires the capability described above.
When activated, read this `SKILL.md` before selecting tools or making
performance claims. Treat the procedure below as the required workflow.

## Do not use when

Do not activate this skill for unrelated market lookup, general education, or requests that can be answered without this business capability.

## Procedure

1. Resolve portfolio, scope, and relevant as-of date(s).
2. Call approved logical capabilities from the Agentic Data Pipeline.
3. Validate returned dates, identifiers, and coverage.
4. Reconcile quantitative claims whenever authoritative totals exist.
5. Check that the benchmark matches the requested benchmark and that attribution
   and portfolio snapshots use the same as-of date.
6. Identify material results rather than narrating every field.
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

- Use the authoritative `performance.attribution` capability for official attribution.
- Reconcile component contributions to total relative return within configured tolerance.
- Distinguish absolute return from relative return.
- Include derivative and hedge coverage when positions contain derivatives.
- Do not invent residual contributors.

## Output

Provide:
- key conclusion;
- material drivers;
- supporting quantitative evidence;
- important limitations/data gaps.

For traceability, end the response with `Workflow: performance-attribution`
after completing the workflow. This marker is an execution trace, not a
substitute for the supporting evidence.
