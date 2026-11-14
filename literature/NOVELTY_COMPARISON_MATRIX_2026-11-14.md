# WAMBU-001 | Falsifiable novelty and comparator matrix

**Working research map, not novelty certification.** Source URLs point to identifiable publications. No row establishes that a technique is the first of its kind. Distinguish original upstream components from adaptations and the developing WAMBU instrument.

| Research question / method | CIKM 2026: Compaction Cliff + Knowledge Triage | Supersede (Patel 2026, preprint) | WAMBU observed v2/v3 | Open, testable distinction |
| --- | --- | --- | --- | --- |
| Exact rule retention over repeated compaction | Direct topic with typed constraint preservation, retrieval, verification and unsafe fallback | Adjacent long-memory context | v2 raw summary and ledger both 100% in synthetic cases | **Not a defensible general novelty claim** |
| Correct use of updated information | Not solely a time-ordered revocation-action benchmark, but typed retention relevant | Directly studies superseded facts and real conversations | v3 revocation probes: all tested full-context/summary/adapted/ledger arms 0/16 errors | Simple synthetic updates already saturated; harder external cases needed |
| Multi-authority precedence and invalid revocations | Component framework could encode authoritative constraints; domain-specific baseline comparison not yet done | Generic changed facts; dialogue updates | v4 offline candidate introduces ranks, time and disputed revocations | Does an independently justified authority/conflict rubric yield different failure modes? **Unknown** |
| Full baseline parity | Authors release native classifier, TypeCompact, TypeDecompose and TypeRetrieve | Released external code and environment | Original upstream TypeCompact component audited; no end-to-end KT reproduction | Faithful reproducibility is **still missing**, do not label adapted baseline official |
| Matched token and information budgets | Explicit compaction budgets/unsafe states | Memory budget experiments | v2/v3 measured raw token counts; prompts and authoritative knowledge unequal | Run matched-information ablations and preserve `COMPACTION_UNSAFE` |
| Naturalistic independent episodes | Five corpora and behavioural benchmarks | Real dialogue update examples | Current policy updates are synthetic, periodic and easy | Human-authored independent source/authority conflicts with blinded adjudication required |
| Confirmatory inferential evidence | Published experiments with reported statistical tests | Preprint reports update effects | v2/v3 exploratory episode differences all zero, no valid confirmatory p-value | Freeze new estimand and adequately powered protocol *before* private split |

## Primary source index

1. Zerhoudi, S., Mitrovic, J. and Granitzer, M. (2026), [The Compaction Cliff in Long-Running AI Agent Memory](https://arxiv.org/abs/2608.22752), CIKM 2026, [DOI:10.1145/3799682.3840567](https://doi.org/10.1145/3799682.3840567); [released code](https://github.com/searchsim-org/cikm26-knowledge-triage).
2. Patel, V. (2026), [Supersede: Diagnosing and Training the Memory-Update Gap in LLM Agents](https://arxiv.org/abs/2606.27472), preprint, with code/data linked from the abstract.
3. Kang et al. (2026), [ACON](https://proceedings.mlr.press/v306/kang26b.html), ICML 2026. This audit has not reproduced its training procedure.
4. Wu et al. (2025), [LongMemEval](https://proceedings.iclr.cc/paper_files/paper/2025/hash/d813d324dbf0598bbdc9c8e79740ed01-Abstract-Conference.html), ICLR 2025.

## Claim adjudication

- Rejected: "first to detect loss of safety rules in agent compaction" and "the ledger significantly outperforms recursive summarisation".
- Pending: "multi-authority policy supersession causes measurably distinct errors from previously published context-memory update benchmarks". Requires falsifiable comparison, naturalistic cases, audited baselines, and independent expert literature assessment.
- Allowed now: "we implemented and piloted a synthetic temporal policy scenario benchmark with no demonstrated difference between the target arms"; "the short-window baseline showed lower overall raw accuracy"; both remain strictly descriptive.

Never insert fictional citations or positive outcomes into the manuscript. Record every departure from published Knowledge Triage as an adaptation with the original revision and operator settings.
