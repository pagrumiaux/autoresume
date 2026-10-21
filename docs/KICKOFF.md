# Kickoff prompt for the first Claude Code session

## Before you start

1. Create two GitHub repos: `resume-agent` (public) and `resume-data` (private).
2. Clone both. Copy `CLAUDE.md` to the root of `resume-agent`, and the `docs/` folder into it.
3. In your shell profile: `export RESUME_DATA_DIR=/path/to/resume-data`.
4. Open `resume-agent` in Claude Code and paste the prompt below.

## Prompt to paste

```text
Read CLAUDE.md and docs/PLAN.md, then the notes in docs/decisions/.
We are starting phase 0 (foundation, no LLM). Use plan mode.

Break phase 0 into small tasks, each a branch and a PR. I expect roughly:
1. Scaffolding: uv project (src layout), ruff, pytest, pre-commit with a guard that
   blocks committing anything from RESUME_DATA_DIR, GitHub Actions CI, a minimal Typer CLI.
2. Bank schema design: do NOT write it. Propose two or three ways to model the experience
   bank and archetypes in Pydantic (bullets with ids, skill tags, FR/EN variants, dates,
   projects, archetype = headline + skills order + bullet ids + signals), with trade-offs.
   I will write the schema; you review it and write the tests.
3. Fake example data in examples/ and tests/fixtures/ that matches the schema.
4. Typst resume template, designed from scratch: clean, one page, ATS-friendly
   (real text, simple columns). Show me two or three layout directions first.
5. `render` command: bank + archetype -> PDF, plus a function that returns the page count.

Respect the ownership table in CLAUDE.md. Ask me before anything ambiguous, and explain
non-obvious choices so I learn the reasoning.
```

## After phase 0

Fill the bank with my real content in `resume-data`, then ask Claude (here or in Claude Code)
to draft the 3–4 seed archetypes from it. Refine them yourself and keep both versions.
