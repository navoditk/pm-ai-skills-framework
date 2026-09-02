"""Resolve a skill's certification profile from its classification.risk_level
(docs/04_EVALUATION_AND_CERTIFICATION.md §4.2a), instead of every caller
hardcoding "analytical-standard". policies/certification.yaml's
risk_level_profiles maps each of the five risk_level values
(informational, low, analytical, decision-support, action) -- the same enum
in framework/schemas/skill.schema.json -- to a profile name in
policies/certification.yaml's profiles block.
"""
from __future__ import annotations

from typing import Tuple


def resolve_profile(policy: dict, risk_level: str) -> Tuple[str, dict]:
    """Return (profile_name, profile_dict) for the given risk_level.

    Raises KeyError with a clear message if risk_level or the profile it
    maps to is missing from policy, rather than silently defaulting --
    a missing mapping is a policy authoring bug that should fail loudly.
    """
    risk_level_profiles = policy.get("risk_level_profiles", {})
    if risk_level not in risk_level_profiles:
        raise KeyError(
            f"No certification profile mapped for risk_level={risk_level!r} "
            f"in policies/certification.yaml's risk_level_profiles "
            f"(known: {sorted(risk_level_profiles)})"
        )
    profile_name = risk_level_profiles[risk_level]
    profiles = policy.get("profiles", {})
    if profile_name not in profiles:
        raise KeyError(
            f"risk_level_profiles maps {risk_level!r} -> {profile_name!r}, "
            f"but no such profile exists in policies/certification.yaml's "
            f"profiles block (known: {sorted(profiles)})"
        )
    return profile_name, profiles[profile_name]
