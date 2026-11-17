"""Detached original-evidence P10 advisory audit. Zero new model calls."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

from study.openrouter_comparison import digest, save
from scripts.p10_ai_scientific_independent_panel import (
    ROOT, ALLOWED, prompts, interpret, chair_prompt, require,
)


def checked(out:Path):
    root=out.resolve()
    manifest=json.loads((root/"manifest.json").read_text())
    files=manifest.get("sha256",{})
    require(len(files)>=5,"ORIGINAL_EVIDENCE_INCOMPLETE")
    for name,sha in files.items():
        p=(root/name).resolve()
        require(p.is_relative_to(root) and p.is_file() and
                digest(p.read_bytes())==sha,"ORIGINAL_EVIDENCE_MISMATCH:"+name)
    return digest((root/"manifest.json").read_bytes())


def audit(config:Path, original:Path):
    manifest_sha=checked(original)
    cfg,cfg_raw,ledger,sources,items=prompts(config)
    meta=json.loads((original/"metadata.json").read_text())
    records=json.loads((original/"original_independent_reviews.json").read_text())
    chair=json.loads((original/"original_ai_chair.json").read_text())
    summary=json.loads((original/"summary.json").read_text())
    paper=(ROOT/cfg["manuscript"]).read_text()
    require(meta["manuscript_sha256"]==digest(paper.encode())
            and meta["config_sha256"]==digest(cfg_raw)
            and meta["claim_ledger_sha256"]==digest(
                (ROOT/cfg["claim_ledger"]).read_bytes()),
            "REVIEWED_SOURCE_AND_CONFIG_NOT_IDENTICAL")
    require(len(items)==len(records)==4,"INCOMPLETE_AI_PANEL")
    require(meta["selected_source_sha256"]=={
        k:v["source_sha256"] for k,v in sources.items()},
        "SOURCE_PROVENANCE_SHA_CHANGED")
    seen=set()
    valid=0
    for (role,prompt,selected), row in zip(items,records):
        require(row["reviewer_id"]==role["id"] and
                row["requested_model"]==role["model"] and
                row["prompt_sha256"]==digest(prompt.encode()),
                "BLIND_PROMPT_OR_MODEL_CHANGED")
        rid=row.get("response_id")
        if rid:
            require(rid not in seen,"DUPLICATE_PROVIDER_ID")
            seen.add(rid)
        if row["review"] is not None:
            exact=interpret(row["original_response_text"],selected,paper)
            require(exact==row["review"],"ORIGINAL_AI_REVIEW_TAMPER")
            valid+=1
        else:
            require(row.get("error"),"MISSING_ERROR_FOR_INVALID_AI_ROLE")
    expected_chair=chair_prompt(meta["manuscript_sha256"],records)
    require(chair["prompt_sha256"]==digest(expected_chair.encode())
            and chair["model"]==cfg["chair"]["model"],
            "AI_CHAIR_EVIDENCE_CHANGED")
    if chair["response_id"]:
        require(chair["response_id"] not in seen,"DUPLICATE_CHAIR_RESPONSE_ID")
        seen.add(chair["response_id"])
    chair_valid=chair["decision"] is not None
    if chair_valid:
        from scripts.p07b_detached_panel_audit import remove_exact_envelope
        raw,_=remove_exact_envelope(chair["original_response_text"])
        require(json.loads(raw)==chair["decision"],"AI_CHAIR_DECISION_TAMPER")
        require(chair["decision"]["advisory_recommendation"] in ALLOWED
                and chair["decision"]["author_final_decision"] is None
                and chair["decision"]["human_independent_review_completed"] is False
                and chair["decision"]["confirmatory_validated"] is False,
                "FORBIDDEN_CHAIR_PROMOTION")
    else:
        require(chair.get("error"),"CHAIR_INVALID_BUT_ERROR_MISSING")
    require(summary["number_of_reviewers_valid"]==valid and
            summary["chair_valid"]==chair_valid and
            summary["human_independent_scientific_reviewers"]==0
            and summary["author_final_decision"] is None
            and summary["heldout_private_sample_touched"] is False
            and summary["scientifically_approved"] is False,
            "SUMMARY_STATUS_INCONSISTENCY")
    return {
        "schema":"WAMBU-P10-DETACHED-AI-ADVISORY-ORIGINAL-REPLAY-V1",
        "classification":"AI_ONLY_INDEPENDENT_PROVIDER_REVIEW_NOT_HUMAN_SCIENCE_CONFIRMATION",
        "original_artifact_manifest_sha256":manifest_sha,
        "original_manuscript_sha256":meta["manuscript_sha256"],
        "original_config_sha256":meta["config_sha256"],
        "original_source_hashes_verified":len(sources),
        "reviewers_expected":4,"valid_original_reviewer_outputs":valid,
        "chair_valid":chair_valid,"unique_original_provider_response_ids":len(seen),
        "advisory_recommendation":chair["decision"]["advisory_recommendation"] if chair_valid else None,
        "human_scientific_reviewers":0,"author_final_decision":None,
        "pre_registered_confirmation":False,
        "confirmatory_result":False,"protected_holdout_touched":False,
        "full_original_knowledge_triage_replication":False,
        "scientifically_approved":False,"journal_submitted":False,
        "new_paid_calls":0,
        "scientific_qualification":"P10_AI_ONLY_ADVISORY_COMPLETE" if valid==4 and chair_valid
            else "P10_AI_ONLY_ADVISORY_PARTIAL",
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--config",type=Path,
                   default=ROOT/"protocol/P10_AI_MANAGED_SCIENTIFIC_REVIEW_V1.json")
    p.add_argument("--original",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    result=audit(a.config,a.original)
    a.out.mkdir(parents=True,exist_ok=True)
    save(a.out/"detached_audit.json",result)
    save(a.out/"manifest.json",{
        "sha256":digest((a.out/"detached_audit.json").read_bytes()),
        "author_final_decision":None,"new_paid_calls":0,
        "human_scientific_reviewers":0,"confirmatory_result":False})
    print(json.dumps(result,indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
