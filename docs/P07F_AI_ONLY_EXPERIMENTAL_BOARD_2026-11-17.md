# P07f | AI-only experimental specialist board and final human-author decision

**Protocol amendment:** [P07F_AI_REVIEW_AUTHOR_SIGNOFF_AMENDMENT_2026-11-17.md](../protocol/P07F_AI_REVIEW_AUTHOR_SIGNOFF_AMENDMENT_2026-11-17.md). This is the explicitly requested **AI-only replacement of internal specialist review roles**, with one real human reserved for final approval: the author.

## Four specialist functions, three first-round model vendors

| Function | Model | Output |
|---|---|---|
| Causal experiment and estimand design | GPT-4.1 Mini | Unit of analysis, confounding, baseline and causal construct adequacy |
| Temporal authority and provenance | Gemini 2.5 Flash | Time of rule availability versus actual governing authority, conflicts and exclusions |
| Benchmark integrity and replicability | Claude Haiku 4.5 | Leakage, case selection bias, ground-truth meaning, matched-data fairness |
| Adversarial synthesis | GPT-4.1 Mini | Same-case three-review disagreement, new source request and author-facing recommendation |

The fourth role is a **synthesiser**, not a fourth independent model or human. Models do not impersonate actual qualified humans or journal reviewers. Each of the first three is blind to other reviewers' replies, the original P07d model panel, previous analyst selection decisions and observed GitHub merge/close outcomes.

## Actual study cases

All eight P07d PR code-change cases are reviewed, **including the three previously screened out**. Original real source evidence is drawn exclusively from original P07d GitHub Actions artifact `14281751027` and P07e event-time qualification artifact `14323695846`. Source and case hashes are verified before processing; each reviewer receives only source-pinned historical normative excerpts and actual retrospective patch evidence, not the evaluator labels or analyst exclusion flags.

First-round reviews require strict JSON, a cited evidence ID, an exact quoted substring, an explicit decision (`include_development_probe`, `exclude_current_policy_pairing` or `needs_additional_source`), source-integrity concerns and an explicit declaration that no human gold is established. Invalid and missing model outputs are retained and reported. Synthesis is skipped for cases missing a first-round role vote instead of filling it by assumption. At most 24 + 8 paid requests, with finite 34 reservations and no automated retries.

## Authority and terminal states

The AI board may recommend case eligibility for **exploratory software-governance or agent-memory research**, not correctness of any historical PR or unsafe authorisation ground truth. This cannot satisfy the existing P07/P10 criterion if the claim explicitly requires **external independent qualified human adjudication**. Such scientific claims must be withdrawn or the research question re-scoped, with the previous frozen criterion retained in version history. An author's approval of AI-assisted analysis is not retrospective evidence of other real humans reviewing the cases.

The final author will explicitly examine original source hashes, case exclusions, all independent model statements, dissent and invalid outputs, exact protocol and manuscript before deciding to approve, reject or request changes. `AUTHOR_APPROVAL_PENDING` is the default for all runs, including unanimous AI opinions. No AI may sign off a scientific protocol freeze, authorise the confirmatory holdout, publish or submit to a journal on behalf of the author.

## Reproducibility tests

- Eight of eight cases are preserved, even when previous analyst exclusions exist.
- No original GitHub outcome or previous AI adjudication is visible to first-round reviewers.
- Every role is separately assigned a predeclared model, prompt SHA-256 and provider response ID.
- Every valid review includes an exact quote from the cited source evidence.
- Invalid provider output is archived without rewrite.
- The detached audit reproduces classifications from original model responses with **zero** new requests.
- `human_adjudicators == 0`, `scientifically_approved == false`, `author_approval == PENDING`, `holdout_touched == false`.

**Status at authoring:** code and one-shot CI prepared; actual conclusions depend on successful observed GitHub Actions and its archived output. Do not interpret code presence as complete AI assessment.
