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
