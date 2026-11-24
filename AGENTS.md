# AGENTS.md

Instructions for every coding agent working in this repo. Keep it under ~100 lines: it is loaded into every agent's context. Detail goes in the reference docs below, read only when needed.

## Project
`autoresume` is a CLI that tailors the user's resume (and an optional cover letter) to a job description. It selects and orders content from a verified **experience bank** instead of generating new claims, iterates with the user's feedback until they say "done", and archives every application. It has two equal goals: a tailored one-page resume in FR or EN in minutes, and the user's learning of low-level agentic engineering. The learning goal decides who writes which code (see Ownership).

## Stack
- Python 3.12+, managed with **uv** (`uv add`, `uv run`). No pip, no requirements.txt.
- **Pydantic v2** for all data models and config; YAML content; **Typst** (Python package) for rendering; **Typer** for the CLI.
- LLM access through provider SDKs only: `anthropic`, `openai` (OpenAI-compatible, also used for Ollama).
- **No agent framework** (LangChain, LangGraph, PydanticAI, …). LiteLLM only later, as a comparison.

## Commands
- Install: `uv sync`
- Test: `uv run pytest`
- Lint / format: `uv run ruff check` and `uv run ruff format`
- All hooks: `uv run pre-commit run --all-files`
- Run locally: `uv run autoresume --help`

## Ownership
The user writes the *core* of the areas `llm/`, `agents/`, `feedback/` and `evals/` themselves, to learn: prompts, agent loops, validators, metrics. For the core, never write implementation code, even if a task seems to ask for it. Allowed there: failing tests marked `@pytest.mark.xfail(strict=True)`, each with a one-line docstring; stubs with `TODO(PA)` and a docstring of the expected behaviour; and a learning brief `docs/learning/<ID>.md` with concepts, API docs links and common traps, but no solution code. Agents implement the plumbing around it (see `docs/decisions/2026-11-25-core-by-user-plumbing-by-agents.md`).

| Area | Who implements |
| --- | --- |
| Scaffolding, CI, pre-commit, packaging | Agents |
| Typst templates, rendering plumbing, file I/O (`render/`) | Agents |
| CLI plumbing (Typer commands, prompts, output) | Agents |
| Test fixtures, fake sample data | Agents |
| Bank and archetype Pydantic schemas (`bank/`, except `loader.py` and `writer.py`) | Co-designed: agents propose and test, the user writes |
| Bank YAML loaders and writer (`bank/loader.py`, `bank/writer.py`) | Agents |
| Plumbing in `llm/`, `agents/`, `feedback/`, `evals/` (provider clients, call logging, CLI wiring, file I/O) | Agents |
| Core in those areas: prompts, agent loops, validators, metrics (the plan's `[Human]` tasks) | User, coached |

## Privacy
- This repo is **public**. Personal data lives in the private `autoresume-data` repo.
- Never commit real resume content, job descriptions, letters, lessons or application archives.
- The data path comes from the env var `AUTORESUME_DATA_DIR`, never hard-coded.
- Tests and examples use the fake data in `tests/fixtures/` and `examples/` only.
- Before any commit, check that no file under the data dir is staged.

## Conventions
- Layout: `src/autoresume/` with `bank/`, `render/`, `llm/`, `agents/`, `feedback/` and `cli.py`; `evals/` at the root.
- Tests live in `tests/`, mirror the package layout, and use pytest.
- Type hints everywhere; docstrings on public functions; small, focused modules.
- Every LLM call is logged as one JSONL line: provider, model, tokens, cost, latency, step name.
- Run ruff check, ruff format and pytest before pushing.

## Reference docs
<!-- Project-wide docs, each with when to read it. Task-specific files go in the plan's read_first instead. -->
- `docs/decisions/`: lasting design decisions; `grep -H "^- Area:" docs/decisions/*.md` lists them by area. Check the ones about the area you change.
- `docs/design.md`: goals, principles, architecture and roadmap. Read before changing how agents, tools or data fit together.

## Workflow rules
Shared by every project: `~/repertoire/rules/workflow.md` (loaded in every session).

## Standards
Language standards: `~/repertoire/standards/python.md`. Read the section you need.

## Rules from review
<!-- One line per rule, added by R- PRs: "- <rule> (from #<PR>)" -->
