# WAMBU-001 | P07d real code-change sources and simulated AI expert reviews: audited completion record

**Date:** 16 November 2026. **Milestone classification:** `REAL_CODE_SOURCE_INTAKE_COMPLETE; AI_EXPERT_ROLE_PANEL_PARTIAL; OFFLINE_AUDIT_COMPLETE; SCIENTIFIC_REFERENCE_UNVALIDATED`.

## Executed evidence, not a proposed result

- [Source/workflow PR #39](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/pull/39), merged source commit `01e77f95408e18cba4cb305e1999bb7048a1de32`.
- [Original GitHub Actions #43977945404](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/43977945404) **FAILED overall** because the paid AI review job finished with seven invalid reviewer outputs. Offline contract CI, real external source harvesting and read-only detached source/reviewer audit **SUCCEEDED**.
- [Original full source evidence #14281751027](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/43977945404/artifacts/14281751027): eight real public changed-code PR metadata records, authentic diff patches, pre-closure dated review/comment events, pinned original PEP/RFC source full texts, and separately preserved factual merged-versus-unmerged outcomes. Access to model-visible inputs was separated into [blind artifact #14281720887](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/43977945404/artifacts/14281720887).
- [Original AI responses #14280804945](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/43977945404/artifacts/14280804945): exactly **24** distinct provider response IDs and 24 pre-request reservations. All 24 raw outputs are preserved, including seven original parse/evidence failures.
- [Independent zero-call source/response audit #14282955695](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/43977945404/artifacts/14282955695): **SUCCESS**, seven original evidence file hashes and the paired prompt/model/response IDs validated; original merge outcomes reconstructed from GitHub PR JSON. No new paid calls or private holdout access.

## Corpus and historical facts

Eight original source-code modification PRs were selected prospectively for this bounded *development* pilot. Four were merged, four closed without merge. The latter are genuine *proposals containing actual code diff patches*, not modifications deployed in the mainline software.

| Case | Real code PR | Recorded historical disposition | Valid AI role outputs |
|---|---|---|---:|
| P07D-CODE-001 | [CPython #133080](https://github.com/python/cpython/pull/133080), C API recursion internals | merged | 2/3 |
| P07D-CODE-002 | [CPython #140345](https://github.com/python/cpython/pull/140345), AST deprecation warnings | merged | 2/3 |
| P07D-CODE-003 | [CPython #130697](https://github.com/python/cpython/pull/130697), Unicode object structs | closed without merge | 2/3 |
| P07D-CODE-004 | [CPython #112639](https://github.com/python/cpython/pull/112639), inspect API deprecation | closed without merge | 3/3 |
| P07D-CODE-005 | [Rust #87652](https://github.com/rust-lang/rust/pull/87652), naked functions never inlined | merged | 3/3 |
| P07D-CODE-006 | [Rust #161002](https://github.com/rust-lang/rust/pull/161002), reject cold custom functions | merged | 1/3 |
| P07D-CODE-007 | [Rust #159382](https://github.com/rust-lang/rust/pull/159382), naked EII diagnostics | closed without merge | 1/3 |
| P07D-CODE-008 | [CPython #133654](https://github.com/python/cpython/pull/133654), old global configurations | closed without merge | 3/3 |

The two external normative source snapshots were SHA-pinned: Python PEP 387 and Rust RFC 2972. They are not necessarily the *effective versions* at each historical decision time. Original GitHub API patches and PR bodies are **retrospective snapshots**, not a guaranteed `created_at`-time view; source authority, effective times and actual semantic correctness remain unverified.

## Three AI role simulations and strict results

Models were GPT-4.1 Mini (backward-compatibility reviewer), Gemini 2.5 Flash (time-and-authority reviewer) and Claude Haiku 4.5 (adversarial code reviewer). They were blind to historical dispositions and the other agents' votes. Each model inspected real source/code excerpts with a hard requirement to quote evidence verbatim and not assert verified normative applicability.

- **17/24** outputs passed predeclared JSON, evidence quote and no-fake-human-claim validators.
- **7/24** failed: **4** responses were not one complete allowed JSON document and **3** did not quote an exact substring of visible source material. They remain failed and are not repaired post hoc.
- Role completion: GPT-4.1 Mini **6/8** valid, Gemini 2.5 Flash **3/8** valid, Claude Haiku 4.5 **8/8** valid.
- **2/8** cases had unanimous, strict-valid AI role assessments: Rust #87652 yielded `plausible_compliance`; CPython #133654 yielded `potential_conflict`. These are model opinions, **not gold-standard expert classifications**.
- Six cases had incomplete or divergent AI assessments. Cases with three valid but split AI opinions are retained as disagreement rather than forced consensus.

No normative precision or recall is reportable: there are **zero** human-validated policy-correctness labels. The observed GitHub merge status does not define whether the change violated policy; even unanimous AI opinions cannot replace real qualified adjudication. Comparisons to the original Knowledge Triage's end-to-end performance are not supported by this stage.

## Exact pending scientific gates

**P07 naturalistic operational authorised-action reference remains PARTIAL** despite real code-change provenance. Real qualified, independently identified case authors and blinded human adjudicators must establish correct authority precedence, effective/observed time, request scope, licence, code correctness and disagreement resolution. If no human expert corpus exists, a clearly labelled negative/reproducibility paper can still use the current exploratory material but cannot claim naturalistic human validation.

**P08 faithful full Knowledge Triage remains PARTIAL/BLOCKED** on upstream embedding endpoint/model and full framework/corpus/budget equivalence. P09 matched-information/budget experiments and P10 external methods/novelty review are not completed. Preregistration remains unfrozen; private confirmatory samples and journal submission are untouched.

The publication road map is [REMAINING_MILESTONES_P07D_TO_PUBLICATION_2026-11-16.md](REMAINING_MILESTONES_P07D_TO_PUBLICATION_2026-11-16.md), which counts **10** still-open major milestones P07–P16. P07d is a substep, not a new major review gate.

**Technical exit decision:** P07d source intake **COMPLETE**; P07d original paid AI role-contract evaluation **PARTIAL**; detached evidence audit **COMPLETE**. The original workflow failure is retained. Scientific P07/P08 **NOT QUALIFIED**.
