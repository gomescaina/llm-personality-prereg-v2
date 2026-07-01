"""Generate synthetic session JSON for analysis pipeline tests."""
import json
import os
import random

import config
import scoring as S

MODELS = ["Model_A", "Model_B", "Model_C"]
N_SESSIONS = 5
TAG = "fixture"


def _random_responses(nums, lo, hi, seed):
    rng = random.Random(seed)
    return {n: rng.randint(lo, hi) for n in nums}


def make_session(model, session_id, seed):
    from instruments import ipip_key, csiv_key
    ipip_nums = [r["num"] for r in ipip_key.ITEMS]
    pid_nums = sorted(scoring_pid5_nums())
    csiv_nums = sorted(csiv_key.ITEMS.keys())
    ipip_r = _random_responses(ipip_nums, 1, 5, seed)
    pid_r = _random_responses(pid_nums, 0, 3, seed + 1)
    csiv_r = _random_responses(csiv_nums, 0, 4, seed + 2)
    return {
        "model": model,
        "slug": "test/model",
        "session": session_id,
        "ts_start": "2026-07-01T00:00:00Z",
        "ts_end": "2026-07-01T00:05:00Z",
        "cost_usd": 0.0,
        "tokens": {"prompt": 100, "completion": 50},
        "instruments": {
            "ipip": {
                "n_items_expected": 300,
                "n_items_answered": 300,
                "responses": {str(k): v for k, v in ipip_r.items()},
                "scored": S.score_ipip(ipip_r),
                "blocks": [{
                    "block": 1,
                    "system_prompt": "test system",
                    "user_prompt": "test user prompt block",
                    "model_version": "test/v1",
                }],
            },
            "pid5": {
                "n_items_expected": 220,
                "n_items_answered": 220,
                "responses": {str(k): v for k, v in pid_r.items()},
                "scored": S.score_pid5(pid_r),
                "blocks": [{
                    "block": 1,
                    "system_prompt": "test system",
                    "user_prompt": "test user pid5",
                    "model_version": "test/v1",
                }],
            },
            "csiv": {
                "n_items_expected": 64,
                "n_items_answered": 64,
                "responses": {str(k): v for k, v in csiv_r.items()},
                "scored": S.score_csiv(csiv_r),
                "blocks": [{
                    "block": 1,
                    "system_prompt": "test system",
                    "user_prompt": "test user csiv",
                    "model_version": "test/v1",
                }],
            },
        },
    }


def scoring_pid5_nums():
    from instruments import pid5_key
    return pid5_key.assigned_items()


def write_fixture():
    # Temporarily map test models into config for load_sessions metadata
    for i, m in enumerate(MODELS):
        config.MODEL_LAB[m] = ["OpenAI", "Anthropic", "Google"][i]
        config.MODEL_TIER[m] = i + 1
    sessions = []
    for mi, model in enumerate(MODELS):
        for s in range(1, N_SESSIONS + 1):
            sessions.append(make_session(model, s, mi * 100 + s))
    os.makedirs(config.OUTPUTS_DIR, exist_ok=True)
    path = os.path.join(config.OUTPUTS_DIR, f"{TAG}_all.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(sessions, f, indent=1)
    return path


if __name__ == "__main__":
    print(write_fixture())
