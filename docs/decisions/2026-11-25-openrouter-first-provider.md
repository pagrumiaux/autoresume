# OpenRouter is the first provider, through the openai SDK
- Date: 2026-11-25
- Area: llm, config, privacy
- Status: accepted
- Source: /compose (Phase 1 planning)

## Context
Phase 1 needs one provider, and I want to compare models from the start. The stack allows provider SDKs only.

## Decision
Phase 1 calls OpenRouter through the `openai` SDK (OpenAI-compatible base URL), with the key in OPENROUTER_API_KEY. The model is a parameter, so trying another model is a flag, not code. Phase 4 still adds a native Anthropic adapter and Ollama; "OpenRouter vs native" becomes the comparison exercise.

## Rejected options
- Anthropic SDK first: native features (prompt caching, strict tool schemas), but one vendor until Phase 4.
- LiteLLM: a library between me and the API, against `2026-10-06-no-agent-framework.md`.

## Consequences
One key, many models. Provider differences stay hidden until Phase 4. Structured-output support varies by model, so validation and retry must not rely on it. Personal data passes through one more company: its privacy settings are checked in P1.S1 before real data is sent.
