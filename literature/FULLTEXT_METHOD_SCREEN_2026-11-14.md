# WAMBU-001 | Method-level prior-art audit (14 November 2026)

**Research role:** distinguish the study's operational question from already published results. A bibliographic mention is not evidence of novelty. This screen can be expanded and independently reviewed, but no model suggestion may certify a scientific contribution.

## Source A: Zerhoudi, Mitrović and Granitzer (2026), CIKM 2026

- **DOI and venue verified:** `10.1145/3799682.3840567`, *The Compaction Cliff in Long-Running AI Agent Memory*, Proceedings of CIKM 2026, Rome.
- **Methods/full text read:** https://arxiv.org/html/2608.22752 , Sections 3.1–3.3 and 4.2–4.5. Public repository: https://github.com/searchsim-org/cikm26-knowledge-triage, inspected commit `a6ceb01a3368cee25ef7ebcf05ebdab8c9be24a4`.
- **What overlaps:** repeated safety-constraint loss under compaction; typed constraint preservation; deterministic verification; model-driven safety decisions. The published TypeCompact includes a protected fidelity lane, minimum safe budget, a verifier and an `Unsafe` fallback. Our unqualified claim that external pinning preserves rules better than generic summaries is **not new**.
- **What is NOT replicated by WAMBU v3:** classification via the actual upstream model/cascade; TypeDecompose and TypeRetrieve; five-corpus evaluation, multiple production models, prescribed budgets. Our comparator is labelled `typed_retention_adapted` rather than `KnowledgeTriageOfficial` or `replication`.
- **Unanswered in this audit:** The released framework does not foreground an explicit actor/category revocation-action benchmark as its main result, but absence of a phrase in the paper is not proof that no prior method does so. We cannot claim a first-of-kind problem.

## Source B: Patel (2026), *Supersede: Diagnosing and Training the Memory-Update Gap in LLM Agents*

- **Publication:** arXiv:2606.27472v1, 25 June 2026. Peer-review status: **preprint**, not a verified accepted journal or conference paper.
- **Methods/full text read:** https://arxiv.org/html/2606.27472 , especially Sections 3–5 and 7.
- **Direct overlap:** correct interpretation of later updates versus obsolete facts; bounded self-maintained memory compared with full history; supersession-aware reward; empirical evidence on LongMemEval's knowledge-update subset.
- **Important negative evidence:** Section 4 reports **100% full-context accuracy on clear templated synthetic supersession timelines**, which were judged saturated; the study used real dialogues for discrimination. WAMBU's explicit synthetic amendment stream may likewise be too easy for strong models. It remains an engineering fixture until harder cases and independent data are introduced.
- **Potential specific extension:** multi-authority *operational policies* with independent rule provenance and both costs of errors (stale false rejection / missed newly active enforcement) under recursive compaction. This is a **candidate** distinct application, not established originality.

## Source C: Kang et al. (2026), ACON (ICML 2026)

- **Primary published record checked:** https://proceedings.mlr.press/v306/kang26b.html, PMLR Vol. 306, pp. 55321–55375.
- **Metadata and abstract:** verified; detailed model-specific protocol and appendix have **not** been independently reviewed here.
- **Overlap:** compression-guideline optimisation from failure trajectories and smaller-model distilled compressors. WAMBU does not implement the ACON training/adaptation procedure and must not claim an ACON reproduction.

## Source D: Wu et al. (2025), LongMemEval (ICLR 2025)

- **Primary published venue:** https://proceedings.iclr.cc/paper_files/paper/2025/hash/d813d324dbf0598bbdc9c8e79740ed01-Abstract-Conference.html.
- **Metadata/abstract-only status** for this audit. It contains knowledge-update tasks, so evaluating information supersession is not itself original.

## Method decisions resulting from this audit

1. **Retire** the generic novelty hypothesis “safety constraints survive compaction when externally pinned”.
2. Keep the published **eight-episode v2 pilot** as a null-effect feasibility result (typed conditions were not evaluated in that pilot).
3. Use v3 synthetic *authorised policy changes* only as an **exploratory feasibility** study, not a publication-valid demonstration of previously undocumented supersession failures.
4. Require independent replication with harder, preferably naturalistic multi-authority policy updates before asserting a novel research finding; predefine temporal authority source and revocation semantics.
5. Keep a clear adaptation-versus-reproduction label for Knowledge Triage, and disclose unequal prompt budgets and available sources in every report.
6. Document a human scientific review and prospective power calculation before creating any holdout observations or claiming a confirmatory run.

## Decision record

- `ENGINEERING_READY_FOR_V3_LIVE_PILOT`: **YES**, subject to passing CI and the independent API preflight.
- `NOVELTY_ESTABLISHED`: **NO**.
- `CONFIRMATORY_PROTOCOL_FROZEN`: **NO**.
- `SUBMISSION_READY`: **NO**.
