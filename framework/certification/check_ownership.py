"""Pre-Tier-1 ownership enforcement gate.

Implements docs/03_SKILL_STANDARD.md §3.8: "No owner -> no certification."
A skill.yaml carrying a placeholder ownership value (business owner,
technical/engineering owner, or domain reviewer) fails this check before any
Tier 1/2/3 evaluation cost is spent -- deterministic, offline, free.

Usage:
    python framework/certification/check_ownership.py skills/my-skill [skills/other-skill ...]
    python framework/certification/check_ownership.py --all   # scan every skills/*/

Exits non-zero (and prints one line per violation) if any target skill's
skill.yaml is missing an ownership field or still carries a placeholder.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]

REQUIRED_FIELDS = ("business", "engineering", "domain_reviewer")

# Literal placeholder strings that mean "not actually assigned yet." Matched
# case-sensitively against the exact field value -- a real team/person slug
# that merely contains a similar word (e.g. "domain-reviewers-team") is not
# a false positive here because these are exact placeholder tokens, not
# substrings.
PLACEHOLDER_VALUES = {
    "domain-owner-required",
    "owner-required",
    "unassigned",
    "",
    None,
}


def check_skill(skill_dir: Path, *, require_manifest: bool = False) -> list[str]:
    """Return a list of violation messages for one skill directory (empty if clean)."""
    skill_yaml = skill_dir / "skill.yaml"
    if not skill_yaml.exists():
        # Not every skill directory ships a skill.yaml (e.g. smoke-test
        # fixtures) -- absence of the file is out of scope for this check.
        return [f"{skill_dir}: missing required skill.yaml"] if require_manifest else []

    data = yaml.safe_load(skill_yaml.read_text()) or {}
    ownership = data.get("ownership") or {}
    try:
        display_path = skill_yaml.relative_to(REPO_ROOT)
    except ValueError:
        # Target lives outside this repo (e.g. a scratch fixture used to
        # exercise this check) -- fall back to the raw path instead of
        # crashing.
        display_path = skill_yaml
    violations = []
    for field in REQUIRED_FIELDS:
        value = ownership.get(field)
        if value in PLACEHOLDER_VALUES:
            violations.append(
                f"{display_path}: ownership.{field} is "
                f"missing or a placeholder ({value!r}) -- no owner, no certification"
                " (docs/03_SKILL_STANDARD.md §3.8)"
            )
    return violations


def main() -> int:
    args = sys.argv[1:]
    if not args:
        print(f"Usage: {sys.argv[0]} <skill-dir> [<skill-dir> ...] | --all", file=sys.stderr)
        return 2

    if args == ["--all"]:
        targets = sorted(p.parent for p in (REPO_ROOT / "skills").glob("*/skill.yaml"))
    else:
        targets = [Path(a) for a in args]

    all_violations: list[str] = []
    for target in targets:
        all_violations.extend(check_skill(target))

    if all_violations:
        for v in all_violations:
            print(f"[OWNERSHIP-FAIL] {v}")
        print(f"\n{len(all_violations)} ownership violation(s) across {len(targets)} skill(s) checked.")
        return 1

    print(f"[OK] ownership check passed for {len(targets)} skill(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
