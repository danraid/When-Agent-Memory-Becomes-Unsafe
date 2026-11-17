"""Original upstream Knowledge Triage cascade logic with deterministic service stubs.

No network, model inference, fabricated empirical finding, or holdout. The
upstream predict() method is used without modification. Stubbed encoder and
LLM never qualify as published end-to-end framework replication.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

PIN="a6ceb01a3368cee25ef7ebcf05ebdab8c9be24a4"

class EncoderStub:
    def __init__(self, kind, enum):
        self.kind=kind
        self.enum=enum
        self.calls=0
    def predict(self,text):
        self.calls+=1
        K=self.enum
        if self.kind=="high":
            return K.BELIEF,{t:(0.8 if t==K.BELIEF else 0.05) for t in K}
        if self.kind=="middle":
            return K.BELIEF,{t:(0.48 if t==K.BELIEF else 0.13) for t in K}
        if self.kind=="low":
            return K.BELIEF,{t:(0.24 if t==K.BELIEF else 0.19) for t in K}
        raise ValueError("UNKNOWN_ENCODER_STUB")

class LLMStub:
    def __init__(self,text):
        self.response_text=text
        self.calls=0
    def complete(self,*args,**kwargs):
        self.calls+=1
        return type("Result",(),{"text":self.response_text})()

def run(upstream:Path):
    upstream=upstream.resolve()
    head=subprocess.run(["git","-C",str(upstream),"rev-parse","HEAD"],
                        text=True,capture_output=True,check=True).stdout.strip()
    if head!=PIN:
        raise ValueError("UNPINNED_UPSTREAM")
    p=upstream/"knowledge_triage"/"classifier_cascade.py"
    digest=hashlib.sha256(p.read_bytes()).hexdigest()
    sys.path.insert(0,str(upstream))
    from knowledge_triage.classifier_cascade import CascadeClassifier
    from knowledge_triage.classifier import KnowledgeType as K
    outcomes={}
    # A high-precision regex hit must short-circuit all remote stages.
    enc=EncoderStub("high",K); llm=LLMStub("CONSTRAINT")
    c=CascadeClassifier(encoder=enc,llm_client=llm).predict("Never commit secrets to version control.")
    assert c.decided_by=="regex" and c.type==K.CONSTRAINT and enc.calls==llm.calls==0
    outcomes["regex_short_circuit"]={"type":c.type.value,"decided_by":c.decided_by}
    enc=EncoderStub("high",K);llm=LLMStub("CONSTRAINT")
    c=CascadeClassifier(encoder=enc,llm_client=llm).predict("The database stores some records.")
    assert c.decided_by=="encoder" and c.type==K.BELIEF and enc.calls==1 and llm.calls==0
    outcomes["encoder_confident"]={"type":c.type.value,"decided_by":c.decided_by}
    enc=EncoderStub("middle",K);llm=LLMStub("CONSTRAINT")
    c=CascadeClassifier(encoder=enc,llm_client=llm).predict("Account data was recently updated.")
    assert c.decided_by=="llm" and c.type==K.CONSTRAINT and enc.calls==llm.calls==1
    outcomes["llm_adjudicator_stub"]={"type":c.type.value,"decided_by":c.decided_by}
    enc=EncoderStub("low",K);llm=LLMStub("UNKNOWN_OUTPUT")
    c=CascadeClassifier(encoder=enc,llm_client=llm).predict("A particular status was recorded.")
    assert c.decided_by=="abstain_as_hard" and c.type==K.CONSTRAINT and c.abstained and llm.calls==1
    outcomes["abstain_as_hard"]={"type":c.type.value,"decided_by":c.decided_by}
    enc=EncoderStub("middle",K)
    c=CascadeClassifier(encoder=enc,llm_client=None,use_llm=False).predict("Account data was recently updated.")
    assert c.decided_by=="encoder" and c.type==K.BELIEF and enc.calls==1
    outcomes["disabled_llm_fallback"]={"type":c.type.value,"decided_by":c.decided_by}
    return {"schema":"WAMBU-R02-ORIGINAL-CASCADE-STUBBED-LOGIC-V1",
            "classification":"UPSTREAM_EXECUTABLE_LOGIC_WITH_DETERMINISTIC_STUBS_NOT_ORIGINAL_RUNTIME",
            "upstream_sha":head,"classifier_cascade_sha256":digest,
            "branch_count":len(outcomes),"outcomes":outcomes,
            "original_encoder_runtime_executed":False,
            "original_llm_runtime_executed":False,
            "full_knowledge_triage_reproduction":False,
            "actual_paid_model_calls":0,"confirmatory_touched":False,
            "external_submission_authorised":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--upstream",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    r=run(a.upstream)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"branches":r["branch_count"],"original_provider_calls":r["actual_paid_model_calls"]}))
if __name__=="__main__":main()
