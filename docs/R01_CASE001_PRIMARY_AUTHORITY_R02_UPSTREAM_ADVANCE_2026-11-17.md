# WAMBU R01/R02 | Primary-source advancement and original-method preflight

**17 November 2026, development only.** These are observations from public source metadata and new reproducible checks. No AI-based editorial review creates independent human ground truth.

## R01: newly recovered contemporaneous authority, CPython #133080

The previously documented candidate for removing `Py_C_RECURSION_LIMIT` and `PyThreadState.c_recursion_remaining` **without a deprecation period** now has a concrete publicly archived authority trace:

1. [C API Working Group decision #59](https://github.com/capi-workgroup/decisions/issues/59) was opened 10 March 2025; it records a recommendation to seek permission, and its discussion says the working group itself could not waive PEP 387.
2. [Steering Council request #288](https://github.com/python/steering-council/issues/288) was created 23 April 2025 at 13:27:30 UTC with the exact named interfaces and request for exceptional removal in Python 3.14.
3. [Steering Council public comment](https://github.com/python/steering-council/issues/288#issuecomment-2828390956), authored 24 April 2025 at 17:46:12 UTC, explicitly accepted removal without a deprecation period. The source comment's creation and update timestamps were identical when checked. This precedes PR creation.
4. [CPython PR #133080](https://github.com/python/cpython/pull/133080) was created 28 April 2025 at 11:41:01 UTC and merged on 29 April 2025 at 10:56:21 UTC. Its text links to Steering Council issue #288. **Merge status is not the evidence of an authorisation**; the Steering Council statement is the historical approval evidence.
5. The [C API working-group follow-up comment](https://github.com/capi-workgroup/decisions/issues/59#issuecomment-2834971171) was created 28 April 2025 at 11:41:40 UTC, **39 seconds after PR creation**, so it MUST NOT appear in any information available to a hypothetical agent at PR-creation time.

[Machine-readable claim and source URLs](../evidence/r01_case_001_public_authority_trace_2026-11-17.json) distinguish the pre-decision source from later corroboration. [Public GitHub replay](../scripts/r01_replay_case001_authority.py) fetches the exact PR, approval comment, acknowledgement and issue from primary GitHub REST endpoints; checks identity, quoted statement and chronology; records hashes of each received response; explicitly refuses operational policy-action gold. [Negative regression tests](../tests/test_r01_live_source_replay.py) reject an edited or future-dated approval.

### Scientific interpretation

**New qualified claim:** an identifiable Steering Council source publicly supported a specific exception **before PR #133080 was created**. The full chronology is a genuine improvement to event-time evidence, without post-PR leakage.

**Not yet qualified:** whether a deployed memory-compacting agent, receiving the approved event stream and an explicit request, would make the correct action; source scope beyond these two interfaces; independent case adjudication; or a comparative memory-safety result. `qualified_action_gold` remains null, and this case cannot enter an accuracy denominator. No change to the 5 documentary / 3 rejected-pairing distinction.

## R01: other named source leads

- [CPython #140344](https://github.com/python/cpython/issues/140344) describes either removing deprecated `ast` classes or adding runtime warnings if removal is premature; [PR #140345](https://github.com/python/cpython/pull/140345) implements the warning route. This is a lead for a *warning versus removal* action instrument, not independently established policy correctness.
- [CPython #133644](https://github.com/python/cpython/issues/133644) is a removal tracker, including [PR #133654](https://github.com/python/cpython/pull/133654). The PR text distinguishes `Py_UTF8Mode` and `Py_InteractiveFlag` as deprecated but not clearly designated for removal. This documents an exception/scope ambiguity, not a validated reject label.
- [CPython #130697](https://github.com/python/cpython/pull/130697) presents itself as a draft for discussion with the C API working group, with a proposed shortest nonexceptional PEP 387 timetable. A draft is not a final source of granted authorisation.
- [CPython #112639](https://github.com/python/cpython/pull/112639) was open for a prolonged period and closed without merge. Closure is not evidence that the proposed deprecation violated policy.

These additional leads must be version-frozen to their relevant event times before inclusion in agent prompts; current PR bodies may be retrospective edits.

## R02: upstream original Knowledge Triage preflight

An independent CI task now checks out the unmodified original repository at `a6ceb01a3368cee25ef7ebcf05ebdab8c9be24a4` and runs the existing original-source [fidelity preflight](../scripts/p08_full_original_knowledge_triage_preflight.py), alongside the live R01 replay. The job intentionally has empty provider credential variables and **cannot** run paid original embedding or LLM calls.

Required model identity in the original method still includes `octen-embedding-8b` and `gpt-5.4-mini`. The preflight is a method/source check, not runtime verification or end-to-end original-method replication. Original SafetyMargin execution, paper datasets/budgets, native embedding relevance and matched downstream action comparisons remain outside the verified component evidence.

**Correct status:** R02 remains `PARTIAL_COMPONENTS_ONLY`; without original service identity and whole-method evidence, call the current comparator **adapted**, not official end-to-end Knowledge Triage replication.

## Verification boundary

Workflow [R01 primary authority / R02 upstream preflight](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/workflows/r01-r02-primary-evidence.yml) archives a standalone manifest. Its actual run conclusion and artifact hashes must be checked before claiming its execution succeeded. The existing no-holdout source-bound workflow and new tests are separate gates.

Author final approval, confirmatory access, protocol freeze and journal submission remain unauthorised under [issue #50](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/issues/50).
