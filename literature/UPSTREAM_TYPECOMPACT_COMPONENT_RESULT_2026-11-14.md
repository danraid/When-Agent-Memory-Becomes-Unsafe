# WAMBU-001 | Original Knowledge Triage TypeCompact component audit

**Observed:** [GitHub Actions run 43640829549](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/43640829549), status **success**, with [original evidence artifact](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/43640829549/artifacts/14132200634).

This audit executes the **unmodified** official `knowledge_triage.classifier`, `knowledge_triage.kb`, and `knowledge_triage.operators.type_compact` modules, pinned to upstream commit `a6ceb01a3368cee25ef7ebcf05ebdab8c9be24a4` of [searchsim-org/cikm26-knowledge-triage](https://github.com/searchsim-org/cikm26-knowledge-triage). The wrapper and v3 synthetic policy event stream are authored for this article. This is a **component-level test**, **not** a complete Knowledge Triage framework or paper replication, and no downstream GPT decision calls were made.

## Verified source classifier behaviour

The official regex classifier categorised **0 / 400** synthetic authorised-policy event presentations as type `constraint`. The event words in WAMBU do not match the author's native regex constraint patterns. At 512 estimated tokens, all 144 tested cases happened to retain all authorised event lines anyway because the token budget was generous. Retention under a generous budget does **not** prove that type-aware safety pinning worked.

## Pre-specified budget sensitivity (144 cases per budget)

| Budget (approx. tokens) | Original regex: all events retained | Explicit source annotation: all events retained | Source-annotation COMPACTION_UNSAFE |
| --- | ---: | ---: | ---: |
| 64 | 0/144 | 144/144 | 112 |
| 128 | 32/144 | 144/144 | 32 |
| 256 | 112/144 | 144/144 | 0 |
| 512 | 144/144 | 144/144 | 0 |

Two evaluation lanes were deliberately separated:
- **Original upstream regex classifier**, unchanged from the pinned source, followed by the unmodified upstream operator. Its `COMPACTION_UNSAFE` status was 0 in these fixtures because the policy events were not recognised as constraints.
- **Source-annotated lane**, with WAMBU's explicitly marked authorised-policy events mapped to `KnowledgeType.CONSTRAINT` before applying the otherwise unchanged upstream operator. This **changes the classifier input** and is **not** the authors' native classifier or an official end-to-end baseline. It retains the event lines even when the operator explicitly returns `COMPACTION_UNSAFE` (112/144 at 64 tokens). Therefore `retained` must not be interpreted as an admissible or safe compaction when the required token budget is exceeded.

## Scientific interpretation

This is a *diagnostic of classifier-domain mismatch and budget validity*, not evidence that the published framework fails or that the WAMBU ledger is superior. Any valid downstream comparison must carry the `COMPACTION_UNSAFE` state, account for classifier or source-annotation privilege and match token/information budgets. The current v3 real-model arm `typed_retention_adapted` is **not** this official native-regex component and must never be relabelled as its replication.

**Status:** PINNED_UPSTREAM_COMPONENT_TEST_PASS; FULL_FRAMEWORK_REPLICATION_NOT_STARTED; PAPER_NOVELTY_NOT_ESTABLISHED; PRIVATE_CONFIRMATORY_HOLDOUT_UNTOUCHED.


## Independent re-audit of original artifact, 14 November 2026

The complete [run 43640829549](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/43640829549) is **success**, whereas the scientific result is **component-only**. Downloaded original ZIP artifact 14132200634 (three JSON members) passes ZIP CRC with recomputed full-archive SHA-256 `0816841655b3987f2ae0a8ed51c572bd7f13dbe781a6f150bee3f6fe81156e12`, matching the recorded GitHub artifact digest.

The downloaded report contains 8 episodes × 18 steps = **144 cases** and 400 authorised event presentations. The official upstream regex matched **0/400** as constraints. At budgets 64, 128, 256 and 512 estimated tokens, all events were retained in the **native-regex** lane in respectively **0, 32, 112, 144 of 144** cases. When WAMBU supplied constraint labels from *outside the upstream classifier*, retention was **144/144 at every budget**, but the operator returned `COMPACTION_UNSAFE` in **112 cases** at budget 64 and **32 cases** at budget 128. Such results **do not satisfy** a maximum token budget. Treat `COMPACTION_UNSAFE` as an invalid/abstaining system outcome, never as compliant preservation.

**Validity qualifications:** This audit computes exact-string retention of synthetic event lines, not temporal decision accuracy; uses the native **regex-only baseline** rather than the upstream selective cascade or SafetyMargin classifier; tests a synthetic budget in estimated tokens; and does not exercise upstream TypeDecompose, TypeRetrieve, end-to-end downstream agent behaviour or the published corpus. Therefore `PINNED_UPSTREAM_COMPONENT_TEST_PASS` means *code executes and evidence can be verified*, **not** that Knowledge Triage was faithfully reproduced at framework or paper level. The source-annotated sensitivity lane is an *adaptation with privileged event labels* and cannot be benchmarked as the official native model.

**Method next step:** exercise the original pinned operators separately with their original signatures; test budget overflow, replication after partitioning and retrieval top-k overflow; record failures as failures without altering upstream code or silently adjusting oracle-sensitive labels. A faithful full-framework baseline remains **INCOMPLETE** until its official classifier/cascade and relevant downstream paths are run with documented equal information access, source provenance and budgets.
