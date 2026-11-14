#!/usr/bin/env python3
"""Offline source-pinned TypeCompact/TypeDecompose/TypeRetrieve component comparison.

Runs unmodified functions from the official pinned CIKM source checkout.
NOT the full Knowledge Triage framework/cascade, NOT a behavioural replication.
No model API, private holdout, confirmatory split or scientific signoff.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from authority_v4.casebook import assemble,CASEBOOK_VERSION
from article_hub.evidence import write_json,sha256
from scripts.audit_upstream_typecompact import _load_upstream,PIN,UPSTREAM


def audit(source:Path,out:Path):
    git=subprocess.run(["git","-C",str(source),"rev-parse","HEAD"],
                       capture_output=True,text=True,check=True).stdout.strip()
    if git!=PIN:
        raise ValueError("PINNED_KNOWLEDGE_TRIAGE_SHA_MISMATCH")
    if not (source/"LICENSE").read_text().startswith("Copyright 2026 The Knowledge Triage Authors"):
        raise ValueError("UPSTREAM_LICENSE_UNVERIFIED")
    kb_module,ops,types=_load_upstream(source)
    cases,reference=assemble()
    if len(cases)!=len(reference):
        raise ValueError("CASEBOOK_SPLIT_MISMATCH")
    rows=[]
    for case in cases:
        lines=[case["initial_message"],case["followup_message"]]
        kb=kb_module.KnowledgeBase.from_lines(lines,topic="policy",source="P07_FICTIONAL")
        regex_types=[item.type.value for item in kb.items]
        for lane in ("upstream_native_regex","source_annotated_sensitivity"):
            if lane=="upstream_native_regex":
                work=kb
            else:
                # INTERVENTION: explicitly relabels supplied case source items;
                # it is NOT the native upstream classification or full framework.
                work=kb_module.KnowledgeBase(items=[
                    kb_module.Item(text=item.text,type=types.KnowledgeType.CONSTRAINT,
                       topic=item.topic,scope=("policy",),source=item.source)
                    for item in kb.items])
            for budget in (32,64,128,256):
                compact,status=ops.type_compact(work,budget)
                partitions=ops.type_decompose(work,budget)
                violations,total=ops.constraint_locality_violations(partitions)
                corpus=work.items
                target="equipment inventory policy"
                # Fixed lexical relevance and explicit domain scope are authored
                # for this diagnostic, not from the original CIKM benchmark.
                relevance=lambda query,item:sum(w in item.text.lower() for w in query.split())
                in_scope=lambda query,item:item.topic=="policy"
                retrieved=ops.type_retrieve(corpus,target,2,relevance,in_scope)
                baseline=ops.baseline_retrieve(corpus,target,2,relevance)
                constraints=[x for x in work.items if x.type==types.KnowledgeType.CONSTRAINT]
                rows.append({
                    "case_id":case["case_id"],"lane":lane,"budget_estimated_tokens":budget,
                    "native_regex_classifications":regex_types,
                    "typecompact_status":status,
                    "typecompact_b_min":work.b_min,
                    "typecompact_output_tokens":compact.total_tokens,
                    "typecompact_source_rows_retained":sum(x.text in {y.text for y in compact.items} for x in work.items),
                    "typedecompose_partition_count":len(partitions),
                    "typedecompose_max_partition_tokens":max((p.tokens for p in partitions),default=0),
                    "typedecompose_partition_budget_valid":all(p.tokens<=budget for p in partitions),
                    "typedecompose_constraint_locality_violations":violations,
                    "typedecompose_constraints_in_scope":total,
                    "typeretrieve_constraint_recall_at_2":ops.constraint_recall_at_k(retrieved,constraints),
                    "baseline_retrieve_constraint_recall_at_2":ops.constraint_recall_at_k(baseline,constraints),
                    "model_calls":0,
                    "case_reference_visible_to_upstream":False,
                    "full_framework_reproduction":False
                })
    srcs={name:sha256((source/"knowledge_triage"/(name+".py")).read_bytes()) for name in ("classifier","kb","operators")}
    report={
        "status":"OFFLINE_ORIGINAL_THREE_OPERATORS_COMPONENTS_ONLY",
        "paper_reproduction":False,"full_framework_reproduction":False,
        "upstream_repo":UPSTREAM,"upstream_git_sha":PIN,"source_module_sha256":srcs,
        "upstream_license":"Apache-2.0","casebook_version":CASEBOOK_VERSION,
        "synthetic_public_development_cases":len(cases),"records":len(rows),
        "native_classifier_tested":"original regex only; no encoder/LLM cascade",
        "source_annotated_sensitivity":"manual relabelling; NOT native classification",
        "type_retrieve_limit":"offline fixed lexical relevance and test domain scope; NOT original paper corpus or retrieval pipeline",
        "decompose_limit":"original operator exercised on very small article-specific synthetic cases; no paper dataset/parameter replication",
        "casebook_references_supplied_to_upstream":False,
        "independent_human_adjudications":0,
        "model_calls":0,"confirmatory_touched":False,"journal_submission_authorized":False,
        "summaries":[{
            "lane":lane,"budget":budget,
            "cases":sum(x["lane"]==lane and x["budget_estimated_tokens"]==budget for x in rows),
            "unsafe":sum(x["lane"]==lane and x["budget_estimated_tokens"]==budget and x["typecompact_status"]=="COMPACTION_UNSAFE" for x in rows),
            "decompose_over_budget":sum(x["lane"]==lane and x["budget_estimated_tokens"]==budget and not x["typedecompose_partition_budget_valid"] for x in rows),
        } for lane in ("upstream_native_regex","source_annotated_sensitivity") for budget in (32,64,128,256)]
    }
    out.mkdir(parents=True,exist_ok=True)
    write_json(out/"operator_comparison.json",report)
    write_json(out/"operator_rows.json",rows)
    write_json(out/"public_cases.json",cases)
    # Sealed reference is retained in a separate artifact but never appears in
    # prompts, original operator calls, or source-visible rows.
    write_json(out/"reference_DEVELOPMENT_NOT_HUMAN.json",reference)
    report["report_sha256"]=sha256((out/"operator_comparison.json").read_bytes())
    return report


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--upstream",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    args=p.parse_args()
    result=audit(args.upstream,args.out)
    print(json.dumps({k:result[k] for k in
      ("status","synthetic_public_development_cases","records","model_calls","confirmatory_touched")},indent=2))


if __name__=="__main__":
    main()
