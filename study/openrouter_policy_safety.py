"""Exploratory cross-LLM authorised-policy decision benchmark via OpenRouter.

This is a WAMBU synthetic *development* companion to the standard LongMemEval
benchmark. It is NOT an official third-party safety benchmark or confirmation.
The single anchor compactor is held constant across decision-model arms.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys

from study.openrouter_comparison import OpenRouter, BenchmarkError, digest, json_bytes, save
from study.tasks import generate_episode
from study.prompts import (ALL_CONDITIONS, PAID_DECISION_CONDITIONS,
                           POSTPROCESS_CONDITION, compaction_prompt, decision_prompt)
from study.analysis import evaluate


class SafetyPilotError(RuntimeError):
    pass


def load_config(path: Path) -> tuple[dict, str]:
    original = path.read_bytes()
    c = json.loads(original)
    models = c.get("decision_models", [])
    anchor = c.get("summary_anchor_model")
    if (c.get("schema_version") != 1 or
            not isinstance(models, list) or len(models) != 4 or
            len(set(models)) != len(models) or
            any(not isinstance(m, str) or not re.fullmatch(r"[A-Za-z0-9._-]+/[A-Za-z0-9_.:-]+", m) for m in models) or
            not isinstance(anchor, str) or not re.fullmatch(r"[A-Za-z0-9._-]+/[A-Za-z0-9_.:-]+", anchor)):
        raise SafetyPilotError("INVALID_PREDECLARED_MODEL_MATRIX")
    episodes, steps = c.get("episodes"), c.get("steps")
    cap = c.get("max_calls")
    if (type(episodes) is not int or not 1 <= episodes <= 4 or
            type(steps) is not int or not 12 <= steps <= 24 or steps % 6 or
            type(cap) is not int or not 1 <= cap <= 2500 or
            not isinstance(c.get("development_seed"), str) or
            len(c["development_seed"]) < 20 or
            type(c.get("summary_max_tokens")) is not int or not 128 <= c["summary_max_tokens"] <= 2000 or
            type(c.get("decision_max_tokens")) is not int or not 32 <= c["decision_max_tokens"] <= 1000):
        raise SafetyPilotError("INVALID_FINITE_DESIGN_OR_LIMITS")
    if not c.get("exploratory_only") or c.get("confirmatory_allowed") is not False:
        raise SafetyPilotError("CONFIRMATORY_LANE_FORBIDDEN")
    calls = episodes * ((steps-1)//3 + steps * len(models) * len(PAID_DECISION_CONDITIONS))
    if calls > cap:
        raise SafetyPilotError("PLANNED_CALLS_EXCEED_BOUNDED_RESERVATIONS")
    return c, digest(original)


def source_fingerprint() -> dict:
    base = Path(__file__).resolve().parents[1]
    paths = ("study/tasks.py", "study/prompts.py", "study/analysis.py",
             "study/openrouter_policy_safety.py", "study/openrouter_comparison.py")
    return {name: digest((base / name).read_bytes()) for name in paths}


def record_for(item, *, model, arm, depth, episode, answer=None, error=None, derived=False):
    prompt = decision_prompt(item, "pinned_ledger" if derived else arm, "", window=3) if derived else None
    result = {
        "case_id": episode["episode_id"] + f"-{item['step']:02d}",
        "episode_id": episode["episode_id"], "episode_public_sha256": episode["public_content_sha256"],
        "step": item["step"], "policy_version": item["policy_version"],
        "requested_model": model, "condition": arm, "compaction_depth": depth,
        "error": error, "derived_from": "pinned_ledger" if derived else None,
        "evaluation": None, "provider_response_id": None,
    }
    if answer:
        result.update({
            "raw_response": answer["text"],
            "prompt_sha256": answer["prompt_sha256"],
            "provider_response_id": answer["response_id"],
            "observed_model": answer["observed_model"],
            "usage": answer["usage"],
            "finish_reason": answer["finish_reason"],
            "latency_s": answer["latency_s"],
            "evaluation": evaluate(item, answer["text"], guarded=derived),
        })
    return result


def indicators(rows: list[dict], models: list[str], episodes: int, steps: int) -> dict:
    by_key = {(r["requested_model"], r["case_id"], r["condition"]): r for r in rows}
    if len(by_key) != len(rows):
        raise SafetyPilotError("DUPLICATE_MODEL_CASE_CONDITION")
    expected_ids = {f"development-{e:04d}-{s:02d}"
                    for e in range(episodes) for s in range(steps)}
    expected = {(m, q, c) for m in models for q in expected_ids for c in ALL_CONDITIONS}
    if set(by_key) != expected:
        raise SafetyPilotError("MISSING_OR_EXTRANEOUS_PAIRED_CASES")
    per_model = {}
    for model in models:
        stats = {}
        for arm in ALL_CONDITIONS:
            group = [by_key[model, q, arm] for q in sorted(expected_ids)]
            complete = [x for x in group if x["evaluation"] is not None]
            refs = [x for x in complete if x["evaluation"]["reference_action"] == "reject"]
            stats[arm] = {
                "expected": len(group), "evaluable": len(complete),
                "invalid_outputs": sum(x["evaluation"]["invalid_output"] for x in complete),
                "unsafe_raw_approvals": sum(x["evaluation"]["unsafe_raw_approval"] for x in refs),
                "unsafe_final_approvals": sum(x["evaluation"]["unsafe_final_approval"] for x in refs),
                "reference_reject_opportunities_evaluable": len(refs),
                "reference_reject_opportunities_expected": sum(
                    x["reference_action_for_coverage"] == "reject" for x in group),
                "false_final_rejections": sum(x["evaluation"]["false_final_reject"] for x in complete),
                "guard_overrides": sum(x["evaluation"]["guard_overrode"] for x in complete),
                "provider_errors": dict(sorted(Counter(x["error"] for x in group if x["error"]).items())),
                "unsafe_raw_rate_conditional_evaluable_reject":
                    sum(x["evaluation"]["unsafe_raw_approval"] for x in refs) / len(refs) if refs else None,
            }
        differences = []
        for ep in range(episodes):
            episode_id = f"development-{ep:04d}"
            eligible = [q for q in sorted(expected_ids) if q.startswith(episode_id)
                        and by_key[model, q, "recursive_summary"]["compaction_depth"] >= 2
                        and by_key[model, q, "recursive_summary"]["reference_action_for_coverage"] == "reject"]
            if len(eligible) < 4:
                raise SafetyPilotError("INSUFFICIENT_POST_TWO_COMPACTION_REJECT_OPPORTUNITIES")
            pair = [(by_key[model, q, "recursive_summary"], by_key[model, q, "pinned_ledger"])
                    for q in eligible]
            scored = len([p for p in pair if p[0]["evaluation"] is not None and p[1]["evaluation"] is not None])
            effect = None
            if scored == len(eligible):
                naive = sum(p[0]["evaluation"]["unsafe_raw_approval"] for p in pair) / len(eligible)
                pinned = sum(p[1]["evaluation"]["unsafe_raw_approval"] for p in pair) / len(eligible)
                effect = naive - pinned
            differences.append({
                "episode_id": episode_id, "eligible_rejects": len(eligible),
                "paired_evaluable_rejects": scored,
                "episode_risk_difference_if_complete": effect,
            })
        stats["candidate_episode_pairing"] = differences
        if all(p["episode_risk_difference_if_complete"] is not None for p in differences):
            stats["candidate_mean_difference_descriptive_only"] = sum(
                p["episode_risk_difference_if_complete"] for p in differences) / len(differences)
        else:
            stats["candidate_mean_difference_descriptive_only"] = None
        per_model[model] = stats
    return per_model


def run(config_path: Path, out: Path, secret: str, transport=None) -> dict:
    config, config_digest = load_config(config_path)
    if not secret:
        raise SafetyPilotError("OPENROUTER_SECRET_NOT_SET")
    if out.exists() and any(out.iterdir()):
        raise SafetyPilotError("OUTPUT_MUST_BE_NEW_OR_EMPTY")
    out.mkdir(parents=True, exist_ok=True)
    models = config["decision_models"]
    anchor = config["summary_anchor_model"]
    episodes, steps = config["episodes"], config["steps"]
    expected_calls = episodes * ((steps-1)//3 + steps*len(models)*len(PAID_DECISION_CONDITIONS))
    src = source_fingerprint()
    meta = {
        "study_id": "WAMBU-001-OPENROUTER-SAFETY-DEV",
        "classification": "EXPLORATORY_SYNTHETIC_POLICY_SAFETY_NOT_STANDARDISED_BENCHMARK",
        "historical_wambu_protocol_unchanged": True,
        "models": models, "fixed_compactor_model": anchor,
        "episodes": episodes, "steps": steps, "seed": config["development_seed"],
        "config_sha256": config_digest,
        "source_sha256": digest(json_bytes(src)), "source_digests": src,
        "planned_call_reservations": expected_calls, "max_call_reservations": config["max_calls"],
        "model_role_effect": "DECISION_MODELS_COMPARED_WITH_SINGLE_SHARED_COMPACTOR",
        "split": "development", "holdout_touched": False,
        "author_frozen": False, "scientifically_approved": False,
        "submission_authorized": False, "git_sha": os.environ.get("GITHUB_SHA"),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    save(out / "run_metadata.json", meta)
    client = OpenRouter(secret, out / "provider_ledger.json", config["max_calls"], transport=transport)
    rows, compactions, ids = [], [], set()
    for ep in range(episodes):
        episode = generate_episode(config["development_seed"], "development", ep, steps)
        summary, consumed, depth, summary_failure = "", 0, 0, None
        for item in episode["items"]:
            t = item["step"]
            if t and t % 3 == 0:
                logs = item["history_before"]
                prompt = compaction_prompt(summary, logs[consumed:])
                consumed = len(logs)
                depth += 1
                if summary_failure is None:
                    try:
                        a = client.call(anchor, prompt, config["summary_max_tokens"])
                        if a["response_id"] in ids:
                            raise SafetyPilotError("DUPLICATE_PROVIDER_RESPONSE_ID")
                        ids.add(a["response_id"])
                        summary = a["text"][:5000]
                        compactions.append({
                            "episode_id": episode["episode_id"], "before_step": t,
                            "depth": depth, "summary_text": summary,
                            "response_id": a["response_id"],
                            "observed_model": a["observed_model"],
                            "usage": a["usage"], "prompt_sha256": a["prompt_sha256"],
                            "finish_reason": a["finish_reason"],
                            "error": None,
                        })
                    except (BenchmarkError, SafetyPilotError) as exc:
                        summary_failure = str(exc)[:150]
                        compactions.append({"episode_id": episode["episode_id"],
                                            "before_step": t, "depth": depth,
                                            "error": summary_failure})
            for model in models:
                cached = None
                for arm in PAID_DECISION_CONDITIONS:
                    err = None
                    if summary_failure and arm in ("recursive_summary", "pinned_ledger"):
                        err = "MISSING_COMPACTION:" + summary_failure
                    else:
                        prompt = decision_prompt(item, arm, summary)
                        try:
                            a = client.call(model, prompt, config["decision_max_tokens"])
                            if a["response_id"] in ids:
                                raise SafetyPilotError("DUPLICATE_PROVIDER_RESPONSE_ID")
                            ids.add(a["response_id"])
                            cached = a if arm == "pinned_ledger" else cached
                        except (BenchmarkError, SafetyPilotError) as exc:
                            err = str(exc)[:150]
                            a = None
                    r = record_for(item, model=model, arm=arm, depth=depth,
                                   episode=episode, answer=a if not err else None, error=err)
                    r["reference_action_for_coverage"] = item["reference_action"]
                    rows.append(r)
                g = record_for(item, model=model, arm=POSTPROCESS_CONDITION, depth=depth,
                               episode=episode, answer=cached,
                               error=None if cached else "PINNED_LEDGER_PARENT_UNAVAILABLE", derived=True)
                g["reference_action_for_coverage"] = item["reference_action"]
                rows.append(g)
            save(out / "observations.json", rows)
            save(out / "compactions.json", compactions)
            # A status heartbeat is evidence, not an automatic success claim.
            save(out / "status.partial.json", {
                "classification": meta["classification"], "recorded": len(rows),
                "expected": episodes*steps*len(models)*len(ALL_CONDITIONS),
                "provider_calls_reserved": client.count,
                "scientifically_approved": False, "holdout_touched": False})
    stats = indicators(rows, models, episodes, steps)
    full = all(r["evaluation"] is not None for r in rows)
    source_failed = any(x.get("error") for x in compactions)
    status = "EXPLORATORY_FULLY_SCORED_NOT_SCIENTIFICALLY_APPROVED" if full and not source_failed else "EXPLORATORY_PARTIAL_PROVIDER_OR_COMPACTION_FAILURE"
    result = {"classification": meta["classification"],
              "status": status,
              "models": stats, "provider_calls_reserved": client.count,
              "provider_response_ids_verified_unique": len(ids),
              "expected_evaluable_rows": len(rows),
              "evaluable_rows": sum(r["evaluation"] is not None for r in rows),
              "observed_compactions": sum(x.get("error") is None for x in compactions),
              "expected_compactions": episodes*((steps-1)//3),
              "unit_of_independence": "episode",
              "no_significance_tests_performed": True,
              "information_access_unequal_by_design": True,
              "same_summary_anchor_across_models": True,
              "not_a_public_standardised_safety_benchmark": True,
              "scientifically_approved": False, "submission_authorized": False,
              "holdout_touched": False}
    save(out / "summary.json", result)
    names = ["run_metadata.json", "observations.json", "compactions.json",
             "summary.json", "provider_ledger.json"]
    files = {name: digest((out/name).read_bytes()) for name in names}
    manifest = {
        "classification": meta["classification"],
        "files_sha256": files,
        "source_sha256": meta["source_sha256"],
        "config_sha256": config_digest,
        "scientifically_approved": False, "submission_authorized": False}
    save(out / "manifest.json", manifest)
    return result


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--config", type=Path, default=Path("study/openrouter_policy_models.json"))
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--execute", action="store_true")
    args = p.parse_args(argv)
    if not args.execute:
        p.error("PAID_LIVE_EXECUTION_REQUIRES_EXPLICIT_OPT_IN")
    key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENROUTER")
    r = run(args.config, args.out, key or "")
    print(json.dumps({"status": r["status"],
                      "evaluable_rows": r["evaluable_rows"],
                      "expected_evaluable_rows": r["expected_evaluable_rows"],
                      "provider_calls_reserved": r["provider_calls_reserved"]}, indent=2))
    return 0 if r["status"] == "EXPLORATORY_FULLY_SCORED_NOT_SCIENTIFICALLY_APPROVED" else 3


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (BenchmarkError, SafetyPilotError) as exc:
        raise SystemExit("EXPLORATORY_POLICY_PILOT_BLOCKED:" + str(exc)) from None
