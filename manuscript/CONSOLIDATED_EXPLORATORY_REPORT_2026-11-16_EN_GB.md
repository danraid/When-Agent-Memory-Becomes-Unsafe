# When Agent Memory Becomes Unsafe: Ceiling Effects, Policy-State Asymmetry and Mixed Cross-Model Evidence in Exploratory Context-Compaction Evaluations

**Consolidated British-English research manuscript, 16 November 2026.** This is an **exploratory, non-confirmatory pre-review draft**, not a registered report, an independently adjudicated safety benchmark, a journal submission or a peer-reviewed publication. Author identities and author-identifying repository links are deliberately omitted from this reading copy; its presence in a named public source repository **does not certify double-blind anonymity**. The separate internal provenance register is not part of any anonymous submission.

## Abstract

Long-running language-model agents use compacted histories to retain instructions while controlling context length. When authoritative rules change, a useful memory must not merely preserve old constraints but also stop applying legitimately superseded ones. We audited multiple development experiments on policy memory and evaluated whether these instruments could detect unsafe authorisation decisions. An eight-episode synthetic pilot produced 144/144 correct responses for full history, recursive summary and an authorised-policy ledger, versus 105/144 for a recent-window control. A distinct four-episode temporal pilot saturated on explicit revocation and new-restriction probes: all 16 probes of each type were handled correctly in every arm. A separate four-model, four-episode OpenRouter safety pilot evaluated 1,433/1,440 planned model-condition observations, with four provider rate-limit failures and three unavailable derived guard outcomes. The exploratory post-two-compaction episode-mean difference in raw unsafe approvals between recursive summary and a policy ledger was zero for two models, negative for one, and not fully estimable for one. A source-pinned original Knowledge Triage TypeCompact component test on 327 author-released files identified 19, 4, 1 and 0 infeasible files at four relative token budgets. Independent public-source intake added six verified PEP/RFC supersession pairs and sixteen authentic governance/code-change PR histories, but no independently human-adjudicated agent-authorisation reference labels. These are **mixed or null descriptive results**, not evidence of universal safety, architectural superiority or statistical equivalence. We identify ceiling effects, unequal authority access, failed evidence contracts and missing human reference validity as the next measurement problems.

**Keywords:** agent memory; recursive compaction; policy supersession; unsafe approval; abstention; real-source provenance; negative findings; reproducibility.

## 1. Introduction

Agents that run for long periods often compress interaction histories into summaries or retrieve records from storage. A safety-relevant instruction may need to persist across that compression, but persistence alone is insufficient when later authenticated actions revoke, narrow or replace it. Applying a stale restriction can wrongly reject a legitimate request; forgetting an active restriction can approve an impermissible request. An evaluation needs to distinguish these errors, the information made available to each system, and the time and authority that establish a rule's validity.

This problem has substantial prior art. The Compaction Cliff and Knowledge Triage propose preserving safety rules through type-sensitive memory operators [1]; Supersede studies agents that fail to update long-term memory when facts change [2]; ACON optimises long-horizon agent context compression [3]; and LongMemEval tests several long-memory capabilities, including updates and abstention [4]. We therefore **do not claim to have invented constraint pinning, memory supersession or typed compaction**. Instead, we examine whether a series of small development instruments discriminated the intended policy-safety failure modes, what actually happened across different LLMs, and which external-validity claims remain unsupported.

Our contributions are bounded: (i) a documented audit of ceiling effects in synthetic temporal-policy tasks; (ii) an exploratory, multi-provider study that preserves missingness and negative contrasts; (iii) a source-faithful **component** diagnostic for the original Knowledge Triage implementation; and (iv) a separation of real published documents, real historical software decisions, AI-simulated expert opinions and independent human ground truth.

## 2. Research questions

**RQ1.** Do the original synthetic development trajectories discriminate memory strategies on policy revocation and activation, or do they saturate?

**RQ2.** What descriptive unsafe-approval and false-rejection differences occur across decision LLMs when a fixed summary model is used and policy-information access differs by arm?

**RQ3.** What budget-feasibility and classifier-domain limitations appear when original, source-pinned Knowledge Triage components are exercised outside their authors' published benchmark?

**RQ4.** What can genuinely external PEP/RFC documents and historically observed code-governance changes establish before qualified independent human adjudication of agent-authorisation decisions?

These questions describe **separate development instruments**. The individual studies differ in task design, sample size, response limits, model mix and error contracts; they are not a pooled confirmation or a model-ranking contest.

## 3. Methods

