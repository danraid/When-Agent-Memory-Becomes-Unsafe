# Blinded human adjudication protocol for AI-generated development cases

**Status: 16 synthetic development cases authored; 0 independent human assessments received.** The cases are synthetic, but they can be independently evaluated by genuine people. This does not create naturalistic external validity.

## Review procedure

Recruit at least two real reviewers with documented expertise in policy interpretation, temporal rules, information security or AI-agent evaluation. Reviewers must be separate from the AI case generator and blinded to model predictions, synthetic heuristic results, and each other's initial responses. Each reviewer records a real identity or verified confidential pseudonym, expertise, conflicts, date, exact casebook commit SHA, decision (approve/reject/abstain), cited event IDs, and a justification. Do not invent a reviewer or claim independence because two AI role names differ.

For each case, reviewers should assess (a) whether the event chronology is coherent, (b) whether the authority hierarchy and scope are sufficient, (c) whether a unique decision follows, and (d) whether the case is suitable for scoring. They may mark `invalid` or `ambiguous` instead of forcing a label. Disagreements must be reconciled by a third genuine independent reviewer or reported as unresolved. The AI-generated scenario labels must not be treated as pre-established gold.

## Review data schema

A reviewer file is a JSON object with `schema: "WAMBU-HUMAN-REVIEW-V1"`, `casebook_commit_sha`, `reviewer_id`, `identity_verified_by`, `expertise`, `conflicts_declared`, `blinded_to_model_outputs: true`, `not_case_generator: true`, and `decisions`. Each decision contains `case_id`, `action` (approve/reject/abstain), `case_validity` (valid/ambiguous/invalid), `reason`, `evidence_event_ids`, and `reviewed_at`. For invalid or ambiguous cases, a specific explanation is required.

Keep reviewer files outside the public model-visible casebook and retain authenticated source evidence. A schema-complete file alone cannot verify that its author is human.

## Limitations and release rules

- Some of the 16 scenarios intentionally expose authority, effective-date, scope or timeline ambiguities. They are not guaranteed to admit a unique gold label.
- No human adjudication has yet occurred. No reviewer identities or decisions are supplied.
- The current casebook is **development-only**, and its synthetic provenance remains explicit.
- Report agreement only after two authentic reviews exist and are verified. Do not count fabricated or AI-generated labels as human data.
- Do not use these cases to claim a naturalistic benchmark, a prospective holdout, or independent replication of a GPT model comparison.
- Keep the existing protected confirmatory split untouched.
