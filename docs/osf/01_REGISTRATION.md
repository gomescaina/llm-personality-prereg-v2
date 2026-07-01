# OSF Registration Text (paste-ready)

## Title

Personality and interpersonal values in large language models: a three-instrument panel study (PID-5, IPIP-NEO-300, CSIV-64)

## Authors

Cainã [affiliation: meusvalores.app]  
Pedro [affiliation TBD]

## Abstract

We administer three English self-report instruments — PID-5 (pathological traits), IPIP-NEO-300 (normal-range Big Five), and CSIV-64 (interpersonal values circumplex) — to a fixed panel of 21 instruction-tuned LLMs (seven providers × three tiers) via OpenRouter at temperature 1.0. Each model completes N = 30 identical sectioned-batched sessions (14 API calls per session). We pre-register hypotheses on three-layer trait–value alignment, cross-instrument convergence, CSIV circumplex fit, role-norm signatures via PID-5 validity scales, and CSIV↔Big Five links at vector (confirmatory) and octant↔facet (secondary) levels. The panel is a descriptive cohort (N = 21 architectures), not a sample of all LLMs. Macrotheme values, behavioural criterion tasks, and public/anonymous administration are deferred to separate registrations.

## Design

- **Panel:** 21 models (see `v1-study/config.py` and methodology v2 Table 3)
- **Sessions:** 30 per model (630 total)
- **Administration:** Human-like English self-report; sectioned-batched blocks
- **Temperature:** 1.0
- **Gateway:** OpenRouter (slugs frozen at pre-registration)
- **Sign-off:** Pedro, 1 July 2026 (gomescaina@gmail.com)

## Hypotheses

See [03_HYPOTHESES.md](03_HYPOTHESES.md). Confirmatory: H-G only. Secondary: H-H. Descriptive: H-A–F.

## Analysis

See [02_ANALYSIS_PLAN.md](02_ANALYSIS_PLAN.md). Scripts: `v1-study/analyze.py` at frozen git commit.

## Materials

- Frozen `v1-study/` repository at tag `prereg-v2.0`
- [methodology-v2.html](../../methodology-v2.html)
- Instrument item lists in `v1-study/instruments/`

## Data availability

Session JSON and analysis outputs uploaded post-collection. No human participant data.
