# Milestone 3 Evidence — Synthetic Agentic Data Pipeline

## What this milestone provides

An agent needs information from somewhere before it can answer a portfolio question. In a real deployment that
information might come from databases, market-data APIs, or MCP services. Those systems are slow to configure and can
change between runs. Milestone 3 supplies a small, local substitute: predictable data and eight named “logical tools.”

This makes the reference skills testable from a clean checkout. It also gives future production adapters a stable
interface to implement.

## Reproduce the evidence

From the repository root:

```bash
.venv/bin/python -m pytest -q tests/test_synthetic_pipeline.py
```

Expected result at completion of this milestone:

```text
8 passed
```

The complete suite is run with:

```bash
.venv/bin/python -m pytest -q
```

## Logical tool catalog

| Tool | What it returns |
| --- | --- |
| `portfolio.summary` | Portfolio return, benchmark, and date |
| `portfolio.positions` | Holdings and derivative-coverage flag |
| `benchmark.positions` | Benchmark holdings |
| `performance.attribution` | Portfolio-versus-benchmark contribution breakdown |
| `risk.factor_exposure` | Factor exposures such as market and value |
| `risk.scenario` | Result of a named stress scenario |
| `market.price_history` | Date-filterable security prices |
| `market.security_context` | Asset class, currency, and derivative metadata |

Example:

```python
from synthetic_data_pipeline.tools import call_tool

call_tool("portfolio.summary", portfolio_id="ABC")
```

Expected shape:

```json
{
  "portfolio_id": "ABC",
  "as_of": "2026-08-25",
  "benchmark": "SPX",
  "return": 0.0042,
  "benchmark_return": 0.0063,
  "source": "synthetic.portfolio",
  "fixture_version": "2026-08-25.v1"
}
```

## What is covered

The `ABC` fixture has AAPL, MSFT, JPM, and an `ES_FUT` index future. Its return is 0.42% versus 0.63% for SPX,
so relative return is -0.21%; the attribution contributions add to that same value. The market fixture has prices on
2026-08-22 and 2026-08-25, and the scenario fixture includes rates up 100 basis points and equities down 10%.

## Deliberate bad-data cases

These are not accidental failures. They are test inputs for skills that should verify evidence:

```python
from synthetic_data_pipeline.tools import LogicalToolError, call_tool

try:
    call_tool("market.price_history", security_id="AAPL", failure_mode="tool_unavailable")
except LogicalToolError as error:
    assert error.code == "TOOL_UNAVAILABLE"

stale = call_tool("portfolio.summary", portfolio_id="ABC", failure_mode="stale_data")
incomplete = call_tool("portfolio.positions", portfolio_id="ABC", failure_mode="omit_derivatives")
```

The tests also show an unknown identifier returning `NOT_FOUND`, date mismatch detection, and explicit derivative
coverage. This is the evidence a reader can use to understand the end product without access to a live system.

## Evidence map

- Interfaces and dispatcher: [`synthetic_data_pipeline/tools.py`](../synthetic_data_pipeline/tools.py)
- Portfolio fixture: [`synthetic_data_pipeline/fixtures/portfolio_abc.json`](../synthetic_data_pipeline/fixtures/portfolio_abc.json)
- Benchmark fixture: [`synthetic_data_pipeline/fixtures/benchmark_spx.json`](../synthetic_data_pipeline/fixtures/benchmark_spx.json)
- Risk and market fixtures: [`synthetic_data_pipeline/fixtures/scenarios.json`](../synthetic_data_pipeline/fixtures/scenarios.json), [`synthetic_data_pipeline/fixtures/market_history.json`](../synthetic_data_pipeline/fixtures/market_history.json)
- Executable proof: [`tests/test_synthetic_pipeline.py`](../tests/test_synthetic_pipeline.py)

Milestone 4 can now build Performance Attribution against these logical tools and fixtures, without introducing a
production-system dependency.
