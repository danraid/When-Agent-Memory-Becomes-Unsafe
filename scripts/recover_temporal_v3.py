#!/usr/bin/env python3
"""Recover a fully observed v3 *empirical* pilot from its immutable Actions artifact.

No network access, no OpenAI API, no reviewer simulation, no inferential testing
and no confirmatory or journal approval. Original artifact bytes are read-only.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

EXPERIMENT_ARMS = (
    "full_history", "recent_window", "recursive_summary",
    "typed_retention_adapted", "temporal_policy_ledger",
)
GUARD_ARM = "temporal_policy_ledger_guard"


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def recover(original: Path, destination: Path) -> dict:
    empirical = original / "empirical"
    manifest = _load(empirical / "manifest.json")
    if manifest.get("holdout_touched") is not False:
        raise ValueError("HOLDOUT_BOUNDARY_BROKEN")
    if manifest.get("scientifically_approved") is not False:
        raise ValueError("UNAUTHORISED_SCIENTIFIC_APPROVAL")
    if manifest.get("submission_authorized") is not False:
        raise ValueError("UNAUTHORISED_SUBMISSION")
    if len(manifest.get("files", [])) != 4:
        raise ValueError("EMPIRICAL_MANIFEST_INCOMPLETE")
    for recorded in manifest["files"]:
        name = recorded["path"]
        path = (empirical / name).resolve()
        if not path.is_relative_to(empirical.resolve()) or not path.is_file():
            raise ValueError("MANIFEST_PATH_INVALID")
        content = path.read_bytes()
        if len(content) != recorded["bytes"] or hashlib.sha256(content).hexdigest() != recorded["sha256"]:
            raise ValueError("EVIDENCE_HASH_MISMATCH")
    summary = _load(empirical / "summary.json")
    if (empirical / "status.json").read_bytes() != (empirical / "summary.json").read_bytes():
        raise ValueError("STATUS_SUMMARY_MISMATCH")
    if summary.get("mode") != "live" or summary.get("split") != "pilot":
        raise ValueError("NOT_REAL_PILOT")
    if summary.get("status") != "REAL_EXPLORATORY_V3_NOT_SCIENTIFICALLY_APPROVED":
        raise ValueError("UNEXPECTED_STATUS")
    if summary.get("holdout_touched") is not False or summary.get("scientifically_approved") is not False:
        raise ValueError("CONFIRMATORY_BOUNDARY_BROKEN")
    if summary.get("submission_authorized") is not False:
        raise ValueError("UNAUTHORISED_SUBMISSION")
    if (summary.get("episodes"), summary.get("steps")) != (4, 18):
        raise ValueError("UNEXPECTED_EXPERIMENT_SIZE")
    observations = _load(empirical / "observations.json")
    compactions = _load(empirical / "compactions.json")
    if (empirical / "observations.partial.json").read_bytes() != (empirical / "observations.json").read_bytes():
        raise ValueError("PARTIAL_OBSERVATIONS_MISMATCH")
    if (empirical / "compactions.partial.json").read_bytes() != (empirical / "compactions.json").read_bytes():
        raise ValueError("PARTIAL_COMPACTIONS_MISMATCH")
    if len(observations) != 432 or len(compactions) != 20:
        raise ValueError("OBSERVATION_OR_COMPACTION_COUNT_MISMATCH")
    scored = defaultdict(dict)
    empirical_ids = []
    for row in observations:
        if hashlib.sha256(row["prompt"].encode("utf-8")).hexdigest() != row["prompt_sha256"]:
            raise ValueError("MODEL_PROMPT_HASH_MISMATCH")
        identity = row["case_id"]
        arm = row["arm"]
        if arm in scored[identity]:
            raise ValueError("DUPLICATE_ARM_CASE")
        scored[identity][arm] = row
        if arm != GUARD_ARM:
            empirical_ids.append(row["provider_response_id"])
    for row in compactions:
        empirical_ids.append(row["provider_response_id"])
    if len(empirical_ids) != 380 or len(set(empirical_ids)) != 380:
        raise ValueError("PROVIDER_RESPONSE_ID_COUNT_MISMATCH")
    required = set(EXPERIMENT_ARMS) | {GUARD_ARM}
    if len(scored) != 72 or any(set(rows) != required for rows in scored.values()):
        raise ValueError("PAIRING_INCOMPLETE")
    for rows in scored.values():
        guard, raw = rows[GUARD_ARM], rows["temporal_policy_ledger"]
        if (guard["provider_response_id"] != raw["provider_response_id"]
                or guard["raw_response"] != raw["raw_response"]):
            raise ValueError("GUARD_IS_NOT_DERIVED")
    episode_ids = {row["episode_id"] for row in observations}
    if len(episode_ids) != 4:
        raise ValueError("INDEPENDENT_EPISODE_COUNT_MISMATCH")
    arms = {}
    for arm in tuple(EXPERIMENT_ARMS) + (GUARD_ARM,):
        rows = [row for row in observations if row["arm"] == arm]
        revocations = [row for row in rows if row["probe_kind"] == "stale_rule_revocation"]
        enforcement = [row for row in rows if row["probe_kind"] == "new_rule_enforcement"]
        arms[arm] = {
            "cases": len(rows),
            "correct_raw": sum(bool(row["evaluation"]["raw_correct"]) for row in rows),
            "revocation_cases": len(revocations),
            "wrongful_stale_rule_rejections": sum(bool(row["evaluation"]["stale_rule_wrongful_reject"]) for row in revocations),
            "new_enforcement_cases": len(enforcement),
            "missed_new_enforcement": sum(bool(row["evaluation"]["missed_new_enforcement"]) for row in enforcement),
        }
    for arm, values in arms.items():
        if (values["cases"], values["revocation_cases"], values["new_enforcement_cases"]) != (72, 16, 16):
            raise ValueError("PROBE_DENOMINATOR_MISMATCH")
        orig = summary["analysis"]["arms"][arm]
        if (values["wrongful_stale_rule_rejections"] != orig["stale_rule_wrongful_rejections"]
                or values["missed_new_enforcement"] != orig["missed_new_enforcements"]
                or values["correct_raw"] != round(orig["raw_accuracy"] * 72)):
            raise ValueError("ARM_METRIC_MISMATCH")
    paired = summary["analysis"]["paired_post_compaction_episodes"]
    if len(paired) != 4 or any(x["adapted_typed_minus_ledger"] != 0.0 for x in paired):
        raise ValueError("CANDIDATE_CONTRAST_MISMATCH")
    ledger = _load(original / "provider-ledger.json")
    review_exists = (original / "advisory" / "reviewers.json").exists()
    if review_exists:
        raise ValueError("ORIGINAL_ARCHIVE_UNEXPECTED_REVIEWER_RECORD")
    result = {
        "classification": "ORIGINAL_V3_ARTIFACT_RECOVERED_DESCRIPTIVE_ONLY",
        "original_run_id": 43640571248,
        "original_artifact_id": 14131424960,
        "overall_workflow_conclusion": "failure",
        "failure_stage": "post-empirical AI advisory EMPTY_ADVISORY_NO_APPROVAL",
        "experiment_complete": True,
        "empirical_manifest_files_verified": 4,
        "independent_episodes": 4,
        "observed_real_decision_calls": 360,
        "observed_real_compactions": 20,
        "scored_cases_including_derived_guard": 432,
        "distinct_empirical_provider_response_ids": len(empirical_ids),
        "provider_ledger_accounted_calls": ledger["calls"],
        "unmatched_accounted_calls": ledger["calls"] - len(empirical_ids),
        "two_advisory_reviews_completed": False,
        "arms": arms,
        "episode_mean_candidate_difference": 0.0,
        "inference": "NO_CONFIRMATORY_P_VALUES_OR_EQUIVALENCE_CLAIM",
        "knowledge_triage_baseline": "ADAPTED_NOT_FULL_OFFICIAL_REPRODUCTION",
        "holdout_touched": False,
        "scientifically_approved": False,
        "submission_authorized": False,
    }
    if result["unmatched_accounted_calls"] != 1:
        raise ValueError("UNEXPECTED_LEDGER_ACCOUNTING")
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "recovery.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    lines = [
        "# WAMBU-001 v3 | Offline archived evidence recovery",
        "",
        "**Original workflow failed during the AI advisory, after successful empirical verification.**",
        "**Exploratory development evidence only; not an independent confirmation or scientific approval.**",
        "",
        f"- Independent episodes: {result['independent_episodes']}; GPT decisions: 360; compactions: 20.",
        "- Scored arm cases: 432, including 72 derived guard cases.",
        "- SHA-256 manifest evidence files verified: 4; unique experimental response IDs: 380.",
        f"- Original provider ledger accounts for {ledger['calls']} calls; one unmatched to completed empirical responses.",
        "- Neither advisory reviewers.json nor a final review report was produced.",
        "",
        "| Arm | Raw correct / 72 | Wrongful revocations / 16 | Missed enforcement / 16 |",
        "| --- | ---: | ---: | ---: |",
    ]
    for arm, val in arms.items():
        lines.append(f"| {arm} | {val['correct_raw']}/72 | {val['wrongful_stale_rule_rejections']}/16 | {val['missed_new_enforcement']}/16 |")
    lines += [
        "",
        "**Candidate episode-average contrast: 0.0000. This is not a statistical equivalence result.**",
        "The adapted typed comparator is NOT the full published Knowledge Triage method.",
        "Confirmatory split remains untouched. No journal approval or submission.",
        "",
        "Sources: https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/43640571248",
        "Original artifact: https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/43640571248/artifacts/14131424960",
    ]
    (destination / "recovery.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--original", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    result = recover(args.original, args.out)
    print(json.dumps({k: result[k] for k in (
        "classification", "independent_episodes", "observed_real_decision_calls",
        "observed_real_compactions", "distinct_empirical_provider_response_ids",
        "two_advisory_reviews_completed", "scientifically_approved",
    )}, indent=2))


if __name__ == "__main__":
    main()
