"""H-A … H-H — regras de pass/fail do OSF (tiers 1–3).

Limiares 15/21 ≈ 71%, mesmo espírito do frame N=7 original.
"""
import psychometrics as psych
from instruments.csiv_key import OCTANT_ORDER

try:
    import numpy as np
    import pandas as pd
    _HAS = True
except Exception:
    _HAS = False

N_MODELS = 21
THRESH_PASS = 15
THRESH_FAIL = 9
HH_PAIR_PASS = 12
HH_PAIR_TOTAL = 16


def _result(hypothesis, tier, criterion, passed, n_pass, n_total, detail=None):
    return {
        "hypothesis": hypothesis,
        "tier": tier,
        "criterion": criterion,
        "result": "pass" if passed else "fail",
        "n_pass": n_pass,
        "n_total": n_total,
        "detail": detail or {},
    }


def adjudicate_h_a(session_df):
    """H-A: três camadas (IPIP + PID + CSIV) coerentes dentro da arquitetura."""
    if not _HAS:
        return _result("H-A", 3, ">=15/21 coherent", False, 0, 0)
    pairs = [
        ("AGENTIC", "IPIP_E", "+"),
        ("AGENTIC", "IPIP_C", "+"),
        ("COMMUNAL", "IPIP_A", "+"),
        ("PID5_Antagonism", "IPIP_A", "-"),
    ]
    n_pass = 0
    per_model = {}
    for model, sub in session_df.groupby("model"):
        if len(sub) < 5:
            continue
        ok = 0
        for a, b, sign in pairs:
            if a not in sub.columns or b not in sub.columns:
                continue
            r = sub[a].corr(sub[b], method="pearson")
            if psych._sign_ok(r, sign):
                ok += 1
        passed = ok >= 3
        per_model[model] = {"n_sign_ok": ok, "passed": passed}
        if passed:
            n_pass += 1
    n_total = len(per_model)
    return _result("H-A", 3, f">={THRESH_PASS}/{N_MODELS} architectures >=3/4 layer links",
                   n_pass >= THRESH_PASS, n_pass, n_total, per_model)


def adjudicate_h_b(per_model_df):
    """CSIV vs trait rank-order dissociation."""
    if not _HAS or per_model_df is None:
        return _result("H-B", 3, "Spearman rho < .50 both", False, 0, 0)
    csiv_rank = per_model_df["AGENTIC"].rank() + per_model_df["COMMUNAL"].rank()
    ipip_cols = [f"IPIP_{d}" for d in "NEOAC" if f"IPIP_{d}" in per_model_df.columns]
    pid_cols = [c for c in per_model_df.columns if c.startswith("PID5_")]
    ipip_rank = per_model_df[ipip_cols].mean(axis=1).rank() if ipip_cols else None
    pid_rank = per_model_df[pid_cols].mean(axis=1).rank() if pid_cols else None
    rho_ipip = csiv_rank.corr(ipip_rank, method="spearman") if ipip_rank is not None else 1.0
    rho_pid = csiv_rank.corr(pid_rank, method="spearman") if pid_rank is not None else 1.0
    passed = (abs(rho_ipip) < 0.50 if rho_ipip == rho_ipip else False) and \
             (abs(rho_pid) < 0.50 if rho_pid == rho_pid else False)
    return _result("H-B", 3, "rho(CSIV, IPIP) and rho(CSIV, PID) both < .50",
                   passed, int(passed), 1,
                   {"rho_csiv_ipip": float(rho_ipip), "rho_csiv_pid": float(rho_pid)})


def adjudicate_h_c(session_df):
    """Role-norm via PRD and variance compression."""
    if not _HAS:
        return _result("H-C", 3, "PRD + variance pattern", False, 0, 0)
    trait_cols = [c for c in session_df.columns
                  if c.startswith("IPIP_") or c.startswith("PID5_")]
    csiv_cols = [c for c in OCTANT_ORDER if c in session_df.columns]
    arch_trait_sd = session_df.groupby("model")[trait_cols].std().mean(axis=1).mean()
    arch_csiv_sd = session_df.groupby("model")[csiv_cols].std().mean(axis=1).mean()
    prd_low = session_df.groupby("model")["PRD"].apply(
        lambda s: (s < 11).mean() if "PRD" in session_df.columns else 0)
    passed = (prd_low.mean() >= 0.5 and arch_trait_sd < arch_csiv_sd)
    return _result("H-C", 3, "PRD<11 majority + trait SD < CSIV SD",
                   passed, int(passed), 1,
                   {"mean_prd_low_rate": float(prd_low.mean()),
                    "trait_sd_mean": float(arch_trait_sd),
                    "csiv_sd_mean": float(arch_csiv_sd)})


