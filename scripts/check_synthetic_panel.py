#!/usr/bin/env python3
"""Validate two explicitly fictional review files, never certify independent humans."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
book=json.loads((ROOT/"fixtures/synthetic_human_review_casebook_v1.json").read_text())
files=sorted((ROOT/"editorial").glob("synthetic_review_simulated_*_not_human.json"))
assert len(files)==2
ids={x["case_id"] for x in book["cases"]}
results=[]
for path in files:
    report=json.loads(path.read_text())
    assert report["simulation_only"] is True
    assert report["independent_human_review"] is False
    assert report["reviewer"]["real_identity_verified"] is False
    assert report["reviewer"]["kind"]=="fictional_roleplay_not_a_person"
    assert report["not_independent_of_case_generator"] is True
    assert len(report["decisions"])==len(ids)==16
    assert {d["case_id"] for d in report["decisions"]}==ids
    assert all(d["simulated"] and d["action"] in ("approve","reject","abstain") for d in report["decisions"])
    results.append({d["case_id"]:d["action"] for d in report["decisions"]})
agreement=sum(results[0][cid]==results[1][cid] for cid in ids)
assert agreement==14
print(json.dumps({"status":"SIMULATED_PANEL_STRUCTURE_PASS","cases":len(ids),"fictional_roles":len(files),
"fictional_role_agreement":agreement,"real_human_reviews":0,"author_validation":"PENDING",
"independent_scientific_validation":False,"confirmatory_touched":False}))
