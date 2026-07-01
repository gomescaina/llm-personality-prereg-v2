"""Análises pré-registradas em cima do JSON das sessões.

Depois da corrida: python analyze.py --tag full
Tier 4 (exploratório) fica em exploratory/ — não misturar c/ H-G confirmatório.
"""
import argparse
import json
import os

import config
import hypotheses
import load_sessions as L
import norms
import psychometrics as psych

try:
    import pandas as pd
    _HAS = True
except Exception:
    _HAS = False


def _out_dir(tag):
    d = os.path.join(config.OUTPUTS_DIR, "analysis", tag)
    os.makedirs(d, exist_ok=True)
    return d


def _write_csv(df, path):
    if df is not None and _HAS and hasattr(df, "to_csv"):
        df.to_csv(path, index=False)


def _validity_summary(session_df):
    if not _HAS:
        return None
    rows = []
    for model, sub in session_df.groupby("model"):
        n = len(sub)
        rows.append({
            "model": model,
            "n_sessions": n,
            "VRIN_flag_rate": sub.get("VRIN_inconsistent", pd.Series()).mean(),
            "ORS_flag_rate": sub.get("ORS_overreporting", pd.Series()).mean(),
            "PRD_under_rate": sub.get("PRD_underreporting", pd.Series()).mean(),
            "PRD_mean": sub["PRD"].mean() if "PRD" in sub.columns else None,
        })
    return pd.DataFrame(rows)


def _csiv_summary(per_model_df):
    if not _HAS:
        return None
    cols = [c for c in ["R2", "AMP", "ELE", "ANG", "AGENTIC", "COMMUNAL"]
            if c in per_model_df.columns]
    return per_model_df[["model", "lab", "tier"] + cols].copy()


def run_analysis(tag, hypotheses_only=False, exploratory_only=False, legacy=False):
    sessions = L.load_raw_sessions(tag)
    out = _out_dir(tag)
    session_df = L.to_session_table(sessions)
    per_model_df = L.to_score_tables(sessions)
    if legacy and per_model_df is not None:
        per_model_df = L.filter_legacy(per_model_df)
        session_df = session_df[session_df["legacy_seven"]]

    if exploratory_only:
        exp = psych.exploratory_octant_domain_matrix(per_model_df)
        exp_dir = os.path.join(out, "exploratory")
        os.makedirs(exp_dir, exist_ok=True)
        _write_csv(exp, os.path.join(exp_dir, "octant_domain_fdr.csv"))
        return out

    if hypotheses_only:
        conv = psych.convergence_panel_summary(session_df)
        cross = psych.cross_loading_check(session_df)
        hyps = hypotheses.adjudicate_all(session_df, per_model_df, conv, cross)
        with open(os.path.join(out, "hypotheses.json"), "w", encoding="utf-8") as f:
            json.dump(hyps, f, indent=2, default=str)
        return out

    # pacote completo — tudo o q §6 pede (+ exploratory à parte)
    from instruments import ipip_key, pid5_key, csiv_key

    item_dfs = L.to_item_dataframes(sessions)
    ipip_scales = {f"IPIP_{f}": items for f, items in ipip_key.FACET_ITEMS.items()}
    pid_scales = {f: items for f, items in pid5_key.FACET_ITEMS.items()}
    csiv_scales = {o: csiv_key.OCTANT_ITEMS[o] for o in csiv_key.OCTANT_ORDER}

    rel_rows = []
    if item_dfs:
        rel_rows.extend(psych.reliability_report_from_items(
            item_dfs.get("ipip"), ipip_scales))
        rel_rows.extend(psych.reliability_report_from_items(
            item_dfs.get("pid5"), pid_scales))
        rel_rows.extend(psych.reliability_report_from_items(
            item_dfs.get("csiv"), csiv_scales))
    rel_df = pd.DataFrame(rel_rows) if rel_rows and _HAS else None
    _write_csv(rel_df, os.path.join(out, "reliability.csv"))

    icc_cols = [c for c in session_df.columns
                if c.startswith("IPIP_") or c.startswith("PID5_")
                or c in csiv_key.OCTANT_ORDER or c in ("AGENTIC", "COMMUNAL")]
    icc_rows = psych.reliability_icc_table(session_df, icc_cols)
    if icc_rows and _HAS:
        icc_df = pd.DataFrame(icc_rows)
        icc_path = os.path.join(out, "reliability_icc.csv")
        icc_df.to_csv(icc_path, index=False)

    _write_csv(_validity_summary(session_df), os.path.join(out, "validity_summary.csv"))

    conv = psych.convergence_panel_summary(session_df)
    _write_csv(conv, os.path.join(out, "convergence.csv"))

    _write_csv(_csiv_summary(per_model_df), os.path.join(out, "csiv_circumplex.csv"))

    _write_csv(norms.profile_norms_table(per_model_df),
               os.path.join(out, "human_norm_profiles.csv"))

    domain_cols = [c for c in per_model_df.columns if c.startswith("IPIP_")]
    intra = psych.intra_lab_profile_distance(per_model_df, domain_cols)
    if intra and _HAS:
        pd.DataFrame([
            {"lab": lab, **vals} for lab, vals in intra.items()
        ]).to_csv(os.path.join(out, "intra_lab_tiers.csv"), index=False)

    cross = psych.cross_loading_check(session_df)
    hyps = hypotheses.adjudicate_all(session_df, per_model_df, conv, cross)
    with open(os.path.join(out, "hypotheses.json"), "w", encoding="utf-8") as f:
        json.dump(hyps, f, indent=2, default=str)

    exp = psych.exploratory_octant_domain_matrix(per_model_df)
    exp_dir = os.path.join(out, "exploratory")
    os.makedirs(exp_dir, exist_ok=True)
    _write_csv(exp, os.path.join(exp_dir, "octant_domain_fdr.csv"))

    _write_report(out, tag, hyps, len(sessions))
    return out


def _write_report(out, tag, hyps, n_sessions):
    lines = [
        f"# Analysis report ({tag})",
        "",
        f"Sessions analyzed: {n_sessions}",
        "",
        "## Hypothesis adjudication",
        "",
    ]
    for h in hyps:
        tier_label = {1: "confirmatory", 2: "secondary", 3: "descriptive", 4: "exploratory"}
        lines.append(f"- **{h['hypothesis']}** (tier {h['tier']} {tier_label.get(h['tier'], '')}): "
                     f"**{h['result'].upper()}** — {h['criterion']} "
                     f"({h['n_pass']}/{h['n_total']})")
    lines.extend([
        "",
        "## Output files",
        "",
        "- reliability.csv, reliability_icc.csv",
        "- validity_summary.csv, convergence.csv",
        "- csiv_circumplex.csv, human_norm_profiles.csv",
        "- intra_lab_tiers.csv, hypotheses.json",
        "- exploratory/octant_domain_fdr.csv (tier 4 — not confirmatory)",
        "",
    ])
    with open(os.path.join(out, "ANALYSIS_REPORT.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="full", help="session file tag (full, fixture, smoke)")
    ap.add_argument("--hypotheses", action="store_true", help="hypotheses only")
    ap.add_argument("--exploratory", action="store_true", help="tier-4 exploratory only")
    ap.add_argument("--legacy", action="store_true", help="LEGACY_SEVEN subset only")
    args = ap.parse_args()
    out = run_analysis(args.tag, args.hypotheses, args.exploratory, args.legacy)
    print(f"Analysis written to {out}")


if __name__ == "__main__":
    main()
