# P07f v2 amendment | Source-ID evidence validation for simulated AI specialists

**17 November 2026. New exploratory version 2.0.0, not a repair or rescore of prior inference.**

## Why v2 is required

The original P07f run [#44076185311](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/44076185311) produced 24 provider responses but only **4/24** passed the strict original schema. Most failed because a model attempted to reproduce source snippets that were not identical byte-for-byte to the evidence; 2 replies also failed the single-JSON requirement. All 24 responses and **zero** syntheses were preserved. The detached audit succeeded and retains the original outcome, which remains `AI_ONLY_PANEL_PARTIAL_PENDING_AUTHOR_REVIEW`.

## Different, prospectively defined v2 measurement contract

Each reviewer must select **one unique source evidence ID** rather than transcribing a quotation. The verifier rejects IDs not present in that same case's original blind evidence and *deterministically* appends a literal source excerpt and SHA-256 from that source ID, with `quote_origin=EXACT_VERBATIM_SOURCE_ID_LOOKUP_NOT_LLM_GENERATED`. This avoids incorrectly presenting an LLM paraphrase as a direct quote without relaxing independent source identity validation. Evidence selection, not copy-and-paste quality, is tested. Models still return structured decisions, rationale, enumerated risk flags and explicit denials of human expertise/human reference gold.

This is a **new exploratory observation**, not a retroactive overwrite, reinterpretation, scientific approval, or preregistered confirmatory repair of v1. Comparisons of output coverage across v1 and v2 are *engineering-validity evidence*, not evidence of better epistemic accuracy or policy-compliance correctness. The original v1 denominator and failed outputs must always be included in any methods report.

The reviewer receives the exact same verified outcome-blind source-data artifact from v1, so no historical GitHub merged/unmerged labels or earlier analyst P07e tag enters first-round prompts. Three distinct model vendors provide role-specific AI reviews. Synthesis is withheld if a role fails. At most 24+8 calls in a single nonretrying request matrix, capped at 34 pre-request reservations. A separate zero-call audit reconstructs the selected evidence quotes, verifies hashes, prompt identities and per-case synthesis, and forbids scientific or author approval.

**Final authority:** the author's explicit separate later evaluation of the actual evidence and manuscript, not automatic consensus. No independent actual human experts are claimed, no clinical/policy authorisation gold is inferred, no protected confirmatory dataset is opened, and journal submission stays controlled by the author.
