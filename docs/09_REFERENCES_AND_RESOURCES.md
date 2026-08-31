# 9. References & Resources

This document collects the external standards, frameworks, documentation, and implementation references that informed the PM AI Skills Quality & Certification Framework.

**For a narrative, one-stop treatment** — what agent skills and
SkillEvaluator actually are, what this project's own tests show, a
feasibility assessment, step-by-step install/run instructions, repo layout
requirements, CI/CD integration guidance, and curated tutorials/courses/a
podcast episode — see
[`docs/15_SKILLS_AND_SKILLEVALUATOR_REFERENCE.md`](15_SKILLS_AND_SKILLEVALUATOR_REFERENCE.md).
This document (09) stays a flat link catalog; document 15 is the guided
walkthrough.

The intent is to give engineers and reviewers a single starting point for understanding:
- Agent Skills packaging;
- NVIDIA SkillEvaluator;
- agent evaluation patterns;
- CI/CD quality gates;
- observability;
- guardrails;
- production evaluation.

---

## NVIDIA SkillEvaluator

### SkillEvaluator overview
https://docs.nvidia.com/skills/skillevaluator

Why it matters:
- defines the three-tier model;
- Tier 1 static/security validation;
- Tier 2 semantic deduplication;
- Tier 3 live-agent evaluation;
- Skill Lift;
- pass@k;
- report outputs.

### Quickstart
https://docs.nvidia.com/skills/skillevaluator/quickstart

Use for:
- first local run;
- understanding dependencies;
- validating installation.

### Tier 1 — Static and Security Validation
https://docs.nvidia.com/skills/skillevaluator/tier1-validation

Relevant concepts:
- quality-check;
- validate;
- PII;
- script linting;
- security scanning;
- optional LLM rubric evaluation.

### Tier 2 — Semantic Deduplication
https://docs.nvidia.com/skills/skillevaluator/tier2-deduplication

Relevant concepts:
- intra-skill duplication;
- inter-skill similarity;
- local catalog;
- exact duplicate / high similarity / similar classifications.

### Tier 3 — Live Evaluation
https://docs.nvidia.com/skills/skillevaluator/tier3-live-evaluation

Relevant concepts:
- with-skill vs without-skill;
- live agent execution;
- discoverability;
- effectiveness;
- efficiency;
- Skill Lift.

### Evaluation Datasets
https://docs.nvidia.com/skills/skillevaluator/eval-datasets

Use for:
- `evals.json`;
- EVAL.md;
- positive/negative cases;
- custom evaluation fixtures;
- Harbor integration.

### Agents & Sandboxes
https://docs.nvidia.com/skills/skillevaluator/agents-and-sandboxes

Use for:
- supported agent CLIs;
- Docker;
- Harbor;
- isolated execution.

### Reports & Results
https://docs.nvidia.com/skills/skillevaluator/reports

Use for:
- JSON;
- HTML;
- Markdown;
- trial results;
- Skill Lift;
- pass@k.

### CI Integration
https://docs.nvidia.com/skills/skillevaluator/ci-integration

Use for:
- merge gates;
- exit codes;
- progressive CI adoption;
- GitHub Actions patterns.

### CLI Reference
https://docs.nvidia.com/skills/skillevaluator/cli-reference

Use when implementing the provider adapter.
Pin the organization-approved SkillEvaluator version before relying on exact flags.

### BENCHMARK.md rollout
https://docs.nvidia.com/skills/skillevaluator/benchmark-rollout

Use for:
- generated benchmark evidence;
- freshness;
- rebenchmark triggers;
- publication decisions.

---

## Anthropic / Agent Skills

### Anthropic — Equipping agents for the real world with Agent Skills
https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills

Why it matters:
- SKILL.md model;
- progressive disclosure;
- skill discovery;
- supporting references/scripts;
- large skill-library context management.

### Agent Skills specification
https://agentskills.io/specification

Use as the portability baseline for skill packaging.

### Anthropic skills repository
https://github.com/anthropics/skills

Useful for:
- examples;
- spec history;
- skill patterns.

---

## OpenAI

### OpenAI Agents SDK
https://openai.github.io/openai-agents-python/

Relevant concepts:
- agents;
- tools;
- handoffs;
- guardrails;
- tracing.

