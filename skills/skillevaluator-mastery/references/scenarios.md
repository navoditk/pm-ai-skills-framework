# Scenarios

Present one scenario at a time via `ask_user` with 4 choices. Award +30 XP
for a correct diagnosis.

1. **"Tier 2 always says 'skipped', even though I set `ANTHROPIC_API_KEY`."**
   → Correct: Tier 2 needs a non-Anthropic embedding provider
   (`SKILL_EVAL_EMBEDDING_PROVIDER=openai` + `OPENAI_API_KEY`, or an
   OpenAI-compatible endpoint). Anthropic does not provide embeddings.
   (Module 3)

2. **"Our Tier 3 run reports the agent never used any tools, but I watched
   it call the shell tool repeatedly."**
   → Correct: possible agent-compatibility gap in the evaluator's
   tool-recognition heuristic — this repository hit exactly this with a
   shell tool that self-reports as `exec`. Read the evaluator's source
   before assuming the skill is broken. (Module 8)

3. **"A brand-new skill directory fails Tier 1 with an `author_format`
   error, and I did write an author."**
   → Correct: the author line is likely present but the `metadata:` block
   itself is missing from frontmatter — a real, observed failure mode.
   (Module 7)

4. **"Tier 1 flags `skill.yaml` and `CHANGELOG.md` as 'unexpected' files."**
   → Correct: non-blocking advisory; the schema check only expects a fixed
   allowed set of subdirectories in the skill root — move the files into
   one, or set `SKILL_EVAL_SCHEMA_ALLOWED_DIRS`. (Module 7)

5. **"Our judge model quietly matches whichever model the agent uses, and
   we never configured that."**
   → Correct: `SKILL_EVAL_JUDGE_MODEL` was never set, so the judge silently
   fell back to the agent's own model, coupling judge cost to agent cost.
   (Module 4)

6. **"A Tier 3 sandbox run can't find our repo's own tool bridge script."**
   → Correct: missing `--copy-repo` flag — an easy-to-forget operator error,
   not an evaluator bug. (Module 4)

7. **"We want a cheap way to validate Tier 3 wiring without spending $15-45
   per skill."**
   → Correct: a Haiku-tier "quick pass" is fast/cheap but is NOT a
   substitute for certification evidence — it compresses Skill Lift toward
   zero on both arms because the agent itself is weaker, not because the
   skill is worse. (Module 4)

8. **"Our Tier 4 grader script mines completed Tier 3 trial data, but a
   rerun of the identical command produced a different directory
   structure."**
   → Correct: this is a real, observed quirk — directory layouts can differ
   between runs of the same tool; defend against it rather than assume a
   fixed layout. (Module 5)
