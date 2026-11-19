# R01 / R06 | Pre-decision PEP 387 revisions verified for CPython cases 002 and 008

**19 November 2026. Status: historically available policy source verified; no qualified action correctness gold.**

The source selection is based on GitHub's exact-file commit history constrained to the corresponding PR creation times, not on a current mutable PEP or issue body:

| Case | PR creation (UTC) | Latest preceding PEP 387 commit | Commit date (UTC) | Git blob |
|---|---|---|---|---|
| P07D-CODE-008 / CPython #133654 | 2025-05-08 10:14:55 | [65029b3](https://github.com/python/peps/blob/65029b3f1f4e656a54395a9b04e8cfa06a569240/peps/pep-0387.rst) | 2025-02-24 14:51:08 | `e5132ba0f9afb7c8527b7d2678a720e40b5db37d` |
| P07D-CODE-002 / CPython #140345 | 2025-10-20 00:54:39 | [fdd5143](https://github.com/python/peps/blob/fdd514309718092256484670a8191f8e747ce3b2/peps/pep-0387.rst) | 2025-09-10 02:08:01 | `07a0fcb7ee5cd5af1218c4885fa4558bf8564240` |

Both snapshots specify a warning-oriented backwards-compatibility process: normally add runtime or C API compiler warnings, allow at least two Python minor versions (with a five-year preference), consult the Steering Council for warning-impossible situations and recognise possible exceptions. A soft deprecation does **not** itself schedule removal.

The 2025-10-20 reviewer's recommendation to add warnings for the AST classes was issued *after* the initial PR was opened. It therefore belongs to a later decision, not the original opening-time task. For the 2025-05-08 C API variables, the 2026 follow-up or outcome also cannot retroactively define an earlier approved action.

Evidence file: [immutable predecision policy source metadata](../evidence/R01_PEP387_PREDECISION_IMMUTABLE_V1.json). Tests: [source chronology regression](../tests/test_r01_pep387_snapshot.py).

**Open scientific requirement:** event-time feature-specific warning and exception records, actual delegated authority and a source-grounded independent action assessor. A PEP rule's existence proves neither its particular applicability nor the correct action in a disputed PR. Zero qualified action-gold labels, zero confirmatory or submission permissions.
