"""Deterministic logical tools used by the reference skills."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

FIXTURE_VERSION = "2026-08-25.v1"
_FIXTURE_ROOT = Path(__file__).parent / "fixtures"

TOOL_CONTRACTS = {
    "portfolio.summary": {"required": ["portfolio_id"], "returns": ["as_of", "benchmark", "return"]},
    "portfolio.positions": {"required": ["portfolio_id"], "returns": ["as_of", "positions"]},
    "benchmark.positions": {"required": ["benchmark_id"], "returns": ["as_of", "positions"]},
    "performance.attribution": {"required": ["portfolio_id"], "returns": ["as_of", "relative_return"]},
    "risk.factor_exposure": {"required": ["portfolio_id"], "returns": ["as_of", "exposures"]},
    "risk.scenario": {"required": ["portfolio_id", "scenario_id"], "returns": ["as_of", "impact"]},
    "market.price_history": {"required": ["security_id"], "returns": ["prices"]},
    "market.security_context": {"required": ["security_id"], "returns": ["security"]},
}


class LogicalToolError(RuntimeError):
    """A predictable error an agent can distinguish from a bad answer."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def available_tools() -> list[str]:
    return sorted(TOOL_CONTRACTS)


def tool_contracts() -> dict[str, dict[str, list[str]]]:
    return copy.deepcopy(TOOL_CONTRACTS)


def _load(name: str) -> dict[str, Any]:
    return json.loads((_FIXTURE_ROOT / name).read_text())


def _portfolio(portfolio_id: str, failure_mode: str | None = None) -> dict[str, Any]:
    if failure_mode == "tool_unavailable":
        raise LogicalToolError("TOOL_UNAVAILABLE", "portfolio data source is unavailable")
    portfolios = _load("portfolio_abc.json")["portfolios"]
    if portfolio_id not in portfolios:
        raise LogicalToolError("NOT_FOUND", f"unknown portfolio: {portfolio_id}")
    portfolio = copy.deepcopy(portfolios[portfolio_id])
    if failure_mode == "stale_data":
        portfolio["as_of"] = "2026-08-22"
    return portfolio


def portfolio_summary(portfolio_id: str, failure_mode: str | None = None) -> dict[str, Any]:
    p = _portfolio(portfolio_id, failure_mode)
    return {
        "portfolio_id": portfolio_id,
        "as_of": p["as_of"],
        "benchmark": p["benchmark"],
        "return": p["return"],
        "benchmark_return": p["benchmark_return"],
        "source": "synthetic.portfolio",
        "fixture_version": FIXTURE_VERSION,
    }


def portfolio_positions(
    portfolio_id: str, failure_mode: str | None = None
) -> dict[str, Any]:
    p = _portfolio(portfolio_id, failure_mode)
    positions = p["positions"]
    if failure_mode == "omit_derivatives":
        positions = [position for position in positions if position.get("type") != "future"]
    return {
        "portfolio_id": portfolio_id,
        "as_of": p["as_of"],
        "positions": positions,
        "coverage": {"derivatives_included": any(item.get("type") == "future" for item in positions)},
        "source": "synthetic.portfolio",
        "fixture_version": FIXTURE_VERSION,
    }


def benchmark_positions(benchmark_id: str, failure_mode: str | None = None) -> dict[str, Any]:
    if failure_mode == "tool_unavailable":
        raise LogicalToolError("TOOL_UNAVAILABLE", "benchmark data source is unavailable")
    benchmarks = _load("benchmark_spx.json")["benchmarks"]
    if benchmark_id not in benchmarks:
        raise LogicalToolError("NOT_FOUND", f"unknown benchmark: {benchmark_id}")
    benchmark = benchmarks[benchmark_id]
    return {
        "benchmark_id": benchmark_id,
        "as_of": benchmark["as_of"],
        "positions": benchmark["positions"],
        "source": "synthetic.benchmark",
        "fixture_version": FIXTURE_VERSION,
    }


