"""Verify current unchanged decision comments and event-time pinned membership, no provider calls."""
import argparse,csv,io,json
from pathlib import Path
from scripts.r01_governance_source_replay import api,pinned_file,sha,load
from scripts.r01_cycle16_extension import NEW,prepare
def verify():
    evidence=[]
    for e in load(NEW+"CASEBOOK.json")["events"]:
        prefix="repos/python/steering-council/issues/"
        a=api(prefix+"comments/"+str(e["comment"]))
        b=next(x for x in api(prefix+str(e["issue"])+"/comments?per_page=100") if x["id"]==e["comment"])
        assert a["body"]==b["body"]==e["observed_body"]
        assert a["created_at"]==a["updated_at"]==b["created_at"]==b["updated_at"]==e["at"]
        assert a["user"]["login"]==b["user"]["login"]==e["handle"]
        pep,pblob=pinned_file("python/peps",e["pep"],"peps/pep-0013.rst")
        roster,rblob=pinned_file("python/devguide",e["roster"],"core-team/core-team.csv")
        for repo,ref in (("python/peps",e["pep"]),("python/devguide",e["roster"])):
            assert api(f"repos/{repo}/commits/{ref}")["commit"]["committer"]["date"]<e["at"]
        assert "* "+e["name"] in pep.split("Current steering council",1)[1].split("Specification",1)[0]
        assert any(row[:2]==[e["name"],e["handle"]] for row in csv.reader(io.StringIO(roster)))
        evidence.append({"event":e["key"],"comment_sha256":sha(a["body"]),"pep_blob":pblob,"roster_blob":rblob,"authority_verified":True})
    return {"status":"PUBLIC_SOURCE_REPLAY_PASS_ONLY","events":evidence,"questions":len(prepare()),"qualified_operational_gold":0,"holdout_accessed":False}
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--output",type=Path,required=True);a=p.parse_args()
    r=verify();a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(r,indent=2)+"\n");print(json.dumps(r))
