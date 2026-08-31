---
name: liquidity-analysis
description: Identify and explain portfolio liquidity risks using approved liquidity metrics and classifications.
metadata:
  author: PM AI <pm-ai@example.com>
---

# Liquidity Analysis

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

- Use `portfolio.positions` for position weight, type, and currency as
  liquidity risk proxies (e.g. concentrated weights, derivative/futures
  positions carrying rollover or margin exposure).
- The reference data has no dedicated liquidity classification field.
  Explicitly disclose that limitation rather than inventing a liquidity
  score, tier, or classification that does not exist in the tool output.
- Never infer a missing position's weight, type, or currency; report it as
  unavailable instead.

## Output

Provide:
- key conclusion;
- material drivers;
- supporting quantitative evidence;
- important limitations/data gaps.

For traceability, end the response with `Workflow: liquidity-analysis`
after completing the workflow. This marker is an execution trace, not a
substitute for the supporting evidence.
