import pytest

from synthetic_data_pipeline.tools import (
    LogicalToolError,
    available_tools,
    call_tool,
    factor_exposure,
    performance_attribution,
    portfolio_positions,
    portfolio_summary,
    price_history,
    scenario_risk,
    security_context,
)


def test_catalog_exposes_stable_logical_tools():
    assert available_tools() == [
        "benchmark.positions",
        "market.price_history",
        "market.security_context",
        "performance.attribution",
        "portfolio.positions",
        "portfolio.summary",
        "risk.factor_exposure",
        "risk.scenario",
    ]


def test_portfolio_summary_and_positions_share_date_and_include_derivative():
    summary = portfolio_summary("ABC")
    positions = portfolio_positions("ABC")
    assert summary["as_of"] == positions["as_of"] == "2026-08-25"
    assert positions["coverage"]["derivatives_included"] is True
    assert any(item["id"] == "ES_FUT" for item in positions["positions"])


def test_attribution_and_factor_data_are_reconcilable():
    attribution = performance_attribution("ABC")
    assert sum(attribution["contributions"].values()) == attribution["relative_return"]
    assert factor_exposure("ABC")["exposures"]["Market"] == 0.82


def test_benchmark_scenario_and_market_fixtures_are_available():
    assert call_tool("benchmark.positions", benchmark_id="SPX")["as_of"] == "2026-08-25"
    assert scenario_risk("ABC", "equity-down-10pct")["impact"] == -0.082
    prices = price_history("AAPL", start_date="2026-08-25")
    assert prices["prices"] == {"2026-08-25": 227.4}
    assert security_context("ES_FUT")["security"]["underlying"] == "SPX"


def test_dispatcher_returns_same_contract_as_direct_call():
    assert call_tool("portfolio.summary", portfolio_id="ABC") == portfolio_summary("ABC")


def test_controlled_failures_are_machine_readable():
    with pytest.raises(LogicalToolError, match="unavailable") as error:
        call_tool("market.price_history", security_id="AAPL", failure_mode="tool_unavailable")
    assert error.value.code == "TOOL_UNAVAILABLE"


def test_stale_fixture_can_expose_date_mismatch():
    summary = portfolio_summary("ABC", failure_mode="stale_data")
    positions = portfolio_positions("ABC")
    assert summary["as_of"] != positions["as_of"]


def test_derivative_omission_is_explicitly_visible():
    positions = portfolio_positions("ABC", failure_mode="omit_derivatives")
    assert positions["coverage"]["derivatives_included"] is False
    assert all(item.get("type") != "future" for item in positions["positions"])
