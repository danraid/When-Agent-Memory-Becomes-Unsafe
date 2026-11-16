"""Detached, zero-call historical PR-source and AI-review audit.

Correctness here means recorded disposition from public GitHub, NOT a human
gold adjudication of an agent's authorised actions. Original source and AI
manifests are checked before any case is parsed.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path

from scripts.p07c_simulated_expert_panel import ROLES, parse_vote, reviewer_prompt
from study.openrouter_comparison import digest, save


def check_manifest(root:Path):
    root=root.resolve()
    m=json.loads((root/"manifest.json").read_text())
    files=m.get("sha256")
    if not isinstance(files,dict) or len(files)<3:
        raise ValueError("INVALID_SOURCE_MANIFEST")
    for name,expected in files.items():
        p=(root/name).resolve()
        if not p.is_relative_to(root) or not p.is_file() or digest(p.read_bytes())!=expected:
            raise ValueError("SOURCE_EVIDENCE_TAMPER_OR_MISSING:"+name)
    return digest((root/"manifest.json").read_bytes()),len(files)


def audit(source_dir:Path, reviews_dir:Path)->dict:
    source_m,schecks=check_manifest(source_dir)
    reviews_m,rchecks=check_manifest(reviews_dir)
    cases=json.loads((source_dir/"model_inputs_no_outcome.json").read_text())
    reference=json.loads((source_dir/"observed_outcomes_evaluator_only.json").read_text())
    raw=json.loads((source_dir/"raw_external_github_sources.json").read_text())
    metadata=json.loads((reviews_dir/"metadata.json").read_text())
    reviewed=json.loads((reviews_dir/"raw_reviews.json").read_text())
    if cases["case_count"]!=8 or metadata["original_model_inputs_sha256"]!=digest(
            (source_dir/"model_inputs_no_outcome.json").read_bytes()):
        raise ValueError("MODEL_INPUT_MISMATCH")
    if metadata["role_models"]!=ROLES or len(reviewed)!=24:
        raise ValueError("INVALID_AI_ROLE_MATRIX")
    bycase={x["case_id"]:x for x in cases["cases"]}
    outcomes={x["case_id"]:x for x in reference["observed_outcomes"]}
    if len(bycase)!=8 or set(bycase)!=set(outcomes):
        raise ValueError("SOURCE_CASE_LABEL_COVERAGE_MISMATCH")
    for record in raw["original_api_payloads"]:
        cid=record["case_id"]
        ref=outcomes[cid]
        p=record["pr"]
        if p["number"]!=ref["number"] or p["state"]!="closed" or (
                ("merged" if p.get("merged_at") else "closed_without_merge")
                !=ref["observed_disposition"]):
            raise ValueError("ORIGINAL_GITHUB_OUTCOME_MISMATCH")
        if digest(json.dumps(p,sort_keys=True,ensure_ascii=False).encode())!=ref["original_pr_snapshot_sha256"]:
            raise ValueError("GITHUB_SOURCE_PR_DIGEST_MISMATCH")
    seen=set()
    provider_ids=set()
    summary=defaultdict(list)
    errors=[]
    for row in reviewed:
        cid,role=row["case_id"],row["role"]
        if (cid,role) in seen or cid not in bycase or role not in ROLES:
            raise ValueError("DUPLICATE_UNDECLARED_REVIEW")
        seen.add((cid,role))
        c=bycase[cid]
        if row["requested_model"]!=ROLES[role] or row["prompt_sha256"]!=digest(
                reviewer_prompt(role,c).encode()):
            raise ValueError("REVIEWER_MODEL_OR_BLIND_PROMPT_CHANGED")
        rid=row.get("original_provider_response_id")
        if rid:
            if rid in provider_ids:
                raise ValueError("DUPLICATE_ORIGINAL_PROVIDER_ID")
            provider_ids.add(rid)
        if row["vote"] is None:
            errors.append({"case_id":cid,"role":role,"error":row["failure"]})
            continue
        v,unwrapped=parse_vote(row["original_model_text"],c)
        if v!=row["vote"] or unwrapped != row["json_envelope_unwrapped"]:
            raise ValueError("AI_REVIEW_RATIONALE_OR_EVIDENCE_TAMPER")
        summary[cid].append(v["disposition"])
    if len(seen)!=8*len(ROLES):
        raise ValueError("MISSING_AI_ROLE_PAIR")
    contrasts=[]
    for cid in sorted(bycase):
        obs=outcomes[cid]["observed_disposition"]
        votes=summary[cid]
        contrasts.append({
            "case_id":cid,"source_pr_url":outcomes[cid]["original_pr_url"],
            "factual_observed_disposition":obs,
            "n_valid_ai_votes":len(votes),
            "n_votes_matching_factual_disposition":sum(x==obs for x in votes),
            "n_ai_abstentions":sum(x=="insufficient_evidence" for x in votes),
            "ai_unanimity":len(votes)==3 and len(set(votes))==1,
            "human_scientific_gold":False,
        })
    return {
        "classification":"DETACHED_HISTORICAL_GOVERNANCE_AI_SIMULATION_AUDIT",
        "original_source_manifest_sha256":source_m,
        "original_ai_manifest_sha256":reviews_m,
        "verified_source_and_review_files":schecks+rchecks,
        "actual_closed_public_pr_events":8,
        "factual_merged":sum(x["observed_disposition"]=="merged" for x in outcomes.values()),
        "factual_closed_without_merge":sum(x["observed_disposition"]=="closed_without_merge" for x in outcomes.values()),
        "expected_votes":24,"valid_votes":sum(len(v) for v in summary.values()),
        "review_errors":errors,
        "ai_votes_matching_historical_disposition":sum(c["n_votes_matching_factual_disposition"] for c in contrasts),
        "ai_abstentions":sum(c["n_ai_abstentions"] for c in contrasts),
        "ai_unanimous_cases":sum(c["ai_unanimity"] for c in contrasts),
        "case_results":contrasts,
        "historical_merge_is_not_policy_action_gold":True,
        "historical_body_could_be_edited_after_decision":True,
        "qualified_independent_human_adjudicators":0,
        "real_observed_governance_dispositions":8,
        "real_observed_policy_authorisation_decisions":0,
        "full_original_knowledge_triage_reproduced":False,
        "new_paid_calls":0,
        "scientifically_approved":False,
        "private_holdout_touched":False,
        "limits":[
            "Factual public merge/closure events are not normative judgements of correctness.",
            "Retrospective GitHub PR bodies/titles may reflect edits made after closure; timestamped comments are pre-closure filtered.",
            "Historical status can be memorised by a pretrained model even if the model prompt omits the explicit outcome.",
            "Three different AI vendors do not constitute independent qualified human experts.",
            "This case family measures prediction of governance dispositions, not memory compaction failure propagation.",
        ],
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True,type=Path)
    p.add_argument("--reviews",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    result=audit(a.source,a.reviews)
    a.out.mkdir(parents=True,exist_ok=True)
    save(a.out/"detached_audit.json",result)
    save(a.out/"manifest.json",{
        "detached_audit_sha256":digest((a.out/"detached_audit.json").read_bytes()),
        "new_paid_calls":0,
        "scientifically_approved":False,
    })
    print(json.dumps({k:result[k] for k in (
        "actual_closed_public_pr_events","factual_merged",
        "factual_closed_without_merge","valid_votes","expected_votes",
        "ai_votes_matching_historical_disposition","ai_unanimous_cases",
        "qualified_independent_human_adjudicators")},indent=2))


if __name__=="__main__":
    main()
