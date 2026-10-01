---
name: skillevaluator-mastery
description: 'Interactive training for NVIDIA SkillEvaluator. Guided lessons, quizzes, scenario challenges, and a full reference covering all four evaluation tiers, install/CLI usage, skill package layout, report formats, and CI/CD integration. Say "skillevalexpert" to start.'
metadata:
  author: PM AI Team <pm-ai@example.com>
  version: 1.0.0
---

# SkillEvaluator Mastery (project-skill loader)

This file is a discovery loader. Coding agents find project skills in
different folders: Claude Code reads `.claude/skills/`, Codex reads
`.agents/skills/`, and GitHub Copilot reads both. An identical copy of this
loader sits in each.

The canonical skill, with its routing table, reference modules, scenarios,
and final exam, is `skills/skillevaluator-mastery/SKILL.md` in the
repository root. That is the copy this repository's NVIDIA SkillEvaluator
Tier 1 checks validate, so it is the single source of truth.

**When this skill is triggered:**
1. Read `skills/skillevaluator-mastery/SKILL.md` (relative to the repository
   root) and follow its instructions.
2. Resolve every `references/...` path it mentions as
   `skills/skillevaluator-mastery/references/...`, not relative to this
   loader.
3. Do not copy its content here; read the canonical file each time so edits
   to it are picked up.
