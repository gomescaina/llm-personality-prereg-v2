import json
import os

import analyze
import config
import load_sessions as L


def test_load_fixture(fixture_sessions_path):
    sessions = L.load_raw_sessions("fixture")
    assert len(sessions) == 15  # 3 models × 5 sessions


def test_session_table(fixture_sessions_path):
    sessions = L.load_raw_sessions("fixture")
    df = L.to_session_table(sessions)
    assert "IPIP_N" in df.columns
    assert "AGENTIC" in df.columns
    assert len(df) == 15


def test_analyze_pipeline(fixture_sessions_path):
    out = analyze.run_analysis("fixture")
    assert os.path.isdir(out)
    assert os.path.isfile(os.path.join(out, "hypotheses.json"))
    assert os.path.isfile(os.path.join(out, "ANALYSIS_REPORT.md"))
    with open(os.path.join(out, "hypotheses.json"), encoding="utf-8") as f:
        hyps = json.load(f)
    assert len(hyps) == 8
    ids = {h["hypothesis"] for h in hyps}
    assert ids == {"H-A", "H-B", "H-C", "H-D", "H-E", "H-F", "H-G", "H-H"}


def test_block_logging_in_fixture(fixture_sessions_path):
    sessions = L.load_raw_sessions("fixture")
    block = sessions[0]["instruments"]["ipip"]["blocks"][0]
    assert "system_prompt" in block
    assert "user_prompt" in block
