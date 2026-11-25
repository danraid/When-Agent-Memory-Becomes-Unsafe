"""Bounded independent AI appraisal of eight public DEVELOPMENT questions.
Never load detached labels; no external tools, holdout, or operational actions.
"""
import argparse
import hashlib
import json
import os
import random
import time
from decimal import Decimal
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from scripts.r01_governance_source_replay import load, prompt_payload

MODELS=("openai/gpt-4.1-mini","mistralai/mistral-small-3.2-24b-instruct")
CAP=512
MAX_PRICE={"prompt":2,"completion":4,"request":0}
MAX_CALLS=16
MAX_PACKET_BYTES=4096
def digest(x):
    return hashlib.sha256(x).hexdigest()
def encode(x):
    return json.dumps(x,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode()
def request(path,key,payload=None):
    url="https://openrouter.ai/api/v1/"+path
    req=Request(url,data=None if payload is None else encode(payload),
                headers={"Authorization":"Bearer "+key,"Content-Type":"application/json","Accept":"application/json","User-Agent":"WAMBU-public-adjudication"})
    with urlopen(req,timeout=90) as f:
        return json.load(f)
def prepare(replay):
    packet=load("fixtures/R01_R06_GOVERNANCE_CASEBOOK_V1.json")
    inputs=load("fixtures/R01_R06_GOVERNANCE_INPUT_V1.json")
    events={e["key"]:e for e in packet["events"]}
    report=json.loads((replay/"report.json").read_text())
    actual=json.loads((replay/"prompts.json").read_text())
    expected=[prompt_payload(c,events,inputs["contract"]) for c in inputs["cases"]]
    if actual!=expected or report["status"]!="SOURCE_AND_TEMPORAL_PREFLIGHT_PASS_ONLY" or report["future_record_exposures"]!=0 or report["source_events"]!=4:
        raise ValueError("REPLAY_MISMATCH")
    for e in report["evidence"]:
        if not e["historical_membership_verified"] or not e["independent_api_routes_agreed"]:
            raise ValueError("UNVERIFIED_SOURCE")
        if e["comment_sha256"]!=digest(events[e["event"]]["observed_body"].encode()):
            raise ValueError("SOURCE_HASH_DRIFT")
    if len(actual)!=8 or len({x["task_id"] for x in actual})!=8:
        raise ValueError("DENOMINATOR_DRIFT")
    for x in actual:
        if set(x)!={"task_id","cutoff","question","contract","records"} or any(y["published_at"]>x["cutoff"] for y in x["records"]):
            raise ValueError("FORBIDDEN_INPUT")
    return actual
def build(model,case):
    # No reference label, other questions, decision after the cutoff, or vote.
    prompt=("You are an independent AI evidence adjudicator, not a human expert. "
            "Assess ONLY the supplied contemporaneous records. Do not infer from outside knowledge or a later decision. "
            "The requested decision is limited to the documented scope, not code correctness or actual permissions. "
            "If the source refers ambiguously to an action or there is no authority record, abstain. "
            "Return exactly one JSON object with keys decision (APPROVE, REJECT, ABSTAIN), "
            "source_ids (list of visible source IDs; empty if no records), reason (one short sentence). "
            "Do not take any real action.\n"+encode(case).decode())
    if len(prompt.encode())>MAX_PACKET_BYTES:
        raise ValueError("INPUT_CAP")
    return {"model":model,"messages":[{"role":"user","content":prompt}],"max_tokens":CAP,"temperature":0,
            "stream":False,"provider":{"allow_fallbacks":False,"max_price":MAX_PRICE},"usage":{"include":True}}
def parse(answer,case):
    d=json.loads(answer)
    if not isinstance(d,dict) or set(d)!={"decision","source_ids","reason"} or d["decision"] not in {"APPROVE","REJECT","ABSTAIN"}:
        raise ValueError("SCHEMA")
    ids=d["source_ids"]
    allowed={x["source_id"] for x in case["records"]}
    if not isinstance(ids,list) or any(not isinstance(i,str) or i not in allowed for i in ids) or len(ids)!=len(set(ids)):
        raise ValueError("INVALID_CITATION")
    if d["decision"]!="ABSTAIN" and not ids:
        raise ValueError("UNSUPPORTED_ACTION")
    if not isinstance(d["reason"],str) or not 5<=len(d["reason"])<=600:
        raise ValueError("REASON")
    return d
def run(replay,out,key,transport=request,sleep=time.sleep):
    cases=prepare(replay)
    out.mkdir(parents=True,exist_ok=True)
    plan=[(m,c) for m in MODELS for c in random.Random("r01-cycle7-"+m).sample(cases,len(cases))]
    rows=[{"model":m,"task_id":c["task_id"],"request_sha256":digest(encode(build(m,c))),"status":"NOT_ATTEMPTED"} for m,c in plan]
    report={"classification":"INDEPENDENT_AI_SOURCE_SCOPE_APPRAISAL_NOT_HUMAN_OR_CONFIRMATORY","source_run_id":45573015890,
            "packet_sha256":digest(encode(cases)),"assigned":len(plan),"models":list(MODELS),"rows":rows,
            "protected_holdout_used":False,"human_review":False,"qualified_agent_action_gold":0}
    def save():
        (out/"report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    save()
    if not key:
        report["blocked"]="MISSING_OPENROUTER_SECRET";save();return report
    catalogue={x["id"]:x for x in transport("models",key)["data"]}
    for model in MODELS:
        item=catalogue.get(model)
        if not item:
            report["blocked"]="MODEL_UNAVAILABLE";save();return report
        pricing=item["pricing"]
        if any(Decimal(pricing[k])*1000000>MAX_PRICE[k] for k in ("prompt","completion")) or Decimal(pricing.get("request","0"))!=0:
            report["blocked"]="PRICE_CAP";save();return report
    for index,((m,c),row) in enumerate(zip(plan,rows)):
        if index>=MAX_CALLS: raise AssertionError("CALL_BOUND")
        if index: sleep(3)
        row["status"]="ATTEMPTED";save()
        try:
            result=transport("chat/completions",key,build(m,c))
            row["receipt_id"]=result.get("id")
            row["provider_model"]=result.get("model")
            row["provider"]=result.get("provider")
            row["response_sha256"]=digest(encode(result))
            row["usage"]=result.get("usage")
            choice=result["choices"][0]
            row["finish_reason"]=choice.get("finish_reason")
            content=choice["message"].get("content")
            row["answer"]=content
            if not row["receipt_id"] or row["provider_model"]!=m or row["finish_reason"]!="stop":
                raise ValueError("INVALID_RECEIPT_OR_TRUNCATION")
            cost=row["usage"]["cost"]
            if not isinstance(cost,(int,float)) or cost<0 or cost>0.02 or row["usage"]["completion_tokens"]>CAP or row["usage"]["prompt_tokens"]>MAX_PACKET_BYTES:
                row["status"]="COST_OR_TOKEN_UNVERIFIED_STOP";save();break
            row["adjudication"]=parse(content,c)
            row["status"]="VALID_AI_ADJUDICATION"
        except HTTPError as e:
            row["status"]="HTTP_"+str(e.code)
        except (URLError,TimeoutError):
            row["status"]="UNKNOWN_OUTCOME_NO_RETRY"
        except (ValueError,KeyError,TypeError,IndexError) as e:
            row["status"]="INVALID_RESPONSE";row["error_type"]=type(e).__name__
        save()
    return report
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--replay",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    x=run(a.replay,a.out,os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENROUTER") or "")
    print(json.dumps({"assigned":x["assigned"],"valid":sum(z["status"]=="VALID_AI_ADJUDICATION" for z in x["rows"]),"blocked":x.get("blocked")}))
if __name__=="__main__": main()
