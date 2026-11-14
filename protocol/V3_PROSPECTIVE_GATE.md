# WAMBU-001 v3 | Prospective analysis and scientific freeze gate

**Status:** UNFROZEN DESIGN CANDIDATE. A general instruction to continue the project is recorded as permission to perform engineering and exploratory work. It is **not** fabricated into a signed, content-specific author freeze of a protocol hash or a scientific endorsement of yet-unobserved findings.

## Proposed question

Following at least two recursive compaction steps, does a currently authoritative, version-aware policy ledger lower *wrongful rejections caused by revoking a once-active constraint* compared with an explicitly labelled adapted typed-retention comparator? A second co-primary study might target enforcement of newly introduced rules, but that would require a separate multiplicity plan. To avoid under-specified multiple testing, **only the stale-revocation error is a candidate primary endpoint**. Newly introduced enforcement is secondary.

## Unit and outcomes

- Unit of independence: policy episode, with 18 turns and four amendments per episode.
- Eligible primary decisions: those tagged `stale_rule_revocation` where the old rule rejects, the current rule approves and at least two compactions have occurred. The label is used only by the post-response evaluator.
- Episode-level risk is wrong (not-APPROVE) model actions / eligible revocation probes. Missing/invalid JSON is conservatively counted as failure.
- Candidate signed difference: `typed_retention_adapted` risk minus `temporal_policy_ledger` risk. Positive values favour the ledger, negative values favour the adapted typed comparator.
- Secondary: wrongful approvals on newly forbidden actions, prompt length, failure-after-pinning, paired effect vs recursive summary, and side effects of the derived guard on observed actions.
- Selection/exclusions: exclude no completed episode merely for zero errors; missing eligible probes are a validity failure and require redesign *before freezing*. Timeouts and provider errors must not be silently scored as successful actions.

## Sources of uncertainty and design changes still needed

- **Ceiling effect:** v2's central contrast is zero. A prospective two-sided variance/power justification cannot validly be fitted to its null, saturated pilot.
- **Comparator:** `typed_retention_adapted` preserves source-labelled policies verbatim, but is **not** the official Knowledge Triage implementation. Direct current-state-of-art claims require source-pinned faithful reproduction.
- **Ecological validity:** explicit formal amendments and oracle-fixed balance may be solved trivially. Add independently authored, naturalistic authority-conflict narratives, including partial revocations, ambiguous authorisation and exceptions.
- **Matched information:** the ledger grants direct current-policy access; results identify a system benefit, not superior intrinsic LLM memory. Additional matched-token and same-source ablations needed for mechanisms.
- **Multiplicity and power:** preregister family-wise hypothesis tests, cluster-level confidence interval method, attrition and bounded sample count **before** collecting holdout responses.
- **Scientific novelty:** prior art already addresses constraint retention (Zerhoudi et al. 2026) and temporal updates (Patel 2026). This application must be distinguished by genuine method or empirical insight, not only a new title.

## A finite conditional acceptance sequence

1. Offline tests detect gold leakage, post-hoc source edits and guard-label substitution; all pass.
2. A distinct four-episode v3 pilot makes genuine GPT calls with full output provenance and a faithful description of the adapted comparator; CI must pass.
3. Pilot analysis quantifies ceiling effects and independent episode variance; model reviewers remain advisory.
4. Source-method audit and critical manuscript review compare CIKM, Supersede, ACON, LongMemEval and relevant newer publications.
5. If the study remains scientifically discriminative, the author reviews **specific locked protocol/code/config hashes** and an independent private seed is established outside the public repo before a confirmatory run.
6. The registered confirmatory workflow executes **once** with finite calls, kept out of pilot tuning. Results, including null/negative findings, are interpreted under the frozen plan.
7. A genuine scientific review precedes any journal submission, with anonymised code and adherence to the target venue's policies.

The user has authorised the *process* to proceed; technical pre-approval never means a positive scientific result exists. No confirmatory or journal-submission claim is granted by this file.
