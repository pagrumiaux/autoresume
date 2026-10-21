# 0004: Public code repo, private data repo

Date: 2026-10-06 · Status: accepted

## Context
The code is a portfolio piece, but the data (bank, job descriptions, letters, feedback) is personal.

## Decision
Two repos: `resume-agent` (public) and `resume-data` (private). The data path comes from the
`RESUME_DATA_DIR` env var. Tests and demos use fake fixtures only.

## Consequences
Need a fake example bank for tests and demos, and a pre-commit guard against leaking data.
