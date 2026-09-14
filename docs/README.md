# PM AI Skills Framework — Documentation Portal

Welcome to the central documentation portal for the PM AI Skills Quality & Certification Framework. Use the interactive tools or path routes below to navigate directly to the material relevant to your role.

> 🌐 **Public Web Curriculum**: [GitHub Pages Site](https://navoditk.github.io/pm-ai-skills-framework/)  
> 📄 **Single-File HTML Artifact**: [skillevaluator-mastery-standalone.html](https://navoditk.github.io/pm-ai-skills-framework/skillevaluator-mastery-standalone.html)  
> 🤖 **Interactive Copilot Agent Skill**: Say **`skillevalexpert`** in any Copilot CLI session inside this checkout

---

## 🎯 Pick Your Path

Find the shortest reading path based on your immediate objective:

| Goal | Recommended Sequence | Cost / Prerequisites |
|---|---|---|
| **Master NVIDIA SkillEvaluator from scratch** | [`16_MASTERY`](16_SKILLEVALUATOR_MASTERY.md) ➔ [`15_REFERENCE`](15_SKILLS_AND_SKILLEVALUATOR_REFERENCE.md) | Free (Offline) |
| **Run a local 5-minute zero-credential test** | [`00_TUTORIAL`](00_TUTORIAL.md) | Free (Offline) |
| **Adopt this framework in another repository** | [`11_QUICKSTART`](11_QUICKSTART_FOR_CONSUMERS.md) ➔ [`06_ADOPTION`](06_ADOPTION_GUIDE.md) | Free (Offline) |
| **Understand purpose & architecture** | [`14_EXECUTIVE_SUMMARY`](14_EXECUTIVE_SUMMARY_AND_WALKTHROUGH.md) ➔ [`02_TARGET_ARCHITECTURE`](02_TARGET_ARCHITECTURE.md) | Reading |
| **Author, evaluate, or certify a skill** | [`03_SKILL_STANDARD`](03_SKILL_STANDARD.md) ➔ [`12_WORKFLOW`](12_END_TO_END_SKILL_WORKFLOW.md) ➔ [`04_CERTIFICATION`](04_EVALUATION_AND_CERTIFICATION.md) | Tier 3 requires Docker & API Keys |
| **Review benchmark evidence & roadmap** | [`10_ROADMAP`](10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md) ➔ [`EVIDENCE_INDEX`](EVIDENCE_INDEX.md) | Reading |

---

## 📚 Complete Document Catalog (00 — 16)

Every core document in this repository serves a specific operational or architectural role:

| Doc # | Title | Purpose | Cost / Prereqs |
|---|---|---|---|
| **00** | [First Tutorial](00_TUTORIAL.md) | Local zero-credential walkthrough | Free (Offline) |
| **01** | [Proposal](01_PROPOSAL.md) | Problem statement, framework goals, non-goals | Reading |
| **02** | [Target Architecture](02_TARGET_ARCHITECTURE.md) | 4-tier engine, governance layer, glossary | Reading |
| **03** | [Skill Standard](03_SKILL_STANDARD.md) | Skill package layout, schema, metadata rules | Reading |
| **04** | [Evaluation & Certification](04_EVALUATION_AND_CERTIFICATION.md) | Risk levels, policy profiles, metric thresholds | Reading |
| **05** | [Implementation Plan](05_IMPLEMENTATION_PLAN.md) | Technical phase breakdown | Reading |
| **06** | [Adoption Guide](06_ADOPTION_GUIDE.md) | Multi-team rollout strategy | Reading |
| **07** | [GitHub Publishing](07_GITHUB_PUBLISHING.md) | Repository publishing & release strategy | Reading |
| **08** | [Demo & Acceptance Plan](08_DEMO_AND_ACCEPTANCE_PLAN.md) | Verification gates & acceptance criteria | Reading |
| **09** | [Reference & Resources](09_REFERENCES_AND_RESOURCES.md) | Academic papers, vendor links, industry standards | Reading |
| **10** | [Roadmap & Progress Tracker](10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md) | Canonical status tracker & milestone records | Reading |
| **11** | [Consumer Quickstart](11_QUICKSTART_FOR_CONSUMERS.md) | Step-by-step consumer setup (`pmai-skills.yaml`) | Free (Offline) |
| **12** | [End-to-End Skill Workflow](12_END_TO_END_SKILL_WORKFLOW.md) | Lifecycle from draft to certification | Tier 3 needs API Keys |
| **13** | [NVIDIA Upgrade Policy](13_NVIDIA_EVALUATOR_UPGRADE_POLICY.md) | Pinned versioning & vendor bug workarounds | Reading |
| **14** | [Executive Summary & Walkthrough](14_EXECUTIVE_SUMMARY_AND_WALKTHROUGH.md) | Standalone overview of verified outcomes | Reading |
| **15** | [SkillEvaluator Reference](15_SKILLS_AND_SKILLEVALUATOR_REFERENCE.md) | One-stop guide to NVIDIA framework & findings | Reading |
| **16** | [SkillEvaluator Mastery Tutorial](16_SKILLEVALUATOR_MASTERY.md) | Self-paced hands-on tutorial for all 4 tiers | Free (Offline) |

---

## 📌 Reading Rules

- The root [README](../README.md) is the high-level project narrative and reference summary.
- Read [`10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md`](10_DEVELOPMENT_ROADMAP_AND_PROGRESS.md) for current execution status rather than inferring state from historical milestone records.
- Read [`EVIDENCE_INDEX.md`](EVIDENCE_INDEX.md) before interpreting benchmark results as a certification decision.
- Historical `MILESTONE_*.md` files retain detailed experiment logs, but support rather than supersede the roadmap and evidence index.

---

## 🔗 Related Repository Resources

- 🛠️ [Framework Source (`framework/`)](../framework/) — Adapter, CLI, certification engine, and schema validators
- 📐 [Reference Skills (`skills/`)](../skills/) — 12 PM skills + 1 utility mastery skill
- 🎯 [Deterministic PM Graders (`graders/`)](../graders/) — Financial reconciliation, date match, and benchmark graders
- 📊 [Synthetic Data Pipeline (`synthetic_data_pipeline/`)](../synthetic_data_pipeline/) — Financial portfolio data generator
- 🔒 [Policies (`policies/`)](../policies/) — Risk-tiered certification and similarity policy definitions
- 📝 [Contributing Guide](../CONTRIBUTING.md) — Guidelines for adding skills, graders, or docs
