# WAMBU R02 | Verified authenticated Octen vendor cascade run

**Run:** [GitHub Actions #44283862849](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/44283862849)  
**UTC:** 2026-11-18 10:17:08  
**Artifact:** [#14417833602](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/44283862849/artifacts/14417833602)  
**ZIP SHA256:** `5638eef9302bdb38fe7448ff79aa58c7c4510aa4fdb97309e4b0c4e40989a43a`  
**Original upstream commit:** `a6ceb01a3368cee25ef7ebcf05ebdab8c9be24a4`  
**Original unmodified classifier SHA256:** `ab2f236cbede0b1b4b69be07ec4a3519de1603f2a3041919563aea2b410b8b52`

## Verified technical result

The one-shot original-model-ID vendor route returned **`REAL_CASCADE_COMPLETE`**, with **`OCTEN_VENDOR_AND_ORIGINAL_LLM:SUCCESS`**. The restricted execution used the [Octen API bridge](../scripts/r02_octen_vendor_embedding_bridge.py), requesting the **Octen vendor model `octen-embedding-8b`** and the original paper's **`gpt-5.4-mini`** identifier from OpenAI. Neither the original authors' `CUSTOM_LLM_ENDPOINT` nor their `CUSTOM_LLM_API_KEY` was provisioned. This is **original model IDs on a vendor endpoint, not proof of original author endpoint parity**.

There was exactly one successful lane. `R02_REQUIRE_LANE=OCTEN_VENDOR_AND_ORIGINAL_LLM` prevented fallback to adapted OpenRouter models, despite an OpenRouter key being present. Source-controlled original cascade and encoder logic were not altered.

| Development stimulus ID | Observed decision stage | Returned type | Confidence | Abstained |
|---|---|---|---:|---|
| regex | regex | constraint | 0.950000 | No |
| encoder | llm | belief | 0.567502 | No |
| uncertain | llm | belief | 0.583677 | No |

The `encoder` stimulus **was adjudicated by an LLM**, not independently classified in the encoder lane. Two of three inputs reached the real LLM. No forced escalation parameter was used. The recorded number of provider requests is a lower bound of nine, not an externally reconciled billing count.

All model texts were artificial, public development probes. The record has **no reference labels**, **no human adjudication**, **no untouched holdout access**, and **no confirmatory sample use**.

## Scientific scope and qualification

**New established result:** Octen vendor endpoint authentication worked, the original embedding model ID returned a supported response checked by the strict 4096-dimension adapter, and the original LLM model identifier completed two adjudications using upstream Python `CascadeClassifier` logic.

**Not established:** identity with the authors' `CUSTOM_LLM_ENDPOINT` deployment, their serving revision and preprocessing; full method corpus/budgets; SafetyMargin execution; published benchmark accuracy; causal or inferential memory-safety result; scientific approval. The report explicitly marks `full_original_knowledge_triage_replication=false`.

**R02 remains PARTIAL**, but the specific original-model-ID dependency has now been exercised on the vendor API. R01 source-grounded operational action gold remains unavailable.

## Reproducibility and protected actions

The exact one-time run used [`protocol/R02_OCTEN_ONE_SHOT_TRIGGER_2026-11-18.json`](../protocol/R02_OCTEN_ONE_SHOT_TRIGGER_2026-11-18.json). Following the run, [`r02-live-cascade-development.yml`](../.github/workflows/r02-live-cascade-development.yml) was restored to **manual dispatch only**, retaining the forced Octen lane for future bounded tests, to avoid automatic paid reruns.

Author approval, confirmatory holdout, frozen preregistration and external journal submission are all **still separately withheld** under [issue #50](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/issues/50).
