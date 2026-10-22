# Public code repo, private data repo
- Date: 2026-10-06
- Area: privacy, config
- Status: accepted
- Source: initial plan

## Context
The code is a portfolio piece, but the data (bank, job descriptions, letters, feedback) is personal.

## Decision
Two repos: `autoresume` (public) and `autoresume-data` (private). The data path comes from the
`AUTORESUME_DATA_DIR` env var. Tests and demos use fake fixtures only.

## Consequences
Need a fake example bank for tests and demos, and a pre-commit guard against leaking data.
