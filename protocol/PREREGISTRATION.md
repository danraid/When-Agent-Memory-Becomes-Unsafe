# WAMBU-001 | Prospective preregistration proposal (UNFROZEN)

**Status:** DRAFT FOR AUTHOR REVIEW. This document is NOT a preregistration, not a confirmation approval, and not a licence to open a private holdout. Source files and analytic decisions are not frozen until a separately recorded author act.

## Prior development and revised study identity

The original two-episode live development test on 2026-11-14 (attempt 2 of GitHub Actions run 43618151905) produced 96 real decision calls, six compactions and two advisory reviews. Its outputs are historical engineering evidence only. That v1 test had non-random step-modulo-six case scheduling, a guard that consulted the evaluator's reference policy, lexicographically sampled reviewer cases, and privileged policy exposure in the ledger arm. These features are not allowed to be silently carried into v2 inferential claims. The fixed full-history and recent-window baselines remain deliberately unequal-information *systems* comparators; this must be reported.

The revised v2 instrument uses six randomly permuted scenario modes per block of six turns, every block containing three certain rejection cases, two certain valid cases and one variable case. Five genuine summary compactions occur before steps 3, 6, 9, 12, 15 in an 18-turn episode. The deployable ledger is reconstructed from public authenticated initial-policy and amendment events; evaluation labels remain detached. The guard runs only that independent authorised-event ledger and the current request. A guard result is a deterministic derivative of the pinned-ledger GPT answer, not a new independent LLM decision.

## Research question and estimand

For independent episode e, let r_e(c) be the proportion of raw GPT APPROVE outputs among all oracle-REJECT situations in steps after at least two completed recursive compactions, arm c. The sole proposed primary contrast is d_e = r_e(recursive_summary) - r_e(pinned_ledger). Proposed estimand D = E_episode[d_e] on independently generated synthetic trajectories in the declared design. A positive D indicates lower unsafe raw approvals under the full system with an externally managed current authorised-policy ledger; it does *not* isolate intrinsic memory capacity, since information access differs between conditions.

We will report raw outputs even when the guard later corrects them. The derived guard is secondary and cannot be considered an independent baseline. Observations from the same episode (all conditions and turns) are not independent samples. The fixed oracle trajectory eliminates action-feedback cascades, so deployment-like long-range error propagation is untested.

## Proposed prospective confirmation design (requires author freeze)

- One model/checkpoint identifier as specified in the version-pinned `study/model_config.json` with observed provider response provenance. Provider may silently update a hosted model, an external validity limitation.
- N = **32 independent episodes**, T = **18 turns** per episode, five recursive compactions. No post-hoc continuation or optional stopping. Public development and pilot seeds cannot generate confirmation.
- Fixed random mode permuting within blocks; each episode must have at least four oracle-reject opportunities after depth >= 2; any nonconforming or incomplete batch fails qualification.
- One primary endpoint and two-sided alpha = 0.05. Paired episode-level sign-flip randomisation (50,000 draws, fixed seed) for the two-sided p-value; exact enumeration for N <= 16. Report episode-bootstrap percentile 95% interval using 20,000 resamples, fixed seed. This method assumes exchangeability/symmetry of paired episode effects for the null test and cannot be claimed valid if diagnostics refute it. No secondary p-values will be called confirmatory.
- Power is **an ex ante sensitivity assumption**, not estimated from two pilot episodes: target absolute risk reduction 0.10, SD of paired episode risk differences 0.20, normal approximation gives N ~= 32 for about 80% nominal power. If true SD is 0.25, power is materially lower. No false claim of guaranteed power.
- Missing case, provider failure, unverifiable response ID, source or evidence digest mismatch, or independent evaluator discrepancy invalidates the entire run. Do not discard bad episodes and replace them with easier ones. Preserve previous failed attempts.
- Balance and token cost per condition, invalid output rate, false rejections, guard override rate and error by compaction depth are descriptive secondary endpoints. Report all planned arms even if results are null or negative.

## Eligibility gates

1. Review the v2 full methods, literature source audit, instrument tests and independent pilot.
2. Fill the design fields in `protocol/STUDY_PLAN.json` and create immutable content digests for protocol, study sources and model configuration. Generate a freeze proposal, not an approval.
3. The human author separately records `FROZEN_BY_AUTHOR`, the reviewed protocol hash, and confirmatory-run authorisation; a private >=32-character holdout seed must be provided as a GitHub Actions secret and kept out of the public repo.
4. Only a strictly gated, single-run confirmation may execute. Even a successful confirmatory computation does not grant external publication or scientific approval.

## Exclusions and non-generalisability

This is a synthetic, English-only, fixed-oracle, simulated approval/rejection workflow. The ledger receives current verified policy information that a windowed memory baseline may lose; performance differences should be interpreted as systems architecture trade-offs, not equal-information or universal claims. Related agent memory and compaction literature already covers adjacent problems; novelty is a bounded, not yet independently accepted, claim. No human peer review has occurred.
