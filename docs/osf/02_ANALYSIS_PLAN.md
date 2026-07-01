# Analysis Plan (pre-registered)

## Analysis tiers

| Tier | Label | Analyses |
|------|-------|----------|
| 1 | Confirmatory | H-G: CSIV AGENTIC/COMMUNAL ↔ IPIP E, A, C (≥3/4 correct signs) |
| 2 | Secondary | H-H: 16 octant↔facet pairs (≥12/16 in ≥15/21 architectures); intra-lab tier distances |
| 3 | Descriptive | H-A–F; α/ω; ICC(3,1); validity distributions; IPIP↔PID-5 convergence; human-norm T-scores |
| 4 | Exploratory | 8×5 octant↔domain matrix with BH-FDR; adaptive +20 sessions; item-by-item fallback |

Tier 4 results are **not** used for confirmatory claims.

## §6.1 Reliability

- Cronbach's α and McDonald's ω per facet/domain/octant, per session; mean ± SD across 30 sessions
- ICC(3,1) on domain scores across sessions, per architecture
- PID-5 VRIN/ORS/PRD flag rates per architecture

**Implementation:** `psychometrics.reliability_report_from_items`, `reliability_icc_table`

## §6.2 IPIP ↔ PID-5 convergence

Five pre-registered domain mappings (Table 1 in methodology). Per architecture: Pearson r, sign check, panel summary.

**Implementation:** `psychometrics.convergence_panel_summary` → H-D

## §6.3 Cross-loadings (H-E)

Depressivity ↔ N1, N3; Suspiciousness ↔ E3, A2 (within architecture). Pass: ≥3/4 links in ≥15/21 models.

## §6.4 CSIV circumplex (H-F)

R², AMP, ELE, ANG per architecture. Pass: panel mean R² > .70 and communal angular displacement; fail if mean R² < .50.

## §6.5 Human-norm comparison

T-scores (PID-5, IPIP domains) and z-scores (CSIV octants) vs published norms.

**Implementation:** `norms.profile_norms_table`

## §6.6 CSIV ↔ Big Five

- **H-G (confirmatory):** architecture-level Spearman ρ, 4 vector↔domain pairings
- **H-H (secondary):** within-architecture Pearson r for 16 octant↔facet pairs

## H-A operational rule

Within each architecture (across 30 sessions), count predicted-sign Pearson correlations among:
- AGENTIC ↔ IPIP_E (+), AGENTIC ↔ IPIP_C (+), COMMUNAL ↔ IPIP_A (+), PID5_Antagonism ↔ IPIP_A (−)

**Coherent** if ≥3/4 correct. Architecture passes H-A if coherent. Panel pass: ≥15/21.

## Execution

```bash
python analyze.py --tag full
```

Outputs in `outputs/analysis/full/` with `ANALYSIS_REPORT.md` and tier-tagged `hypotheses.json`.
