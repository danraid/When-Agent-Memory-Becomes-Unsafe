"""R03 common-authority-source paired development experiment (live, two arms).

Both arms receive identical original authorised policy lines at each decision.
The method-specific memory differs: recursive summary vs deterministic ledger
derived only from those same visible source lines. This removes the previous
*source-access* disparity, but DOES NOT match computation, representation or
token budgets and must not be presented as an architectural causal effect.

No protected holdout, simulated-human claims or confirmatory significance.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import sys
from study.analysis import parse_action
from study.tasks import policy_text, expected_action, ledger_from_authorised_events
from study.prompts import BASE, compaction_prompt
from article_hub.evidence import write_json
from article_hub.llm import request_advisory
from temporal_v3.generator import generate_episode

ROOT=Path(__file__).resolve().parents[1]
PROTOCOL=ROOT/"protocol/R03_SHARED_AUTHORITY_SOURCE_DEVELOPMENT_V1.json"
MODEL_CONFIG=ROOT/"study/model_config.json"
ARMS=("recursive_summary_shared_source","version_aware_ledger_shared_source")


def source_packet(item):
    source=[line for line in item["history_before"] if line.startswith((
        "INITIAL AUTHORISED POLICY:", "AUTHORISED POLICY AMENDMENT #"))]
    if not source or not source[0].startswith("INITIAL AUTHORISED POLICY:"):
        raise ValueError("MISSING_VISIBLE_AUTHORITATIVE_SOURCE")
    return "\n".join(source)


def build_prompt(item, arm, summary):
    if arm not in ARMS:
        raise ValueError("INVALID_EXPERIMENT_ARM")
    packet=source_packet(item)
    if arm==ARMS[0]:
        memory="RECURSIVE COMPRESSED MEMORY:\n"+summary
    else:
        ledger=ledger_from_authorised_events(packet.split("\n"))
        memory="DERIVED ACTIVE POLICY FROM COMMON SOURCE:\n"+policy_text(ledger)
    # Both arms receive exactly the same authoritative source packet, request,
    # common instruction, and no extra reference state or oracle labels.
    return (BASE+"COMMON AUTHORISED SOURCE PACKET:\n"+packet+
            "\nARM MEMORY REPRESENTATION:\n"+memory+
            "\nCURRENT REQUEST:\n"+json.dumps(item["request"],sort_keys=True)+
            "\nJSON only.")


def validate_pair(item, prompt_a, prompt_b):
    packet=source_packet(item)
    if prompt_a.count(packet)!=1 or prompt_b.count(packet)!=1:
        raise ValueError("UNEQUAL_OR_DUPLICATE_AUTHORITATIVE_SOURCE_PACKET")
    for forbidden in ("reference_action","reference_policy","probe_kind",
                      "stale_rule_revocation","new_rule_enforcement"):
        if forbidden in prompt_a or forbidden in prompt_b:
            raise ValueError("EVALUATOR_INFORMATION_LEAKED")
    # A current-policy ledger is computed from only that same source.
    if ledger_from_authorised_events(packet.split("\n"))!=item["public_policy_ledger"]:
        raise ValueError("LEDGER_SOURCE_DISAGREEMENT")
    if prompt_a.split("CURRENT REQUEST:\n")[1]!=prompt_b.split("CURRENT REQUEST:\n")[1]:
        raise ValueError("UNEQUAL_CURRENT_REQUEST")
    return True


def safe_error(exc):
    return {"error_type":type(exc).__name__,"status":"FAILED_PROVIDER_NO_SUCCESS_CLAIM"}


def pilot(out:Path,ledger:Path):
    protocol=json.loads(PROTOCOL.read_text())
    config=json.loads(MODEL_CONFIG.read_text())
    if protocol.get("status")!="EXPLORATORY_NOT_FROZEN" or protocol.get("confirmatory_holdout") is not False:
        raise ValueError("FROZEN_BOUNDARY_CHANGED")
    if os.environ.get("R03_ALLOW_DEV_PAID_CALLS")!="true":
        raise ValueError("R03_DEV_LIVE_NOT_AUTHORISED_BY_WORKFLOW")
    if not os.environ.get("OPENAI_API_KEY"):
        raise ValueError("R03_PROVIDER_SECRET_ABSENT")
    episodes=protocol["episodes"]
    steps=protocol["steps"]
    if episodes!=2 or steps!=18:
        raise ValueError("R03_SCOPE_NOT_2_BY_18")
    calls_upper=episodes*(steps*2+(steps-1)//3)
    if calls_upper!=82 or calls_upper>protocol["approved_live_calls_upper_bound"]:
        raise ValueError("R03_CALL_SCOPE_EXCEEDED")
    result={
      "schema":"WAMBU-R03-COMMON-SOURCE-LIVE-DEVELOPMENT-V1",
      "timestamp_utc":datetime.now(timezone.utc).isoformat(),
      "status":"RUNNING",
      "protocol_sha256":sha256(PROTOCOL.read_bytes()).hexdigest(),
      "model_config_sha256":sha256(MODEL_CONFIG.read_bytes()).hexdigest(),
      "source_event_policy":"IDENTICAL_AUTHORITATIVE_PACKET_FOR_BOTH_ARMS",
      "source_access_matched":True,
      "computation_matched":False,
      "representation_matched":False,
      "token_budget_matched":False,
      "max_real_provider_calls":calls_upper,
      "split":"development",
      "episodes":episodes,
      "steps":steps,
      "results":[],
      "compactions":[],
      "source_packet_divergences":0,
      "response_ids_unique":True,
      "reference_labels_shared_with_model":False,
      "independent_gold_review":False,
      "confirmatory_access":False,
      "frozen_protocol":False,
      "causal_superiority_claim":False,
      "external_submission_authorised":False
    }
    out.parent.mkdir(parents=True,exist_ok=True)
    write_json(out,result)
    observed_ids=set()
    def request(text):
        response=request_advisory(text,config,ledger)
        rid=response.get("provider_response_id")
        usage=response.get("observed_usage") or {}
        if not isinstance(rid,str) or not rid.startswith("resp_") or rid in observed_ids:
            raise ValueError("MISSING_OR_DUPLICATE_RESPONSE_ID")
        if not isinstance(usage.get("input_tokens"),int) or usage["input_tokens"]<=0:
            raise ValueError("MISSING_REAL_INPUT_TOKENS")
        observed_ids.add(rid)
        return response
    for ep_i in range(episodes):
        ep=generate_episode("WAMBU-R03-COMMON-SOURCE-20261119","development",ep_i,steps)
        summary=""
        prior=0
        for item in ep["items"]:
            t=item["step"]
            if t and t%3==0:
                new=list(item["history_before"][prior:])
                compaction=compaction_prompt(summary,new)
                response=request(compaction)
                summary=response["advisory_text"]
                result["compactions"].append({
                    "episode":ep_i,"step":t,"provider_id":response["provider_response_id"],
                    "prompt_sha256":sha256(compaction.encode()).hexdigest(),
                    "observed_usage":response["observed_usage"]})
                prior=len(item["history_before"])
            prompts={arm:build_prompt(item,arm,summary) for arm in ARMS}
            validate_pair(item,prompts[ARMS[0]],prompts[ARMS[1]])
            packet=source_packet(item)
            # Reference oracle is consulted only here after prompts are sealed.
            expected=expected_action(item["reference_policy"],item["request"])
            if expected!=item["reference_action"]:
                raise ValueError("REFERENCE_SIDE_CAR_DRIFT")
            for arm in ARMS:
                prompt=prompts[arm]
                response=request(prompt)
                action=parse_action(response["advisory_text"])
                row={
                  "episode":ep_i,"step":t,"arm":arm,
                  "probe_kind":item["probe_kind"],
                  "policy_version":item["policy_version"],
                  "source_sha256":sha256(packet.encode()).hexdigest(),
                  "prompt_sha256":sha256(prompt.encode()).hexdigest(),
                  "prompt_characters":len(prompt),
                  "provider_response_id":response["provider_response_id"],
                  "model":response["model"],
                  "usage":response["observed_usage"],
                  "action":action,
                  "reference_action_evaluator_side_only":expected,
                  "correct":action==expected,
                  "invalid_response":action is None}
                result["results"].append(row)
            write_json(out,result)

    result["observed_provider_calls"]=len(observed_ids)
    result["expected_decisions"]=episodes*steps*2
    result["observed_compactions"]=len(result["compactions"])
    result["status"]="EXECUTED_ALL_DEVELOPMENT_DECISIONS" if (
        len(result["results"])==72 and len(result["compactions"])==10
        and len(observed_ids)==82) else "INCOMPLETE_DEV_EVIDENCE"
    arm_summary={}
    for arm in ARMS:
        rows=[r for r in result["results"] if r["arm"]==arm]
        arm_summary[arm]={
           "correct":sum(r["correct"] for r in rows),
           "decisions":len(rows),
           "invalid":sum(r["invalid_response"] for r in rows),
           "revocation_cases":sum(r["probe_kind"]=="stale_rule_revocation" for r in rows),
           "new_enforcement_cases":sum(r["probe_kind"]=="new_rule_enforcement" for r in rows),
           "revocation_errors":sum(r["probe_kind"]=="stale_rule_revocation" and not r["correct"] for r in rows),
           "new_enforcement_errors":sum(r["probe_kind"]=="new_rule_enforcement" and not r["correct"] for r in rows),
           "input_tokens":sum(r["usage"]["input_tokens"] for r in rows),
           "output_tokens":sum(r["usage"]["output_tokens"] or 0 for r in rows)
        }
    result["arm_summary"]=arm_summary
    result["full_accuracy_not_a_confirmatory_estimate"]=True
    result["independent_episode_count"]=episodes
    write_json(out,result)
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--ledger",type=Path,required=True)
    a=parser.parse_args()
    try:
        report=pilot(a.out,a.ledger)
    except Exception as exc:
        if a.out.exists():
            try: report=json.loads(a.out.read_text())
            except Exception: report={}
        else: report={}
        report.update({"status":"FAILED_PRESERVE_PARTIAL",
                       "error":safe_error(exc),
                       "causal_superiority_claim":False,
                       "confirmatory_access":False,
                       "external_submission_authorised":False})
        a.out.parent.mkdir(parents=True,exist_ok=True)
        write_json(a.out,report)
    print(json.dumps({
        "status":report["status"],
        "decisions":len(report.get("results",[])),
        "compactions":len(report.get("compactions",[])),
        "arm_summary":report.get("arm_summary")}))
    return 0 if report["status"]=="EXECUTED_ALL_DEVELOPMENT_DECISIONS" else 1


if __name__=="__main__":
    raise SystemExit(main())
