"""Detached P07f AI-methodology evidence audit: no provider calls, no promotion."""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path

from study.openrouter_comparison import digest,save
from scripts.p07f_ai_methodology_experts import (
    manifest, role_prompt, parse_role, synth_prompt, parse_synthesis,
)

def require(ok,reason):
    if not ok:
        raise ValueError(reason)

def audit(root:Path):
    root=root.resolve()
    manifest_sha=manifest(root)
    packetbytes=(root/"blind_model_inputs.json").read_bytes()
    packet=json.loads(packetbytes)
    metadata=json.loads((root/"metadata.json").read_text())
    rows=json.loads((root/"first_round.json").read_text())
    syn=json.loads((root/"syntheses.json").read_text())
    summary=json.loads((root/"summary.json").read_text())
    cases={x["case_id"]:x for x in packet["cases"]}
    roles=metadata["models"]
    require(len(cases)==8 and len(roles)==3 and len(set(roles.values()))==3,
            "INVALID_CASES_OR_ROLE_SET")
    require(metadata["model_inputs_sha256"]==digest(packetbytes)
            and metadata["human_adjudicators"]==0 and
            metadata["author_decision"]=="PENDING_EXPLICIT_REVIEW_OF_SPECIFIC_ARTIFACT",
            "MODEL_INPUT_CHANGED_OR_AUTHOR_FALSELY_APPROVED")
    require(len(rows)==24 and len(syn)==8,"INCOMPLETE_REVIEW_MATRIX")
    seen=set()
    provider_ids=set()
    valid=0
    bycase={}
    for row in rows:
        cid,role=row["case_id"],row["role"]
        require((cid,role) not in seen and cid in cases and role in roles,
                "DUPLICATED_OR_UNDECLARED_ROLE")
        seen.add((cid,role))
        require(row["requested_model"]==roles[role] and
                row["prompt_sha256"]==digest(role_prompt(role,cases[cid]).encode()),
                "ROLE_MODEL_OR_BLIND_PROMPT_TAMPER")
        rid=row.get("provider_response_id")
        if rid is not None:
            require(rid not in provider_ids,"DUPLICATE_PROVIDER_ID")
            provider_ids.add(rid)
        if row["review"] is None:
            require(bool(row.get("error")),"MISSING_FAILURE_EVIDENCE")
            continue
        parsed,unboxed=parse_role(row["raw_text"],cases[cid])
        require(parsed==row["review"] and unboxed==row["normalized_json_fence"],
                "REVIEW_OUTPUT_TAMPER")
        bycase.setdefault(cid,[]).append(row)
        valid+=1
    require(len(seen)==24 and valid==summary["valid_first_round"] and
            len(provider_ids)==summary["provider_response_ids"],
            "UNFAITHFUL_24_REVIEW_SUMMARY")
    syn_by_id={}
    for row in syn:
        cid=row["case_id"]
        require(cid in cases and cid not in syn_by_id,"SYNTHESIS_CASE_ID_DUPLICATE")
        syn_by_id[cid]=row
        prior=bycase.get(cid,[])
        if row["synthesis"] is None:
            require(bool(row.get("error")),"SILENT_FAILED_SYNTHESIS")
        else:
            require(len(prior)==3 and row.get("provider_response_id") not in provider_ids,
                    "INVALID_SYNTHESIS_PROVIDER_OR_MISSING_ROLES")
            provider_ids.add(row["provider_response_id"])
            p=synth_prompt(cases[cid],prior)
            require(row["prompt_sha256"]==digest(p.encode()),
                    "SYNTHESIS_PROMPT_NOT_FROM_THIS_CASE")
            parsed,unboxed=parse_synthesis(row["raw_text"])
            require(parsed==row["synthesis"] and unboxed==row["normalized_json_fence"],
                    "SYNTHESIS_RESPONSE_TAMPER")
    require(len(syn_by_id)==8 and
            sum(x["synthesis"] is not None for x in syn)==summary["valid_syntheses"],
            "INVALID_SYNTHESIS_COUNTS")
    require(summary["human_adjudicators"]==0
            and summary["actual_human_policy_ground_truth"]==0
            and summary["author_approval"]=="PENDING"
            and summary["scientifically_approved"] is False
            and summary["holdout_touched"] is False,
            "AUTOMATIC_SCIENTIFIC_OR_AUTHOR_APPROVAL_FORBIDDEN")
    decisions=Counter(r["review"]["decision"] for r in rows if r["review"])
    require(dict(decisions)==summary["ai_decisions_descriptive_only"],
            "DECISION_SUMMARY_MISMATCH")
    return {
        "schema":"WAMBU-P07F-DETACHED-AI-ONLY-AUDIT-V1",
        "original_manifest_sha256":manifest_sha,
        "original_blind_cases_sha256":digest(packetbytes),
        "cases":8,"first_round_expected":24,
        "first_round_strict_valid":valid,
        "first_round_invalid":24-valid,
        "synthesis_valid":sum(x["synthesis"] is not None for x in syn),
        "ai_role_divergent_cases":sum(len(set(r["review"]["decision"]
                                      for r in bycase.get(cid,[])))>1
                                      for cid in cases),
        "original_provider_ids":len(provider_ids),
        "ai_decision_counts":dict(decisions),
        "same_case_synthesis_only":True,
        "author_final_approval":"PENDING_EXPLICIT_CONTENT_SPECIFIC_REVIEW",
        "qualified_human_adjudicators":0,
        "genuine_human_policy_gold":0,
        "original_knowledge_triage_full_fidelity":False,
        "holdout_touched":False,
        "scientifically_approved":False,
        "new_paid_calls":0,
        "correct_claim":"EXPLORATORY_AI_GENERATED_METHODS_OPINIONS_ONLY",
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--review-dir",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    result=audit(a.review_dir)
    require(not a.out.exists() or not any(a.out.iterdir()),"CANNOT_REWRITE_AUDIT")
    a.out.mkdir(parents=True,exist_ok=True)
    save(a.out/"detached_report.json",result)
    save(a.out/"manifest.json",{
        "report_sha256":digest((a.out/"detached_report.json").read_bytes()),
        "author_approval":"PENDING","human_adjudicators":0,
        "new_paid_calls":0,"scientifically_approved":False})
    print(json.dumps(result,indent=2))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
