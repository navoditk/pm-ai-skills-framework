# 14. Executive Summary & End-to-End Walkthrough

This document is written to stand alone. Read only this file and you should
be able to explain what this project is, why it exists, what has actually
been built and proven versus what is still aspirational, and speak to its
pros and cons in a room. Every claim below points at real evidence in the
repository rather than asking you to take it on faith.

---

## Executive summary

A portfolio-management organization accumulates AI "skills" — packaged
instructions that teach an AI assistant to do a specific job, like explaining
why a portfolio underperformed its benchmark — faster than any team can
review by hand. Left ungoverned, that library fills with duplicates,
inconsistent quality, and skills nobody can prove are actually correct or
even useful. This project builds a **governance layer over one third-party
evaluation engine (NVIDIA SkillEvaluator)** that answers five questions before
any skill is trusted in production: is it well-built and safe, is it
different from what already exists, does it measurably help the agent, are
its financial claims correct, and can another team reproduce the verdict.

The project deliberately narrowed its own ambition partway through: it is
**not** trying to become a generic, domain-agnostic agent-skills platform. It
leans on NVIDIA to do the hard evaluation engineering and confines its own
code to four things a PM organization specifically needs — ownership
enforcement, duplicate detection, finance-specific correctness checks, and
risk-proportional certification cost.

