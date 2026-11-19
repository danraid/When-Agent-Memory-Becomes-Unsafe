"""Fail-closed offline contract for author-requested major revisions (#50).

This gate checks scientific claim *boundaries* and provenance bookkeeping.
Passing is NOT scientific acceptance or proof that major revisions are complete.
"""
from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "editorial/MAJOR_REVISION_EVIDENCE_STATUS_2026-11-17.json"
ALLOWED = {"OPEN", "PARTIAL", "BLOCKED", "COMPLETE"}
EXPECTED = {f"R{i:02d}" for i in range(1, 9)}


def verify(root: pathlib.Path = ROOT) -> dict:
    path = root / MANIFEST.relative_to(ROOT)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return {"passed": False, "checks": {"readable_manifest": False}, "error": str(exc)}
    decisions = (
        "author_final_approval",
        "confirmatory_protocol_freeze_authorised",
        "confirmatory_holdout_access_authorised",
        "external_submission_authorised",
    )
    panel = data.get("ai_panel", {})
    revisions = data.get("revisions", {})
    source = str(data.get("source_commit", ""))
    checks = {
        "schema_and_decision": data.get("schema") == "WAMBU-MAJOR-REVISION-EVIDENCE-V1"
            and data.get("author_decision") == "MAJOR_REVISIONS_REQUESTED",
        "approval_locks": all(data.get(k) is False for k in decisions),
        "exploratory_only": data.get("scientific_scope") == "EXPLORATORY_ONLY",
        "source_pinned": len(source) == 40
            and all(c in "0123456789abcdef" for c in source),
        "panel_counts_exact": panel.get("case_count") == 8
            and panel.get("first_round") == 24
            and panel.get("strict_valid") == 22
            and panel.get("valid_syntheses") == 6
            and panel.get("human_adjudications") == 0
            and panel.get("full_knowledge_triage_reproduced") is False,
        "all_revision_items": set(revisions) == EXPECTED,
        "status_vocabulary": all(isinstance(x, dict)
            and x.get("state") in ALLOWED for x in revisions.values()),
        "evidence_resolves": all(isinstance(x.get("evidence"), str)
            and ".." not in pathlib.PurePosixPath(x["evidence"]).parts
            and (root / x["evidence"]).is_file() for x in revisions.values()),
        "reasons_nonempty": all(isinstance(x.get("reason"), str)
            and len(x["reason"].strip()) >= 20 for x in revisions.values()),
        "no_unearned_completion": not any(x.get("state") == "COMPLETE"
            for x in revisions.values()),
    }
    return {"schema": data.get("schema"), "passed": all(checks.values()),
            "checks": checks, "scientific_approval": False,
            "external_submission": False, "holdout_access": False}


if __name__ == "__main__":
    report = verify()
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if report["passed"] else 1)
