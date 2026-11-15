#!/usr/bin/env python3
"""Validate synthetic human-review intake without pretending human review happened."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/"fixtures/synthetic_human_review_casebook_v1.json"
book=json.loads(p.read_text())
assert book["simulation_only"] is True
assert book["human_review_status"]=="PENDING"
cases=book["cases"]
assert len(cases)==book["case_count"]==16
ids=[c["case_id"] for c in cases]
assert len(ids)==len(set(ids))
for c in cases:
    assert c["split"]=="development" and c["synthetic"] and c["fictional_roleplay"]
    assert len(c["events"])>=2
    assert c["writer_declaration"]["fictional_not_human"]
    assert "expected_action" not in c and "gold_action" not in c and "adjudicated_action" not in c
    assert all("action" not in e for e in c["events"])
print(json.dumps({"status":"SYNTHETIC_CASEBOOK_STRUCTURE_PASS","cases":len(cases),
                  "independent_human_reviews":0,"gold_labels":0,
                  "confirmatory_touched":False,"scientific_validation":False}))
