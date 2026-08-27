import json
from pathlib import Path

_FIXTURE = json.loads(
    (Path(__file__).parent / "fixtures" / "portfolio_abc.json").read_text()
)

def portfolio_summary(portfolio_id: str):
    p = _FIXTURE["portfolios"][portfolio_id]
    return {k: p[k] for k in ["as_of", "benchmark", "return", "benchmark_return"]}

def portfolio_positions(portfolio_id: str):
    return _FIXTURE["portfolios"][portfolio_id]["positions"]

def performance_attribution(portfolio_id: str):
    p = _FIXTURE["portfolios"][portfolio_id]
    return {"as_of": p["as_of"], "benchmark": p["benchmark"],
            "relative_return": p["return"] - p["benchmark_return"],
            "contributions": p["attribution"]}

def factor_exposure(portfolio_id: str):
    p = _FIXTURE["portfolios"][portfolio_id]
    return {"as_of": p["as_of"], "exposures": p["factor_exposure"]}
