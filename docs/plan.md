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

### P0.S18 — Education in the bank schema
- goal: The bank has an `education` list (institution, degree, optional topic, start and end years), so the resume template prints degrees from the bank like everything else.
- depends_on: [P0.S8, P0.S17]
- touches: [src/autoresume/bank/schema.py, tests/bank/, examples/bank/bank.yaml, tests/fixtures/bank/bank.yaml, tests/test_fixtures.py]
- read_first: [docs/decisions/2026-11-23-bank-schema.md#decision, docs/decisions/2026-11-24-education-on-bank.md#decision]
- size: M
- acceptance:
  - `Bank` has a required `education` list; each entry has `institution` (non-empty string), `degree` (FR and EN text), an optional `topic` (FR and EN text), `start` (int year) and `end` (int year, omitted for an ongoing programme)
  - a year outside 1900–2100, or a `start` after the `end`, is rejected with an error naming the entry's institution
  - a bank without `education` is rejected with an error naming the field
  - `examples/bank/` and `tests/fixtures/` each have at least one fictional education entry with FR and EN text, and every bank built in the tests loads
  - the whole test suite and `ruff check` pass
- notes: `bank/schema.py` is a co-designed area. The user explicitly authorised an agent to write this model, for this task only, on 2026-11-24. Do not change other files in `bank/`.

### P0.S11 — Resume Typst template
- goal: The chosen layout as a Typst template that reads resume data instead of hard-coded text, in FR or EN.
- depends_on: [P0.S8, P0.S10, P0.S18]
- touches: [src/autoresume/render/templates/, tests/render/test_template.py]
- acceptance:
  - compiling the template with hand-built data matching the fake bank and each fake archetype gives a one-page PDF, in FR and in EN
  - text in the PDF is extractable with pypdf
  - the template prints each education entry (institution, degree, years) in FR and in EN
  - the PR description lists each checklist item from the P0.S10 issue and how it was addressed
- notes: Read the P0.S10 issue first: `gh issue list --state closed --search "P0.S10 in:title"`. The step that builds template data from a bank comes in P0.S12.

### P0.S12 — Render function and page count
- goal: A function that turns a bank and an archetype into a PDF through the template, with a proper FR/EN heading for every skill category, and a function that returns a PDF's page count, which later agents use to check the one-page limit.
- depends_on: [P0.S11]
- touches: [src/autoresume/render/__init__.py, src/autoresume/render/render.py, src/autoresume/render/headings.py, tests/render/test_render.py]
- read_first: [docs/decisions/2026-11-24-category-headings-table.md#decision, docs/decisions/2026-11-24-soft-skills-not-rendered.md#decision]
- acceptance:
  - `render(bank, archetype, lang, out)` writes a PDF for the fake bank and each fake archetype, in FR and EN
  - the PDF built from the fake bank contains each of its education entries
  - `page_count(pdf)` returns 1 for those outputs, and 2 for a resume the test builds to overflow the page
  - the template data has a `category_titles` entry for every skill category it contains, taken in the requested language from a table in `src/autoresume/render/headings.py` with these headings (EN / FR): audio "Audio" / "Audio", ml "Machine learning" / "Machine learning", mlops "MLOps & engineering" / "MLOps et ingénierie", programming "Programming" / "Programmation", music "Music" / "Musique", languages "Languages" / "Langues", data "Data" / "Données"
  - a category missing from the table gets a tidied heading (hyphens to spaces, first letter capitalized: `soft-skills` gives "Soft skills"), a warning naming the category is logged (checked with `caplog`), and the render does not fail
  - with a bank the test builds that has a `soft` skill, that skill is left out of the template data

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
- depends_on: [P0.S1, P0.S17, P0.S18]
- acceptance:
  - `uv run python -c "from autoresume.bank import load_bank; load_bank('$AUTORESUME_DATA_DIR')"` runs without errors
  - `uv run python -c "from autoresume.bank import load_bank; b, _ = load_bank('$AUTORESUME_DATA_DIR'); assert len(b.education) >= 3"` runs without errors

### P0.S15 — [Human] Draft and refine the seed archetypes
- goal: With Claude, draft 3–4 seed archetypes from your filled bank, then refine them yourself, keeping both versions.
- depends_on: [P0.S13, P0.S14]
- acceptance:
  - 3–4 archetypes in `autoresume-data/archetypes/`, each in a drafted and a refined version
  - `uv run autoresume render` gives a one-page PDF for each refined archetype, in FR and EN
- notes: Candidates: audio ML research engineer, embedded/edge audio AI, real-time audio DSP and MIR, speech AI.

### P0.Z — Cleanup
- goal: Remove duplication and simplify the phase's code, with no change in behaviour.
- depends_on: [P0.S2, P0.S3, P0.S4, P0.S6, P0.S8, P0.S9, P0.S11, P0.S12, P0.S13, P0.S17, P0.S18]
- touches: [src/autoresume/render/, src/autoresume/cli.py, src/autoresume/bank/loader.py, tests/, scripts/]
- acceptance:
  - no duplicated helpers across the phase; all existing tests pass unchanged
  - `git diff --stat origin/main -- src/autoresume/bank/ ':!src/autoresume/bank/loader.py'` is empty
- test_first: false

### P0.D — Docs
- goal: A README that explains what autoresume is, how to install it and how to render a resume from the example bank, and a Phase 0 entry in the CHANGELOG.
- depends_on: [P0.S2, P0.S3, P0.S4, P0.S6, P0.S8, P0.S9, P0.S11, P0.S12, P0.S13, P0.S17, P0.S18]
- touches: [README.md, CHANGELOG.md]
- acceptance:
  - README covers install (`uv sync`), setting `AUTORESUME_DATA_DIR`, and `autoresume render` with the example bank
  - CHANGELOG has a Phase 0 entry
- agent: docs-writer

### P0.S16 — [Human] Phase 0 retro
- goal: You write what you learned in Phase 0 and what should change in the plan, before Phase 1 is planned.
- dropped: true
- reason: folded into Phase 1 planning
- depends_on: [P0.Z, P0.D, P0.S15]
- acceptance:
  - `docs/retros/phase-0.md` exists with what you learned and what changed in the plan

## Phase 1 — Single structured call

### P1.S1 — [Human] OpenRouter key and data-retention check
- goal: You create an OpenRouter API key and check that its data policy, and that of the providers you will route to, is acceptable for your bank, so personal data only goes where you agreed.
- depends_on: []
- acceptance:
  - the variable OPENROUTER_API_KEY is set in your shell (never paste its value into the plan, an issue or a PR)
  - the issue closing this task says which OpenRouter privacy settings you chose (for example, no providers that train on prompts) and which models you will try

### P1.S2 — OpenRouter client and call log
- goal: A thin client over the `openai` SDK pointed at OpenRouter, which sends a chat request, returns the text with its usage, and logs every call as one JSONL line, so later tasks call one interface and every call is costed.
- depends_on: []
- touches: [src/autoresume/llm/, tests/llm/, pyproject.toml, uv.lock]
- read_first: [docs/decisions/2026-11-25-openrouter-first-provider.md#decision]
- acceptance:
  - `LLMClient.complete(messages, model=, step=, json_schema=None)` returns a result with the text, input and output tokens, cost in USD (or None when the response has none) and latency in seconds
  - with `json_schema` given, a test with a fake transport asserts the request body has a `response_format` carrying that schema
  - each call appends one JSON line to the log file with provider, model, input and output tokens, cost, latency and step name, and no prompt or response text
  - the log file defaults to `$AUTORESUME_DATA_DIR/logs/llm.jsonl`; with AUTORESUME_DATA_DIR unset and no log path given, an error names the variable
  - a missing OPENROUTER_API_KEY raises an error that names the variable
  - tests use a fake HTTP transport or a fake client; `uv run pytest` makes no network call
- notes: Use the `openai` SDK with OpenRouter's base URL; no other LLM library. Also provide a `FakeLLMClient` that returns queued responses and records the requests, for the agent and CLI tests.

### P1.S3 — Tailoring decision options
- goal: A short proposal with two or three shapes for the JSON the model returns (the tailoring decision), so you can pick one before any tests are written.
- depends_on: []
- touches: [docs/proposals/tailoring-decision.md]
- read_first: [src/autoresume/bank/schema.py, docs/decisions/2026-10-06-selection-over-generation.md, docs/design.md#design principles]
- acceptance:
  - `docs/proposals/tailoring-decision.md` describes each option with a YAML or JSON example built from the fake bank in `examples/bank`
  - one option expresses the decision as a variant `Archetype` (`extends` plus `ListDelta`), so `render` can use it unchanged
  - each option says how a validator rejects a bullet, project or skill id that is not in the bank, and how it caps the number of bullets changed versus the archetype (the drift budget)
  - the proposal ends with a recommendation and its trade-offs
- test_first: false

### P1.S4 — [Human] Choose the tailoring decision shape
- goal: You pick the shape of the tailoring decision, so the tests, your code and the `tailor` command share one format.
- depends_on: [P1.S3]
- acceptance:
  - a decision record `docs/decisions/<date>-tailoring-decision.md` names the chosen shape, the drift cap and the rejected options

### P1.S5 — Tests, stub and brief for the tailoring decision model
- goal: Failing tests, a `TODO(PA)` stub and a learning brief for the Pydantic model of the tailoring decision, so you can write it against a clear spec with guidance.
- depends_on: [P1.S4]
- touches: [src/autoresume/agents/__init__.py, src/autoresume/agents/decision.py, tests/agents/__init__.py, tests/agents/test_decision.py, docs/learning/P1.S6.md]
- read_first: [docs/decisions/2026-11-25-core-by-user-plumbing-by-agents.md#decision]
- acceptance:
  - a stub of the decision model in `src/autoresume/agents/decision.py`, in the shape chosen in P1.S4, with a docstring of the expected behaviour and `TODO(PA)`, and no validation logic
  - tests cover: an unknown bullet, project or skill id is rejected; more bullet changes than the drift cap are rejected; a valid decision built from the fake bank is accepted
  - each test has a one-line docstring; every test is marked `xfail(strict=True)` and `uv run pytest` passes
  - `docs/learning/P1.S6.md` explains Pydantic validators with outside context (the bank), links the Pydantic docs and lists common traps, with no solution code
- test_first: false

### P1.S6 — [Human] Write the tailoring decision model
- goal: You write the Pydantic model of the tailoring decision, which rejects any id missing from the bank and any change beyond the drift cap, so no claim can leave the bank.
- depends_on: [P1.S5]
- acceptance:
  - every test in `tests/agents/test_decision.py` passes with its xfail marker removed
  - PR titled `P1.S6: …`, reviewed by pr-reviewer, merged
- notes: Coached: read `docs/learning/P1.S6.md`; Bob coaches by levels (hint, explanation, example) and writes none of the code.

### P1.S7 — Tests, stubs and brief for the tailoring call
- goal: Failing tests, `TODO(PA)` stubs, fake job descriptions and a learning brief for `tailor`, the call that turns a job description into a checked decision, so you can write it with guidance.
- depends_on: [P1.S2, P1.S5]
- touches: [src/autoresume/agents/tailor.py, tests/agents/test_tailor.py, tests/fixtures/jds/, docs/learning/P1.S8.md]
- read_first: [docs/decisions/2026-11-25-core-by-user-plumbing-by-agents.md#decision]
- acceptance:
  - a stub `tailor(jd, bank, archetype, client, model)` in `src/autoresume/agents/tailor.py` with a docstring of the expected behaviour and `TODO(PA)`, and no implementation
  - tests, using `FakeLLMClient`, cover: a valid response returns a decision; an invalid response is retried with the validation error sent back to the model; after 2 failed retries it raises an error carrying the last validation errors; the request passes the decision's JSON schema
  - `tests/fixtures/jds/` holds 3 fake job descriptions, each with one valid response written by hand from the fake bank (no real job description, no real model output)
  - each test has a one-line docstring; every test is marked `xfail(strict=True)` and `uv run pytest` passes
  - `docs/learning/P1.S8.md` explains structured outputs, retrying with error feedback and prompt layout, links the API docs and lists common traps, with no solution code
- test_first: false

### P1.S8 — [Human] Write the prompt and the validate-and-retry call
- goal: You write the tailoring prompt and the loop that calls the model, validates its JSON against the decision model and retries with the errors, so one call turns a job description into a checked decision.
- depends_on: [P1.S6, P1.S7]
- acceptance:
  - every test in `tests/agents/test_tailor.py` passes with its xfail marker removed
  - PR titled `P1.S8: …`, reviewed by pr-reviewer, merged
- notes: Coached: read `docs/learning/P1.S8.md`; Bob coaches by levels (hint, explanation, example) and writes none of the code.

### P1.S9 — Render a tailoring decision
- goal: A function that applies a tailoring decision to its archetype and renders the result, reporting the page count, so the `tailor` command only has to wire steps together.
- depends_on: [P1.S6]
- touches: [src/autoresume/render/tailored.py, tests/render/test_tailored.py]
- read_first: [src/autoresume/render/render.py]
- acceptance:
  - `render_decision(bank, archetype, decision, lang, out)` writes a PDF for each hand-written response in `tests/fixtures/jds/` and returns its page count
  - the bullets in the PDF follow the decision's order, not the archetype's
  - a decision that overflows the page returns 2 and still writes the PDF
- notes: Lives in `render/`, not `agents/`.

### P1.S10 — `tailor` command
- goal: `autoresume tailor` reads a job description, calls `tailor`, renders the resume and saves everything in a new application folder, so one command goes from job description to resume.
- depends_on: [P1.S7, P1.S9]
- touches: [src/autoresume/cli.py, tests/test_cli_tailor.py]
- read_first: [src/autoresume/cli.py, docs/design.md#tech stack and repo]
- acceptance:
  - `uv run autoresume tailor --jd <file> --archetype <id> --lang en --name <slug>` creates `$AUTORESUME_DATA_DIR/applications/<yyyy-mm-dd>_<slug>/` with `job_description.md`, `decision.json` and `resume.pdf`
  - `--model` picks the model, with a default set in one place in the code
  - the command prints the model, tokens and cost of the call
  - a resume over one page exits non-zero with a message giving the page count; the folder is still written
  - an existing folder is never overwritten: the command exits non-zero
  - tests replace `tailor` and the client with fakes, so they pass while P1.S8's tests are still xfail

### P1.S11 — [Human] First real runs and model comparison
- goal: You tailor your resume to two real job descriptions with two or three models, and note cost and quality, to pick Phase 1's default model.
- depends_on: [P1.S1, P1.S8, P1.S10, P0.S15]
- acceptance:
  - two application folders in `autoresume-data/applications/`, each with a one-page `resume.pdf`
  - `autoresume-data/notes/phase-1-models.md` compares the models tried (cost per run from the log, quality in your words) and names the default
  - the default model in the code matches it (a `Q-` PR if it changed)

### P1.S12 — Tests, stubs and brief for the add-experience interview
- goal: Failing tests, `TODO(PA)` stubs and a learning brief for the interview step behind `add-experience`, which asks questions until it can propose a valid bank entry.
- depends_on: [P1.S2, P1.S5]
- touches: [src/autoresume/agents/interview.py, tests/agents/test_interview.py, docs/learning/P1.S13.md]
- read_first: [src/autoresume/bank/schema.py, docs/decisions/2026-11-25-core-by-user-plumbing-by-agents.md#decision]
- acceptance:
  - a stub `next_turn(history, bank, client, model)` returns either a question to ask or a draft entry (a bullet, an experience or a project) validated against the bank schema, with a docstring of the expected behaviour and `TODO(PA)`
  - tests, using `FakeLLMClient`, cover: a question is returned while information is missing; a valid draft is returned once it is complete; an invalid draft is retried with the validation error; a draft reusing an existing id is rejected; a draft missing its FR or EN text is rejected
  - each test has a one-line docstring; every test is marked `xfail(strict=True)` and `uv run pytest` passes
  - `docs/learning/P1.S13.md` explains conversation state, when to stop asking, and validating structured output, links the API docs and lists common traps, with no solution code
- test_first: false
- notes: Depends on P1.S5 only because P1.S5 creates the `agents/` package.

### P1.S13 — [Human] Write the interview step
- goal: You write `next_turn`, so the model interviews you about an experience and proposes a bank entry only when it is complete and valid.
- depends_on: [P1.S12]
- acceptance:
  - every test in `tests/agents/test_interview.py` passes with its xfail marker removed
  - PR titled `P1.S13: …`, reviewed by pr-reviewer, merged
- notes: Coached: read `docs/learning/P1.S13.md`; Bob coaches by levels (hint, explanation, example) and writes none of the code.

### P1.S14 — `add-experience` command
- goal: `autoresume add-experience` runs the interview in the terminal, shows the draft entry, and on your OK saves it to the bank, so the bank grows without hand-editing YAML.
- depends_on: [P1.S10, P1.S12]
- touches: [src/autoresume/cli.py, src/autoresume/bank/writer.py, tests/test_cli_add_experience.py, tests/bank/test_writer.py]
- read_first: [src/autoresume/bank/loader.py, docs/decisions/2026-11-23-bank-schema.md#decision]
- acceptance:
  - the command loops: prints the question, reads your answer, until `next_turn` returns a draft; then shows it in FR and EN and asks to save, edit or cancel
  - on save, the entry is written to the bank file the layout puts it in, other entries and comments are kept, and `load_bank` on the result succeeds
  - if the bank no longer loads after the write, the file is restored and the command exits non-zero with the error
  - cancel writes nothing
  - tests replace `next_turn` with a fake, so they pass while P1.S13's tests are still xfail
- notes: Keeping YAML comments may need `ruamel.yaml`; add it with `uv add` if so. `bank/writer.py` is agent-owned, like `loader.py`.

### P1.Z — Cleanup
- goal: Remove duplication and simplify the phase's agent-written code, with no change in behaviour.
- depends_on: [P1.S2, P1.S3, P1.S5, P1.S7, P1.S9, P1.S10, P1.S12, P1.S14]
- touches: [src/autoresume/llm/, src/autoresume/cli.py, src/autoresume/render/, src/autoresume/bank/writer.py, tests/]
- acceptance:
  - no duplicated helpers across the phase; all existing tests pass unchanged
  - `gh pr diff <n> --name-only` lists no file under `src/autoresume/agents/` and not `src/autoresume/bank/schema.py`
- test_first: false
- notes: Deliberately does not wait for the [Human] code tasks; it leaves your code alone.

### P1.D — Docs
- goal: README sections for `tailor` and `add-experience` with the OpenRouter setup, and a Phase 1 entry in the CHANGELOG.
- depends_on: [P1.S2, P1.S3, P1.S5, P1.S7, P1.S9, P1.S10, P1.S12, P1.S14]
- touches: [README.md, CHANGELOG.md]
- acceptance:
  - README covers setting OPENROUTER_API_KEY, `autoresume tailor` and `autoresume add-experience`, and where the call log is written
  - CHANGELOG has a Phase 1 entry
- agent: docs-writer
