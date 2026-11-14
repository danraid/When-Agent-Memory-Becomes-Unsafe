# Study implementation | NOT a general-purpose benchmark

- `tasks.py`: deterministic synthetic episodes with authorised amendments, no prior decisions in history.
- `prompts.py`: full history, short window, recursive GPT summary, and pinned ledger prompts. No hidden reference labels.
- `runner.py`: real opt-in GPT compactions, four independent paid decision calls per step, plus derived safety guard; SHA256 evidence manifests.
- `analysis.py`: strict deterministic JSON evaluator and descriptives; no automatic significance tests.
- `review.py`: two inexpensive model advisory reviews, without gold labels; not independent scholarly review.
- `model_config.json` and `reviewer_config.json`: no USD ceiling, but finite calls and token bounds; no credentials stored.

The source hub's static context-memory benchmark is retained under `article_hub/` solely for reusable infrastructure, not as article evidence.
