"""R01 independently recalculate real-source documentary pilot, no new API calls."""
from __future__ import annotations
import argparse,json
from hashlib import sha256
from pathlib import Path
from r01_documentary.challenge import FIXTURE,PRIMARY,validated,prompt_for,grade

def audit(r):
    d,p=validated()
    rows=r.get("observations",[])
    by={x.get("id"):x for x in rows}
    ids=[x.get("provider_response_id") for x in rows]
    checks={
      "complete":r.get("state")=="EXECUTED_DOCUMENTARY_DEV" and len(rows)==12
             and len(by)==12 and {t["id"] for t in d["tasks"]}==set(by),
      "fixture_sha256":r.get("fixture_sha256")==sha256(FIXTURE.read_bytes()).hexdigest(),
      "authority_sha256":r.get("authority_sha256")==sha256(PRIMARY.read_bytes()).hexdigest(),
      "real_unique_responses":len(ids)==12 and len(set(ids))==12 and
               all(isinstance(x,str) and x.startswith("resp_") for x in ids),
      "prompt_and_source_hash_reconstructed":True,
      "sidecar_and_grade_recalculated":True,
      "response_hashes":True,
      "model_usage":True,
      "no_scientific_promotion":r.get("fully_independent_real_operational_action_gold")==0
         and r.get("no_holdout_access") is True
         and r.get("external_submission_authorised") is False
    }
    grades=[]
    for t in d["tasks"]:
        rec=by.get(t["id"])
        if not rec:
            checks["prompt_and_source_hash_reconstructed"]=False
            checks["sidecar_and_grade_recalculated"]=False
            checks["response_hashes"]=False
            continue
        prompt,sources=prompt_for(t,d,p)
        if (rec.get("prompt_sha256")!=sha256(prompt.encode()).hexdigest()
            or rec.get("source_ids")!=[x["id"] for x in sources]
            or rec.get("source_hashes")!={x["id"]:sha256(json.dumps(x,sort_keys=True).encode()).hexdigest() for x in sources}):
            checks["prompt_and_source_hash_reconstructed"]=False
        if rec.get("reference_documentary_state_evaluator_only")!=t["reference_documentary_state"]:
            checks["sidecar_and_grade_recalculated"]=False
        raw=rec.get("raw_model_response")
        if not isinstance(raw,str) or rec.get("response_sha256")!=sha256(raw.encode()).hexdigest():
            checks["response_hashes"]=False
        else:
            recomputed=grade(t,raw,sources)
            grades.append(recomputed)
            if recomputed!=rec.get("grade"):
                checks["sidecar_and_grade_recalculated"]=False
        usage=rec.get("usage") or {}
        if not isinstance(usage.get("input_tokens"),int) or usage["input_tokens"]<=0:
            checks["model_usage"]=False
    correct=sum(x.get("documentary_match",False) for x in grades)
    baseline=sum(x["reference_documentary_state"]=="not_established" for x in d["tasks"])
    return {
       "schema":"WAMBU-R01-REAL-DOCUMENTARY-DETACHED-AUDIT-V1",
       "passed":all(checks.values()),"checks":checks,
       "observed":len(rows),"reference_distribution":{"grant_supported":2,"not_established":10},
       "observed_source_defined_matches":correct,
       "always_not_established_baseline_matches":baseline,
       "valid_source_citations":sum(x.get("valid_source_ids",False) for x in grades),
       "unsupported_grant_records":sum(x.get("unsupported_grant",False) for x in grades),
       "source_grounded_scope_count":1,
       "qualified_independent_agent_action_gold":0,
       "evidence_task_is_not_operational_safety":True,
       "new_paid_calls":0,"holdout_touched":False,"author_final_approval":False,
       "external_submission_authorised":False
    }
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--report",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    d=audit(json.loads(args.report.read_text()))
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(d,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"passed":d["passed"],
       "checks_failed":[k for k,v in d["checks"].items() if not v],
       "documentary_matches":d["observed_source_defined_matches"],
       "baseline":d["always_not_established_baseline_matches"],
       "valid_citations":d["valid_source_citations"],
       "unsupported_grants":d["unsupported_grant_records"]}))
    return 0 if d["passed"] else 1
if __name__=="__main__":raise SystemExit(main())
