# 2. Target Design & Architecture

## 2.1 Target architecture

```text
+------------------------------------------------------------------+
|                       PM / RESEARCH EXPERIENCE                    |
| Chat | Copilot | Canvas | Dashlet | Research Application          |
+-------------------------------+----------------------------------+
                                |
                                v
+------------------------------------------------------------------+
|                    AGENT / ORCHESTRATOR                           |
| intent | planning | skill selection | context | handoffs          |
+----------------------+----------------------+---------------------+
                       |                      |
                       v                      v
+--------------------------------+   +------------------------------+
| SKILL RUNTIME                  |   | POLICY / AUTHORIZATION       |
| discover | load | execute      |   | identity | entitlements      |
| version | instrument           |   | tool permissions | audit     |
+---------------+----------------+   +---------------+--------------+
                |                                    |
                +------------------+-----------------+
                                   v
+------------------------------------------------------------------+
|                       AGENTIC DATA PIPELINE                       |
| Stable logical tool contracts over governed data and analytics    |
|                                                                  |
| positions | portfolios | benchmarks | risk | market data          |
| attribution | research | scenarios | reference data               |
|                                                                  |
| Implementations may be APIs, MCP, RPC, Python, SQL, KDB, etc.     |
+------------------------------------------------------------------+

====================================================================

+------------------------------------------------------------------+
|                    SKILLS ENGINEERING PLANE                       |
|                                                                  |
| PM AI CLI / SDK                                                  |
|      |                                                           |
|      +--> NVIDIA SkillEvaluator Adapter                          |
|      |      +--> Tier 1 validation                               |
|      |      +--> Tier 2 dedup / similarity                       |
|      |      +--> Tier 3 live agent evaluation                    |
|      |                                                           |
|      +--> PM domain graders                                      |
|      +--> certification engine                                   |
|      +--> reporting / BENCHMARK evidence                         |
|      +--> registry publishing                                    |
+------------------------------------------------------------------+

====================================================================

+------------------------------------------------------------------+
|                      OBSERVABILITY PLANE                          |
| OpenTelemetry traces | evaluation scores | cost | latency | drift |
+------------------------------------------------------------------+
```

## 2.1a Layer-by-layer explanation

The diagram in 2.1 has two halves that run at different cadences: a runtime
half (top) that serves live PM users, and a skills-engineering half (bottom)
that develops and governs skills offline. They connect only through certified
skill packages and the shared Agentic Data Pipeline contracts — a live user
session never triggers an evaluation run, and an evaluation run never touches
production traffic.

**PM / Research Experience.** The surfaces a portfolio manager or researcher
actually uses — chat, copilot panes, canvas, dashlets. This layer has no
opinion about skills; it only renders what the agent layer produces.

**Agent / Orchestrator.** Owns intent recognition, planning, skill selection,
context management, and handoffs between skills. This is where "which skill
should handle this request" gets decided at runtime — a decision the
similarity/dedup governance in the skills-engineering plane exists to keep
tractable, by keeping the set of selectable skills small and non-redundant.

**Skill Runtime.** Discovers, loads, versions, and executes certified skill
packages, and instruments execution for the observability plane. The runtime
should refuse to load a skill that isn't resolvable to a certified
version/digest once the registry (2.6) is in place — it should never infer
certification merely from a skill folder's existence.

**Policy / Authorization.** Decides whether a specific operation a skill wants
to perform (read this portfolio, call this tool) is actually permitted for
this identity. This is deliberately separate from the skill's own
instructions — a skill describes *how* to do a job; authorization decides
*whether* this caller may.

**Agentic Data Pipeline.** See 2.2 — the stable logical-capability layer
skills depend on instead of physical data systems.

**Skills Engineering Plane.** Everything this repository actually builds: the
CLI/SDK, the NVIDIA adapter and its Tier 1/2/3 wrapping, PM domain graders,
the certification engine, reporting, and registry publishing. This plane
produces the certified artifacts the runtime consumes; it does not run inside
a live user request.

**Observability Plane.** Collects OpenTelemetry-style traces, evaluation
scores, cost, latency, and drift signals from both halves. Production
telemetry from here is what feeds regression-case creation (see
`docs/10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md`, Milestone 10) — a defect
observed in production should become a permanent eval case, not just a
one-off fix.

## 2.2 Why "Agentic Data Pipeline"

The term describes a governed layer that turns heterogeneous enterprise data and analytics into stable, agent-consumable capabilities.

A skill should request logical capabilities such as:

```text
portfolio.positions
performance.attribution
risk.factor_exposure
benchmark.positions
market.price_history
```

It should not encode infrastructure such as:

```text
query database X table Y
call vendor endpoint Z directly
```

