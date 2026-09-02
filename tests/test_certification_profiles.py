import pytest
import yaml

from framework.certification.engine import decide
from framework.certification.profile_resolver import resolve_profile

REPO_ROOT_POLICY = yaml.safe_load(open("policies/certification.yaml"))

ALL_RISK_LEVELS = ["informational", "low", "analytical", "decision-support", "action"]


@pytest.mark.parametrize("risk_level", ALL_RISK_LEVELS)
def test_every_schema_risk_level_resolves_to_a_real_profile(risk_level):
    profile_name, profile = resolve_profile(REPO_ROOT_POLICY, risk_level)
    assert profile_name
    assert "hard_gates" in profile
    assert "minimum_metrics" in profile


def test_unknown_risk_level_raises_clear_error():
    with pytest.raises(KeyError, match="not-a-real-risk-level"):
        resolve_profile(REPO_ROOT_POLICY, "not-a-real-risk-level")


def test_rigor_increases_with_risk_level():
    """Discoverability floor should be monotonically non-decreasing as risk
    rises informational -> low -> analytical -> decision-support, matching
    docs/04_EVALUATION_AND_CERTIFICATION.md section 4.2a's intent that
    certification rigor scales with downstream risk."""
    floors = []
    for risk_level in ["informational", "low", "analytical", "decision-support"]:
        _, profile = resolve_profile(REPO_ROOT_POLICY, risk_level)
        floors.append(profile["minimum_metrics"]["discoverability"])
    assert floors == sorted(floors)


def test_decision_support_promotes_tier4_metrics_to_hard_gates():
    _, analytical = resolve_profile(REPO_ROOT_POLICY, "analytical")
    _, decision_support = resolve_profile(REPO_ROOT_POLICY, "decision-support")
    assert "financial_accuracy" in analytical["minimum_metrics"]
    assert "financial_accuracy" not in analytical["hard_gates"]
    assert "financial_accuracy" in decision_support["hard_gates"]
    assert "financial_accuracy" not in decision_support["minimum_metrics"]


def test_action_profile_cannot_pass_without_a_recorded_human_review():
    """No metrics collector in this repo produces human_review_required --
    this proves an action-tier skill cannot self-certify from automated
    Tier 1-4 evidence alone, by design."""
    _, action = resolve_profile(REPO_ROOT_POLICY, "action")
    metrics_without_human_review = {
        "security": "pass",
        "authorization": "pass",
        "regression_pass_rate": 1.0,
        "data_provenance": 1.0,
        "financial_accuracy": 0.999,
        "temporal_consistency": 1.0,
        "correctness": 0.99,
        "discoverability": 0.99,
        "effectiveness": 0.99,
        "efficiency": 0.99,
        "skill_lift_overall": 0.20,
    }
    decision = decide(metrics_without_human_review, action)
    assert decision.status == "FAIL"
    assert any("human_review_required" in f for f in decision.failures)

    metrics_with_human_review = dict(metrics_without_human_review, human_review_required=True)
    decision = decide(metrics_with_human_review, action)
    assert decision.status == "PASS"


def test_real_skills_still_resolve_to_analytical_standard():
    """Both flagship skills' generate_benchmark.py now derive their profile
    from classification.risk_level rather than a hardcoded string -- confirm
    that still lands on analytical-standard for skills classified analytical."""
    profile_name, _ = resolve_profile(REPO_ROOT_POLICY, "analytical")
    assert profile_name == "analytical-standard"
