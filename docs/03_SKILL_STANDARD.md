# 3. Skill Definition Standard

## 3.1 Required package

Every skill must contain:

```text
<skill>/
├── SKILL.md
├── skill.yaml
├── CHANGELOG.md
├── BENCHMARK.md              # generated after certification
├── references/
├── scripts/
├── evals/
│   ├── EVAL.md
│   ├── evals.json
│   ├── config.yml
│   └── grader.py             # optional
└── tests/
```

## 3.2 SKILL.md

`SKILL.md` is agent-consumable. Keep it concise enough for progressive disclosure.

Required content:
- name/description frontmatter;
- when to use;
- when not to use;
- required procedure;
- authoritative data/tool rules;
- ambiguity handling;
- temporal rules;
- output expectations;
- prohibited behavior.

## 3.3 skill.yaml

`skill.yaml` is platform-consumable.

Required fields:
- stable skill ID;
- semantic version;
- owner;
- domain;
- risk classification;
- dependencies;
- logical tools;
- required permission scopes;
- evaluation policy;
- certification policy.

See `framework/schemas/skill.schema.json`.

## 3.4 Evaluation ownership

Every production skill must own:
- capability cases;
- golden cases;
- negative discoverability cases;
- adversarial cases;
- regression cases.

Production incidents become regression cases.

## 3.5 Skill naming

Prefer business capability names:

Good:
- `performance-attribution`
- `risk-explanation`

Avoid:
- `use-risk-api`
- `tool-helper`
- `portfolio-prompt-v2`

## 3.6 Dependencies

Skills depend on logical tools, not physical data systems.

Example:

```yaml
dependencies:
  tools:
    - performance.attribution@v1
    - benchmark.positions@v1
```

## 3.7 Versioning

Use semantic versioning.

- PATCH — clarification/fix with no intended contract change.
- MINOR — backward-compatible capability extension.
- MAJOR — material behavioral/contract change.

Any version change triggers required benchmark policy.

## 3.8 Quality ownership

Every skill must have:
- business owner;
- technical owner;
- domain reviewer;
- risk class.

No owner -> no certification. **This is enforced as an automated pre-Tier-1
CI check on `skill.yaml`, not a review convention** — a manifest containing a
placeholder value (for example the literal string
`domain-owner-required`) fails validation before any evaluation cost is
spent. **Implemented 2026-08-31**: `framework/certification/check_ownership.py`
(unit-tested in `tests/test_ownership_gate.py`) runs as a real step in
`.github/workflows/skills-quality.yml`'s `tier1` job, before the Tier 1
`skillevaluator validate` call, against every skill changed in a PR. All 13
reference skills now carry real (synthetic-org) `domain_reviewer` values
instead of the placeholder — the check was verified to actually catch a
reverted placeholder before this was true.
