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

A production adapter can later map these contracts to real APIs, databases, MCP servers, or analytics services.
