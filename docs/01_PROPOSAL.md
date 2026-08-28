# 1. Proposal: Enterprise Skills Quality & Certification Framework

## 1.1 Problem

An asset-management AI platform needs a scalable way to create and operate reusable skills without allowing quality to vary by team or repository.

The target state is not a collection of `SKILL.md` files. It is a **skills engineering system** that provides the equivalent of software engineering discipline for agentic capabilities:

- templates;
- schemas;
- dependency contracts;
- unit and integration tests;
- agent evaluations;
- quantitative quality scores;
- security checks;
- semantic duplicate detection;
- CI/CD gates;
- benchmark evidence;
- certification;
- versioning;
- observability;
- remediation guidance.

## 1.2 Proposed solution

Build a reusable framework that combines four evaluation tiers:

### Tier 1 — Construction, quality, and security
Use NVIDIA SkillEvaluator for deterministic skill-quality checks, security scanning, optional rubric evaluation, and PM-specific metadata validation.

### Tier 2 — Catalog hygiene
Use NVIDIA semantic deduplication to detect:
- repeated instructions inside a skill;
- redundant or highly similar skills across the library.

### Tier 3 — Behavioral evaluation
Use NVIDIA live-agent evaluation to test:
- Security;
- Correctness;
- Discoverability;
- Effectiveness;
- Efficiency;
- Skill Lift;
- pass@k reliability.

Always retain a without-skill baseline for certification runs so Skill Lift remains measurable.

### Tier 4 — Asset-management domain certification
Apply deterministic or domain-specific graders for:
- financial reconciliation;
- portfolio/benchmark consistency;
- temporal correctness;
- data provenance;
- currency consistency;
- portfolio coverage;
- authorization/tool-policy compliance;
- numerical grounding.

## 1.3 Why NVIDIA SkillEvaluator

NVIDIA solves a large portion of the generic problem:
- standardized skill validation;
- semantic similarity checks;
- local skill catalogs;
- live-agent sandbox execution through Harbor;
- with-skill versus without-skill comparison;
- multi-attempt evaluation;
- report artifacts;
- CI-friendly exit behavior.

The organization should **use NVIDIA as an engine but not expose NVIDIA as the enterprise contract**.

This creates a real dependency risk: an upstream NVIDIA release can change
evaluation behavior in ways that silently affect what "certified" means (a
concrete instance already occurred — see
`docs/13_NVIDIA_EVALUATOR_UPGRADE_POLICY.md` §13.6). The adapter boundary
described in `docs/02_TARGET_ARCHITECTURE.md` §2.4 and the staged upgrade
process in `docs/13_NVIDIA_EVALUATOR_UPGRADE_POLICY.md` are the accepted
mitigation for this risk — not a reason to avoid depending on NVIDIA.

## 1.4 Expected organizational benefits

### Consistency
Every skill is evaluated by the same lifecycle.

### Quality transparency
Teams can compare skills across common dimensions instead of relying on subjective demonstrations.

### Catalog control
Duplicate capabilities can be detected before merge.

### Reusability
Finance graders and test patterns become shared organizational assets.

### Faster onboarding
A team can adopt the framework through a package, configuration file, and reusable CI workflow.

### Model portability
A skill can be benchmarked across approved agents/models without changing the skill standard.

### Safer production adoption
A skill version is promoted only after hard gates and benchmark evidence succeed.

### Continuous improvement
Production defects are converted into permanent regression cases.

## 1.5 Non-goals

The framework does not:
- replace the agent runtime;
- replace authorization;
- replace the Agentic Data Pipeline;
- require every tool to use MCP;
- require one model provider;
- make NVIDIA a mandatory permanent runtime dependency;
- allow LLM graders to override deterministic financial truth;
- **become a generic, domain-agnostic skills platform for arbitrary use cases
  outside asset management.** The framework is deliberately scoped to PM/
  asset-management skill governance. Its value — a single approved-skill
  catalog, one shared certification vocabulary, and reusable finance graders
  — depends on staying scoped to this organization's skill library rather
  than generalizing across domains. A different domain adopting similar
  discipline should stand up its own instance rather than push this
  repository toward domain-neutral abstraction.

## 1.6 Deliverables

The reference implementation should include:

- 12 PM skills;
- 10 starter eval cases per skill;
- common skill schema;
- reusable NVIDIA adapter;
- 6+ finance graders;
- CI policies;
- benchmark/report normalizer;
- synthetic Agentic Data Pipeline;
- deliberate defect demonstrations;
- second-repository adoption example;
- GitHub publishing instructions.

## 1.7 Success criteria

The project succeeds when it empirically demonstrates:

1. **Quality is measurable** — all reference skills receive reproducible multidimensional results.
2. **Bad skills are caught** — intentionally degraded variants fail for understandable reasons.
3. **Redundancy is caught** — near-duplicate candidates are detected and governed.
4. **Skills add measurable value** — Skill Lift distinguishes useful skills from unnecessary ones.
5. **Domain errors are caught** — PM graders detect errors generic graders miss.
6. **The framework is portable** — another repo adopts the same controls with minimal configuration.
