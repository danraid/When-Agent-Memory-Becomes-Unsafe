# Operator guide | Agentic Research Hub 0.2.0

## Safe modes

- `python -m unittest discover -s tests -v`: local unit and integration checks, no internet or GPT.
- `python scripts/hub.py plan`: reads research state without promoting a stage.
- `python scripts/hub.py demo --output runs/demo`: repeatable synthetic demonstration with SHA256 provenance and report, NOT a scientific experiment.
- `python scripts/hub.py verify --directory runs/demo`: checks the saved manifest against exact evidence bytes.
- `python scripts/hub.py discover --fixture tests/fixtures/openalex_mock.json --output runs/fixture.json`: tests the bibliographic parser on intentionally fictional records.
- `python scripts/hub.py discover --live --output runs/discovery.json`: bounded live OpenAlex research metadata search with optional Crossref DOI identity checks. Set `OPENALEX_API_KEY` for the free tier at scale and `CROSSREF_CONTACT_EMAIL` for polite Crossref access. The latter is optional. Never commit keys.

Live search uses only the first result page of each research query, 1-8 queries, up to 25 records/query and 25 DOI identity lookups. It does not claim full-text validation, copyright permissions, novelty or empirical validity.

## Opt-in OpenAI advisory

1. Choose a model in `paper.json`, enable `api.enabled`, fill explicit current **USD per million input/output tokens** prices, confirm per-job budgets.
2. Set `OPENAI_API_KEY` as a repository Actions secret. Do not hardcode in source.
3. Prepare a bounded non-sensitive UTF-8 prompt file, not confidential source text without authorization.
4. Run `python scripts/hub.py advisory --execute --prompt-file path/to/input.txt --output runs/advisory.json` from a serial job.

The local file ledger reserves an intentionally conservative worst-case cost *before* any request. Unknown network outcomes retain reservations. The ledger is NOT a provider invoice and is NOT shared between concurrent Actions jobs or across machines. Disable parallel paid jobs and use GitHub concurrency. The tool sets `store=false` and records only a prompt SHA256, usage if reported, output advisory text and a redacted ledger. It never awards scientific approval.

## Article-specific research

The generic demonstration is **not** evidence about GPT agents. After creating a separate article repository (only on approval), define hypotheses, data boundaries, baselines, tasks, random seeds, unit tests, independent validators, statistical plan, and author approvals there. A valid preregistered protocol must precede access to confirmatory data.

Do not treat metadata verification as proof that a paper's full text was reviewed. Do not turn the generic technical report into a journal manuscript.
