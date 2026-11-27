"""Bounded real R04 development-only stress trial with checkpointed provenance."""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime,timezone
from hashlib import sha256
import json
import os
from pathlib import Path
from article_hub.evidence import write_json
from article_hub.llm import request_advisory
from study.analysis import parse_action
from study.prompts import compaction_prompt
from r04_stress.instrument import episode,ARMS,prompt_for,validate_source_parity

ROOT=Path(__file__).resolve().parents[1]
PROTO=ROOT/"protocol/R04_TEMPORAL_AUTHORITY_STRESS_DEV_V1.json"
MODEL=ROOT/"study/model_config.json"
SEED="WAMBU-R04-STRESS-DEVELOPMENT-20261119"


def safe_fail(e):
    return {"type":type(e).__name__,"text_redacted":True}


def pilot(output:Path,ledger:Path):
    p=json.loads(PROTO.read_text())
    m=json.loads(MODEL.read_text())
    if (p.get("state")!="DESIGNED_NOT_FROZEN_OR_CONFIRMED"
        or p.get("split")!="development_only"
        or p.get("episodes")!=2 or p.get("steps_per_episode")!=18
        or p.get("max_paid_calls")!=116 or
        p.get("confirmatory_holdout",False) or p.get("external_submission",False)):
        raise ValueError("UNAPPROVED_OR_DRIFTED_SCIENTIFIC_PROTOCOL")
    if os.getenv("R04_ALLOW_LIVE_DEV")!="true" or not os.getenv("OPENAI_API_KEY"):
        raise ValueError("R04_DEV_CALL_SCOPE_NOT_AVAILABLE")
    if output.exists():
        raise ValueError("R04_OUTPUT_MUST_BE_NEW")
    output.parent.mkdir(parents=True,exist_ok=True)
    report={
      "schema":"WAMBU-R04-STRESS-LIVE-DEVELOPMENT-V1",
      "state":"RUNNING",
      "date_utc":datetime.now(timezone.utc).isoformat(),
      "protocol_sha256":sha256(PROTO.read_bytes()).hexdigest(),
      "model_config_sha256":sha256(MODEL.read_bytes()).hexdigest(),
      "source_parity":True,"representation_parity":False,
      "token_budget_parity":False,
      "gold_leaked_to_prompt":False,
      "split":"development","episodes":2,"query_count":36,
      "arm_count":3,"max_calls":116,
      "observations":[],"compactions":[],
      "independent_real_world_gold":False,"measured_causal_effect":False,
      "confirmatory_touched":False,"external_submission":False}
    write_json(output,report)
    response_ids=set()
    def model_call(prompt):
        r=request_advisory(prompt,m,ledger)
        rid=r.get("provider_response_id")
        usage=r.get("observed_usage") or {}
        if (not isinstance(rid,str) or not rid.startswith("resp_")
            or rid in response_ids or
            not isinstance(usage.get("input_tokens"),int)
            or usage["input_tokens"]<=0):
            raise ValueError("INVALID_REAL_PROVIDER_EVIDENCE")
        response_ids.add(rid)
        return r
    for k in range(2):
        ep=episode(SEED,k)
        # Four sequential compactions over all eight public events. These
        # are real provider calls and are shared, never judge calls.
        summary=""
        for i in range(4):
            chunk=ep["events"][2*i:2*i+2]
            cp=compaction_prompt(summary,chunk)
            ans=model_call(cp)
            summary=ans["advisory_text"]
            report["compactions"].append({
              "episode":k,"iteration":i,"provider_response_id":ans["provider_response_id"],
              "prompt_sha256":sha256(cp.encode()).hexdigest(),
              "usage":ans["observed_usage"]})
            write_json(output,report)
        for case in ep["cases"]:
            prompts=validate_source_parity(case,ep["events"],summary)
            packet="\n".join(ep["events"])
            for arm,prompt in zip(ARMS,prompts):
                r=model_call(prompt)
                action=parse_action(r["advisory_text"])
                row={
                    "episode":k,"id":case["id"],"arm":arm,
                    "source_sha256":sha256(packet.encode()).hexdigest(),
                    "query_sha256":sha256(json.dumps(case["query"],sort_keys=True,separators=(",",":")).encode()).hexdigest(),
                    "prompt_sha256":sha256(prompt.encode()).hexdigest(),
                    "provider_response_id":r["provider_response_id"],
                    "model":r["model"],
                    "usage":r["observed_usage"],
                    "action":action,
                    "evaluator_expected_action":case["expected_action"],
                    "correct":action==case["expected_action"],
                    "invalid_response":action is None,
                    "evaluator_scenario_family":case["case_family"]}
                report["observations"].append(row)
                write_json(output,report)
    by_arm={}
    for arm in ARMS:
        rows=[x for x in report["observations"] if x["arm"]==arm]
        by_arm[arm]={
          "correct":sum(x["correct"] for x in rows),
          "decisions":len(rows),
          "invalid":sum(x["invalid_response"] for x in rows),
          "input_tokens":sum(x["usage"]["input_tokens"] for x in rows)}
    per_case={}
    for x in report["observations"]:
        per_case.setdefault(x["id"],[]).append(x["action"])
    report["paired_disagreements"]=sum(len(set(a))>1 for a in per_case.values())
    report["arm_summary"]=by_arm
    report["observed_provider_calls"]=len(response_ids)
    report["state"]="EXECUTED_ALL_DEV_CASES" if (
        len(report["observations"])==108 and len(report["compactions"])==8
        and len(response_ids)==116) else "INCOMPLETE_DEV_EXECUTION"
    report["instrument_discriminative_observed"]=any(v["correct"]<36 for v in by_arm.values())
    report["scientific_label"]=("DEVELOPMENT_NONCEILING_OBSERVED" if report["instrument_discriminative_observed"]
                                else "DEVELOPMENT_CEILING_PERSISTS")
    write_json(output,report)
    return report


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--ledger",required=True,type=Path)
    a=p.parse_args()
    try:
        r=pilot(a.out,a.ledger)
    except Exception as e:
        if a.out.exists():
            try: r=json.loads(a.out.read_text())
            except Exception: r={}
        else: r={}
        r.update(state="FAILED_PRESERVE_PARTIAL",safe_error=safe_fail(e),
                 confirmatory_touched=False,external_submission=False,
                 measured_causal_effect=False)
        a.out.parent.mkdir(parents=True,exist_ok=True)
        write_json(a.out,r)
    print(json.dumps({k:r.get(k) for k in
       ("state","scientific_label","observed_provider_calls",
        "paired_disagreements","arm_summary")},sort_keys=True))
    return 0 if r["state"]=="EXECUTED_ALL_DEV_CASES" else 1
if __name__=="__main__":
    raise SystemExit(main())