### 3.1. Study structure and independent units

The earlier policy-memory v2 development pilot used eight synthetic episodes of 18 decision turns each. Its full-history, recent-window, recursive-summary and authorised-policy-ledger arms made genuine model decisions, with a deterministic guard derivative. A separate v3 temporal pilot used four 18-turn episodes and added an adapted typed-retention condition. The simulator provided an oracle reference for each request; episode trajectories, rather than individual turns, were the meaningful independent units. The temporal run's original advisory-review workflow failed, while the empirical observations were preserved and later audited.

Later OpenRouter safety pilots used a common summary anchor across decision-model arms, a finite per-call ledger and a detached evaluator. The main four-episode multi-model study used GPT-4.1 Mini, Gemini 2.5 Flash, DeepSeek V3.1 and Qwen3 Next 80B A3B Instruct. Each model encountered 72 decisions in each of five conditions: full history, recent window, recursive summary, explicit authorised-policy ledger, and a derived deterministic guard that reused the ledger arm's raw response. The planned total was 4 × 72 × 5 = 1,440 scored model-condition rows. The shared compacting model was GPT-4.1 Mini. The ledger arm received explicit current authorised-policy information that may have been absent from truncated histories.

The v3 typed-retention adaptation and the externally managed ledger are **not** the complete Knowledge Triage framework. The guard is likewise not another independent LLM observation. Because the memory arms were not equal-information treatments, comparisons assess *configured systems*, not intrinsic model memory under identical evidence.

### 3.2. Outcomes and predeclared development contrasts

We distinguish a raw **unsafe approval**, when a model authorises a request that the simulator reference requires rejecting, from a **false rejection**, when a permissible request is denied. Invalid JSON, provider errors, missing guard derivatives and source-comparison failures remain explicit missing/invalid observations. These outcomes are not treated as successes merely because a downstream deterministic guard could correct a raw model action.

For the OpenRouter policy-safety study, the exploratory contrast was the per-episode proportion of raw unsafe approvals after at least two genuine summary compactions in the `recursive_summary` condition **minus** the corresponding proportion in `pinned_ledger`, restricted to reference-reject cases. No full four-episode mean is calculated when an episode lacks a paired eligible response. We do not report p-values, infer equivalence or treat repeated turns as independent samples. The earlier two-episode and later four-episode OpenRouter pilot runs are reported separately because their seed and pacing policies differ.

### 3.3. External public benchmark companion

A separate LongMemEval-S cleaned **six-question** development sample was used as an external question-answering companion [4]. Four decision models were run under three memory arms, yielding 72 model-condition responses in the later successful pilot. A distinct Claude Haiku scorer assessed answers only after response generation; that scorer is fallible and **not** an independent human adjudicator. Six questions do not support model ranking or external claims about the safety of operational actions. This public Q&A instrument is **not** the synthetic policy-authorisation benchmark used elsewhere in this paper.

### 3.4. Original-source Knowledge Triage component diagnostic

At upstream revision `a6ceb01a3368cee25ef7ebcf05ebdab8c9be24a4` of [1]'s released code, original `KnowledgeBase`, regex `classify_instruction` and `type_compact` functions were executed on 327 authors' public sample files under relative estimated-token budgets of 25%, 50%, 75% and 100%. The resulting 1,308 file-budget trials recorded `COMPACTION_UNSAFE` rather than counting infeasible outputs as safe compression.

Additional externally sourced PEP/RFC excerpt tests ran the original TypeCompact, TypeDecompose and TypeRetrieve operator functions at budgets 16, 32 and 64 under the native regex classifier. Relevance and topic-scope callbacks used by TypeRetrieve were WAMBU-created adapters, not the paper's published evaluation stack. The original embedding classifier, LLM adjudication cascade, SafetyMargin and full downstream benchmarks were **not** reproduced. This component run is not the complete Knowledge Triage framework. Consequently these are source-faithful component tests, not an end-to-end methods replication.

### 3.5. Public document provenance, governance outcomes and code diffs

We verified six PEP/RFC supersession source–target pairs at explicit repository revisions and original Git blob identities. Twelve study-constructed questions, six correct-target and six substituted-target controls, tested literal supersession links. Three AI role simulations per question produced 36 original responses; exact documentary evidence was separated from evaluator-side references.

A distinct collection of eight authentic closed Python PEP/Rust RFC governance PRs documented five public merges and three closures without merge. A later collection of eight code-modifying CPython/Rust PRs documented four merged and four unmerged proposals, including actual code patch snapshots and pre-closure time-stamped review comments. Three AI-simulated specialist roles reviewed each case. Factual PR disposition was kept outside the reviewer prompts.

