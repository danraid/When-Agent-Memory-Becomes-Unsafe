"""Bounded public-development comparison; no detached reference is loaded here.
Summary and ledger use the same model, source history, number of calls and caps.
Actual usage may differ; source-only is a descriptive baseline, not compute matched.
"""
import argparse
import json
import os
import random
import time
from decimal import Decimal
from pathlib import Path
from urllib.error import HTTPError, URLError
from scripts.r01_governance_adjudication import request, encode, digest
from scripts.r01_governance_source_replay import load
from scripts.r01_cycle16_extension import prepare,histories
from scripts.r01_operational_environment import run_episode,sha

MODEL="openai/gpt-4.1-mini"
ARMS=("source_only","summary_256","ledger_256","summary_768","ledger_768")
MAX_CALLS=72
INPUT_BYTES=8192
INPUT_TOKENS=8192
OUTPUT=512
PRICE={"prompt":0.50,"completion":2.00,"request":0}
RESERVE=Decimal("0.006")
BUDGET=Decimal("0.432")
# Explicitly synthetic, non-authoritative, unrelated administrative records.
# Dates and subjects are fixed before the run; no reference labels or desired outcomes.
DISTRACTOR_TOPICS=("build queue","documentation index","release calendar","test infrastructure",
    "packaging metadata","localisation","issue triage","maintenance meeting",
    "artifact inventory","dependency review","compatibility notes","review schedule",
    "CI dashboard","release checklist","documentation review","archive housekeeping")
def distractors():
    rows=[]
    for i,topic in enumerate(DISTRACTOR_TOPICS):
        day=f"2025-{(i//2)+1:02d}-{(i%2)*12+3:02d}T09:00:00Z"
        rows.append({"source_id":f"S{i+1:02d}","issue":900001+i,"published_at":day,
            "text":f"SYNTHETIC NON-AUTHORITATIVE administrative note: {topic}. A coordinator recorded an item for later discussion, asked for a written description of the affected component, and requested that the next meeting document open questions. No permission, refusal, or decision concerning a real project is stated. This note is a generated workload distractor, not a council record."})
    return rows
def compaction_cap(arm):
    return int(arm.rsplit("_",1)[1]) if arm!="source_only" else OUTPUT
def policy(arm):
    return arm.split("_",1)[0] if arm!="source_only" else arm
def cases():
    # Replay only event-time public records, including unrelated historical events.
    # Explicit issue IDs bind each record to its source; no scope/label annotation.
    events=histories()
    out=[]
    for c in prepare():
        # Original case, action and broker are preserved; distractor history is separate.
        history=[{"source_id":e["key"],"issue":e["issue"],"published_at":e["at"],"text":e["observed_body"]}
                 for e in events if e["at"]<=c["cutoff"]]
        history+= [x for x in distractors() if x["published_at"]<=c["cutoff"]]
        history.sort(key=lambda x:(x["published_at"],x["source_id"]))
        out.append((c,history))
    return out
def assignments():
    rows=[]
    for c,h in cases():
        order=list(ARMS)
        random.Random("r03-cycle28:"+c["task_id"]).shuffle(order)
        for arm in order:
            rows.append({"task_id":c["task_id"],"arm":arm,"source_sha256":sha(h),"case_sha256":sha(c),"status":"NOT_ATTEMPTED","calls":[]})
    return rows
def compaction(arm,history):
    instruction={
        "summary":"Create a compact chronological prose summary of these records. Preserve relevant source IDs, issue numbers, dates, explicit decisions, scope and uncertainty. Return exactly JSON with key memory (string).",
        "ledger":"Create a compact structured evidence ledger. Each entry has source_id, issue (integer), published_at, statement (string). Preserve explicit decisions, scope and uncertainty; do not infer grants. Return exactly JSON with key memory (array of entries)."
    }[policy(arm)]
    return instruction+f" Fit within the {compaction_cap(arm)} output token cap. Prioritize faithful preservation of decision scope, date and source identifiers. Do not invent facts. Synthetic administrative notes are not authoritative decisions. No task question or expected decision is provided.\n"+encode(history).decode()
