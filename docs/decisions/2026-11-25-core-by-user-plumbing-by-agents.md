# I write each phase's core; agents write the plumbing, and I am coached
- Date: 2026-11-25
- Area: workflow, llm, agents, feedback, evals
- Status: accepted
- Source: /compose (Phase 1 planning)
- Supersedes (in part): 2026-10-21-tests-first-in-user-owned-areas.md (who implements; its tests-first mechanics stay)

## Context
`2026-10-21-tests-first-in-user-owned-areas.md` reserves all of `llm/`, `agents/`, `feedback/` and `evals/` for me. I want to understand how agents work with little code to write, as in a job where coding is delegated.

## Decision
In those areas, agents implement the plumbing (provider clients, logging, CLI, file I/O, including `bank/writer.py`). I write the core of each phase: prompts, agent loops, validators and metrics. Each core task is preceded by an agent task with strict-xfail tests, `TODO(PA)` stubs and a learning brief `docs/learning/<ID>.md` (concepts, API docs, traps, no solution code). Bob coaches each core task by levels (hint, explanation, example) and writes none of its code. The tests-first mechanics of the old record still apply to the core.

## Rejected options
- I write everything in those areas: most practice, too slow for my goal.
- Agents write everything and I review: fastest, but reviewing code I never wrote teaches less.

## Consequences
One extra PR per core task (tests, stubs, brief). Plan tasks name which parts are core. The Ownership table in AGENTS.md changes through an `R-` PR.
