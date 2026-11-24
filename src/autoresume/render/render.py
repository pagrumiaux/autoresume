"""Render a bank and an archetype to a PDF (stub: P0.S12 not implemented yet)."""

from pathlib import Path

from autoresume.bank.schema import Archetype, Bank


def render(bank: Bank, archetype: Archetype, lang: str, out: Path) -> None:
    """Write the resume PDF to `out`."""
    raise NotImplementedError


def page_count(pdf: Path) -> int:
    """Return the number of pages of the PDF at `pdf`."""
    raise NotImplementedError
