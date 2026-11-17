# WAMBU-001 | R01/R02 evidence-qualified execution report

**Date:** 17 November 2026  
**Authority:** author-requested scientific revisions, issue #50  
**Branch:** `revision/author-decision-50-scientific-remediation`  
**Interpretation:** evidence checks and implementation completed **only for bounded documentary qualification and comparator coverage**. This does not close the scientific R01/R02 outcome requirements.

## R01 | Real task validity and action labels

The original P07d casebook comprises **8 public code-change events** from CPython and Rust. Historical P07e source-availability screening identifies **5 direct-document-topic candidates**, **3 unsuitable pairings**. The latter are explicitly disqualified from the *current supplied norm pairing*: one Rust code-change event predates the named RFC's adoption; two other Rust changes lack the necessary direct governing clause.

| Case | Public change | P07e documentary tag | R01 agent-action gold |
|---|---|---|---|
| 001 | CPython #133080 | DIRECT_POLICY_TOPIC | UNQUALIFIED |
| 002 | CPython #140345 | DIRECT_POLICY_TOPIC | UNQUALIFIED |
| 003 | CPython #130697 | DIRECT_POLICY_TOPIC | UNQUALIFIED |
| 004 | CPython #112639 | DIRECT_POLICY_TOPIC | UNQUALIFIED |
| 005 | Rust #87652 | LATER_RULE_NOT_ADOPTED_AS_OF_CASE | EXCLUDE CURRENT PAIRING |
| 006 | Rust #161002 | NONMATCHING_RULE_SCOPE | EXCLUDE CURRENT PAIRING |
| 007 | Rust #159382 | ADJACENT_BUT_NO_VERIFIED_NORMATIVE_CLAUSE | EXCLUDE CURRENT PAIRING |
| 008 | CPython #133654 | DIRECT_POLICY_TOPIC | UNQUALIFIED |

**No case is approved as operational agent-action correctness gold.** Historical source identity, policy adoption, in-force status, authority rank, exceptions, actor privileges and correct action are distinct propositions. The original P07e source history contains no adjudicated agent action. P07f simulated specialist role opinions (22/24 strict valid, six valid syntheses asking for sources) are advisory and do not close the missing authority trace. Historical GitHub merge/closure is an outcome, not normative truth. Do not add these cases to an accuracy denominator.

**Implemented:** `scripts/r01_qualify_public_policy_actions.py` gives deterministic source-matrix qualification and fails closed even when supplied an apparently complete self-attested case. The program requires independent evidence review before making any scientific correctness assertion. `tests/test_r01_r02_scientific_gates.py` includes a fabricated assertion rejection test.

**Remaining genuine dependency:** reconstruct authenticated event-time governing policy including applicable exceptions, tie to agent-visible authorisation at the decision time, verify evidence independently, and record an explicit verdict or abstention with provenance. Researcher-authored simulations may probe design but are never actual qualified human adjudications.

## R02 | Exact original Knowledge Triage comparability

The source-pinned original is `searchsim-org/cikm26-knowledge-triage` commit `a6ceb01a3368cee25ef7ebcf05ebdab8c9be24a4`, with upstream identity and licence requirements checked in the existing preflight.

| Published methodological dependency | Evidence state |
|---|---|
| Source pin and unmodified native operators | Component-level evidence |
| Original regex classification and TypeCompact | Components exercised |
| TypeDecompose and TypeRetrieve | Components exercised; article-specific lexical/scope adapters for retrieval |
| Original encoder `octen-embedding-8b` | NOT EXECUTED in the complete comparator |
| Original LLM cascade `gpt-5.4-mini` | NOT EXECUTED in the complete comparator |
| SafetyMargin | NOT EXECUTED end to end |
| Original paper retrieval datasets, budgets and scoring | NOT REPRODUCED |
| Paired downstream agent action under matched information | NOT REPRODUCED |

The preflight explicitly recognises that an available OpenRouter account or alternative embedding model **does not establish original endpoint or model identity**. The correct narrower result remains *source-pinned original component characterisation*, not full framework replication. `COMPACTION_UNSAFE` is an infeasible budget outcome and must never be recoded to successful compression.

**Implemented:** `scripts/r02_audit_original_kt_parity.py` provides a conservative method coverage matrix and refuses to promote source inspection to an executed original cascade. An offline workflow archives R01/R02 reports and tests the scientific non-promotion boundary.

**Remaining genuine dependency:** source-exact runtime identity of original embedding and LLM services; execute and archive the full original sequence on a defensible matched corpus/budget; verify original paper metric and downstream decision parity. Where external original services cannot be obtained, use an **explicitly adapted comparator** and remove the full replication claim.

## Machine-verifiable outputs

On the branch, run:

```sh
python -m unittest discover -s tests -p 'test_r01_r02_scientific_gates.py' -v
python -m scripts.r01_qualify_public_policy_actions --out runs/r01-r02/r01.json
python -m scripts.r02_audit_original_kt_parity --out runs/r01-r02/r02.json
```

The dedicated `r01-r02-scientific-gates.yml` preserves these reports as Actions evidence. Its result and artifact identity must be inspected before claiming successful remote execution.

## Final scientific state

- **R01:** `BLOCKED_NO_INDEPENDENT_ACTION_GOLD`; documentation screening and conservative validator implemented.
- **R02:** `PARTIAL_COMPONENTS_ONLY`; component provenance and exact missing-method coverage check implemented.
- **Author final approval:** WITHHELD (issue #50).
- **Preregistration and confirmatory holdout:** NOT AUTHORISED / UNTOUCHED.
- **Journal submission:** NOT AUTHORISED.

This report documents the actual bounded technical work, not a completed empirical R01/R02 milestone. An external model review or passing CI cannot silently change the status.
