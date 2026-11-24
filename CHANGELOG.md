# Changelog

## Phase 0: foundations

- Project skeleton: installable with `uv sync`, `autoresume` command with `--help`.
- Experience bank format: skills, bullets, education, projects and archetypes, loaded and validated from YAML.
- Fictional example bank in `examples/bank` for demos and tests.
- Resume layout in Typst, in English and French, with a sidebar design. Soft skills are not printed.
- `autoresume render --archetype <id> --out <file.pdf>` renders a resume from a bank, reading it from `AUTORESUME_DATA_DIR` by default. Accepts `--lang en|fr` and `--bank`.
- Guardrails: pre-commit blocks commits of files under the data directory, and CI runs lint and tests on every pull request.
