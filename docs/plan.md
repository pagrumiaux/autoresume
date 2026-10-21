# Plan

Format: `docs/PLAN_FORMAT.md`. Goals, architecture and the phase roadmap: `docs/design.md`.
Each later phase is added here with `/jam` before it starts.

## Phase 0 — Foundation (no LLM)

### P0.S1 — [Human] Create the private data repo and set the env var
- goal: You create the private `autoresume-data` repo that holds all personal content, and point the CLI to its local clone.
- depends_on: []
- acceptance:
  - `gh repo view pagrumiaux/autoresume-data --json visibility` reports `PRIVATE`
  - the repo is cloned locally and `AUTORESUME_DATA_DIR` is set to that path in your shell profile

### P0.S2 — Project skeleton
- goal: A uv project with a src layout for the `autoresume` package, ruff and pytest configured, and a minimal Typer CLI, so later tasks have a place for code and a way to test it.
- depends_on: []
- touches: [pyproject.toml, uv.lock, .python-version, src/autoresume/__init__.py, src/autoresume/cli.py, tests/test_cli.py]
- acceptance:
  - `uv sync` succeeds on a fresh clone; `requires-python` is `>=3.12`
  - runtime dependencies typer, pydantic, pyyaml, typst and pypdf, and dev dependencies ruff, pytest and pre-commit, are declared in `pyproject.toml`
  - `uv run autoresume --help` exits 0
  - `uv run ruff check` and `uv run ruff format --check` pass
  - `uv run pytest` passes and includes a test that invokes the CLI
- test_first: false

### P0.S3 — Data guard, pre-commit and CI
- goal: Pre-commit runs ruff and blocks any commit that stages a file from the data dir, and GitHub Actions runs ruff and pytest on every PR, so personal data can't leak and main stays green.
- depends_on: [P0.S2]
- touches: [.pre-commit-config.yaml, scripts/check_no_data.py, tests/test_check_no_data.py, .github/workflows/]
- read_first: [docs/decisions/2026-10-06-public-code-private-data.md]
- acceptance:
  - the guard fails, naming the file, when a staged file resolves to a path under `AUTORESUME_DATA_DIR` (tested with a temporary directory)
  - the guard passes when no staged file is under that dir, and when `AUTORESUME_DATA_DIR` is unset (as in CI)
  - `uv run pre-commit run --all-files` runs ruff check, ruff format and the guard, and passes
  - a workflow in `.github/workflows/` runs `uv run ruff check`, `uv run ruff format --check` and `uv run pytest` on pull requests to main; `gh pr checks` shows it passing on this task's PR

### P0.S4 — Bank and archetype schema options
- goal: A short design note proposing two or three ways to model the experience bank and archetypes in Pydantic, with trade-offs, so you can choose one before writing the schema.
- depends_on: []
- touches: [docs/proposals/bank-schema.md]
- read_first: [docs/decisions/2026-10-06-selection-over-generation.md, docs/decisions/2026-10-06-archetypes-with-human-confirmation.md]
- acceptance:
  - the note presents 2–3 options, each with a short code sketch covering bullets with ids, skill tags, FR/EN variants, dates, projects, and archetypes (headline, skills order, bullet ids, projects, signals)
  - each option lists trade-offs: validation strength, ease of editing the YAML by hand, how agents will query it, how archetype variants inherit from a parent
  - the note proposes a file layout for a bank directory (e.g. `bank.yaml` plus `archetypes/`)
  - nothing is added under `src/`
- test_first: false
- notes: Co-designed area. Propose and explain; do not write the schema.

### P0.S5 — [Human] Choose the bank schema design
- goal: You pick one option (or a mix) from the proposal and the bank directory layout, so the tests and your schema follow one design.
- depends_on: [P0.S4]
- acceptance:
  - a decision record `docs/decisions/<date>-bank-schema.md` names the chosen design, the bank directory layout and the rejected options

### P0.S6 — Tests and stubs for the bank schema
- goal: Failing tests and `TODO(PA)` stubs for the chosen schema, so you can write the Pydantic models against a clear, readable spec.
- depends_on: [P0.S2, P0.S5]
- touches: [src/autoresume/bank/, tests/bank/]
- read_first: [docs/proposals/bank-schema.md, docs/decisions/2026-10-21-tests-first-in-user-owned-areas.md]
- acceptance:
  - model stubs in `src/autoresume/bank/` have a docstring of the expected behaviour and `TODO(PA)`, and no implementation
  - tests validate plain dicts and cover each validation rule of the chosen design, including: every bullet has FR and EN text, bullet ids are unique, an archetype referencing an unknown bullet id is rejected
  - each test has a one-line docstring naming the rule it checks
  - every test is marked `xfail(strict=True)` and `uv run pytest` passes
- test_first: false
- notes: The chosen design is in the decision record from P0.S5. Do not implement the models.

### P0.S7 — [Human] Write the bank schema
- goal: You read the P0.S6 tests and write the Pydantic models that make them pass.
- depends_on: [P0.S6]
- acceptance:
  - every test in `tests/bank/` passes with its xfail marker removed
  - PR titled `P0.S7: …`, reviewed by pr-reviewer, merged

### P0.S17 — Bank loaders
- goal: Functions that read a bank directory (the layout chosen in P0.S5) from YAML into your models, with errors that say which file and what is wrong.
- depends_on: [P0.S7]
- touches: [src/autoresume/bank/loader.py, tests/bank/test_loader.py]
- acceptance:
  - `load_bank(path)` returns the bank and its archetypes for a valid directory built in `tmp_path`
  - a YAML syntax error raises an error naming the file and line
  - a schema violation raises an error naming the file and the invalid field
  - a missing directory or `bank.yaml` raises a clear error, not a raw traceback from deep inside
