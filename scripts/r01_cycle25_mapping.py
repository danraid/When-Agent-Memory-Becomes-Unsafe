"""Blind development appraisal of the eight cycle-16 mappings, no previous votes or labels."""
import argparse,json,os,random,time
from decimal import Decimal
from pathlib import Path
from urllib.error import HTTPError,URLError
from scripts.r01_governance_adjudication import request,encode,digest,parse
from scripts.r01_governance_envelope_audit import unwrap
from scripts.r01_cycle16_extension import prepare,NEW
from scripts.r01_governance_source_replay import load
MODELS=("mistralai/mistral-small-3.2-24b-instruct","google/gemini-2.5-flash")
PRICE={"prompt":2,"completion":4,"request":0}
CAP=768
INPUT_CAP=4096
RESERVE=Decimal("0.02")
SOURCE_SHA="6c41bc8859874e9b7d6a2d0c4cf71be8e65edaa74e3b20dd982752092982a34b"
def typed_action(original):
    action=dict(original)
    tier=action.pop("version")
    if action["operation"] not in ("set_mock_platform_tier","create_mock_pep11_pr_draft") or tier not in ("2","3"):
        raise ValueError("AFFECTED_OPERATION_ONLY")
    action["support_tier"]=int(tier)
    return action

def frame(source):
    data=load(NEW+"INPUT.json")["cases"]
    cases=[{"task_id":x["id"],"question":x["question"],"requested_mock_action":typed_action(x["requested_mock_action"])} for x in data if x["id"] in ("Q13","Q14","Q15","Q16")]
    assert len(cases)==4
    # Repeat only affected mapping questions, with fresh matched wrong-tier controls.
    for i,c in enumerate((cases[0],cases[2])):
        a=dict(c["requested_mock_action"])
        a["support_tier"]=5-a["support_tier"]
        cases.append({"task_id":"T"+str(i+1),"question":c["question"],"requested_mock_action":a})
    # Opaque identifiers in provider prompts; do not reveal control status.
    return cases
def payload(model,case):
    prompt=("Assess only semantic correspondence of the requested mock action to the question, irrespective of permission, refusal, or missing records. Do not adjudicate authority. A matching action may be forbidden. Evaluate operation, target and support_tier. support_tier is the numerical support classification of the platform, never a decision revision or software version. For a PR draft, it is the proposed support tier; creating a draft is not merging it. Return JSON only with mapping_status (MATCHES_REQUEST, AMBIGUOUS, MISMATCH) and mapping_reason (5-600 characters). No actions.\n"+encode({k:v for k,v in case.items() if k!='task_id'}).decode())
    assert set(case)=={"task_id","question","requested_mock_action"}
    assert len(prompt.encode())<=INPUT_CAP
    return {"model":model,"messages":[{"role":"user","content":prompt}],"max_tokens":CAP,"temperature":0,"stream":False,"provider":{"allow_fallbacks":False,"max_price":PRICE},"usage":{"include":True}}
def validate(text,case):
    text,wrapped=unwrap(text);x=json.loads(text)
    if type(x) is not dict or set(x)!={"mapping_status","mapping_reason"} or x["mapping_status"] not in ("MATCHES_REQUEST","AMBIGUOUS","MISMATCH") or not isinstance(x["mapping_reason"],str) or not 5<=len(x["mapping_reason"])<=600:raise ValueError("MAPPING_SCHEMA")
    return x,wrapped
