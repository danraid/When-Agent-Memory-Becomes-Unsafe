"""Detached, zero-provider-call audit of exact Markdown-fenced JSON vote envelopes.

Original outputs and GitHub Actions failure remain unchanged. This script only
removes a single complete outer JSON code fence and revalidates original evidence.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path

from scripts.p07b_ai_panel import ROLE_MODELS, prompt, parse_vote
from study.openrouter_comparison import digest, save


class PanelAuditError(ValueError):
    pass


def require(ok, reason):
    if not ok:
        raise PanelAuditError(reason)


def check_manifest(root: Path, name: str, field: str) -> tuple[str,int]:
    root = root.resolve()
    path = root / name
    require(path.is_file(), "MISSING_ORIGINAL_MANIFEST")
    manifest = json.loads(path.read_text(encoding="utf-8"))
    files = manifest.get(field)
    require(isinstance(files,dict) and len(files)>=2,"INVALID_MANIFEST_HASHES")
    for fname, expected in files.items():
        f = (root/fname).resolve()
        require(f.is_relative_to(root) and f.is_file(),"ORIGINAL_EVIDENCE_MISSING")
        require(digest(f.read_bytes())==expected,"ORIGINAL_EVIDENCE_TAMPER_DETECTED")
    return digest(path.read_bytes()),len(files)


def remove_exact_envelope(raw: str) -> tuple[str,bool]:
    text = raw.strip()
    prefix = "```json\n"
    suffix = "\n```"
    if text.startswith(prefix) and text.endswith(suffix):
        inner=text[len(prefix):-len(suffix)].strip()
        require("```" not in inner,"NESTED_FENCE_NOT_PERMITTED")
        return inner,True
    return text,False


def audit(source_root:Path, panel_root:Path):
    source_manifest,source_checks=check_manifest(source_root,"source_manifest.json","files_sha256")
    panel_manifest,panel_checks=check_manifest(panel_root,"manifest.json","files_sha256")
    original_source=(source_root/"source_cases_public.json").read_bytes()
    c=json.loads(original_source)
    refs=json.loads((source_root/"reference_sidecar_evaluator_only.json").read_text())
    metadata=json.loads((panel_root/"run_metadata.json").read_text())
    old_summary=json.loads((panel_root/"summary.json").read_text())
    old_votes=json.loads((panel_root/"votes.json").read_text())
    require(metadata["source_cases_sha256"]==digest(original_source),"SOURCE_IDENTITY_MISMATCH")
    require(metadata["models"]==ROLE_MODELS and
            metadata["classification"]=="THREE_BLIND_AI_ROLES_SIMULATED_NOT_HUMAN_INDEPENDENCE",
            "ROLE_OR_CLASSIFICATION_CHANGED")
    require(metadata["human_adjudicators"]==0 and old_summary["human_adjudicators"]==0
            and old_summary["scientifically_approved"] is False,
            "HUMAN_OR_SCIENCE_PROMOTION_FORBIDDEN")
    by_id={x["case_id"]:x for x in c["cases"]}
    labels={x["case_id"]:x["reference_link_status_from_verified_text"]
            for x in refs["references"]}
    require(len(by_id)==12 and set(by_id)==set(labels),"WRONG_CASEBOOK")
    expected={(cid,role) for cid in by_id for role in ROLE_MODELS}
    keys=[(x["case_id"],x["role"]) for x in old_votes]
    require(len(keys)==36 and len(set(keys))==36 and set(keys)==expected,
            "INCOMPLETE_OR_DUPLICATED_VOTE_MATRIX")
    parsed,failed,provider_ids=[],[],set()
    for row in old_votes:
        case=by_id[row["case_id"]]
        require(row["model"]==ROLE_MODELS[row["role"]] and
                row["prompt_sha256"]==digest(prompt(row["role"],case).encode("utf-8")),
                "MODEL_OR_PROMPT_CHANGED")
        provenance=row.get("response")
        if provenance is not None:
            rid=provenance["response_id"]
            require(isinstance(rid,str) and rid and rid not in provider_ids,
                    "DUPLICATE_PROVIDER_RESPONSE_ID")
            require(provenance["prompt_sha256"]==row["prompt_sha256"],
                    "PROVIDER_PROMPT_HASH_MISMATCH")
            provider_ids.add(rid)
        raw=row.get("raw_model_output")
        if raw is None:
            failed.append({"case_id":row["case_id"],"role":row["role"],
                           "reason":row.get("error") or "MISSING_ORIGINAL_RESPONSE"})
            continue
        text,wrapped=remove_exact_envelope(raw)
        try:
            verdict=parse_vote(text,case["source_evidence"]["quoted_line"])
        except ValueError as exc:
            failed.append({"case_id":row["case_id"],"role":row["role"],"reason":str(exc)})
            continue
        parsed.append({
            "case_id":row["case_id"],"role":row["role"],"model":row["model"],
            "verdict":verdict,
            "original_response_id":provenance["response_id"],
            "original_raw_text_sha256":digest(raw.encode("utf-8")),
            "recovered_exact_json_fence":bool(wrapped and row["vote"] is None),
            "original_vote_valid":row["vote"] is not None,
            "reference_sidecar_was_never_in_review_prompt":True,
            "independent_human_adjudication":False,
        })
    grouped=defaultdict(list)
    for x in parsed:
        grouped[x["case_id"]].append(x)
    case_results=[]
    for cid in sorted(by_id):
        rows=grouped[cid]
        votes=[x["verdict"]["decision"] for x in rows]
        complete=len(votes)==3
        unanimous=complete and len(set(votes))==1
        case_results.append({
            "case_id":cid,"expected_literal_document_link":labels[cid],
            "reviewed":len(votes),"ai_unanimous":votes[0] if unanimous else None,
            "ai_disagreement":len(set(votes))>1,
            "votes_matching_reference":sum(x==labels[cid] for x in votes),
            "human_adjudicated":False,
        })
    return {
        "classification":"DETACHED_STRICT_FENCED_JSON_RECOVERY_AI_SIMULATED_ONLY",
        "original_run_status_preserved":old_summary["status"],
        "original_source_manifest_sha256":source_manifest,
        "original_panel_manifest_sha256":panel_manifest,
        "original_evidence_hashes_verified":source_checks+panel_checks,
        "expected_votes":36,"original_strict_valid_votes":sum(x["vote"] is not None for x in old_votes),
        "recovered_fenced_json_votes":sum(x["recovered_exact_json_fence"] for x in parsed),
        "valid_after_envelope_recovery":len(parsed),"unrecoverable":failed,
        "unique_provider_response_ids":len(provider_ids),
        "ai_unanimous_cases":sum(x["ai_unanimous"] is not None for x in case_results),
        "ai_disagreement_cases":sum(x["ai_disagreement"] for x in case_results),
        "ai_votes_matching_study_created_link_reference":sum(x["votes_matching_reference"] for x in case_results),
        "case_results":case_results,"votes":parsed,
        "original_outputs_unmodified":True,"new_paid_calls":0,
        "human_adjudicators":0,"naturalistic_operational_policy_gold":0,
        "original_kt_full_replication":False,
        "protected_holdout_touched":False,"scientifically_approved":False,
        "limits":[
            "Original CI remains a FAILED strict-JSON run, not retroactively passed.",
            "Recovery strips only an exact whole Markdown code fence; JSON content and quote checks are unchanged.",
            "The reference evaluates study-authored literal document-link questions, not independently adjudicated operational decisions.",
            "AI unanimity is not independent human review, scientific validation or journal peer review."
        ],
    }


def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--panel",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args(argv)
    report=audit(args.source,args.panel)
    args.out.mkdir(parents=True,exist_ok=True)
    save(args.out/"normalisation_audit.json",report)
    save(args.out/"audit_manifest.json",{
        "audit_sha256":digest((args.out/"normalisation_audit.json").read_bytes()),
        "original_source_manifest_sha256":report["original_source_manifest_sha256"],
        "original_panel_manifest_sha256":report["original_panel_manifest_sha256"],
        "new_paid_calls":0,"human_adjudicators":0,"scientific_approval":False,
    })
    print(json.dumps({k:report[k] for k in (
        "original_strict_valid_votes","recovered_fenced_json_votes",
        "valid_after_envelope_recovery","ai_unanimous_cases",
        "ai_disagreement_cases","ai_votes_matching_study_created_link_reference",
        "new_paid_calls","human_adjudicators")},indent=2))
    return 0 if not report["unrecoverable"] else 3


if __name__=="__main__":
    raise SystemExit(main())
