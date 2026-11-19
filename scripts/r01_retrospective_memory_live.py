"""R01 retrospective provenance-memory trial, public dev-only 25 paid calls.

Both methods receive identical common intake; their bounded retained memories
differ and are the only evidence in the decision prompts. This does not
establish real-time policy action correctness or isolate the effect of memory.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json,os
from pathlib import Path
from article_hub.evidence import write_json
from article_hub.llm import request_advisory
from r01_documentary.challenge import validated,grade,sources_for,FIXTURE,PRIMARY
from r01_documentary.memory_stress import (
  common_feed,compaction_prompt,deterministic_ledger,bounded_memory,
  decision_prompt,PROTOCOL,words)

ROOT=Path(__file__).resolve().parents[1]
MODEL=ROOT/"study/model_config.json"
ARMS=("recursive_summary","deterministic_source_ledger")


def pilot(out:Path,ledger:Path):
    p=json.loads(PROTOCOL.read_text())
    if p.get("status")!="DEVELOPMENT_DESIGNED_NOT_LIVE_QUALIFIED" or p.get("holdout") or p.get("external_submission"):
        raise ValueError("MEMORY_STRESS_PROTOCOL_NOT_DEVELOPMENT")
    if os.environ.get("R01_ALLOW_MEMORY_DEV_CALLS")!="true" or not os.environ.get("OPENAI_API_KEY"):
        raise ValueError("MEMORY_DEV_CALLS_NOT_ENABLED")
    if out.exists():
        raise ValueError("NO_OVERWRITE_EXISTING_MEMORY_EVIDENCE")
    doc,primary=validated()
    config=json.loads(MODEL.read_text())
    feed=common_feed()
    result={
      "schema":"WAMBU-R01-RETROSPECTIVE-MEMORY-LIVE-V1",
      "status":"RUNNING",
      "split":"retrospective_public_development_only",
      "common_feed_sha256":sha256(feed.encode()).hexdigest(),
      "fixture_sha256":sha256(FIXTURE.read_bytes()).hexdigest(),
      "authority_sha256":sha256(PRIMARY.read_bytes()).hexdigest(),
      "model_config_sha256":sha256(MODEL.read_bytes()).hexdigest(),
      "common_intake_to_both_arms":True,
      "decision_time_source_exposure_matched":False,
      "memory_budget_words":220,
      "intake_words":words(feed),
      "expected_calls":25,
      "observations":[],
      "memory_evidence":{},
      "source_defined_gold_not_independent_action_gold":True,
      "qualified_real_operational_actions":0,
      "confirmatory_touched":False,
      "scientific_superiority_claim":False,
      "external_submission_authorised":False}
    out.parent.mkdir(parents=True,exist_ok=True)
    write_json(out,result)
    used=set()
    def call(prompt):
        if len(used)>=25:
            raise ValueError("EXCEEDED_25_CALL_RESEARCH_SCOPE")
        r=request_advisory(prompt,config,ledger)
        rid=r.get("provider_response_id")
        u=r.get("observed_usage") or {}
        if not isinstance(rid,str) or not rid.startswith("resp_") or rid in used or not isinstance(u.get("input_tokens"),int) or u["input_tokens"]<=0:
            raise ValueError("INVALID_PROVIDER_PROVENANCE")
        used.add(rid)
        return r
    cp=compaction_prompt()
    compactor=call(cp)
    summary=bounded_memory(compactor["advisory_text"])
    alternate=bounded_memory(deterministic_ledger())
    memories={ARMS[0]:summary,ARMS[1]:alternate}
    result["memory_evidence"]={
      arm:{"memory_text":text,
           "memory_sha256":sha256(text.encode()).hexdigest(),
           "words":words(text)}
      for arm,text in memories.items()}
    result["memory_evidence"]["recursive_summary"]["compaction_response_id"]=compactor["provider_response_id"]
    result["memory_evidence"]["recursive_summary"]["usage"]=compactor["observed_usage"]
    write_json(out,result)
    for task in doc["tasks"]:
        original_visible=sources_for(task,doc,primary)
        for arm in ARMS:
            prompt=decision_prompt(task,memories[arm])
            r=call(prompt)
            grade_result=grade(task,r["advisory_text"],original_visible)
            try:
                parsed=json.loads(r["advisory_text"])
            except (ValueError,TypeError):
                parsed=None
            citation_ids=parsed.get("evidence_ids",[]) if isinstance(parsed,dict) else []
            memory_citations=(
                isinstance(citation_ids,list) and
                all(isinstance(cid,str) and cid in memories[arm] for cid in citation_ids))
            result["observations"].append({
               "task_id":task["id"],"case_id":task["case_id"],"arm":arm,
               "prompt_sha256":sha256(prompt.encode()).hexdigest(),
               "raw_model_response":r["advisory_text"],
               "response_sha256":sha256(r["advisory_text"].encode()).hexdigest(),
               "provider_response_id":r["provider_response_id"],
               "model":r["model"],"usage":r["observed_usage"],
               "evaluator_sidecar_reference":task["reference_documentary_state"],
               "memory_citations_valid":bool(memory_citations),
               "grade":grade_result})
            write_json(out,result)
    result["observed_paid_calls"]=len(used)
    result["status"]="EXECUTED_ALL_MEMORY_DEV" if len(used)==25 and len(result["observations"])==24 else "PARTIAL_MEMORY_DEV"
    result["summary"]={}
    for arm in ARMS:
        rows=[x for x in result["observations"] if x["arm"]==arm]
        result["summary"][arm]={
          "matches":sum(x["grade"]["documentary_match"] for x in rows),
          "valid_document_citations":sum(x["grade"]["valid_source_ids"] for x in rows),
          "valid_retained_memory_citations":sum(x["memory_citations_valid"] for x in rows),
          "unsupported_grants":sum(x["grade"]["unsupported_grant"] for x in rows),
          "invalid_json":sum(not x["grade"]["valid"] for x in rows),
          "decision_input_tokens":sum(x["usage"]["input_tokens"] for x in rows)}
    result["baseline_always_not_established"]=sum(
       t["reference_documentary_state"]=="not_established" for t in doc["tasks"])
    write_json(out,result)
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--ledger",required=True,type=Path)
    args=p.parse_args()
    try:
        r=pilot(args.out,args.ledger)
    except Exception as e:
        try:r=json.loads(args.out.read_text())
        except Exception:r={}
        r.update(status="FAILED_PRESERVE_PARTIAL",
                 error_type=type(e).__name__,qualified_real_operational_actions=0,
                 confirmatory_touched=False,external_submission_authorised=False)
        args.out.parent.mkdir(parents=True,exist_ok=True)
        write_json(args.out,r)
    print(json.dumps({k:r.get(k) for k in
      ("status","observed_paid_calls","baseline_always_not_established","summary")},sort_keys=True))
    return 0 if r["status"]=="EXECUTED_ALL_MEMORY_DEV" else 1

if __name__=="__main__":
    raise SystemExit(main())
