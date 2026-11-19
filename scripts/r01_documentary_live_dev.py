"""R01 original-source documentary authorisation challenge: bounded paid DEVELOPMENT.

12 timestamp/scope questions; judge documentary evidence only. This is never
a source-independent action gold benchmark or confirmatory memory experiment.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
import os
from pathlib import Path
from article_hub.evidence import write_json
from article_hub.llm import request_advisory
from r01_documentary.challenge import validated,prompt_for,grade,FIXTURE,PRIMARY

ROOT=Path(__file__).resolve().parents[1]
MODEL=ROOT/"study/model_config.json"


def execute(out:Path,ledger:Path):
    if os.getenv("R01_ALLOW_DOCUMENTARY_DEV_CALLS")!="true" or not os.getenv("OPENAI_API_KEY"):
        raise ValueError("DOCUMENTARY_LIVE_SCOPE_NOT_ENABLED")
    if out.exists():
        raise ValueError("NO_OVERWRITE_EXISTING_EVIDENCE")
    doc,primary=validated()
    config=json.loads(MODEL.read_text())
    if config.get("max_output_tokens",0)<256:
        raise ValueError("NEEDS_JSON_REASON_OUTPUT_BUDGET")
    result={
      "schema":"WAMBU-R01-DOCUMENTARY-TIME-SCOPE-LIVE-V1",
      "state":"RUNNING",
      "split":"public_development_only",
      "fixture_sha256":sha256(FIXTURE.read_bytes()).hexdigest(),
      "authority_sha256":sha256(PRIMARY.read_bytes()).hexdigest(),
      "model_config_sha256":sha256(MODEL.read_bytes()).hexdigest(),
      "planned_calls":12,
      "observations":[],
      "source_status":"VERIFIED_PRIMARY_DOCUMENTARY_CASEBOOK",
      "scope_qualified_real_case_count":1,
      "fully_independent_real_operational_action_gold":0,
      "model_generated_review_is_not_independent_human_adjudication":True,
      "no_holdout_access":True,
      "scientific_superiority_claim":False,
      "external_submission_authorised":False
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    write_json(out,result)
    seen=set()
    for task in doc["tasks"]:
        prompt,sources=prompt_for(task,doc,primary)
        # The reference is never concatenated to prompts or provider messages.
        response=request_advisory(prompt,config,ledger)
        rid=response.get("provider_response_id")
        usage=response.get("observed_usage") or {}
        if (not isinstance(rid,str) or not rid.startswith("resp_")
            or rid in seen or
            not isinstance(usage.get("input_tokens"),int) or usage["input_tokens"]<=0):
            raise ValueError("UNVERIFIED_OR_DUPLICATE_PROVIDER_RESPONSE")
        seen.add(rid)
        graded=grade(task,response["advisory_text"],sources)
        result["observations"].append({
          "id":task["id"],"case_id":task["case_id"],
          "prompt_sha256":sha256(prompt.encode()).hexdigest(),
          "source_ids":[x["id"] for x in sources],
          "source_hashes":{x["id"]:sha256(json.dumps(x,sort_keys=True).encode()).hexdigest() for x in sources},
          "reference_documentary_state_evaluator_only":task["reference_documentary_state"],
          "source_defined_not_operational_gold":True,
          "response_sha256":sha256(response["advisory_text"].encode()).hexdigest(),
          "provider_response_id":rid,"model":response["model"],
          "usage":usage,"grade":graded
        })
        write_json(out,result)
    data=result["observations"]
    result["observed_paid_calls"]=len(seen)
    result["source_defined_documentary_matches"]=sum(x["grade"]["documentary_match"] for x in data)
    result["valid_json_records"]=sum(x["grade"]["valid"] for x in data)
    result["valid_source_reference_records"]=sum(x["grade"]["valid_source_ids"] for x in data)
    result["unsupported_grants"]=sum(x["grade"]["unsupported_grant"] for x in data)
    result["observed_grant_support_claims"]=sum(x["grade"]["status"]=="grant_supported" for x in data)
    result["always_not_established_baseline_correct"]=sum(
        t["reference_documentary_state"]=="not_established" for t in doc["tasks"])
    result["technical_execution_complete"]=(len(data)==12 and len(seen)==12)
    result["state"]="EXECUTED_DOCUMENTARY_DEV" if result["technical_execution_complete"] else "INCOMPLETE"
    result["scientific_state"]="NO_INDEPENDENT_OPERATIONAL_ACTION_GOLD"
    write_json(out,result)
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--ledger",required=True,type=Path)
    a=p.parse_args()
    try:
        report=execute(a.out,a.ledger)
    except Exception as e:
        try: report=json.loads(a.out.read_text())
        except Exception: report={}
        report.update(state="FAILED_PRESERVE_PARTIAL",
                      error_type=type(e).__name__,
                      fully_independent_real_operational_action_gold=0,
                      no_holdout_access=True,external_submission_authorised=False)
        a.out.parent.mkdir(parents=True,exist_ok=True)
        write_json(a.out,report)
    print(json.dumps({k:report.get(k) for k in
       ("state","observed_paid_calls","source_defined_documentary_matches",
        "valid_json_records","unsupported_grants","always_not_established_baseline_correct")}))
    return 0 if report["state"]=="EXECUTED_DOCUMENTARY_DEV" else 1
if __name__=="__main__":
    raise SystemExit(main())
