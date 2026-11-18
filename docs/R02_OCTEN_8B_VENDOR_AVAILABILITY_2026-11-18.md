# WAMBU R02 | Octen-Embedding-8B availability and integration

**Research status:** Code integration implemented and offline contracts tested. **External credential/provisioning NOT verified.** Scientific author decision #50 unchanged.

## Primary vendor documentation

The [official Octen Embedding API](https://docs.octen.ai/api-reference/embedding) documents:
- `POST https://api.octen.ai/embedding` with a Bearer API key, or `x-api-key`;
- `model: octen-embedding-8b`, `dimension: 4096`;
- `input_type: document`, which does not inject the extra query instruction;
- JSON `code: 0`, `data.model`, and indexed `data.results[].embedding`;
- paid service provisioning: **a payment method is required** for API use.

The model's openly distributed weights may also be obtained from [Hugging Face](https://huggingface.co/Octen/Octen-Embedding-8B), subject to model-card constraints and local hardware capacity. Hosting the weights independently would constitute a different serving deployment and must be recorded separately.

## Integration implemented in PR #51

- [`scripts/r02_octen_vendor_embedding_bridge.py`](../scripts/r02_octen_vendor_embedding_bridge.py): an authenticated API client translates the vendor's documented response into the OpenAI-compatible object used by the **unmodified** original `EncoderClassifier.fit/predict`. It validates `data.model`, number/order of results, the original 4096 dimensions and finite floats. Credentials, request text and embeddings are not logged.
- [`scripts/r02_execute_live_cascade.py`](../scripts/r02_execute_live_cascade.py): prioritises the original authors' exact endpoint/key when configured; next the **Octen vendor model ID with original LLM**; otherwise clearly labelled adapted OpenRouter models. The vendor lane is named `OCTEN_VENDOR_AND_ORIGINAL_LLM`.
- [`tests/test_r02_octen_vendor_embedding_bridge.py`](../tests/test_r02_octen_vendor_embedding_bridge.py) tests valid vendor response, wrong model, truncated embedding, invalid indexes, non-finite vectors, safe transport construction and missing key.
- [`.github/workflows/r02-octen-vendor-bridge-ci.yml`](../.github/workflows/r02-octen-vendor-bridge-ci.yml): deterministic tests **without network or paid inference**.
- [`.github/workflows/r02-live-cascade-development.yml`](../.github/workflows/r02-live-cascade-development.yml): accepts `secrets.OCTEN_API_KEY`, `secrets.OPENAI_API_KEY`; manual workflow dispatch only, to prevent unintended expenditure.

## Exact steps to provide access

1. Obtain the vendor's own Octen account/API key with an active payment method. Official documentation calls this an API Bearer token.
2. In GitHub repository Settings → Secrets and variables → Actions, create **repository secret** `OCTEN_API_KEY`. Do not put its value in a PR, issue, log, fixture or chat.
3. Ensure the existing repository secret `OPENAI_API_KEY` has access to the original `gpt-5.4-mini` model. Key presence does **not** imply model entitlement.
4. Once the secret is installed, manually run **Actions → Article 1 | R02 one-shot live cascade development attempt → Run workflow** on `revision/author-decision-50-scientific-remediation`. This workflow attempts the vendor lane only after the authors' `CUSTOM_LLM_API_KEY` and `CUSTOM_LLM_ENDPOINT` lane, if present. The adapted lane is a separate fallback.
5. Inspect the archived `cascade_live_report.json` for `result.lane`, the actual model IDs, errors and `source_vs_method_parity`. If the vendor is unavailable (invalid key, balance, rate limit), do not report original-model execution.

## Methodological boundary

Identical **model identifiers** on the vendor endpoint and the published upstream experiment do not, without further evidence, demonstrate identical serving revision, prompt preprocessing, quantisation or full-paper methodological parity. The original model-ID vendor lane is **NOT** the author's original `CUSTOM_LLM_ENDPOINT`. The original paper's corpus, budgets, SafetyMargin and downstream agent-task comparisons are still separate requirements.

**Current verified outcome:** earlier live OpenRouter-adapted cascade works (run #44228839055); the Octen vendor bridge code is prepared. **No authenticated Octen API call or Octen vendor embedding inference has been verified in this work package.** No protected holdout, author final approval or external journal submission.
