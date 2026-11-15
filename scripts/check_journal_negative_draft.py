#!/usr/bin/env python3
"""Offline journal draft integrity check. Does not certify scientific validity."""
import json
import pathlib
import re
import sys

ROOT=pathlib.Path(__file__).resolve().parents[1]
PAPER=ROOT/"manuscript/JOURNAL_NEGATIVE_RESULTS_ANONYMOUS_DRAFT_EN_GB.md"
LEDGER=ROOT/"editorial/JOURNAL_CLAIM_LEDGER_2026-11-14.json"
AUDIT=ROOT/"docs/INDEXED_JOURNAL_SUBMISSION_AUDIT_2026-11-14.md"
def verify():
    article=PAPER.read_text(encoding="utf-8")
    ledger=json.loads(LEDGER.read_text(encoding="utf-8"))
    audit=AUDIT.read_text(encoding="utf-8")
    checks={
      "all_required_sections":all(s in article for s in ("## Abstract","## 1. Introduction","## 2. Research questions","## 3. Methods","## 4. Results","## 5. Discussion","## 6. Threats to validity","## 7. Reproducibility","## 8. Conclusion","## References")),
      "v2_counts":all(s in article for s in ("105 | 25 | 14","144 | 0 | 0","eight independent episodes")),
      "v3_counts":all(s in article for s in ("52 | 0 | 0","All 20 recent-window errors occurred in control tasks")),
      "original_source_counts":all(s in article for s in ("308 | 19 | 210","323 | 4 | 224","326 | 1 | 227","327 | 0 | 228")),
      "failed_workflow_disclosed":"original run's advisory-review failure" in article,
      "no_human_review_claim":"no human peer-review endorsement" in article.lower(),
      "non_equivalence":"not evidence that the methods are equivalent" in article,
      "holdout_untouched":"No confirmatory holdout was accessed" in article,
      "not_submission":"not an approved anonymous submission" in article,
      "anonymous_body_no_named_repository":not re.search(r"github.com/danraid|Daniel Raaid|When-Agent-Memory-Becomes-Unsafe/actions",article,re.I),
      "claim_ledger_references_exist":all((ROOT/c["evidence"]).is_file() for c in ledger["claims"]),
      "claim_ledger_not_confirmatory":all(not c.get("confirmatory",False) for c in ledger["claims"]),
      "human_gold_zero":ledger["independent_human_adjudications"]==0,
      "submission_false":ledger["journal_submission"] is False,
      "gate_documented":"NOT SUBMISSION READY" in audit,
    }
    print(json.dumps({"scope":"OFFLINE_EDITORIAL_CONSISTENCY_ONLY","scientific_approval":False,"journal_submission":False,"checks":checks},indent=2))
    return all(checks.values())
if __name__=="__main__":
    sys.exit(0 if verify() else 1)
