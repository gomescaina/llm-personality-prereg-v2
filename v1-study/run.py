"""Orchestrator: build blocks, call the panel, parse, score, and persist.

Modos (sem --run = só plano, não gasta API):
  python run.py --smoke           # 2 modelos, 1 sessão, só IPIP
  python run.py --full --run      # painel completo — só DEPOIS do OSF

Outputs vão para outputs/; manifest grava git commit qdo existir.
"""
import argparse, json, os, time, datetime, subprocess
import config
import prompts
import parser as P
import client as C
import scoring as S

INSTRUMENT_META = {
    "pid5": {"parse": P.parse_pid5, "score": S.score_pid5, "min": 0, "max": 3},
    "ipip": {"parse": P.parse_ipip, "score": S.score_ipip, "min": 1, "max": 5},
    "csiv": {"parse": P.parse_csiv, "score": S.score_csiv, "min": 0, "max": 4},
}


def _slug_for(name):
    for n, slug, t, mt in config.PANEL:
        if n == name:
            return slug, t, mt
    raise KeyError(name)


def _instrument_nums(instrument):
    if instrument == "pid5":
        return sorted(prompts.PID5_ITEM_TEXT)
    if instrument == "ipip":
        from instruments import ipip_key
        return sorted(r["num"] for r in ipip_key.ITEMS)
    if instrument == "csiv":
        from instruments import csiv_key
        return sorted(csiv_key.ITEMS)


def _session_plan(instruments):
    """Return {instrument: [(block_idx, n_blocks, [(num,text),...]), ...]}."""
    plan = {}
    for inst in instruments:
        plan[inst] = prompts.block_plan(inst)
    return plan


def run_session(model_name, session_id, instruments, dry_run=True):
    """Execute one session for one model across the given instruments."""
    slug, temp, mt = _slug_for(model_name)
    plan = _session_plan(instruments)
    result = {
        "model": model_name, "slug": slug, "session": session_id,
        "ts_start": datetime.datetime.utcnow().isoformat() + "Z",
        "instruments": {}, "cost_usd": 0.0, "tokens": {"prompt": 0, "completion": 0},
    }
    for inst in instruments:
        blocks = plan[inst]
        meta = INSTRUMENT_META[inst]
        responses = {}
        blocks_log = []
        for block_idx, n_blocks, items in blocks:
            expected_nums = [n for n, _ in items]
            system_prompt, user_prompt = prompts.build_block_prompts(
                inst, items, block_idx, n_blocks)
            if dry_run:
                blocks_log.append({"block": block_idx, "n_blocks": n_blocks,
                                   "n_items": len(items),
                                   "system_prompt": system_prompt,
                                   "user_prompt": user_prompt,
                                   "dry_run": True})
                continue
            comp = C.completion(slug, user_prompt, system=system_prompt,
                                temperature=temp, max_tokens=mt)
            entry = {"block": block_idx, "n_blocks": n_blocks, "n_items": len(items),
                     "system_prompt": system_prompt, "user_prompt": user_prompt,
                     "attempts": comp.get("attempts"), "ms": comp.get("ms"),
                     "usage": comp.get("usage"), "model_version": comp.get("model_version"),
                     "error": comp.get("error")}
            cost = C.estimate_cost(comp.get("usage", {}), slug)
            entry["cost_usd"] = cost
            if cost:
                result["cost_usd"] += cost
            u = comp.get("usage", {})
            result["tokens"]["prompt"] += u.get("prompt_tokens", 0)
            result["tokens"]["completion"] += u.get("completion_tokens", 0)
            text = comp.get("text") or ""
            parsed, dropped, oor, n_parsed = meta["parse"](text, expected_nums)
            # retry once se drift ou itens caídos — aprendemos cedo q isso acontece
            if (text and not P.looks_like_list(text, len(expected_nums))) or dropped:
                comp2 = C.completion(slug, user_prompt, system=system_prompt,
                                     temperature=temp, max_tokens=mt)
                text2 = comp2.get("text") or ""
                parsed2, dropped2, oor2, n_parsed2 = meta["parse"](text2, expected_nums)
                if len(parsed2) > len(parsed):
                    parsed, dropped, oor, n_parsed = parsed2, dropped2, oor2, n_parsed2
                entry["retry"] = True
            responses.update(parsed)
            entry.update({"dropped": dropped, "out_of_range": oor,
                          "n_parsed": n_parsed, "raw_reply_head": text[:300]})
            blocks_log.append(entry)
            time.sleep(0.5)
        scored = meta["score"](responses) if not dry_run else None
        result["instruments"][inst] = {
            "n_items_expected": len(_instrument_nums(inst)),
            "n_items_answered": len(responses),
            "responses": responses, "scored": scored, "blocks": blocks_log,
        }
    result["ts_end"] = datetime.datetime.utcnow().isoformat() + "Z"
    return result


