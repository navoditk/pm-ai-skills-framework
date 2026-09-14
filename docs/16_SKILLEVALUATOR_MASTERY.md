# 16. SkillEvaluator Mastery — A From-Scratch, Hands-On Tutorial

This is the from-scratch companion to
[`docs/15_SKILLS_AND_SKILLEVALUATOR_REFERENCE.md`](15_SKILLS_AND_SKILLEVALUATOR_REFERENCE.md).
Doc 15 is the reference to look things up in; this document is the
progressive, hands-on exercise to actually build the muscle memory —
scaffold a toy skill, watch each tier fire, break it on purpose, and read a
real report. It assumes zero prior SkillEvaluator experience.

An interactive, gamified version of this same material (lessons, quizzes,
scenario challenges, a final exam) is published publicly and updated automatically on every push:
- 🌐 **GitHub Pages Web Site**: [https://navoditk.github.io/pm-ai-skills-framework/](https://navoditk.github.io/pm-ai-skills-framework/)
- 📄 **Standalone Single-File HTML Artifact**: [skillevaluator-mastery-standalone.html](https://navoditk.github.io/pm-ai-skills-framework/skillevaluator-mastery-standalone.html)

It also lives as an agent skill at
[`skills/skillevaluator-mastery/`](../skills/skillevaluator-mastery/). If
you're using GitHub Copilot CLI (or another Copilot surface) inside a
checkout of this repository, it's auto-discovered via the project-skill
loader at `.github/skills/skillevaluator-mastery/SKILL.md` — just say
**"skillevalexpert"**. To use it elsewhere, copy the
`skills/skillevaluator-mastery/` folder to `.github/skills/`,
`.claude/skills/`, `.agents/skills/`, or `~/.copilot/skills/` in the target
location. This document is the self-paced, read-it-yourself version.

---

## 0. Before you start

You need: `uv` (or `pip`), Python 3.12/3.13, `git`. Everything through
step 3 below is free and needs no API key, no Docker, and no live model.
Steps 4+ are clearly marked with their real cost/credential requirements —
do not run them without reading the caveat first.

---

## Step 1 — Install Tier 1 only

```bash
uv tool install --python 3.13 "skillevaluator[all] @ git+https://github.com/NVIDIA/SkillEvaluator.git"
skillevaluator --version
skillevaluator health-check
```

If you only want Tier 1 (no security scanning), the plain `skillevaluator`
extra is enough — see `docs/15_...` §4 for all the install variants and why
this repository pins an exact commit instead of `@main`.

## Step 2 — Scaffold a toy skill from scratch

```bash
mkdir -p /tmp/my-first-skill/evals
```

Create `/tmp/my-first-skill/SKILL.md`:

```markdown
---
name: my-first-skill
description: Say hello in a specific format.
metadata:
  author: Your Name <you@example.com>
---

# My First Skill

## Use when

Use this skill when asked to greet someone.

## Procedure

1. Greet the user by name if given.
2. Otherwise greet generically.
```

This is intentionally minimal — you'll break it on purpose in Step 4.

## Step 3 — Run Tier 1 and read the report

```bash
skillevaluator quality-check /tmp/my-first-skill
skillevaluator validate /tmp/my-first-skill --no-dedup
```

Look at:
- The overall quality score and which dimensions it scored on.
- Any advisory findings about missing recommended sections (`## Do not use
  when`, `## Examples`, etc. — see `docs/15_...` §5 for the full list).
- Whether the security scan step ran (it needs `gitleaks`/SkillSpector
  installed separately — `docs/15_...` §4).

**Checkpoint:** you should see a passing schema check (the frontmatter has
`name`, `description`, and a `metadata.author`) but likely several advisory
quality findings, because the body is minimal.

## Step 4 — Break it on purpose, then fix it

Remove the `metadata:` block entirely and rerun `quality-check`. This is a
**real, observed failure mode** in this repository — the `author_format`
check fails outright, not just an advisory finding (`docs/15_...` §5). Put
the block back, then remove the `## Use when` section and rerun — this time
notice it's an advisory finding, not a hard failure. This distinction (hard
schema failure vs. advisory quality finding) is the single most useful
thing to internalize about Tier 1.

Now add a `skill.yaml` at the skill root with placeholder content and rerun
`quality-check` again — Tier 1's schema check may flag it as an "unexpected"
root file (`docs/15_...` §5); move it into an allowed layout, or note the
`SKILL_EVAL_SCHEMA_ALLOWED_DIRS` escape hatch, without treating it as a bug.

## Step 5 — Inspect a real report from this repository

Rather than running Tier 3 yourself (see the cost caveat in Step 7), read
an already-generated report:

```bash
ls reports/*.json
cat skills/portfolio-overview/BENCHMARK.md
```

Compare the raw JSON's shape (`agents`, `dimensions_with_skill`, `lift`,
`pass_at_k`, or `quality_summary` for Tier 1-only reports) against
`framework/adapters/nvidia_skillevaluator.py`'s `parse_nvidia_report` —
run this in a Python shell to see the normalized shape produced:

```bash
uv run python -c "
from framework.adapters.nvidia_skillevaluator import parse_nvidia_report_file
import json
result = parse_nvidia_report_file(
    'reports/skillevaluator-output-20260904020239.json',
    skill_id='pm.demo', skill_name='Demo', skill_version='0.0.0')
print(json.dumps(result, indent=2)[:2000])
"
```

**Checkpoint:** you should be able to say, in one sentence each, what the
raw NVIDIA shape looks like and what this repository's normalized adapter
produces from it — and why the distinction matters (`docs/15_...` §7).

## Step 6 — Understand Tier 2 without spending money

Tier 2 needs a working embedding provider that is **not** Anthropic. Rather
than configuring one, read `catalogs/skill-catalog.json`'s structure (an
`entries` list, each with an `embedding` vector and a `content_fingerprint`)
and `policies/similarity.yaml`'s governance actions
(`EXACT_DUPLICATE` → block, `HIGH_SIMILARITY` → advisory review). Then read
`framework/certification/check_similarity.py` to see how this repository
turns a raw similarity score into one of those actions.

## Step 7 — Understand Tier 3 without spending money (unless you choose to)

**Real cost warning, read before running anything here:** a full Tier 3
matrix in this repository's own experience took 30-55 minutes and roughly
$15-45 per skill (`docs/15_...` §2-3, `docs/MILESTONE_4_PERFORMANCE_ATTRIBUTION.md`).

Instead of running it, read the milestone doc above end-to-end. It walks
through: the exact command used, the four real bugs found (an
agent-compatibility gap, a judge truncation bug, a missing `--copy-repo`
flag, and API credit exhaustion), and how the final Skill Lift number
(+0.1253) was computed and interpreted. If and when you do choose to run a
real Tier 3 matrix, use the exact command in `docs/15_...` §4c, and budget
time, Docker, an agent credential, and a **separate** judge-model credential
via `SKILL_EVAL_JUDGE_MODEL`.

## Step 8 — Understand Tier 4 and certification, on top

Read `graders/finance/portfolio_overview.py` alongside
`skills/portfolio-overview/evals/grader.py` to see the thin-hook pattern,
then `policies/certification.yaml` and
`framework/certification/profile_resolver.py` to see how this repository
turns raw Tier 1-4 evidence into a pass/fail certification decision that is
explicitly independent of SkillEvaluator's own opinion (`docs/02_TARGET_ARCHITECTURE.md`,
`docs/04_EVALUATION_AND_CERTIFICATION.md`).

---

## Self-test checklist

Before considering yourself "SkillEvaluator-literate," you should be able
to answer, without looking anything up:

- [ ] What does each of the four tiers check, and which are free vs. costly?
- [ ] What's the difference between a schema failure and a quality finding?
- [ ] Why does Tier 2 need a non-Anthropic embedding provider?
- [ ] What does "Skill Lift" mean, and what does a real number (e.g.
      +0.1253) tell you?
- [ ] What are the three easy-to-forget Tier 3 requirements
      (`--copy-repo`, `SKILL_EVAL_JUDGE_MODEL`, judge vs. agent credential)?
- [ ] What's the difference between the raw NVIDIA report shape and this
      repository's normalized adapter output, and why does that boundary
      exist?
- [ ] Where does SkillEvaluator's job end and this repository's own
      certification logic begin?

For the gamified version of this same checklist (with quizzes, scenario
challenges, and a scored final exam), use
[`skills/skillevaluator-mastery/`](../skills/skillevaluator-mastery/).