def run(source,out,key,transport=request,sleep=time.sleep):
    cases=frame(source)
    plan=[(m,c) for m in MODELS for c in random.Random("r01-cycle25:"+m).sample(cases,len(cases))]
    assert len(plan)==12
    rows=[{"model":m,"task_id":c["task_id"],"request_sha256":digest(encode(payload(m,c))),"status":"NOT_ATTEMPTED"} for m,c in plan]
    report={"classification":"TYPED_TIER_DEVELOPMENT_APPRAISAL","assigned":12,"attempts":0,"rows":rows,"historical_authority_votes_unchanged":True,
      "packet_sha256":digest(encode(cases)),"budget_reservation_usd":"0.24","reported_cost_usd":"0","holdout_accessed":False,"qualified_operational_gold":0}
    out.mkdir(parents=True,exist_ok=True)
    def save():(out/"report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    save()
    if not key:report["blocked"]="MISSING_CREDENTIAL";save();return report
    try:
        catalogue={x["id"]:x for x in transport("models",key)["data"]}
        for m in MODELS:
            item=catalogue[m];p=item["pricing"]
            if any(Decimal(p[k])*1000000>PRICE[k] for k in ("prompt","completion")) or Decimal(p.get("request",0))!=0 or int(item["context_length"])<INPUT_CAP+CAP:
                raise ValueError("PRICE_OR_CONTEXT_CAP")
            for k,limit in (("internal_reasoning",4),("input_cache_read",2),("input_cache_write",2)):
                if Decimal(p.get(k,0) or 0)*1000000>limit:raise ValueError("EXTRA_PRICE")
    except (ValueError,KeyError,TypeError,ArithmeticError,HTTPError,URLError):
        report["blocked"]="CATALOGUE_OR_PRICE";save();return report
    seen=set();spent=Decimal(0)
    for i,((m,c),row) in enumerate(zip(plan,rows)):
        if i:sleep(3)
        assert report["attempts"]<12 and RESERVE*(report["attempts"]+1)<=Decimal("0.24")
        row["status"]="ATTEMPTED";report["attempts"]+=1;save()
        try:
            res=transport("chat/completions",key,payload(m,c))
            row.update(receipt_id=res.get("id"),provider_model=res.get("model"),response_sha256=digest(encode(res)),usage=res.get("usage"))
            rid=row["receipt_id"];u=row["usage"]
            if not rid or rid in seen or row["provider_model"]!=m:raise RuntimeError("RECEIPT_IDENTITY")
            seen.add(rid)
            cost=Decimal(str(u["cost"]))
            if not cost.is_finite() or cost<0:raise RuntimeError("INVALID_COST")
            spent+=cost;report["reported_cost_usd"]=str(spent)
            if cost>RESERVE or spent>Decimal("0.24") or not 0<=u["prompt_tokens"]<=INPUT_CAP or not 0<=u["completion_tokens"]<=CAP:raise RuntimeError("COST_OR_TOKEN_CAP")
            ch=res["choices"][0];row.update(finish_reason=ch.get("finish_reason"),answer=ch["message"]["content"])
            if row["finish_reason"]!="stop":raise ValueError("TRUNCATION")
            row["adjudication"],row["exact_envelope"]=validate(row["answer"],c)
            row["status"]="VALID_AI_ADJUDICATION"
        except HTTPError as e:
            row["status"]="HTTP_"+str(e.code)
            if e.code!=429:save();break
        except (URLError,TimeoutError,OSError):
            row["status"]="UNKNOWN_NO_RETRY";save();break
        except (RuntimeError,KeyError,TypeError,IndexError,ArithmeticError) as e:
            row["status"]="UNVERIFIED_STOP";row["error_type"]=type(e).__name__;save();break
        except ValueError as e:
            row["status"]="INVALID_RESPONSE";row["error_type"]=type(e).__name__
        save()
    return report
def main():
    p=argparse.ArgumentParser();p.add_argument("--source",type=Path,required=True);p.add_argument("--out",type=Path,required=True);a=p.parse_args()
    r=run(a.source,a.out,os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENROUTER") or "")
    print(json.dumps({"assigned":r["assigned"],"attempts":r["attempts"],"valid":sum(x["status"]=="VALID_AI_ADJUDICATION" for x in r["rows"]),"blocked":r.get("blocked")}))
if __name__=="__main__":main()