def _out_path(name):
    os.makedirs(config.OUTPUTS_DIR, exist_ok=True)
    return os.path.join(config.OUTPUTS_DIR, name)


def _git_commit():
    """Hash do commit p/ manifest — best effort, se não tiver git fica None."""
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                           text=True, cwd=config.ROOT, timeout=5)
        return r.stdout.strip() or None
    except Exception:
        return None


def _write_manifest(tag, models, sessions, instruments, all_results):
    manifest = {
        "tag": tag,
        "ts": datetime.datetime.utcnow().isoformat() + "Z",
        "git_commit": _git_commit(),
        "panel": [{"model": m, "slug": _slug_for(m)[0],
                     "lab": config.MODEL_LAB.get(m),
                     "tier": config.MODEL_TIER.get(m)} for m in models],
        "n_sessions_per_model": sessions,
        "instruments": instruments,
        "n_sessions_completed": len(all_results),
        "total_cost_usd": round(sum(r["cost_usd"] for r in all_results), 4),
        "total_tokens": {
            "prompt": sum(r["tokens"]["prompt"] for r in all_results),
            "completion": sum(r["tokens"]["completion"] for r in all_results),
        },
        "temperature": config.TEMPERATURE,
        "openrouter_base_url": config.OPENROUTER_BASE_URL,
    }
    with open(_out_path(f"{tag}_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=1, ensure_ascii=False)
    return manifest


def execute(models, sessions, instruments, tag):
    all_results = []
    for m in models:
        for s in range(1, sessions + 1):
            print(f"[{tag}] {m} session {s}/{sessions}")
            res = run_session(m, s, instruments, dry_run=False)
            all_results.append(res)
            fn = _out_path(f"{tag}_{m.replace(' ','_')}_s{s:02d}.json")
            with open(fn, "w", encoding="utf-8") as f:
                json.dump(res, f, indent=1, ensure_ascii=False)
    with open(_out_path(f"{tag}_all.json"), "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=1, ensure_ascii=False)
    manifest = _write_manifest(tag, models, sessions, instruments, all_results)
    total = manifest["total_cost_usd"]
    toks = manifest["total_tokens"]["prompt"] + manifest["total_tokens"]["completion"]
    print(f"[{tag}] done. sessions={len(all_results)} cost=${total:.2f} tokens={toks}")
    print(f"[{tag}] manifest written to outputs/{tag}_manifest.json "
          f"(git_commit={manifest['git_commit']})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--run", action="store_true",
                    help="actually call the API; without this, only the plan is printed")
    args = ap.parse_args()

    if args.smoke:
        models = config.SMOKE_MODELS
        sessions = config.SMOKE_SESSIONS
        instruments = config.SMOKE_INSTRUMENTS
        tag = "smoke"
    elif args.full:
        models = [n for n, *_ in config.PANEL]
        sessions = config.N_SESSIONS
        instruments = ["ipip", "pid5", "csiv"]
        tag = "full"
    else:
        print("Specify --smoke or --full. Add --run to execute API calls.")
        return

    plan = _session_plan(instruments)
    print(f"Mode: {tag} | models={models} | sessions={sessions} | instruments={instruments}")
    for inst, blocks in plan.items():
        sizes = [len(b) for _, _, b in blocks]
        print(f"  {inst}: {len(blocks)} blocks, sizes={sizes}, total={sum(sizes)} items/session/model")

    if not args.run:
        print("Dry run only (no API calls). Add --run to execute.")
        # Persist a dry-run plan for inspection.
        with open(_out_path(f"{tag}_plan.json"), "w", encoding="utf-8") as f:
            json.dump({inst: [{"block": i+1, "n_blocks": len(blocks),
                               "items": [(n, t) for n, t in b]}
                              for i, (_, _, b) in enumerate(blocks)]
                       for inst, blocks in plan.items()}, f, indent=1)
        print(f"Plan written to outputs/{tag}_plan.json")
        return

    if not os.environ.get(config.OPENROUTER_API_KEY_ENV):
        print(f"ERROR: {config.OPENROUTER_API_KEY_ENV} is not set.")
        return
    execute(models, sessions, instruments, tag)


if __name__ == "__main__":
    main()
