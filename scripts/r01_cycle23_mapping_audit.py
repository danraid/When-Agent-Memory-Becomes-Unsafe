import argparse,json
from pathlib import Path
from scripts.r01_cycle23_mapping import frame,payload,validate,MODELS,digest,encode
def audit(r):
    cases={c["task_id"]:c for c in frame(None)}
    assert r["assigned"]==22 and len(r["rows"])==22 and r["holdout_accessed"] is False
    assert {(x["model"],x["task_id"]) for x in r["rows"]}=={(m,q) for m in MODELS for q in cases}
    votes={};ids=set()
    for x in r["rows"]:
        m,q=x["model"],x["task_id"]
        assert x["request_sha256"]==digest(encode(payload(m,cases[q])))
        if x.get("receipt_id"):
            assert x["receipt_id"] not in ids;ids.add(x["receipt_id"])
        if x["status"]=="VALID_AI_ADJUDICATION":
            assert x["provider_model"]==m and x["finish_reason"]=="stop"
            v,w=validate(x["answer"],cases[q]);assert v==x["adjudication"];votes[m,q]=v["mapping_status"]
    controls={q:[votes.get((m,q)) for m in MODELS] for q in cases if q.startswith("C")}
    passed=all(v==["MISMATCH","MISMATCH"] for v in controls.values())
    return {"classification":"DEVELOPMENT_MAPPING_ONLY","valid":len(votes),"controls":controls,"controls_passed":passed,"candidate_votes":{q:[votes.get((m,q)) for m in MODELS] for q in cases if q.startswith("Q")},"qualified_operational_gold":0,"holdout_accessed":False}
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--original",type=Path,required=True);p.add_argument("--out",type=Path,required=True);a=p.parse_args();r=audit(json.loads(a.original.read_text()));a.out.write_text(json.dumps(r,indent=2)+"\n");print(json.dumps(r))
