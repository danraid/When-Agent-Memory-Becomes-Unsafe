# Experimental engine v0.3.0: bounded GPT decision tasks

## Terminal state and scope

The hub can generate controlled synthetic policy/ledger episodes, execute **actual GPT decisions** only when the author has explicitly configured model, pricing, limits and API key, and compare five paired conditions. The reference judge runs outside the prompts. Every run stores per-case prompts, raw model responses, reference labels, deterministic evaluations, hashes and descriptive statistics. No manuscript is thereby publication-ready.

## Experimental interventions and baselines

- `full_history`: complete policy and preceding requests (costly reference baseline).
- `window_only`: initial policy appears only at the first step; after that the last two requests remain.
- `structured_memory`: concise pinned policy plus last two requests.
- `structured_memory_ablated`: identical memory layout but policy constraints omitted (information ablation).
- `structured_memory_with_guard`: pinned policy plus deterministic guard, where the **final system action** may be overridden. Report raw model behaviour and final system safety **separately**.

This is a narrow *synthetic access-policy benchmark*, not a demonstration of performance on real deployed agents. The fixed oracle world state ensures identical context per condition and avoids hidden feedback loops. This is deliberate control, not a simulation of every production system.

## Offline test

```sh
python -m unittest discover -s tests -v
python scripts/hub.py empirical --mode mock --split development --episodes 2 --steps 7 --output runs/mock-test
python scripts/hub.py verify --directory runs/mock-test
python scripts/hub.py freeze-proposal --output runs/freeze-proposal.json
```

`mock` always approves and is **never** counted as real GPT observations.

## Real pilot / development only (explicit paid opt-in)

1. Generate an independent paper repo. Choose a specific model and set accurate **input and output price rates** in `paper.json`, enable the API, and bound tokens/USD/calls. Configure `OPENAI_API_KEY` as a GitHub secret.
2. Run an instrument test in `development` with `--mode live --execute --episodes 2 --steps 7`. The 5 conditions require 70 API calls for 2 episodes x 7 steps.
3. Verify the produced manifest and examine raw responses, invalid JSON rate, safety overrides and potential ceiling effects. Revise *exploratory* design as necessary; do not select after seeing confirmatory outcomes.
4. For `pilot`, use `--split pilot --mode live --execute`; pilot uses a different public development seed and its results remain exploratory.

The budget ledger reserves worst-case cost **within one serial job** and is not an organisation-wide spending monitor. Separate workflow dispatches are new budgets. Set provider-side usage limits too.

## Confirmatory gate

A `confirmatory` execution is blocked unless all hold: (a) model calls enabled and explicit `--execute`, (b) protocol hash matches an author-maintained `FROZEN_BY_AUTHOR` lock, (c) deterministic judge source hash matches the lock, (d) separately recorded author approval names that same protocol hash, (e) a private, distinct holdout seed with >=32 characters arrives only through `HUB_HOLDOUT_SEED`, and (f) per-job preflight budget covers planned calls. The CLI **never** generates human approval. `freeze-proposal` emits hashes only for the author to review. Approval JSON alone is a recorded declaration and not cryptographic identity verification; protect the branch and require human PR review.

Results are not automatically promoted in research_state.json. Scores and 95% intervals are descriptive. For confirmatory inference, group observations by *episode*, apply the declared analysis plan and account for multiple testing. If the frozen protocol is incomplete, **do not use confirmatory mode**.

## Explicit limitations

No real GPT trials were paid for during hub validation. The baseline `window_only` is a truncation baseline, not a learned summarizer. The independent judge is a separate deterministic function, not an external human peer reviewer. Review journal requirements separately and avoid promoting synthetic outcomes to scientific evidence.
