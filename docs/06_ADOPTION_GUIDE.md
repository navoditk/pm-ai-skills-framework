# 6. Adoption Guide: How Any Asset-Management Repository Uses the Framework

## 6.1 Intended user

A team should not need to understand SkillEvaluator internals.

They should need to understand only:
- the organization skill standard;
- their own domain;
- how to write eval cases;
- any domain-specific grader they own.

## 6.2 Minimal consuming repo

```text
my-domain-skills/
├── skills/
│   ├── skill-a/
│   └── skill-b/
├── pmai-skills.yaml
└── .github/workflows/skills-quality.yml
```

## 6.3 Repository configuration

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
  local_path: ./graders

reporting:
  json: true
  markdown: true
  html: true
```

## 6.4 Team workflow

```text
pmai-skills init <skill>
pmai-skills validate <skill>
pmai-skills similarity <skill>
pmai-skills evaluate <skill> --profile pr
pmai-skills report <skill>
```

For certification:

```text
pmai-skills certify <skill> --profile release
```

## 6.5 What the central platform provides

- skill schema;
- CLI;
- NVIDIA adapter;
- similarity governance;
- report normalization;
- common graders;
- finance graders;
- certification engine;
- GitHub Actions reusable workflow;
- benchmark format.

## 6.6 What the local team provides

- SKILL.md;
- business ownership;
- use-case-specific instructions;
- evaluation cases;
- domain-specific fixtures;
- optional specialist graders;
- local tool dependencies.

## 6.7 Why this scales

A risk team and a credit research team can use different skills and graders while sharing:
- the same lifecycle;
- the same benchmark contract;
- the same certification vocabulary;
- the same CI mechanism;
- the same duplicate-detection catalog.

## 6.8 Portability rule

No local repo should:
- parse raw NVIDIA results directly;
- hardcode NVIDIA CLI commands throughout application code;
- duplicate certification logic;
- redefine organization-wide score names.

All provider-specific logic lives behind the adapter.
