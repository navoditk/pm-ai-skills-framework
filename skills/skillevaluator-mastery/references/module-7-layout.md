# Module 7: Skill Package Layout

Teach these points one at a time, grounded in
`docs/15_SKILLS_AND_SKILLEVALUATOR_REFERENCE.md` §5.

## Required layout

```text
skills/<skill-name>/
├── SKILL.md              # required
├── skill.yaml            # optional metadata this repo's governance layer reads
├── CHANGELOG.md          # optional
├── evals/
│   ├── config.yml        # harbor/tier3 run parameters, grading mode
│   ├── evals.json        # the eval case dataset
│   └── grader.py         # custom Tier 4 grading hook
└── tests/                # optional local unit tests for the grader
```

## SKILL.md frontmatter Tier 1 actually checks

```yaml
---
name: my-skill                          # required; must match the directory name
description: One sentence, plus WHEN     # required; missing "when to use" language
                                          # is flagged as a discoverability finding
metadata:
  author: Team Name <team@example.com>   # required for the author_format check
---
```

A missing `metadata:` block is a **real, observed failure mode** — several
skills in this repository started without one and failed Tier 1's
`author_format` check until it was added.

## A real, observed quirk

By default, Tier 1's schema check flags files like `skill.yaml` and
`CHANGELOG.md` sitting in the skill root as "unexpected" — it expects the
root to contain only `SKILL.md` plus a small allowed set of subdirectories
(`agents/`, `assets/`, `config/`, `evals/`, `references/`, `scripts/`,
`tests/`, `tools/`). These are non-blocking advisories, not hard failures —
move such files into an allowed subdirectory or set
`SKILL_EVAL_SCHEMA_ALLOWED_DIRS` for a clean report.

## Recommended body sections

`## Use when`, `## Do not use when`, `## Procedure`, `## Instructions`/
`## Usage`, `## Examples`, prerequisites/limitations/troubleshooting — each
an advisory finding if missing, not a hard fail, but each genuinely moves
the quality score.

## Quiz (5+ questions, use ask_user with 4 choices each)

Ask about: the required frontmatter fields, the missing-metadata failure
mode, the allowed-subdirectory quirk, and recommended body sections.