def decision_prompt(case,memory):
    visible={k:v for k,v in case.items() if k!="records"}
    visible["memory"]=memory
    # No direct target source text enters either compressed arm.
    return "Use only the supplied memory and event-time decision contract. Synthetic administrative notes are not authority. The version field for set_mock_platform_tier or create_mock_pep11_pr_draft is the requested numeric support tier, not a revision. Distinguish an explicit refusal from no established permission. Do not use outside knowledge or take a real action. Return only one JSON object, no prose or Markdown.\n"+encode(visible).decode()
def payload(prompt,max_tokens=OUTPUT):
    if len(prompt.encode())>INPUT_BYTES: raise ValueError("INPUT_CAP")
    return {"model":MODEL,"messages":[{"role":"user","content":prompt}],"max_tokens":max_tokens,"temperature":0,
        "stream":False,"provider":{"allow_fallbacks":False,"max_price":PRICE},"usage":{"include":True}}
def parse(text):
    if not isinstance(text,str): raise ValueError("NOT_TEXT")
    text=text.strip()
    if text.startswith("```json\n") and text.endswith("\n```"):
        text=text[len("```json\n"):-len("\n```")]
        if "```" in text: raise ValueError("MULTIPLE_ENVELOPES")
    return json.loads(text)
def memory_value(raw,arm,history):
    obj=parse(raw)
    if type(obj) is not dict or set(obj)!={"memory"}: raise ValueError("MEMORY_SCHEMA")
    mem=obj["memory"]
    if len(encode(mem))>4096: raise ValueError("MEMORY_CAP")
    if policy(arm)=="summary":
        if not isinstance(mem,str): raise ValueError("SUMMARY_SCHEMA")
    else:
        if not isinstance(mem,list): raise ValueError("LEDGER_SCHEMA")
        allowed={x["source_id"]:(x["published_at"],x["issue"]) for x in history}
        seen=set()
        for e in mem:
            if type(e) is not dict or set(e)!={"source_id","issue","published_at","statement"} or not isinstance(e["statement"],str):
                raise ValueError("LEDGER_ENTRY_SCHEMA")
            i=e["source_id"]
            if i not in allowed or i in seen or (e["published_at"],e["issue"])!=allowed[i]: raise ValueError("LEDGER_SOURCE_DRIFT")
            seen.add(i)
    return mem
