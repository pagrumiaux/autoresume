# Bank schema: nested bullets with inline FR/EN variants (Scheme A)
- Date: 2026-11-23
- Area: bank, schema, data-format
- Status: accepted
- Source: P0.S5, proposal docs/proposals/bank-schema.md (P0.S4)

## Context
The bank needs bullets with stable ids and skill tags, FR and EN text, dates, projects and archetypes. The proposal gave three layouts (A, B, C); the schema code and tests need one.

## Decision
Scheme A: a single `bank.yaml` where bullets are nested inside the job or project they belong to, and every translatable string is an inline `{fr, en}` mapping.
- Skills: a plain `id` with a `label` ({fr, en}) and a `category` used to group skills in the resume. No levels.
- Dates: full `YYYY-MM-DD` so PyYAML parses them natively as dates; use day `01` when only month and year matter. `end` is omitted for ongoing roles.
- A bullet belongs to a job or a project, never both (no overlap, so no sharing).
- Archetype `signals` are free text.
- Archetypes (carried over from the proposal, not decided here): `extends` inheritance and `{add, remove}` list edits, as in the proposal's shared archetype design.

Directory layout (`$AUTORESUME_DATA_DIR`; fake equivalents in `tests/fixtures/` and `examples/`):
```
autoresume-data/
  bank.yaml            # skills, experiences (with bullets), projects (with bullets)
  archetypes/
    <id>.yaml          # one file per archetype, file name = id
```

## Rejected options
- B (flat bullet registry): its main advantage was sharing one bullet between a job and a project, which the no-overlap rule removes; it costs indirection between sections.
- C (one file per language): weakest validation (FR/EN parity is a cross-file check), and two files to keep in sync by hand.

## Consequences
- Ids must be unique across the whole bank and tags must exist in `skills`: a model validator enforces both. A `bank.bullets()` helper flattens jobs and projects for id and tag queries.
- Moving a bullet between a job and a project means moving its text.
- Splitting `bank.yaml` into several files stays possible later if it grows too large.
