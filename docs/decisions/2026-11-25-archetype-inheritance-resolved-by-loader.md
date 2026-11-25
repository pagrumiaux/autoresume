# Archetype inheritance is resolved by the loader; list deltas remove first, then append
- Date: 2026-11-25
- Area: bank, loader, archetypes
- Status: accepted
- Source: B-archetype-inheritance

## Context
Archetypes may `extends` a parent, omit fields, and edit `bullets`/`signals` with a `{add, remove}` ListDelta. Nothing merged them, so a variant reached the renderer with a ListDelta or None and printed no work section and no projects.

## Decision
`load_bank` returns archetypes with inheritance resolved (parents first, so file order and chains do not matter): every field is set and `bullets`/`signals` are plain lists. An omitted field takes the parent's value, a plain list replaces it, and a ListDelta applies to the parent's resolved list: `remove` first, then `add` items not already present are appended, parent order kept. `extends` stays set for provenance. A cycle raises `BankLoadError` naming a file of the cycle. Consumers (render, agents) never see a ListDelta.

## Rejected options
- Resolve in the renderer: every consumer would repeat it and could forget; the schema docstring already assigns it to the loader.
- Add first, then remove: `add: [x], remove: [x]` would drop `x`; remove-then-add lets a variant move an inherited item to the end.

## Consequences
- `ListDelta` exists only between YAML and `load_bank`; code that builds an `Archetype` by hand (tests) must give plain lists to be rendered.
- A `remove` naming an id the parent lacks is ignored, not an error.
