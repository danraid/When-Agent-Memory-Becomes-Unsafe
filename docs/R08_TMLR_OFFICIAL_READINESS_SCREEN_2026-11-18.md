# R08 | Current official TMLR readiness and declaration audit

**Date of source check:** 18 November 2026. **TMLR is a provisional target only**, not an authorised submission destination. **Status:** factual requirements screened, manuscript and submission package NOT CLEARED.

## Verified official requirements

- [Official author guidelines](https://www.jmlr.org/tmlr/author-guide.html): double-blind submission; author identities withheld from reviewer PDF and supplementary ZIP/PDF; mandatory TMLR LaTeX style and PDF; complete active OpenReview profiles; disclosure of financial conflicts, funding and human-subject/ethics information as applicable.
- [Official submission instructions](https://www.jmlr.org/tmlr/submissions.html): required current style, no unauthorised formatting changes; submission through OpenReview.
- [Official FAQ](https://www.jmlr.org/tmlr/faq.html): generative AI usage must be transparently declared in the first-page footnote and authors remain responsible for claims, ideas and results. An agent advisory or AI model cannot count as independent human peer review.
- [Official editorial policies](https://www.jmlr.org/tmlr/editorial-policies.html): author contribution and accountability, originality, and separate identification of LLM assistance; no LLM can be listed as author.

## Actual WAMBU submission blockers

1. **Scope and contribution:** R01 naturalistic action labels not independently verified, R03 unequal-information contrasts still confounded, R04 non-discriminative sample and power assumptions still unvalidated.
2. **Comparator scope:** R02 full 200-item *author-authored public phrasing diagnostic* now executed and separately source-audited, but the full published Knowledge Triage downstream compaction/retrieval benchmarks and authors' endpoint parity are still absent. Mark the diagnostic as exploratory and source-dependent.
3. **Source and citation reliability:** R07 primary-source overlap screen exists, but full passage-level literature audit, broader coverage and independent novelty conclusion remain pending.
4. **Anonymity:** current public PR/issue and repository names are author-identifying; never link the public author-named GitHub repository in a double-blind submission. Produce a separate anonymised supplement only after inspecting for names, handles, email, organisation, DOI links and metadata leaks.
5. **Authorship/funding/conflicts:** verify true author details, exact contribution statements, affiliations, source licenses, and any applicable ethics determination; leave unknown fields unfilled until verified.
6. **Editorial validity:** final author approval and a separate, explicit external submission authorisation are absent. No pre-review upload to OpenReview, nor unapproved journal PDF claim.

## Data to obtain from author before any actual submission

- Confirm exact byline/affiliation(s), OpenReview active profile(s), corresponding author.
- Declare truthful funding, grants, employer/financial conflicts and institutional ethics oversight as applicable.
- Verify licenses of all third-party source artifacts and rights to release anonymised excerpts.
- Review and approve exact wording of first-page AI-assistance disclosure, including model-assisted experiments and AI role simulations.
- Approve journal choice and the *exact final anonymised manuscript*, then separately authorise upload to OpenReview.

## Permitted work now

Continue factual source checks, document and figure QA, repository-internal experiment logging and creation of an anonymous **candidate** package with identifying metadata removed. Do not declare any R08 gate fully satisfied by file existence or green CI alone. A final blinded submission may not be produced by merely renaming a public identified path.

**R08 verdict: PARTIAL SOURCE READINESS; not publication-ready.**
