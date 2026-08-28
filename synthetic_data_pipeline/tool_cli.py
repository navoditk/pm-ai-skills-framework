"""Command-line bridge for logical tools inside a sandboxed evaluator."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from synthetic_data_pipeline.tools import call_tool


def main() -> None:
    parser = argparse.ArgumentParser(description="Invoke a deterministic PM AI logical tool")
    parser.add_argument("tool_name", choices=(
        "portfolio.summary", "portfolio.positions", "benchmark.positions",
        "performance.attribution", "risk.factor_exposure", "risk.scenario",
        "market.price_history", "market.security_context",
    ))
    parser.add_argument("--portfolio-id")
    parser.add_argument("--benchmark-id")
    parser.add_argument("--scenario-id")
    parser.add_argument("--security-id")
    parser.add_argument("--start-date")
    parser.add_argument("--end-date")
    parser.add_argument("--failure-mode")
    args = parser.parse_args()
    values: dict[str, Any] = {
        key.replace("_", "-"): value
        for key, value in vars(args).items()
        if key not in {"tool_name"} and value is not None
    }
    values = {key.replace("-", "_"): value for key, value in values.items()}
    print(json.dumps(call_tool(args.tool_name, **values), sort_keys=True))


if __name__ == "__main__":
    main()
