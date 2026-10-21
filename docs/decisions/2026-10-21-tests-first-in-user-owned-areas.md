# Agents write tests and stubs; I implement my own areas
- Date: 2026-10-21
- Area: workflow, bank, llm, agents, feedback, evals
- Status: accepted
- Source: /jam

## Context
`/play` sends every untagged task to agents, but the learning goal reserves the bank schema,
`llm/`, `agents/`, `feedback/` and `evals/` for me to write.

## Decision
Work in those areas is two plan tasks. First an agent task writes failing tests, each with a
one-line docstring, marked `@pytest.mark.xfail(strict=True)`, plus stubs with `TODO(PA)` and a
docstring of the expected behaviour (`test_first: false`). Then a `[Human]` task: I read the tests,
implement, remove the markers, open a PR titled with the task ID, and ask for a pr-reviewer review.

## Rejected options
- Failing tests without xfail: main and every PR's CI turn red until I implement.
- I write both tests and code everywhere: more design practice, but slower; kept as a per-task
  exception when a task's notes say so.

## Consequences
Strict xfail fails once the code passes, so markers can't linger. My pace sets the pace of these
areas, by design.
