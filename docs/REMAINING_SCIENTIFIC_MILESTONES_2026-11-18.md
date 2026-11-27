# WAMBU-001 | Remaining scientific milestones after author major-revision decision

**Status date:** 2026-11-18. **Source:** issue #50, author review decision: **MAJOR_REVISIONS_REQUESTED**, no additional comments. **PR:** #51 (draft, not merged). This is an execution ledger, not a claim that a test passed or a journal submission occurred.

## Scientific completion gates, ordered by prerequisites

| Gate | Work required | Independent acceptance evidence | Current state |
|---|---|---|---|
| R01 | Source-qualified real operational tasks | Reconstructed event-time policy revisions; actor permissions and exceptions; independent source reviewer evidence; safe action/abstention verdicts and provenance without downstream model access | BLOCKED: 0 qualified agent-action gold; one documented Steering Council exception; other issue/PR chronologies are evidence leads |
| R02A | Full 200-item public source-authored adversarial classifier/SafetyMargin benchmark | 40 original public source items + 160 disjoint original public items, each with original source hash, 3 method outputs, exact model IDs and independent offline source replay; preserve errors | IN PROGRESS; 40 audited, 160 GitHub Actions run #44396020700 launched |
| R02B | Full original-method comparator parity | Published TypeCompact/Decompose/Retrieve/SafetyMargin native constraints, original paper corpora, matched budgets and evaluation; precise model service versions and original endpoint differences; source-pinned evidence | PARTIAL: original components and vendor model IDs executed, authors' exact server parity unverified |
| R03 | Matched-information arm comparison | One frozen event stream; per-decision allowed source set and effective times equal across arms; identical base model and token budget or measured deviations; all evaluator gold restricted to sealed sidecar | OPEN; existing current-policy ledger got privileged state, so earlier systems comparisons cannot isolate architecture |
| R04 | Discriminative independent episodes and valid uncertainty | Non-ceiling dev episodes with explicit revocation + new enforcement, episode-level paired variance/power sensitivity, predeclared estimand/exclusions/missingness/multiplicity, no peeking into confirmatory holdout | OPEN; preliminary n=32 estimate assumes sigma=.20 and delta=.10, not evidence of real power |
| R05 | Source-valid AI specialist methodology board | Existing v1/v2 missingness (22/24 first-round valid, 6/8 syntheses) retained; evidence-first replay and JSON validation; disagreements and vetoes reported; distinguish AI specialists from human reviewers | PARTIAL; invalid original reviews cannot be promoted |
| R06 | Temporal authority/provenance | Applicable policy adopted at the decision date; immutable rules and exceptions, issuer and actor scope, precise Git/blob identities, edits and time-leakage audit | PARTIAL; public PR merge and closure never imply policy ground truth |
| R07 | Originality and literature claim audit | Claim-by-claim anchored overlap with Knowledge Triage, Supersede, ACON, LongMemEval; complete method-level primary reading, no unsupported superiority or 'first-of-kind' language | OPEN; negative methodology/reproducibility path is safer until novelty demonstrated |
| R08 | Indexed journal readiness | Full citations; documented ethical/licensing decisions; verified author/funding/conflicts/AI disclosures; anonymous source and figure package; current TMLR style and declared target journal | OPEN; author facts may not be invented |

## Publication-stage gates (not subsumed by R01–R08)

1. **New AI-board developmental review:** report PASS/PARTIAL/FAIL and source-linked objections, with no imaginary human scientific peer review.
2. **New author final scientific decision:** the present decision is **corrections required**, not approval.
3. **Confirmatory study if desired:** requires separately approved frozen protocol and protected sample release; no authority for it in the author instruction to carry on.
4. **External journal submission:** another explicit, later author decision approving the exact final manuscript and submission action. No CI test or AI approval can waive this.

## Source-aligned R02 run and integrity

- Archived 40-item original authors' public subset: run #44290963608; independent audit #44291270040.
- Remaining 160 original source items: scoped run #44396020700; report checkpoints each item and marks any failed provider call.
- Source reconciliation: `scripts/audit_r02_complete_public_200.py` and `.github/workflows/r02-public-200-detached.yml`, requiring exactly 200 disjoint source-hash-matched entries.
- All paid source-input workflows are intended to return to **manual dispatch** after a one-shot run. A PASS on CI only means the bounded result is structurally reproducible; it is not a scientifically independent action benchmark.

## When Octen can be discontinued

Do **not** recommend account cancellation or removal of the credential while future approved original-model-ID experiments (particularly source-matched real retrieval/compaction and budget parity) still require Octen and have no documented replacement. Once all Octen-dependent approved runs are archived, their provenance is verified offline and no further Octen input is required for the chosen paper scope, notify the author that the service can be disabled; do not remove the secret yourself. A daily conditional notice automation was explicitly created for this purpose.

## Immutable scientific rules

No retrospective label leakage; no invented policy action gold; no reinterpretation of `COMPACTION_UNSAFE` as success; no pooling disjoint pilot episodes as independent replications; no unqualified endpoint parity; no provider errors hidden as successful abstentions; no invalidated AI-review votes counted; no confirmatory holdout access or external submission before independent author decisions.
