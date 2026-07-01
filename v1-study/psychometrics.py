"""Psychometrics: α, ω, ICC, convergência, CSIV↔IPIP, intra-lab.

ICC(3,1) é o do protocolo (§6.1); ICC(2,k) ficou como extra se precisarmos.
"""
try:
    import numpy as np
    import pandas as pd
    _HAS = True
except Exception:
    _HAS = False


def cronbach_alpha(items_df):
    """items_df: rows = cases, cols = items (numeric). Returns alpha or None."""
    if not _HAS:
        return None
    df = items_df.dropna()
    if df.shape[0] < 2 or df.shape[1] < 2:
        return None
    k = df.shape[1]
    var_items = df.var(axis=0, ddof=1)
    var_total = df.sum(axis=1).var(ddof=1)
    if var_total == 0:
        return None
    return (k / (k - 1)) * (1 - var_items.sum() / var_total)


def mcdonald_omega(items_df):
    """McDonald's omega via single-factor PCA approximation."""
    if not _HAS:
        return None
    df = items_df.dropna()
    if df.shape[0] < 10 or df.shape[1] < 3:
        return None
    try:
        corr = df.corr().values
        eigvals = np.linalg.eigvalsh(corr)
        eigvals = np.sort(eigvals)[::-1]
        lam2 = max(0.0, eigvals[0])
        k = df.shape[1]
        loading = np.sqrt(lam2 / k) if k else 0.0
        if loading >= 1:
            return None
        return (k * loading ** 2) / (k * loading ** 2 + k * (1 - loading ** 2))
    except Exception:
        return None


def icc_2_k(scores_matrix):
    """ICC(2,k) for absolute agreement. rows=cases, cols=sessions/raters."""
    if not _HAS:
        return None
    df = scores_matrix.dropna()
    if df.shape[0] < 2 or df.shape[1] < 2:
        return None
    try:
        import pingouin as pg
        long = df.reset_index().melt(id_vars="index", var_name="rater", value_name="score")
        long.columns = ["target", "rater", "score"]
        icc = pg.intraclass_corr(data=long, targets="target", raters="rater",
                                 ratings="score", nan="drop")
        row = icc[icc["Type"] == "ICC2k"]
        return float(row["ICC"].iloc[0]) if not row.empty else None
    except Exception:
        return _icc_2_k_manual(df)


def _icc_2_k_manual(df):
    n, k = df.shape
    grand = df.values.mean()
    BMS = k * df.mean(axis=1).var(ddof=1) if n > 1 else 0.0
    JMS = n * df.mean(axis=0).var(ddof=1) if k > 1 else 0.0
    EMS = (df.values - df.mean(axis=1, keepdims=True) - df.mean(axis=0, keepdims=True) + grand)
    EMS = (EMS ** 2).sum() / ((n - 1) * (k - 1)) if (n > 1 and k > 1) else 0.0
    num = BMS - EMS
    den = BMS + (k - 1) * EMS + k * (JMS - EMS) / n
    if den == 0:
        return None
    return num / den


def icc_3_1(scores_matrix):
    """ICC(3,1) — single measurement, absolute agreement (methodology §6.1)."""
    if not _HAS:
        return None
    df = scores_matrix.dropna()
    if df.shape[0] < 2 or df.shape[1] < 2:
        return None
    try:
        import pingouin as pg
        long = df.reset_index().melt(id_vars="index", var_name="rater", value_name="score")
        long.columns = ["target", "rater", "score"]
        icc = pg.intraclass_corr(data=long, targets="target", raters="rater",
                                 ratings="score", nan="drop")
        row = icc[icc["Type"] == "ICC3"]
        return float(row["ICC"].iloc[0]) if not row.empty else None
    except Exception:
        return None


def reliability_icc_table(session_df, score_cols, model_col="model", session_col="session"):
    """ICC(3,1) per architecture per domain-level score (sessions as raters)."""
    if not _HAS:
        return []
    rows = []
    for model, mdf in session_df.groupby(model_col):
        for col in score_cols:
            if col not in mdf.columns:
                continue
            vals = mdf[[session_col, col]].dropna()
            if vals.shape[0] < 2:
                continue
            mat = vals.set_index(session_col)[[col]].T
            icc = icc_3_1(mat)
            rows.append({"model": model, "variable": col, "icc_3_1": icc})
    return rows


