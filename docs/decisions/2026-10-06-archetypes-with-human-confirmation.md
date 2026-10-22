# Archetypes with human confirmation and retrieval-based learning
- Date: 2026-10-06
- Area: archetypes, agents, feedback
- Status: accepted
- Source: initial plan

## Context
Applications fall into role families, but new families appear. The agent must not silently
force a job into the wrong archetype or multiply near-duplicate archetypes.

## Decision
- Archetypes are presets: headline (FR/EN), skills order, default bullet ids, projects, signals.
- 3–4 seeds are drafted from the filled bank, then refined by me; both versions are kept.
- The analyst scores each archetype with an explicit "none fits" option; I confirm or correct
  every pick. Decisions are logged and similar past decisions are retrieved as prompt examples.
- A new archetype is proposed only after showing the nearest existing one; variants can inherit.

## Rejected options
- Fine-tuning a classifier: far too few examples.
- Fully automatic classification: errors would go unnoticed.

## Consequences
Agreement rate becomes a measurable metric; confirmation can relax to low-confidence cases only.
