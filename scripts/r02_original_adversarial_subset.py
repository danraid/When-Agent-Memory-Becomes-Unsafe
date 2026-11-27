"""Balanced 40-item source-aligned R02 development subset of published 200 items.

Public original Knowledge Triage authors' stress-test prompts, not new scientific
gold or confirmatory sample. Compares original regex, original cascade with Octen
vendor model-ID and GPT-5.4-mini, and original SafetyMargin. All observed
provider errors are retained; no fake success denominator or API fallback.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

from scripts.r02_execute_live_cascade import PIN, octen_vendor_providers, provider_error

# 2 base rules from each published source domain: medical, software,
# finance, legal and customer support. 10 rules * 4 forms = 40 items.
SELECTED_BASE_RULE_INDICES=(0,1,12,13,22,23,30,31,38,39)
FORMS=("imperative","declarative","conditional","passive")


def build_items(source_rows):
    if len(source_rows)!=50:
        raise ValueError("ORIGINAL_50_RULE_CORPUS_MISSING")
    out=[]
    for i in SELECTED_BASE_RULE_INDICES:
        row=source_rows[i]
        if len(row)<7:
            raise ValueError("CORPUS_ROW_SHAPE_CHANGED")
        for j,form in enumerate(FORMS):
            out.append({"id":f"R{i:02d}-{form}",
                        "domain":row[0],"form":form,
                        "text":row[j+3]})
    if len(out)!=40 or len({x["id"] for x in out})!=40:
        raise ValueError("UNEXPECTED_BENCHMARK_SUBSET")
    if Counter(x["domain"] for x in out)!={
        "medical":8,"software":8,"financial":8,"legal":8,"support":8}:
        raise ValueError("DOMAIN_BALANCE_CHANGED")
    return out


def run(upstream:Path,environ=None):
    env=os.environ if environ is None else environ
    if env.get("R02_ALLOW_LIVE_CALLS")!="true" or env.get("R02_REQUIRE_LANE")!="OCTEN_VENDOR_AND_ORIGINAL_LLM":
        raise ValueError("NON_VENDOR_LANE_DISALLOWED")
    if not env.get("OCTEN_API_KEY") or not env.get("OPENAI_API_KEY"):
        raise ValueError("MISSING_ORIGINAL_MODEL_CREDENTIALS")
    upstream=upstream.resolve()
    commit=subprocess.run(["git","-C",str(upstream),"rev-parse","HEAD"],
                    check=True,capture_output=True,text=True).stdout.strip()
    if commit!=PIN:
        raise ValueError("ORIGINAL_UPSTREAM_HASH_DRIFT")
    sys.path.insert(0,str(upstream))
    from experiments.adversarial_classifier import BASE_RULES,FORMS as upstream_forms
    from knowledge_triage.classifier import KnowledgeType, classify_instruction
    from knowledge_triage.classifier_cascade import CascadeClassifier,EncoderClassifier
    from knowledge_triage.safety_margin import classify_by_margin
    if tuple(upstream_forms)!=FORMS:
        raise ValueError("UPSTREAM_PHRASING_FORMS_CHANGED")
    examples=build_items(BASE_RULES)
    embedding,llm=octen_vendor_providers()
    rows=[]
    out={
      "schema":"WAMBU-R02-ORIGINAL-ADVERSARIAL-SUBSET-DEVELOPMENT-V1",
      "timestamp_utc":datetime.now(timezone.utc).isoformat(),
      "status":"STARTED",
      "upstream_sha":commit,
      "source_adversarial_corpus_sha256":hashlib.sha256(
        (upstream/"experiments/adversarial_classifier.py").read_bytes()).hexdigest(),
      "source_classifier_sha256":hashlib.sha256(
        (upstream/"knowledge_triage/classifier_cascade.py").read_bytes()).hexdigest(),
      "source_margin_sha256":hashlib.sha256(
        (upstream/"knowledge_triage/safety_margin.py").read_bytes()).hexdigest(),
      "selected_original_indices":list(SELECTED_BASE_RULE_INDICES),
      "model_ids_requested":{"embedding":"octen-embedding-8b","llm":"gpt-5.4-mini"},
      "vendor_endpoint_not_author_endpoint":True,
      "original_source_published_constraints_are_not_independent_gold":True,
      "original_paper_full_benchmark_reproduced":False,
      "protected_holdout_access":False,
      "external_submission_authorised":False,
      "run_scope":"PUBLIC_40_OF_200_DEVELOPMENT_DIAGNOSTIC",
      "results":rows,
      "expected_items":40,
    }
    try:
        encoder=EncoderClassifier()
        t0=time.monotonic()
        encoder.fit(embedding)
        out["encoder_fit_ms"]=round((time.monotonic()-t0)*1000,2)
    except Exception as exc:
        out["status"]="BLOCKED_ENCODER_INITIALIZATION"
        out["error"]=provider_error(exc)
        return out
    cascade=CascadeClassifier(encoder=encoder,llm_client=llm,use_llm=True)
    for item in examples:
        row={
          "id":item["id"],"domain":item["domain"],"form":item["form"],
          "input_sha256":hashlib.sha256(item["text"].encode()).hexdigest(),
        }
        try:
            baseline=classify_instruction(item["text"])
            row["regex_type"]=baseline.value
        except Exception as exc:
            row["regex_error"]=provider_error(exc)
        t0=time.monotonic()
        try:
            r=cascade.predict(item["text"])
            row.update(cascade_status="OK",cascade_type=r.type.value,
                       decided_by=r.decided_by,
                       confidence=round(float(r.confidence),6),
                       abstained=bool(r.abstained))
        except Exception as exc:
            row.update(cascade_status="FAILED",cascade_error=provider_error(exc))
        row["cascade_elapsed_ms"]=round((time.monotonic()-t0)*1000,2)
        t0=time.monotonic()
        try:
            typ,margin,raw=classify_by_margin(
                llm,item["text"],item["domain"],threshold=0.5,max_tokens=512)
            row.update(margin_status="OK",margin_type=typ.value,
                       margin=round(float(margin),6),
                       explicit_margin_marker=("SAFETY_MARGIN:" in raw.upper()),
                       raw_sha256=hashlib.sha256(raw.encode()).hexdigest())
        except Exception as exc:
            row.update(margin_status="FAILED",margin_error=provider_error(exc))
        row["margin_elapsed_ms"]=round((time.monotonic()-t0)*1000,2)
        rows.append(row)
        if len(rows)%10==0:
            print("COMPLETED_SOURCE_ITEMS",len(rows),flush=True)

    out["status"]="ALL_40_DEVELOPMENT_ITEMS_EXECUTED" if len(rows)==40 and all(
      x.get("cascade_status")=="OK" and x.get("margin_status")=="OK" and
      "regex_type" in x for x in rows) else "PARTIAL_OR_FAILED_DEVELOPMENT_ITEMS"
    out["octen_requests_attempted"]=embedding.requests
    out["octen_responses_validated"]=embedding.responses
    out["provider_substitution"]=False
    out["cascade_stage_counts"]=dict(Counter(x.get("decided_by","error") for x in rows))
    out["source_defined_constraint_rate_by_form"]={}
    for form in FORMS:
        selected=[x for x in rows if x["form"]==form]
        out["source_defined_constraint_rate_by_form"][form]={
            method:round(sum(x.get(field)=="constraint" for x in selected)/10,4)
            for method,field in (("regex","regex_type"),
                                  ("cascade","cascade_type"),
                                  ("safety_margin","margin_type"))}
    out["error_cases"]=[x["id"] for x in rows if x.get("cascade_status")!="OK" or x.get("margin_status")!="OK"]
    return out


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--upstream",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    try:
        result=run(args.upstream)
    except Exception as exc:
        result={"schema":"WAMBU-R02-ORIGINAL-ADVERSARIAL-SUBSET-DEVELOPMENT-V1",
          "status":"PRECONDITION_FAILED","error":provider_error(exc),
          "original_paper_full_benchmark_reproduced":False,
          "protected_holdout_access":False,"external_submission_authorised":False}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:result.get(k) for k in (
       "status","octen_responses_validated","cascade_stage_counts",
       "source_defined_constraint_rate_by_form")},sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