def reliability_report_from_items(item_df, scale_map, model_col="model", session_col="session"):
    """α/ω per scale per architecture from long-format item data."""
    if not _HAS or item_df is None or item_df.empty:
        return []
    rows = []
    for model, mdf in item_df.groupby(model_col):
        wide = mdf.pivot_table(index=session_col, columns="item_num", values="raw")
        for scale_name, item_nums in scale_map.items():
            cols = [n for n in item_nums if n in wide.columns]
            if len(cols) < 2:
                continue
            sub = wide[cols].dropna(how="all")
            alphas, omegas = [], []
            for sess in sub.index:
                row = sub.loc[[sess]].dropna(axis=1)
                if row.shape[1] >= 2:
                    a, o = cronbach_alpha(row), mcdonald_omega(row)
                    if a is not None:
                        alphas.append(a)
                    if o is not None:
                        omegas.append(o)
            rows.append({
                "model": model,
                "scale": scale_name,
                "alpha_mean": float(np.mean(alphas)) if alphas else None,
                "alpha_sd": float(np.std(alphas, ddof=1)) if len(alphas) > 1 else None,
                "omega_mean": float(np.mean(omegas)) if omegas else None,
                "omega_sd": float(np.std(omegas, ddof=1)) if len(omegas) > 1 else None,
                "n_sessions": int(sub.shape[0]),
            })
    return rows


def cross_loading_check(session_df, model_col="model"):
    """H-E: Depressivity and Suspiciousness dual-loadings within architecture."""
    if not _HAS:
        return None
    checks = [
        ("Depressivity", "N1", "+"),
        ("Depressivity", "N3", "+"),
        ("Suspiciousness", "E3", "+"),
        ("Suspiciousness", "A2", "-"),
    ]
    results = {}
    models = session_df[model_col].unique()
    n_pass = 0
    for m in models:
        sub = session_df[session_df[model_col] == m]
        if len(sub) < 5:
            continue
        ok = 0
        detail = {}
        for pid_facet, ipip_facet, sign in checks:
            pc = f"PID5_{pid_facet}"
            if pc not in sub.columns or ipip_facet not in sub.columns:
                continue
            r = sub[pc].corr(sub[ipip_facet], method="pearson")
            good = _sign_ok(r, sign)
            detail[f"{pid_facet}<->{ipip_facet}"] = {"r": r, "sign_ok": good}
            if good:
                ok += 1
        passed = ok >= 3
        if passed:
            n_pass += 1
        results[m] = {"n_sign_ok": ok, "passed": passed, "detail": detail}
    return {"per_model": results, "n_pass": n_pass, "n_total": len(models)}


def exploratory_octant_domain_matrix(per_model_df):
    """Tier 4: 8 octants × 5 IPIP domains with BH-FDR q-values."""
    if not _HAS:
        return None
    from instruments.csiv_key import OCTANT_ORDER
    domains = ["N", "E", "O", "A", "C"]
    rows = []
    pvals = []
    for oct in OCTANT_ORDER:
        for dom in domains:
            if oct not in per_model_df.columns or f"IPIP_{dom}" not in per_model_df.columns:
                continue
            rho = per_model_df[oct].corr(per_model_df[f"IPIP_{dom}"], method="spearman")
            n = per_model_df[[oct, f"IPIP_{dom}"]].dropna().shape[0]
            try:
                from scipy import stats
                p = stats.spearmanr(per_model_df[oct], per_model_df[f"IPIP_{dom}"]).pvalue
            except Exception:
                p = None
            rows.append({"octant": oct, "domain": dom, "rho": rho, "p": p, "n": n})
            if p is not None and p == p:
                pvals.append(p)
    if pvals:
        m = len(pvals)
        sorted_p = sorted(enumerate(pvals), key=lambda x: x[1])
        qmap = {}
        for rank, (idx, p) in enumerate(sorted_p, 1):
            qmap[idx] = min(1.0, p * m / rank)
        j = 0
        for i, row in enumerate(rows):
            if row["p"] is not None and row["p"] == row["p"]:
                row["q_bh"] = qmap.get(j)
                j += 1
            else:
                row["q_bh"] = None
    try:
        return pd.DataFrame(rows)
    except Exception:
        return rows


