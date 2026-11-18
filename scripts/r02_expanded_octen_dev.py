"""R02 bounded live Octen 8B + original GPT classifier/SafetyMargin development diagnostic.

The official pinned Knowledge Triage source is imported unchanged. This uses
Octen's vendor API, not the authors' unpublished custom serving endpoint.
No holdout, accuracy estimate, independent gold, or paper replication.
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

from scripts.r02_execute_live_cascade import PIN, original_providers, provider_error, octen_vendor_providers

ROOT=Path(__file__).resolve().parents[1]
CASES=ROOT/"fixtures/R02_EXPANDED_LIVE_DEV_2026-11-18.json"


def run(upstream: Path, fixture: Path=CASES, getenv=None) -> dict:
    env=os.environ if getenv is None else getenv
    if env.get("R02_ALLOW_LIVE_CALLS")!="true" or env.get("R02_REQUIRE_LANE")!="OCTEN_VENDOR_AND_ORIGINAL_LLM":
        raise ValueError("R02_ORIGINAL_MODEL_VENDOR_LANE_NOT_AUTHORISED")
    if not env.get("OCTEN_API_KEY") or not env.get("OPENAI_API_KEY"):
        raise ValueError("R02_REQUIRED_VENDOR_OR_LLM_SECRET_MISSING")
    head=subprocess.run(["git","-C",str(upstream),"rev-parse","HEAD"],
                        check=True,capture_output=True,text=True).stdout.strip()
    if head!=PIN:
        raise ValueError("R02_UPSTREAM_COMMIT_DRIFT")
    data=json.loads(fixture.read_text(encoding="utf-8"))
    cases=data["classifier_cases"]
    margin_cases=data["safety_margin_cases"]
    if data.get("schema")!="WAMBU-R02-EXPANDED-DEV-CASES-V1" or len(cases)!=20 or len(margin_cases)!=6:
        raise ValueError("R02_FIXTURE_UNEXPECTED")
    if len({x["id"] for x in cases+margin_cases})!=26:
        raise ValueError("R02_DUPLICATE_IDS")
    sys.path.insert(0,str(upstream.resolve()))
    from knowledge_triage.classifier_cascade import CascadeClassifier, EncoderClassifier
    from knowledge_triage.safety_margin import classify_by_margin
    # This follows the source's model identifiers. The Octen transport adapter
    # validates vendor-reported model id and 4096-dimensional vectors.
    embedding, llm=octen_vendor_providers()
    out={
      "schema":"WAMBU-R02-EXPANDED-LIVE-DIAGNOSTIC-V1",
      "timestamp_utc":datetime.now(timezone.utc).isoformat(),
      "status":"STARTED",
      "upstream_sha":head,
      "fixture_sha256":hashlib.sha256(fixture.read_bytes()).hexdigest(),
      "source_classifier_sha256":hashlib.sha256(
         (upstream/"knowledge_triage/classifier_cascade.py").read_bytes()).hexdigest(),
      "source_safety_margin_sha256":hashlib.sha256(
         (upstream/"knowledge_triage/safety_margin.py").read_bytes()).hexdigest(),
      "model_ids_requested":{"embedding":"octen-embedding-8b","llm":"gpt-5.4-mini"},
      "provider_route":"OCTEN_VENDOR_AND_ORIGINAL_LLM",
      "author_endpoint_equivalence_proven":False,
      "classification_results":[],
      "safety_margin_results":[],
      "model_runtime_available":False,
      "measured_accuracy":False,
      "reference_gold_labels":0,
      "test_input_count":26,
      "confirmatory_access":False,
      "original_paper_benchmark_reproduced":False,
      "external_journal_submission_authorised":False,
    }
    encoder=EncoderClassifier()
    try:
        t0=time.monotonic()
        encoder.fit(embedding)
        out["encoder_fit_ms"]=round((time.monotonic()-t0)*1000,2)
        out["model_runtime_available"]=True
        classifier=CascadeClassifier(encoder=encoder,llm_client=llm,use_llm=True)
    except Exception as exc:
        out["status"]="BLOCKED_ENCODER_FIT"
        out["error"]=provider_error(exc)
        out["octen_requests_attempted"]=embedding.requests
        out["octen_responses_validated"]=embedding.responses
        return out

    for item in cases:
        start=time.monotonic()
        row={"id":item["id"],
             "input_sha256":hashlib.sha256(item["text"].encode()).hexdigest()}
        try:
            result=classifier.predict(item["text"])
            row.update(status="OK",stage=result.decided_by,type=result.type.value,
                       confidence=round(float(result.confidence),6),
                       abstained=bool(result.abstained))
        except Exception as exc:
            row.update(status="FAILED",error=provider_error(exc))
        row["elapsed_ms"]=round((time.monotonic()-start)*1000,2)
        out["classification_results"].append(row)

    for item in margin_cases:
        start=time.monotonic()
        row={"id":item["id"],
             "input_sha256":hashlib.sha256(item["text"].encode()).hexdigest()}
        try:
            typ,margin,raw=classify_by_margin(llm,item["text"],item["domain"],
                                               threshold=0.5,max_tokens=512)
            row.update(status="OK",type=typ.value,
                       margin=round(float(margin),6),
                       response_sha256=hashlib.sha256(raw.encode()).hexdigest(),
                       response_has_explicit_marker=("SAFETY_MARGIN:" in raw.upper()))
        except Exception as exc:
            row.update(status="FAILED",error=provider_error(exc))
        row["elapsed_ms"]=round((time.monotonic()-start)*1000,2)
        out["safety_margin_results"].append(row)

    n_good=sum(x["status"]=="OK" for x in out["classification_results"])
    n_margin=sum(x["status"]=="OK" for x in out["safety_margin_results"])
    out["status"]=("EXECUTED_ALL_DEV_PROBES" if (n_good,n_margin)==(20,6)
                    else "PARTIAL_DEV_PROBES_WITH_FAILURES")
    out["route_counts"]=dict(Counter(x.get("stage","error") for x in out["classification_results"]))
    out["type_counts"]=dict(Counter(x.get("type","error") for x in out["classification_results"]))
    out["margin_explicit_marker_count"]=sum(
        x.get("response_has_explicit_marker",False) for x in out["safety_margin_results"])
    out["classifier_succeeded"]=n_good
    out["margin_succeeded"]=n_margin
    out["octen_requests_attempted"]=embedding.requests
    out["octen_responses_validated"]=embedding.responses
    out["no_provider_fallback"]=True
    return out


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--upstream",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    try:
        result=run(args.upstream)
    except Exception as exc:
        result={"schema":"WAMBU-R02-EXPANDED-LIVE-DIAGNOSTIC-V1",
                "status":"PRECONDITION_FAILED","error":provider_error(exc),
                "original_paper_benchmark_reproduced":False,
                "confirmatory_access":False,"external_journal_submission_authorised":False}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:result.get(k) for k in (
        "status","classifier_succeeded","margin_succeeded",
        "route_counts","octen_responses_validated")},sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
