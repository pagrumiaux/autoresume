# Plan format

`docs/plan.md` is read by `/play` to schedule tasks in parallel. Give this file to the LLM that writes your plan.

## Structure
- Phases: `## Phase <n> — <name>`
- Tasks: `### P<n>.S<m> — <title>`. Put `[Human]` before the title for a step only a person can do: create an account or an API key, find information, make a decision. Untagged tasks go to agents.
- IDs are stable: never renumber. New tasks get new IDs.
- Each agent task is one PR a human can review in 5–15 minutes.

## Task fields
- `goal:` — one or two plain sentences saying what the task delivers and why, readable without opening another document. First field of every new task (tasks marked `done: true` may omit it). The criteria in `acceptance` prove it; the goal says what it is, for a human reviewer and to keep the agent focused.
- `depends_on: [IDs]` — tasks that must be finished first (`[]` if none). List only real dependencies: anything not listed may run in parallel. An agent task that needs a key, an account or a decision depends on the `[Human]` task that provides it.
- `touches: [paths]` — files or folders the task will change. Tasks that can run in parallel must not share paths. Not needed for `[Human]` tasks.
- `acceptance:` — concrete criteria, each provable by a test or a command. For a `[Human]` task: what "done" means (e.g. "STRIPE_KEY set in .env").
- `read_first: [paths]` — optional, 1–4 files this task needs that an agent wouldn't find on its own: code to copy, a spec section, a specific decision record. Task-specific only: AGENTS.md is always loaded, and project-wide docs are listed in it.
- `agent:` — `task-runner` (default), `debugger` or `docs-writer`.
- `test_first: false` — optional. Skips the test-writer, for trivial, config or UI-only tasks.
- `effort: high | xhigh` — optional, for a task that needs more reasoning than usual (tricky algorithm, concurrency, security).
- `notes:` — optional context for the implementer.
- `done: true` — only for work finished before this workflow. Otherwise status comes from GitHub: a merged PR, or a closed issue for `[Human]` tasks, whose title starts with the ID.
- `dropped: true` + `reason:` — set by `/jam` when a task is no longer wanted.

## Phase endings
Every phase ends with two tasks that depend on all its other agent tasks:
- `P<n>.Z — Cleanup`: remove duplication across the phase and simplify, with no behaviour change (`test_first: false`).
- `P<n>.D — Docs`: README and CHANGELOG for the phase (`agent: docs-writer`).

## Example

```markdown
## Phase 2 — Uploads

### P2.S1 — [Human] Create the S3 bucket and access key
- goal: You create the storage bucket and key that the upload service will use.
- depends_on: []
- acceptance:
  - bucket `myapp-uploads` exists; S3_KEY_ID and S3_SECRET are set in .env

### P2.S2 — Storage service
- goal: A small module that saves an uploaded file to the bucket and loads it back by id.
- depends_on: [P2.S1]
- touches: [src/storage/, tests/storage/]
- read_first: [docs/decisions/2026-10-10-s3-storage.md]
- acceptance:
  - `save(file)` stores a file and returns an id; `load(id)` returns the same bytes
  - unknown ids raise NotFound

### P2.S3 — Audio-upload endpoint
- goal: An HTTP endpoint that accepts a WAV file, stores it through the storage service and returns its id.
- depends_on: [P2.S2]
- touches: [src/api/upload/, tests/api/]
- read_first: [src/api/health/routes.py]
- acceptance:
  - POST /upload with a WAV under 50 MB returns 201 and the file id
  - files over 50 MB are rejected with 413

### P2.Z — Cleanup
- goal: Remove duplication and simplify the phase's code, with no change in behaviour.
- depends_on: [P2.S2, P2.S3]
- touches: [src/]
- acceptance:
  - no duplicated helpers across the phase; all existing tests pass unchanged
- test_first: false

### P2.D — Docs
- goal: Document the upload endpoint in the README and add a Phase 2 entry to the CHANGELOG.
- depends_on: [P2.S2, P2.S3]
- touches: [README.md, CHANGELOG.md, docs/]
- acceptance:
  - README documents the upload endpoint; CHANGELOG has a Phase 2 entry
- agent: docs-writer
```
