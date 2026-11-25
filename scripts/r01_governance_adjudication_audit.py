"""Detached scoring of original AI responses. Never calls a provider."""
import argparse
import json
from collections import Counter
from pathlib import Path
from scripts.r01_governance_source_replay import load
from scripts.r01_governance_adjudication import MODELS,prepare,parse,build,digest,encode

def audit(replay,original):
    cases={x["task_id"]:x for x in prepare(replay)}
    ref={x["id"]:x["label"] for x in load("fixtures/R01_R06_GOVERNANCE_LABELS_V1.json")["labels"]}
    r=json.loads(original.read_text())
    assert r["assigned"]==16 and r["protected_holdout_used"] is False
    assert r["packet_sha256"]==digest(encode(list(cases.values())))
    assert len(r["rows"])==16
    assert {(x["model"],x["task_id"]) for x in r["rows"]}=={(m,i) for m in MODELS for i in cases}
    ids=set()
    valid={}
    for row in r["rows"]:
        k=(row["model"],row["task_id"])
        assert row["request_sha256"]==digest(encode(build(k[0],cases[k[1]])))
        if row["status"]!="VALID_AI_ADJUDICATION": continue
        assert row["provider_model"]==k[0] and row["finish_reason"]=="stop"
        assert row["receipt_id"] and row["receipt_id"] not in ids
        ids.add(row["receipt_id"])
        v=parse(row["answer"],cases[k[1]])
        assert v==row["adjudication"]
        valid[k]=v["decision"]
    cells=[]
    for i in cases:
        votes=[valid.get((m,i)) for m in MODELS]
        same=all(v is not None for v in votes) and votes[0]==votes[1]
        cells.append({"task_id":i,"provisional_label":ref[i],"votes":votes,"agreement":same,
                      "status":"AI_CONCORDANT_WITH_REFERENCE" if same and votes[0]==ref[i] else "UNRESOLVED"})
    return {"status":"AI_ADJUDICATION_RECEIPTS_AUDITED_NOT_ACTION_GOLD","source_events":4,"questions":8,"assigned":16,
            "valid":len(valid),"statuses":dict(Counter(x["status"] for x in r["rows"])),
            "concordant_with_reference":sum(x["status"]=="AI_CONCORDANT_WITH_REFERENCE" for x in cells),
            "unresolved":sum(x["status"]=="UNRESOLVED" for x in cells),"cells":cells,
            "qualified_agent_action_gold":0,"independent_human_adjudication":False,"holdout_accessed":False,
            "original_report_sha256":digest(original.read_bytes())}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--replay",type=Path,required=True)
    p.add_argument("--original",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args();x=audit(a.replay,a.original)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(x,indent=2)+"\n")
    print(json.dumps(x))
if __name__=="__main__":main()
