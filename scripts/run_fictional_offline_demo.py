#!/usr/bin/env python3
"""Offline *illustrative* comparison of two explicitly deterministic heuristics.

No LLM inference, no genuine independent human labels, no confirmatory data.
The simplistic heuristics were designed after seeing the fictional examples:
this is a software demonstration, not an unbiased experiment.
"""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
CASES=ROOT/"fixtures/fictional_development_casebook.json"
LABELS=ROOT/"fixtures/fictional_development_roleplay_labels.json"
OUT=ROOT/"empirical/fictional_offline_demo_2026-11-15.json"

def hash_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def rule_action(rule):
    s=rule.lower()
    if any(x in s for x in ("prohibited","require rejection","reject","cannot relax")):return "reject"
    if any(x in s for x in ("permitted","allowed")):return "approve"
    return "abstain"

def latest_text(case):
    return rule_action(case["events"][-1]["rule"])

def conservative_temporal(case):
    events=case["events"]
    current=[e for e in events if e["effective_at"]<=case["decision_time"] and e["issued_at"]<=case["decision_time"]]
    if not current:return "abstain"
    first=current[0]
    active=[first]
    for e in current[1:]:
        # No assumed hierarchy. Explicit same-issuer supersession only.
        if first["issuer"]!=e["issuer"]:continue
        if first["scope"]!=e["scope"]:continue
        if first["event_id"] not in e["supersedes"]:continue
        active.append(e)
    return rule_action(active[-1]["rule"])

def main():
    book=json.loads(CASES.read_text());labels=json.loads(LABELS.read_text())
    assert book["simulation_only"] and labels["simulation_only"]
    by_label={d["case_id"]:d["action"] for d in labels["adjudications"]}
    rows=[]
    for case in book["cases"]:
        cid=case["case_id"]
        # A priori demonstration exclusions: no explicit authority delegation or
        # tie-breaker in case 06/07; no semantic scoring of their fabricated labels.
        qualified=cid not in {"FICTIONAL-DEV-06","FICTIONAL-DEV-07"}
        predictions={"last_text_heuristic":latest_text(case),"temporal_same_issuer_heuristic":conservative_temporal(case)}
        rows.append({"case_id":cid,"qualified_for_illustrative_scoring":qualified,
                     "fictional_reference_action":by_label[cid],
                     "predictions":predictions,
                     "correct":{k:(v==by_label[cid]) if qualified else None for k,v in predictions.items()},
                     "exclusion_reason":"authority/delegation or equal-rank precedence underspecified" if not qualified else None})
    n=sum(x["qualified_for_illustrative_scoring"] for x in rows)
    totals={k:sum(x["correct"][k] is True for x in rows if x["qualified_for_illustrative_scoring"])
            for k in ("last_text_heuristic","temporal_same_issuer_heuristic")}
    report={"schema":"WAMBU-FICTIONAL-OFFLINE-DEMO-V1","status":"SIMULATION_ONLY_NOT_SCIENTIFIC_EVIDENCE",
            "casebook_sha256":hash_file(CASES),"fictional_labels_sha256":hash_file(LABELS),
            "total_fictional_cases":len(rows),"illustratively_scored_cases":n,
            "excluded_underspecified_cases":len(rows)-n,
            "human_participants":0,"independent_human_adjudications":0,
            "gpt_calls":0,"confirmatory_touched":False,
            "heuristic_design_posthoc":True,"unbiased_comparison":False,
            "correct_by_heuristic":totals,"observations":rows}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({"cases":len(rows),"scored":n,"correct":totals,"output":str(OUT)},indent=2))

if __name__=="__main__":main()
