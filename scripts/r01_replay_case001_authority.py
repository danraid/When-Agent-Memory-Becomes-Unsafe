"""R01 case 001: independently replay public GitHub event-time authority evidence.

Uses public GitHub REST JSON; cannot infer independent experimental action
ground truth from a historical authority statement. Does not need secrets.
"""
from __future__ import annotations
import argparse
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
from urllib.request import Request,urlopen

PR="https://api.github.com/repos/python/cpython/pulls/133080"
SC="https://api.github.com/repos/python/steering-council/issues/comments/2828390956"
WG="https://api.github.com/repos/capi-workgroup/decisions/issues/comments/2834971171"
SC_ISSUE="https://api.github.com/repos/python/steering-council/issues/288"
SOURCES=(PR,SC,WG,SC_ISSUE)
APPROVAL="Thanks for bringing this to our attention! The SC is fine with this removal sans-deprecation."
ACK="Approved by SC, tracked in https://github.com/python/cpython/issues/133079"

def dt(s):
    return datetime.fromisoformat(s.replace("Z","+00:00"))

def load_url(url,fetch=None):
    if fetch is not None:
        return fetch(url)
    request=Request(url,headers={"Accept":"application/vnd.github+json",
       "User-Agent":"WAMBU-R01-evidence-replay",
       "X-GitHub-Api-Version":"2022-11-28"})
    with urlopen(request,timeout=40) as response:
        return response.read()

def audit(fetch=None):
    raw={url:load_url(url,fetch) for url in SOURCES}
    docs={url:json.loads(b) for url,b in raw.items()}
    pr,sc,wg,issue=(docs[url] for url in SOURCES)
    required={
      "correct_pr":pr.get("number")==133080 and pr.get("base",{}).get("repo",{}).get("full_name")=="python/cpython",
      "sc_issue":issue.get("number")==288,
      "sc_comment_identity":sc.get("id")==2828390956 and sc.get("user",{}).get("login")=="emilyemorehouse",
      "sc_literal_approval":sc.get("body","").strip()==APPROVAL,
      "sc_publication_pre_pr":dt(sc["created_at"])<dt(pr["created_at"]),
      "sc_comment_not_retrospectively_edited":sc.get("updated_at")==sc.get("created_at"),
      "ack_literal":wg.get("body","").strip()==ACK,
      "ack_post_pr_creation":dt(wg["created_at"])>dt(pr["created_at"]),
      "pr_after_formal_exception_request":dt(issue["created_at"])<dt(pr["created_at"]),
      "pr_link_to_exception":"/python/steering-council/issues/288" in pr.get("body",""),
    }
    return {
       "schema":"WAMBU-R01-CASE001-GITHUB-REPLAY-V1",
       "passed":all(required.values()),
       "checks":required,
       "case_id":"P07D-CODE-001",
       "source_sha256":{url:sha256(raw[url]).hexdigest() for url in SOURCES},
       "pr_creation_time":pr["created_at"],
       "exception_statement_time":sc["created_at"],
       "later_wg_ack_time":wg["created_at"],
       "approval_scope":"PUBLIC_STEERING_COUNCIL_STATEMENT_PRECEDES_PR",
       "does_not_establish_agent_action_gold":True,
       "independent_human_experiment_reviews":0,
       "holdout_access":False,
       "external_submission":False,
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",required=True,type=Path)
    args=parser.parse_args()
    r=audit()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(r,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"passed":r["passed"],"checks":r["checks"]},indent=2))
    return 0 if r["passed"] else 1

if __name__=="__main__":
    raise SystemExit(main())
