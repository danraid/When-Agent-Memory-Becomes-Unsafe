"""Read-only source and AI audit of actual P07d code-change observations.

No extra provider calls. Historical PR merge outcome is a factual descriptor,
not a normative 'correct policy' reference label; all invalid outputs retained.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import json
from pathlib import Path

from scripts.p07d_code_expert_simulation import ROLES,parse_vote,prompt
from study.openrouter_comparison import digest,save


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def checked(root:Path,name="manifest.json"):
    root=root.resolve()
    m=root/name
    require(m.is_file(),"MISSING_IMMUTABLE_EVIDENCE_MANIFEST")
    obj=json.loads(m.read_text())
    hashes=obj.get("files_sha256") or obj.get("sha256")
    require(isinstance(hashes,dict) and len(hashes)>=3,"INCOMPLETE_EVIDENCE")
    for name,sha in hashes.items():
        p=(root/name).resolve()
        require(p.is_relative_to(root) and p.is_file()
                and digest(p.read_bytes())==sha,
                "MISSING_OR_TAMPERED_SOURCE_OR_RESPONSE:"+name)
    return len(hashes),digest(m.read_bytes())


def audit(source:Path,reviews:Path):
    n_source,sha_source=checked(source)
    n_reviews,sha_reviews=checked(reviews)
    blind_bytes=(source/"blind_code_cases.json").read_bytes()
    blind=json.loads(blind_bytes)
    observed=json.loads((source/"observed_dispositions_evaluator_only.json").read_text())
    original=json.loads((source/"raw_original_sources.json").read_text())
    meta=json.loads((reviews/"metadata.json").read_text())
    rows=json.loads((reviews/"reviews.json").read_text())
    summary=json.loads((reviews/"summary.json").read_text())
    require(meta["casebook_sha256"]==digest(blind_bytes)
            and meta["models"]==ROLES
            and meta["human_reviewers"]==0
            and summary["scientifically_approved"] is False,
            "UNTRUSTED_OR_PROMOTED_PANEL")
    bycase={c["case_id"]:c for c in blind["cases"]}
    ref={x["case_id"]:x for x in observed["events"]}
    receipts={x["case_id"]:x for x in original["source_pr_metadata"]}
    require(len(bycase)==len(ref)==len(receipts)==8
            and set(bycase)==set(ref)==set(receipts),
            "CASE_OR_REFERENCE_MISMATCH")
    for cid,entry in receipts.items():
        factual=ref[cid]
        p=entry["original_pr"]
        files=entry["original_changed_files"]
        require(p["number"]==factual["pr"] and
                (("merged" if p.get("merged_at")
                  else "closed_without_merge")==factual["actual_disposition"]),
                "RETROSPECTIVE_GITHUB_DISPOSITION_CHANGED")
        for payload,key in (
            (p,"snapshot_pr_sha256"),
            (files,"snapshot_file_metadata_sha256"),
            (entry["original_issue_comments"],"snapshot_comments_sha256"),
            (entry["original_pr_reviews"],"snapshot_reviews_sha256")):
            require(digest(json.dumps(payload,sort_keys=True,
                ensure_ascii=False).encode())==factual[key],
                "RAW_EXTERNAL_SOURCE_SHA256_CHANGED")
        require(len(files)==factual["full_modified_files"],
                "CHANGED_FILES_MISMATCH")
        require(bycase[cid]["historical_normative_applicability_not_verified"]
                is True,"UNJUSTIFIED_POLICY_AUTHORITY_PROMOTION")
    seen=set()
    provider_ids=set()
    votes=defaultdict(list)
    failures=[]
    for r in rows:
        key=(r["case_id"],r["role"])
        require(key not in seen and r["case_id"] in bycase
                and r["role"] in ROLES,"EXTRA_OR_DUPLICATED_CASE_REVIEW")
        seen.add(key)
        require(r["model"]==ROLES[r["role"]] and
                r["prompt_sha256"]==digest(
                    prompt(r["role"],bycase[r["case_id"]]).encode()),
                "MODEL_ROLE_OR_BLIND_PROMPT_MISMATCH")
        rid=r.get("provider_id")
        if rid:
            require(rid not in provider_ids,"DUPLICATE_PROVIDER_RESPONSE_ID")
            provider_ids.add(rid)
        if r["assessment"] is None:
            failures.append({"case_id":r["case_id"],"role":r["role"],
                             "error":r.get("error"),"original_response_id":rid})
            continue
        v,unboxed=parse_vote(r["original_text"],bycase[r["case_id"]])
        require(v==r["assessment"] and
                r["json_fence_unboxed"]==unboxed,
                "SCIENTIFIC_REVIEW_RESPONSE_TAMPERED")
        votes[r["case_id"]].append(v["assessment"])
    require(len(seen)==24 and len(rows)==24 and
            summary["valid_reviews"]==sum(map(len,votes.values())) and
            summary["invalid_reviews"]==len(failures) and
            summary["provider_response_ids"]==len(provider_ids),
            "INCOMPLETE_OR_CHANGED_PANEL")
    percase=[]
    for cid in sorted(bycase):
        arr=votes[cid]
        percase.append({
            "case_id":cid,
            "source_pr_url":ref[cid]["source_pr_url"],
            "observed_disposition_not_gold":ref[cid]["actual_disposition"],
            "valid_ai_role_assessments":len(arr),
            "ai_unanimous_if_all_three":
                arr[0] if len(arr)==3 and len(set(arr))==1 else None,
            "ai_role_disagreement":len(set(arr))>1,
            "source_policy_qualified":False,
            "real_human_reference_action":False,
        })
    return {
        "classification":"DETACHED_REAL_CODE_CASES_AND_AI_ONLY_AUDIT",
        "original_source_manifest_sha256":sha_source,
        "original_panel_manifest_sha256":sha_reviews,
        "original_manifest_files_verified":n_source+n_reviews,
        "actual_public_changed_code_prs":8,
        "merged":sum(x["actual_disposition"]=="merged" for x in ref.values()),
        "closed_without_merge":sum(x["actual_disposition"]=="closed_without_merge"
                                    for x in ref.values()),
        "expected_ai_reviews":24,
        "strict_valid_ai_reviews":sum(map(len,votes.values())),
        "invalid_ai_reviews":failures,
        "unique_paid_provider_response_ids":len(provider_ids),
        "ai_unanimous_cases":sum(x["ai_unanimous_if_all_three"] is not None
                                  for x in percase),
        "cases":percase,
        "human_expert_adjudications":0,
        "human_policy_action_ground_truth":0,
        "original_full_knowledge_triage_replicated":False,
        "observed_git_merge_is_not_normative_policy_gold":True,
        "historical_policy_applicability_unverified":True,
        "retrospective_code_diff_temporally_frozen":False,
        "new_paid_calls":0,"confirmatory_touched":False,
        "scientifically_approved":False,
        "limitations":[
            "Actual code modifications and public GitHub dispositions are real, but correctness is not inferred from merge status.",
            "Original policy text and final code diff may have been updated after proposal or closure.",
            "Human decisions in public PRs are observed, not blind independent human adjudication under the WAMBU protocol.",
            "Three AI specialist roles are simulations, not independent real qualified people.",
            "No matched-information, matched-token compacted-memory comparisons occur in this bounded source-reality pilot.",
        ]
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True,type=Path)
    p.add_argument("--reviews",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    result=audit(a.source,a.reviews)
    a.out.mkdir(parents=True,exist_ok=True)
    save(a.out/"audit.json",result)
    save(a.out/"manifest.json",{
        "audit_sha256":digest((a.out/"audit.json").read_bytes()),
        "new_paid_calls":0,"human_policy_reference_labels":0,
        "scientifically_approved":False})
    print(json.dumps({k:result[k] for k in (
        "actual_public_changed_code_prs","merged","closed_without_merge",
        "expected_ai_reviews","strict_valid_ai_reviews",
        "unique_paid_provider_response_ids","human_expert_adjudications")}))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
