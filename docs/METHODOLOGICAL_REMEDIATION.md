# WAMBU-001 | Bounded post-pilot validity remediation

**Objective:** Remove discovered validity defects from the v1 instrument and execute an independently seeded *development/pilot* test without touching confirmation. Do not promote the historical v1 pilot to confirmation.

## Observed evidence

The v1 GPT pilot (run 43618151905, attempt 2) successfully executed 104 real provider calls and an evidence package. The reviewer highlighted deterministic lexicographic sampling, paired cases masquerading as independent review observations and privileged policy display. Inspection of source additionally found a step-modulo-six mode schedule and guard intervention using reference_policy, which is shared with the hidden scoring oracle.

## Selected engineering changes

- **No reference-policy guard leak:** `tasks.ledger_from_authorised_events()` reconstructs rules from public authorised events only. The ledger-pinned agent and rule-based guard use this independent state, while the evaluator alone reads `reference_policy`. Negative tests tamper with the hidden reference state and verify unchanged model prompts and guard policy action.
- **Randomised but balanced tasks:** shuffle six request modes each block, preserving target coverage with no easy t mod 6 answer cue. Fix the experimental RNG seed and source digest for reproducibility; publish generator code and public pilot seeds.
- **Less biased advisory case selection:** sample depth-stratified paired cases with SHA256 ranking across all conditions. Inputs exclude oracle actions and final correctness. Two low-cost LLM opinions remain advisory, not peer review.
- **Episode-level statistics:** `study.inference` refuses unpaired, incomplete or insufficiently eligible episode results. No per-turn pseudoreplication. The proposed 32-episode, 18-step confirmation uses a fixed two-sided paired sign-flip test and paired episode bootstrap, subject to author freeze.
- **Information access confound retained and labeled:** the primary contrast is a *systems intervention* (explicit policy persistence). A ledger deliberately provides stronger policy persistence than summary-only. It cannot claim a model-only causal effect or equal-information comparison. Full-history and truncated-window conditions are diagnostic context baselines.
- **Evidence:** provider response IDs, hash manifests, source hashes, compaction depth and derived guard outputs are logged. No API credentials, private holdout seeds or fabricated references are published.

## Current boundary

The v2 changes require deterministic CI and a genuinely new **pilot split**, not reuse or relabel of the v1 development dataset. Author freeze, confirmatory secret seed, final scholarly claims and journal submission remain downstream gates. Any failure encountered in this milestone is an engineering fix unless it invalidates scientific assumptions; no artificial gate relaxation is permitted.
