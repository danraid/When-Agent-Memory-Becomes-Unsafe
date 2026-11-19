"""Independent offline replay audit of real R03 common-authority dev episodes.

Reconstruct public source packet hashes and evaluator decisions from the fixed
development generator. Does not call any provider or report causal effect.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
from hashlib import sha256
import json
from pathlib import Path
from temporal_v3.generator import generate_episode
from study.tasks import expected_action
from scripts.r03_common_authority_live_dev import source_packet,ARMS,PROTOCOL,MODEL_CONFIG


def audit(r:dict):
    prot=json.loads(PROTOCOL.read_text())
    recorded=r.get("results",[])
    comps=r.get("compactions",[])
    observed=defaultdict(dict)
    ids=[]
    errors=[]
    for row in recorded:
        key=(row.get("episode"),row.get("step"))
        if row.get("arm") in observed[key]:
            errors.append("DUPLICATE_CASE_ARM")
        observed[key][row.get("arm")]=row
        ids.append(row.get("provider_response_id"))
    ids += [x.get("provider_id") for x in comps]
    checks={
      "original_protocol":r.get("protocol_sha256")==sha256(PROTOCOL.read_bytes()).hexdigest()
         and r.get("model_config_sha256")==sha256(MODEL_CONFIG.read_bytes()).hexdigest(),
      "complete_real_run":r.get("status")=="EXECUTED_ALL_DEVELOPMENT_DECISIONS"
         and len(recorded)==72 and len(comps)==10,
      "model_output_ids_unique":len(ids)==82 and len(set(ids))==82
         and all(isinstance(s,str) and s.startswith("resp_") for s in ids),
      "honest_source_and_representation":r.get("source_access_matched") is True
         and r.get("computation_matched") is False
         and r.get("representation_matched") is False
         and r.get("token_budget_matched") is False
         and r.get("source_packet_divergences")==0,
      "no_scientific_promotion":r.get("confirmatory_access") is False
         and r.get("frozen_protocol") is False
         and r.get("causal_superiority_claim") is False
         and r.get("external_submission_authorised") is False
         and r.get("reference_labels_shared_with_model") is False,
      "source_episode_labels_match":True,
      "both_arms_paired":True,
      "model_usage_recorded":True,
      "evaluator_sidecar_consistent":True,
    }
    per_arm={arm:[] for arm in ARMS}
    for episode in range(2):
        e=generate_episode("WAMBU-R03-COMMON-SOURCE-20261119","development",episode,18)
        for item in e["items"]:
            key=(episode,item["step"])
            rows=observed.get(key,{})
            if set(rows)!=set(ARMS):
                checks["both_arms_paired"]=False
                continue
            h=sha256(source_packet(item).encode()).hexdigest()
            correct=expected_action(item["reference_policy"],item["request"])
            for arm,row in rows.items():
                per_arm[arm].append(row)
                if row.get("source_sha256")!=h or row.get("policy_version")!=item["policy_version"]:
                    checks["source_episode_labels_match"]=False
                if row.get("reference_action_evaluator_side_only")!=correct or row.get("correct")!=(row.get("action")==correct):
                    checks["evaluator_sidecar_consistent"]=False
                usage=row.get("usage",{})
                if not isinstance(usage.get("input_tokens"),int) or usage.get("input_tokens",0)<=0:
                    checks["model_usage_recorded"]=False
    checks["unique_recording"]=not errors and len(observed)==36
    return {
      "schema":"WAMBU-R03-DETACHED-PAIRED-SOURCE-AUDIT-V1",
      "passed":all(checks.values()),
      "checks":checks,
      "development_episode_count":2,
      "paired_model_decision_count":36,
      "per_arm":{arm:{
          "n":len(rows),
          "correct":sum(x.get("correct",False) for x in rows),
          "invalid":sum(x.get("invalid_response",False) for x in rows),
          "revocation_errors":sum(x.get("probe_kind")=="stale_rule_revocation" and not x.get("correct") for x in rows),
          "new_enforcement_errors":sum(x.get("probe_kind")=="new_rule_enforcement" and not x.get("correct") for x in rows),
          "input_tokens":sum((x.get("usage") or {}).get("input_tokens") or 0 for x in rows),
      } for arm,rows in per_arm.items()},
      "scientific_inference":"EXPLORATORY_NO_CAUSAL_COMPARISON",
      "new_paid_calls":0,
      "holdout":False,
      "author_approval":False,
      "external_submission":False
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--report",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    data=json.loads(args.report.read_text())
    result=audit(data)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"passed":result["passed"],"checks":result["checks"],"per_arm":result["per_arm"]},indent=2))
    return 0 if result["passed"] else 1

if __name__=="__main__":
    raise SystemExit(main())
