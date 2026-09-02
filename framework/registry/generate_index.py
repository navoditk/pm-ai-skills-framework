"""Generate a lightweight skill registry index.

Pulled forward from Milestone 12 (docs/10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md,
"Following PR -- Lightweight registry"): the artifact that actually prevents
duplicate skill-building going forward, not just detects it after the fact
the way the Tier 2 similarity gate does at PR time.

Reads three already-computed, already-committed sources -- no new API calls,
no live-agent spend:
  1. catalogs/skill-catalog.json      -- which skills exist (id, path)
  2. skills/<name>/skill.yaml         -- owner, risk_level, version
  3. skills/<name>/BENCHMARK.json     -- certification status, if certified

"Last benchmark date" comes from the BENCHMARK.json file's last git commit
date, not a field inside the file -- BENCHMARK.json doesn't carry its own
generation timestamp, and git history is the honest source of truth for
"when was this last regenerated" (a file with no commits, e.g. a fresh
uncommitted regeneration, falls back to filesystem mtime).

Usage:
    python framework/registry/generate_index.py [-o catalogs/skill-registry.json]
"""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]


def _git_last_commit_date(path: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%aI", "--", str(path.relative_to(REPO_ROOT))],
            cwd=REPO_ROOT, capture_output=True, text=True, check=True,
        )
    except subprocess.CalledProcessError:
        return None
    date = result.stdout.strip()
    if date:
        return date
    if path.exists():
        return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()
    return None


def build_registry() -> dict:
    catalog = json.loads((REPO_ROOT / "catalogs" / "skill-catalog.json").read_text())

    entries = []
    for entry in catalog["entries"]:
        skill_dir = REPO_ROOT / "skills" / entry["path"]
        skill_yaml_path = skill_dir / "skill.yaml"
        if not skill_yaml_path.exists():
            continue
        manifest = yaml.safe_load(skill_yaml_path.read_text())

        benchmark_path = skill_dir / "BENCHMARK.json"
        if benchmark_path.exists():
            benchmark = json.loads(benchmark_path.read_text())
            certification = benchmark.get("certification", {})
            certification_state = certification.get("status", "UNKNOWN")
            certification_profile = certification.get("profile")
            last_benchmark_date = _git_last_commit_date(benchmark_path)
        else:
            certification_state = "NOT_CERTIFIED"
            certification_profile = None
            last_benchmark_date = None

        entries.append({
            "id": manifest["skill"]["id"],
            "name": manifest["skill"]["name"],
            "version": manifest["skill"]["version"],
            "path": entry["path"],
            "domain": manifest.get("classification", {}).get("domain"),
            "risk_level": manifest.get("classification", {}).get("risk_level"),
            "owner": {
                "business": manifest.get("ownership", {}).get("business"),
                "engineering": manifest.get("ownership", {}).get("engineering"),
                "domain_reviewer": manifest.get("ownership", {}).get("domain_reviewer"),
            },
            "certification_state": certification_state,
            "certification_profile": certification_profile,
            "last_benchmark_date": last_benchmark_date,
            "content_fingerprint": entry.get("content_fingerprint"),
        })

    entries.sort(key=lambda e: e["id"])

    return {
        "schema_version": 1,
        "generated_from": {
            "catalog": "catalogs/skill-catalog.json",
            "catalog_created_at": catalog.get("created_at"),
        },
        "skills": entries,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", default="catalogs/skill-registry.json")
    args = parser.parse_args()

    registry = build_registry()
    out_path = REPO_ROOT / args.output
    out_path.write_text(json.dumps(registry, indent=2) + "\n")

    certified = sum(1 for s in registry["skills"] if s["certification_state"] == "PASS")
    failed = sum(1 for s in registry["skills"] if s["certification_state"] == "FAIL")
    not_certified = sum(1 for s in registry["skills"] if s["certification_state"] == "NOT_CERTIFIED")
    print(f"{len(registry['skills'])} skills indexed -> {out_path}")
    print(f"  certified (PASS): {certified}  certified (FAIL): {failed}  not yet certified: {not_certified}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
