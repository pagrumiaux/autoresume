# CLAUDE.md

## Project

`resume-agent` is a CLI that tailors my resume (and an optional cover letter) to a job description.
It selects and orders content from a verified **experience bank** instead of generating new claims,
iterates with my feedback until I say "done", and archives every application.

It has two equal goals:

1. **Productivity:** a tailored one-page resume in FR or EN, in minutes.
2. **Learning:** I am building low-level agentic engineering skills for industry roles.
   This goal decides who writes which code (see Ownership).

Full plan: `docs/PLAN.md`. Design decisions: `docs/decisions/`.

## Ownership: who writes what

This is the most important rule in this file.

| Area | Who implements | Your role |
| --- | --- | --- |
| Repo scaffolding, CI, pre-commit, packaging | Claude | Implement |
| Typst templates, rendering plumbing, file I/O | Claude | Implement |
| CLI plumbing (Typer commands, prompts, output) | Claude | Implement |
| Test fixtures, fake sample data | Claude | Implement |
| Bank and archetype Pydantic schemas (`bank/`) | Co-designed | Propose a design and trade-offs; I write it; you review |
| Provider adapters and routing (`llm/`) | Me | Explain, review, write tests first; do NOT implement |
| Agent loop, agents, orchestration (`agents/`) | Me | Explain, review, write tests first; do NOT implement |
| Feedback log, lessons, archetype learning (`feedback/`) | Me | Explain, review, write tests first; do NOT implement |
| Drift, traceability and eval metrics (`evals/`, checks) | Me | Explain, review, write tests first; do NOT implement |

In the "Me" areas, never write implementation code unless I explicitly ask for it in that message.
Instead: explain the concept, point to the relevant API docs, suggest an interface, write failing
tests, and review my code honestly (correctness, design, readability). Stubs with `TODO(PA)` and a
docstring describing the expected behavior are fine.

When explaining, tell me *why* a solution works and what made my problem tricky. I come from
research and want to learn team-grade practices, so point out non-idiomatic code.

## Privacy: hard rules

- This repo is **public**. Personal data lives in a separate private repo (`resume-data`).
- Never commit real resume content, job descriptions, letters, lessons or application archives here.
- The data path comes from config (env var `RESUME_DATA_DIR`), never hard-coded.
- Tests and examples use the fake data in `tests/fixtures/` and `examples/` only.
- Before any commit, check that no file under the data dir is staged.

## Conventions

- Python 3.12+, managed with **uv** (`uv add`, `uv run`). No pip, no requirements.txt.
- **ruff** for lint and format; **pytest** for tests; **pre-commit** runs both.
- **Pydantic v2** for all data models and config. Type hints everywhere.
- **No agent framework** (LangChain, LangGraph, etc.). Provider SDKs only: `anthropic`, `openai`
  (OpenAI-compatible, also used for Ollama). LiteLLM only later, as a comparison.
- Small, focused modules. Docstrings on public functions.
- Every LLM call is logged as one JSONL line: provider, model, tokens, cost, latency, step name.

## Workflow

- Start each phase in plan mode and break it into small tasks.
- One branch and one PR per task, even working alone. Conventional commit messages.
- Run `uv run ruff check`, `uv run ruff format`, `uv run pytest` before proposing a commit.
- A design choice worth remembering gets a short note in `docs/decisions/` (template: `0000-template.md`).
- End each phase with a short retro in `docs/retros/phase-N.md`: what I learned, what changed in the plan.

## Current status

Phase 0 (foundation, no LLM) has not started. See `docs/PLAN.md` for phases.