**Historical observation is not policy correctness.** A merged proposal is not automatically compliant; an unmerged proposal is not necessarily unsafe. GitHub PR titles, bodies and diff snapshots retrieved retrospectively may reflect post-decision edits, although individual comments were filtered by their historical timestamps. The quoted PEP/RFC revision may not have been the legally or procedurally effective version at the event time. No authentic operational *agent-authorisation* decision reference was independently established from these records.

### 3.6. Integrity, failures and scientific review status

Original experiments retained model outputs, provider response identifiers, configuration/source hashes and original failure status. Detached audits re-checked source/configuration, prompt construction, evaluator and guard derivation and missingness without buying replacement model inferences. A green offline replay certifies computational reproducibility of a frozen evaluator under its rules, **not** semantic validity of the reference labels.

AI-simulated domain-review roles were deliberately blind to one another's outputs, but they are not genuinely independent qualified human experts. Original strict JSON contracts and subsequent detached, explicitly labelled presentation-envelope normalisation were recorded as different evidence states. Across all phases, **zero independent human policy-action adjudications**, **zero authorised confirmatory holdout runs**, and **zero journal submissions** were documented.

## 4. Results

### 4.1. Synthetic policy-memory ceiling

**Table 1.** Eight-episode synthetic development pilot, 18 turns per episode.

| Memory system | Correct / 144 | Unsafe approvals / 88 reject opportunities | False rejections |
|---|---:|---:|---:|
| Full history | 144 | 0 | 0 |
| Recent window | 105 | 25 | 14 |
| Recursive summary | 144 | 0 | 0 |
| Authorised-policy ledger | 144 | 0 | 0 |
| Derived guard | 144 | 0 | 0 |

The episode-level raw unsafe-approval contrast between recursive summary and ledger was zero in each of the eight independent episodes. That result indicates **no observed improvement** in this ceiling-prone sample, not proof of equivalence.

**Table 2.** Distinct four-episode temporal pilot.

| Memory system | Correct / 72 | Wrongful revocation rejections / 16 | Missed new-rule enforcement / 16 |
|---|---:|---:|---:|
| Full history | 72 | 0 | 0 |
| Recent window | 52 | 0 | 0 |
| Recursive summary | 72 | 0 | 0 |
| Adapted typed archive | 72 | 0 | 0 |
| Authorised-policy ledger | 72 | 0 | 0 |
| Derived guard | 72 | 0 | 0 |

The recent-window arm achieved 52/72 correct responses; all 20 of its errors occurred in controls. Every system correctly handled all 16 explicit revocation and 16 newly effective restriction probes. Thus, the available probe family was **non-discriminative** for the temporal mechanism under test. These two development studies were not combined into a common significance analysis.

### 4.2. Multi-model policy-safety pilot

The four-model, four-episode OpenRouter study produced **1,433/1,440 scored rows (99.51%)**, with all **20/20** shared recursive compactions present. Four Gemini API calls returned HTTP 429, leading to four missing paid decisions and three additional unavailable derived guard outcomes. The original workflow was recorded as **failed/partial**; a later read-only evidence audit succeeded. The prior two-episode OpenRouter study scored **714/720** planned rows, again separately and not pooled.

**Table 3.** Unsafe **raw** approvals among evaluated reference-reject cases in the four-episode study; the guard column shows final actions after deterministic override.

| Decision model | Full history | Recent window | Recursive summary | Policy ledger | Guard, final |
|---|---:|---:|---:|---:|---:|
| GPT-4.1 Mini | 2/40 | 9/40 | 1/40 | 1/40 | 0/40 |
| Gemini 2.5 Flash | 0/39 | 16/40 | 3/40 | 1/38 | 0/38 |
| DeepSeek V3.1 | 0/40 | 2/40 | 0/40 | 0/40 | 0/40 |
| Qwen3 Next 80B | 0/40 | 8/40 | 1/40 | 1/40 | 0/40 |

For the predeclared exploratory post-two-compaction contrast (recursive summary minus ledger), the episode-mean difference was **0.0000** for GPT-4.1 Mini, **0.0000** for DeepSeek V3.1 and **−0.035714** for Qwen3 Next; the Gemini mean was **not estimable** because two episodes lacked eligible paired decisions. The Qwen result runs **against** a uniform positive ledger effect. No cross-model significance ranking is appropriate with four independent episodes per model.

