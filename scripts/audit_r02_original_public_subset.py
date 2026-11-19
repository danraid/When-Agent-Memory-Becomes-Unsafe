"""Detached source-anchored audit of the original Knowledge Triage 40/200 pilot.

Public source labels describe authored safety constraints. They are not
independently adjudicated agent actions, and subset recalls are descriptive.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys
from scripts.r02_original_adversarial_subset import PIN, FORMS,build_items

ROOT=Path(__file__).resolve().parents[1]


def audit(report:dict,upstream:Path):
    sys.path.insert(0,str(upstream.resolve()))
    from experiments.adversarial_classifier import BASE_RULES
    original=build_items(BASE_RULES)
    original_map={x["id"]:x for x in original}
    observed=report.get("results",[])
    ids=[x.get("id") for x in observed]
    source_hash=sha256((upstream/"experiments/adversarial_classifier.py").read_bytes()).hexdigest()
    checks={
      "pinned_upstream":report.get("upstream_sha")==PIN,
      "authored_corpus_hash":report.get("source_adversarial_corpus_sha256")==source_hash,
      "all_40_original_items":len(ids)==40 and len(set(ids))==40 and set(ids)==set(original_map),
      "exact_original_item_hashes":all(
         x.get("input_sha256")==sha256(original_map[x["id"]]["text"].encode()).hexdigest()
         for x in observed if x.get("id") in original_map),
      "forms_and_domains_unchanged":all(
         x.get("form")==original_map[x["id"]]["form"]
         and x.get("domain")==original_map[x["id"]]["domain"]
         for x in observed if x.get("id") in original_map),
      "model_ids":report.get("model_ids_requested")=={"embedding":"octen-embedding-8b","llm":"gpt-5.4-mini"},
      "no_provider_substitution":report.get("provider_substitution") is False
          and report.get("vendor_endpoint_not_author_endpoint") is True,
      "all_three_methods_run":all(
         x.get("cascade_status")=="OK" and x.get("margin_status")=="OK"
         and x.get("regex_type") for x in observed),
      "source_labels_not_independent":report.get("original_source_published_constraints_are_not_independent_gold") is True,
      "no_paper_promotion":report.get("original_paper_full_benchmark_reproduced") is False
          and report.get("protected_holdout_access") is False
          and report.get("external_submission_authorised") is False,
      "all_original_subset_done":report.get("status")=="ALL_40_DEVELOPMENT_ITEMS_EXECUTED",
    }
    rates={}
    for form in FORMS:
        subset=[x for x in observed if x.get("form")==form]
        n=len(subset)
        rates[form]={
          "n":n,
          "regex_constraint_retention":sum(x.get("regex_type")=="constraint" for x in subset),
          "cascade_constraint_retention":sum(x.get("cascade_type")=="constraint" for x in subset),
          "margin_constraint_retention":sum(x.get("margin_type")=="constraint" for x in subset),
        }
    return {
      "schema":"WAMBU-R02-ORIGINAL-SUBSET-DETACHED-AUDIT-V1",
      "passed":all(checks.values()),"checks":checks,
      "subset_results_by_form":rates,
      "observed_cascade_stages":dict(Counter(x.get("decided_by","error") for x in observed)),
      "observed_total":len(observed),
      "scientific_label_type":"PUBLIC_SOURCE_AUTHORED_CONSTRAINT_INTENT",
      "independent_agent_action_gold":0,
      "confirmatory_access":False,
      "original_paper_full_reproduction":False,
      "new_paid_provider_calls":0,
      "external_submission_authorised":False,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--report",required=True,type=Path)
    p.add_argument("--upstream",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    r=audit(json.loads(args.report.read_text()),args.upstream)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"passed":r["passed"],"failed_checks":[k for k,v in r["checks"].items() if not v],"by_form":r["subset_results_by_form"]},indent=2))
    return 0 if r["passed"] else 1
if __name__=="__main__":
    raise SystemExit(main())
