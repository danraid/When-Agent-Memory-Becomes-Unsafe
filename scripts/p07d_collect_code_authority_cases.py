"""Collect authentic code-change diffs and pre-closure review events.

These are retrospective public repository decisions, never human-adjudicated
policy action gold. Historical body, final diff and policy snapshot may postdate
a PR decision. Such temporal provenance uncertainty is explicit in every case.
"""
from __future__ import annotations
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import argparse
import json
import os
import urllib.request

from study.openrouter_comparison import digest, save


def request_bytes(url: str, token: str = "", fetcher=None) -> bytes:
    if fetcher is not None:
        return fetcher(url)
    headers = {"User-Agent":"WAMBU-P07D/1.0",
               "Accept":"application/vnd.github+json",
               "X-GitHub-Api-Version":"2022-11-28"}
    if token and "api.github.com" in url:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read()


def since_before(start: str, stamp: str, end: str) -> bool:
    def parse(s):
        return datetime.fromisoformat(s.replace("Z","+00:00"))
    return parse(start) <= parse(stamp) < parse(end)


def anchor_excerpt(source: str, needle: str):
    lines = source.splitlines()
    matches = [(i,x) for i,x in enumerate(lines) if needle in x]
    if len(matches) != 1:
        raise ValueError("AMBIGUOUS_OR_MISSING_NORMATIVE_EXCERPT:"+needle)
    i,line = matches[0]
    return {"line_1based":i+1,"exact_text":line.strip(),
            "sha256":digest(line.strip().encode())}


