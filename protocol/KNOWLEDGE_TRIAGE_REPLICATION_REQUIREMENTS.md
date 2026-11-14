# WAMBU-001 | Source-pinned Knowledge Triage full-framework replication requirements

**Status: SPECIFICATION ONLY; FULL REPRODUCTION NOT IMPLEMENTED OR CLAIMED.** This document distinguishes the observed original TypeCompact component audit from a defensible end-to-end comparator.

## Original source

- Zerhoudi, Mitrovic and Granitzer, *The Compaction Cliff in Long-Running AI Agent Memory* (CIKM 2026), [DOI 10.1145/3799682.3840567](https://doi.org/10.1145/3799682.3840567).
- [Author released repository](https://github.com/searchsim-org/cikm26-knowledge-triage); inspected upstream revision `a6ceb01a3368cee25ef7ebcf05ebdab8c9be24a4`. Before further execution record the exact available licence and dependencies of the released revision.
- Existing [original component diagnostic](../literature/UPSTREAM_TYPECOMPACT_COMPONENT_RESULT_2026-11-14.md), including native classifier **0/400 constraints**, matched-budget `COMPACTION_UNSAFE` accounting, and **source-annotated** lane separately reported.

## Mandatory distinction

- **Original upstream native classifier + TypeCompact component:** already used in a bounded offline diagnostic. This is NOT entire framework reproduction.
- **Source-annotated TypeCompact:** changes type input relative to native classifier. Label `SOURCE_ANNOTATED_ORIGINAL_OPERATOR_NOT_NATIVE_CLASSIFIER`.
- **Article-specific `typed_retention_adapted`:** locally authored TypeCompact-inspired archive. Label `ADAPTED_NOT_OFFICIAL_REPRODUCTION`.
- **Full Knowledge Triage:** requires upstream implemented classifier/cascade, operators, verifier/unsafe fallbacks, retrieval/decomposition paths where relevant and original parameter definitions, with source SHA, environment, model and token-budget traceability. Not yet executed.

## Acceptance contract before honest baseline claim

1. Pin source SHA and release/license, lock dependency versions and obtain unaltered upstream operator source hashes.
2. Explicitly identify which *published* experiments, datasets, budgets, seeds, model interfaces, classifier mode and metrics are being replicated. Record deviations from original paper separately.
3. Run native upstream classification first; persist each original type assignment without post-hoc rewriting. Never call source-annotated data the native classifier.
4. Preserve explicit `COMPACTION_UNSAFE` and failures as outcomes, not success or excluded cases. Infeasible budgets may invalidate a matched comparison and must be reported.
5. Supply matched-information and matched-token-budget comparisons, or call all unequal-information contrasts **systems-level** only. Precompute no hidden reference labels in a model-visible policy ledger.
6. Exercise downstream model decisions only under a valid, independently checked source-policy representation. Record provider IDs, tokens, inference prompts and full retrospective evidence hashes.
7. Test order sensitivity, source authenticity, update revisions, revocations and scope conflicts, without silently changing official algorithms. Any new adapter, schema mapping or annotation must have an explicit name.
8. Obtain human method-level review and compare against prior papers including Supersede (2026). An 'official' label is allowed only after verifiable implementation fidelity, not based on similar output behaviour.

## Strict non-promotion rules

No current evidence proves full-framework replication, novel contributions, generalisation or superiority of the policy ledger. Technical integration and bounded GitHub Actions successes cannot authorise confirmatory access. GPT reviewer advisories are not peer review. A failed/unsafe upstream case cannot be removed without a predeclared exclusion rule.

**Exit for P08:** immutable upstream code, original-method coverage manifest, transparent differences, comparator integration, matched information/budget stress tests, independent provenance audit and reference-backed report. Until then **P08 NOT COMPLETE**.
