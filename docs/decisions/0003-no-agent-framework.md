# 0003: No agent framework; own provider layer

Date: 2026-10-06 · Status: accepted

## Context
A main goal is to learn agentic engineering low-level for industry roles, and to pick the cheapest
adequate model per step, including local models.

## Decision
Use provider SDKs directly (Anthropic, OpenAI-compatible for Ollama and others) behind my own thin
adapter layer, with per-step routing. Write the tool loop by hand. Compare with LiteLLM or a
framework later, as a documented exercise.

## Alternatives considered
- LangGraph / PydanticAI from day one: faster, but hides what I want to learn.
- Single provider only: simpler, but no cost/quality routing and less to learn.

## Consequences
More code to own and test, and real exposure to tool-format differences between providers.
