# WAMBU R03 | Real common-authority-source pilot, two paired episodes

**Date:** 19 November 2026 UTC. **Scientific label:** exploratory development, non-causal. **Author approval:** withheld by issue #50.

## Implementation and primary evidence

- [Real development workflow #44499126116](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/44499126116) **PASS**, [artifact #14516607397](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/44499126116/artifacts/14516607397), ZIP SHA-256 `0c442bc9682610d6bb81ea82fe23220063a15884152deacdec6836e1d8ed61c5`.
- [Independent detached source-and-sidecar replay #44499598557](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/44499598557) **PASS**, [artifact #14516338371](https://github.com/danraid/When-Agent-Memory-Becomes-Unsafe/actions/runs/44499598557/artifacts/14516338371), ZIP SHA-256 `0a14dd3468cc7fdf0a447691bb3958c93ca7767fd8cbcd9f136017e89f7be570`.
- [Protocol](../protocol/R03_SHARED_AUTHORITY_SOURCE_DEVELOPMENT_V1.json); [real runner](../scripts/r03_common_authority_live_dev.py); [replay verifier](../scripts/audit_r03_shared_authority_dev.py); [negative tests](../tests/test_r03_common_authority.py).
- Two independently seeded public development episodes, 18 decision steps per episode, two paid model arms, 10 separate recursive compaction requests. **82 original provider calls, 72 model decisions and 10 compactions**, with provider IDs recorded and no duplicate response IDs.

## Design and exact scientific boundary

The *same* unmodified authoritative initial policy and amendments, extracted only from the public event stream, were inserted into **both** agent prompts on each paired turn. The request and instruction were also identical.

- **Arm A:** recursive summary representation plus the common source packet.
- **Arm B:** deterministic version-aware policy ledger derived **only from that same packet**, plus the identical source packet.

This eliminates the previous unfair advantage whereby the ledger obtained an externally supplied current-policy state *unavailable from the other arm's inputs*. It does **not** equalise computation, representation, context length, rendering or total cognitive advantage. The ledger computes an active state using deterministic parsing; the summary arm must reason over source and summary. The comparison therefore remains systems-level, exploratory and **not causal memory-architecture inference**.

Gold reference policy and target action remained in an evaluator-sidecar after model outputs. Source hashes and paired observations were independently reconstructed without additional paid calls. All results are synthetic, with no genuine external action gold or R01 qualified event-time cases.

## Observed results

| Indicator | Recursive summary + same authority | Derived ledger + same authority |
|---|---:|---:|
| Raw correct decisions | **36 / 36** | **36 / 36** |
| Invalid responses | 0 | 0 |
| Eligible revocation probes | 8 | 8 |
| Revocation errors | 0 | 0 |
| Newly active restriction probes | 8 | 8 |
| Missed new restrictions | 0 | 0 |
| Model input tokens across decision calls | 14,218 | 8,542 |

The source-identical pilot again displayed a **complete accuracy ceiling and zero observed difference**. Arm A consumed 5,676 more input tokens in model-decision requests, about **66.4% more than the ledger arm** (the difference describes these measured inputs, not matched budgets or end-to-end cost). There is no statistical evidence of method equivalence, safety gain or treatment superiority from two episodes.

**R03 terminal verdict:** `PARTIAL`. A genuine matched-authoritative-source access development run and detached replay were completed, but **context budgets and representation complexity remain non-matched**, and the instrument lacks a discriminative signal. Any new confirmatory causal hypothesis must be designed prospectively rather than inferred from these saturated observations.

## Next bounded scientific work

Use source-qualified real tasks and non-ceiling development probes to design an equitable representation and budget comparison with per-arm source visibility, compaction count and tokens measured. Keep source and reference labels separate. Do not use the protected holdout or automatically rerun large paid studies on saturated prompts.

The one-shot paid push trigger was removed after the successful execution; manual workflow dispatch remains available. **Octen was not used or needed by this R03 pilot.** R02 original-model full framework is a separate unfinished dependency.

**No author sign-off, confirmation or external submission.**
