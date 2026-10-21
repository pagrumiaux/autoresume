# 0001: Selection over generation, with an experience bank

Date: 2026-10-06 · Status: accepted

## Context
Tailored resumes must not overclaim, and must not look overfitted to the job description,
which reads as a red flag to recruiters.

## Decision
All resume and letter content comes from a verified experience bank (YAML, FR + EN variants).
Agents select, order and lightly rephrase; a new claim enters the bank only after my approval.
Every output sentence must trace back to a bank entry.

## Alternatives considered
- Free generation from a base resume: fast, but overclaims and drifts in tone.
- Fully manual variants per role: safe, but no learning value and slow.

## Consequences
Phase 0 requires real effort to fill the bank. In return, traceability can be checked
mechanically and every resume stays recognizably mine.
