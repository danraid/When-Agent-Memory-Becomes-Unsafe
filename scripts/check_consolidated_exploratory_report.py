"""Fail-closed editorial integrity gate for the consolidated WAMBU report.

This proves local provenance/linkage and non-promotion, NOT scientific validity,
human peer review, publisher formatting, or an actual journal submission.
Offline only: no provider requests, holdout reads, or author-identifying export.
"""
from __future__ import annotations
import json
import pathlib
import re
from hashlib import sha256

ROOT=pathlib.Path(__file__).resolve().parents[1]
MANUSCRIPT=ROOT/"manuscript/CONSOLIDATED_EXPLORATORY_REPORT_2026-11-16_EN_GB.md"
LEDGER=ROOT/"editorial/CONSOLIDATED_EXPLORATORY_CLAIM_LEDGER_2026-11-16.json"
MANDATORY=("## Abstract","## 1. Introduction","## 2. Research questions",
           "## 3. Methods","## 4. Results","## 5. Discussion",
           "## 6. Threats to validity","## 7. Ethics",
           "## 8. Conclusion","## References")
EVIDENCE_TOKENS={
    "V2-CEILING":("144/144","105/144"),
    "V3-TEMPORAL-CEILING":("72/72","52/72"),
    "OPENROUTER-V2-MIXED":("1,433/1,440","0.0000","−0.035714","not estimable"),
    "OPENROUTER-V1-PARTIAL":("714/720",),
    "LONGMEMEVAL-S-SIX":("72/72","LongMemEval-S"),
    "KT-UPSTREAM-ORIGINAL-COMPONENT":("327","19, 4, 1 and 0"),
    "P07B-LINKS-AI-ROLEPLAY":("36/36","12 constructed"),
    "P07C-PUBLIC-PR":("17/24","five public merges"),
    "P07D-REAL-CODE":("four merged","17/24"),
}
BLOCKED_FLAGS={
    "full_original_knowledge_triage_reproduced",
    "protected_holdout_touched",
    "preregistration_frozen_by_author",
    "confirmatory_study_executed",
    "independent_peer_reviewed",
    "final_author_manuscript_approved",
    "journal_submitted",
    "journal_accepted",
}
BANNED=["statistically significant improvement","confirmatory success",
        "fully replicated knowledge triage","independently human validated",
        "accepted at tmlr","author-approved final submission"]


def verify():
    text=MANUSCRIPT.read_text(encoding="utf-8")
    raw=LEDGER.read_bytes()
    ledger=json.loads(raw)
    assert ledger["classification"]=="EXPLORATORY_ONLY_NON_CONFIRMATORY"
    assert ledger["manuscript"]==str(MANUSCRIPT.relative_to(ROOT))
    flags=ledger["scientific_flags"]
    checks={
        "all_sections":all(s in text for s in MANDATORY),
        "no_author_identifying_urls_or_byline":
            not re.search(r"github\.com/danraid|Daniel Raaid|danielraid|@gmail",text,re.I),
        "non_promotion":all(flags[f] is False for f in BLOCKED_FLAGS)
            and flags["independent_human_policy_adjudications"]==0,
        "explicit_status": all(t in text for t in (
            "exploratory","non-confirmatory","zero independent human",
            "not policy correctness","not the complete","holdout")),
        "claims_have_source_paths":all(
            (ROOT/c["evidence"]).is_file() and
            ".." not in pathlib.PurePosixPath(c["evidence"]).parts
            for c in ledger["claims"]),
        "all_nine_evidence_families":set(EVIDENCE_TOKENS)=={
            c["id"] for c in ledger["claims"]},
        "claim_values_in_manuscript":all(
            all(x.lower() in text.lower() for x in EVIDENCE_TOKENS[c["id"]])
            for c in ledger["claims"]),
        "no_forbidden_phrases":all(x not in text.lower() for x in BANNED),
        "reference_records":len(ledger["external_primary_references"])>=4
            and all(r["locator"].startswith("https://")
                    for r in ledger["external_primary_references"]),
        "references_present":all(f"[{i}]" in text for i in range(1,6)),
        "not_claimed_tmlr_ready":"not an approved" in text.lower()
            or "not a registered report" in text.lower(),
        "no_private_seed":"holdout_seed" not in text
            and "OPENROUTER_API_KEY" not in text,
    }
    report={
        "schema":"WAMBU-CONSOLIDATED-EDITORIAL-OFFLINE-AUDIT-V1",
        "classification":"DOCUMENT_INTEGRITY_NOT_SCIENTIFIC_APPROVAL",
        "manuscript_sha256":sha256(MANUSCRIPT.read_bytes()).hexdigest(),
        "claim_ledger_sha256":sha256(raw).hexdigest(),
        "checks":checks,
        "passed":all(checks.values()),
        "scientifically_approved":False,
        "independently_peer_reviewed":False,
        "human_case_gold_qualified":False,
        "confirmatory_touched":False,
        "journal_submission":False,
    }
    return report


def main():
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=pathlib.Path)
    args=p.parse_args()
    r=verify()
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n",
                            encoding="utf-8")
    print(json.dumps({"passed":r["passed"],"checks":r["checks"]},indent=2))
    return 0 if r["passed"] else 1


if __name__=="__main__":
    raise SystemExit(main())
