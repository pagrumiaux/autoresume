# Structured LLM output through JSON schema and a Pydantic retry, via OpenRouter
- Date: 2026-11-24
- Area: llm, agents
- Status: accepted
- Source: /compose, Phase 1

## Context
Phase 1 needs the model to return tailoring decisions the code can trust. The user wants to compare many models for quality and cost, and Phase 4 adds a provider layer later.

## Decision
Calls go through the `openai` SDK pointed at OpenRouter. Each call sends the Pydantic model's JSON schema, sets `require_parameters` so only models that support it are used, parses the reply into the model, and retries with the validation error on failure. The model name per step is set in `config.yaml` in the data dir; the key comes from `OPENROUTER_API_KEY`. The detected language is part of the reply, inferred from the job description.

## Rejected options
- Anthropic SDK directly: one provider only, model comparison needs Phase 4 first.
- Plain JSON in the prompt with our own parser: teaches less current practice and fails more often.

## Consequences
- Models without JSON-schema support are unusable; a failing model is replaced, not worked around.
- This refines the no-agent-framework record: one OpenAI-compatible gateway now, per-step routing by config.
- Phase 4 adds the Anthropic adapter next to this client; the function boundary of `llm/` must stay thin.
- Cost comes from OpenRouter's usage data into the call log.
