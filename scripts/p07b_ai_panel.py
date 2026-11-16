"""Three mutually blind AI scientific reviewers for real-source P07b probes.

AI-generated reviews are NOT human adjudication, peer review, or independent
professional certification. Reference labels are never passed to reviewers.
Uses provider-visible original sourced excerpts only. No automatic paid retries.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re

from study.openrouter_comparison import OpenRouter, BenchmarkError, digest, save

ROLE_MODELS = {
    "source_provenance": "openai/gpt-4.1-mini",
    "temporal_semantics": "google/gemini-2.5-flash",
    "adversarial_methods": "anthropic/claude-haiku-4.5",
}
LABELS = {"supported", "not_supported", "insufficient_evidence"}
ROLE_TEXT = {
    "source_provenance": "Check whether the original quoted span and pinned source and target identities support the literal explicit supersession link. Do not infer authenticity or downstream policy authority.",
    "temporal_semantics": "Separate the document link at the pinned revision from effective dates, applicability to requests, timing, issuer ranks, and organisational policy. Do not infer missing temporal authority.",
    "adversarial_methods": "Actively look for unsupported inferences, ambiguous target references, contradicted identity, poor evidence and false confidence. Favour insufficient_evidence if the evidence does not determine the literal requested link.",
}

def parse_vote(raw: str, excerpt: str) -> dict:
    # Accept only strict JSON, an allowed answer, an explicit evidence quote,
    # and defensible, limited claims. Do not auto-correct malformed outputs.
    try:
        obj = json.loads(raw)
    except (TypeError, ValueError) as exc:
        raise ValueError("INVALID_REVIEW_JSON") from None
    required = {"decision", "quoted_evidence", "reason", "confidence", "authority_semantics_resolved"}
    if not isinstance(obj, dict) or set(obj) != required:
        raise ValueError("INVALID_REVIEW_SCHEMA")
    if obj["decision"] not in LABELS or type(obj["confidence"]) not in (int, float) or not 0 <= obj["confidence"] <= 1:
        raise ValueError("INVALID_REVIEW_LABEL_OR_CONFIDENCE")
    quote = obj["quoted_evidence"]
    if not isinstance(quote, str) or not quote.strip() or quote not in excerpt:
        raise ValueError("EVIDENCE_QUOTE_NOT_IN_SOURCE_EXCERPT")
    if obj["authority_semantics_resolved"] is not False:
        raise ValueError("FABRICATED_OPERATIONAL_AUTHORITY_RESOLUTION")
    if not isinstance(obj["reason"], str) or not 12 <= len(obj["reason"]) <= 1300:
        raise ValueError("INVALID_REASON_LENGTH")
    return obj


def prompt(role: str, case: dict) -> str:
    if role not in ROLE_TEXT:
        raise ValueError("UNKNOWN_REVIEW_ROLE")
    safe = {
        "question": case["question"],
        "source_document": case["source_document"],
        "target_document": case["target_document"],
        "source_evidence": case["source_evidence"],
        "target_identity": case["target_identity"],
    }
    return ("This is an AI-only, simulated scientific document review. "
            "You are not a human or professional human adjudicator. "
            "Work entirely independently, without seeing other model opinions, "
            "evaluator-side answers, or hidden annotation metadata.\n"
            "ROLE: " + role + ". " + ROLE_TEXT[role] + "\n"
            "The task asks ONLY for the documented relationship at the pinned "
            "source revision. Do NOT decide an operational approve/reject action. "
            "Never infer a source hierarchy or effective time from a metadata reference.\n"
            "SOURCE MATERIAL:\n" + json.dumps(safe, sort_keys=True, ensure_ascii=False) +
            "\nReturn strictly one JSON object with exactly these keys: "
            "decision (supported | not_supported | insufficient_evidence), "
            "quoted_evidence (an exact nonempty substring of source_evidence.quoted_line), "
            "reason (12-1300 characters), confidence (0 to 1), "
            "authority_semantics_resolved (false, always).\n")


def run(cases_path: Path, output: Path, key: str, transport=None):
    if not key:
        raise ValueError("OPENROUTER_SECRET_MISSING")
    cases_raw = cases_path.read_bytes()
    cases = json.loads(cases_raw)
    if (cases.get("schema") != "P07B-PUBLIC-SOURCE-SUPERSESSION-CASES-V1" or
            cases.get("split") != "public_development_source_review_only" or
            len(cases.get("cases", [])) != 12):
        raise ValueError("INVALID_SOURCE_CASEBOOK_OR_SPLIT")
    if output.exists() and any(output.iterdir()):
        raise ValueError("NONEMPTY_OUTPUT_REJECTED")
    output.mkdir(parents=True, exist_ok=True)
    provenance = {
        "classification": "THREE_BLIND_AI_ROLES_SIMULATED_NOT_HUMAN_INDEPENDENCE",
        "models": ROLE_MODELS, "source_cases_sha256": digest(cases_raw),
        "source_manifest_sha256": cases["source_manifest_sha256"],
        "expected_calls": 12 * len(ROLE_MODELS), "maximum_calls": 42,
        "human_adjudicators": 0, "independent_professional_review": False,
        "genuine_naturalistic_action_labels": 0, "holdout_touched": False,
        "author_approval": False, "science_approval": False,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "git_sha": os.getenv("GITHUB_SHA"),
    }
    save(output / "run_metadata.json", provenance)
    client = OpenRouter(key, output / "provider_ledger.json", 42, transport)
    votes = []
    seen_response_ids = set()
    for case in cases["cases"]:
        for role, model in ROLE_MODELS.items():
            text_prompt = prompt(role, case)
            row = {
                "case_id": case["case_id"], "role": role, "model": model,
                "prompt_sha256": digest(text_prompt.encode()), "vote": None,
                "error": None, "classification": "AI_SIMULATED_REVIEW_ONLY",
            }
            try:
                r = client.call(model, text_prompt, max_tokens=400)
                if r["response_id"] in seen_response_ids:
                    raise ValueError("DUPLICATE_PROVIDER_RESPONSE_ID")
                seen_response_ids.add(r["response_id"])
                row["response"] = {
                    k: v for k, v in r.items() if k != "text"
                }
                row["raw_model_output"] = r["text"]
                row["vote"] = parse_vote(r["text"], case["source_evidence"]["quoted_line"])
            except (BenchmarkError, ValueError) as exc:
                row["error"] = str(exc)[:130]
            votes.append(row)
            save(output / "votes.json", votes)
            print(case["case_id"], role,
                  "VALID" if row["vote"] is not None else "FAILED",
                  flush=True)
    by_case = defaultdict(list)
    for row in votes:
        by_case[row["case_id"]].append(row)
    case_results = []
    for case in cases["cases"]:
        group = by_case[case["case_id"]]
        valid = [r["vote"]["decision"] for r in group if r["vote"]]
        agreement = len(valid) == len(ROLE_MODELS) and len(set(valid)) == 1
        case_results.append({
            "case_id": case["case_id"],
            "valid_votes": len(valid),
            "unanimous_ai_vote": valid[0] if agreement else None,
            "status": "AI_AGREEMENT_DESCRIPTIVE_NOT_HUMAN_GOLD" if agreement
                      else "AI_DISAGREEMENT_OR_PROVIDER_FAILURE",
            "role_decisions": {r["role"]: r["vote"]["decision"] if r["vote"] else None for r in group},
        })
    summary = {
        "classification": provenance["classification"],
        "status": "AI_REVIEW_FINISHED_DESCRIPTIVE_ONLY" if all(r["vote"] for r in votes)
                  else "AI_REVIEW_INCOMPLETE_ERRORS_RETAINED",
        "expected_votes": len(cases["cases"]) * len(ROLE_MODELS),
        "parsed_valid_votes": sum(r["vote"] is not None for r in votes),
        "unanimous_ai_cases": sum(c["unanimous_ai_vote"] is not None for c in case_results),
        "case_results": case_results,
        "model_errors": dict(sorted(Counter(r["error"] for r in votes if r["error"]).items())),
        "human_adjudicators": 0,
        "true_independent_human_labels": 0,
        "qualified_realworld_operational_cases": 0,
        "fully_original_knowledge_triage_baseline": False,
        "scientifically_approved": False,
        "holdout_touched": False,
    }
    save(output/"summary.json", summary)
    save(output/"manifest.json", {
        "files_sha256": {p.name: digest(p.read_bytes())
                         for p in output.glob("*.json") if p.name != "manifest.json"},
        "classification": provenance["classification"],
        "scientifically_approved": False,
        "holdout_touched": False,
    })
    return summary


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--cases", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--execute", action="store_true")
    a = p.parse_args()
    if not a.execute:
        p.error("Paid API execution requires --execute")
    key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENROUTER")
    result = run(a.cases, a.out, key or "")
    print(json.dumps({k: result[k] for k in ("status", "expected_votes",
                                             "parsed_valid_votes", "unanimous_ai_cases",
                                             "human_adjudicators")}))
    return 0 if result["status"] == "AI_REVIEW_FINISHED_DESCRIPTIVE_ONLY" else 3


if __name__ == "__main__":
    raise SystemExit(main())
