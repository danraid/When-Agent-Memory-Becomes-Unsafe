"""P10 original-AI-review recovery: preserve original four paid outputs, call chair ONCE.

Never repeat failed original reviewer requests. All original strict-invalid votes
remain strict-invalid. A later AI chair is an explicit amendment, not an original
simultaneous validation, human review, or a confirmatory science approval.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime, timezone
import json
import os
from pathlib import Path

from scripts.p10_ai_scientific_independent_panel import (
    ROOT, ALLOWED, prompts, chair_prompt, require,
)
from scripts.p07b_detached_panel_audit import remove_exact_envelope
from study.openrouter_comparison import OpenRouter, BenchmarkError, digest, save


ORIGINAL_RUN=44009705898
ORIGINAL_ARTIFACT=14296356384


def verify_original(original:Path,config_path:Path):
    cfg,raw,ledger,sources,prompt_items=prompts(config_path)
    original_meta=(original/"metadata.json").read_bytes()
    original_rows=(original/"original_independent_reviews.json").read_bytes()
    meta=json.loads(original_meta)
    rows=json.loads(original_rows)
    require(meta["classification"]=="FOUR_PROVIDER_INDEPENDENT_AI_ADVISORY_ONLY"
            and meta["manuscript_sha256"]==digest((ROOT/cfg["manuscript"]).read_bytes())
            and meta["config_sha256"]==digest(raw)
            and meta["author_final_decision"] is None
            and meta["protected_holdout_touched"] is False,
            "ORIGINAL_METADATA_INVALID")
    require(len(rows)==len(prompt_items)==4,"ORIGINAL_REVIEW_COUNT_WRONG")
    ids=[]
    for (role,p,selected),row in zip(prompt_items,rows):
        require(row["reviewer_id"]==role["id"]
                and row["requested_model"]==role["model"]
                and row["prompt_sha256"]==digest(p.encode())
                and row.get("review") is None
                and bool(row.get("error"))
                and bool(row.get("original_response_text"))
                and bool(row.get("response_id")),
                "ORIGINAL_REVIEW_WAS_CHANGED_OR_MISCLASSIFIED")
        ids.append(row["response_id"])
    require(len(set(ids))==4,"ORIGINAL_PROVIDER_IDS_NOT_DISTINCT")
    return cfg,meta,rows,{
        "original_metadata_sha256":digest(original_meta),
        "original_four_reviews_sha256":digest(original_rows),
        "original_response_ids":ids,
        "original_strict_valid_reviews":0,
        "original_invalid_reviews":4,
        "original_chair_executed":False,
        "source_run_id":ORIGINAL_RUN,
        "source_artifact_id":ORIGINAL_ARTIFACT,
        "source_manifest_exists":(original/"manifest.json").exists(),
        "original_source_paths":[x["evidence"] for x in ledger["claims"]]
    }


def valid_chair(raw):
    content,_=remove_exact_envelope(raw)
    try:
        d=json.loads(content)
    except (ValueError,TypeError):
        raise ValueError("CHAIR_OUTPUT_INCOMPLETE_JSON") from None
    required={"advisory_recommendation","critical_objections","minority_positions",
              "required_repairs","confidence_caveat","author_final_decision",
              "human_independent_review_completed","confirmatory_validated"}
    require(isinstance(d,dict) and set(d)==required,"CHAIR_SCHEMA_INVALID")
    require(d["advisory_recommendation"] in ALLOWED and
            d["author_final_decision"] is None and
            d["human_independent_review_completed"] is False and
            d["confirmatory_validated"] is False,
            "CHAIR_FALSE_SCIENCE_OR_HUMAN_STATUS")
    for k in ("critical_objections","minority_positions","required_repairs"):
        require(isinstance(d[k],list) and len(d[k])<=25 and
                all(isinstance(x,str) for x in d[k]),"CHAIR_LIST_INVALID")
    require(isinstance(d["confidence_caveat"],str) and len(d["confidence_caveat"])>=10,
            "CHAIR_CAVEAT_INVALID")
    return d


def recover(config_path:Path,original:Path,out:Path,secret:str,transport=None):
    require(bool(secret),"OPENROUTER_SECRET_UNAVAILABLE")
    require(not(out.exists() and any(out.iterdir())),"RECOVERY_DIRECTORY_NONEMPTY")
    cfg,meta,rows,provenance=verify_original(original,config_path)
    out.mkdir(parents=True,exist_ok=True)
    report={
        "schema":"WAMBU-P10-ORIGINAL-FOUR-AI-REVIEWS-RECOVERY-V1",
        "classification":"ORIGINAL_STRICT_REVIEW_FAILURES_PRESERVED_CHAIR_CALLED_ONLY_IN_LATER_AMENDMENT",
        **provenance,
        "created_utc":datetime.now(timezone.utc).isoformat(),
        "author_final_decision":None,"human_science_reviewers":0,
        "protected_confirmation_touched":False,"scientifically_approved":False,
        "journal_submitted":False,
    }
    save(out/"original_review_provenance.json",report)
    prompt=chair_prompt(meta["manuscript_sha256"],rows)
    chair={"chair_id":cfg["chair"]["id"],"requested_model":cfg["chair"]["model"],
           "original_chair_posthoc_amendment":True,
           "original_review_runs_preserved":True,
           "prompt_sha256":digest(prompt.encode()),
           "response_id":None,"original_text":None,
           "parsed_advisory":None,"error":None}
    client=OpenRouter(secret,out/"one_call_ledger.json",1,transport)
    try:
        result=client.call(cfg["chair"]["model"],prompt,2200)
        chair.update({"response_id":result["response_id"],
                      "original_text":result["text"],
                      "observed_model":result["observed_model"],
                      "usage":result["usage"],
                      "finish_reason":result["finish_reason"]})
        require(result["response_id"] not in provenance["original_response_ids"],
                "DUPLICATE_CHAIR_PROVIDER_ID")
        chair["parsed_advisory"]=valid_chair(result["text"])
    except (BenchmarkError,ValueError) as exc:
        chair["error"]=str(exc)[:200]
    save(out/"posthoc_ai_chair.json",chair)
    status=("AI_ADVISORY_POSTHOC_CHAIR_PARSED_ORIGINAL_REVIEWERS_INVALID"
            if chair["parsed_advisory"] is not None else
            "AI_ADVISORY_POSTHOC_CHAIR_UNPARSEABLE_OR_FAILED")
    summary={
        "classification":"P10_AI_ADVISORY_PARTIAL_ONLY_NOT_INDEPENDENT_SCIENTIFIC_CONFIRMATION",
        "original_four_valid":0,"original_four_invalid":4,
        "original_four_provider_responses":4,
        "posthoc_chair_provider_response_id_present":bool(chair["response_id"]),
        "posthoc_chair_strict_schema_valid":chair["parsed_advisory"] is not None,
        "chair_advisory":chair["parsed_advisory"]["advisory_recommendation"]
                           if chair["parsed_advisory"] is not None else None,
        "status":status,
        "author_final_decision":None,
        "independent_human_scientific_reviewers":0,
        "confirmed_scientific_result":False,"protected_holdout_touched":False,
        "scientifically_approved":False,"journal_submitted":False,
        "explicit_limitations":[
            "All original four AI reviewers failed original strict schema/quote validation.",
            "The AI chair was called only on a subsequent amended workflow, not during original execution.",
            "Raw review content is preserved even when automated evidence qualification fails.",
            "AI reviewer statements cannot substitute for an independently adjudicated naturalistic reference.",
            "The author, not any of five AI models, is the only final approver."
        ],
    }
    save(out/"summary.json",summary)
    save(out/"manifest.json",{
        "sha256":{p.name:digest(p.read_bytes()) for p in out.glob("*.json")
                  if p.name!="manifest.json"},
        "strict_original_valid_reviews":0,
        "new_paid_calls_reserved":1,
        "author_final_decision":None,
        "human_reviewers":0,
        "confirmed_scientific_result":False
    })
    print(json.dumps(summary,indent=2),flush=True)
    return summary


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--config",type=Path,default=ROOT/"protocol/P10_AI_MANAGED_SCIENTIFIC_REVIEW_V1.json")
    p.add_argument("--original",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--execute",action="store_true")
    a=p.parse_args()
    if not a.execute:
        p.error("One paid AI-chair call requires --execute")
    s=recover(a.config,a.original,a.out,
              os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENROUTER") or "")
    return 0 if s["posthoc_chair_provider_response_id_present"] else 3


if __name__=="__main__":
    raise SystemExit(main())