def convergence_panel_summary(session_df, model_col="model"):
    """Per-architecture IPIP↔PID-5 sign checks for H-D."""
    if not _HAS:
        return None
    rows = []
    for model, sub in session_df.groupby(model_col):
        pid_cols = [f"PID5_{d}" for d, _, _, _ in PID5_IPIP_CONVERGENCE]
        ip_cols = [f"IPIP_{d}" for _, d, _, _ in PID5_IPIP_CONVERGENCE]
        n_ok = 0
        pair_rs = []
        for (pd_dom, ip_dom, sign, _), pc, ic in zip(
                PID5_IPIP_CONVERGENCE, pid_cols, ip_cols):
            if pc not in sub.columns or ic not in sub.columns:
                continue
            r = sub[pc].corr(sub[ic], method="pearson")
            pair_rs.append(abs(r) if r == r else 0)
            if _sign_ok(r, sign):
                n_ok += 1
        csiv_cols = ["AGENTIC", "COMMUNAL"]
        ipip_dom_cols = [f"IPIP_{d}" for d in "NEOAC"]
        csiv_rs = []
        for cc in csiv_cols:
            for ic in ipip_dom_cols:
                if cc in sub.columns and ic in sub.columns:
                    r = sub[cc].corr(sub[ic], method="pearson")
                    if r == r:
                        csiv_rs.append(abs(r))
        rows.append({
            "model": model,
            "n_convergence_sign_ok": n_ok,
            "mean_abs_r_ipip_pid": float(np.mean(pair_rs)) if pair_rs else None,
            "mean_abs_r_ipip_csiv": float(np.mean(csiv_rs)) if csiv_rs else None,
            "h_d_pass": (n_ok >= 4 and
                        (float(np.mean(pair_rs)) if pair_rs else 0) >
                        (float(np.mean(csiv_rs)) if csiv_rs else 0)),
        })
    try:
        return pd.DataFrame(rows)
    except Exception:
        return rows


PID5_IPIP_CONVERGENCE = [
    ("Negative Affect", "N", "+", "strong"),
    ("Detachment", "E", "-", "strong"),
    ("Antagonism", "A", "-", "strong"),
    ("Disinhibition", "C", "-", "strong"),
    ("Psychoticism", "O", "+", "modest"),
]

# Pre-registered CSIV vector ↔ IPIP domain pairings (H-G, confirmatory).
CSIV_VECTOR_IPIP = [
    ("AGENTIC", "E", "+"),
    ("AGENTIC", "C", "+"),
    ("COMMUNAL", "A", "+"),
    ("COMMUNAL", "E", "+"),
]

# Secondary octant ↔ IPIP facet pairings (H-H). Facet = IPIP key (e.g. E3).
CSIV_OCTANT_FACET = [
    ("PA", "E3", "+"), ("PA", "C4", "+"),
    ("BC", "E3", "+"), ("BC", "A5", "-"),
    ("DE", "A5", "-"), ("DE", "A2", "-"),
    ("FG", "E5", "-"), ("FG", "A5", "-"),
    ("HI", "E5", "-"), ("HI", "E2", "-"),
    ("JK", "A3", "+"), ("JK", "A6", "+"),
    ("LM", "A3", "+"), ("LM", "A1", "+"),
    ("NO", "E2", "+"), ("NO", "A3", "+"),
]


def convergence_correlations(pid5_domains_df, ipip_domains_df):
    """Pearson r between PID-5 and IPIP domain scores across sessions."""
    if not _HAS:
        return None
    joined = pid5_domains_df.join(ipip_domains_df)
    full = joined.corr(method="pearson")
    pred = {}
    for pd_dom, ip_dom, sign, mag in PID5_IPIP_CONVERGENCE:
        if pd_dom in joined and ip_dom in joined:
            r = joined[pd_dom].corr(joined[ip_dom])
            pred[f"{pd_dom}<->{ip_dom}"] = {"r": r, "predicted_sign": sign,
                                            "predicted_magnitude": mag}
    return {"predicted": pred, "full_matrix": full}


def _sign_ok(r, predicted):
    if r is None or r != r:
        return None
    if predicted == "+":
        return r > 0
    if predicted == "-":
        return r < 0
    return None


