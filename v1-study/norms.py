"""Human norm comparison: T-scores and z-scores for scored variables.

Norm sources (methodology v2 §6.5):
- PID-5: US census-matched domain averages (2024 book appendix; T=50 at norm mean)
- IPIP-NEO-300: domain raw score norms (Johnson UK–Ireland approximate mid-band)
- CSIV-64: University of Idaho octant norms (from csiv_key.NORMS)
"""
from instruments import csiv_key

# PID-5 worksheet domain norm means on 0..3 average metric (approximate census norms).
PID5_DOMAIN_NORMS = {
    "Negative Affect": {"mean": 0.55, "sd": 0.25},
    "Detachment": {"mean": 0.45, "sd": 0.22},
    "Antagonism": {"mean": 0.35, "sd": 0.20},
    "Disinhibition": {"mean": 0.40, "sd": 0.22},
    "Psychoticism": {"mean": 0.30, "sd": 0.18},
}

# IPIP-NEO-300 domain raw score norms (mid adult band, approximate).
IPIP_DOMAIN_NORMS = {
    "N": {"mean": 138, "sd": 24},
    "E": {"mean": 138, "sd": 26},
    "O": {"mean": 138, "sd": 24},
    "A": {"mean": 156, "sd": 22},
    "C": {"mean": 144, "sd": 24},
}


def t_score(value, mean, sd):
    if value is None or sd == 0:
        return None
    return 50 + 10 * (float(value) - mean) / sd


def pid5_domain_tscores(domain_averages):
    """domain_averages: {domain: average 0..3}. Returns {domain: T}."""
    out = {}
    for dom, stats in PID5_DOMAIN_NORMS.items():
        v = domain_averages.get(dom)
        out[dom] = t_score(v, stats["mean"], stats["sd"]) if v is not None else None
    return out


def ipip_domain_tscores(domain_raws):
    out = {}
    for dom, stats in IPIP_DOMAIN_NORMS.items():
        v = domain_raws.get(dom)
        out[dom] = t_score(v, stats["mean"], stats["sd"]) if v is not None else None
    return out


def csiv_octant_zscores(octants):
    out = {}
    for o in csiv_key.OCTANT_ORDER:
        v = octants.get(o)
        if v is None:
            out[f"z_{o}"] = None
        else:
            out[f"z_{o}"] = (v - csiv_key.NORMS["M"][o]) / csiv_key.NORMS["SD"][o]
    return out


def profile_norms_table(per_model_df):
    """Build human-norm T/z profile rows for each architecture."""
    rows = []
    for _, row in per_model_df.iterrows():
        pid5_avgs = {d.replace("PID5_", ""): row.get(f"PID5_{d.replace('PID5_', '')}")
                     for d in PID5_DOMAIN_NORMS}
        pid5_avgs = {k: row.get(f"PID5_{k}") for k in PID5_DOMAIN_NORMS}
        ipip_raws = {k: row.get(f"IPIP_{k}") for k in IPIP_DOMAIN_NORMS}
        octants = {o: row.get(o) for o in csiv_key.OCTANT_ORDER}
        entry = {"model": row["model"], "lab": row.get("lab"), "tier": row.get("tier")}
        for k, v in pid5_domain_tscores(pid5_avgs).items():
            entry[f"T_PID5_{k}"] = v
        for k, v in ipip_domain_tscores(ipip_raws).items():
            entry[f"T_IPIP_{k}"] = v
        for k, v in csiv_octant_zscores(octants).items():
            entry[k] = v
        rows.append(entry)
    try:
        import pandas as pd
        return pd.DataFrame(rows)
    except Exception:
        return rows
