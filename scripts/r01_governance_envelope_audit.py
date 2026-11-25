"""Exact-envelope sensitivity, original strict results immutable; optional single blind third opinion."""
import argparse
import hashlib
import json
import os
from decimal import Decimal
from pathlib import Path
from urllib.error import HTTPError, URLError
from scripts.r01_governance_adjudication import MODELS, prepare, build, parse, digest, encode, request
from scripts.r01_governance_source_replay import load

ORIGINAL_SHA="bba1624d2ee32547fdeccb2ae1b83faa34e6d8130884efee908793c718cdc5a3"
THIRD="google/gemini-2.5-flash"

def unwrap(text):
    if not isinstance(text,str): raise ValueError("NOT_TEXT")
    text=text.strip()
    if text.startswith("```json\n") and text.endswith("\n```"):
        inner=text[len("```json\n"):-len("\n```")]
        if "```" in inner: raise ValueError("MULTIPLE_ENVELOPES")
        return inner,True
    return text,False

def audit(replay, original):
    cases={x["task_id"]:x for x in prepare(replay)}
    refs={x["id"]:x["label"] for x in load("fixtures/R01_R06_GOVERNANCE_LABELS_V1.json")["labels"]}
    raw=original.read_bytes()
    if digest(raw)!=ORIGINAL_SHA: raise ValueError("ORIGINAL_HASH_DRIFT")
    report=json.loads(raw)
    assert report["packet_sha256"]==digest(encode(list(cases.values())))
    assert report["assigned"]==16 and len(report["rows"])==16 and report["protected_holdout_used"] is False
    assert {(r["model"],r["task_id"]) for r in report["rows"]}=={(m,q) for m in MODELS for q in cases}
    votes={}; ids=set(); recovered=[]; strict=0; cost=Decimal(0)
    for row in report["rows"]:
        m,q=row["model"],row["task_id"]
        assert row["request_sha256"]==digest(encode(build(m,cases[q])))
        assert row["receipt_id"] and row["receipt_id"] not in ids and row["provider_model"]==m and row["finish_reason"]=="stop"
        ids.add(row["receipt_id"])
        assert row["response_sha256"] and 0<=row["usage"]["cost"]<=0.02 and row["usage"]["completion_tokens"]<=512
        cost+=Decimal(str(row["usage"]["cost"]))
        text,envelope=unwrap(row["answer"])
        parsed=parse(text,cases[q])
        if row["status"]=="VALID_AI_ADJUDICATION":
            assert not envelope and row["adjudication"]==parsed
            strict+=1
        else:
            assert row["status"]=="INVALID_RESPONSE" and row["error_type"]=="JSONDecodeError" and envelope
            recovered.append({"model":m,"task_id":q,"original_status":row["status"],"answer_sha256":digest(row["answer"].encode()),"normalized_answer_sha256":digest(text.encode())})
        votes[m,q]=parsed["decision"]
    cells=[{"task_id":q,"provisional_label":refs[q],"votes":[votes[m,q] for m in MODELS],"concordant":all(votes[m,q]==refs[q] for m in MODELS)} for q in cases]
    return {"classification":"POST_HOC_EXACT_ENVELOPE_SENSITIVITY_NOT_ORIGINAL_STRICT_RESULT",
            "source_run_id":45608449806,"original_report_sha256":ORIGINAL_SHA,"assigned":16,"strict_original":strict,
            "sensitivity_valid":len(votes),"recovered":recovered,"concordant":sum(c["concordant"] for c in cells),
            "unresolved":[c["task_id"] for c in cells if not c["concordant"]],"cells":cells,"historical_reported_cost_usd":str(cost),
            "new_provider_calls":0,"qualified_agent_action_gold":0,"holdout_accessed":False},cases

def third_opinion(case,key):
    out={"classification":"NEW_SINGLE_BLIND_AI_ADVISORY_NOT_FINAL_GOLD","task_id":case["task_id"],"model":THIRD,"attempts":0,"qualified_agent_action_gold":0,"holdout_accessed":False}
    if not key: return {**out,"status":"MISSING_CREDENTIAL"}
    payload=build(THIRD,case)
    out["request_sha256"]=digest(encode(payload))
    try:
        items={x["id"]:x for x in request("models",key)["data"]}
        pricing=items[THIRD]["pricing"]
        if Decimal(pricing["prompt"])*1000000>2 or Decimal(pricing["completion"])*1000000>4 or Decimal(pricing.get("request","0"))!=0:
            return {**out,"status":"PRICE_CAP_BLOCKED"}
        out["attempts"]=1
        receipt=request("chat/completions",key,payload)
        out.update(receipt_id=receipt.get("id"),returned_model=receipt.get("model"),response_sha256=digest(encode(receipt)),usage=receipt.get("usage"))
        ch=receipt["choices"][0]
        out.update(finish_reason=ch.get("finish_reason"),answer=ch["message"]["content"])
        if not out["receipt_id"] or out["returned_model"]!=THIRD or out["finish_reason"]!="stop" or not 0<=out["usage"]["cost"]<=0.02 or out["usage"]["completion_tokens"]>512:
            raise ValueError("RECEIPT_OR_BUDGET")
        text,wrapped=unwrap(out["answer"])
        out.update(adjudication=parse(text,case),envelope=wrapped,status="VALID_THIRD_ADVISORY")
    except HTTPError as e: out["status"]="HTTP_"+str(e.code)
    except (URLError,TimeoutError): out["status"]="UNKNOWN_NO_RETRY"
    except (KeyError,ValueError,TypeError,IndexError) as e: out.update(status="INVALID_OR_BLOCKED",error_type=type(e).__name__)
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--replay",type=Path,required=True);p.add_argument("--original",type=Path,required=True);p.add_argument("--out",type=Path,required=True);p.add_argument("--third",action="store_true")
    a=p.parse_args();x,cases=audit(a.replay,a.original)
    a.out.mkdir(parents=True,exist_ok=True)
    (a.out/"sensitivity.json").write_text(json.dumps(x,indent=2)+"\n")
    print(json.dumps({k:x[k] for k in ("assigned","strict_original","sensitivity_valid","concordant","unresolved")}))
    if a.third:
        assert x["unresolved"]==["Q04"]
        y=third_opinion(cases["Q04"],os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENROUTER") or "")
        (a.out/"third.json").write_text(json.dumps(y,indent=2)+"\n")
        print(json.dumps({k:y.get(k) for k in ("status","attempts","task_id","adjudication")}))
if __name__=="__main__": main()
