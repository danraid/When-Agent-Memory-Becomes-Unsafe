"""Reconstruct bounded public authority evidence, never run an agent or access holdout."""
import csv
import hashlib
import io
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parents[1]
def load(path):
    return json.loads((ROOT/path).read_text())
def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
def api(path):
    headers={"Accept":"application/vnd.github+json","User-Agent":"wambu-r01-public-source-replay"}
    if os.getenv("GH_TOKEN"):
        headers["Authorization"]="Bearer "+os.environ["GH_TOKEN"]
    with urlopen(Request("https://api.github.com/"+path,headers=headers),timeout=30) as f:
        return json.load(f)
def pinned_file(repo,ref,path):
    import base64
    x=api(f"repos/{repo}/contents/{path}?ref={ref}")
    return base64.b64decode(x["content"]).decode("utf-8"),x["sha"]
def prompt_payload(case, events, contract):
    e=events[case["event"]]
    visible=[]
    if e["at"]<=case["cutoff"]:
        visible.append({"source_id":e["key"],"published_at":e["at"],"text":e["observed_body"]})
    return {"task_id":case["id"],"cutoff":case["cutoff"],"question":case["question"],"contract":contract,"records":visible}
def run():
    p=load("fixtures/R01_R06_GOVERNANCE_CASEBOOK_V1.json")
    inputs=load("fixtures/R01_R06_GOVERNANCE_INPUT_V1.json")
    labels=load("fixtures/R01_R06_GOVERNANCE_LABELS_V1.json")
    events={e["key"]:e for e in p["events"]}
    evidence=[]
    for e in events.values():
        prefix="repos/python/steering-council/issues/"
        a=api(prefix+"comments/"+str(e["comment"]))
        b=next(x for x in api(prefix+str(e["issue"])+"/comments?per_page=100") if x["id"]==e["comment"])
        assert a["body"]==b["body"]==e["observed_body"]
        assert a["created_at"]==a["updated_at"]==b["created_at"]==b["updated_at"]==e["at"]
        assert a["user"]["login"]==b["user"]["login"]==e["handle"]
        assert e["anchor"] in a["body"]
        pep,pep_blob=pinned_file("python/peps",e["pep"],"peps/pep-0013.rst")
        roster,roster_blob=pinned_file("python/devguide",e["roster"],"core-team/core-team.csv")
        for repo,ref in (("python/peps",e["pep"]),("python/devguide",e["roster"])):
            assert api(f"repos/{repo}/commits/{ref}")["commit"]["committer"]["date"]<e["at"]
        council=pep.split("Current steering council",1)[1].split("Specification",1)[0]
        assert "* "+e["name"] in council
        assert any(row[:2]==[e["name"],e["handle"]] for row in csv.reader(io.StringIO(roster)))
        evidence.append({"event":e["key"],"comment_sha256":sha(a["body"]),"pep_sha256":sha(pep),"pep_blob":pep_blob,"roster_sha256":sha(roster),"roster_blob":roster_blob,"independent_api_routes_agreed":True,"historical_membership_verified":True})
    payloads=[prompt_payload(c,events,inputs["contract"]) for c in inputs["cases"]]
    label_by_id={x["id"]:x["label"] for x in labels["labels"]}
    assert len(payloads)==len(label_by_id)==8 and len(events)==4
    assert all(set(x)=={"task_id","cutoff","question","contract","records"} for x in payloads)
    assert all(r["published_at"]<=x["cutoff"] for x in payloads for r in x["records"])
    counts={k:sum(v==k for v in label_by_id.values()) for k in ("APPROVE","REJECT","ABSTAIN")}
    report={"status":"SOURCE_AND_TEMPORAL_PREFLIGHT_PASS_ONLY","source_events":len(evidence),"provisional_development_questions":len(payloads),"label_distribution":counts,"majority_baseline":max(counts.values())/len(payloads),"future_record_exposures":0,"qualified_agent_action_gold":0,"independent_action_adjudication":False,"holdout_accessed":False,"provider_calls":0,"evidence":evidence}
    out=ROOT/"runs"/"r01-governance-cycle4"
    out.mkdir(parents=True,exist_ok=True)
    (out/"report.json").write_text(json.dumps(report,indent=2)+"\n")
    (out/"prompts.json").write_text(json.dumps(payloads,indent=2)+"\n")
    print(json.dumps(report))
if __name__=="__main__":
    run()
