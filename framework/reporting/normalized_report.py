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
    lines += ["", "## Domain Metrics"]
    for k, v in result.get("domain_metrics", {}).items():
        lines.append(f"- **{k}:** {v}")
    lines += ["", "## Findings"]
    for f in result.get("findings", []):
        lines.append(f"- {f}")
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")
