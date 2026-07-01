# LLM Personality Study (v2)

Pre-registration-ready study: PID-5 + IPIP-NEO-300 + CSIV-64 across a 21-model OpenRouter panel.

## Key files

| Path | Purpose |
|------|---------|
| [methodology-v2.html](methodology-v2.html) | Full protocol for Pedro / OSF |
| [docs/SIGNOFF.md](docs/SIGNOFF.md) | Pedro approval (2026-07-01) |
| [docs/osf/](docs/osf/) | OSF deposit package |
| [v1-study/](v1-study/) | Collection + analysis scripts |

## Workflow

```
1. Pedro sign-off          → docs/SIGNOFF.md ✓
2. Implement & test        → v1-study/ (pytest)
3. Phase 5 validation      → python -m pytest v1-study/tests/
4. Freeze + OSF register   → see docs/osf/DEPOSIT_CHECKLIST.md
5. Data collection         → python v1-study/run.py --full --run
6. Analysis                → python v1-study/analyze.py --tag full
```

## Panel

Seven providers × three tiers = **21 models**, N = 30 sessions each, T = 1.0, English, sectioned-batched administration.

See [v1-study/config.py](v1-study/config.py) for frozen OpenRouter slugs.