- notes: The layout is in the decision record from P0.S5. Use the user's models as they are; do not change other files in `bank/`.

### P0.S8 — Fake example data
- goal: A small fake bank and fake archetypes for a fictional person, valid against the schema, for tests and demos without personal data.
- depends_on: [P0.S17]
- touches: [examples/bank/, tests/fixtures/, tests/test_fixtures.py]
- acceptance:
  - `examples/bank/` holds a bank of 2–3 experiences and 6–10 bullets, with FR and EN text for every entry, and 2 archetypes
  - `tests/fixtures/` holds a smaller bank and one archetype for unit tests
  - a test loads every example and fixture with the bank loaders without errors
  - all content is fictional

### P0.S9 — Three Typst layout directions
- goal: Three one-page resume layouts in Typst with hard-coded fake content, rendered to PDF, so you can pick a design before the real template is built.
- depends_on: [P0.S2]
- touches: [examples/layouts/]
- acceptance:
  - `examples/layouts/` has three `.typ` files and their rendered PDFs; each PDF is one page
  - text in each PDF is extractable with pypdf (real text, simple columns, ATS-friendly)
  - `examples/layouts/README.md` describes each direction in 2–3 lines
- test_first: false

### P0.S10 — [Human] Pick a layout direction
- goal: You choose one of the three layouts and list the changes you want, so the template is built once.
- depends_on: [P0.S9]
- acceptance:
  - the issue that closes this task names the chosen direction and lists the wanted changes as a checklist (e.g. margins, columns, section order, fonts)

### P0.S11 — Resume Typst template
- goal: The chosen layout as a Typst template that reads resume data instead of hard-coded text, in FR or EN.
- depends_on: [P0.S8, P0.S10]
- touches: [src/autoresume/render/templates/, tests/render/test_template.py]
- acceptance:
  - compiling the template with hand-built data matching the fake bank and each fake archetype gives a one-page PDF, in FR and in EN
  - text in the PDF is extractable with pypdf
  - the PR description lists each checklist item from the P0.S10 issue and how it was addressed
- notes: Read the P0.S10 issue first: `gh issue list --state closed --search "P0.S10 in:title"`. The step that builds template data from a bank comes in P0.S12.

### P0.S12 — Render function and page count
- goal: A function that turns a bank and an archetype into a PDF through the template, and a function that returns a PDF's page count, which later agents use to check the one-page limit.
- depends_on: [P0.S11]
- touches: [src/autoresume/render/__init__.py, src/autoresume/render/render.py, tests/render/test_render.py]
- acceptance:
  - `render(bank, archetype, lang, out)` writes a PDF for the fake bank and each fake archetype, in FR and EN
  - `page_count(pdf)` returns 1 for those outputs, and 2 for a resume the test builds to overflow the page

### P0.S13 — `render` command
- goal: `autoresume render` exposes the render function on the command line, reading the bank from `AUTORESUME_DATA_DIR` by default.
- depends_on: [P0.S12]
- touches: [src/autoresume/cli.py, tests/test_cli_render.py]
- acceptance:
  - `uv run autoresume render --bank examples/bank --archetype <name> --lang en --out <file>` writes a one-page PDF
  - without `--bank`, the bank is read from `AUTORESUME_DATA_DIR`; if it is unset, the command exits non-zero with a clear message, not a traceback
  - an invalid bank exits non-zero and prints the validation errors

### P0.S14 — [Human] Fill the bank
- goal: You write your real experience bank in FR and EN in `autoresume-data`, starting with current experiences.
- depends_on: [P0.S1, P0.S17]
- acceptance:
  - `uv run python -c "from autoresume.bank import load_bank; load_bank('$AUTORESUME_DATA_DIR')"` runs without errors

### P0.S15 — [Human] Draft and refine the seed archetypes
- goal: With Claude, draft 3–4 seed archetypes from your filled bank, then refine them yourself, keeping both versions.
- depends_on: [P0.S13, P0.S14]
- acceptance:
  - 3–4 archetypes in `autoresume-data/archetypes/`, each in a drafted and a refined version
  - `uv run autoresume render` gives a one-page PDF for each refined archetype, in FR and EN
- notes: Candidates: audio ML research engineer, embedded/edge audio AI, real-time audio DSP and MIR, speech AI.

### P0.Z — Cleanup
- goal: Remove duplication and simplify the phase's code, with no change in behaviour.
- depends_on: [P0.S2, P0.S3, P0.S4, P0.S6, P0.S8, P0.S9, P0.S11, P0.S12, P0.S13, P0.S17]
- touches: [src/autoresume/render/, src/autoresume/cli.py, src/autoresume/bank/loader.py, tests/, scripts/]
- acceptance:
  - no duplicated helpers across the phase; all existing tests pass unchanged
  - `git diff --stat origin/main -- src/autoresume/bank/ ':!src/autoresume/bank/loader.py'` is empty
- test_first: false

### P0.D — Docs
- goal: A README that explains what autoresume is, how to install it and how to render a resume from the example bank, and a Phase 0 entry in the CHANGELOG.
- depends_on: [P0.S2, P0.S3, P0.S4, P0.S6, P0.S8, P0.S9, P0.S11, P0.S12, P0.S13, P0.S17]
- touches: [README.md, CHANGELOG.md]
- acceptance:
  - README covers install (`uv sync`), setting `AUTORESUME_DATA_DIR`, and `autoresume render` with the example bank
  - CHANGELOG has a Phase 0 entry
- agent: docs-writer

### P0.S16 — [Human] Phase 0 retro
- goal: You write what you learned in Phase 0 and what should change in the plan, before Phase 1 is planned.
- depends_on: [P0.Z, P0.D, P0.S15]
- acceptance:
  - `docs/retros/phase-0.md` exists with what you learned and what changed in the plan
