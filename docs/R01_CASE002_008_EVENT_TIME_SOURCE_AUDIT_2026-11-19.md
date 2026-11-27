# R01 | Event-time source admissibility: CPython cases 002 and 008

**Date:** 19 November 2026. **Status:** documentary evidence improvement only, **not** independent operational ground truth.

## Case P07D-CODE-002 (CPython PR #140345)

- [Original issue #140344](https://github.com/python/cpython/issues/140344) was created **2025-10-20 00:42:50 UTC**.
- [PR #140345](https://github.com/python/cpython/pull/140345) was created **2025-10-20 00:54:39 UTC**.
- [Reviewer comment](https://github.com/python/cpython/issues/140344#issuecomment-3420516752) advocating following PEP 387 and issuing runtime deprecation warnings was created **2025-10-20 04:37:26 UTC**.
- [Author follow-up](https://github.com/python/cpython/issues/140344#issuecomment-3422089335) acknowledging the warning-first approach was created **2025-10-20 13:33:56 UTC**.

**Timing implication:** the last two comments could not be visible at PR creation. They may be used only for a subsequent decision whose cutoff is explicitly after the respective comment timestamps. The current issue body was later updated and must not be treated as an immutable copy of the text visible 11 minutes after issue creation.

The comments are real upstream reviewer/author statements, but do not establish a universally valid agent action label, an entire policy state, or researcher-independent adjudication.

## Case P07D-CODE-008 (CPython PR #133654)

- [Original issue #133644](https://github.com/python/cpython/issues/133644) was created **2025-05-08 07:27:31 UTC**.
- [PR #133654](https://github.com/python/cpython/pull/133654) was created **2025-05-08 10:14:55 UTC**.
- A [comment](https://github.com/python/cpython/issues/133644#issuecomment-2862215994) about a separate libmpdecimal removal was created at **08:31:45 UTC** and updated at **08:55:01 UTC** on 8 May, both before the PR. It should not be reused as direct policy authority for unrelated global variables.
- Later comments in July 2025 and February 2026 discuss deferrals and soft deprecation. These cannot retroactively determine May 2025 policy obligations.
- PR author text distinguishes two deprecated global variables that were *not explicitly scheduled for removal* in the relevant documentation; this is a substantive exception/scope conflict requiring historical PEP 387 and official documentation snapshots.

**Timing implication:** publicly available related discussions are not by themselves proof that the named APIs could correctly be removed. PR closure without merge in October 2026 is not action correctness gold.

## Auditable output

[Structured sources and event times](../evidence/R01_CASE002_008_PREDECISION_COMMENT_TIMELINE_2026-11-19.json) and [negative/pre-decision chronology tests](../tests/test_r01_predecision_comment_timeline.py) are now checked in GitHub CI. Model-visible sources must exclude all comments with timestamps after the case decision point. At any new decision point the investigator must verify the governing PEP revision, effective policy, actor authorisation and exception scope from source-pinned links.

**R01 scientific status:** still `BLOCKED` for an independently source-verified real-agent action gold set. No human adjudication was carried out, and no simulation may be reported as a human judgement. Final author review, protected confirmatory data and external submission remain unauthorised.
