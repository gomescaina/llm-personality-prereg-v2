# Data quality and parsing rules (v2)

## Response parsing

- Expected format: numbered list, one line per item: `<item number> = <rating>`
- Alternatives accepted: `Item 5: 3`, `5 - 3`, markdown bullets (see `parser.py`)
- Out-of-range ratings: excluded from scoring; logged in block `out_of_range`
- Missing items: logged in block `dropped`; one automatic API retry if drift or drops detected
- Duplicate item numbers: last occurrence wins

## Session completeness

- **IPIP:** all 300 items required for full domain scores
- **PID-5:** APA proration rule — ≤25% missing per facet → prorate; >25% → facet not computable
- **CSIV:** all 64 items required for circumplex metrics (R², ANG, vectors)

## Parse failure handling

1. First API call per block
2. If format drift (`looks_like_list` fails) or dropped items → one retry with identical prompts
3. Session flagged in block log (`retry: true`) if retry used
4. Partial sessions retained; scoring uses available items only

## Validity flags (PID-5)

- VRIN ≥ 17 → inconsistent responding
- ORS ≥ 3 → overreporting
- PRD < 11 → underreporting (role-norm direction for H-C)

## Logging (Option A)

Each block in session JSON stores verbatim `system_prompt` and `user_prompt`, plus `model_version`, latency, tokens, and `raw_reply_head` (first 300 chars).
