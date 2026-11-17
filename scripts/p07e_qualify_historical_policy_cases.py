"""P07e: source-pinned historical normative availability and scope screening.

Inputs: ORIGINAL P07d GitHub Actions source artifact (do not reconstruct or
rewrite), and frozen *analyst-proposed* topic tags. Each PR receives two
historical source snapshots by commit at creation/closure. The output never
assigns operational approve/reject policy gold or human credentials.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import quote

from study.openrouter_comparison import digest, save

ORIGINAL_RUN_ID=43977945404
ORIGINAL_SOURCE_ARTIFACT_ID=14281751027


def strict(flag:bool,code:str):
    if not flag:
        raise ValueError(code)


def get_bytes(url:str, token:str="", fetch=None):
    if fetch:
        return fetch(url)
    hdr={"User-Agent":"WAMBU-P07E-historical-policy-audit",
         "Accept":"application/vnd.github+json",
         "X-GitHub-Api-Version":"2022-11-28"}
    if token and url.startswith("https://api.github.com/"):
        hdr["Authorization"]="Bearer "+token
    with urlopen(Request(url,headers=hdr),timeout=40) as r:
        return r.read()


def history(repo:str,path:str,at:str,token:str="",fetch=None):
    start=f"https://api.github.com/repos/{repo}/commits"
    q=f"?path={quote(path,safe='')}&until={quote(at,safe='')}&per_page=1"
    raw=get_bytes(start+q,token,fetch)
    commits=json.loads(raw)
    strict(isinstance(commits,list) and len(commits)<=1,
           "INVALID_HISTORICAL_COMMIT_RESPONSE")
    if not commits:
        return ({"available":False,"prior_commit":None,
                 "source_sha256":None,"source_text":None,
                 "evidence":"NO_DOCUMENT_COMMIT_FOUND_BY_DATE"},
                {"commits_api_sha256":digest(raw),"raw_git_text_sha256":None})
    commit=commits[0]
    sha=commit["sha"]
    committed=commit["commit"]["committer"]["date"]
    strict(datetime.fromisoformat(committed.replace("Z","+00:00")) <=
           datetime.fromisoformat(at.replace("Z","+00:00")),
           "FUTURE_SOURCE_REVISION_LEAK")
    raw_url=f"https://raw.githubusercontent.com/{repo}/{sha}/{path}"
    blob=get_bytes(raw_url,token,fetch)
    text=blob.decode("utf-8")
    strict(len(blob)>100,"HISTORICAL_NORMATIVE_SOURCE_TRUNCATED")
    return {
        "available":True,"prior_commit":sha,
        "source_sha256":digest(blob),
        "committer_date":committed,
        "source_url":f"https://github.com/{repo}/blob/{sha}/{path}",
        "source_text":text,
        "evidence":"GIT_COMMIT_AND_SOURCE_BYTES_PRIOR_TO_EVENT"},
        {"commits_api_sha256":digest(raw),
         "raw_git_text_sha256":digest(blob)}


def extract_line(text:str|None, anchor:str):
    if text is None:
        return {"anchor_present":False,"line_number":None,"literal_quote":None}
    matching=[(i+1,line.strip()) for i,line in enumerate(text.splitlines())
              if anchor in line]
    strict(len(matching)<=1,"HISTORICAL_ANCHOR_AMBIGUOUS")
    if not matching:
        return {"anchor_present":False,"line_number":None,"literal_quote":None}
    return {"anchor_present":True,
            "line_number":matching[0][0],
            "literal_quote":matching[0][1]}


def inspect(source_dir:Path, matrix_path:Path, config_path:Path,
            fetch=None) -> dict:
    source_dir=source_dir.resolve()
    raw=(source_dir/"manifest.json").read_bytes()
    manifest=json.loads(raw)
    checks=manifest["files_sha256"]
    strict(set(checks)=={
        "blind_code_cases.json","observed_dispositions_evaluator_only.json",
        "raw_original_sources.json"},"ORIGINAL_ARTIFACT_SET_CHANGED")
    for fname,sha in checks.items():
        p=source_dir/fname
        strict(p.is_file() and digest(p.read_bytes())==sha,
               "ORIGINAL_P07D_SOURCE_HASH_FAILED:"+fname)
    original=json.loads((source_dir/"raw_original_sources.json").read_text())
    observed=json.loads((source_dir/"observed_dispositions_evaluator_only.json").read_text())
    blind=json.loads((source_dir/"blind_code_cases.json").read_text())
    original_by_id={x["case_id"]:x for x in original["source_pr_metadata"]}
    observed_by_id={x["case_id"]:x for x in observed["events"]}
    blind_by_id={x["case_id"]:x for x in blind["cases"]}
    analyst=json.loads(matrix_path.read_text())
    cfg=json.loads(config_path.read_text())
    strict(analyst["schema"]=="WAMBU-P07E-CASE-SCOPE-TRIAGE-V1" and
           analyst["original_run"]==ORIGINAL_RUN_ID and
           analyst["source_artifact_id"]==ORIGINAL_SOURCE_ARTIFACT_ID,
           "HISTORICAL_TRIAGE_PROVENANCE_MISMATCH")
    strict(cfg["schema"]=="WAMBU-P07D-REAL-CODE-CHANGE-CASES-V1",
           "ORIGINAL_CASE_MATRIX_MISMATCH")
    tags={x["id"]:x for x in analyst["cases"]}
    cases_cfg={x["id"]:x for x in cfg["cases"]}
    strict(len(tags)==len(cases_cfg)==len(blind_by_id)==8 and
           set(tags)==set(cases_cfg)==set(blind_by_id)==
           set(original_by_id)==set(observed_by_id),
           "EIGHT_CASE_IDENTITY_MATRIX_INVALID")
    source_cfg={x["key"]:x for x in cfg["normative_sources"]}
    token=os.getenv("GITHUB_TOKEN","")
    snapshots={}
    qualified=[]
    for cid in sorted(tags):
        c=cases_cfg[cid]
        src=source_cfg[c["normative"]]
        datum=observed_by_id[cid]
        original_pr=original_by_id[cid]["original_pr"]
        strict(original_pr["number"]==c["pr"] and
               datum["pr"]==c["pr"] and
               c["repository"]==datum["repository"],"PR_ID_MISMATCH")
        temporal={}
        for kind,event_at in (
            ("at_creation",datum["created_at"]),
            ("at_closure",datum["observed_closed_at"])):
            key=(c["normative"],event_at)
            if key not in snapshots:
                snapshots[key]=history(src["repository"],src["path"],event_at,
                                       token,fetch)
            history_data,receipt=snapshots[key]
            excerpts=[extract_line(history_data["source_text"],anchor)
                      for anchor in src["anchors"]]
            temporal[kind]={
                "event_utc":event_at,
                "historical_source_present":history_data["available"],
                "prior_source_commit_sha":history_data["prior_commit"],
                "source_sha256":history_data["source_sha256"],
                "commit_datetime":history_data.get("committer_date"),
                "source_url":history_data.get("source_url"),
                "historical_clauses":excerpts,
                "exact_original_anchor_all_found":all(x["anchor_present"]
                                                       for x in excerpts),
                "source_bytes_provenance_sha256":receipt["raw_git_text_sha256"],
                "source_commit_api_response_sha256":receipt["commits_api_sha256"],
                "issuer_policy_effective_at_verified":False,
                "normative_scope_qualified":False,
            }
        tag=tags[cid]
        direct=tag["scope_tag"]=="DIRECT_POLICY_TOPIC"
        both_docs=all(temporal[x]["historical_source_present"] for x in temporal)
        clauses=all(temporal[x]["exact_original_anchor_all_found"]
                    for x in temporal)
        # The only possible positive statement is documentary feasibility.
        document_candidate=bool(direct and both_docs and clauses)
        qualified.append({
            "case_id":cid,"observed_pr_url":datum["source_pr_url"],
            "observed_github_disposition_not_correctness_gold":datum["actual_disposition"],
            "source_topic_tag":tag["scope_tag"],
            "proposed_topic":tag["topic"],"proposed_topic_rationale":tag["reason"],
            "analyst_tag_not_independent_review":True,
            "creation":temporal["at_creation"],
            "closure":temporal["at_closure"],
            "source_changed_between_creation_closure":
                temporal["at_creation"]["source_sha256"] !=
                temporal["at_closure"]["source_sha256"],
            "documentary_qualification":"DOCUMENTARY_FEASIBILITY_ONLY"
                if document_candidate else
                "NOT_ELIGIBLE_FOR_CURRENT_DOCUMENT_POLICY_PAIRING",
            "candidate_for_future_human_source_review":document_candidate,
            "historical_normative_adoption_proven":False,
            "human_blind_policy_adjudication":False,
            "correct_authorisation_action":None,
            "confirmatory_eligible":False,
        })
    return {
        "schema":"WAMBU-P07E-SOURCE_HISTORY-QUALIFICATION-V1",
        "classification":"REAL_GIT_SOURCE_HISTORY_AND_ANALYST_SCOPE_TRIAGE_NOT_HUMAN_GOLD",
        "original_source_artifact_id":ORIGINAL_SOURCE_ARTIFACT_ID,
        "original_run_id":ORIGINAL_RUN_ID,
        "original_source_manifest_sha256":digest(raw),
        "analyst_scope_tags_sha256":digest(matrix_path.read_bytes()),
        "original_case_config_sha256":digest(config_path.read_bytes()),
        "checked_cases":8,
        "documentary_feasible_cases":sum(
            x["candidate_for_future_human_source_review"] for x in qualified),
        "current_policy_pairing_not_eligible":sum(
            not x["candidate_for_future_human_source_review"] for x in qualified),
        "document_history_reconstructed":True,
        "human_policy_gold_labels":0,
        "independent_human_experts":0,
        "qualified_operational_agent_authorisations":0,
        "private_holdout_touched":False,
        "scientifically_approved":False,
        "case_reports":qualified,
        "limitations":[
            "A commit predating a PR does not by itself demonstrate normative adoption, effective scope or approval correctness.",
            "GitHub merge or closure is an observed historical workflow outcome, not independent policy-action gold.",
            "Analyst-proposed topic tags are not human independent adjudication.",
            "Contemporary retrospective PR body/diff may have been revised since the actual decision.",
            "This stage contains no memory-compaction agent experiment or full original Knowledge Triage replication."
        ]
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",required=True,type=Path)
    p.add_argument("--matrix",type=Path,
                   default=Path("protocol/P07E_HISTORICAL_SCOPE_TRIAGE.json"))
    p.add_argument("--original-config",type=Path,
                   default=Path("protocol/P07D_REAL_CODE_CHANGE_MATRIX.json"))
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    out=a.out
    strict(not out.exists() or not any(out.iterdir()),
           "NO_OVERWRITING_EXISTING_QUALIFICATION_EVIDENCE")
    report=inspect(a.source,a.matrix,a.original_config)
    out.mkdir(parents=True,exist_ok=True)
    save(out/"historical_qualification.json",report)
    save(out/"manifest.json",{
        "report_sha256":digest((out/"historical_qualification.json").read_bytes()),
        "original_source_manifest_sha256":report["original_source_manifest_sha256"],
        "human_policy_gold_labels":0,"private_holdout_touched":False,
        "scientific_approval":False})
    print(json.dumps({k:report[k] for k in (
        "checked_cases","documentary_feasible_cases",
        "current_policy_pairing_not_eligible","human_policy_gold_labels")}))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
