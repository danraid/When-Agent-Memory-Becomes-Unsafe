"""Collect real, externally decided GitHub governance events with provenance.

Public observed merge/non-merge outcome is FACT, NOT ground-truth for a policy
authorisation task. Original PR bodies can be edited; this is retrospective,
NOT a pre-decision point-in-time snapshot or independently adjudicated corpus.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import urllib.request
import urllib.error

from study.openrouter_comparison import digest, save


def get_json(url: str, transport=None):
    if transport:
        return transport(url)
    headers={"Accept":"application/vnd.github+json",
             "User-Agent":"WAMBU-P07C-public-research/1.0",
             "X-GitHub-Api-Version":"2022-11-28"}
    token=os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"]="Bearer "+token
    request=urllib.request.Request(url,headers=headers)
    with urllib.request.urlopen(request,timeout=35) as response:
        return json.load(response)


def allowed_record(r):
    return (isinstance(r,dict) and r.get("classification") ==
            "REAL_OBSERVED_PUBLIC_PR_DISPOSITIONS_AI_SIMULATED_DEVELOPMENT" and
            r.get("independent_human_adjudicators") == 0 and
            r.get("scientifically_approved") is False and
            r.get("confirmatory_holdout_touched") is False and
            len(r.get("cases",[])) == 8 and
            len({(c["repo"],c["number"]) for c in r["cases"]})==8)


def build(config_path: Path, transport=None):
    raw=config_path.read_bytes()
    cfg=json.loads(raw)
    if not allowed_record(cfg):
        raise ValueError("PREDECLARED_PUBLIC_GOVERNANCE_MATRIX_INVALID")
    cutoff=datetime.fromisoformat(cfg["data_cutoff_utc"].replace("Z","+00:00"))
    model_cases,hidden,receipts=[],[],[]
    for spec in cfg["cases"]:
        repo,num=spec["repo"],spec["number"]
        if repo not in ("python/peps","rust-lang/rfcs") or type(num) is not int:
            raise ValueError("UNDECLARED_REPO_OR_PR")
        prefix=f"https://api.github.com/repos/{repo}"
        pr=get_json(f"{prefix}/pulls/{num}",transport)
        comments=get_json(f"{prefix}/issues/{num}/comments?per_page=100",transport)
        if not isinstance(pr,dict) or not isinstance(comments,list):
            raise ValueError("INVALID_SOURCE_API_SHAPE")
        if pr.get("number")!=num or pr.get("state")!="closed":
            raise ValueError("NOT_OBSERVED_CLOSED_PR")
        finished=pr.get("closed_at")
        created=pr.get("created_at")
        if not finished or not created:
            raise ValueError("MISSING_HISTORICAL_EVENT_TIMES")
        event_time=datetime.fromisoformat(finished.replace("Z","+00:00"))
        first=datetime.fromisoformat(created.replace("Z","+00:00"))
        if not first<event_time<=cutoff:
            raise ValueError("IMPOSSIBLE_OR_POSTCUTOFF_EVENT")
        merged=bool(pr.get("merged_at"))
        if merged and pr["merged_at"]!=finished:
            raise ValueError("MERGE_TIME_DIFFERS_FROM_CLOSE_TIME_REVIEW")
        title=pr.get("title")
        body=pr.get("body") or ""
        if not isinstance(title,str) or len(title)<5 or not isinstance(body,str):
            raise ValueError("INVALID_PR_HISTORY")
        # Issue comments are individual timestamped public events. The original
        # PR title/body are current snapshots, not historical snapshots.
        prior=[]
        for c in comments:
            stamp=c.get("created_at")
            if not stamp or not c.get("body"):
                continue
            t=datetime.fromisoformat(stamp.replace("Z","+00:00"))
            if first<=t<event_time:
                prior.append({"created_at":stamp,"excerpt":c["body"][:500],
                              "comment_url":c.get("html_url")})
        prior.sort(key=lambda c:(c["created_at"],str(c["comment_url"])))
        model_case={
            "case_id":spec["case_id"],"domain":"public_software_governance",
            "question":("Assess whether this proposal was likely to be merged or "
                        "closed without merge based only on the provided proposal "
                        "and pre-decision discussion. Abstain when evidence is "
                        "insufficient. This is historical outcome estimation, "
                        "not an approval instruction."),
            "title":title,
            "proposal_excerpt":body[:1800],
            "created_at_utc":created,
            "predecision_discussion":[{"created_at":c["created_at"],
                                        "excerpt":c["excerpt"]} for c in prior[:4]],
            "provenance_class":"PUBLIC_GITHUB_PR_RETROSPECTIVE_SNAPSHOT",
            "source_body_historically_frozen":False,
            "outcome_disclosed":False,
        }
        if any(k in model_case for k in ("merged","state","closed_at","observed_disposition","reference_action")):
            raise ValueError("MODEL_VISIBLE_OUTCOME_LEAK")
        model_cases.append(model_case)
        hidden.append({
            "case_id":spec["case_id"],"repo":repo,"number":num,
            "original_pr_url":pr.get("html_url"),"created_at":created,
            "observed_closed_at":finished,
            "observed_merged_at":pr.get("merged_at"),
            "observed_disposition":"merged" if merged else "closed_without_merge",
            "observed_disposition_not_scientific_gold":True,
            "comments_count_before_close":len(prior),
            "original_pr_snapshot_sha256":digest(json.dumps(pr,sort_keys=True,ensure_ascii=False).encode()),
            "original_issue_comments_sha256":digest(json.dumps(comments,sort_keys=True,ensure_ascii=False).encode()),
            "original_head_sha":pr.get("head",{}).get("sha"),
            "original_base_sha_at_collection":pr.get("base",{}).get("sha"),
            "title_body_may_have_been_edited_after_close":True,
            "qualified_independent_human_label":False,
        })
        receipts.append({"case_id":spec["case_id"],"pr":pr,"issue_comments":comments})
    if len(model_cases)!=8 or sum(x["observed_disposition"]=="merged" for x in hidden)<2 or sum(x["observed_disposition"]=="closed_without_merge" for x in hidden)<2:
        raise ValueError("INSUFFICIENT_BOTH_HISTORICAL_OUTCOME_CLASSES")
    public={
        "schema":"WAMBU-P07C-REAL-GOVERNANCE-INPUTS-V1",
        "classification":"RETROSPECTIVE_REAL_EVENTS_NO_HUMAN_REFERENCE",
        "split":"development_only","cases":model_cases,
        "declared_protocol_sha256":digest(raw),
        "case_count":len(model_cases),"observed_historical_events":8,
        "independently_adjudicated_policy_actions":0,
        "historical_predecision_snapshot_guaranteed":False,
        "holdout_touched":False,
    }
    sidecar={"schema":"WAMBU-P07C-OBSERVED-GITHUB-OUTCOMES-EVALUATOR-ONLY",
             "label_kind":"PUBLIC_ACTUAL_PR_DISPOSITION_NOT_POLICY_GOLD",
             "observed_outcomes":hidden,"human_adjudications":0,
             "no_independent_expert_reference":True}
    provenance={"schema":"WAMBU-P07C-HISTORICAL-RAW-SOURCE-SNAPSHOTS-V1",
                "original_api_payloads":receipts,"config_sha256":digest(raw),
                "collected_at_utc":datetime.now(timezone.utc).isoformat(),
                "snapshot_is_retrospective":True,"public_metadata_may_contain_personal_identifiers":True}
    return public,sidecar,provenance


def materialise(config_path: Path,out:Path,transport=None):
    if out.exists() and any(out.iterdir()):
        raise ValueError("NEVER_OVERWRITE_ORIGINAL_SOURCE_EVIDENCE")
    public,sidecar,source=build(config_path,transport)
    out.mkdir(parents=True,exist_ok=True)
    for filename,payload in (
        ("model_inputs_no_outcome.json",public),
        ("observed_outcomes_evaluator_only.json",sidecar),
        ("raw_external_github_sources.json",source)):
        save(out/filename,payload)
    save(out/"manifest.json",{
        "sha256":{p.name:digest(p.read_bytes()) for p in out.glob("*.json")
                  if p.name!="manifest.json"},
        "historical_outcome_reference_not_human_policy_gold":True,
        "no_confirmatory_access":True,
        "no_scientific_approval":True,
    })
    return {"historical_events":8,
            "merged":sum(x["observed_disposition"]=="merged" for x in sidecar["observed_outcomes"]),
            "closed_without_merge":sum(x["observed_disposition"]=="closed_without_merge" for x in sidecar["observed_outcomes"]),
            "qualified_human_adjudications":0}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--config",type=Path,default=Path("protocol/P07C_REAL_GOVERNANCE_SOURCE_MATRIX.json"))
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    print(json.dumps(materialise(a.config,a.out),indent=2))


if __name__=="__main__":
    main()
