---
name: skillevaluator-mastery
description: 'Interactive training for NVIDIA SkillEvaluator. Guided lessons, quizzes, scenario challenges, and a full reference covering all four evaluation tiers, install/CLI usage, skill package layout, report formats, and CI/CD integration. Say "skillevalexpert" to start.'
metadata:
  author: PM AI Team <pm-ai@example.com>
  version: 1.0.0
---

# SkillEvaluator Mastery (project-skill loader)

This file exists only so GitHub Copilot (CLI, cloud agent, code review, IDE
agent mode) auto-discovers this skill from its project-skill path
(`.github/skills/`, per
[About agent skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills)).

The full, canonical skill — routing table, XP/leveling behavior, and all
eight reference modules, scenarios, and final exam — lives at
`skills/skillevaluator-mastery/SKILL.md` in this repository root. That path
is also the one validated by this repository's own NVIDIA SkillEvaluator
Tier 1 checks, so it must remain the single source of truth.

**When this skill is triggered:**
1. Read `skills/skillevaluator-mastery/SKILL.md` (repository-root relative)
   and follow its instructions exactly.
2. Resolve every `references/...` path it mentions as
   `skills/skillevaluator-mastery/references/...` (repository-root
   relative), not relative to this loader file.
3. Do not duplicate or re-derive its content here — always read the
   canonical file fresh so edits to it are picked up automatically.
