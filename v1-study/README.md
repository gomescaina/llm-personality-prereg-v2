# v1-study

Data-collection and analysis pipeline for the three-instrument LLM personality study (v2 protocol).

## Panel (21 models, N = 30 sessions each)

| Lab | Tier 1 | Tier 2 | Tier 3 |
|-----|--------|--------|--------|
| OpenAI | GPT-4o-mini | GPT-4o | GPT-4.1 |
| Anthropic | Claude Haiku 4.5 | Claude Sonnet 4.6 | Claude Opus 4.6 |
| Google | Gemini 2.5 Flash Lite | Gemini 2.5 Flash | Gemini 2.5 Pro |
| Meta | Llama 3.1 8B | Llama 3.1 70B | Llama 3.3 70B |
| Mistral | Mistral Small 3.2 24B | Mistral Medium 3.1 | Mistral Large |
| DeepSeek | V4 Flash | V3.2 | V4 Pro |
| Qwen | Qwen 2.5 72B | Qwen3 Max | Qwen3 235B A22B |

## Layout

```
v1-study/
  config.py           # 21-model panel, lab/tier metadata
  prompts.py          # verbatim instructions + system prompt
  run.py              # collection orchestrator
  analyze.py          # pre-registered analysis orchestrator
  load_sessions.py    # JSON → DataFrames
  psychometrics.py    # reliability, convergence, CSIV↔IPIP
  hypotheses.py       # H-A–H-H adjudication
  norms.py            # human-norm T-scores
  tests/              # Phase 5 validation suite
  outputs/            # sessions + analysis/
```

## Commands

```bash
pip install -r requirements.txt

# Collection (dry-run)
python run.py --full

# Collection (live — after OSF registration)
python run.py --full --run

# Analysis
python analyze.py --tag full
python analyze.py --tag full --hypotheses
python analyze.py --tag full --legacy

# Validation (Phase 5)
python -m pytest tests/ -v
```

## Pre-registration

1. Pedro sign-off on [methodology-v2.html](../methodology-v2.html) — done ([SIGNOFF.md](../docs/SIGNOFF.md))
2. Pass Phase 5: `python -m pytest tests/ -v`
3. Freeze at git tag `prereg-v2.0`; register on OSF ([docs/osf/DEPOSIT_CHECKLIST.md](../docs/osf/DEPOSIT_CHECKLIST.md))
4. Only then: `python run.py --full --run`

Estimated budget: **~$65–85** (630 sessions × 14 calls).
