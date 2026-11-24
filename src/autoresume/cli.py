"""Command-line entry point."""

import os
from pathlib import Path
from typing import Annotated, NoReturn

import typer

from autoresume.bank.loader import BankLoadError, load_bank
from autoresume.render.render import render as render_pdf

app = typer.Typer(help="Tailor your resume to a job description.", no_args_is_help=True)


@app.callback()
def main() -> None:
    """Tailor your resume to a job description."""


def _fail(message: str) -> NoReturn:
    typer.echo(message, err=True)
    raise SystemExit(1)


@app.command()
def render(
    archetype: Annotated[str, typer.Option(help="Archetype id to render.")],
    out: Annotated[Path, typer.Option(help="Output PDF path.")],
    lang: Annotated[str, typer.Option(help="Language: en or fr.")] = "en",
    bank: Annotated[
        Path | None, typer.Option(help="Bank directory (default: $AUTORESUME_DATA_DIR).")
    ] = None,
) -> None:
    """Render the resume of an archetype to a PDF."""
    if lang not in ("en", "fr"):
        _fail(f"Invalid --lang {lang!r}: expected 'en' or 'fr'.")
    if bank is None:
        env = os.environ.get("AUTORESUME_DATA_DIR")
        if not env:
            _fail("No bank given: pass --bank or set AUTORESUME_DATA_DIR.")
        bank = Path(env)
    try:
        loaded, archetypes = load_bank(bank)
    except BankLoadError as exc:
        _fail(f"Invalid bank: {exc}")
    if archetype not in archetypes:
        _fail(f"Unknown archetype {archetype!r}. Available: {', '.join(sorted(archetypes))}")
    render_pdf(loaded, archetypes[archetype], lang, out)
    typer.echo(f"Wrote {out}")
