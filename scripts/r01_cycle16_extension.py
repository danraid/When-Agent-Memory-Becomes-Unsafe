"""Public development extension. No reference label or real permission enters a model prompt."""
from scripts.r01_governance_source_replay import load,prompt_payload
from scripts.r01_operational_environment import CONTRACT,run_episode,sha

NEW="fixtures/R01_R06_CYCLE16_"
def prepare():
    data=load(NEW+"INPUT.json")
    book=load(NEW+"CASEBOOK.json")
    assert data["split"]=="public_development_only"
    events={e["key"]:e for e in book["events"]}
    cases=[]
    for c in data["cases"]:
        p=prompt_payload(c,events,"")
        p.pop("contract")
        p["target_issue"]=c["target_issue"]
        p["requested_mock_action"]=c["requested_mock_action"]
        p["decision_contract"]=CONTRACT
        p["response_contract"]="Return exactly JSON keys decision,action,source_ids. APPROVE requires the exact requested_mock_action; REJECT or ABSTAIN require null. Cite only records from target_issue; other historical records are not admissible citations. Use [] when no relevant record exists. This is a mock action only."
        assert all(x["published_at"]<=p["cutoff"] for x in p["records"])
        cases.append(p)
    assert len(cases)==8 and len(events)==4
    return cases
def histories():
    return load("fixtures/R01_R06_GOVERNANCE_CASEBOOK_V1.json")["events"]+load(NEW+"CASEBOOK.json")["events"]
