# CLI target interface

The framework should expose a thin stable command line:

```text
pmai-skills init
pmai-skills validate
pmai-skills similarity
pmai-skills evaluate
pmai-skills compare
pmai-skills certify
pmai-skills report
```

Provider-specific details stay in `framework/adapters/`.
