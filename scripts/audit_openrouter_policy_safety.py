#!/usr/bin/env python3
"""Detached audit of a version-pinned OpenRouter policy-safety development run.

No network, paid model, private holdout or human adjudicator involved. It verifies
original artifact digests FIRST; then reconstructs all simulator cases from the
public development seed, independently recomputes original evaluations and prompts,
and reports missingness without imputation. This audits reproducibility, not science.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

from study.tasks import generate_episode
from study.prompts import (
    ALL_CONDITIONS, PAID_DECISION_CONDITIONS, POSTPROCESS_CONDITION,
    compaction_prompt, decision_prompt,
)
from study.analysis import evaluate
from study.openrouter_comparison import digest, json_bytes, save


class DetachedAuditError(ValueError):
    pass


def require(condition: bool, message: str):
    if not condition:
        raise DetachedAuditError(message)


def verified_json(root: Path, filename: str, expected: str):
    target = (root / filename).resolve()
    require(target.is_relative_to(root.resolve()) and target.is_file(),
            "MISSING_OR_TRAVERSING_SOURCE_FILE:" + filename)
    require(digest(target.read_bytes()) == expected,
            "EVIDENCE_DIGEST_MISMATCH:" + filename)
    return json.loads(target.read_text(encoding="utf-8"))


def audit(root: Path, source_root: Path) -> dict:
    root = root.resolve()
    source_root = source_root.resolve()
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    require(manifest.get("scientifically_approved") is False and
            manifest.get("submission_authorized") is False,
            "UNAUTHORISED_MANIFEST_PROMOTION")
    hashes = manifest.get("files_sha256")
    require(isinstance(hashes, dict) and len(hashes) >= 5,
            "INVALID_OR_INCOMPLETE_ORIGINAL_MANIFEST")
    evidence = {name: verified_json(root, name, expected)
                for name, expected in sorted(hashes.items())}
    meta, rows, compactions, summary, ledger = (
        evidence["run_metadata.json"], evidence["observations.json"],
        evidence["compactions.json"], evidence["summary.json"],
        evidence["provider_ledger.json"],
    )
    require(meta.get("study_id") == "WAMBU-001-OPENROUTER-SAFETY-DEV-V2" and
            meta.get("split") == "development" and
            meta.get("author_frozen") is False and
            meta.get("holdout_touched") is False and
            summary.get("holdout_touched") is False and
            summary.get("scientifically_approved") is False and
            summary.get("submission_authorized") is False,
            "INVALID_SCIENTIFIC_OR_SPLIT_STATUS")
    require(meta.get("git_sha") and isinstance(meta.get("git_sha"), str),
            "MISSING_EXECUTABLE_COMMIT_SHA")
    require(isinstance(meta.get("source_digests"), dict) and
            len(meta["source_digests"]) >= 5,
            "MISSING_SOURCE_DIGEST_SET")
    for path, expected in meta["source_digests"].items():
        target = (source_root / path).resolve()
        require(target.is_relative_to(source_root) and target.is_file(),
                "MISSING_PINNED_SOURCE:" + path)
        require(digest(target.read_bytes()) == expected,
                "PINNED_SOURCE_DIGEST_MISMATCH:" + path)
    require(digest(json_bytes(meta["source_digests"])) == meta["source_sha256"],
            "SOURCE_COLLECTION_DIGEST_MISMATCH")
    cfg_path = source_root / "study/openrouter_policy_v2_models.json"
    require(cfg_path.is_file() and digest(cfg_path.read_bytes()) == meta["config_sha256"],
            "CONFIG_DIGEST_MISMATCH")
    config = json.loads(cfg_path.read_text(encoding="utf-8"))
    n, steps, models = meta["episodes"], meta["steps"], meta["models"]
    require(n == 4 and steps == 18 and models == config["decision_models"],
            "DESIGN_MATRIX_MISMATCH")
    require(meta["fixed_compactor_model"] == config["summary_anchor_model"],
            "COMPACTOR_IDENTITY_MISMATCH")
    require(meta["pacing_intervals"] == config["model_min_interval_seconds"] and
            meta["cooldown_after_429_seconds"] == config["cooldown_after_429_seconds"],
            "PACING_POLICY_MISMATCH")
    assert len(ALL_CONDITIONS) == 5
    require(len(rows) == n * steps * len(models) * len(ALL_CONDITIONS),
            "MISSING_OR_SURPLUS_OBSERVATION_ROWS")
    require(len(compactions) == n * ((steps - 1) // 3),
            "MISSING_OR_SURPLUS_COMPACTIONS")
    index = {}
    for row in rows:
        key = (row["episode_id"], row["step"], row["requested_model"], row["condition"])
        require(key not in index, "DUPLICATE_CASE_MODEL_ARM")
        index[key] = row
    compaction_index = {}
    for c in compactions:
        key = (c["episode_id"], c["before_step"])
        require(key not in compaction_index, "DUPLICATE_COMPACTION_STEP")
        compaction_index[key] = c
    observed_ids = set()
    errors = Counter()
    recomputed = {}
    per_episode_cases = []
    eligible_pairs = {model: [] for model in models}

    for i in range(n):
        episode = generate_episode(meta["seed"], "development", i, steps)
        ep_id = episode["episode_id"]
        summary_text = ""
        consumed = 0
        depth = 0
        episode_reject_after_depth2 = []
        for item in episode["items"]:
            t = item["step"]
            if t and t % 3 == 0:
                c = compaction_index.get((ep_id, t))
                require(c is not None and c.get("error") is None,
                        "MISSING_OR_FAILED_COMPACTION:" + ep_id + ":" + str(t))
                depth += 1
                require(c["depth"] == depth and c["before_step"] == t,
                        "INVALID_COMPACTION_DEPTH")
                logs = item["history_before"]
                source_prompt = compaction_prompt(summary_text, logs[consumed:])
                require(c["prompt_sha256"] == digest(source_prompt.encode("utf-8")),
                        "COMPACTION_PROMPT_DIGEST_MISMATCH")
                consumed = len(logs)
                summary_text = c["summary_text"]
                require(isinstance(summary_text, str) and summary_text,
                        "EMPTY_COMPACTED_MEMORY")
                rid = c["response_id"]
                require(isinstance(rid, str) and rid and rid not in observed_ids,
                        "DUPLICATE_OR_MISSING_COMPACTION_RESPONSE_ID")
                observed_ids.add(rid)
            if depth >= 2 and item["reference_action"] == "reject":
                episode_reject_after_depth2.append(t)
            for model in models:
                by_arm = {}
                for arm in ALL_CONDITIONS:
                    key = (ep_id, t, model, arm)
                    r = index.get(key)
                    require(r is not None, "MISSING_PAIRED_CASE:" + str(key))
                    by_arm[arm] = r
                    require(r["case_id"] == f"{ep_id}-{t:02d}" and
                            r["episode_public_sha256"] == episode["public_content_sha256"] and
                            r["policy_version"] == item["policy_version"] and
                            r["compaction_depth"] == depth and
                            r["reference_action_for_coverage"] == item["reference_action"],
                            "REFERENCE_OR_PAIRING_DIVERGENCE:" + str(key))
                    if r["evaluation"] is None:
                        require(isinstance(r.get("error"), str) and r["error"],
                                "MISSING_CASE_WITHOUT_CAUSE:" + str(key))
                        errors[(model, arm, r["error"])] += 1
                        require(r.get("provider_response_id") is None,
                                "ERROR_WITH_PROVIDER_SUCCESS_ID")
                        continue
                    require(r.get("error") is None and
                            isinstance(r.get("raw_response"), str) and
                            r["raw_response"],
                            "UNEXPLAINED_EVALUATED_CASE")
                    expected_eval = evaluate(item, r["raw_response"],
                                             guarded=(arm == POSTPROCESS_CONDITION))
                    require(r["evaluation"] == expected_eval,
                            "REFERENCE_EVALUATION_MISMATCH:" + str(key))
                    if arm in PAID_DECISION_CONDITIONS:
                        prompt = decision_prompt(item, arm, summary_text)
                        require(r["prompt_sha256"] == digest(prompt.encode("utf-8")),
                                "PAID_DECISION_PROMPT_DIGEST_MISMATCH:" + str(key))
                        rid = r["provider_response_id"]
                        require(isinstance(rid, str) and rid and rid not in observed_ids,
                                "DUPLICATE_OR_MISSING_PAID_RESPONSE_ID")
                        observed_ids.add(rid)
                parent, guard = by_arm["pinned_ledger"], by_arm[POSTPROCESS_CONDITION]
                require(guard.get("derived_from") == "pinned_ledger",
                        "INVALID_GUARD_LINEAGE")
                if parent["evaluation"] is None:
                    require(guard["evaluation"] is None and
                            guard["error"] == "PINNED_LEDGER_PARENT_UNAVAILABLE",
                            "UNSUPPORTED_GUARD_WITH_MISSING_PARENT")
                else:
                    require(guard["evaluation"] is not None and
                            guard["provider_response_id"] == parent["provider_response_id"] and
                            guard["raw_response"] == parent["raw_response"] and
                            guard["prompt_sha256"] == parent["prompt_sha256"],
                            "GUARD_PARENT_PROVENANCE_MISMATCH")
            if depth >= 2 and item["reference_action"] == "reject":
                for model in models:
                    naive = index[(ep_id, t, model, "recursive_summary")]
                    pinned = index[(ep_id, t, model, "pinned_ledger")]
                    eligible_pairs[model].append((ep_id, naive, pinned))
        require(len(episode_reject_after_depth2) >= 4,
                "INSUFFICIENT_POST_COMPACTION_REJECTS")
        per_episode_cases.append({"episode": ep_id,
                                  "post_depth2_reject_opportunities":
                                      len(episode_reject_after_depth2)})
    require(summary["provider_response_ids_verified_unique"] == len(observed_ids),
            "RESPONSE_ID_COUNT_MISMATCH")
    require(summary["provider_calls_reserved"] == ledger["reserved_calls"] ==
            meta["planned_call_reservations"] == n * (5 + 18 * 16),
            "PROVIDER_RESERVATION_COUNT_MISMATCH")
    scored = sum(r["evaluation"] is not None for r in rows)
    require(scored == summary["evaluable_rows"] and
            len(rows) == summary["expected_evaluable_rows"],
            "COVERAGE_COUNT_MISMATCH")

    model_results = {}
    for model in models:
        arm_stats = {}
        for arm in ALL_CONDITIONS:
            sample = [r for r in rows if r["requested_model"] == model
                      and r["condition"] == arm]
            valid = [r for r in sample if r["evaluation"] is not None]
            reject = [r for r in valid if r["evaluation"]["reference_action"] == "reject"]
            approve = [r for r in valid if r["evaluation"]["reference_action"] == "approve"]
            arm_stats[arm] = {
                "scored": len(valid), "expected": len(sample),
                "reject_opportunities_scored": len(reject),
                "reject_opportunities_expected": sum(
                    r["reference_action_for_coverage"] == "reject" for r in sample),
                "unsafe_raw": sum(r["evaluation"]["unsafe_raw_approval"] for r in reject),
                "unsafe_final": sum(r["evaluation"]["unsafe_final_approval"] for r in reject),
                "valid_approvals_scored": len(approve),
                "false_rejections": sum(r["evaluation"]["false_final_reject"] for r in approve),
                "invalid_output_count": sum(r["evaluation"]["invalid_output"] for r in valid),
                "guard_overrides": sum(r["evaluation"]["guard_overrode"] for r in valid),
            }
            original = summary["models"][model][arm]
            check = {"evaluable": "scored", "expected": "expected",
                     "reference_reject_opportunities_evaluable": "reject_opportunities_scored",
                     "reference_reject_opportunities_expected": "reject_opportunities_expected",
                     "unsafe_raw_approvals": "unsafe_raw",
                     "unsafe_final_approvals": "unsafe_final",
                     "false_final_rejections": "false_rejections",
                     "invalid_outputs": "invalid_output_count", "guard_overrides": "guard_overrides"}
            for key, target in check.items():
                require(original[key] == arm_stats[arm][target],
                        "AGGREGATE_DISCREPANCY:" + model + ":" + arm + ":" + key)

        ep_results = []
        for ep in range(n):
            ep_id = f"development-{ep:04d}"
            matching = [(a, b) for observed_ep, a, b in eligible_pairs[model]
                        if observed_ep == ep_id]
            paired = [(a,b) for a,b in matching if a["evaluation"] and b["evaluation"]]
            effect = (sum(int(a["evaluation"]["unsafe_raw_approval"]) -
                          int(b["evaluation"]["unsafe_raw_approval"])
                          for a,b in matching) / len(matching)
                      if len(paired) == len(matching) else None)
            original = summary["models"][model]["candidate_episode_pairing"][ep]
            require(original["episode_id"] == ep_id and
                    original["eligible_rejects"] == len(matching) and
                    original["paired_evaluable_rejects"] == len(paired) and
                    original["episode_risk_difference_if_complete"] == effect,
                    "EPISODE_EFFECT_MISMATCH:" + model + ":" + ep_id)
            ep_results.append({"episode_id": ep_id, "eligible": len(matching),
                               "paired_evaluable": len(paired),
                               "risk_difference_if_complete": effect})
        effects = [r["risk_difference_if_complete"] for r in ep_results]
        average = sum(effects)/n if all(x is not None for x in effects) else None
        require(average == summary["models"][model]["candidate_mean_difference_descriptive_only"],
                "PRIMARY_CONTRAST_MISMATCH:" + model)
        model_results[model] = {
            "arms": arm_stats, "primary_episode_contrasts": ep_results,
            "mean_episode_risk_difference_if_complete": average,
        }

    return {
        "classification": "DETACHED_REPRODUCIBILITY_AUDIT_EXPLORATORY_ONLY",
        "original_run_git_sha": meta["git_sha"],
        "original_status": summary["status"],
        "original_manifest_sha256": digest((root/"manifest.json").read_bytes()),
        "original_config_sha256": meta["config_sha256"],
        "original_source_sha256": meta["source_sha256"],
        "original_evidence_files_verified": len(hashes),
        "expected_rows": len(rows), "scored_rows": scored,
        "coverage": scored/len(rows),
        "compactions": len(compactions),
        "provider_calls_reserved_not_billing": summary["provider_calls_reserved"],
        "distinct_paid_provider_response_ids": len(observed_ids),
        "errors": [{"model": model, "arm": arm, "error": error, "count": count}
                   for (model, arm, error), count in sorted(errors.items())],
        "eligible_cases_by_episode": per_episode_cases,
        "models": model_results,
        "unit_of_independence": "episode",
        "holdout_touched": False, "scientifically_approved": False,
        "submission_authorized": False,
        "limitations": [
            "Recomputing the source-pinned simulator evaluator checks reproducibility, not independent semantic validity.",
            "Four synthetic episodes are not powered for inferential claims.",
            "Different memory arms have unequal authoritative information access.",
            "Qwen and other model outputs may include provider-specific version drift.",
            "Incomplete model-arm outcomes are not imputed or re-run.",
            "The public benchmark LongMemEval is a separate Q&A study, not this safety outcome.",
            "No independent human adjudication, naturalistic case validation or official full-method comparator."
        ],
    }


def markdown(a: dict) -> str:
    lines = [
        "# WAMBU-001 | Detached policy-safety development audit",
        "",
        f"**Historical run status:** \`{a['original_status']}\`.",
        f"**Scored coverage:** {a['scored_rows']}/{a['expected_rows']} ({a['coverage']:.2%}).",
        f"**Compactions:** {a['compactions']}; **evidence digests matched:** {a['original_evidence_files_verified']}.",
        "**Scientific status:** exploratory development, no confirmatory inference.",
        "",
        "| Model | Full history | Recent | Recursive summary | Authorised ledger | Guard (final) |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for model, result in a["models"].items():
        vals = []
        for arm in ALL_CONDITIONS:
            g = result["arms"][arm]
            n = g["reject_opportunities_scored"]
            unsafe = g["unsafe_final"] if arm == POSTPROCESS_CONDITION else g["unsafe_raw"]
            vals.append(f"{unsafe}/{n} ({g['scored']}/{g['expected']} scored)")
        lines.append("| "+model+" | "+" | ".join(vals)+" |")
    lines.extend(["","## Primary exploratory episode risk difference",
                  "Raw unsafe approval rate, recursive summary minus authorised ledger. "
                  "Each episode is an independent unit; no p-values, no model rank.",
                  ""])
    for model, result in a["models"].items():
        diff = result["mean_episode_risk_difference_if_complete"]
        display = "unavailable: incomplete matched cases" if diff is None else f"{diff:+.4f}"
        lines.append(f"- **{model}:** {display}; episode effects "
                     + ", ".join("NA" if ep["risk_difference_if_complete"] is None
                                 else f"{ep['risk_difference_if_complete']:+.4f}"
                                 for ep in result["primary_episode_contrasts"]))
    lines.extend(["", "## Missing provider outcomes (no re-use or imputation)", ""])
    for er in a["errors"]:
        lines.append(f"- {er['model']}, {er['arm']}: {er['count']} × \`{er['error']}\`")
    lines.extend(["", "## Limitations", ""])
    lines.extend("- " + t for t in a["limitations"])
    lines.append("")
    return "\n".join(lines)


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, type=Path)
    p.add_argument("--source-root", type=Path, default=Path("."))
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args(argv)
    result = audit(args.input, args.source_root)
    args.out.mkdir(parents=True, exist_ok=True)
    save(args.out/"audit.json", result)
    (args.out/"audit.md").write_text(markdown(result), encoding="utf-8")
    manifest = {
        "source_artifact_manifest_sha256": result["original_manifest_sha256"],
        "audit_json_sha256": digest((args.out/"audit.json").read_bytes()),
        "audit_md_sha256": digest((args.out/"audit.md").read_bytes()),
        "scientifically_approved": False,
    }
    save(args.out/"audit_manifest.json", manifest)
    print(json.dumps({"status": result["original_status"],
                      "scored": result["scored_rows"],
                      "expected": result["expected_rows"],
                      "verified_evidence_files": result["original_evidence_files_verified"]}))
    return 0


if __name__ == "__main__":
    main()
