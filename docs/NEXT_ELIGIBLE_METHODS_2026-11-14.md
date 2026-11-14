# WAMBU-001 | Next eligible methodology: offline source fidelity and authority provenance

**State:** PARTIAL IMPLEMENTATION; DEVELOPMENT ONLY (2026-11-14). No confirmatory data, new GPT call, human-review conclusion, protocol freeze or submission.

## Bounded objective

Before considering a new paid pilot, establish source-accurate Knowledge Triage operator behaviour and design a prospectively adjudicable corpus of multi-authority updates. Scientific success is **not** implied by CI passing.

## Completed verifiable offline work

- The original Knowledge Triage checkout is pinned to commit `a6ceb01a3368cee25ef7ebcf05ebdab8c9be24a4`; the [operator script](../scripts/verify_knowledge_triage_operators.py) imports **unmodified** official `classifier.py`, `kb.py`, `operators.py` and probes TypeCompact, TypeDecompose, TypeRetrieve with compact source-labelled fixtures.
- The script returns machine-readable evidence of `COMPACTION_UNSAFE`, a successful sufficient-budget pinned case, per-partition constraint locality, possible post-replication budget overflow and `k < in-scope constraint count` retrieval truncation. This characterises source behaviour without attributing shortcomings to any published end-to-end paper experiment.
- [Offline CI](../.github/workflows/knowledge-triage-method-ci.yml) verifies the exact source commit and performs bounded unit and component checks. No OpenAI key or paid model step is available in this workflow.
- [Constructed authority cases](../authority_v4/naturalistic_style.py) consist of four **fictional realistic-style** document chains: authorised revocation against lower-trust operator note; new high-authority enforcement; delayed receipt of retroactive revocation; same-rank simultaneous contradictory directives. [Tests](../tests/test_authority_naturalistic_style.py) check gold reference logic and exclude privileged event/expected-action fields from model-visible cases. These are **not actual naturalistic empirical observations**.

## Scientific distinction: comparator ladder

1. **Original TypeCompact component** with official source and regex classifier: executed and re-audited, see [report](../literature/UPSTREAM_TYPECOMPACT_COMPONENT_RESULT_2026-11-14.md). It classified 0/400 authorised synthetic event presentations as constraints. Label injection in an alternative lane is not native classification.
2. **Pinned three-operator source integration:** bounded offline integration verification and known corner cases, but source-labelled fixture access is explicitly privileged; this is not original-classifier validity or a reproduced paper.
3. **Complete Knowledge Triage reference:** **NOT DONE.** Requires the authors' actual classification cascade and SafetyMargin path where applicable, original treatment of abstention/overflow, TypeDecompose/TypeRetrieve in a downstream task, source/data version and budget parity, run-level evidence, and separate empirical downstream agent decisions. It must be called faithful reproduction only when the actual published conditions have been implemented and checked.
4. **Original WAMBU adapted typed retention and proposed temporal ledger:** these remain **separate treatments**; do not rename `typed_retention_adapted` or infer original-method efficacy from WAMBU v3 synthetic performance.

## Genuine naturalistic source collection still required

For each real-world multi-authority case, record: public source URL and immutable retrieval hash; issuer and authority provenance; effective timestamp versus observed timestamp; action and revocation target; actor/category scope; original/redacted text with licence/consent review; missing/conflicting evidence; source-selection exclusions; independent adjudicators' blind labels and disagreement resolution. Freeze development inclusion/exclusion and outcome definition **before** drawing a statistically powered confirmatory sample. Exclude private/personal information, policy interpretations beyond the source and leaked gold labels from model prompts.

Do not fabricate public-source URLs or call hand-written scenarios observed real cases. The four fixtures above solely exercise mechanics. Genuine naturalistic cases cannot be declared complete until provenance has been independently checked and any personal information is handled appropriately.

## Exit gate and prohibitions

**This bounded offline engineering step:** pinned upstream modules checked; original source not modified; overflow and truncation behaviour transparently recorded; realistic constructed fixtures and label-isolation tested; CI actually passed. Only then mark **OFFLINE_METHOD_FIXTURES_PASS**.

**Still blocked:** external-source naturalistic corpus, complete reference framework fidelity, independent blinded scientific review, specificity of falsifiable protocol, power estimation and novelty assessment, locked confirmatory protocol and holdout use. The four-episode v3 pilot remains historical development data only. Neither pilot nor synthetic fixtures count as independent confirmation. No scientific submission is claimed.
