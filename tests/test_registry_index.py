from framework.registry.generate_index import build_registry


def test_registry_covers_every_catalog_entry():
    registry = build_registry()
    assert len(registry["skills"]) == 13


def test_certified_skills_carry_a_real_status_and_profile():
    registry = build_registry()
    by_id = {s["id"]: s for s in registry["skills"]}

    perf_attr = by_id["pm.performance.attribution"]
    assert perf_attr["certification_state"] == "FAIL"
    assert perf_attr["certification_profile"] == "analytical-standard"
    assert perf_attr["last_benchmark_date"] is not None

    portfolio = by_id["pm.portfolio.overview"]
    assert portfolio["certification_state"] == "FAIL"
    assert portfolio["last_benchmark_date"] is not None


def test_uncertified_skills_report_not_certified_with_no_date():
    registry = build_registry()
    by_id = {s["id"]: s for s in registry["skills"]}

    exposure = by_id["pm.exposure.analysis"]
    assert exposure["certification_state"] == "NOT_CERTIFIED"
    assert exposure["certification_profile"] is None
    assert exposure["last_benchmark_date"] is None


def test_every_entry_carries_owner_and_risk_level():
    registry = build_registry()
    for skill in registry["skills"]:
        assert skill["risk_level"] in {
            "informational", "low", "analytical", "decision-support", "action",
        }
        assert skill["owner"]["domain_reviewer"]
        assert skill["owner"]["domain_reviewer"] != "domain-owner-required"
