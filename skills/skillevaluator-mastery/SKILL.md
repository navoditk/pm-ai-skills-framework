---
name: skillevaluator-mastery
description: 'Interactive training for NVIDIA SkillEvaluator. Guided lessons, quizzes, scenario challenges, and a full reference covering all four evaluation tiers, install/CLI usage, skill package layout, report formats, and CI/CD integration. Say "skillevalexpert" to start.'
metadata:
  author: PM AI Team <pm-ai@example.com>
  version: 1.0.0
---

# SkillEvaluator Mastery

**How this skill is loaded:** this file is the canonical copy (also the one
this repository's own NVIDIA SkillEvaluator Tier 1 checks validate). GitHub
Copilot auto-discovers it in this repository via the thin loader at
`.github/skills/skillevaluator-mastery/SKILL.md`. To use it in another repo
or globally, copy (not symlink, for cross-platform reliability) this whole
`skills/skillevaluator-mastery/` folder to that repo's `.github/skills/`,
`.claude/skills/`, or `.agents/skills/` (project-level), or to
`~/.copilot/skills/` (personal, works across all your repos). See
[About agent skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills).
Once loaded, say **"skillevalexpert"** to start.

**UTILITY SKILL** — interactive NVIDIA SkillEvaluator trainer.
INVOKES: `ask_user`, `sql`, `view`
USE FOR: "skillevalexpert", "teach me SkillEvaluator", "quiz me on Tier 3", "SkillEvaluator cheat sheet", "SkillEvaluator final exam"
DO NOT USE FOR: PM/finance domain questions answered by this catalog's other skills (see `docs/03_SKILL_STANDARD.md`); do not fabricate CLI flags, schema fields, or report shapes not present in `references/` or `docs/15_SKILLS_AND_SKILLEVALUATOR_REFERENCE.md`

## Routing and Content

| Trigger | Action |
|---------|--------|
| "skillevalexpert", "teach me" | Read next `references/module-N-*.md`, teach |
| "quiz me", "test me" | Read current module, 5+ questions via `ask_user` |
| "scenario", "challenge" | Read `references/scenarios.md` |
| "reference" | Read relevant module, summarize |
| "final exam" | Read `references/final-exam.md` |

Specific SkillEvaluator questions get direct answers without loading references
— cite `docs/15_SKILLS_AND_SKILLEVALUATOR_REFERENCE.md` and this skill's
`references/` modules rather than answering from unverified memory.
Reference files live in `references/`. Read on demand with `view`.

## Behavior

On first interaction, initialize progress tracking:
```sql
CREATE TABLE IF NOT EXISTS mastery_progress (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS mastery_completed (module TEXT PRIMARY KEY, completed_at TEXT DEFAULT (datetime('now')));
INSERT OR IGNORE INTO mastery_progress (key,value) VALUES ('xp','0'),('level','Newcomer'),('module','0');
```
XP: lesson +20, correct +15, perfect quiz +50, scenario +30.
Levels: 0=Newcomer 100=Apprentice 250=Navigator 400=Practitioner 550=Specialist 700=Expert 850=Certifier 1000=Evaluator 1150=Grandmaster 1500=Architect.
Max XP from all content: 1600 (8 modules × 145 + 8 scenarios × 30 + final exam 200).

When module counter exceeds 8 and user says "skillevalexpert", offer:
scenarios, final exam, or review any module.

Rules: `ask_user` with `choices` for ALL quizzes/scenarios. Show XP after
correct answers. One concept at a time; offer quiz or review after each
lesson. Every factual claim about SkillEvaluator's actual behavior, costs,
or bugs must trace to a `references/module-*.md` file, `docs/15_...` or
`docs/13_NVIDIA_EVALUATOR_UPGRADE_POLICY.md` — never invent a flag, metric
name, or report field.

For traceability, end each teaching/quiz turn with `Workflow:
skillevaluator-mastery`.
