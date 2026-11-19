"""Execute the remaining 160 public original-source Knowledge Triage stress items.

This completes the *public 200-item source corpus coverage* when independently
combined with the archived 40-item run. This does not replicate the entire paper,
calibrate model margins or create independent operational agent-action gold.

The original upstream code is imported unmodified. A source-pinned Octen 8B
vendor adapter and original-model-ID GPT adjudicator are used; the authors'
original custom embedding endpoint is not proven equivalent. Reports are
checkpointed case by case to survive provider outages or CI timeouts.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime,timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from scripts.r02_execute_live_cascade import octen_vendor_providers, provider_error, PIN
from scripts.r02_original_adversarial_subset import SELECTED_BASE_RULE_INDICES,FORMS


def remaining_items(source_rows):
    if len(source_rows)!=50 or tuple(FORMS)!=("imperative","declarative","conditional","passive"):
        raise ValueError("ORIGINAL_SOURCE_CORPUS_DRIFT")
    excluded=set(SELECTED_BASE_RULE_INDICES)
    assert len(excluded)==10
    indices=[i for i in range(len(source_rows)) if i not in excluded]
    cases=[]
    for i in indices:
        row=source_rows[i]
        if len(row)<7:
            raise ValueError("ORIGINAL_SOURCE_ROW_DRIFT")
        for j,form in enumerate(FORMS):
            cases.append({"id":f"R{i:02d}-{form}","domain":row[0],
                          "form":form,"text":row[j+3]})
    if len(cases)!=160 or len({x["id"] for x in cases})!=160:
        raise ValueError("REMAINING_ITEM_COUNT_DRIFT")
    return cases


def atomic_json(path:Path,report:dict):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(path.name+".tmp")
    tmp.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    tmp.replace(path)


def run(upstream:Path,out_path:Path,environ=None):
    env=os.environ if environ is None else environ
    if env.get("R02_ALLOW_LIVE_CALLS")!="true" or env.get("R02_REQUIRE_LANE")!="OCTEN_VENDOR_AND_ORIGINAL_LLM":
        raise ValueError("OCTEN_EXCLUSIVE_LANE_REQUIRED")
    if not env.get("OCTEN_API_KEY") or not env.get("OPENAI_API_KEY"):
        raise ValueError("REQUIRED_VENDOR_AND_LLM_KEYS_MISSING")
    upstream=upstream.resolve()
    head=subprocess.run(["git","-C",str(upstream),"rev-parse","HEAD"],
                        capture_output=True,text=True,check=True).stdout.strip()
    if head!=PIN:
        raise ValueError("ORIGINAL_UPSTREAM_PIN_DRIFT")
    sys.path.insert(0,str(upstream))
    from experiments.adversarial_classifier import BASE_RULES, FORMS as ORIGINAL_FORMS
    from knowledge_triage.classifier import classify_instruction
    from knowledge_triage.classifier_cascade import CascadeClassifier,EncoderClassifier
    from knowledge_triage.safety_margin import classify_by_margin

    if tuple(ORIGINAL_FORMS)!=tuple(FORMS):
        raise ValueError("ORIGINAL_FORMS_DRIFT")
    cases=remaining_items(BASE_RULES)
    report={
       "schema":"WAMBU-R02-ORIGINAL-STRESS-REMAINING160-V1",
       "date_utc":datetime.now(timezone.utc).isoformat(),
       "status":"RUNNING",
       "upstream_sha":head,
       "source_adversarial_corpus_sha256":sha256(
           (upstream/"experiments/adversarial_classifier.py").read_bytes()).hexdigest(),
       "source_classifier_sha256":sha256(
           (upstream/"knowledge_triage/classifier_cascade.py").read_bytes()).hexdigest(),
       "source_margin_sha256":sha256(
           (upstream/"knowledge_triage/safety_margin.py").read_bytes()).hexdigest(),
       "previous_pilot_original_indices":list(SELECTED_BASE_RULE_INDICES),
       "remaining_original_indices":[i for i in range(50) if i not in set(SELECTED_BASE_RULE_INDICES)],
       "model_ids_requested":{"embedding":"octen-embedding-8b","llm":"gpt-5.4-mini"},
       "vendor_api_not_same_as_authors_deployment":True,
       "provider_fallback_allowed":False,
       "source_labels_are_authored_intent_not_independent_action_gold":True,
       "reference_action_gold_count":0,
       "reported_accuracy_claim":False,
       "full_paper_replication":False,
       "protected_holdout_touched":False,
       "external_submission_authorised":False,
       "expected_cases":160,
       "cases":[],
    }
    atomic_json(out_path,report)
    embedding,llm=octen_vendor_providers()
    encoder=EncoderClassifier()
    try:
        t0=time.monotonic()
        encoder.fit(embedding)
        report["encoder_fit_ms"]=round(1000*(time.monotonic()-t0),2)
    except Exception as exc:
        report["status"]="BLOCKED_ENCODER_INITIALIZATION"
        report["safe_error"]=provider_error(exc)
        report["octen_requests_attempted"]=embedding.requests
        report["octen_responses_validated"]=embedding.responses
        atomic_json(out_path,report)
        return report

    cascade=CascadeClassifier(encoder=encoder,llm_client=llm,use_llm=True)
    for num,item in enumerate(cases,1):
        entry={"id":item["id"],"domain":item["domain"],"form":item["form"],
               "input_sha256":sha256(item["text"].encode()).hexdigest()}
        try:
            entry["regex_type"]=classify_instruction(item["text"]).value
        except Exception as exc:
            entry["regex_error"]=provider_error(exc)
        t0=time.monotonic()
        try:
            prediction=cascade.predict(item["text"])
            entry.update(cascade_status="OK",cascade_type=prediction.type.value,
                         decided_by=prediction.decided_by,
                         abstained=bool(prediction.abstained),
                         confidence=round(float(prediction.confidence),6))
        except Exception as exc:
            entry.update(cascade_status="FAILED",cascade_error=provider_error(exc))
        entry["cascade_ms"]=round(1000*(time.monotonic()-t0),2)
        t0=time.monotonic()
        try:
            typ,margin,raw=classify_by_margin(
                llm,item["text"],item["domain"],threshold=0.5,max_tokens=512)
            entry.update(margin_status="OK",margin_type=typ.value,
                         margin=round(float(margin),6),
                         explicit_margin_marker=("SAFETY_MARGIN:" in raw.upper()),
                         raw_sha256=sha256(raw.encode()).hexdigest())
        except Exception as exc:
            entry.update(margin_status="FAILED",margin_error=provider_error(exc))
        entry["safety_margin_ms"]=round(1000*(time.monotonic()-t0),2)
        report["cases"].append(entry)
        report["octen_requests_attempted"]=embedding.requests
        report["octen_responses_validated"]=embedding.responses
        if num%10==0:
            print("ORIGINAL_REMAINING_ITEMS_PROCESSED",num,flush=True)
        atomic_json(out_path,report)
        time.sleep(0.12)

    rows=report["cases"]
    report["stage_counts"]=dict(Counter(x.get("decided_by","failed") for x in rows))
    report["method_coverage"]={
        "regex":sum("regex_type" in x for x in rows),
        "cascade":sum(x.get("cascade_status")=="OK" for x in rows),
        "safety_margin":sum(x.get("margin_status")=="OK" for x in rows),
        "explicit_margin_marker":sum(x.get("explicit_margin_marker") is True for x in rows),
    }
    report["source_authored_constraint_retention"]={}
    for form in FORMS:
        subset=[x for x in rows if x["form"]==form]
        report["source_authored_constraint_retention"][form]={
          "n":len(subset),
          **{key:sum(x.get(field)=="constraint" for x in subset)
             for key,field in (("regex","regex_type"),("cascade","cascade_type"),
                               ("safety_margin","margin_type"))}}
    report["failed_case_ids"]=[x["id"] for x in rows
        if x.get("cascade_status")!="OK" or x.get("margin_status")!="OK" or
           "regex_type" not in x or x.get("explicit_margin_marker") is not True]
    report["status"]="ALL_160_SOURCE_CASES_COMPLETE" if not report["failed_case_ids"] else "PARTIAL_OR_INVALID_SOURCE_RESULTS"
    atomic_json(out_path,report)
    return report


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--upstream",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    try:
        report=run(args.upstream,args.out)
    except Exception as exc:
        report={"schema":"WAMBU-R02-ORIGINAL-STRESS-REMAINING160-V1",
                "status":"PRECONDITION_FAILURE","safe_error":provider_error(exc),
                "full_paper_replication":False,"protected_holdout_touched":False,
                "external_submission_authorised":False}
        atomic_json(args.out,report)
    print(json.dumps({"status":report["status"],
       "processed":len(report.get("cases",[])),
       "failed":len(report.get("failed_case_ids",[])),
       "method_coverage":report.get("method_coverage",{}),
       "retention":report.get("source_authored_constraint_retention",{})},sort_keys=True))
    return 0 if report["status"]=="ALL_160_SOURCE_CASES_COMPLETE" else 1

if __name__=="__main__":
    raise SystemExit(main())
