# O que copiar para o repo GitHub (pré-registro v2)

Copia **a pasta inteira `LLMs`** (ou renomeia para `llm-personality-v2`) com esta estrutura.
Não precisas de ficheiros soltos na raiz do Desktop — um repo = uma pasta.

## Copiar (obrigatório)

```
LLMs/                          ← raiz do repo GitHub
├── README.md
├── methodology-v2.html
├── methodology-v1-redirect.txt
├── .gitignore
├── docs/
│   ├── SIGNOFF.md
│   ├── DATA_QUALITY_RULES.md
│   ├── COPY_FOR_GITHUB.md      ← este ficheiro (opcional mas útil)
│   └── osf/
│       ├── 01_REGISTRATION.md
│       ├── 02_ANALYSIS_PLAN.md
│       ├── 03_HYPOTHESES.md
│       ├── 04_DEFERRED_SCOPE.md
│       ├── 05_DATA_DICTIONARY.md
│       ├── 06_INSTRUMENTS/
│       │   └── prompts_note.txt
│       ├── 07_EXPLORATORY_ANNEX.md
│       ├── 08_LIMITATIONS.md
│       ├── DEPOSIT_CHECKLIST.md
│       ├── SIGNOFF.md
│       └── FROZEN_COMMIT.txt     ← atualizar depois do commit
└── v1-study/
    ├── README.md
    ├── requirements.txt
    ├── config.py
    ├── prompts.py
    ├── parser.py
    ├── client.py
    ├── scoring.py
    ├── run.py
    ├── analyze.py
    ├── load_sessions.py
    ├── psychometrics.py
    ├── hypotheses.py
    ├── norms.py
    ├── instruments/
    │   ├── __init__.py
    │   ├── pid5_items.csv
    │   ├── pid5_key.py
    │   ├── ipip_neo_300_items.csv
    │   ├── ipip_key.py
    │   ├── csiv_items.csv
    │   └── csiv_key.py
    ├── tests/
    │   ├── __init__.py
    │   ├── conftest.py
    │   ├── test_parser_scoring.py
    │   ├── test_analyze.py
    │   ├── test_run.py
    │   └── fixtures/
    │       ├── __init__.py
    │       └── generate_fixture.py
    ├── scripts/
    │   └── prepare_freeze.py
    ├── archive/                  ← referência histórica (macrothemes etc.)
    │   ├── macrothemes.csv
    │   └── pid5_validity_key.json
    └── outputs/
        └── .gitkeep              ← pasta vazia; dados vêm depois do OSF
```

## Não copiar

| Excluir | Porquê |
|---------|--------|
| `v1-study/outputs/*.json`, `outputs/analysis/` | Gerado por testes/corridas |
| `v1-study/.pytest_cache/` | Cache local |
| `**/__pycache__/` | Bytecode Python |
| `.env` / API keys | Segurança |

## Opcional (contexto, não entra no freeze OSF)

- `personality-research-proposal-for-pedro.html` — proposta antiga
- `manuscript_text.txt` — paper de valores

## Depois de colar no GitHub

```bash
cd LLMs   # ou o nome que deres
pip install -r v1-study/requirements.txt
cd v1-study
python -m pytest tests/ -v
python run.py --full
git init
git add .
git commit -m "Pre-registration freeze v2"
python scripts/prepare_freeze.py
git tag -a prereg-v2.0 -m "Pre-registration freeze v2"
git push -u origin main --tags
```

Depois: OSF seguindo `docs/osf/DEPOSIT_CHECKLIST.md`.