def performance_attribution(portfolio_id: str, failure_mode: str | None = None) -> dict[str, Any]:
    p = _portfolio(portfolio_id, failure_mode)
    relative_return = round(p["return"] - p["benchmark_return"], 10)
    contributions = p["attribution"]
    if failure_mode == "omit_sector":
        contributions = {key: value for key, value in contributions.items() if key != "Financials"}
    return {
        "portfolio_id": portfolio_id,
        "as_of": p["as_of"],
        "benchmark": p["benchmark"],
        "portfolio_return": p["return"],
        "benchmark_return": p["benchmark_return"],
        "relative_return": relative_return,
        "contributions": contributions,
        "source": "synthetic.attribution",
        "fixture_version": FIXTURE_VERSION,
    }


def factor_exposure(portfolio_id: str, failure_mode: str | None = None) -> dict[str, Any]:
    p = _portfolio(portfolio_id, failure_mode)
    return {
        "portfolio_id": portfolio_id,
        "as_of": p["as_of"],
        "exposures": p["factor_exposure"],
        "source": "synthetic.factor_risk",
        "fixture_version": FIXTURE_VERSION,
    }


def scenario_risk(
    portfolio_id: str, scenario_id: str, failure_mode: str | None = None
) -> dict[str, Any]:
    p = _portfolio(portfolio_id, failure_mode)
    scenarios = _load("scenarios.json")["scenarios"]
    if scenario_id not in scenarios:
        raise LogicalToolError("NOT_FOUND", f"unknown scenario: {scenario_id}")
    scenario = scenarios[scenario_id]
    return {
        "portfolio_id": portfolio_id,
        "as_of": p["as_of"],
        "scenario_id": scenario_id,
        "scenario": scenario["description"],
        "impact": scenario["impact"],
        "source": "synthetic.scenario",
        "fixture_version": FIXTURE_VERSION,
    }


def price_history(
    security_id: str,
    start_date: str | None = None,
    end_date: str | None = None,
    failure_mode: str | None = None,
) -> dict[str, Any]:
    if failure_mode == "tool_unavailable":
        raise LogicalToolError("TOOL_UNAVAILABLE", "market data source is unavailable")
    securities = _load("market_history.json")["securities"]
    if security_id not in securities:
        raise LogicalToolError("NOT_FOUND", f"unknown security: {security_id}")
    prices = securities[security_id]["prices"]
    prices = {
        date: value
        for date, value in prices.items()
        if (start_date is None or date >= start_date) and (end_date is None or date <= end_date)
    }
    return {
        "security_id": security_id,
        "prices": prices,
        "source": "synthetic.market",
        "fixture_version": FIXTURE_VERSION,
    }


def security_context(security_id: str, failure_mode: str | None = None) -> dict[str, Any]:
    if failure_mode == "tool_unavailable":
        raise LogicalToolError("TOOL_UNAVAILABLE", "security reference data is unavailable")
    securities = _load("market_history.json")["securities"]
    if security_id not in securities:
        raise LogicalToolError("NOT_FOUND", f"unknown security: {security_id}")
    security = {key: value for key, value in securities[security_id].items() if key != "prices"}
    return {
        "security_id": security_id,
        "security": security,
        "source": "synthetic.market",
        "fixture_version": FIXTURE_VERSION,
    }


def call_tool(tool_name: str, **arguments: Any) -> dict[str, Any]:
    """Invoke a logical tool by its stable agent-facing name."""
    handlers = {
        "portfolio.summary": portfolio_summary,
        "portfolio.positions": portfolio_positions,
        "benchmark.positions": benchmark_positions,
        "performance.attribution": performance_attribution,
        "risk.factor_exposure": factor_exposure,
        "risk.scenario": scenario_risk,
        "market.price_history": price_history,
        "market.security_context": security_context,
    }
    if tool_name not in handlers:
        raise LogicalToolError("UNKNOWN_TOOL", f"unknown logical tool: {tool_name}")
    return handlers[tool_name](**arguments)