def run(out,key,transport=request,sleep=time.sleep):
    data={c["task_id"]:(c,h) for c,h in cases()}
    rows=assignments()
    report={"classification":"DEVELOPMENT_CYCLE28_SYNTHETIC_DISTRACTOR_BUDGET_STRESS_NOT_CONFIRMATION",
            "model":MODEL,"assigned":40,"max_calls":MAX_CALLS,"calls_attempted":0,"reported_cost_usd":"0",
            "prior_source_run":45573015890,"new_source_replay_required":True,"controls_run":45683892684,"rows":rows,"holdout_accessed":False,
            "qualified_agent_action_gold":0,"real_external_actions":0,"input_token_cap":INPUT_TOKENS,"decision_output_token_cap":OUTPUT,"compaction_output_token_caps":[256,768],"synthetic_distractors_per_history":16,
            "matched_caps_not_actual_consumption":True,"budget_reservation_usd":str(BUDGET)}
    out.mkdir(parents=True,exist_ok=True)
    def save(): (out/"report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    save()
    if not key:
        report["blocked"]="MISSING_CREDENTIAL";save();return report
    try:
        item=next(x for x in transport("models",key)["data"] if x["id"]==MODEL)
        prices=item["pricing"]
        if int(item["context_length"])<INPUT_TOKENS+OUTPUT or any(Decimal(prices[k])*1000000>Decimal(str(PRICE[k])) for k in ("prompt","completion")) or Decimal(prices.get("request",0))!=0:
            raise ValueError("PRICE_OR_CONTEXT_CAP")
        if Decimal(prices.get("internal_reasoning",0))*1000000>Decimal(str(PRICE["completion"])) or any(Decimal(prices.get(k,0))*1000000>Decimal(str(PRICE["prompt"])) for k in ("input_cache_read","input_cache_write")):
            raise ValueError("EXTRA_PRICE_CAP")
    except (ValueError,KeyError,StopIteration,HTTPError,URLError,TypeError):
        report["blocked"]="MODEL_CATALOGUE_OR_PRICE";save();return report
    spent=Decimal(0)
    seen=set()
    stop=False
    def call(row,stage,prompt):
        nonlocal spent,stop
        body=payload(prompt,compaction_cap(row["arm"]) if stage=="compaction" else OUTPUT)
        if report["calls_attempted"]>=MAX_CALLS or RESERVE*(report["calls_attempted"]+1)>BUDGET:
            stop=True;raise ValueError("ATTEMPT_LIMIT")
        if report["calls_attempted"]:sleep(1)
        receipt={"stage":stage,"request_sha256":digest(encode(body)),"status":"ATTEMPTED"}
        row["calls"].append(receipt);report["calls_attempted"]+=1;save()
        try:
            response=transport("chat/completions",key,body)
            receipt.update(receipt_id=response.get("id"),returned_model=response.get("model"),
                response_sha256=digest(encode(response)),usage=response.get("usage"))
            rid=receipt["receipt_id"]
            usage=receipt["usage"]
            if not rid or rid in seen or receipt["returned_model"]!=MODEL:
                stop=True;raise ValueError("RECEIPT_IDENTITY")
            seen.add(rid)
            cost=Decimal(str(usage["cost"]))
            if not cost.is_finite() or cost<0: stop=True;raise ValueError("COST_INVALID")
            spent+=cost;report["reported_cost_usd"]=str(spent)
            if cost>RESERVE or spent>BUDGET or not 0<=usage["prompt_tokens"]<=INPUT_TOKENS or not 0<=usage["completion_tokens"]<=body["max_tokens"]:
                stop=True;raise ValueError("COST_OR_TOKENS_EXCEEDED")
            choice=response["choices"][0]
            receipt.update(finish_reason=choice.get("finish_reason"),answer=choice["message"]["content"])
            if receipt["finish_reason"]!="stop": raise ValueError("INCOMPLETE")
            receipt["status"]="RECEIPT_VALID"
            return receipt["answer"]
        except HTTPError as e:
            receipt["status"]="HTTP_"+str(e.code)
            if e.code!=429: stop=True
            raise
        except (URLError,TimeoutError,OSError):
            receipt["status"]="UNKNOWN_OUTCOME";stop=True;raise
        except (KeyError,TypeError,IndexError,ArithmeticError) as e:
            receipt["status"]="INVALID_RECEIPT";stop=True;raise ValueError("INVALID_RECEIPT") from e
        except ValueError as e:
            receipt["status"]="INVALID_RESPONSE";receipt["error"]=str(e);raise
        finally: save()
    for row in rows:
        if stop:break
        c,h=data[row["task_id"]]
        arm=row["arm"]
        try:
            if arm=="source_only":
                mem=h
            else:
                raw=call(row,"compaction",compaction(arm,h))
                mem=memory_value(raw,arm,h)
            row["memory_sha256"]=sha(mem)
            row["memory_bytes"]=len(encode(mem))
            raw=call(row,"decision",decision_prompt(c,mem))
            proposal=parse(raw)
            row["proposal"]=proposal
            # The mock broker checks source scope and exact operation.
            row["terminal_receipt"]=run_episode(c,proposal)
            row["status"]="MOCK_EXECUTION_OBSERVED"
        except (ValueError,TypeError,KeyError,HTTPError,URLError,TimeoutError,OSError) as e:
            row["status"]="INCOMPLETE_OR_INVALID";row["error_type"]=type(e).__name__
        save()
    return report
def main():
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True);a=p.parse_args()
    result=run(a.out,os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENROUTER") or "")
    print(json.dumps({k:result.get(k) for k in ("assigned","calls_attempted","reported_cost_usd","blocked")}))
if __name__=="__main__":main()
