"""Bank YAML loader (stub: P0.S17 not implemented yet)."""

from pathlib import Path

from autoresume.bank.schema import Archetype, Bank


class BankLoadError(Exception):
    """Raised when a bank directory cannot be loaded; the message names the file."""


def load_bank(path: Path) -> tuple[Bank, dict[str, Archetype]]:
    """Load `bank.yaml` and `archetypes/*.yaml` from `path`."""
    raise NotImplementedError
