"""No provider calls. Score all assigned rows and replay mock effects."""
import argparse
import json
from collections import Counter
from pathlib import Path
from scripts.r01_memory_policy_cycle13 import cases,assignments,ARMS,MODEL,parse,payload,compaction,decision_prompt,memory_value
from scripts.r01_governance_adjudication import digest,encode
from scripts.r01_operational_environment import sha,run_episode
from scripts.r01_operational_oracle import score
from scripts.r01_governance_source_replay import load
def audit(report):
    data={c["task_id"]:(c,h) for c,h in cases()}
    ref={x["id"]:x["label"] for x in load("fixtures/R01_R06_GOVERNANCE_LABELS_V1.json")["labels"]}
    frame=assignments()
    assert report["assigned"]==21 and len(report["rows"])==21
    assert report["holdout_accessed"] is False and report["real_external_actions"]==0
    assert report["calls_attempted"]==sum(len(r["calls"]) for r in report["rows"])<=35
    seen=set(); rows=[]
    for planned,actual in zip(frame,report["rows"]):
        assert all(planned[k]==actual[k] for k in ("task_id","arm","case_sha256","source_sha256"))
        c,h=data[actual["task_id"]];arm=actual["arm"]
        metrics={"task_id":actual["task_id"],"arm":arm,"status":actual["status"],"terminal_success":None,"unsafe_mock_effect":None,"input_tokens":0,"output_tokens":0,"cost_usd":0}
        for call in actual["calls"]:
            if call.get("receipt_id"):
                assert call["receipt_id"] not in seen;seen.add(call["receipt_id"])
            u=call.get("usage") or {}
            metrics["input_tokens"]+=u.get("prompt_tokens",0)
            metrics["output_tokens"]+=u.get("completion_tokens",0)
            metrics["cost_usd"]+=u.get("cost",0)
        if actual["status"]=="MOCK_EXECUTION_OBSERVED":
            calls=actual["calls"]
            assert len(calls)==(1 if arm=="source_only" else 2)
            assert all(x["status"]=="RECEIPT_VALID" and x["returned_model"]==MODEL and x["finish_reason"]=="stop" for x in calls)
            mem=h
            if arm!="source_only":
                assert calls[0]["stage"]=="compaction"
                assert calls[0]["request_sha256"]==digest(encode(payload(compaction(arm,h))))
                mem=memory_value(calls[0]["answer"],arm,h)
            assert actual["memory_sha256"]==sha(mem)
            assert calls[-1]["stage"]=="decision"
            assert calls[-1]["request_sha256"]==digest(encode(payload(decision_prompt(c,mem))))
            assert actual["proposal"]==parse(calls[-1]["answer"])
            assert actual["terminal_receipt"]==run_episode(c,actual["proposal"])
            s=score(c,actual["terminal_receipt"],ref[actual["task_id"]])
            metrics["terminal_success"]=s["terminal_success"];metrics["unsafe_mock_effect"]=s["unsupported_mock_effect"]
        rows.append(metrics)
    per_arm={}
    for arm in ARMS:
        a=[x for x in rows if x["arm"]==arm]
        per_arm[arm]={"assigned":len(a),"observed":sum(x["terminal_success"] is not None for x in a),
            "successes":sum(x["terminal_success"] is True for x in a),"unsafe_mock_effects":sum(x["unsafe_mock_effect"] is True for x in a),
            "unascertainable":sum(x["terminal_success"] is None for x in a),"input_tokens":sum(x["input_tokens"] for x in a),
            "output_tokens":sum(x["output_tokens"] for x in a),"reported_cost_usd":sum(x["cost_usd"] for x in a)}
    return {"classification":"DETACHED_DEVELOPMENT_MOCK_OUTCOMES_NOT_OPERATIONAL_GOLD","assigned":21,"source_events":4,"provider_attempts":report["calls_attempted"],"per_arm":per_arm,
            "paired_complete_questions":sum(all(next(x for x in rows if x["task_id"]==q and x["arm"]==a)["terminal_success"] is not None for a in ARMS) for q in data),
            "rows":rows,"qualified_agent_action_gold":0,"confirmatory":False,"holdout_accessed":False}
def main():
    p=argparse.ArgumentParser();p.add_argument("--original",type=Path,required=True);p.add_argument("--out",type=Path,required=True);a=p.parse_args()
    r=audit(json.loads(a.original.read_text()));a.out.write_text(json.dumps(r,indent=2)+"\n");print(json.dumps({k:v for k,v in r.items() if k!="rows"}))
if __name__=="__main__":main()
