from dataclasses import dataclass
from typing import Dict, List

@dataclass
class CertificationDecision:
    status: str
    failures: List[str]

def decide(metrics: Dict, policy: Dict) -> CertificationDecision:
    failures = []

    for name, required in policy.get("hard_gates", {}).items():
        actual = metrics.get(name)
        if isinstance(required, (int, float)):
            if actual is None or actual < required:
                failures.append(f"{name}: {actual} < {required}")
        elif actual != required:
            failures.append(f"{name}: {actual} != {required}")

    for name, minimum in policy.get("minimum_metrics", {}).items():
        actual = metrics.get(name)
        if actual is None or actual < minimum:
            failures.append(f"{name}: {actual} < {minimum}")

    return CertificationDecision(
        status="PASS" if not failures else "FAIL",
        failures=failures,
    )
