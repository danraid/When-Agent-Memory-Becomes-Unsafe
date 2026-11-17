"""Strict, zero-call detached audit of the distinct P07f v2 source-ID run."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from study.openrouter_comparison import digest,save
import scripts.p07f_detached_ai_review_audit as old
from scripts.p07f_v2_evidence_id_panel import role_prompt_v2,parse_role_v2

def audit(root:Path):
    old.role_prompt=role_prompt_v2
    old.parse_role=parse_role_v2
    meta=json.loads((root/"metadata.json").read_text())
    if (meta["schema"]!="WAMBU-P07F-V2-ORIGINAL-AI-ROLE-REVIEWS" or
        meta["previous_v1_run_id"]!=44076185311 or
        meta["previous_v1_4_of_24_valid_preserved_not_repaired"] is not True or
        meta["evidence_id_contract"]!="DETERMINISTIC_EXACT_VERBATIM_SOURCE_LOOKUP"):
        raise ValueError("MISMATCHED_V2_PREDECLARED_EVIDENCE_CONTRACT")
    result=old.audit(root)
    result.update({
        "schema":"WAMBU-P07F-V2-DETACHED-AI-ONLY-AUDIT",
        "version":"2.0.0",
        "original_v1_run_44076185311_kept_immutable":True,
        "model_quote_was_generated":False,
        "quote_is_deterministic_exact_evidence_lookup":True,
        "author_approval":"PENDING",
        "scientifically_approved":False,
    })
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--review-dir",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    result=audit(a.review_dir)
    if a.out.exists() and any(a.out.iterdir()):
        raise ValueError("NEVER_OVERWRITE_V2_AUDIT")
    a.out.mkdir(parents=True,exist_ok=True)
    save(a.out/"audit.json",result)
    save(a.out/"manifest.json",{
        "audit_sha256":digest((a.out/"audit.json").read_bytes()),
        "original_v1_preserved":True,"paid_calls":0,
        "author_approval":"PENDING","human_ground_truth":0})
    print(json.dumps({k:result[k] for k in (
        "version","first_round_expected","first_round_strict_valid",
        "first_round_invalid","synthesis_valid","author_approval")},indent=2))

if __name__=="__main__":
    main()
