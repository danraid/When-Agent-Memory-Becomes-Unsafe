# Development-only repair audit and submission decision

**Status: four ambiguities repaired in versioned synthetic casebook v2; not independently human validated.**

The original 16-case v1 is retained unchanged. The new [v2 casebook](../fixtures/synthetic_human_review_casebook_v2.json) repairs the four cases identified in the author's conditional approval:

| Case | Defect in v1 | Explicit v2 repair | Editorial expectation (not independent gold) |
| --- | --- | --- | --- |
| SYN-DEV-005 | Region-north permission incorrectly marked as region-south and as superseding a south restriction | e2 scope corrected to north; removed invalid supersession; defined scope-matching rule | South prohibition remains applicable |
| SYN-DEV-010 | Same-day conflict lacked precedence | Later directive dated 2 May, decision 3 May, explicit supersession retained | Permission applies |
| SYN-DEV-015 | Grant and revocation conflated into one event | Separated grant (e2) and subsequent revocation (e3), with explicit timing | Sharing remains prohibited |
| SYN-DEV-016 | Unclear rule-making authority | Explicitly designated Team Office as policy authority and removed invalid committee supersession | Original prohibition remains |

**Author decision:** the previously recorded approval was conditional on corrections. These changes satisfy the *specified textual repairs* as an engineering check. They do not imply the author personally inspected or unconditionally signed off v2. The author review remains **CONDITIONAL, AWAITING V2 SIGN-OFF**. The prior fictional reviewers' labels and 14/16 agreement apply only to **v1**, and must not be silently carried over as a v2 review.

## Publication boundary

The existing [negative-results journal manuscript](../manuscript/JOURNAL_NEGATIVE_RESULTS_ANONYMOUS_DRAFT_EN_GB.md) is the active evidence-bearing draft. The 16 synthetic cases are **post-hoc development instruments**, not external validation, independent human review or confirmatory evidence. No new GPT evaluation of v2 has occurred in this repair. No target journal or article type is confirmed, author declarations are outstanding, no official-format PDF is verified, and no submission receipt exists.

**Current terminal state:** `DEVELOPMENT_FIXTURES_REPAIRED; SCIENTIFIC_REVIEW_PENDING; JOURNAL_SUBMISSION_BLOCKED`.

For a defensible submission, obtain authentic independent review or clearly position the paper as exploratory methodological negative-results research without claiming it, resolve novelty and source comparators, verify declarations and permissions, freeze manuscript/code/data with a reproducibility package, select an appropriate indexed journal and comply with its actual instructions. Author sign-off on the exact submission version is also required.
