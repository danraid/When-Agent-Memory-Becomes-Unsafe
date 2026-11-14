# Editorial engine v0.4.0 | journal-neutral draft package

## What is implemented

The renderer produces `manuscript.md`, `manuscript.tex`, `references.bib`, `citation_provenance.json`, `submission_checklist.md`, `editorial_status.json` and an integrity `manifest.json`. Optional ReportLab PDF is a **draft proof only**, never a journal-compliant final typeset file. The GitHub workflow is manual, and packages are downloadable Actions artifacts rather than automatic Git commits/submissions.

## Citations

1. Run real `discover --live` and save result into `editorial/catalogue.json`. A citation record must be `METADATA_VERIFIED`, have an OpenAlex identifier and `CROSSREF_IDENTITY_MATCH`, and include a raw Crossref identity snapshot with matching DOI/title and checksum. Offline fixture records are rejected.
2. For each scientific method/result claim, create a short excerpt in `evidence/excerpts/`, calculate SHA256, and add an `editorial/claims.json` record containing DOI, claim text, excerpt path/hash, page or section locator and a `human_review` with decision `VERIFIED`, method `MANUAL_FULLTEXT_REVIEW`, named reviewer and timestamp. This describes recorded work; it does not independently authenticate a human identity or the correctness of their review.
3. The renderer checks the bibliographic identity, excerpt bytes, locator, and recorded review before emitting `[@doi_...]` citations or `.bib` entries. It rejects mismatched title, DOI, hashes, paths, or uncatalogued citations. `METADATA_VERIFIED` alone cannot justify article conclusions.
4. If no valid sources exist, the system generates a **blank literature-review scaffold**, not a fake scholarly review. All author-provided prose remains subject to author fact-checking.

## Operational usage

```sh
python -m unittest discover -s tests -v
python scripts/hub.py editorial --output runs/editorial-draft
python scripts/hub.py verify --directory runs/editorial-draft
# To attach a local prior experiment (mock or real; classifications preserved):
python scripts/hub.py editorial --results runs/empirical-smoke --output runs/editorial-with-results
# Optional PDF proof (reportlab>=4):
python scripts/hub.py editorial --pdf --output runs/editorial-pdf
```

Keep the manuscript prepared for the **chosen journal** only after checking its live author instructions and using its official template. Do not claim acceptance, peer review, full-text verification or preregistration based solely on a passing test run. Do not expose repository construction details in published books/articles.

## Required manual steps before submission

Current journal instructions, author metadata and affiliations, conflicts/funding/data access, ethical review if applicable, rights, original citation source inspection, author approval, statistical review and actual submission must all be handled explicitly by humans. The engine has no journal submission adapter and no submission-approved state.
