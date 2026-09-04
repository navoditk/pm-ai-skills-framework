"""Thin, local CLI for the framework's implemented governance paths.

The CLI deliberately keeps NVIDIA-specific behavior in the adapter and makes
the boundary between offline checks and credentialed evaluation explicit.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

from framework.adapters.nvidia_skillevaluator import NvidiaSkillEvaluatorProvider, parse_nvidia_report_file
from framework.certification.check_ownership import check_skill
from framework.certification.check_similarity import main as similarity_main
from framework.certification.engine import decide
from framework.certification.profile_resolver import resolve_profile
from framework.schemas.validation import validate_skill_package

REPO_ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = REPO_ROOT / "policies" / "certification.yaml"


def _skill_dir(value: str) -> Path:
    path = Path(value).resolve()
    if not path.is_dir():
        raise argparse.ArgumentTypeError(f"skill directory does not exist: {value}")
    return path


def cmd_init(args: argparse.Namespace) -> int:
    target = Path(args.path)
    if target.exists() and any(target.iterdir()):
        print(f"refusing to initialize non-empty directory: {target}", file=sys.stderr)
        return 2
    target.mkdir(parents=True, exist_ok=True)
    name = target.name
    (target / "evals").mkdir()
    (target / "tests").mkdir()
    (target / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: Use when ...\nmetadata:\n  author: Team <team@example.com>\n---\n\n# {name}\n\n## Use when\n\nDescribe the requests this skill handles.\n\n## Do not use when\n\nDescribe out-of-scope requests.\n\n## Procedure\n\n1. Resolve the request and required evidence.\n2. Use only approved logical tools.\n3. State limitations and provenance.\n",
        encoding="utf-8",
    )
    (target / "skill.yaml").write_text(
        f"schema_version: 1\nskill:\n  id: pm.{name.replace('-', '.')}\n  name: {name}\n  version: 0.1.0\n\nownership:\n  business: replace-me\n  engineering: replace-me\n  domain_reviewer: replace-me\n\nclassification:\n  domain: replace-me\n  risk_level: informational\n\ndependencies:\n  tools: []\n\nevaluation:\n  dataset: evals/evals.json\n\ncertification: {{}}\n",
        encoding="utf-8",
    )
    (target / "evals" / "EVAL.md").write_text(
        f"# {name} evaluation guidance\n\nDescribe positive, negative, adversarial, and regression coverage.\n",
        encoding="utf-8",
    )
    (target / "evals" / "evals.json").write_text(
        json.dumps({"skill_name": name, "evals": []}, indent=2) + "\n", encoding="utf-8"
    )
    (target / "evals" / "config.yml").write_text("schema_version: 1\n", encoding="utf-8")
    print(f"initialized skill scaffold at {target}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    # `validate ./skills` is the documented library form; a path containing a
    # manifest is the documented single-skill form.
    targets = sorted(args.path.glob("*/")) if args.all or not (args.path / "skill.yaml").exists() else [args.path]
    if not targets:
        print(f"no skill packages found under {args.path}", file=sys.stderr)
        return 2
    failed = False
    for target in targets:
        errors = validate_skill_package(target)
        errors.extend(check_skill(target, require_manifest=True))
        if errors:
            failed = True
            print("\n".join(f"[FAIL] {e}" for e in errors))
        else:
            print(f"[OK] {target}: framework package checks passed")
        if args.tier1:
            provider = NvidiaSkillEvaluatorProvider(executable=args.evaluator)
            result = provider.validate(str(target))
            if not result.normalized["passed"]:
                failed = True
                print(f"[FAIL] {target}: NVIDIA Tier 1 validation failed\n{result.raw['stderr']}")
    return 1 if failed else 0


def cmd_similarity(args: argparse.Namespace) -> int:
    sys.argv = ["pmai-skills similarity", *[str(p) for p in args.paths]]
    return similarity_main()


def cmd_evaluate(args: argparse.Namespace) -> int:
    provider = NvidiaSkillEvaluatorProvider(executable=args.evaluator)
    result = provider.evaluate(str(args.path), args.profile)
    if result.raw["stdout"]:
        print(result.raw["stdout"])
    if result.raw["stderr"]:
        print(result.raw["stderr"], file=sys.stderr)
    return result.raw["returncode"]


def cmd_report(args: argparse.Namespace) -> int:
    report = parse_nvidia_report_file(
        args.input,
        skill_id=args.skill_id,
        skill_name=args.skill_name,
        skill_version=args.skill_version,
    )
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"wrote normalized report to {args.output}")
    return 0


def cmd_certify(args: argparse.Namespace) -> int:
    policy = yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))
    manifest = yaml.safe_load((args.path / "skill.yaml").read_text(encoding="utf-8"))
    profile_name, profile = resolve_profile(policy, manifest["classification"]["risk_level"])
    if args.metrics is None:
        print("certify requires --metrics JSON from a completed benchmark; live evaluation and policy decision are separate steps", file=sys.stderr)
        return 2
    metrics = json.loads(args.metrics.read_text(encoding="utf-8"))
    decision = decide(metrics, profile)
    print(json.dumps({"skill": manifest["skill"]["id"], "profile": profile_name, "status": decision.status, "failures": decision.failures}, indent=2))
    return 0 if decision.status == "PASS" else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pmai-skills", description="PM AI skill validation and evaluation tools")
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="create a skill package scaffold")
    init.add_argument("path")
    init.set_defaults(func=cmd_init)
    validate = sub.add_parser("validate", help="run offline framework checks")
    validate.add_argument("path", type=Path, nargs="?", default=Path("skills"))
    validate.add_argument("--all", action="store_true")
    validate.add_argument("--tier1", action="store_true", help="also invoke NVIDIA Tier 1")
    validate.add_argument("--evaluator", default=None)
    validate.set_defaults(func=cmd_validate)
    similarity = sub.add_parser("similarity", help="apply catalog similarity governance")
    similarity.add_argument("paths", type=Path, nargs="+")
    similarity.set_defaults(func=cmd_similarity)
    evaluate = sub.add_parser("evaluate", help="run NVIDIA Tier 3")
    evaluate.add_argument("path", type=_skill_dir)
    evaluate.add_argument("--profile", default="pr", choices=["pr", "certification", "release"])
    evaluate.add_argument("--evaluator", default=None)
    evaluate.set_defaults(func=cmd_evaluate)
    report = sub.add_parser("report", help="normalize a raw NVIDIA JSON report")
    report.add_argument("input", type=Path)
    report.add_argument("output", type=Path)
    report.add_argument("--skill-id", required=True)
    report.add_argument("--skill-name", required=True)
    report.add_argument("--skill-version", required=True)
    report.set_defaults(func=cmd_report)
    certify = sub.add_parser("certify", help="apply certification policy to completed metrics")
    certify.add_argument("path", type=_skill_dir)
    certify.add_argument("--profile", default="release", choices=["release", "certification"], help="release policy decision (risk level selects the actual policy profile)")
    certify.add_argument("--metrics", type=Path, help="JSON object of normalized metrics")
    certify.set_defaults(func=cmd_certify)
    return parser


def main() -> int:
    return args.func(args) if (args := build_parser().parse_args()).func else 2


if __name__ == "__main__":
    raise SystemExit(main())
