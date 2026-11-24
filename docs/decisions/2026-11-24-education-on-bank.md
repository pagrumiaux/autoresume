# Education is a required list on Bank, with integer years
- Date: 2026-11-24
- Area: bank, schema, data-format
- Status: accepted
- Source: /compose, P0.S18

## Context
The resume needs degrees. The bank schema (2026-11-23-bank-schema.md) has skills, experiences and projects only, with full `YYYY-MM-DD` dates. Education is the same for every archetype and a resume prints only its years.

## Decision
`Bank` gets a required `education` list. Each entry has an `institution` (string), a `degree` and an optional `topic` (both FR and EN text), a `start` year and an `end` year (integers; `end` omitted for an ongoing programme). Every entry is printed, in list order: archetypes do not select education.

The schema is a co-designed area (agents propose and test, the user writes). For this one change, by the user's explicit choice on 2026-11-24, an agent writes the model in P0.S18, tests first. This is a one-off exception to the tests-first-in-user-owned-areas record, not a change to the ownership table.

## Rejected options
- Education inside archetypes: it never varies, so it would be repeated in every file.
- `YYYY-MM-DD` dates: they invent a month and a day the user does not have.
- An optional list that defaults to empty: a resume with no education would pass silently.
- Fixed text in the template: it would sit outside the bank, with no FR/EN validation.

## Consequences
- Every bank (real, example, fixture, test) needs an `education` list.
- Years are the one place that does not follow the full-date rule of the bank-schema record.
- A year range check (1900–2100) and `start <= end` are enforced by the model.
