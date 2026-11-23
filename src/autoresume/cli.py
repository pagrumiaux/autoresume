"""Command-line entry point."""

import typer

app = typer.Typer(help="Tailor your resume to a job description.", no_args_is_help=True)


@app.callback()
def main() -> None:
    """Tailor your resume to a job description."""
