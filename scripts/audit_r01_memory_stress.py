"""Offline replay of bounded R01 retrospective memory task study, zero inference."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
from r01_documentary.challenge import validated,sources_for,grade,FIXTURE,PRIMARY
from r01_documentary.memory_stress import common_feed,deterministic_ledger,decision_prompt,words,PROTOCOL

def audit(r):
    d,primary=validated()
    cases={x["id"]:x for x in d["tasks"]}
    a=r.get("observations",[])
    ids=[x.get("provider_response_id") for x in a]
    memory=r.get("memory_evidence",{})
    arm_names={"recursive_summary","deterministic_source_ledger"}
    if "recursive_summary" in memory:
        ids.append(memory["recursive_summary"].get("compaction_response_id"))
    checks={
      "complete_25_calls":r.get("status")=="EXECUTED_ALL_MEMORY_DEV" and len(a)==24
          and len(set(ids))==25 and all(isinstance(x,str) and x.startswith("resp_") for x in ids),
      "source_fixture_integrity":r.get("fixture_sha256")==sha256(FIXTURE.read_bytes()).hexdigest()
          and r.get("authority_sha256")==sha256(PRIMARY.read_bytes()).hexdigest(),
      "common_feed":r.get("common_feed_sha256")==sha256(common_feed().encode()).hexdigest()
          and r.get("common_intake_to_both_arms") is True,
      "memories_fit_budget":set(memory)==arm_names and all(
          isinstance(memory[x].get("memory_text"),str)
          and memory[x].get("words")==words(memory[x]["memory_text"])
          and memory[x]["words"]<=220
          and memory[x].get("memory_sha256")==sha256(memory[x]["memory_text"].encode()).hexdigest()
          for x in memory),
      "no_duplicate_task_arm":True,"all_queries_and_responses_replayed":True,
      "source_defined_gold_not_action_gold":r.get("qualified_real_operational_actions")==0
          and r.get("source_defined_gold_not_independent_action_gold") is True
          and r.get("confirmatory_touched") is False
          and r.get("external_submission_authorised") is False
          and r.get("decision_time_source_exposure_matched") is False,
    }
    seen=set()
    byarm={x:[] for x in arm_names}
    for item in a:
        tid=item.get("task_id")
        arm=item.get("arm")
        key=(tid,arm)
        if tid not in cases or arm not in arm_names or key in seen:
            checks["no_duplicate_task_arm"]=False
            continue
        seen.add(key)
        byarm[arm].append(item)
        task=cases[tid]
        prompt=decision_prompt(task,memory[arm]["memory_text"])
        raw=item.get("raw_model_response")
        source=sources_for(task,d,primary)
        if (item.get("prompt_sha256")!=sha256(prompt.encode()).hexdigest()
            or not isinstance(raw,str) or item.get("response_sha256")!=sha256(raw.encode()).hexdigest()
            or item.get("evaluator_sidecar_reference")!=task["reference_documentary_state"]
            or item.get("grade")!=grade(task,raw,source)):
            checks["all_queries_and_responses_replayed"]=False
        try: parsed=json.loads(raw)
        except (ValueError,TypeError):parsed=None
        cites=parsed.get("evidence_ids",[]) if isinstance(parsed,dict) else []
        memory_citations=(isinstance(cites,list) and all(
            isinstance(cid,str) and cid in memory[arm]["memory_text"] for cid in cites))
        if item.get("memory_citations_valid")!=memory_citations:
            checks["all_queries_and_responses_replayed"]=False
    if len(seen)!=24 or any(len(byarm[x])!=12 for x in arm_names):
        checks["no_duplicate_task_arm"]=False
    summary={}
    for arm,rows in byarm.items():
        summary[arm]={
           "n":len(rows),
           "matched":sum(x.get("grade",{}).get("documentary_match",False) for x in rows),
           "valid_memory_citations":sum(x.get("memory_citations_valid",False) for x in rows),
           "unsupported_grants":sum(x.get("grade",{}).get("unsupported_grant",False) for x in rows),
           "input_tokens":sum((x.get("usage") or {}).get("input_tokens") or 0 for x in rows)
        }
        if r.get("summary",{}).get(arm,{}).get("matches")!=summary[arm]["matched"]:
            checks["all_queries_and_responses_replayed"]=False
    return {
      "schema":"WAMBU-R01-RETROSPECTIVE-MEMORY-DETACHED-V1",
      "passed":all(checks.values()),"checks":checks,
      "by_arm":summary,
      "baseline_always_not_established":10,
      "retrospective_not_real_time_operational":True,
      "model_memory_comparison_not_causal":True,
      "qualified_real_action_gold":0,
      "new_paid_calls":0,"holdout":False,"external_submission":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--report",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    o=audit(json.loads(a.report.read_text()))
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(o,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"passed":o["passed"],"failed_checks":[k for k,v in o["checks"].items() if not v],"by_arm":o["by_arm"]}))
    return 0 if o["passed"] else 1
if __name__=="__main__":raise SystemExit(main())