Safety and utility were in tension: within the recursive-summary condition, false rejections on 32 valid-reference requests were GPT-4.1 Mini **6**, Gemini **3**, DeepSeek **15**, and Qwen **10**. Those values warn against treating low unsafe-approval counts as a complete measure of quality. The guard's zero *observed final* unsafe approvals do not mean the raw model always acted safely or that unobserved deployment failures are impossible.

### 4.3. External LongMemEval companion

The later public six-question LongMemEval-S development run obtained **72/72 scored model-condition answers** across four models and three memory arms. The full-history arm was descriptively stronger than truncated and recursive-summary arms in this very small sample, but memory conditions did not have identical information and the sample is not inferentially representative. LongMemEval evaluates conversational question answering, not authorisation actions; it cannot be substituted for the safety endpoint in Table 3.

### 4.4. Knowledge Triage original-component feasibility

**Table 4.** Original TypeCompact on 327 authors' public sample files.

| Estimated-token budget | Feasible / 327 | COMPACTION_UNSAFE | Files with native regex constraints, among feasible | Conditional exact constraint retention |
|---|---:|---:|---:|---:|
| 25% | 308 | 19 | 210 | 1.000 |
| 50% | 323 | 4 | 224 | 1.000 |
| 75% | 326 | 1 | 227 | 1.000 |
| 100% | 327 | 0 | 228 | 1.000 |

Conditional exact-string retention follows the original operator's constraint-pinning logic; it is **not** independently adjudicated semantic rule recall or a new algorithmic improvement. At 25% of estimated source tokens, 19 files could not fit the protected material. Separate source-backed document-excerpt experiments ran **36** operator/budget trials; the native regex presented all **72 input-item presentations as beliefs**, rather than constraints, and TypeDecompose produced **two over-budget partitions**. These are documented native-classifier domain and budget behaviours, not evidence that the authors' published complete method failed.

### 4.5. Genuinely external sources and AI-only reviewers

**Table 5.** Source-realistic development tasks. Each row is a *different instrument*, not another treatment arm.

| Evidence family | Authentic external material | AI evaluation | Scientific ground-truth limit |
|---|---|---|---|
| P07b document links | 6 verified PEP/RFC source pairs; 12 constructed link questions | Original strict 7/36 votes; detached exact-fence reparse 36/36, 7/12 unanimous, 31/36 matched constructed documentary labels | Links, not operational agent decisions |
| P07c governance PRs | 8 genuinely closed public PRs; 5 merged, 3 not merged | 17/24 strict-valid, 11 matched observed disposition, 6 abstained | Observed merge status is not normative correctness |
| P07d code PRs | 8 authentic source-code-diff proposals; 4 merged, 4 unmerged | 17/24 strict-valid; two of eight cases unanimous among all three valid AI roles | Retrospective patches and policy-effective times uncertain |

The P07b original JSON-strict workflow remains failed, notwithstanding the later transparent presentation-only recovery of fenced JSON. Both P07c and P07d AI panels retained **seven** strict-invalid outputs. These are not replacement human validators, and their opinion agreement cannot establish policy-action correctness.

## 5. Discussion

Three findings emerge. First, a plausible synthetic experiment can be **non-discriminative on its target mechanism** while an obvious information-removal control produces errors. In the temporal pilot, reporting overall recent-window accuracy without showing that all explicit supersession probes saturated would mischaracterise the result.

Second, information access is a central confound. A ledger that always receives current authenticated policy state is not a controlled test of intrinsic memory capacity relative to a window that may never see that state. The multi-model study likewise provides no uniform positive ledger effect in its post-two-compaction contrast. Negative or zero differences are legitimate outcomes and cannot be 'repaired' by repeating provider calls until an expected sign appears.

Third, *external* can refer to several quite different things: documents authored outside the study, historical human development choices, model-generated simulated reviews, or real prospective independently qualified human adjudications. Only the first two were sourced; the last was not completed. Reported P07b–P07d material broadens source realism but cannot support a naturalistic *agent-authorisation* gold-label claim.

A genuinely discriminative next design would require authenticated policy issuer and effective-time state, conflicting or delayed updates, identical access to source evidence across memory systems, independently judged operational reference decisions, and a prospectively selected episode count. It should additionally preserve abort/abstain as a legitimate action and penalise false rejections. Claims of complete Knowledge Triage comparability must wait for its exact original classifier/embedding/LLM cascade, SafetyMargin, author-published evaluation corpus and downstream scoring under documented budgets. Until then, our comparisons must retain **component-only** or **adapted** labels.

