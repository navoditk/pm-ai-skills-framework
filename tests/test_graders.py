from graders.finance.attribution_reconciliation import grade as recon
from graders.finance.temporal_consistency import grade as temporal
from graders.finance.benchmark_consistency import grade as benchmark

def test_reconciliation_passes():
    r = recon(-0.0021, [-0.0012, -0.0005, -0.0003, -0.0001], tolerance=1e-9)
    assert r["score"] == 1.0

def test_temporal_detects_mismatch():
    r = temporal("2026-08-25", ["2026-08-25", "2026-08-22"])
    assert r["score"] == 0.0

def test_benchmark():
    assert benchmark("SPX", "SPX")["score"] == 1.0