def adjudicate_h_d(convergence_df):
    if convergence_df is None or convergence_df.empty:
        return _result("H-D", 3, "IPIP-PID > IPIP-CSIV; >=4/5 signs", False, 0, 0)
    n_pass = int(convergence_df["h_d_pass"].sum())
    n_total = len(convergence_df)
    return _result("H-D", 3, f">={THRESH_PASS}/{N_MODELS} architectures pass",
                   n_pass >= THRESH_PASS, n_pass, n_total,
                   convergence_df.set_index("model")["h_d_pass"].to_dict())


def adjudicate_h_e(cross_loading):
    if not cross_loading:
        return _result("H-E", 3, f">={THRESH_PASS}/{N_MODELS} cross-loadings", False, 0, 0)
    return _result("H-E", 3, f">={THRESH_PASS}/{N_MODELS} models >=3/4 facet links",
                   cross_loading["n_pass"] >= THRESH_PASS,
                   cross_loading["n_pass"], cross_loading["n_total"],
                   cross_loading.get("per_model"))


def adjudicate_h_f(per_model_df):
    if not _HAS or per_model_df is None or "R2" not in per_model_df.columns:
        return _result("H-F", 3, "mean R2 > .70 + communal ANG", False, 0, 0)
    mean_r2 = per_model_df["R2"].mean()
    # Communal semicircle: LM(0), NO(45), JK(315) — mean angle toward communion
    communal_angs = []
    for ang in per_model_df.get("ANG", []):
        if ang is None or ang != ang:
            continue
        a = float(ang) % 360
        communal_angs.append(a <= 90 or a >= 270 or (315 <= a <= 360))
    communal_rate = np.mean(communal_angs) if communal_angs else 0
    passed = mean_r2 > 0.70 and communal_rate >= 0.5
    fail = mean_r2 < 0.50
    result = "fail" if fail else ("pass" if passed else "fail")
    return {
        "hypothesis": "H-F", "tier": 3,
        "criterion": "mean R2 > .70 AND communal ANG majority; fail if R2 < .50",
        "result": result,
        "n_pass": int(passed),
        "n_total": 1,
        "detail": {"mean_R2": float(mean_r2), "communal_rate": float(communal_rate)},
    }


def adjudicate_h_g(per_model_df):
    links = psych.csiv_ipip_vector_links(per_model_df)
    if not links:
        return _result("H-G", 1, ">=3/4 vector-domain signs", False, 0, 4)
    passed = links["n_sign_ok"] >= 3
    return _result("H-G", 1, ">=3/4 correct signs (confirmatory)",
                   passed, links["n_sign_ok"], links["n_total"],
                   links.get("predictions"))


def adjudicate_h_h(session_df):
    pairs = psych.csiv_octant_facet_within_architecture(session_df)
    if not pairs:
        return _result("H-H", 2, f">={HH_PAIR_PASS}/{HH_PAIR_TOTAL} pairs in >={THRESH_PASS}/21 arch",
                       False, 0, HH_PAIR_TOTAL)
    n_pairs_pass = sum(1 for v in pairs.values()
                       if v.get("n_sign_ok", 0) >= THRESH_PASS)
    passed = n_pairs_pass >= HH_PAIR_PASS
    return _result("H-H", 2, f">={HH_PAIR_PASS}/{HH_PAIR_TOTAL} pairs in >={THRESH_PASS}/21 arch",
                   passed, n_pairs_pass, HH_PAIR_TOTAL, pairs)


def adjudicate_all(session_df, per_model_df, convergence_df, cross_loading):
    return [
        adjudicate_h_a(session_df),
        adjudicate_h_b(per_model_df),
        adjudicate_h_c(session_df),
        adjudicate_h_d(convergence_df),
        adjudicate_h_e(cross_loading),
        adjudicate_h_f(per_model_df),
        adjudicate_h_g(per_model_df),
        adjudicate_h_h(session_df),
    ]
