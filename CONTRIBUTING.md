# Contributing

Use the repository's local environment:

```bash
uv sync --extra dev
uv run pytest -q
uv run pmai-skills validate skills
```

For a skill change, update `SKILL.md`, `skill.yaml`, evaluation cases, and any
affected grader or regression tests. Do not commit credentials or raw live-agent
reports. If benchmark evidence changes, update the tracked `BENCHMARK.md` and
`BENCHMARK.json` records and explain the benchmark identity in the pull request.

Use the checklist in `.github/pull_request_template.md`. Tier 3 is expensive
and should be run deliberately, with model, evaluator, dataset, and cost recorded.
