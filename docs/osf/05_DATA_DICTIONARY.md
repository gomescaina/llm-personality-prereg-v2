# Data Dictionary

## Session file: `outputs/{tag}_{Model}_s{NN}.json`

| Field | Type | Description |
|-------|------|-------------|
| `model` | string | Display name from `config.PANEL` |
| `slug` | string | OpenRouter model slug |
| `session` | int | Session number 1..30 |
| `ts_start`, `ts_end` | ISO8601 | UTC timestamps |
| `cost_usd` | float | Estimated API cost |
| `tokens.prompt`, `tokens.completion` | int | Token counts |
| `instruments.{inst}.responses` | object | `{item_num: rating}` raw Likert |
| `instruments.{inst}.scored` | object | Scoring output (see below) |
| `instruments.{inst}.blocks[]` | array | Per-block API log |

## Block record (Option A logging)

| Field | Description |
|-------|-------------|
| `block`, `n_blocks`, `n_items` | Block index and size |
| `system_prompt` | Verbatim system message |
| `user_prompt` | Verbatim user message (full block) |
| `model_version` | OpenRouter model version string |
| `raw_reply_head` | First 300 chars of model reply |
| `dropped`, `out_of_range`, `n_parsed` | Parse diagnostics |
| `retry` | true if second attempt used |
| `ms`, `usage`, `cost_usd` | Performance |

## Scored: IPIP (`scored.domains`, `scored.facets`)

- Domains: `N`, `E`, `O`, `A`, `C` — raw sum (60–300)
- Facets: `N1`..`C6` — average (1–5)

## Scored: PID-5

- `facets.{name}.average` — 0..3 metric
- `domains_worksheet.{Negative Affect|...}.average`
- `validity.VRIN`, `ORS`, `PRD`, `flags.*`

## Scored: CSIV

- `octants.PA`..`NO` — mean 0..4
- `metrics.AGENTIC`, `COMMUNAL`, `R2`, `AMP`, `ELE`, `ANG`
- `z.*` — optional norm z-scores

## Analysis outputs: `outputs/analysis/{tag}/`

| File | Content |
|------|---------|
| `hypotheses.json` | H-A–H-H adjudication with tier tags |
| `reliability.csv` | α/ω by model × scale |
| `reliability_icc.csv` | ICC(3,1) by model × variable |
| `validity_summary.csv` | VRIN/ORS/PRD rates |
| `convergence.csv` | IPIP↔PID-5 per model |
| `csiv_circumplex.csv` | R², ANG, vectors |
| `human_norm_profiles.csv` | T/z norm profiles |
| `intra_lab_tiers.csv` | Tier distance by lab |
| `exploratory/octant_domain_fdr.csv` | Tier 4 only |

## Rating scales

- IPIP: 1–5 (Very Inaccurate → Very Accurate)
- PID-5: 0–3 (Very False → Very True)
- CSIV: 0–4 (not important → extremely important)
