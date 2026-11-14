# WAMBU-001 | P07 and P08 bounded implementation design

**Authority:** candidate engineering work. This is not a frozen scientific design, qualified naturalistic benchmark, full Knowledge Triage framework reproduction or new paid empirical study.

## Evidence

- Historical v2 and v3 measured zero candidate effect and saturated simple policy-amendment probes.
- The author-released [Knowledge Triage repository](https://github.com/searchsim-org/cikm26-knowledge-triage), **pinned to** `a6ceb01a3368cee25ef7ebcf05ebdab8c9be24a4`, contains unmodified TypeCompact, TypeDecompose, TypeRetrieve operators, a native regex classifier, and more advanced encoder/LLM classifier implementations.
- The original pinned [LICENSE](https://github.com/searchsim-org/cikm26-knowledge-triage/blob/a6ceb01a3368cee25ef7ebcf05ebdab8c9be24a4/LICENSE) is Apache-2.0; the project dependencies are defined in its pyproject. This work loads read-only original modules at runtime. It does not vendor or rewrite their implementations.

## Bounded terminal state

1. A public, intentionally fictional, twelve-case development casebook demonstrates varied organisational communication, authority disputes, revocation, source trust, delayed effective times, scope and abstention. Each public case is separate from its simulator-only reference sidecar. **Zero cases are independently human-adjudicated; all cases remain synthetic and authored within the research project.** No confirmation or private seed exists.
2. A finite offline workflow runs the **three original pinned operator functions** and native regex classifier on the same public cases, plus a distinctly labelled source-annotated sensitivity lane that changes type inputs. Original source revision and module SHA256 are written to output.
3. Original TypeCompact `COMPACTION_UNSAFE` remains an outcome, never relabelled successful. TypeDecompose partition-locality and budget checks are reported. TypeRetrieve is evaluated only with an article-specific, simple lexical relevance function and test scope. These are **component-level** tests, not the published five-corpus benchmark.
4. Source-visible KB does not receive reference action, fixture family or human-review claims. All model calls, cost-bearing inference calls and confirmatory accesses equal zero.
5. GitHub Actions archive contains input cases, segregated development-only reference sidecar, operator rows and summary.

## Engineering choices and caveats

The approach uses read-only loading of source-pinned author modules rather than vendoring code. Both native regex and source-annotated lanes are reported side by side because an annotation changes the source-classification method. The chosen lexical relevance and topic scope are not the authors' published downstream retrieval evaluator. Token budgets use the original 4-chars/token heuristic, not model tokenizer parity. TypeDecompose may emit partitions over budget on impossible inputs; such outcomes are reported as fail/unsafe, never silently filtered.

## Exit and blockers

Engineering acceptance: CI passes the casebook/reference separation tests, exact upstream commit check, three operator invocations and no-call constraints; original evidence artifact exists and is audited. **P07 remains PARTIAL** until human independent case authorship/adjudication and a defensibly naturalistic corpus. **P08 remains PARTIAL** until original published baseline's full classifier/cascade, benchmark corpora, semantics, safe fallback and matched downstream model behaviour can be independently verified.

No inference, scientific approval, confirmation or submission can follow solely from these tests.