def csiv_ipip_vector_links(per_model_df):
    """Cross-architecture Spearman ρ: CSIV vectors vs IPIP domains (H-G).

    per_model_df: rows = model names, cols include AGENTIC, COMMUNAL,
                  and IPIP domains N, E, O, A, C (architecture-level means).
    """
    if not _HAS or per_model_df is None or per_model_df.shape[0] < 3:
        return None
    preds = {}
    for csiv_col, ip_col, sign in CSIV_VECTOR_IPIP:
        if csiv_col in per_model_df.columns and ip_col in per_model_df.columns:
            rho = per_model_df[csiv_col].corr(per_model_df[ip_col], method="spearman")
            preds[f"{csiv_col}<->{ip_col}"] = {
                "rho": float(rho) if rho == rho else None,
                "predicted_sign": sign,
                "sign_ok": _sign_ok(rho, sign),
                "n": int(per_model_df.shape[0]),
            }
    n_ok = sum(1 for v in preds.values() if v.get("sign_ok"))
    return {"predictions": preds, "n_sign_ok": n_ok, "n_total": len(CSIV_VECTOR_IPIP)}


def csiv_octant_facet_within_architecture(session_df, model_col="model"):
    """Within-architecture octant ↔ facet correlations pooled across models (H-H).

    session_df: one row per session; cols = model, octant scores (PA..NO),
                  facet keys (E1..C6 as column names matching IPIP keys).
    Returns per-pair summary: fraction of architectures with correct sign.
    """
    if not _HAS or session_df is None:
        return None
    results = {}
    models = session_df[model_col].unique()
    for octant, facet, sign in CSIV_OCTANT_FACET:
        key = f"{octant}<->{facet}"
        ok = 0
        rs = []
        for m in models:
            sub = session_df[session_df[model_col] == m]
            if octant not in sub.columns or facet not in sub.columns:
                continue
            if len(sub) < 5:
                continue
            r = sub[octant].corr(sub[facet], method="pearson")
            if r == r:
                rs.append(r)
                if _sign_ok(r, sign):
                    ok += 1
        results[key] = {
            "predicted_sign": sign,
            "n_architectures": len(rs),
            "n_sign_ok": ok,
            "mean_r": float(np.mean(rs)) if rs else None,
        }
    return results


def csiv_octant_facet_panel(per_model_df):
    """Cross-architecture Spearman ρ for each octant–facet pair (exploratory)."""
    if not _HAS or per_model_df is None or per_model_df.shape[0] < 3:
        return None
    from instruments.csiv_key import OCTANT_ORDER
    out = {}
    for octant, facet, sign in CSIV_OCTANT_FACET:
        if octant in per_model_df.columns and facet in per_model_df.columns:
            rho = per_model_df[octant].corr(per_model_df[facet], method="spearman")
            out[f"{octant}<->{facet}"] = {
                "rho": float(rho) if rho == rho else None,
                "predicted_sign": sign,
                "sign_ok": _sign_ok(rho, sign),
            }
    return out


def intra_lab_profile_distance(per_model_df, domain_cols, model_col="model"):
    """Within-lab Euclidean distance across tier profiles (descriptive).

    per_model_df must include model_col and lab/tier columns or use config mapping.
    """
    if not _HAS:
        return None
    try:
        import config as cfg
    except Exception:
        return None
    if model_col not in per_model_df.columns:
        per_model_df = per_model_df.copy()
        per_model_df[model_col] = per_model_df.index
    labs = {}
    for _, row in per_model_df.iterrows():
        name = row[model_col]
        lab = cfg.MODEL_LAB.get(name)
        tier = cfg.MODEL_TIER.get(name)
        if lab is None or tier is None:
            continue
        vec = row[domain_cols].astype(float).values
        labs.setdefault(lab, {})[tier] = vec
    distances = {}
    for lab, tiers in labs.items():
        if len(tiers) < 2:
            continue
        sorted_tiers = sorted(tiers.keys())
        dists = []
        for i in range(len(sorted_tiers) - 1):
            a, b = tiers[sorted_tiers[i]], tiers[sorted_tiers[i + 1]]
            dists.append(float(np.linalg.norm(a - b)))
        distances[lab] = {
            "tier_pairs": len(dists),
            "mean_adjacent_distance": float(np.mean(dists)) if dists else None,
            "n_tiers": len(tiers),
        }
    return distances
