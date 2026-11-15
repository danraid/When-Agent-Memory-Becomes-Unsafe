#!/usr/bin/env python3
"""Verify v2 repairs against frozen v1 without promoting synthetic cases to human evidence."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
v1=json.loads((ROOT/"fixtures/synthetic_human_review_casebook_v1.json").read_text())
v2=json.loads((ROOT/"fixtures/synthetic_human_review_casebook_v2.json").read_text())
a={c["case_id"]:c for c in v1["cases"]}
b={c["case_id"]:c for c in v2["cases"]}
assert len(a)==len(b)==16 and set(a)==set(b)
changed={k for k in a if a[k]!=b[k]}
assert changed=={"SYN-DEV-005","SYN-DEV-010","SYN-DEV-015","SYN-DEV-016"},changed
assert b["SYN-DEV-005"]["events"][1]["scope"]=="region north"
assert b["SYN-DEV-005"]["events"][1]["supersedes"]==[]
assert b["SYN-DEV-010"]["events"][1]["issued_at"]>b["SYN-DEV-010"]["events"][0]["issued_at"]
assert b["SYN-DEV-010"]["decision_time"]>=b["SYN-DEV-010"]["events"][1]["effective_at"]
assert len(b["SYN-DEV-015"]["events"])==3
assert b["SYN-DEV-015"]["events"][2]["supersedes"]==["e2"]
assert "designated policy authority" in b["SYN-DEV-016"]["authority_context"]
assert b["SYN-DEV-016"]["events"][1]["supersedes"]==[]
assert v2["simulation_only"] is True and v2["human_review_status"]=="PENDING"
for c in b.values():
    assert c["split"]=="development" and c["synthetic"] and c["fictional_roleplay"]
    assert not any(k in c for k in ("gold_action","expected_action","adjudicated_action"))
print(json.dumps({"status":"SYNTHETIC_V2_REPAIR_STRUCTURE_PASS","cases":16,"changed":sorted(changed),"human_independent_reviews":0,"author_v2_signoff":"PENDING","confirmatory_touched":False,"publication_ready":False}))