This creates portability.

```text
Skill
  |
  v
Logical Tool Contract
  |
  v
Agentic Data Pipeline
  |
  +--> KDB
  +--> Snowflake
  +--> internal API
  +--> Bloomberg
  +--> research store
```

## 2.3 Responsibility boundaries

### Skills framework owns
- skill packaging standards;
- evaluation standards;
- domain graders;
- similarity governance;
- quality gates;
- certification;
- reporting;
- registry metadata.

### Agentic Data Pipeline owns
- data access;
- tool implementations;
- schemas;
- authentication integration;
- entitlements;
- lineage;
- data SLAs.

### Agent runtime owns
- routing;
- planning;
- context management;
- handoffs;
- user interaction.

### Policy layer owns
- whether a requested operation is permitted.

## 2.4 Evaluation provider abstraction

Do not let consuming repos import NVIDIA-specific report schemas.

```text
Framework Eval API
      |
      +-- NvidiaSkillEvaluatorProvider
      +-- FutureInternalProvider
      +-- AgentCoreProvider
      +-- OtherProvider
```

Normalized output:

```json
{
  "skill_id": "...",
  "version": "...",
  "generic_metrics": {},
  "domain_metrics": {},
  "skill_lift": {},
  "reliability": {},
  "certification": {}
}
```

## 2.4a NVIDIA version pinning and upgrade path

The adapter boundary in 2.4 exists primarily to make one fact true: **a
NVIDIA SkillEvaluator version upgrade is a contained, testable event, not a
library-wide breaking change.**

```text
Pinned NVIDIA version (exact version + commit)
        |
        v
framework/adapters/nvidia_skillevaluator.py   <-- only this file should need
        |                                          to change on upgrade
        v
Normalized PM AI result schema                <-- stays stable across
        |                                          evaluator versions
        v
Certification engine / reporting / registry   <-- never touched by an
                                                    evaluator version bump
```

If an evaluator upgrade requires changing certification logic, reporting, or
registry code — not just the adapter — that is a signal the adapter boundary
has leaked and should be tightened.

The full upgrade process (triggers, staged compatibility testing, rollback,
ownership, and the running log of known evaluator-compatibility gaps) is
defined in
[`docs/13_NVIDIA_EVALUATOR_UPGRADE_POLICY.md`](13_NVIDIA_EVALUATOR_UPGRADE_POLICY.md).
The Milestone 4 finding that the pinned evaluator's Tier 3 execution heuristic
does not recognize Codex's `exec` action (`docs/MILESTONE_4_PERFORMANCE_ATTRIBUTION.md`)
is the first real entry in that log, and is the motivating example for why
this policy exists rather than being handled ad hoc.

## 2.5 Benchmark identity

A benchmark result is valid only for a defined tuple:

```text
skill version
+ dataset version
+ agent
+ model
+ evaluator version
+ grader version
+ tool/data-pipeline fixture version
+ execution environment
```

Any material change marks evidence stale and triggers re-evaluation.

## 2.6 Runtime trust

Certified packages should eventually be signed and resolved by version/digest.

```text
Agent requests skill
      |
      v
Registry resolves certified version
      |
      v
Verify digest/signature
      |
      v
Load skill
```

The runtime should never infer certification merely from the existence of a skill folder.

## 2.7 Governance model

The skills-engineering plane exists to answer one operational question for a
growing PM skill library: **should this skill be built, and can this version
be trusted?** Three mechanisms carry most of that weight, in the order they
apply to a new skill:

1. **Ownership gate (pre-Tier-1).** A skill manifest without a real business
   owner and domain reviewer does not enter evaluation at all. This is
   enforced as a schema/CI check on `skill.yaml`, not a documentation
   convention — see `docs/03_SKILL_STANDARD.md` §3.8.
2. **Central catalog + Tier 2 similarity (pre-merge).** Every candidate skill
   is compared against one organization-wide approved-skill catalog before
   merge. This is the primary defense against the duplication problem in
   `docs/01_PROPOSAL.md` §1.1 — it is cheaper to block a near-duplicate at PR
   time than to detect it after both skills are in production.
3. **Risk-tiered certification rigor (pre-production).** Certification cost
   and strictness scale with the skill's declared `risk_level`
   (`informational` through `action` in `skill.schema.json`), so a summary
   skill and a decision-support skill are not held to the same evaluation
   budget or the same bar. See `docs/04_EVALUATION_AND_CERTIFICATION.md`.

A lightweight registry view — generated from the catalog and certification
results, not maintained by hand — is the visible artifact this produces: a
single place a PM engineer checks *before* building a new skill, to see
whether something similar already exists and who owns it.
