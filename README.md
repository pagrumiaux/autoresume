# autoresume

`autoresume` tailors a resume to a job description. It selects and orders content from a verified **experience bank** instead of inventing new claims. Phase 0 provides the bank format, the Typst resume layout, and a `render` command. Tailoring to a job description is not implemented yet.

## Install

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```sh
uv sync
uv run autoresume --help
```

## Data directory

Your personal bank lives outside this repository, in a directory you choose (for example a private `autoresume-data` repo). Point the tool at it with an environment variable:

```sh
export AUTORESUME_DATA_DIR=/path/to/autoresume-data
```

Never commit real resume content to this repo. The data guard in pre-commit blocks any staged file under `AUTORESUME_DATA_DIR`.

## Render a resume

`render` writes a one-page PDF for an archetype. Without `--bank`, it reads the bank from `AUTORESUME_DATA_DIR`.

```sh
uv run autoresume render --archetype data-engineer --out resume.pdf
```

Options:

- `--archetype` (required): archetype id, as defined in the bank's `archetypes/` directory.
- `--out` (required): output PDF path.
- `--lang`: `en` (default) or `fr`.
- `--bank`: bank directory. Defaults to `$AUTORESUME_DATA_DIR`.

To try it without personal data, use the fictional bank in `examples/bank`:

```sh
AUTORESUME_DATA_DIR=examples/bank uv run autoresume render --archetype data-engineer --out /tmp/example.pdf
```

Known limits in Phase 0: the output has no name or contact block yet (identity is not read from the bank), and `soft` skills are never printed.

## Development

```sh
uv run pytest
uv run ruff check
uv run ruff format
uv run pre-commit run --all-files
```

Design notes live in `docs/` (`design.md`, and `decisions/` for lasting choices).
