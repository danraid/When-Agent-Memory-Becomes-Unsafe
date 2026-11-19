# R01 | Real operational-source qualification and evidence-sufficiency pilot

**19 November 2026. Status: one narrowly scoped authority grant verified; real-world operational action gold still zero.** Source classification is documentary development evidence, not independent peer review.

## Primary-source findings

The earlier eight-case CPython/Rust matrix yielded five directly related CPython documentary candidates and three inapplicable or temporally invalid Rust policy pairings. This work expanded immutable predecision source identity for the five CPython candidates. Structured matrix: [R01_OPERATIONAL_AUTHORITY_5_CASES_2026-11-19.json](../evidence/R01_OPERATIONAL_AUTHORITY_5_CASES_2026-11-19.json).

| Candidate | Supported narrower observation | Missing for action gold |
|---|---|---|
| Python/cpython [#133080](https://github.com/python/cpython/pull/133080) | [Steering Council issue #288](https://github.com/python/steering-council/issues/288) explicitly requests an exception for `Py_C_RECURSION_LIMIT` and `PyThreadState.c_recursion_remaining`; [Steering Council comment](https://github.com/python/steering-council/issues/288#issuecomment-2828390956) agrees to this exact removal without deprecation on 2025-04-24 at 17:46:12 UTC, before PR creation on 2025-04-28 at 11:41:01 UTC. The first PR commit `4e1690b30317d24247d31c8866d9633d2da39e97` precedes creation. This **proves the particular exception grant**, not a blanket exemption for any API | Source-specific code correctness, downstream compatibility and independent operational action adjudication |
| Python/cpython [#140345](https://github.com/python/cpython/pull/140345) | Historic [PEP 387](https://github.com/python/peps/blob/fdd514309718092256484670a8191f8e747ce3b2/peps/pep-0387.rst) precedes creation. Reviewer and author comments in issue #140344 were written **after** PR opening; first listed PR commit was also after opening | Precise event-time patch and formal decision criteria |
| Python/cpython [#130697](https://github.com/python/cpython/pull/130697) | Historic PEP available and first commit predates opening; proposal explicitly a *discussion draft* on C API | Change-specific adoption/approval and allowable action |
| Python/cpython [#112639](https://github.com/python/cpython/pull/112639) | Historic PEP 387 source `bf0b381704265f2d013255744a92671895287332` precedes PR; the later PR closure is not normative evidence | Specific rule adoption, effective dates and independently valid decision |
| Python/cpython [#133654](https://github.com/python/cpython/pull/133654) | Historical PEP available; current PR record expressly excludes two globals, `Py_UTF8Mode` and `Py_InteractiveFlag`, due uncertain removal status | Initial-time immutability of edited PR text, exception scope and validated operational action |

## Actual bounded development execution

[Source-defined task fixture](../fixtures/R01_REAL_DOCUMENTARY_TEMPORAL_CHALLENGE_V1.json) comprises twelve documentary questions. Only two have positive *within-casebook* explicit Steering Council grant references. The other ten require reporting that a grant is **not established by the supplied records**, not that it does not exist globally.

- [Real 12-call workflow #44556331337](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/44556331337): PASS; [artifact #14545447018](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/44556331337/artifacts/14545447018), SHA-256 `eb91150aa297d09f4388bdcdc999938097eb6b6c9bd91701a41a84cc695e0e4e`.
- [Independent zero-inference replay #44556730396](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/44556730396): PASS; [artifact #14544828443](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/44556730396/artifacts/14544828443), SHA-256 `e4d5c892b9877235cfc5539d5d8dc3b763ebab064e34cd88a83d84546690a27a`.
- **12/12** model documentary statuses matched source-defined reference, **12/12** provided valid source IDs, **0** unsupported positive exception grants. All questions and source hashes were independently reconstructed with zero additional model calls.
- **Trivial conservative baseline: 10/12 = 83.3%** merely answering `not_established` on all questions. Thus the pilot is a valid bounded evidence-processing execution, but **not discriminative** enough for a scientific model comparison.
- Source snippets are concise *researcher-constructed summaries* of public primary sources, not verbatim certified historical issue-body snapshots. The predecision PEP/SC decision identities are independently preserved elsewhere. No model performance on actual live code actions or broader casebook correctness is inferred.

## Next instrument prepared

The more demanding [retrospective provenance-under-compaction protocol](../protocol/R01_RETROSPECTIVE_PROVENANCE_MEMORY_STRESS_V1.json) uses a common 246-word public source digest, two bounded memory representations (structured 138 words and an LLM-generated summary capped at 220), and the same twelve time-and-scope queries with citation validity checks. Unlike an authentic event-time replay, it intentionally includes later information and asks retrospective *as-of* questions; this is explicitly a memory/provenance engineering diagnostic, not a naturalistic action task. The original public data source is identical at intake, but model computation and memory representations are not matched.

**Scientific admission gate remains CLOSED:** no independent correct operational action gold, no authentic blind human adjudication, no confirmatory holdout, no causal memory-safety effect, and no author approval or journal submission. An AI specialist panel may support source qualification, but must never be misrepresented as independent human review.
