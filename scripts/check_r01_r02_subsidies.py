"""Offline source-evidence subsidy contract for R01 and original-method R02.

Checks case-specific acquisition requirements and method attestation requirements.
Cannot establish truth merely by a file saying it is verified.
"""
from __future__ import annotations
import argparse
import json
from hashlib import sha256
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
R01=ROOT/"protocol/R01_EVENT_TIME_EVIDENCE_ACQUISITION_V1.json"
R02=ROOT/"protocol/R02_ORIGINAL_KT_REPLICATION_EVIDENCE_V1.json"
REQUIRED_CASE_PROOF={
    "normative_commit_at_decision","normative_sha256_at_decision",
    "adoption_and_effective_time_proof_url","issuer_authority_evidence_url",
    "actor_authorisation_evidence_url","exception_evidence_url",
    "action_definition","decision_timestamp_utc","quote_with_line_numbers",
    "independent_source_verification",
}
REQUIRED_KT_IDS={f"KT{i:02d}" for i in range(1,9)}
VALID_GATES={"PARTIAL","BLOCKED","COMPLETE"}


def audit(root:Path=ROOT):
    r01_path=root/R01.relative_to(ROOT)
    r02_path=root/R02.relative_to(ROOT)
    r01=json.loads(r01_path.read_text(encoding="utf-8"))
    r02=json.loads(r02_path.read_text(encoding="utf-8"))
    cases=r01.get("cases",[])
    methods=r02.get("methods",[])
    case_ids=[x.get("case_id") for x in cases]
    checks={
      "r01_schema":r01.get("schema")=="WAMBU-R01-EVIDENCE-ACQUISITION-REGISTER-V1",
      "r02_schema":r02.get("schema")=="WAMBU-R02-REPLICATION-EVIDENCE-CONTRACT-V1",
      "exact_case_set":len(cases)==8 and set(case_ids)=={f"P07D-CODE-{i:03d}" for i in range(1,9)}
          and len(set(case_ids))==8,
      "case_proof_complete_as_template":all(set(x.get("source_capture",{}))==REQUIRED_CASE_PROOF for x in cases),
      "case_status_not_promoted":all(x.get("qualified_action") is None and
          x.get("scientific_classification")=="AWAITING_AUTHORITY_EVIDENCE" for x in cases),
      "source_urls":all(x.get("public_pr","").startswith("https://github.com/")
          and x.get("normative_document","").startswith("https://github.com/") for x in cases),
      "no_simulated_human_gold":r01.get("operational_gold_labels")==0
          and r01.get("expected_human_adjudications")==0
          and r01.get("confirmatory_eligible") is False,
      "exact_kt_method_set":len(methods)==8 and {x.get("id") for x in methods}==REQUIRED_KT_IDS,
      "method_evidence_requirements":all(x.get("gate") in VALID_GATES and
           x.get("evidence_required") and isinstance(x.get("evidence_required"),list) for x in methods),
      "original_model_names":r02.get("required_exact_model_identity",{}).get("encoder")=="octen-embedding-8b"
          and r02.get("required_exact_model_identity",{}).get("cascade_adjudicator")=="gpt-5.4-mini",
      "method_claims_remain_bounded":r02.get("original_full_framework_reproduced") is False
          and r02.get("model_substitution_equivalent") is False
          and r02.get("openrouter_key_alone_proves_original_services") is False
          and r02.get("observed_paid_calls_this_packet")==0,
      "no_approval_or_external_submit":all(
          r02.get("authorisation",{}).get(k) is False for k in
          ("confirmation","holdout","external_submission")),
      "reported_unsafe_is_failure":r02.get("reporting_contract",{}).get("mandatory_failure_status")=="COMPACTION_UNSAFE"
          and r02.get("reporting_contract",{}).get("never_treat_failed_or_unsafe_as_success") is True,
    }
    return {"schema":"WAMBU-R01-R02-SUBSIDY-VALIDATION-V1",
            "checks":checks,"passed":all(checks.values()),
            "r01_qualified_gold":0,"r02_full_original_reproduction":False,
            "source_manifest_sha256":{
              "r01":sha256(r01_path.read_bytes()).hexdigest(),
              "r02":sha256(r02_path.read_bytes()).hexdigest()},
            "scientific_author_approval":False,"confirmatory_touched":False,
            "external_submission":False}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path)
    args=parser.parse_args()
    report=audit()
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"passed":report["passed"],"checks":report["checks"]},indent=2))
    return 0 if report["passed"] else 1


if __name__=="__main__":
    raise SystemExit(main())
