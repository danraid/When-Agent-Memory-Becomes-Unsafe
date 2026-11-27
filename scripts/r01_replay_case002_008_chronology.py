"""Public event chronology for P07D code 002/008, without retrospective gold.

Fetches original PR and associated issue metadata; body text is mutable, hence
not certified as event-time wording. No models, secrets, private data or holdout.
"""
from __future__ import annotations
import argparse
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
from urllib.request import Request,urlopen

CASES={"P07D-CODE-002":(140345,140344),"P07D-CODE-008":(133654,133644)}
def stamp(s): return datetime.fromisoformat(s.replace("Z","+00:00"))
def get(url,fetch=None):
    if fetch: return fetch(url)
    request=Request(url,headers={"Accept":"application/vnd.github+json",
        "User-Agent":"WAMBU-R01-GitHub-event-trace",
        "X-GitHub-Api-Version":"2022-11-28"})
    with urlopen(request,timeout=40) as f: return f.read()

def audit(fetch=None):
    rows=[]
    for cid,(prnum,issue_num) in CASES.items():
        pu=f"https://api.github.com/repos/python/cpython/pulls/{prnum}"
        iu=f"https://api.github.com/repos/python/cpython/issues/{issue_num}"
        pb=get(pu,fetch);ib=get(iu,fetch)
        p=json.loads(pb);i=json.loads(ib)
        if p.get("number")!=prnum or i.get("number")!=issue_num:
            raise ValueError("CASE_PR_ISSUE_IDENTITY_MISMATCH")
        if p.get("base",{}).get("repo",{}).get("full_name")!="python/cpython":
            raise ValueError("NON_ORIGINAL_PR")
        if stamp(i["created_at"])>stamp(p["created_at"]):
            raise ValueError("ISSUE_WAS_CREATED_AFTER_PR")
        if p.get("merged_at") and p.get("closed_at")!=p.get("merged_at"):
            raise ValueError("INCONSISTENT_MERGE_TIMESTAMPS")
        rows.append({"case_id":cid,"pr":prnum,"issue":issue_num,
            "pr_url":p.get("html_url"),"issue_url":i.get("html_url"),
            "pr_created":p["created_at"],"issue_created":i["created_at"],
            "pr_closed":p.get("closed_at"),"pr_merged":p.get("merged_at"),
            "source_response_sha256":{"pr":sha256(pb).hexdigest(),"issue":sha256(ib).hexdigest()},
            "source_body_temporally_authenticated":False,
            "event_time_policy_authority_qualified":False,
            "observation":"CURRENT_PUBLIC_RECORD_WITH_HISTORICAL_EVENT_TIMESTAMPS",
            "operational_gold_action":None})
    return {"schema":"WAMBU-R01-ISSUE-PR-CHRONOLOGY-V1",
       "cases":rows,"real_event_pairs":len(rows),
       "historical_body_immutability_proven":False,
       "qualifying_new_gold_actions":0,
       "confirmatory_touched":False,"external_submission_authorised":False}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",required=True,type=Path)
    args=ap.parse_args(); r=audit()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"real_event_pairs":r["real_event_pairs"],
                      "gold":r["qualifying_new_gold_actions"]},indent=2))
if __name__=="__main__": main()
