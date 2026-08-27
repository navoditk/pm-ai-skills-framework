# 11. Quickstart: Apply the Framework to Your Own Repository

This is the shortest path for a team that already has an Agent Skills repository.

## Step 1 — Add framework configuration

Create:

```text
pmai-skills.yaml
```

Example:

```yaml
framework_version: 1
skills_root: ./skills
profile: asset-management

evaluation:
  provider: nvidia-skillevaluator
  baseline_required_for_certification: true

similarity:
  use_central_catalog: true

graders:
  packages:
    - pmai_finance_graders

reporting:
  json: true
  markdown: true
  html: true
```

## Step 2 — Make each skill conform to the standard

Each skill should contain:

```text
SKILL.md
skill.yaml
evals/EVAL.md
evals/evals.json
```

Optional:
- scripts;
- references;
- custom grader;
- deterministic tests.

## Step 3 — Install the central framework

Target future usage:

```bash
pip install pmai-skills-framework
```

Pin an organization-approved version.

## Step 4 — Validate your skills

```bash
pmai-skills validate ./skills
```

This runs:
- organization schema checks;
- NVIDIA Tier 1 checks.

## Step 5 — Check for duplication

```bash
pmai-skills similarity ./skills/my-new-skill
```

The new skill is checked against the centrally published approved-skill catalog.

## Step 6 — Run a fast developer evaluation

```bash
pmai-skills evaluate ./skills/my-new-skill --profile pr
```

Review:
- discoverability;
- correctness;
- effectiveness;
- efficiency;
- security;
- domain metrics.

## Step 7 — Add domain cases and graders

If the skill makes quantitative financial claims, prefer deterministic graders.

Examples:
- attribution reconciliation;
- benchmark match;
- date match;
- official risk value;
- data provenance.

## Step 8 — Open a PR

The reusable GitHub workflow runs:
- schema;
- Tier 1;
- Tier 2;
- fast Tier 3;
- domain graders.

## Step 9 — Certification

For release:

```bash
pmai-skills certify ./skills/my-new-skill --profile release
```

Certification retains the without-skill baseline and measures Skill Lift.

## Step 10 — Publish evidence

Successful certification produces:
- normalized JSON;
- Markdown/HTML report;
- BENCHMARK.md;
- registry metadata.

---

# What you do NOT need to copy

Do not copy:
- NVIDIA adapter implementation;
- certification engine;
- common finance graders;
- report renderer;
- organization CI logic.

Those belong to the centrally versioned framework.

Your repo owns:
- its skills;
- its eval cases;
- optional specialized graders;
- local fixtures;
- ownership metadata.
