"""Metadata-only replay of 16 public development candidate sources; never promotes eligibility."""
import argparse,json,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def replay(frame,fetch):
    assert len(frame["rows"])==16 and len({x["source_comment_id"] for x in frame["rows"]})==16
    result=[]
    for row in frame["rows"]:
        u=f"https://api.github.com/repos/{row['repository']}/issues/comments/{row['source_comment_id']}"
        try:
            x=fetch(u)
            # No raw comment body copied or sent to a model.
            exact=x["id"]==row["source_comment_id"] and x["html_url"]==row["source_url"] and x["created_at"]==row["observed_publication_timestamp"]
            result.append({"id":row["id"],"source_identity_matches":exact,"created_at":x["created_at"],"updated_at":x["updated_at"],"edited":x["updated_at"]!=x["created_at"],"eligible":False})
        except Exception as exc:
            result.append({"id":row["id"],"source_identity_matches":False,"error_type":type(exc).__name__,"eligible":False})
    return {"classification":"SOURCE_METADATA_REPLAY_NOT_QUALIFICATION","screened":16,"matching":sum(x["source_identity_matches"] for x in result),"eligible":0,"rows":result,"holdout_accessed":False}
def fetch(url):
    import os
    req=urllib.request.Request(url,headers={"User-Agent":"Public source metadata audit","Accept":"application/vnd.github+json","Authorization":"Bearer "+os.environ["GH_TOKEN"]})
    with urllib.request.urlopen(req,timeout=20) as r:return json.load(r)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",type=Path,required=True);a=p.parse_args()
    frame=json.loads((ROOT/"fixtures/PRESSURE_CYCLE34_SCREENED_CANDIDATES.json").read_text())
    r=replay(frame,fetch);a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(r,indent=2)+"\n");print(json.dumps({k:v for k,v in r.items() if k!="rows"}))
