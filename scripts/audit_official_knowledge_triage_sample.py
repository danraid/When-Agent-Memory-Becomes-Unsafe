#!/usr/bin/env python3
"""Reproduce a bounded native-regex TypeCompact component sweep on official public sample.

Uses immutable upstream source and sample corpus; no GPT classifier cascade,
no human ground truth, no published experiment reproduction claim.
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
from scripts.audit_upstream_typecompact import _load_upstream,PIN
from article_hub.evidence import write_json


def git_sha(root):
    return subprocess.run(["git","-C",str(root),"rev-parse","HEAD"],
                          capture_output=True,text=True,check=True).stdout.strip()


def run(upstream:Path,out:Path,limit:int=327):
    if git_sha(upstream)!=PIN:
        raise ValueError("UPSTREAM_REVISION_NOT_PINNED")
    if not (1<=limit<=327):
        raise ValueError("FINITE_PUBLIC_SAMPLE_BOUND_REQUIRED")
    sample=upstream/"data"/"sample"
    manifest=json.loads((sample/"manifest.json").read_text())
    if manifest.get("n_files")!=327:
        raise ValueError("UPSTREAM_SAMPLE_MANIFEST_MISMATCH")
    files=manifest["files"][:limit]
    if len(files)!=limit or len({x["name"] for x in files})!=limit:
        raise ValueError("SAMPLE_FILE_LIST_INVALID")
    kb_mod,ops,cls=_load_upstream(upstream)
    K=cls.KnowledgeType
    rows=[]
    for f in files:
        path=sample/f["name"]
        data=path.read_bytes()
        text=data.decode("utf-8")
        if len(text)!=f["chars"]:
            raise ValueError("UPSTREAM_SAMPLE_LENGTH_MISMATCH_"+f["name"])
        kb=kb_mod.KnowledgeBase.from_lines(text.splitlines())
        initial_constraints=[x for x in kb.items if x.type==K.CONSTRAINT]
        for ratio in (0.25,0.50,0.75,1.0):
            budget=max(1,int(kb.total_tokens*ratio))
            result,status=ops.type_compact(kb,budget)
            out_text="\n".join(x.text for x in result.items)
            unsafe=status=="COMPACTION_UNSAFE"
            if status not in ("ok","COMPACTION_UNSAFE"):
                raise ValueError("UNKNOWN_OFFICIAL_OPERATOR_STATUS")
            rows.append({
                "sample_file":f["name"],
                "sample_sha256":hashlib.sha256(data).hexdigest(),
                "native_regex_classifier":"knowledge_triage.classifier.classify_instruction",
                "ratio":ratio,"budget_estimated_tokens":budget,
                "original_total_estimated_tokens":kb.total_tokens,
                "original_b_min_estimated_tokens":kb.b_min,
                "original_constraint_items":len(initial_constraints),
                "operator_status":status,
                "operator_output_estimated_tokens":result.total_tokens,
                "output_over_budget":result.total_tokens>budget,
                "constraints_preserved_exactly":sum(any(y.text==x.text for y in result.items)
                                                  for x in initial_constraints),
                "constraint_recall_if_feasible":(sum(any(y.text==x.text for y in result.items)
                                                  for x in initial_constraints)/len(initial_constraints)
                                                  if initial_constraints and not unsafe else None),
                "official_source_unmodified":True
            })
    summaries=[]
    for ratio in (0.25,0.50,0.75,1.0):
        subset=[x for x in rows if x["ratio"]==ratio]
        feasible=[x for x in subset if x["operator_status"]=="ok"]
        valid=[x["constraint_recall_if_feasible"] for x in feasible if x["constraint_recall_if_feasible"] is not None]
        summaries.append({"ratio":ratio,"total_files":len(subset),
            "unsafe_files":len(subset)-len(feasible),
            "output_over_budget_files":sum(x["output_over_budget"] for x in subset),
            "feasible_files":len(feasible),
            "feasible_with_constraints":len(valid),
            "native_regex_constraint_recall_mean_feasible_only":(sum(valid)/len(valid) if valid else None)})
    result={"status":"OFFICIAL_SOURCE_AND_SAMPLE_NATIVE_REGEX_TYPECOMPACT_COMPONENT_SWEEP",
            "paper_reproduction":False,"full_framework_reproduction":False,
            "official_sample_count":manifest["n_files"],
            "processed_files":limit,"rows":len(rows),"upstream_revision":PIN,
            "source_module_sha256":{x:hashlib.sha256((upstream/"knowledge_triage"/(x+".py")).read_bytes()).hexdigest()
                                     for x in ("classifier","kb","operators")},
            "sample_manifest_sha256":hashlib.sha256((sample/"manifest.json").read_bytes()).hexdigest(),
            "classifier":"original regex only; no encoder, LLM, SafetyMargin or cascade",
            "ratio_budgets":"original 4 chars/token heuristic, per-file estimated budget",
            "metric":"native regex-classified exact source constraint rows retained; not independent semantic safety labels",
            "zero_native_constraints_not_evidence_of_safety":True,
            "unsafe_excluded_from_recall_and_counted_separately":True,
            "source_annotated":False,"paid_model_calls":0,"confirmatory_touched":False,
            "independent_human_adjudications":0,"scientific_approval":False,
            "summaries":summaries}
    out.mkdir(parents=True,exist_ok=True)
    write_json(out/"official_sample_component_summary.json",result)
    write_json(out/"official_sample_component_rows.json",rows)
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--upstream",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    p.add_argument("--limit",type=int,default=327)
    a=p.parse_args()
    r=run(a.upstream,a.out,limit=a.limit)
    print(json.dumps({"status":r["status"],"processed_files":r["processed_files"],
        "rows":r["rows"],"summaries":r["summaries"]},indent=2))


if __name__=="__main__":
    main()
