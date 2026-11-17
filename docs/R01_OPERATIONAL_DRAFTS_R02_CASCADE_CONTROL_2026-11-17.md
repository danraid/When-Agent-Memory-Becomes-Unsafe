# WAMBU-001 | R01 operational task drafts and R02 original cascade control-flow audit

**17 November 2026.** Bounded continuation of GitHub issue #50 and draft PR #51.

## R01 outcome

Three source-backed *development task drafts* were added to [the segregated task packet](../fixtures/R01_SOURCE_BACKED_OPERATIONAL_TASK_DRAFTS_V1.json):

1. CPython #133080: evaluate the very narrow two-interface exception explicitly documented by the Steering Council before PR creation, with original source timestamps.
2. CPython #140345: analyse a request to introduce runtime deprecation warnings rather than immediately remove certain AST classes, with original issue creation before PR creation.
3. CPython #133654: analyse a proposed C-API variable removal while distinguishing deprecation from explicit pending-removal status.

**Each draft has `correct_action=null` and `independent_adjudication_status=NOT_DONE`.** These are operational questions, not validated answers. A scenario referring to an approval is not proof that a particular agent has all required information to decide safely. The draft includes only source references known to precede the specified event timestamp; original issue body text may have changed, so it must not be assumed to be an immutable historic version. The [task tests](../tests/test_r01_operational_task_drafts.py) fail when sources are future-dated or when the packet exposes reference-label fields.

**Scientific consequence:** the benchmark is better specified for development. However, R01 remains blocked from operational accuracy scoring without independent source-grounded action adjudication; no agent accuracy rates or human adjudications have been created.

## R02 outcome

Source inspection of the original upstream [classifier cascade](https://github.com/searchsim-org/cikm26-knowledge-triage/blob/a6ceb01a3368cee25ef7ebcf05ebdab8c9be24a4/knowledge_triage/classifier_cascade.py) confirms four ordered gates: regex classification; prototype-embedding encoder; GPT adjudicator on low confidence; and conservative abstention as a constraint for very-low-confidence unresolved items.

A new [offline cascade execution harness](../scripts/r02_execute_upstream_cascade_stubbed.py) calls the original `CascadeClassifier.predict` without editing its source, using explicitly stubbed encoder and LLM responses to exercise five branches: regex short-circuit, confident encoder, LLM adjudication, abstain-as-hard and no-LLM fallback. A GitHub Actions task checks out the fixed upstream commit and records the original source SHA256.

This **is not the published runtime**. An encoder stub is not `octen-embedding-8b`, an LLM stub is not `gpt-5.4-mini`, and neither the published classifier accuracy nor safety benefit can be estimated from these branch tests. The upstream original SafetyMargin and the complete original retrieval/budget benchmark also remain unexecuted.

**Acceptance:** only call this `ORIGINAL_CASCADE_CONTROL_FLOW_WITH_DETERMINISTIC_STUBS` after verifying the dedicated workflow output. The classification `FULL_ORIGINAL_KNOWLEDGE_TRIAGE_REPRODUCED` is forbidden.

## Unchanged scientific authority

- Original paid experiments, adverse/null findings, and failure records are not changed.
- Confirmatory holdout remains untouched.
- No model service keys or paid inference are used by this scope.
- No author final approval or external journal submission has occurred.
