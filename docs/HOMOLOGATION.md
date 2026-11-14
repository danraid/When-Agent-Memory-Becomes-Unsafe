# Hub engineering homologation: actual GPT API observations

## Objective and terminal state

After local deterministic tests pass, execute **exactly one bounded development-split trial** (2 episodes x 5 steps x 5 paired conditions = 50 genuine GPT responses), then two genuinely requested low-cost blind methodological reviews, validate all evidence, and record `ENGINEERING_HOMOLOGATED`. A mere successful GitHub job is insufficient: the real-provider IDs, API token counts, evidence hashes, pairing, deterministic outcome labels and review traces must be present.

## Actual models

- Experimental actor: `gpt-6.1-terra` (OpenAI Responses API).
- Cheap blind advisory reviewer: `gpt-6-luna`, two separate prompts covering JSON format and context-related methodological risks.
- Ground-truth reference: deterministic Python evaluator, not an LLM or a copied answer key in prompts.

See current provider documentation for availability and price. The code's per-million-token estimates are **informational, not a provider billing record**.

## No monetary ceiling, but finite workload

`api.budget.max_usd=null` explicitly disables the USD preflight cap for the live homologation. This is not unlimited autonomous spend: 50 primary requests and 2 reviewers are predefined. Input/output-token and call-count ceilings protect against runaway retries, excessive context or infinite workflows. The workflow triggers automatically only when the specific homologation workflow file changes, or when manually dispatched; there is no schedule and it writes no code or branches after running.

## Process

1. Set `OPENAI_API_KEY` as a GitHub Actions **repository secret**. It must be valid for `gpt-6.1-terra` and `gpt-6-luna`.
2. Run the complete deterministic unit test suite.
3. Execute a finite real-agent development trial, storing observed prompts, model answers, provider response IDs and usage.
4. Calculate reference outcomes with the independent deterministic evaluator.
5. Run two blind advisory GPT-6 Luna reviews with no supplied reference labels.
6. Validate exactly paired observations, unique provider IDs, token usage and reviewers. Write a hashed evidence manifest.
7. Report `ENGINEERING_HOMOLOGATED` only on successful observed evidence, otherwise retain an error or `BLOCKED_*` status.

Evidence is available as a GitHub Actions artifact named `hub-real-provider-homologation-<run_id>`. Nothing is written to confirmatory data, frozen scientific protocols, publication status or a new Article 1 repository. The run does **not** claim scientific novelty, third-party validation or journal submission readiness.

## Scope of the word *homologated*

This is **engineering homologation of the API experiment machinery**, not scientific confirmation of a particular hypothesis, independent human peer review, or author permission to publish. Article-specific exploratory/confirmatory protocols must still be registered and approved independently.

## Failure handling

If the GitHub secret is unavailable, save `preflight.json` with `BLOCKED_OPENAI_API_KEY_NOT_CONFIGURED`; do not create false provider observations. If the provider fails, do not relabel partial results as PASS. A bounded manual re-run can be carried out after fixing the environment or a demonstrated engineering defect.
