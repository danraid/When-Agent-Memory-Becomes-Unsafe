# Source-screening and overlap audit | 14 November 2026

**Evidence standard:** publisher pages verified; where specified, publisher/hosted PDF sections were visually inspected for title, authors and relevant scientific scope. This is a structured methodological *screen*, not a claim that every article was exhaustively line-by-line audited or that the paper has established novelty. Do not label candidates as SCIENTIFICALLY_APPROVED without human scholarly review.

| Work, authoritative record | Verification level | Relevance and overlap | Gap not yet proved unique |
|---|---|---|---|
| Liu et al. (2024), *Lost in the Middle*, TACL 12:157-173, DOI 10.1162/tacl_a_00638, https://aclanthology.org/2024.tacl-1.9/ | PUBLISHER_METADATA_AND_PDF_METHOD_SPOTCHECKED | Controlled relevant-information position, long-context distractors, key-value retrieval. Documents context-location sensitivity rather than policy-rule persistence. | Synthetic contexts alone are not new. |
| Wu et al. (2025), *LongMemEval*, ICLR, https://proceedings.iclr.cc/paper_files/paper/2025/hash/d813d324dbf0598bbdc9c8e79740ed01-Abstract-Conference.html | PUBLISHER_METADATA_AND_PDF_METHOD_SPOTCHECKED | 500-question long-term-memory benchmark including temporal reasoning, knowledge updating and abstention. Authorised policy changes overlap broadly with knowledge updates. | Cannot claim memory update evaluation is new. |
| Kang et al. (2026), *ACON: Optimizing Context Compression for Long-horizon LLM Agents*, ICML, PMLR 306:55321-55375, https://proceedings.mlr.press/v306/kang26b.html | PUBLISHER_ABSTRACT_AND_PMLR_RECORD_VERIFIED; full text not yet checked | Optimises compression guidelines using failure trajectories; broad history/state preservation with agents. | Cannot claim repeated agent context compression is novel. |
| Liu et al. (2026), *CompactionBench*, Microsoft research preprint, https://www.microsoft.com/en-us/research/wp-content/uploads/2026/10/CompactionBench_preprint.pdf | HOSTED_PREPRINT_PDF_ABSTRACT_AND_BENCHMARK_SECTION_SPOTCHECKED | Explicit multi-turn persistent coding-agent compaction and executable quality assessment; performance/cost/caching questions. PREPRINT, not established peer-reviewed acceptance. | Cannot call compaction evaluation itself first-of-kind. |
| Wang et al. (2026), *Context Compression for LLM Agents: A Survey of Methods, Failure Modes, and Evaluation*, EMNLP, DOI 10.18653/2026.emnlp-main.2396, https://aclanthology.org/2026.emnlp-main.2396/ | PUBLISHER_METADATA_AND_PDF_FAILURE_TAXONOMY_SPOTCHECKED | Distinguishes F1 pre-compression decisions, F2 in-compression information loss and F3 post-compression access errors; explicit critical-constraint preservation is already part of taxonomy. | Novelty cannot reside in asserting compression loses critical constraints. |

## Proposed narrowly bounded contribution, NOT a novelty certificate

A version-controlled, episode-paired empirical test of authorised, *superseded* workflow constraints when GPT recursively summarises its own operational memory, contrasting raw decisions under (1) summary only and (2) the *systems-level addition* of independently persisted current authorised policies. The rule guard is an explicitly secondary, non-LLM post-processor. The hypothesis concerns a specific architecture's unsafe raw approval rate after two or more compactions, **not** intrinsic LLM recall at matched information or a universal safety result.

## Bias and publication checks remaining

- Check full methods/appendices of ACON and other overlapping methods, especially whether policy-ledger baselines are already evaluated; no absolute novelty language before this check.
- Verify true official volume/DOI/venue identities before BibTeX export; DOI-free conference papers should be cited by publisher URL, not invented DOI.
- Human method review is still required. No unverified quotation or literature-based success claim enters manuscript results.
- Report negative, null and uncertain findings equally. Distinguish the in-development benchmark from naturalistic policy workflows, state-dependent feedback and production agents.
