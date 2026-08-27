# 7. GitHub Implementation & Publishing Guide

## 7.1 Create the repository locally

From the generated blueprint directory:

```bash
cd pm-ai-skills-framework-blueprint
git init
git checkout -b main
git add .
git commit -m "Initial PM AI skills quality framework blueprint"
```

## 7.2 Create an empty GitHub repository

Create a repository such as:

```text
pm-ai-skills-framework
```

Recommended initial visibility for organizational work:
- private.

Do not initialize the remote repo with a README if the local repo already contains one.

## 7.3 Add remote and push

```bash
git remote add origin git@github.com:<ORG>/pm-ai-skills-framework.git
git push -u origin main
```

HTTPS is also possible if that is the organization's standard.

## 7.4 Branch protection

Protect `main`.

Require:
- pull request;
- required review(s);
- Tier 1 quality job;
- PM schema job;
- unit tests;
- similarity job;
- domain grader job once mature;
- signed commits if organizational policy requires them.

Start Tier 3 as advisory, then make it blocking after evaluation stability is established.

## 7.5 Repository environments

Create environments such as:
- `eval-dev`;
- `eval-certification`.

Keep model/provider credentials in GitHub Actions secrets or the organization's secret manager.

Never put agent/model credentials in:
- `SKILL.md`;
- `skill.yaml`;
- `evals/config.yml`;
- committed `.env` files.

## 7.6 Recommended GitHub metadata

Add:
- CODEOWNERS;
- pull request template;
- issue templates for skill gaps and eval failures;
- Dependabot or organization equivalent;
- security scanning;
- tagged releases for framework versions.

## 7.7 Release model

Suggested tags:

```text
framework-v0.1.0
framework-v0.2.0
framework-v1.0.0
```

Skills maintain independent semantic versions in `skill.yaml`.

## 7.8 Publish framework for reuse

Once stabilized, package the reusable Python components as an internal package:

```text
pmai-skills-framework
```

and publish to the organization's approved package registry.

Consuming repositories should pin a compatible version.

## 7.9 Reusable workflows

Move CI logic into a centrally maintained reusable GitHub workflow when supported by organizational policy.

A consuming repo then calls the central workflow rather than copying it.

## 7.10 First GitHub milestone sequence

Milestone 1 — Framework skeleton  
Milestone 2 — 3 reference skills  
Milestone 3 — 12 reference skills  
Milestone 4 — finance graders  
Milestone 5 — certification + reports  
Milestone 6 — second repo adoption  
Milestone 7 — registry integration

## 7.11 Suggested PR sequence

Avoid one enormous initial PR.

1. repository contracts/docs;
2. provider adapter;
3. synthetic pipeline;
4. first skill;
5. first finance grader;
6. first end-to-end report;
7. remaining skills;
8. similarity catalog;
9. CI gates;
10. portability example.
