# Scientific authority and evidence contract

## Literature status
`CANDIDATE`: discovered record. `METADATA_VERIFIED`: DOI/title/venue checked. `ABSTRACT_SCREENED`: topical background only. `FULLTEXT_PENDING`: no audited method. `FULLTEXT_AUDITED`: exact claims and source methods checked with page/section, provenance, licence and limitations. `SCIENTIFICALLY_APPROVED`: independently reviewed claim-specific decision with author approval. `REJECTED`/`RETRACTED`/`SUPERSEDED`: persistent audit trail.

An API reviewer cannot grant `SCIENTIFICALLY_APPROVED`. Book-specific eligibility from EDD/SDD does not automatically establish paper-grade experimental evidence.

## Experimental gates
Set hypotheses, primary outcomes, model assumptions, inclusion criteria, sample-size rationale, statistics and stopping rules *before* confirmatory execution. Keep exploratory, calibration and untouched confirmatory partitions separate. Record revisions as amendments rather than silently rewriting old protocols. A machine-generated boolean is not sufficient proof of a human approval; require reviewable GitHub PRs/decisions.

## Reproducibility
For each result: executable SHA, configuration hash, source identities, measured outputs, sample IDs, seeds, environment and dependencies, model/version and prompt identity, API usage, independent checks, uncertainty, failed runs and limitations. External submission is human controlled.
