# Exploratory Analysis Annex (Tier 4)

These analyses are pre-specified but **not confirmatory**. Results inform follow-up hypotheses only.

## Included in v2 (tier 4)

1. **8×5 octant↔domain matrix** with Benjamini–Hochberg FDR (`exploratory/octant_domain_fdr.csv`)
2. **Adaptive +20 sessions** if ICC(3,1) < .70 on any domain (methodology §5.4) — flagged exploratory if triggered
3. **Item-by-item fallback** (N = 10) if batched truncation detected — contingency only
4. **Logprobs** — secondary channel if exposed by gateway; not primary analysis
5. **Legacy seven subset** — `analyze.py --legacy` for manuscript continuity

## Excluded from confirmatory claims

- Any post-hoc pairing not in `CSIV_OCTANT_FACET` or `CSIV_VECTOR_IPIP`
- Rank-order patterns discovered after data collection
- Cross-lab comparisons beyond descriptive tier distances

## Reporting rule

Exploratory findings appear in a separate Results subsection labeled **Exploratory (tier 4)** and do not update H-G confirmatory inference.
