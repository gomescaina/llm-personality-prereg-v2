"""Carrega outputs/{tag}_all.json → tabelas p/ analyze.py."""
import glob
import json
import os

import config

try:
    import pandas as pd
    _HAS = True
except Exception:
    _HAS = False


def _outputs_dir():
    return config.OUTPUTS_DIR


def load_raw_sessions(tag="full"):
    """Load sessions from {tag}_all.json or individual session files."""
    all_path = os.path.join(_outputs_dir(), f"{tag}_all.json")
    if os.path.isfile(all_path):
        with open(all_path, encoding="utf-8") as f:
            return json.load(f)
    pattern = os.path.join(_outputs_dir(), f"{tag}_*_s*.json")
    paths = sorted(glob.glob(pattern))
    if not paths:
        raise FileNotFoundError(f"No session files for tag={tag!r} in {_outputs_dir()}")
    out = []
    for p in paths:
        with open(p, encoding="utf-8") as f:
            out.append(json.load(f))
    return out


def _flat_items(session, instrument):
    inst = session.get("instruments", {}).get(instrument, {})
    responses = inst.get("responses") or {}
    rows = []
    for num, val in responses.items():
        rows.append({
            "model": session["model"],
            "session": session["session"],
            "lab": config.MODEL_LAB.get(session["model"]),
            "tier": config.MODEL_TIER.get(session["model"]),
            "legacy_seven": session["model"] in config.LEGACY_SEVEN,
            "instrument": instrument,
            "item_num": int(num),
            "raw": val,
        })
    return rows


def to_item_dataframes(sessions):
    """Return {instrument: DataFrame} with one row per item response."""
    if not _HAS:
        return None
    by_inst = {"ipip": [], "pid5": [], "csiv": []}
    for s in sessions:
        for inst in by_inst:
            by_inst[inst].extend(_flat_items(s, inst))
    return {k: pd.DataFrame(v) if v else pd.DataFrame() for k, v in by_inst.items()}


def _session_row(session):
    """One row per session with key scored variables."""
    row = {
        "model": session["model"],
        "session": session["session"],
        "lab": config.MODEL_LAB.get(session["model"]),
        "tier": config.MODEL_TIER.get(session["model"]),
        "legacy_seven": session["model"] in config.LEGACY_SEVEN,
        "cost_usd": session.get("cost_usd"),
    }
    ipip = session.get("instruments", {}).get("ipip", {}).get("scored") or {}
    for dom, info in (ipip.get("domains") or {}).items():
        row[f"IPIP_{dom}"] = info.get("raw")
    for facet, info in (ipip.get("facets") or {}).items():
        row[facet] = info.get("average")

    pid = session.get("instruments", {}).get("pid5", {}).get("scored") or {}
    for dom, info in (pid.get("domains_worksheet") or {}).items():
        row[f"PID5_{dom}"] = info.get("average")
    for facet, info in (pid.get("facets") or {}).items():
        row[f"PID5_{facet}"] = info.get("average")
    val = pid.get("validity") or {}
    row["VRIN"] = val.get("VRIN")
    row["ORS"] = val.get("ORS")
    row["PRD"] = val.get("PRD")
    for k, v in (val.get("flags") or {}).items():
        row[k] = v

    csiv = session.get("instruments", {}).get("csiv", {}).get("scored") or {}
    for octant, val in (csiv.get("octants") or {}).items():
        row[octant] = val
    for k, v in (csiv.get("metrics") or {}).items():
        row[k] = v
    return row


def to_session_table(sessions):
    if not _HAS:
        return None
    return pd.DataFrame([_session_row(s) for s in sessions])


def to_score_tables(sessions):
    """Architecture-level means (one row per model)."""
    if not _HAS:
        return None
    sess = to_session_table(sessions)
    if sess is None or sess.empty:
        return None
    num_cols = [c for c in sess.columns
                if c not in ("model", "session", "lab", "tier", "legacy_seven", "cost_usd")
                and sess[c].dtype != bool]
    agg = sess.groupby("model", as_index=False)[num_cols].mean(numeric_only=True)
    meta = sess.groupby("model", as_index=False).first()[
        ["model", "lab", "tier", "legacy_seven"]]
    return meta.merge(agg, on="model")


def filter_legacy(per_model_df):
    if per_model_df is None:
        return None
    return per_model_df[per_model_df["legacy_seven"]].copy()
