"""Detached, zero-provider-call audit of archived R02 expanded development run.

Checks immutable input identities, recorded provider identity, counts and stage
integrity. It does NOT validate model predictions against scientific gold.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PIN="a6ceb01a3368cee25ef7ebcf05ebdab8c9be24a4"


def audit(report: dict, fixture: dict) -> dict:
    expected_cases={x["id"]:x for x in fixture["classifier_cases"]}
    expected_margins={x["id"]:x for x in fixture["safety_margin_cases"]}
    classifications=report.get("classification_results",[])
    margins=report.get("safety_margin_results",[])
    def unique_ids(rows):
        return len({r.get("id") for r in rows})==len(rows)
    checks={
       "original_upstream_commit": report.get("upstream_sha")==PIN,
       "fixture_integrity": report.get("fixture_sha256")==hashlib.sha256(
           (ROOT/"fixtures/R02_EXPANDED_LIVE_DEV_2026-11-18.json").read_bytes()).hexdigest(),
       "all_20_items":len(classifications)==20 and unique_ids(classifications)
             and {x.get("id") for x in classifications}==set(expected_cases),
       "all_6_margins":len(margins)==6 and unique_ids(margins)
             and {x.get("id") for x in margins}==set(expected_margins),
       "input_hashes":all(
           x.get("input_sha256")==hashlib.sha256(expected_cases[x["id"]]["text"].encode()).hexdigest()
           for x in classifications if x.get("id") in expected_cases)
           and all(
           x.get("input_sha256")==hashlib.sha256(expected_margins[x["id"]]["text"].encode()).hexdigest()
           for x in margins if x.get("id") in expected_margins),
       "models_recorded":report.get("model_ids_requested")=={
           "embedding":"octen-embedding-8b","llm":"gpt-5.4-mini"},
       "sole_vendor_lane":report.get("provider_route")=="OCTEN_VENDOR_AND_ORIGINAL_LLM"
           and report.get("no_provider_fallback") is True,
       "all_status_ok":all(x.get("status")=="OK" for x in classifications+margins),
       "valid_prediction_type_and_route":all(
           x.get("type") in {"constraint","procedural","belief","preference","episodic"}
           and x.get("stage") in {"regex","encoder","llm","abstain_as_hard"}
           and isinstance(x.get("confidence"),(int,float))
           and 0<=x["confidence"]<=1
           for x in classifications),
       "valid_margins":all(
           x.get("type") in {"constraint","belief"}
           and isinstance(x.get("margin"),(float,int))
           and 0<=x["margin"]<=1
           for x in margins),
       "all_explicit_margin_markers":all(
           x.get("response_has_explicit_marker") is True for x in margins),
       "route_count_consistency":report.get("route_counts")==dict(
           Counter(x.get("stage") for x in classifications)),
       "all_octen_vectors_validated":report.get("octen_responses_validated")==25
           and report.get("octen_requests_attempted")==25,
       "no_scientific_promotion":report.get("reference_gold_labels")==0
           and report.get("measured_accuracy") is False
           and report.get("original_paper_benchmark_reproduced") is False
           and report.get("author_endpoint_equivalence_proven") is False
           and report.get("confirmatory_access") is False
           and report.get("external_journal_submission_authorised") is False,
       "all_dev_probes_executed":report.get("status")=="EXECUTED_ALL_DEV_PROBES"
           and report.get("classifier_succeeded")==20
           and report.get("margin_succeeded")==6,
    }
    diagnostic_note={
        "s04_reviewer_attention":next(({"margin":x.get("margin"),"type":x.get("type")}
                         for x in margins if x.get("id")=="S04"),None),
        "interpretation":"S04 designed as a noncritical development example; a high margin is only a screening signal, not an independently validated false positive.",
    }
    return {
      "schema":"WAMBU-R02-EXPANDED-DETACHED-AUDIT-V1",
      "passed":all(checks.values()),"checks":checks,
      "observed_route_counts":dict(Counter(x.get("stage") for x in classifications)),
      "observed_type_counts":dict(Counter(x.get("type") for x in classifications)),
      "classifier_count":len(classifications),"safety_margin_count":len(margins),
      "safety_margin_observations":[{"id":x["id"],"type":x.get("type"),"margin":x.get("margin")}
                                    for x in margins],
      "diagnostic_note":diagnostic_note,
      "genuine_human_reference_actions":0,
      "author_final_approval":False,
      "holdout_touched":False,
      "original_paper_replicated":False,
      "new_paid_model_calls":0,
      "external_submission_authorised":False,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--report",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    report=json.loads(args.report.read_text(encoding="utf-8"))
    fixture=json.loads((ROOT/"fixtures/R02_EXPANDED_LIVE_DEV_2026-11-18.json").read_text(encoding="utf-8"))
    result=audit(report,fixture)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"passed":result["passed"],
       "classifier":result["classifier_count"],
       "safety_margin":result["safety_margin_count"],
       "failed_checks":[k for k,v in result["checks"].items() if not v]},indent=2))
    return 0 if result["passed"] else 1

if __name__=="__main__":
    raise SystemExit(main())