As of this writing, the foundational architecture (Milestones 0-3) is built
and evidenced. The first real skill taken through the full pipeline
(Performance Attribution, Milestone 4) has been the proving ground for the
framework, and in the process **four distinct, real bugs were found and
fixed** — mostly not in this project's own code, but in the third-party
evaluator and in how it was being invoked — before a complete, clean 150-trial
result was achieved. That result shows a real, substantial Skill Lift
(+0.1253) and, when run through the project's own certification engine
against real policy, an honest **FAIL** verdict for two well-understood,
documented reasons — not a vague or fabricated pass. That debugging-and-honest-failure
trail is itself the best evidence that the governance model works: it caught
problems a demo would have hidden, and it refused to call an incomplete
result "certified." See
[Milestone 4](#milestone-4-the-proving-ground-with-four-real-bugs-found)
below for the full story, and `docs/10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md`
for the live status.

---

## The problem, in plain terms

Picture a large asset manager where different teams independently build AI
skills: "explain portfolio performance," "summarize risk," "compare to
benchmark." Within a year, without a shared process, you get:

- **Duplicates** — five teams build near-identical skills under different names.
- **Inconsistent quality** — some skills are rigorously tested, others are one
  person's untested prompt.
- **No way to compare** — nobody can say "skill A is better than skill B" with
  evidence, only demos.
- **Silent financial errors** — a skill that quietly reconciles a number
  wrong is a real business risk in front of clients or regulators.
- **No feedback loop** — production failures don't turn into regression tests,
  so the same mistake recurs.

This is a governance and quality-engineering problem, not a research problem.
The solution borrowed the discipline software engineering already has for
code — schemas, tests, CI gates, versioning — and applied it to skills.

## Why lean on NVIDIA instead of building this from scratch

NVIDIA SkillEvaluator already solves the generic 80% of this problem:
structural/security validation, semantic duplicate detection, and live-agent
sandboxed execution with a with-skill-vs-without-skill comparison ("Skill
Lift"). Building an equivalent engine from scratch would be years of work
duplicating something that already exists and is actively maintained.

The explicit design discipline (`docs/01_PROPOSAL.md` §1.3, §1.5;
`docs/02_TARGET_ARCHITECTURE.md` §2.4) is: **use NVIDIA as the engine, never
expose it as the contract.** A thin adapter
(`framework/adapters/nvidia_skillevaluator.py`) translates NVIDIA's raw output
into a stable internal schema, so nothing downstream — certification logic,
reports, a future registry — ever parses NVIDIA's format directly. This
matters concretely: it is what made the debugging trail in Milestone 4
possible to reason about and fix without destabilizing the rest of the
system, and it is why an evaluator version upgrade is a contained, testable
event rather than a rewrite (see
`docs/13_NVIDIA_EVALUATOR_UPGRADE_POLICY.md`).

## The governance model — what this project actually contributes

Given NVIDIA does the generic evaluation work, this project's own value-add
is narrow and specific, decided explicitly partway through the project (see
`docs/01_PROPOSAL.md` §1.5, "Explicit scope decision"; the project considered
and rejected generalizing into a domain-agnostic platform). Three mechanisms,
in the order they apply to a new skill:

1. **Ownership gate, before any evaluation runs.** A skill manifest without a
   real business owner and domain reviewer should not enter the pipeline —
   "no owner, no certification" (`docs/03_SKILL_STANDARD.md` §3.8). Currently
   documented but not yet enforced by an automated check (see
   [Honest gaps](#honest-gaps-and-open-risks) below).
2. **Central duplicate-detection catalog, before merge.** Every new skill is
   checked against an approved-skill catalog so two teams don't independently
   build the same capability under different names — the single highest-
   leverage control against the original duplication problem, and cheaper
   than catching it after both skills reach production.
3. **Risk-tiered certification cost, before production.** Not every skill
   needs the same evaluation budget. A skill's declared `risk_level`
   (`informational` through `action` in `skill.schema.json`) should
   proportionally scale how many live-agent attempts, how much case coverage,
   and whether finance-domain grading is a hard gate versus advisory
   (`docs/04_EVALUATION_AND_CERTIFICATION.md` §4.2a).

## Architecture, in one picture

```text
PM / Research experience  ->  Agent / Orchestrator  ->  Skill Runtime + Policy Layer
                                                              |
                                                              v
                                            Agentic Data Pipeline (logical tool contracts)
                                                              |
====================  skills engineering plane runs alongside, not inline  ====================
                                                              |
                                                              v
        Skill source  ->  NVIDIA SkillEvaluator (Tier 1/2/3)  ->  PM domain graders (Tier 4)
                                     |                                     |
                                     v                                     v
                          normalized adapter output  ---->  certification engine  ->  registry
```

Two boundaries carry most of the design's weight:

- **The Agentic Data Pipeline boundary.** Skills call stable logical
  capabilities (`portfolio.positions`, `performance.attribution`), never a
  physical database or vendor API directly
  (`docs/02_TARGET_ARCHITECTURE.md` §2.2). A local, deterministic
  implementation of this exists in `synthetic_data_pipeline/` so evaluation
  never depends on production systems (Milestone 3).
- **The NVIDIA adapter boundary**, described above.

Full layer-by-layer detail: `docs/02_TARGET_ARCHITECTURE.md`.

## The four-tier evaluation model

| Tier | What it checks | Who runs it |
|---|---|---|
| 1 — Construction/security | Package structure, metadata, security scanning | NVIDIA SkillEvaluator |
| 2 — Catalog hygiene | Duplicate/near-duplicate detection against an approved catalog | NVIDIA SkillEvaluator |
| 3 — Live behavior | Agent runs the skill with and without it available; measures Skill Lift, correctness, efficiency | NVIDIA SkillEvaluator (Harbor sandbox) |
| 4 — Domain truth | Deterministic finance checks: reconciliation, date consistency, provenance, coverage | This project's own graders (`graders/finance/`) |

Hard gates (security, ownership, regression pass rate) can never be
overridden by a high weighted average score
(`docs/04_EVALUATION_AND_CERTIFICATION.md` §4.3) — a design choice that
mirrors financial-controls thinking, not typical software QA.

---

## Milestone-by-milestone status

Authoritative live source: `docs/10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md`.
Summarized here for a cold read:

- **Milestone 0 (Blueprint) — DONE.** All design docs, 12 reference skill
  scaffolds, 120 starter eval cases, 6 starter finance graders.
- **Milestone 1 (Dev environment + NVIDIA smoke test) — DONE.** Pinned
  SkillEvaluator `0.2.1`, verified Tier 1 against a real skill (11/11 checks),
  completed one controlled Tier 3 sandbox run.
- **Milestone 2 (Normalized contracts) — DONE.** The adapter/schema boundary
  described above, with test coverage proving nothing downstream depends on
  NVIDIA's raw format.
- **Milestone 3 (Synthetic data pipeline) — DONE.** Deterministic local
  fixtures (portfolio, benchmark, attribution, risk, scenario, market data)
  so reference evaluations never touch production systems.
- **Milestone 4 (Performance Attribution vertical slice) — IN PROGRESS,**
  see the detailed walkthrough immediately below — this is where almost all
  of the project's real engineering rigor has been exercised so far.
- **Milestones 5-12 — NOT STARTED.** Three-skill slice, deliberate-defect
  demonstration, full 12-skill library, complete finance grader library,
  real CI/CD gates, remediation engine, cross-repo portability, registry.
  These are specified in detail (`docs/10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md`)
  but no code exists yet.

## Milestone 4: the proving ground, with four real bugs found

This is the part of the project that has actually been stress-tested against
a live agent, a live judge model, and a real Docker sandbox — and it is worth
walking through in detail, because the *debugging trail itself* is the
strongest evidence that this framework's discipline is real rather than
theatrical.

**The goal:** take one financial skill (explaining why a portfolio's
performance differed from its benchmark) all the way from source through
live-agent evaluation, domain grading, and a certification verdict.

**Bug 1 — an agent-compatibility gap, not a skill defect.** The first full
Tier 3 run (using Codex as the test agent) came back with `skill_efficiency`
pinned at `0.08` regardless of how well the agent actually used the skill.
Root-caused by reading the evaluator's own source: Codex's shell tool reports
itself as `exec`, a string absent from the evaluator's execution-recognition
list (which does recognize `bash`, `execute`, `exec_command`, `run`, `shell`,
`command`). Rather than patch around this, the fix was to switch the Tier 3
agent to Claude Code, which is a first-class supported agent in the same
pinned evaluator version and whose native tool names (`Bash`, `Read`, and a
dedicated `Skill` tool) are already recognized. Confirmed live: the same
fixture that exposed the Codex bug scored `skill_execution: 1.00`,
`efficiency: 1.00` with Claude Code.

**Bug 2 — a token-budget bug in the evaluator's judge, found by reading its
own source.** Running the full 25-case, 3-attempt matrix, ~25% of judge calls
(the ones that grade `accuracy`/`goal_accuracy`) failed with "Judge response
was not a valid JSON object" — enough to occasionally exhaust all 3 attempts
for a case and block score aggregation entirely. The evaluator's own source
revealed why: `judge_accuracy` and `_judge_goal_accuracy_custom` call the
judge with the library default `max_tokens=1024` and no retry, while a
sibling function (`judge_behavior_check`) in the *same file* already had this
exact truncation failure fixed (`max_tokens=4096` plus one retry, with a code
comment describing the identical symptom) — the fix was simply never
extended to the other two judges. This was fixed with a small, tracked local
patch (`patches/skillevaluator-0.2.1-judge-max-tokens.patch`) that mirrors
the evaluator's own already-proven fix, documented as a workaround pending an
upstream contribution (`docs/13_NVIDIA_EVALUATOR_UPGRADE_POLICY.md` §13.6).

**Bug 3 — a missing CLI flag, this project's own mistake.** With the judge
fixed, the full matrix finally produced complete, non-null scores — but ~80%
of trials showed the agent unable to find
`/workspace/repo/synthetic_data_pipeline/tool_cli.py` inside the sandbox, so
it correctly refused to fabricate numbers rather than answer. The evaluator
supports a `--copy-repo` flag that stages the surrounding repository into the
sandbox; it was simply never included in the run command. This is not a
defect in the framework or the evaluator — it is a reminder that a governed
pipeline still depends on the human (or agent) operating it correctly, and
that live-run evidence needs to be sanity-checked for environment confounds
before being read as a verdict about the skill itself.

**Bug 4 — API credit exhaustion, mid-run, twice.** Live evaluation is
expensive: each of 150 trials makes one agent call plus up to three judge
calls, all against Claude models. Two subsequent full-matrix attempts died
mid-run when the API key's prepaid balance ran out. After topping up, the
Tier 3 agent was switched from `claude-opus-5` to `claude-sonnet-5`
(alongside the judge, already decoupled onto Sonnet for cost reasons) —
cheap enough to finally complete a full matrix, and a genuine first data
point for the framework's own "model portability" goal.

**The final, clean result:** a complete 150-trial matrix scored 75/75 on
both arms with `execution_status: "succeeded"` — **Overall Skill Lift:
+0.1253** (0.9362 with-skill vs. 0.8109 baseline), clearing the required
0.10 minimum with real margin. Run through the project's own certification
engine against real policy, the first verdict was **FAIL** on seven counts:
discoverability narrowly missing its floor, plus six Tier 4/hard-gate
metrics Tier 3 alone can't produce. Closing that gap — done entirely by
mining the already-completed run's data on disk, at an explicit instruction
to spend no further API budget after today's repeated credit exhaustion —
extended Tier 4 domain grading from one hand-checked case to 14 of 25
(41 of 42 expected trials, a clean 1.0 on all six deterministic checks
everywhere it applied), computed all three missing hard gates from data
already collected (`regression_pass_rate: 1.0`, `authorization: pass` with
zero permission denials across all 150 trials, `data_provenance: 1.0`), and
precisely diagnosed the one remaining failure: discoverability's 0.8862
average is fully explained by two "ambiguous-input" cases whose *correct*
behavior is to use no tools at all — excluding just those, discoverability
is 0.9632, comfortably above the floor. **Final verdict: FAIL for exactly
one well-evidenced, well-understood reason**, not seven under-evidenced
ones — with a real, generated `skills/performance-attribution/BENCHMARK.md`
as the artifact of record, and the one open question (fix the metric, or
accept and document the exception) deliberately left to a human reviewer
rather than resolved by an agent mid-session. Full numbers and the complete
resolution trail are in `docs/MILESTONE_4_PERFORMANCE_ATTRIBUTION.md`.

---

## Pros and cons — an honest assessment

### Strengths

- **The vendor-abstraction discipline is real, not aspirational.** The
  adapter boundary was load-bearing during Milestone 4's debugging — every
  fix was made without touching certification logic, reporting, or anything
  downstream of the adapter.
- **The four-tier model with hard gates mirrors real audit/compliance
  thinking**, not typical software QA: a high average score can never
  override a failed security or provenance check.
- **The project's documentation practice is unusually honest.** The roadmap
  tracker records blockers, root causes, and exact evidence paths rather than
  polishing status. `docs/MILESTONE_4_PERFORMANCE_ATTRIBUTION.md` explicitly
  says "do not lower certification thresholds or infer success from the final
  response marker" — a real integrity commitment, not boilerplate.
- **The scope-narrowing decision was deliberate and is documented as a
  decision**, not a default. Choosing to stay PM-specific rather than
  generalize is defensible and keeps the project's actual differentiators
  (a shared catalog, shared certification vocabulary, reusable finance
  graders) coherent.

### Weaknesses and open risks

- **Single-vendor dependency, now demonstrated twice.** Two of the four bugs
  found in Milestone 4 were in NVIDIA's evaluator itself, not in this
  project's code. The adapter boundary limits *blast radius* but does not
  eliminate the dependency risk — this project is still exposed to whatever
  NVIDIA ships next, and local patches are a stopgap, not a permanent
  posture.
- **Live evaluation cost is real and was underestimated.** A single 150-trial
  certification matrix exhausted a prepaid API balance mid-run, twice, in one
  day. At Milestone 7 scale (12 skills, 300+ cases), this needs an explicit
  budget model, not ad hoc top-ups.
- **Evidence-extraction code can look complete while quietly assuming a
  uniform case shape.** The Tier 4 wiring done in Milestone 4 passed cleanly
  on one case and then immediately failed on a structurally different one
  for a reason that had nothing to do with the skill's correctness — the
  trajectory-to-evidence extractor was unconditionally populating
  "expected positions" regardless of whether a case's own prompt asked
  about positions at all (the underlying grader's own logic was already
  correct; the bug was one layer up, in what evidence was handed to it).
  Root-caused and fixed by grounding a per-case classification directly in
  the eval cases' own text rather than a guessed heuristic, with a
  regression test added. This is exactly the kind of gap the framework
  exists to catch, and it is a reminder that "the grader ran and returned a
  score" is not the same as "the evidence it graded was scoped correctly."
- **The governance mechanisms are still mostly specified, not built.** As of
  this writing: the central duplicate-detection catalog referenced in
  `pmai-skills.yaml` doesn't exist yet (only a skill-specific catalog does);
  the ownership-placeholder check described in `docs/03_SKILL_STANDARD.md`
  §3.8 is not automated — all 12 reference skills currently carry the literal
  placeholder `domain-owner-required`; the CI workflow
  (`.github/workflows/skills-quality.yml`) is mostly `echo` placeholders, not
  functioning gates; and the `pmai-skills` CLI described throughout the
  README and adoption docs does not exist as code. None of this is hidden —
  it is tracked plainly in the roadmap — but a reader relying only on the
  README/adoption guide would form an overly advanced mental model of what's
  actually built.
- **Live-run evidence is expensive and slow.** A single 150-trial
  certification matrix took roughly an hour end to end in this session, and
  three separate runs were needed before a clean, unconfounded result was
  achieved. At the scale of Milestone 7 (12 skills, 300+ cases), this cost
  needs a real budget model — none exists yet.
- **Only one skill has been taken to this depth.** Performance Attribution is
  the sole proof point. The "framework works for multiple skill patterns"
  claim is Milestone 5's job, not yet demonstrated.
- **No cross-skill or library-scale testing exists.** Every evaluation so far
  tests one skill in isolation. A real production library will have an
  orchestrator choosing between many similar skills — an interaction/routing
  failure mode this framework does not yet evaluate for.

## What "certified" will mean once Milestone 4 closes

Once the corrected run's results are in, closing Milestone 4 requires:
normalizing the result through the PM AI adapter (not NVIDIA's raw format),
applying `policies/certification.yaml`'s hard gates and minimum-metric
thresholds, and generating `BENCHMARK.md` — an immutable, reproducible
evidence record tied to the exact skill version, dataset, agent, model, and
evaluator version used (`docs/02_TARGET_ARCHITECTURE.md` §2.5). A benchmark
becomes stale and must be rerun the moment any of those five things change —
including a NVIDIA version bump, per `docs/13_NVIDIA_EVALUATOR_UPGRADE_POLICY.md`.

## Where to look for more detail

| Question | Document |
|---|---|
| What are we actually trying to achieve? | `docs/01_PROPOSAL.md` |
| How is the system architected? | `docs/02_TARGET_ARCHITECTURE.md` |
| What must a skill package look like? | `docs/03_SKILL_STANDARD.md` |
| How is a skill scored and certified? | `docs/04_EVALUATION_AND_CERTIFICATION.md` |
| What's done, in progress, and next? | `docs/10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md` |
| How do we handle NVIDIA changing under us? | `docs/13_NVIDIA_EVALUATOR_UPGRADE_POLICY.md` |
| The full Milestone 4 evidence trail | `docs/MILESTONE_4_PERFORMANCE_ATTRIBUTION.md` |
| How would another team adopt this? | `docs/06_ADOPTION_GUIDE.md`, `docs/11_QUICKSTART_FOR_CONSUMERS.md` |
