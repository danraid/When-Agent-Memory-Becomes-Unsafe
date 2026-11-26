"""Fail-closed preparation of independent public-development review requests.
No provider calls: dispatch adapter must be separately qualified.
"""
import json
import re
import hashlib

GATES = ("rights_verified", "authority_verified", "independence_verified", "immutable_version_verified")
FIELDS = {"opaque_id", "source_reference", "authorized_factual_representation", "authority_evidence", "cutoff", "question_mapping"}
SCOPE = FIELDS - {"question_mapping"}
def prepare(record, models, phase):
    if phase not in ("scope", "mapping"):
        raise ValueError("unknown phase")
    if len(models) != 2 or len({m["family"] for m in models}) != 2:
        raise ValueError("two distinct model families required")
    if record.get("split") != "public_development" or not all(record.get(k) is True for k in GATES):
        return []
    packet = record["packet"]
    allowed = SCOPE if phase == "scope" else FIELDS
    if set(packet) != allowed:
        raise ValueError("unexpected or absent packet fields")
    if not re.fullmatch(r"[a-f0-9]{32}",packet["opaque_id"]):
        raise ValueError("opaque identifier required")
    payload = json.dumps(packet, sort_keys=True, separators=(",",":"))
    digest = hashlib.sha256(payload.encode()).hexdigest()
    return [{"phase":phase,"model":m["model"],"family":m["family"],"packet_sha256":digest,
             "packet":json.loads(payload),"fresh_context_required":True,"dispatched":False}
            for m in models]

def self_test():
    models=[{"model":"synthetic-A","family":"A"},{"model":"synthetic-B","family":"B"}]
    rec={"split":"public_development",**dict.fromkeys(GATES,True),"packet":
         {"opaque_id":"a"*32,"source_reference":"synthetic","authorized_factual_representation":"synthetic",
          "authority_evidence":"synthetic","cutoff":"synthetic"}}
    assert len(prepare(rec,models,"scope"))==2
    for gate in GATES:
        assert prepare({**rec,gate:False},models,"scope")==[]
    assert prepare({**rec,"split":"holdout"},models,"scope")==[]
    try: prepare({**rec,"packet":{**rec["packet"],"gold_action":"x"}},models,"scope")
    except ValueError: pass
    else: raise AssertionError("unexpected field accepted")
    try: prepare(rec,[models[0],models[0]],"scope")
    except ValueError: pass
    else: raise AssertionError("same family accepted")
    print("synthetic preflight passed; no dispatch")

if __name__=="__main__":
    self_test()
