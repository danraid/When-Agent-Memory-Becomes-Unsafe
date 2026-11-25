"""Detached evaluation, no credentials or provider calls."""
import argparse,json
from collections import Counter
from decimal import Decimal
from pathlib import Path
from scripts.r01_cycle20_adjudication import frame,payload,validate,MODELS,SOURCE_SHA
from scripts.r01_governance_adjudication import digest,encode
from scripts.r01_cycle16_extension import NEW
from scripts.r01_governance_source_replay import load
def audit(source,original):
    cases={x["task_id"]:x for x in frame(source)}
    refs={x["id"]:x["label"] for x in load(NEW+"LABELS.json")["labels"]}
    assert set(cases)==set(refs)
    r=json.loads(original.read_text())
    assert r["assigned"]==16 and len(r["rows"])==16 and r["holdout_accessed"] is False
    assert r["source_replay_sha256"]==SOURCE_SHA and r["packet_sha256"]==digest(encode(list(cases.values())))
    assert {(x["model"],x["task_id"]) for x in r["rows"]}=={(m,q) for m in MODELS for q in cases}
    ids=set();valid={}
    for x in r["rows"]:
        m,q=x["model"],x["task_id"]
        assert x["request_sha256"]==digest(encode(payload(m,cases[q])))
        if x.get("receipt_id"):
            assert x["receipt_id"] not in ids;ids.add(x["receipt_id"])
        if x["status"]!="VALID_AI_ADJUDICATION":continue
        assert x["receipt_id"] and x["provider_model"]==m and x["finish_reason"]=="stop" and 0<=Decimal(str(x["usage"]["cost"]))<=Decimal("0.02")
        v,w=validate(x["answer"],cases[q]);assert v==x["adjudication"] and w==x["exact_envelope"];valid[m,q]=v
    cells=[]
    for q in cases:
        votes=[valid.get((m,q)) for m in MODELS]
        concordant=all(v and v["decision"]==refs[q] and v["mapping_status"]=="MATCHES_REQUEST" for v in votes)
        cells.append({"task_id":q,"provisional_reference":refs[q],"votes":votes,"status":"AI_CONCORDANT_SOURCE_SCOPE_AND_MAPPING" if concordant else "UNRESOLVED"})
    return {"classification":"DETACHED_DEVELOPMENT_APPRAISAL_NOT_OPERATIONAL_GOLD","assigned":16,"attempts":r["attempts"],"valid":len(valid),
      "statuses":dict(Counter(x["status"] for x in r["rows"])),"concordant_cases":sum(c["status"]=="AI_CONCORDANT_SOURCE_SCOPE_AND_MAPPING" for c in cells),
      "unresolved_cases":[c["task_id"] for c in cells if c["status"]=="UNRESOLVED"],"cells":cells,
      "original_report_sha256":digest(original.read_bytes()),"qualified_operational_gold":0,"holdout_accessed":False}
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--source",type=Path,required=True);p.add_argument("--original",type=Path,required=True);p.add_argument("--out",type=Path,required=True);a=p.parse_args()
    r=audit(a.source,a.original);a.out.write_text(json.dumps(r,indent=2)+"\n");print(json.dumps({k:v for k,v in r.items() if k!="cells"}))
