# Eval set from pasted job descriptions, no fetching
- Date: 2026-10-06
- Area: evals, privacy
- Status: accepted
- Source: initial plan

## Context
Quality needs an eval set, but callbacks are too rare to measure; the set must come from real job
descriptions without adding a scraping layer.

## Decision
The eval set is built from past and hand-picked job descriptions that I paste in. They live in the
private data repo (`eval_jds/`). Nothing fetches job postings from the web.

## Rejected options
- Fetching postings from their URLs: more code and fragile scraping, with no gain at this scale.

## Consequences
Eval set size grows only with my effort; metrics stay proxy metrics (drift, traceability, page
fit, feedback rounds, archetype agreement).
