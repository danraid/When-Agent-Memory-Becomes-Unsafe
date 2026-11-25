"""Enforce source-scope evaluation partition; do not infer operational gold."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def partition(cases, policy):
    excluded=set(policy["exclude_from_scored_comparison"])
    ids=[c["id"] for c in cases]
    if len(set(ids))!=len(ids) or not excluded<=set(ids):
        raise ValueError("PARTITION_DRIFT")
    return ([c for c in cases if c["id"] not in excluded],
            [c for c in cases if c["id"] in excluded])
def main():
    source=json.loads((ROOT/"fixtures/R01_R06_GOVERNANCE_INPUT_V1.json").read_text())
    policy=json.loads((ROOT/"protocol/R01_SOURCE_SCOPE_POLICY_CYCLE9.json").read_text())
    scored,diagnostic=partition(source["cases"],policy)
    assert len(scored)==7 and [x["id"] for x in diagnostic]==["Q04"]
    assert policy["holdout_authorized"] is False
    assert policy["candidate_replacement"]["status"]=="UNVALIDATED_NEW_DEVELOPMENT_ITEM"
    print(json.dumps({"development_candidates":len(scored),"diagnostic_only":len(diagnostic),"qualified_operational_gold":0,"holdout_accessed":False}))
if __name__=="__main__":main()
