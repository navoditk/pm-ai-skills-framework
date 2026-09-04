# 15. Skills & SkillEvaluator — One-Stop Reference

This document is the reference after completing the local tutorial. Start with
[`docs/00_TUTORIAL.md`](00_TUTORIAL.md) for a no-credentials exercise. This
document is the single place to point someone who asks "what are agent
skills, what does NVIDIA SkillEvaluator actually do, is it worth adopting,
and how do I get it running on my own repo?" It is written to stand alone —
combining the official upstream documentation with this project's own
hands-on findings (including the real bugs, costs, and gotchas discovered by
actually running it, not just reading its docs). Every claim about *this
project's* experience links to the evidence doc it came from; every claim
about the *external* ecosystem cites its source.

---

## 1. What SkillEvaluator is, and what it helps achieve

**NVIDIA SkillEvaluator** is an open-source, multi-tier framework for
evaluating AI agent artifacts — starting with agent skills — through
deterministic quality gates, semantic overlap detection, synthetic
evaluation-dataset generation, and live agent evaluation that measures how a
skill actually changes agent behavior
([NVIDIA docs](https://docs.nvidia.com/skills/skillevaluator);
[GitHub](https://github.com/NVIDIA/SkillEvaluator);
[NVIDIA technical blog](https://developer.nvidia.com/blog/evaluating-ai-agent-skill-performance-with-nvidia-skillevaluator/)).
Its support level is explicitly **Experimental** — community-supported on a
best-effort basis through GitHub Issues, no SLA. That matters: this project
found and worked around real bugs in it (§4 below), which is exactly the
kind of thing "Experimental" should lead you to expect.

**The problem it solves.** As a team accumulates AI skills (packaged
instructions that teach an agent to do a specific job), review-by-eyeball
stops scaling. SkillEvaluator answers, with numbers instead of opinions:

- Is the skill well-formed and safe? (Tier 1)
- Is it a near-duplicate of something that already exists? (Tier 2)
- Does having the skill actually change agent behavior for the better —
  and by how much? (Tier 3 — "Skill Lift": the with-skill score minus the
  without-skill score)
- Is the agent's own answer, with the skill, actually correct? (Tier 4 —
  domain-specific graders you write; SkillEvaluator supplies the harness,
  not the finance/legal/domain judgment)

**What it does not do:** it does not build skills for you, does not run
your production agent, does not manage credentials or a data pipeline, and
does not (by itself) decide certification policy — that is what this
project's own `framework/certification/engine.py` and
`policies/certification.yaml` add on top. See
`docs/02_TARGET_ARCHITECTURE.md` for how this project draws that line.

---

## 2. What our own tests actually show

Two skills in this repository have been taken all the way through the real
pipeline — live agent, live judge model, real Docker sandbox, real
certification policy. Both results are real, both are `FAIL`, and both
failures are precisely diagnosed rather than vague:

| Skill | Trials | Skill Lift | Certification | Why |
|---|---|---|---|---|
| Performance Attribution | 150 (75/75 both arms) | **+0.1253** | FAIL | Discoverability 0.8862 < 0.90 — a metric-scoping artifact (two eval cases whose *correct* behavior is to use no tools at all), not a real defect. Full trail: `docs/MILESTONE_4_PERFORMANCE_ATTRIBUTION.md`. |
| Portfolio Overview | 150 (75/75 both arms) | **+0.1316** | FAIL | The same discoverability shortfall (0.8942), independently corroborated by SkillEvaluator's own report — plus a newly discovered certification **policy gap**: a minimum metric (`reconciliation`) specific to one skill's grader auto-fails every other skill regardless of quality. Evidence: `skills/portfolio-overview/BENCHMARK.md`. |

Getting Performance Attribution's result required finding and fixing **four
real bugs** — not toy issues, actual blockers:

1. An agent-compatibility gap in the evaluator's Tier 3 execution heuristic
   (Codex's shell tool self-reports as `exec`, a string the evaluator's
   recognized-tool-name list didn't include).
2. A token-budget bug in the evaluator's own judge code (`max_tokens=1024`,
   no retry, on two of three judge functions — the third had already fixed
   the identical bug, the fix just wasn't propagated). Patched locally,
   tracked in `patches/`.
3. A missing `--copy-repo` CLI flag (this project's own operator error, not
   an evaluator bug) that left the sandbox unable to find the repo's own
   tool bridge.
4. API credit exhaustion mid-run, twice — a real operating-cost lesson, not
   a bug.

Beyond those two full certifications: **Milestone 6** deliberately introduced
six synthetic defects (vague description, duplicate skill, missing
derivatives, mismatched dates, weak/no-value skill, unauthorized data
source) and confirmed the framework catches five of them directly with real
evidence (a Tier 2 similarity score of 0.9468 on the deliberate duplicate;
existing grader regression tests for the domain-correctness defects) — see
`docs/MILESTONE_6_DELIBERATE_DEFECTS.md`. **Milestone 9** put a real Tier 1
check into CI (§6 below), and its first live run against a real PR passed
in 54 seconds.

**The honest summary: no skill in this catalog has cleared certification
outright yet**, and that is reported plainly rather than smoothed over —
see `docs/14_EXECUTIVE_SUMMARY_AND_WALKTHROUGH.md` for the full cold-read
walkthrough with an honest pros/cons assessment.

---

## 3. Feasibility: how hard is it to bring this to a real repo?

Grounded in this project's actual experience, not the marketing pitch:

**What's genuinely easy:**
- Tier 1 (schema, security, PII, quality scoring) is **entirely offline and
  free** — no API key, no Docker, no sandbox. `skillevaluator quality-check
  <skill>` and `skillevaluator validate <skill>` (Tier 1 only) run in
  seconds and are safe to run constantly, including in CI on every PR (this
  project's Milestone 9 job does exactly this).
- The pinned-version install is a single `pip`/`uv` command plus one line
  for an optional security scanner (§5).
- The tool is genuinely agent-agnostic at the CLI level — switching Tier 3's
  agent (Codex → Claude Code) was a one-flag change once the compatibility
  gap was diagnosed.

**What's genuinely hard, and costs real money and time:**
- **Tier 2 needs a working embedding provider**, and Anthropic does not
  provide one — you need `SKILL_EVAL_EMBEDDING_PROVIDER=openai` (or
  `nv_build` / an OpenAI-compatible endpoint) plus that provider's key, even
  if your Tier 3 agent is entirely Claude-based. This project only
  discovered this because Tier 2 silently reported "skipped" rather than
  erroring, on every run, until an OpenAI key was wired in.
- **Tier 3 is expensive and slow.** A full 25-case × 3-attempt × 2-arm
  matrix (150 trials) against `claude-sonnet-5` as both agent and judge
  took this project **30-55 minutes and roughly $15-45** per skill, and
  exhausted a modest prepaid API balance mid-run more than once in one day
  of iterative debugging. A cheap Haiku-tier "quick pass" (same 150 trials,
  weaker model) ran in ~12 minutes for ~$1-3 — useful for validating
  wiring, **not** a substitute for real certification evidence: Haiku's
  quick-pass numbers on this project's skills failed nearly every
  certification threshold that Sonnet cleared, because a weaker agent
  compresses Skill Lift toward zero on *both* arms, not because the skill
  itself is worse.
- **Tier 3 needs Docker** (or a local/cloud sandbox), the selected agent's
  own credentials, and — separately, and easy to forget — a judge-model
  credential and the `SKILL_EVAL_JUDGE_MODEL` override, or the judge
  silently falls back to whichever model the agent under test uses,
  coupling judge cost to agent cost for no reason.
- **The evaluator itself has real bugs** at "Experimental" support level —
  budget time to read its source when something looks wrong rather than
  assuming the skill is broken. Both real bugs this project found (§2) were
  root-caused by reading `skillevaluator`'s own vendored source, not by
  guessing.
- **Directory layouts can differ between runs of the same tool** — this
  project observed two different completed-trial directory structures
  across otherwise-identical invocations of `skillevaluator validate
  --agent-eval`; any custom post-hoc analysis script (like the Tier 4
  extraction pipeline in §7) needs to defend against that rather than
  assume a fixed layout.

**Bottom line:** Tier 1 is worth adopting almost unconditionally — it's
free and catches real, fixable structural problems (see the `SKILL.md`
schema/quality findings in every Tier 1 report this project has generated).
Tier 2 needs one extra credential decision. Tier 3 is a genuine cost/time
investment that should be reserved for skills where you actually want
certification-grade evidence, not run reflexively on every change — this is
exactly why this project's own Milestone 7 right-sizing decision limits full
Tier 3 depth to three flagship skills and keeps the other nine at Tier 1/2
only (`docs/10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md`).

---

## 4. Installing SkillEvaluator — step by step

### 4a. The general, upstream-recommended install

Per the [official installation guide](https://docs.nvidia.com/skills/skillevaluator/installation):

```bash
# Prerequisites: uv (or pip), Python 3.12 or 3.13, git; Docker only if you'll run Tier 3
uv tool install --python 3.13 "skillevaluator[all] @ git+https://github.com/NVIDIA/SkillEvaluator.git"

# Smaller footprints, if you don't need everything:
#   skillevaluator              -- Tier 1 only, no security scanning
#   skillevaluator[security]    -- + Bandit/pip-audit
#   skillevaluator[tier2,tier3] -- + dedup and live-agent eval

# Verify
skillevaluator --version
skillevaluator health-check
```

External security tools are installed separately to avoid dependency
conflicts:

```bash
brew install gitleaks                                       # or: go install / release binary
uv tool install git+https://github.com/NVIDIA/SkillSpector.git
```

### 4b. How this project pins and installs it (reproducible, recommended for any real adoption)

Installing `@main` is fine for exploration; for anything you intend to
certify against, **pin an exact commit** — SkillEvaluator's own release
notes and this project's Milestone 4 both found real, breaking behavioral
differences worth pinning against
(`docs/13_NVIDIA_EVALUATOR_UPGRADE_POLICY.md`):

```bash
uv venv .venv --python 3.13
uv pip install --python .venv/bin/python \
  'skillevaluator[all] @ git+https://github.com/NVIDIA/SkillEvaluator.git@009aa300be7925c7ba75760592baeb941cc29ba8'
uv pip install --python .venv/bin/python \
  'git+https://github.com/NVIDIA/SkillSpector.git@29b0dc8c39424e8e31ca055fa027adf8ba8f9650'
brew install gitleaks

# This project's local tracked patch for a real judge-truncation bug found
# in the pinned version -- see §2 and patches/README.md. Skip this line if
# you're pinning a version where NVIDIA has since fixed it upstream.
patch -p1 -d .venv/lib/python3.13/site-packages < patches/skillevaluator-0.2.1-judge-max-tokens.patch
```

Full reasoning for pinning (not just installing latest) and the upgrade
process when you do want to move the pin: `docs/13_NVIDIA_EVALUATOR_UPGRADE_POLICY.md`.

### 4c. Running each tier

```bash
# Tier 1 -- free, offline, seconds. Do this on every skill, constantly.
skillevaluator quality-check skills/my-skill
skillevaluator validate skills/my-skill --no-dedup

# Tier 2 -- needs an embedding provider (not Anthropic; see §3)
SKILL_EVAL_EMBEDDING_PROVIDER=openai OPENAI_API_KEY=... \
  skillevaluator similarity-check skills/ --type skill

# Tier 3 -- needs Docker, agent credentials, a judge model, and real time/$
SKILL_EVAL_LLM_PROVIDER=anthropic ANTHROPIC_API_KEY=... \
SKILL_EVAL_JUDGE_MODEL=claude-sonnet-5 \
  skillevaluator validate skills/my-skill \
  --agent-eval -a claude-code --agent-model claude-code=claude-sonnet-5 \
  --env-mode docker --copy-repo \
  --results-dir reports/my-skill-tier3 -r cli,json,markdown
```

`--copy-repo` and `SKILL_EVAL_JUDGE_MODEL` are both easy to forget and both
silently degrade your results rather than error loudly — see §3 and
`docs/MILESTONE_4_PERFORMANCE_ATTRIBUTION.md` for exactly how each one bit
this project the first time.

---

## 5. Repository and skill-package layout requirements

SkillEvaluator's Tier 1 schema check is opinionated about layout. Grounded
in real findings from every Tier 1 report this project has generated:

```text
skills/<skill-name>/
├── SKILL.md              # required
├── skill.yaml            # optional metadata this project's own governance layer reads
├── CHANGELOG.md          # optional
├── evals/
│   ├── config.yml        # harbor/tier3 run parameters, grading mode
│   ├── evals.json        # the eval case dataset
│   └── grader.py         # custom Tier 4 grading hook
└── tests/                # optional local unit tests for the grader
```

**`SKILL.md` frontmatter** — the schema and quality checks specifically
look for:

```yaml
---
name: my-skill                          # required; must match the directory name
description: One sentence, plus WHEN     # required; missing "when to use" language
                                          # is flagged as a discoverability finding
metadata:
  author: Team Name <team@example.com>   # required for the author_format check
  # tags: [finance, reporting]           # recommended, not required
# version: 1.0.0                        # recommended, not required
---
```

A missing `metadata:` block is a real, observed failure mode in this
project — several skills started without one and failed Tier 1's
`author_format` check until it was added.

**Recommended body sections** (each an advisory finding if missing, not a
hard fail, but each genuinely moves the quality score): `## Use when`,
`## Do not use when`, `## Procedure`, `## Instructions` or `## Usage`,
`## Examples`, prerequisites/limitations/troubleshooting sections.

**A real, observed quirk:** by default, Tier 1's schema check flags files
like `skill.yaml` and `CHANGELOG.md` sitting in the skill root as
"unexpected" — it expects the skill root to contain only `SKILL.md` plus a
small set of subdirectories (`agents/`, `assets/`, `config/`, `evals/`,
`references/`, `scripts/`, `tests/`, `tools/`). These are non-blocking
advisories in this project's configuration, not hard failures, but if you
want a clean report, either move such files into an allowed subdirectory or
set `SKILL_EVAL_SCHEMA_ALLOWED_DIRS`.

**`evals/evals.json` shape** (this project's convention, one case shown):

```json
{
  "skill_name": "my-skill",
  "evals": [
    {
      "id": "my-skill-001",
      "category": "explicit-positive",
      "prompt": "...",
      "expected_output": "...",
      "assertions": ["Do not fabricate facts.", "..."],
      "expected_skill": "my-skill"
    }
  ]
}
```

**`evals/config.yml`** (real, working example from this repo):

```yaml
schema_version: 1
harbor:
  n_attempts: 3
  pass_threshold: 0.80
  n_concurrent: 4
  agent_runtime_preflight: true
  base_image_mode: reuse
  pre_agent_setup:
    - >-
      if test -r /workspace/skills/my-skill/SKILL.md; then
        printf '%s\n' '# Required skill bootstrap' \
          'Before answering, read /workspace/skills/my-skill/SKILL.md with cat.' \
          > /workspace/AGENTS.md;
      fi
skill_workspace:
  mode: group
grading:
  mode: default_plus_custom
```

**`evals/grader.py`** is a thin hook — real Tier 4 domain logic belongs in a
shared, reusable module (this project's pattern: `graders/finance/*.py`,
composed from generic building blocks — see Milestone 8 in
`docs/10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md` for why reusability across
skills was made an explicit exit criterion):

```python
from graders.finance.my_skill import grade as grade_evidence

def grade(case, trajectory=None, expected=None):
    evidence = trajectory or expected or {}
    result = grade_evidence(evidence)
    return {"skill": "my-skill", "metrics": result["metrics"],
            "score": result["score"], "notes": []}
```

---

## 6. CI/CD integration

This project has a real, working example rather than a theoretical
recipe: `.github/workflows/skills-quality.yml`'s `tier1` job. It installs
the pinned evaluator (plus SkillSpector and gitleaks), diffs the PR against
its base SHA to find changed `skills/*` directories, and runs
`skillevaluator validate <skill> --no-dedup` on each — a non-zero exit
blocks the PR (given branch protection requires the check). Its first real
run, against this project's own PR #4, passed in 54 seconds. No API keys
required, because Tier 1 is LLM-free by default.

**Extending this to Tier 2 in CI** needs an embedding-provider secret
(`OPENAI_API_KEY` or equivalent) and a central approved-skill catalog to
diff new/changed skills against (`catalogs/` in this repo) — SkillEvaluator's
own docs describe this as a standard "merge gate with exit codes" pattern,
and mention a maintained GitHub Actions recipe as part of progressive
adoption.

**Extending to Tier 3 in CI** needs a Docker-capable runner, the target
agent's credentials, a separately-configured judge model, and — given the
real cost data in §3 — a firm opinion on *when* it runs. This project's own
recommendation, informed by real experience: keep Tier 3 **advisory, not
blocking**, on every PR (too slow and expensive to gate routine merges), and
reserve blocking Tier 3 runs for an explicit release/certification workflow
that runs on demand or on a schedule, not on every commit. See the
`similarity`, `tier3-fast`, and `domain-graders` jobs in this project's own
workflow file for the placeholder shape that pattern would fill in, and
`docs/10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md`'s Milestone 9 section for why
this project deliberately stopped at the Tier 1 gate rather than building
the full pipeline.

---

## 7. What this project built on top (reusable patterns)

Two pieces of this project's own code are worth knowing about if you're
adopting SkillEvaluator elsewhere, because they solve problems the tool
itself doesn't:

- **A normalized adapter** (`framework/adapters/nvidia_skillevaluator.py`)
  that translates NVIDIA's raw report JSON into a stable internal schema, so
  nothing downstream (certification logic, reporting) parses vendor-specific
  fields directly — this is what makes an evaluator version bump a
  contained, testable event instead of a library-wide breaking change. See
  `docs/02_TARGET_ARCHITECTURE.md`.
- **A free, post-hoc Tier 4 extraction pipeline**
  (`skills/*/evals/{tier3_trial_extractor,aggregate_tier4,generate_benchmark}.py`)
  that mines already-completed Tier 3 trial data on disk to compute
  domain-specific correctness metrics and hard gates (regression pass rate,
  authorization/permission-denial scanning) **without any new API calls** —
  built because SkillEvaluator's own Tier 4 is bring-your-own-grader, and
  because re-running live evaluation just to compute a metric you already
  have the raw data for is exactly the kind of unnecessary spend this
  project's real credit-exhaustion experience (§2) made a priority to avoid.

---

## 8. References

### What agent skills are, and the open standard

- [Anthropic: Agent Skills open standard, agentskills.io](https://www.unite.ai/anthropic-opens-agent-skills-standard-continuing-its-pattern-of-building-industry-infrastructure/) — published as an open spec on December 18, 2025; Microsoft, OpenAI, Atlassian, Figma, Cursor, and GitHub have adopted it.
- [agentskills/agentskills — the specification repo](https://github.com/agentskills/agentskills)
- [anthropics/skills — Anthropic's own 17 official skills, spec included](https://github.com/anthropics/skills)
- [Anthropic docs: Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/skills.md) — the SKILL.md format, progressive disclosure, loading behavior.
- [Simon Willison: Agent Skills](https://simonwillison.net/2025/Dec/19/agent-skills/) — independent, widely-cited explainer on why the format matters.
- [Strapi: What Are Agent Skills and How To Use Them](https://strapi.io/blog/what-are-agent-skills-and-how-to-use-them)

### MCP vs. Skills — a distinction worth understanding before designing a skill

- [MCP vs Agent Skills: Understanding the Difference](https://greenido.dev/2026/05/13/mcp-vs-skills-two-very-different-ways-to-extend-agents/) — the core framing: MCP is the agent's sensory/action interface to external systems; Skills are the agent's procedural memory (how to do a task once it has the tools).
- [The Agentic Stack: Agent Skills vs. MCP](https://medium.com/codetodeploy/the-agentic-stack-a-deep-dive-into-agent-skills-vs-model-context-protocol-mcp-9f378ce0db14)

### NVIDIA SkillEvaluator

- [Official documentation](https://docs.nvidia.com/skills/skillevaluator)
- [Installation guide](https://docs.nvidia.com/skills/skillevaluator/installation)
- [GitHub repository](https://github.com/NVIDIA/SkillEvaluator)
- [NVIDIA technical blog: Evaluating AI Agent Skill Performance with NVIDIA SkillEvaluator](https://developer.nvidia.com/blog/evaluating-ai-agent-skill-performance-with-nvidia-skillevaluator/)
- [Scan Agent Skills Before Installation](https://docs.nvidia.com/skills/scanning-agent-skills) — NVIDIA's own security-scanning guidance for third-party skills, relevant background for this project's Tier 1 security/PII checks.

### How other companies approach skills, tools, and agent extensibility

- **OpenAI** — [Agents SDK documentation](https://developers.openai.com/api/docs/guides/agents): Agents, Tools, Handoffs, Guardrails as the primitive vocabulary; tool/function calling as the mechanism closest to what Anthropic calls a "skill" plus MCP combined. [Python SDK](https://openai.github.io/openai-agents-python/) / [JS SDK](https://openai.github.io/openai-agents-js/guides/tools/).
- **GitHub** — [About agent skills (GitHub Docs)](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills): Copilot's own Agent Skills, interoperable with the same `anthropics/skills` format; GitHub documents six customization primitives (agents, skills, hooks, plugins, extensions, instruction files). [github/awesome-copilot skills collection](https://github.com/github/awesome-copilot/blob/main/docs/README.skills.md).

### Tutorials, courses, and a podcast episode

- [Anthropic Academy: Introduction to Agent Skills](https://anthropic.skilljar.com/introduction-to-agent-skills) — official, free course.
- [Anthropic Academy: Claude Code 101](https://anthropic.skilljar.com/claude-code-101) and [Claude Code in Action](https://anthropic.skilljar.com/claude-code-in-action).
- [Claude Agent SDK — Full Workshop, Thariq Shihipar (Anthropic), YouTube](https://www.youtube.com/watch?v=TqC1qOfiVcQ)
- ["Claude Skills explained: How to create reusable AI workflows" — How I AI podcast (Claire Vo), Apple Podcasts](https://podcasts.apple.com/us/podcast/claude-skills-explained-how-to-create-reusable-ai-workflows/id1809663079?i=1000732963909) / [written version, Lenny's Newsletter](https://www.lennysnewsletter.com/p/claude-skills-explained) — walks through building and using Skills in Claude Code and Cursor for recurring workflows.

### This project's own evidence, referenced throughout this document

| Topic | Document |
|---|---|
| Full architecture and the adapter/certification boundary | `docs/02_TARGET_ARCHITECTURE.md` |
| NVIDIA version pinning and upgrade process | `docs/13_NVIDIA_EVALUATOR_UPGRADE_POLICY.md` |
| Milestone 4 — first real certification attempt, all four bugs, in detail | `docs/MILESTONE_4_PERFORMANCE_ATTRIBUTION.md` |
| Milestone 5 — second certified skill, the reconciliation policy-gap finding | `docs/10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md`, `skills/portfolio-overview/BENCHMARK.md` |
| Milestone 6 — deliberate defect demonstration, in detail | `docs/MILESTONE_6_DELIBERATE_DEFECTS.md` |
| Full milestone status and the 2026-08-30 scope decision | `docs/10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md` |
| Standalone cold-read executive summary | `docs/14_EXECUTIVE_SUMMARY_AND_WALKTHROUGH.md` |