## 6. Threats to validity

**Construct:** synthetic 'approve/reject' records simplify enterprise policies; public PEP/RFC links are not authorisation rules. **Internal validity:** unequal policy access, common fixed simulator trajectories, fixed compactor shared across model arms, and retrospective PR body/diff contamination. **Reference validity:** the simulator reference is deterministic rather than independently human adjudicated; GitHub merge/closure is factual workflow state, not ethical or technical correctness. **Statistical:** only eight and four independent episodes in central development studies, and four in the multi-model comparison; selection of six LongMemEval items prevents stable model rankings; no pre-registered confirmatory testing has occurred. **Operational:** hosted checkpoints may drift, HTTP 429 errors created nonrandom missingness and strict model-output contracts rejected outputs. **Method equivalence:** externally adapted retrieval callbacks and native regex-only components do not reproduce the full Knowledge Triage paper. **Novelty:** method-level overlap with [1–3] remains, and no independent external scientific novelty assessment has authorised a positive originality claim.

## 7. Ethics, reproducibility and disclosures

This research used public software-source material and synthetic agent tasks, not recruited human research subjects. It nevertheless used **public reviewer and contributor comments** in source archives; data licensing, privacy assessment and any ethics exemption need confirmation under the intended venue's rules. AI systems assisted with case construction, coding, editing and simulated scientific specialist reviews. **No AI model was represented as a real human expert or journal reviewer.** The author remains responsible for all results, references and originality. The complete author-identifying evidence/provenance register is maintained separately; any anonymous journal supplement must be produced afresh without public identity leaks. Actions artefacts may expire and are not, by themselves, permanent archival repositories.

Data availability for double-blind review, funding, author affiliation, competing interests, legal rights to redistribute excerpts and any human-ethics declaration must be confirmed by the actual author. A publisher-specific first-page AI-use disclosure, verified official LaTeX style and author-approved complete anonymous supplement are still required before a TMLR submission. No permission to release confirmatory data or submit this manuscript is inferred from permission to continue research work.

## 8. Conclusion

The available exploratory instruments identify a **ceiling on simple temporal-policy probes**, a descriptive vulnerability of short-memory windows to lost context, mixed/null cross-model effects, and budget-feasibility limits in an original compaction component. They do not validate a uniformly safer memory architecture, prove model equivalence, replicate the entire Knowledge Triage system or establish correctness on independently adjudicated real-world authorisation decisions. The scientific value at this stage is methodological: preserving original failures and separating simulated evidence from qualified reference truth reveal what a stronger future benchmark must establish.

**Terminal research status:** `EXPLORATORY_REPORT_COMPLETE_FOR_AUTHOR_AND_EXTERNAL_METHOD_REVIEW`; `PROSPECTIVE_CONFIRMATION_NOT_AUTHORISED`; `JOURNAL_SUBMISSION_NOT_AUTHORISED`.

## References

[1] Zerhoudi, S., Mitrović, J. and Granitzer, M. (2026). The Compaction Cliff in Long-Running AI Agent Memory. *Proceedings of the 35th ACM International Conference on Information and Knowledge Management (CIKM '26).* DOI: [10.1145/3799682.3840567](https://doi.org/10.1145/3799682.3840567).

[2] Patel, V. (2026). Supersede: Diagnosing and Training the Memory-Update Gap in LLM Agents. *arXiv* preprint [2606.27472](https://arxiv.org/abs/2606.27472).

[3] Kang, M., Chen, W.-N., Han, D., Inan, H. A., Wutschitz, L., Chen, Y., Sim, R. and Rajmohan, S. (2026). ACON: Optimizing Context Compression for Long-horizon LLM Agents. *Proceedings of Machine Learning Research*, **306**, 55321–55375. [Primary publisher record](https://proceedings.mlr.press/v306/kang26b.html).

[4] Wu, D., Wang, H., Yu, W., Zhang, Y., Chang, K.-W. and Yu, D. (2025). LongMemEval: Benchmarking Chat Assistants on Long-Term Interactive Memory. *International Conference on Learning Representations (ICLR 2025).* [Proceedings record](https://proceedings.iclr.cc/paper_files/paper/2025/hash/d813d324dbf0598bbdc9c8e79740ed01-Abstract-Conference.html).

[5] Liu, N. F. et al. (2024). Lost in the Middle: How Language Models Use Long Contexts. *Transactions of the Association for Computational Linguistics*, **12**, 157–173. [Publisher record](https://aclanthology.org/2024.tacl-1.9/).