def collect(config_path:Path, api=None, raw=None):
    cfg_bytes=config_path.read_bytes()
    cfg=json.loads(cfg_bytes)
    if (cfg.get("schema") != "WAMBU-P07D-REAL-CODE-CHANGE-CASES-V1"
        or len(cfg["cases"]) != 8 or cfg["expected_paid_reviews"] != 24
        or cfg["no_human_gold"] is not True or cfg["allow_confirmatory"] is not False):
        raise ValueError("INVALID_FROZEN_DEVELOPMENT_MATRIX")
    token=os.getenv("GITHUB_TOKEN","")
    def getj(url):
        return json.loads(request_bytes(url,token,api))
    def getb(url):
        return request_bytes(url,token,raw)
    normative={}
    original_source_receipts={}
    for s in cfg["normative_sources"]:
        url=(f"https://raw.githubusercontent.com/{s['repository']}/"
             f"{s['commit']}/{s['path']}")
        b=getb(url)
        text=b.decode("utf-8")
        spans=[anchor_excerpt(text,n) for n in s["anchors"]]
        normative[s["key"]]={
            "url":s["source_url"],"commit":s["commit"],
            "source_sha256":digest(b),"quoted_rules":spans,
            "historical_version_applicability_unverified":True,
        }
        original_source_receipts[s["key"]]={"url":url,"original_text":text,
                                            "sha256":digest(b)}
    cases,reference,receipts=[],[],[]
    seen=set()
    for slot in cfg["cases"]:
        key=(slot["repository"],slot["pr"])
        if key in seen or slot["repository"] not in ("python/cpython","rust-lang/rust"):
            raise ValueError("UNDECLARED_OR_DUPLICATE_SOURCE")
        seen.add(key)
        root=f"https://api.github.com/repos/{slot['repository']}"
        p=getj(f"{root}/pulls/{slot['pr']}")
        files=getj(f"{root}/pulls/{slot['pr']}/files?per_page=100")
        comments=getj(f"{root}/issues/{slot['pr']}/comments?per_page=100")
        reviews=getj(f"{root}/pulls/{slot['pr']}/reviews?per_page=100")
        if (p["number"] != slot["pr"] or p["state"]!="closed"
            or not isinstance(files,list) or not files or
            not isinstance(comments,list) or not isinstance(reviews,list)
            or len(files) != p["changed_files"] or
            len(files)>cfg["max_changed_files_per_pr"]):
            raise ValueError("SOURCE_CLOSED_PR_OR_FILES_INCOMPLETE")
        created,closed=p["created_at"],p["closed_at"]
        if not since_before(created,created,closed) or not since_before(
                created,closed,cfg["snapshot_limit_utc"]):
            raise ValueError("TIME_OR_CUTOFF_INVALID")
        observed="merged" if p.get("merged_at") else "closed_without_merge"
        candidate_files=[]
        for f in files:
            patch=f.get("patch")
            if (isinstance(patch,str) and patch.strip() and
                f.get("changes",0)<=cfg["max_changes_per_pr"]):
                candidate_files.append({
                    "path":f["filename"],"status":f["status"],
                    "changed_lines":f["changes"],
                    "patch":patch[:cfg["max_patch_characters"]],
                    "patch_sha256":digest(patch.encode()),
                    "patch_excerpt_truncated":len(patch)>cfg["max_patch_characters"],
                })
        if not candidate_files:
            raise ValueError("NO_REVIEWABLE_REAL_CODE_DIFF")
        def before_event(e, field):
            stamp=e.get(field)
            return bool(stamp and since_before(created,stamp,closed))
        comments_before=[
            {"at":c["created_at"],"excerpt":c["body"][:cfg["max_comment_characters"]],
             "source_url":c.get("html_url")}
            for c in comments if before_event(c,"created_at") and c.get("body")
        ]
        reviews_before=[
            {"at":v["submitted_at"],"excerpt":(v.get("body") or "")[:cfg["max_comment_characters"]],
             "review_state":v.get("state","UNKNOWN"),
             "source_url":v.get("html_url")}
            for v in reviews if before_event(v,"submitted_at") and v.get("body")
        ]
        comments_before.sort(key=lambda r:(r["at"],r["excerpt"]))
        reviews_before.sort(key=lambda r:(r["at"],r["excerpt"]))
        rule=normative[slot["normative"]]
        model_case={
            "case_id":slot["id"],
            "task":"Inspect actual public code changes and compare their stated rationale with quoted governing guidance. Identify possible compatibility/authority conflicts; abstain on missing effective-time or scope evidence. Do not guess whether the PR was merged.",
            "repository_domain":slot["repository"],
            "title":p["title"],"description_retrospective":(p.get("body") or "")[:1200],
            "created_at":created,
            "code_patches_retrospective":candidate_files[:cfg["max_sampled_patches_per_pr"]],
            "preclosure_comments":[{"at":c["at"],"excerpt":c["excerpt"]}
                                   for c in comments_before[:cfg["max_preclosure_comments"]]],
            "preclosure_reviews":[{"at":c["at"],"excerpt":c["excerpt"],"review_state":c["review_state"]}
                                  for c in reviews_before[:cfg["max_preclosure_comments"]]],
            "source_guidance":rule,
            "historical_normative_applicability_not_verified":True,
            "retrospective_diff_not_guaranteed_at_pr_creation":True,
            "policy_approval_reference_available":False,
            "observed_pr_disposition_visible":False,
        }
        if any(x in model_case for x in ("merged_at","closed_at","observed_disposition","gold_action","reference_action")):
            raise ValueError("LABEL_LEAK")
        cases.append(model_case)
        reference.append({
            "case_id":slot["id"],"repository":slot["repository"],"pr":slot["pr"],
            "source_pr_url":p["html_url"],"created_at":created,
            "observed_closed_at":closed,"observed_merged_at":p["merged_at"],
            "actual_disposition":observed,
            "head_commit_sha":p["head"]["sha"],
            "snapshot_pr_sha256":digest(json.dumps(p,sort_keys=True,ensure_ascii=False).encode()),
            "snapshot_file_metadata_sha256":digest(json.dumps(files,sort_keys=True,ensure_ascii=False).encode()),
            "snapshot_comments_sha256":digest(json.dumps(comments,sort_keys=True,ensure_ascii=False).encode()),
            "snapshot_reviews_sha256":digest(json.dumps(reviews,sort_keys=True,ensure_ascii=False).encode()),
            "full_modified_files":len(files),
            "patches_sampled":len(model_case["code_patches_retrospective"]),
            "preclosure_comments_total":len(comments_before),
            "preclosure_review_comments_total":len(reviews_before),
            "external_human_adjudicated_policy_correctness":False
        })
        receipts.append({"case_id":slot["id"],"original_pr":p,
                         "original_changed_files":files,
                         "original_issue_comments":comments,
                         "original_pr_reviews":reviews})
    merged=sum(x["actual_disposition"]=="merged" for x in reference)
    if (len(cases)!=8 or merged!=cfg["expected_observed_merged"] or
        (8-merged)!=cfg["expected_observed_closed_without_merge"]):
        raise ValueError("PREDECLARED_OUTCOME_BALANCE_CHANGED")
    return (
        {"schema":"WAMBU-P07D-REAL-CODE-BLIND-INPUTS-V1",
         "classification":"REAL_PUBLIC_CODE_CHANGES_RETROSPECTIVE_NO_POLICY_GOLD",
         "cases":cases,"source_config_sha256":digest(cfg_bytes),
         "observed_code_change_prs":len(cases),
         "independent_human_policy_adjudications":0,
         "confirmatory_touched":False},
        {"schema":"WAMBU-P07D-ACTUAL-PR-DISPOSITIONS-EVALUATOR-ONLY",
         "reference_kind":"FACTUAL_WORKFLOW_DISPOSITION_NOT_POLICY_GOLD",
         "events":reference,"human_policy_reference_labels":0},
        {"schema":"WAMBU-P07D-RAW-PUBLIC-CODE-RECEIPTS",
         "source_config_sha256":digest(cfg_bytes),
         "source_normative_snapshots":original_source_receipts,
         "source_pr_metadata":receipts,
         "retrieved_utc":datetime.now(timezone.utc).isoformat(),
         "may_contain_public_personal_identifiers":True,
         "exact_predecision_PR_body_or_diff_guaranteed":False}
    )


def run(config:Path,out:Path,api=None,raw=None):
    if out.exists() and any(out.iterdir()):
        raise ValueError("SOURCE_EVIDENCE_ALREADY_EXISTS_CANNOT_OVERWRITE")
    blind,observed,source=collect(config,api,raw)
    out.mkdir(parents=True,exist_ok=True)
    for name,data in (
        ("blind_code_cases.json",blind),
        ("observed_dispositions_evaluator_only.json",observed),
        ("raw_original_sources.json",source)):
        save(out/name,data)
    save(out/"manifest.json",{
        "files_sha256":{p.name:digest(p.read_bytes()) for p in out.glob("*.json")
                        if p.name!="manifest.json"},
        "no_human_reference":True,"no_confirmatory_access":True})
    return {"case_count":len(blind["cases"]),"observed_merged":sum(
            x["actual_disposition"]=="merged" for x in observed["events"]),
            "observed_closed_without_merge":sum(
            x["actual_disposition"]=="closed_without_merge" for x in observed["events"]),
            "independent_human_policy_labels":0}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--config",type=Path,
                   default=Path("protocol/P07D_REAL_CODE_CHANGE_MATRIX.json"))
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    print(json.dumps(run(args.config,args.out),sort_keys=True))


if __name__=="__main__":
    main()
