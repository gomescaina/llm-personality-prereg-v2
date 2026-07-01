# prereg-v2-export

**Copia esta pasta inteira** para o GitHub (ou renomeia para o nome do repo).
Não precisas de mais nada fora daqui.

## Conteúdo

| Parte | O quê |
|-------|--------|
| `methodology-v2.html` | Protocolo completo (Pedro + OSF) |
| `docs/` | Sign-off, regras de qualidade, pacote OSF |
| `v1-study/` | Scripts de recolha + análise + testes |
| `personality-research-proposal-for-pedro.html` | Proposta original (contexto) |
| `manuscript_text.txt` | Paper de valores (contexto) |

## Antes do commit

```bash
cd v1-study
pip install -r requirements.txt
python -m pytest tests/ -v
python run.py --full
```

## Depois do commit

```bash
python scripts/prepare_freeze.py
git tag -a prereg-v2.0 -m "Pre-registration freeze v2"
```

Segue `docs/osf/DEPOSIT_CHECKLIST.md` para o OSF.
Só depois do timestamp OSF: `python run.py --full --run`

## O que NÃO vem aqui (de propósito)

- `outputs/*.json` — dados gerados depois da corrida
- `.pytest_cache/` — cache local
- API keys — nunca commitar
