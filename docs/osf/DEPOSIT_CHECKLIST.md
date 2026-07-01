# OSF Deposit Checklist

## Before registration

- [ ] Phase 5 tests pass: `cd v1-study && python -m pytest tests/ -v`
- [ ] Dry-run confirms 21 models: `python run.py --full`
- [ ] Pedro sign-off recorded: [../SIGNOFF.md](../SIGNOFF.md)

## Freeze

- [ ] Commit all changes
- [ ] Run `python scripts/prepare_freeze.py` (writes `FROZEN_COMMIT.txt`)
- [ ] Create git tag: `git tag -a prereg-v2.0 -m "Pre-registration freeze v2"`
- [ ] Export zip of repo at tag (exclude `outputs/full_*` session data if any)

## OSF project structure

1. **Registration** — paste from [01_REGISTRATION.md](01_REGISTRATION.md)
2. **Analysis plan** — upload [02_ANALYSIS_PLAN.md](02_ANALYSIS_PLAN.md)
3. **Hypotheses** — upload [03_HYPOTHESES.md](03_HYPOTHESES.md)
4. **Materials** — upload frozen `v1-study/` + `methodology-v2.html`
5. **Data dictionary** — [05_DATA_DICTIONARY.md](05_DATA_DICTIONARY.md)
6. **Deferred scope** — [04_DEFERRED_SCOPE.md](04_DEFERRED_SCOPE.md)
7. **Exploratory annex** — [07_EXPLORATORY_ANNEX.md](07_EXPLORATORY_ANNEX.md)
8. **Limitations** — [08_LIMITATIONS.md](08_LIMITATIONS.md)

## After registration timestamp

- [ ] Run `python run.py --full --run` (~$65–85)
- [ ] Run `python analyze.py --tag full`
- [ ] Upload session JSON + `outputs/analysis/full/` to OSF

## Do not

- Collect full data before OSF registration is timestamped
- Report tier-4 exploratory results as confirmatory
- Bundle deferred studies (macrothemes, behavior, visibility) into this registration
