# P08b | Source-faithful public sample component sweep, not full replication

## Bounded objective and original source

Execute the original authors' unmodified `classify_instruction`, `KnowledgeBase.from_lines` and `type_compact` on all **327 publicly released AgentArtifactCorpus sample files** at the immutable [Knowledge Triage source revision](https://github.com/searchsim-org/cikm26-knowledge-triage/tree/a6ceb01a3368cee25ef7ebcf05ebdab8c9be24a4), with file-level source hashes and a documented sample manifest hash. This is not the published benchmark regime, which includes the authors' cascade and LLM comparisons.

The [original public sample](https://github.com/searchsim-org/cikm26-knowledge-triage/tree/a6ceb01a3368cee25ef7ebcf05ebdab8c9be24a4/data/sample) has a manifest of 327 files. The original project README states a licence and privacy/opt-out policy for the sample. No upstream source texts are committed to this project or included in the produced artifacts.

## Original component protocol

- Use upstream `classifier.py`, `kb.py` and `operators.py` unchanged. No post-hoc type annotation or human gold injection.
- For each file, original `KnowledgeBase.from_lines` classifies nonempty lines using the upstream regex classifier.
- Run TypeCompact at budgets `int(kb.total_tokens * ratio)` for 25%, 50%, 75% and 100% (minimum 1 token), retaining the upstream estimated-token heuristic. Each ratio is **an article-authored sensitivity sweep**, not an assertion of exact published benchmark parameters.
- Record `COMPACTION_UNSAFE` separately; if constraints exceed budget, report the original unsafe output but do not treat it as feasible preservation.
- Exact-text retention of native regex-classified constraints is an instrument diagnostic, **not a safety-rule semantic recall metric**. Cases with zero native constraint classifications cannot be treated as safe or correct.
- Each record stores a file hash, original token estimate, native `b_min`, budget, constraint count, output status, overflow and preservation. Aggregates use only feasible files for their conditional recall and separately count infeasible files.
- No paid model calls, classifier cascade, SafetyMargin, TypeDecompose/TypeRetrieve published benchmark or downstream task, and no private holdout.

## Full P08b still requires

The original authors' classifier cascade/embedding/LLM or SafetyMargin path under a versioned dependency lock and model availability; the exact published dataset selection, seeds, budget regime and metrics; matched downstream model prompts and source information; original-implementation full framework controls; independent method-level review. See [P08b issue](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/issues/6). **This component sweep cannot close that issue.**