The PM AI framework should remain compatible with Agents SDK as a possible runtime, but should not depend on it.

### OpenAI agent-building overview
https://openai.com/index/new-tools-for-building-agents/

Useful for understanding:
- agent/tool composition;
- tracing;
- guardrails;
- runtime architecture.

### OpenAI Guardrails
https://guardrails.openai.com/

Relevant for:
- separating business skill behavior from safety/policy controls;
- prompt-injection checks;
- output validation;
- custom guardrails.

---

## Microsoft

### Microsoft Agent Framework
https://learn.microsoft.com/en-us/agent-framework/

Useful as a reference for:
- agents;
- workflows;
- skills;
- tools;
- enterprise agent architecture.

### Agent Framework Evaluation
https://learn.microsoft.com/en-us/agent-framework/agents/evaluation

Relevant concepts:
- evaluation APIs;
- local evaluators;
- expected outputs;
- tool evaluation;
- workflow evaluation.

### Microsoft Foundry — Evaluate Agents
https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/evaluate-agent

Relevant concepts:
- evaluation datasets;
- acceptance thresholds;
- production evaluation;
- quality/safety criteria.

### Foundry quality gates
https://learn.microsoft.com/en-us/agent-framework/integrations/by-component/evaluation/microsoft-foundry

Useful as another industry reference for:
- evaluation in CI;
- managed evaluators;
- agent behavior evaluation.

---

## OpenTelemetry

### Semantic Conventions
https://opentelemetry.io/docs/specs/semconv/

### Semantic convention concepts
https://opentelemetry.io/docs/concepts/semantic-conventions/

Why it matters:
- common trace/metric/log naming;
- vendor-neutral observability;
- ability to send PM AI telemetry to multiple backends.

The target design should emit skill, agent, model, tool, latency, error, and evaluation information using an OpenTelemetry-compatible contract.

---

## AWS / Bedrock AgentCore

### Amazon Bedrock AgentCore documentation
https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/

Relevant concepts to review:
- agent evaluation;
- dataset evaluation;
- trace/tool evaluation;
- custom evaluators;
- production monitoring.

AgentCore is a potential production-evaluation provider when the target environment is AWS-centric. It should sit behind the PM AI evaluation-provider abstraction rather than become the skill standard.

---

## LangChain / LangSmith / OpenEvals

### LangSmith Evaluation
https://docs.langchain.com/langsmith/evaluation

### Pytest integration
https://docs.langchain.com/langsmith/pytest

Useful patterns:
- dataset-driven testing;
- regression experiments;
- developer-centric eval workflows;
- CI integration.

These are useful implementation references even if LangSmith is not the organization-wide production platform.

---

## Google

### Google Agents CLI Evaluation
https://google.github.io/agents-cli/guide/evaluation/

Useful concepts:
- eval generation;
- grading;
- compare;
- failure analysis;
- optimization.

This is a useful reference for the planned PM AI failure-clustering and remediation workflow.

---

## Design guidance for this repository

External frameworks should be used according to this hierarchy:

```text
Open standard / portable concept
        |
        v
PM AI organization contract
        |
        v
Provider adapters
        |
        +--> NVIDIA SkillEvaluator
        +--> AgentCore
        +--> Foundry
        +--> internal evaluators
```

The repository should avoid encoding provider-specific assumptions above the adapter layer.

---

## Recommended reading sequence

For a developer new to this project:

1. Anthropic Agent Skills overview
2. Agent Skills specification
3. NVIDIA SkillEvaluator overview
4. NVIDIA Tier 1
5. NVIDIA Tier 2
6. NVIDIA Tier 3
7. NVIDIA evaluation datasets
8. NVIDIA CI integration
9. NVIDIA reports / BENCHMARK
10. PM AI `docs/02_TARGET_ARCHITECTURE.md`
11. PM AI `docs/04_EVALUATION_AND_CERTIFICATION.md`
12. PM AI `docs/05_IMPLEMENTATION_PLAN.md`

For platform architects, additionally review:
- Microsoft Agent Framework evaluation;
- OpenTelemetry semantic conventions;
- AWS AgentCore evaluation;
- OpenAI Agents SDK / Guardrails.
