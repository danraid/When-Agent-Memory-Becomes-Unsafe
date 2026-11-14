# WAMBU-001 | v3 comparator design after CIKM 2026 overlap
**Status:** DESIGN PROPOSAL ONLY. Supersedes proposed novelty interpretation, **not** the observed v2 feasibility pilot. Confirmation remains blocked. No author freeze has been recorded.

## Terminal state
A genuine, reproducible method comparison of temporal policy supersession exists, with independent agent decisions, baseline provenance, null-safe reporting, and an untouched future confirmation set. No scientific novelty is assumed in advance.

## Observed gap
The initial five-paper screen missed Zerhoudi et al., *The Compaction Cliff in Long-Running AI Agent Memory*, ACM CIKM 2026, DOI 10.1145/3799682.3840567. Its published Knowledge Triage already tests exact constraint retention over repeated compaction, deterministic operators, and downstream safety. Our generic "preserve constraints under compaction" hypothesis would be inadequate on novelty grounds. See `literature/HIGH_OVERLAP_PRIOR_ART_2026-11-14.md`.

## Independent prior-art baseline
- Upstream implementation: https://github.com/searchsim-org/cikm26-knowledge-triage
- Inspected immutable upstream main revision: `a6ceb01a3368cee25ef7ebcf05ebdab8c9be24a4` (read-only source; verify license and dependencies before use).
- Relevant upstream modules: `knowledge_triage/operators.py` (`type_compact`/`type_retrieve`), `knowledge_triage/kb.py`, `knowledge_triage/classifier.py`, and `scripts/kt_compact.py`.
- Upstream code includes a deliberate `COMPACTION_UNSAFE` state when pinned constraints and procedures exceed budget. Never silently substitute a success result or drop the safety rule. Classifier misclassification must be separately measured.
- A faithful paper reproduction requires the upstream classifier, selected operator(s), model and budget and exact commit plus licence provenance. If run settings cannot be matched, call it **an adapted Knowledge Triage baseline**, not an exact replication. A home-built keyed policy ledger must never be labelled a Knowledge Triage reproduction.

## Proposed *new* scientific question
When **authorised policies change or revoke earlier restrictions**, which architecture minimises both (a) failure to enforce the newly active restriction and (b) wrongful persistence of a superseded rule after multiple context compactions? This measures *temporal policy correctness* and may offer a narrower contribution beyond static rule-preservation benchmarks. Novelty remains unverified until direct method overlap is examined.

## Distinct outcome channels
1. **Missed enforcement:** raw APPROVE when the *currently authorised* policy requires REJECT, after an update (safety failure).
2. **Stale-rule persistence:** raw REJECT when the current policy allows APPROVE but a previously superseded restriction would reject it (availability/correctness failure). Eligibility must ensure no other current rejection rule applies.
3. **Correct update adoption:** both new prohibitions and explicit revocations obeyed.
4. **Memory content fidelity:** literal constraint preservation, update and supersession versioning and a factual provenance indicator, assessed separately from actions.
5. **Derived policy guard interventions:** always reported independently of raw model skill.

## Candidate arms
- Full authorised history.
- Short recent context.
- GPT recursive summary only.
- GPT recursive summary plus external authoritative policy ledger.
- Upstream Knowledge Triage typed compaction and/or retrieval, with clearly documented source-commit adaptation.
- Optional matched-information and matched-token-budget arms, but any unequal-information contrasts remain explicitly described as system architecture comparisons.
- Derived guard on a reused raw ledger output, **not** a new LLM call.

## Required engineering before any confirmation
1. Design balanced causal revocation probes with authenticated supersession events, independent oracle checks, no old-rule/policy leakage into output labels, and future/holdout isolation.
2. Implement upstream comparator in its own namespace; preserve license and SOURCE_SHA256 and benchmark with the same policy update stream.
3. Audit source code and selected experimental protocol sections of CIKM 2026 and ACON, not merely their abstract. Record differences and testable hypotheses without declaring first-of-kind novelty.
4. Collect only a new development/pilot split, with episodes as independent clusters, stable prompts/IDs, and cost and length measurements by arm.
5. Predefine primary estimand and multiplicity plan (one primary metric, preordered or adjusted secondary contrasts), credible variance/power assumptions, and all stop/failure policies.
6. Submit the scientific design and full-text audit for author review. Only then produce author-signed frozen protocol hashes and independently generated private seed. Never derive confirmation seed from public dev/pilot seeds.

## Boundaries
The already-running v2 pilot of eight 18-step episodes at GitHub Actions run 43624782133 is a methods and instrument feasibility check. Its data may not be retrospectively relabelled v3 confirmation, even if statistically encouraging. Negative/null results remain publishable as scientifically honest development findings. No automatic scientific approval or external submission is authorised.
