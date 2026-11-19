"""Detached 200-item source identity, completeness and exploratory retention audit.

Reads archived outputs of 40-item plus disjoint 160-item LIVE workflows; makes
no paid API calls. Verifies original public upstream content at a pinned SHA and
does not equate author-constructed constraints with independent action gold.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys

from scripts.r02_original_adversarial_subset import PIN,FORMS,build_items
from scripts.r02_original_remaining_160 import remaining_items


def audit(first:dict,second:dict,upstream:Path)->dict:
    upstream=upstream.resolve()
    sys.path.insert(0,str(upstream))
    from experiments.adversarial_classifier import BASE_RULES
    source_file=upstream/"experiments/adversarial_classifier.py"
    source_hash=sha256(source_file.read_bytes()).hexdigest()
    expected=build_items(BASE_RULES)+remaining_items(BASE_RULES)
    by_id={x["id"]:x for x in expected}
    recorded=first.get("results",[])+second.get("cases",[])
    ids=[x.get("id") for x in recorded]
    checks={
      "original_public_source_pinned":first.get("upstream_sha")==PIN and second.get("upstream_sha")==PIN,
      "original_source_sha256":first.get("source_adversarial_corpus_sha256")==source_hash
          and second.get("source_adversarial_corpus_sha256")==source_hash,
      "disjoint_public_splits":len(first.get("results",[]))==40
          and len(second.get("cases",[]))==160
          and not ({x.get("id") for x in first.get("results",[])}
                   & {x.get("id") for x in second.get("cases",[])}),
      "original_all_200_ids":len(ids)==200 and len(set(ids))==200 and set(ids)==set(by_id),
      "identical_public_source_text_hash":all(
          x.get("input_sha256")==sha256(by_id[x["id"]]["text"].encode()).hexdigest()
          for x in recorded if x.get("id") in by_id),
      "domain_and_form":all(
          x.get("domain")==by_id[x["id"]]["domain"] and x.get("form")==by_id[x["id"]]["form"]
          for x in recorded if x.get("id") in by_id),
      "original_model_ids":all(x.get("model_ids_requested")=={
          "embedding":"octen-embedding-8b","llm":"gpt-5.4-mini"} for x in (first,second)),
      "no_unmarked_substitution":first.get("provider_substitution") is False
          and second.get("provider_fallback_allowed") is False
          and first.get("vendor_endpoint_not_author_endpoint") is True
          and second.get("vendor_api_not_same_as_authors_deployment") is True,
      "all_provider_methods_recorded":all(x.get("regex_type") and
          x.get("cascade_status")=="OK" and
          x.get("margin_status")=="OK" and
          x.get("explicit_margin_marker",x.get("explicit_margin_marker",False)) is True
          for x in recorded),
      "full_source_test_runs_completed":
          first.get("status")=="ALL_40_DEVELOPMENT_ITEMS_EXECUTED"
          and second.get("status")=="ALL_160_SOURCE_CASES_COMPLETE"
          and second.get("method_coverage")=={
             "regex":160,"cascade":160,"safety_margin":160,
             "explicit_margin_marker":160},
      "not_promoted_to_scientific_confirmation":
          first.get("original_paper_full_benchmark_reproduced") is False
          and second.get("full_paper_replication") is False
          and second.get("reported_accuracy_claim") is False
          and second.get("reference_action_gold_count")==0
          and first.get("protected_holdout_access") is False
          and second.get("protected_holdout_touched") is False
          and first.get("external_submission_authorised") is False
          and second.get("external_submission_authorised") is False,
    }
    rates={}
    for form in FORMS:
        subset=[x for x in recorded if x.get("form")==form]
        rates[form]={
          "n":len(subset),
          "regex_constraint":sum(x.get("regex_type")=="constraint" for x in subset),
          "cascade_constraint":sum(x.get("cascade_type")=="constraint" for x in subset),
          "safety_margin_constraint":sum(x.get("margin_type")=="constraint" for x in subset),
        }
    deviations=[
        {"id":x["id"],"form":x["form"],"domain":x["domain"],
         "regex":x.get("regex_type"),"cascade":x.get("cascade_type"),
         "safety_margin":x.get("margin_type"),
         "margin":x.get("margin")}
        for x in recorded if x.get("cascade_type")!="constraint"
        or x.get("margin_type")!="constraint"]
    return {
      "schema":"WAMBU-R02-PUBLISHED-200-SOURCE-DETACHED-AUDIT-V1",
      "passed":all(checks.values()),"checks":checks,
      "source_authored_retention_counts_by_form":rates,
      "cascade_decision_stages":dict(Counter(x.get("decided_by","failure") for x in recorded)),
      "source_authored_discrepancies":deviations,
      "observed_source_public_items":len(recorded),
      "independently_qualified_operational_gold":0,
      "new_paid_model_calls":0,
      "author_original_endpoint_parity_established":False,
      "original_entire_paper_reproduced":False,
      "confirmatory_holdout_used":False,
      "external_submission_authorised":False,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--first40",type=Path,required=True)
    p.add_argument("--remaining160",type=Path,required=True)
    p.add_argument("--upstream",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    result=audit(json.loads(args.first40.read_text()),json.loads(args.remaining160.read_text()),args.upstream)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"passed":result["passed"],
       "n":result["observed_source_public_items"],
       "rates":result["source_authored_retention_counts_by_form"],
       "failed_checks":[k for k,v in result["checks"].items() if not v]},indent=2))
    return 0 if result["passed"] else 1

if __name__=="__main__":
    raise SystemExit(main())
