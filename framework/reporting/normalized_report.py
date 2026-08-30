import json
from pathlib import Path

def write_json(result: dict, path: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(result, indent=2), encoding="utf-8")

def write_markdown(result: dict, path: str):
    lines = [
        "# PM AI Skill Certification Report",
        "",
        f"**Skill:** {result.get('skill', {}).get('name', 'unknown')}",
        f"**Version:** {result.get('skill', {}).get('version', 'unknown')}",
        f"**Certification:** {result.get('certification', {}).get('status', 'UNKNOWN')}",
        "",
        "## Generic Metrics",
    ]
    for k, v in result.get("generic_metrics", {}).items():
        lines.append(f"- **{k}:** {v}")

    skill_lift = result.get("skill_lift") or {}
    reliability = result.get("reliability") or {}
    # `reliability` nests pass@k separately per arm (with_skill/without_skill/
    # lift); fall back to the dict itself for providers that report pass@k flat.
    pass_at_k = reliability.get("with_skill", reliability) if "rate" not in reliability else reliability
    if skill_lift or pass_at_k:
        lines += ["", "## Incremental Value"]
        if "delta" in skill_lift:
            lines.append(
                f"- **Skill Lift:** {skill_lift['delta']:+.4f} "
                f"(with-skill {skill_lift.get('with_skill')}, "
                f"baseline {skill_lift.get('without_skill')})"
            )
        if "rate" in pass_at_k:
            k = pass_at_k.get("k", "?")
            lines.append(
                f"- **pass@{k}:** {pass_at_k['rate']} "
                f"({pass_at_k.get('passed_cases')}/{pass_at_k.get('total_cases')} cases)"
            )

    lines += ["", "## Domain Metrics"]
    for k, v in result.get("domain_metrics", {}).items():
        lines.append(f"- **{k}:** {v}")

    certification = result.get("certification") or {}
    failures = certification.get("failures") or []
    if failures:
        lines += ["", "## Certification Gate Failures"]
        for f in failures:
            lines.append(f"- {f}")

    lines += ["", "## Findings"]
    for f in result.get("findings", []):
        lines.append(f"- {f}")
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")
