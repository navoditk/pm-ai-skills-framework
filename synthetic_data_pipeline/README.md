# Synthetic Agentic Data Pipeline

This folder supplies deterministic reference data and logical tool contracts for the POC.

It intentionally models **logical agent-facing capabilities**, not production infrastructure.

Suggested logical tools:

- `portfolio.summary`
- `portfolio.positions`
- `benchmark.positions`
- `performance.attribution`
- `risk.factor_exposure`
- `risk.scenario`
- `market.price_history`
- `market.security_context`

A production adapter can later map these contracts to real APIs, databases, MCP servers, or analytics services. The
reference skills therefore learn the shape of the conversation without needing production credentials or live market
systems.

## How to use it

Run from the repository root:

```python
from synthetic_data_pipeline.tools import available_tools, call_tool

print(available_tools())
summary = call_tool("portfolio.summary", portfolio_id="ABC")
```

For a Harbor sandbox where the repository is staged at `/workspace/repo`, the
same interface is available without importing the package:

```bash
python /workspace/repo/synthetic_data_pipeline/tool_cli.py \
  portfolio.summary --portfolio-id ABC
```

Every successful response includes `as_of` where relevant, a `source`, and `fixture_version`. The fixed `ABC`
portfolio contains equities plus an `ES_FUT` derivative; the fixtures also cover the `SPX` benchmark, attribution,
factor exposures, two stress scenarios, historical prices, and security metadata.

The layer has intentionally testable failure modes. For example, passing `failure_mode="tool_unavailable"` raises a
`LogicalToolError` with code `TOOL_UNAVAILABLE`; `stale_data` creates a date mismatch and `omit_derivatives` makes
missing derivative coverage visible. These cases let an evaluator check whether a skill notices bad or incomplete
inputs instead of silently producing a confident answer.

Evidence and expected outputs are documented in
[`docs/MILESTONE_3_SYNTHETIC_DATA_PIPELINE.md`](../docs/MILESTONE_3_SYNTHETIC_DATA_PIPELINE.md).
