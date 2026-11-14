# P07b | Real public supersession documents: provenance-only gate

This work separates **real externally authored source documents** from **real independently human-adjudicated authority-conflict cases**. Only the former is implemented.

## Six independently published document pairs

The [machine-readable candidate manifest](../protocol/P07_PUBLIC_SOURCE_CANDIDATES.json) pins original GitHub commits and blob SHA-1 identifiers. The [verifier](../scripts/verify_p07_public_sources.py) checks actual source and target text at exact pinned revisions with `git show`, records SHA-256 and checks explicit supersession relationships.

- [PEP 5](https://github.com/python/peps/blob/5595f77d7d9cdddae99d4510b145df2496a9c891/peps/pep-0005.rst) -> [PEP 387](https://github.com/python/peps/blob/5595f77d7d9cdddae99d4510b145df2496a9c891/peps/pep-0387.rst)
- [PEP 291](https://github.com/python/peps/blob/5595f77d7d9cdddae99d4510b145df2496a9c891/peps/pep-0291.rst) -> PEP 387
- [PEP 215](https://github.com/python/peps/blob/5595f77d7d9cdddae99d4510b145df2496a9c891/peps/pep-0215.rst) -> [PEP 292](https://github.com/python/peps/blob/5595f77d7d9cdddae99d4510b145df2496a9c891/peps/pep-0292.rst)
- [PEP 631](https://github.com/python/peps/blob/5595f77d7d9cdddae99d4510b145df2496a9c891/peps/pep-0631.rst) -> [PEP 621](https://github.com/python/peps/blob/5595f77d7d9cdddae99d4510b145df2496a9c891/peps/pep-0621.rst)
- [Rust RFC 1201](https://github.com/rust-lang/rfcs/blob/f43d5789b838fb0d80962e3d4b45fb9ddfcc9a07/text/1201-naked-fns.md) -> [RFC 2972](https://github.com/rust-lang/rfcs/blob/f43d5789b838fb0d80962e3d4b45fb9ddfcc9a07/text/2972-constrained-naked.md)
- [Rust RFC 1183](https://github.com/rust-lang/rfcs/blob/f43d5789b838fb0d80962e3d4b45fb9ddfcc9a07/text/1183-swap-out-jemalloc.md) -> [RFC 1974](https://github.com/rust-lang/rfcs/blob/f43d5789b838fb0d80962e3d4b45fb9ddfcc9a07/text/1974-global-allocators.md)

These documents provide genuine source supersession links, **not** a ready-to-use set of authenticated organisational instructions. The source authors did not participate in this study; source-document authorship does not count as independent study adjudication. A PEP's formal status is not a substitute for reconstructing authority precedence, event-observation times, or action semantics.

## Next scientific eligibility gate

A human case writer must prospectively convert each relevant source into a licensed, privacy-safe task with decision time and issuer hierarchy. A different human must independently adjudicate its correct response; disagreement handling and exclusions must be documented before an LLM run. A minimum of one independently qualified method reviewer must examine the mapping and overlap with CIKM Knowledge Triage and Supersede. The same individual must not silently act as author and blind adjudicator. Until then P07b remains **PARTIAL**, P09 paid pilot and all confirmatory work are blocked.

No text from the third-party documents is redistributed in the project, only commit/blob metadata and public links. Follow source licences and consent rules for any future excerpts.
