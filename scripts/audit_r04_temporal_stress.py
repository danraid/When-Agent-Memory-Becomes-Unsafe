"""Independent offline source/gold separation audit for R04 development stress run.

Reports all observed errors and non-ceiling behaviour, without treating a
synthetic policy oracle or two episodes as scientific confirmatory evidence.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path
from r04_stress.instrument import episode,ARMS
from scripts.r04_temporal_authority_live import PROTO,MODEL,SEED


def audit(r):
    rows=r.get("observations",[])
    comp=r.get("compactions",[])
    expected={}
    for ep in range(2):
        data=episode(SEED,ep)
        src=sha256("\n".join(data["events"]).encode()).hexdigest()
        for c in data["cases"]:
            expected.update({(ep,c["id"],arm):{
                "source_sha256":src,"gold":c["expected_action"],"query_sha256":sha256(
                    json.dumps(c["query"],sort_keys=True,separators=(",",":")).encode()).hexdigest(),
            } for arm in ARMS})
    keys=[(x.get("episode"),x.get("id"),x.get("arm")) for x in rows]
    ids=[x.get("provider_response_id") for x in rows]+[x.get("provider_response_id") for x in comp]
    checks={
        "complete_run":r.get("state")=="EXECUTED_ALL_DEV_CASES" and len(rows)==108 and len(comp)==8,
        "protocol_hash":r.get("protocol_sha256")==sha256(PROTO.read_bytes()).hexdigest(),
        "config_hash":r.get("model_config_sha256")==sha256(MODEL.read_bytes()).hexdigest(),
        "all_paired":len(keys)==108 and len(set(keys))==108 and set(keys)==set(expected),
        "all_source_hashes_match":all(x.get("source_sha256")==expected.get(k,{}).get("source_sha256")
                                    for k,x in zip(keys,rows)),
        "all_query_hashes_match":all(x.get("query_sha256")==expected.get(k,{}).get("query_sha256")
                                    for k,x in zip(keys,rows)),
        "all_sidecar_gold_matches":all(x.get("evaluator_expected_action")==expected.get(k,{}).get("gold")
                                    for k,x in zip(keys,rows)),
        "correctness_recomputed":all(x.get("correct")==(x.get("action")==expected.get(k,{}).get("gold"))
                                   for k,x in zip(keys,rows)),
        "real_unique_provider_ids":len(ids)==116 and len(set(ids))==116 and
                                   all(isinstance(i,str) and i.startswith("resp_") for i in ids),
        "all_usage_observed":all(isinstance((x.get("usage") or {}).get("input_tokens"),int)
                                 and x["usage"]["input_tokens"]>0 for x in rows+comp),
        "no_scientific_promotion":r.get("gold_leaked_to_prompt") is False
            and r.get("confirmatory_touched") is False
            and r.get("external_submission") is False
            and r.get("measured_causal_effect") is False
            and r.get("source_parity") is True
            and r.get("token_budget_parity") is False,
    }
    byarm={}
    for arm in ARMS:
        a=[x for x in rows if x.get("arm")==arm]
        byarm[arm]={"correct":sum(x.get("correct",False) for x in a),
                    "invalid":sum(x.get("invalid_response",False) for x in a),
                    "observed":len(a),
                    "input_tokens":sum(x.get("usage",{}).get("input_tokens",0) for x in a)}
    mismatch=sum(len({x.get("action") for x in rows if x.get("id")==case["id"]})>1
                 for e in range(2) for case in episode(SEED,e)["cases"])
    return {
      "schema":"WAMBU-R04-STRESS-DETACHED-AUDIT-V1",
      "passed":all(checks.values()),"checks":checks,
      "by_arm":byarm,"paired_disagreements":mismatch,
      "discriminative_observed":any(v["correct"]<36 for v in byarm.values()),
      "new_provider_calls":0,"real_world_action_gold":0,
      "causal_result":False,"holdout_touched":False,"external_submission":False}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--report",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    result=audit(json.loads(a.report.read_text()))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"passed":result["passed"],"failed":[k for k,v in result["checks"].items() if not v],
        "by_arm":result["by_arm"],"disagreements":result["paired_disagreements"]},sort_keys=True))
    return 0 if result["passed"] else 1
if __name__=="__main__":raise SystemExit(main())
