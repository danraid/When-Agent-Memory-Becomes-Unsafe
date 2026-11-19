# WAMBU-001 | Complete 200-item public Knowledge Triage phrasing diagnostic

**Date:** 18 November 2026 (UTC)  
**Classification:** audited complete original-public-source **phrasing diagnostic**, NOT a reproduction of the full Knowledge Triage paper, NOT operational agent-action validation, NOT a confirmatory result.

## Immutable evidence and implementation

- **Original code and original source authored stress corpus:** [Knowledge Triage upstream](https://github.com/searchsim-org/cikm26-knowledge-triage) @ `a6ceb01a3368cee25ef7ebcf05ebdab8c9be24a4`.
- **First 40 source items:** [real run #44290963608](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/44290963608), [independent source audit #44291270040](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/44291270040).
- **Remaining 160 disjoint source items:** [real run #44396020700](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/44396020700), [artifact #14472165746](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/44396020700/artifacts/14472165746), ZIP SHA256 `57449eb51eb3ce6d41b59470f744623fd32a248da738edcaaf1f07c253e5e581`.
- **Full 200-case independent no-call audit:** [Actions #44396939218](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/44396939218), [artifact #14470461554](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/44396939218/artifacts/14470461554), ZIP SHA256 `07b88623924f5bd57ac8a37d6b21b49bae422379430a271e5644411a38e4ef25`.
- Original upstream cascade and SafetyMargin code unchanged. Authenticated model IDs: vendor Octen `octen-embedding-8b` (not the author's unpublished serving endpoint) and OpenAI `gpt-5.4-mini`.
- The 160-case run processed **160/160**, all three methods and all `SAFETY_MARGIN:` markers, **zero recorded failures**. The source hash audit reconciled 40+160 **different** IDs, each matched to the exact public upstream authored item, and reported **zero failed checks**.

## Results: source-authored constraint retention

The denominator per form is **50 original researcher-authored constraint phrasings**. This describes whether each classifier retained the source-defined constraint category. These are not independently qualified human safety judgments, agent actions, memory safety accuracy or statistical confirmation.

| Form | Original regex constraints | Original cascade (Octen + GPT) | Original SafetyMargin |
|---|---:|---:|---:|
| Imperative (n=50) | 50/50 (100%) | 50/50 (100%) | 49/50 (98%) |
| Declarative (n=50) | 0/50 (0%) | 20/50 (40%) | 46/50 (92%) |
| Conditional (n=50) | 19/50 (38%) | 50/50 (100%) | 48/50 (96%) |
| Passive (n=50) | 40/50 (80%) | 48/50 (96%) | 50/50 (100%) |
| **All source-defined items (n=200)** | **109/200 (54.5%)** | **168/200 (84%)** | **193/200 (96.5%)** |

The previously reported 40-case stratified subset had declarative cascade retention of 60%; the full 200-case source-authored corpus yields 40%. This **sampling sensitivity** illustrates why the earlier subset should not have been interpreted as a published benchmark replicate.

The outcomes expose a particularly important unclosed issue: **30 declarative source-authored constraints were not retained by the original cascade as constraints**; SafetyMargin did not retain four such declarative constraints. These observations require source/item-level qualitative review and possible replication under the original serving environment before attributing causality to model architecture.

## Exact boundaries of the result

1. The complete published **200-item adversarial phrasing dataset** has been processed; the publication's other corpora, TypeCompact, TypeDecompose, TypeRetrieve and downstream behavioral benchmarks have **not** been fully reproduced here.
2. The official Octen API exposes the model ID and 4,096-dimensional vectors but is not proven identical to the authors' `CUSTOM_LLM_ENDPOINT` serving revision, quantisation, preprocessing or runtime.
3. The same source-defined 'constraint' intent applies to all four original phrasings. **No independent operational action gold** or real retrospective policy authorization is inferred from these source labels.
4. The R01/real-agent study remains blocked, R03 matched-information comparison unexecuted and R04 prospective discriminative design unapproved. We do not compute significance or effect-size causality from this exploratory reuse of the original public source.
5. These results may be included in an explicitly labelled *reproduction/diagnostic appendix* without claims of superiority, independent adjudication, clinical applicability, or confirmation.

## Octen dependency

The published original **200-item phrasing workload no longer needs further Octen calls**, because its dataset is fully covered and independently audited. However, **R02 as a whole still requires Octen** if original-model-ID classification/retrieval is used in the remaining source-matched corpus, retrieval/compaction, budget and downstream comparator experiments. No author decision was made to drop that broader comparator; therefore do not recommend disabling Octen yet.

The one-shot paid push trigger was removed from `.github/workflows/r02-original-remaining-160.yml`. Future paid workflows require a separately bounded manual execution; no background paid loop was initiated. The previously configured daily condition-watch will notify the author when no approved remaining work depends on Octen.

**Author final approval remains withheld; confirmatory holdout and external journal submission remain blocked.**
