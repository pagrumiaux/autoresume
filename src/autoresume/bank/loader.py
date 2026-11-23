"""Bank YAML loader: reads the directory layout of docs/decisions/2026-11-23-bank-schema.md.

Every failure is raised as `BankLoadError` with a message that starts with the file path, so
the user never sees a raw traceback from PyYAML or Pydantic.
"""

from collections import Counter
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from autoresume.bank.schema import Archetype, Bank


class BankLoadError(Exception):
    """Raised when a bank directory cannot be loaded; the message names the file."""


def load_bank(path: Path) -> tuple[Bank, dict[str, Archetype]]:
    """Load `bank.yaml` and `archetypes/*.yaml` from `path`.

    Returns the bank and the archetypes keyed by id. A missing `archetypes/` directory gives an
    empty dict. Raises BankLoadError (naming the file) on any problem.
    """
    path = Path(path)
    if not path.is_dir():
        raise BankLoadError(f"{path}: bank directory not found")
    bank_file = path / "bank.yaml"
    if not bank_file.is_file():
        raise BankLoadError(f"{bank_file}: file not found")

    bank_data = _read_yaml(bank_file)
    bank = _validate(Bank, bank_data, bank_file)
    _reject_duplicate_ids(bank, bank_file)

    archetypes: dict[str, Archetype] = {}
    archetype_dir = path / "archetypes"
    if archetype_dir.is_dir():
        for file in sorted(archetype_dir.glob("*.yaml")):
            archetype = _validate(Archetype, _read_yaml(file), file)
            _check_archetype(archetype, file, bank)
            archetypes[archetype.id] = archetype
    for file_id, archetype in archetypes.items():
        if archetype.extends is not None and archetype.extends not in archetypes:
            raise BankLoadError(
                f"{archetype_dir / (file_id + '.yaml')}: extends unknown archetype "
                f"{archetype.extends!r}"
            )
    return bank, archetypes


def _read_yaml(file: Path) -> Any:
    """Parse one YAML file; syntax errors name the file and line."""
    try:
        return yaml.safe_load(file.read_text(encoding="utf-8"))
    except yaml.MarkedYAMLError as exc:
        mark = exc.problem_mark
        where = f"line {mark.line + 1}, column {mark.column + 1}" if mark else "unknown line"
        raise BankLoadError(f"{file}: YAML syntax error at {where}: {exc.problem}") from exc
    except (yaml.YAMLError, OSError, UnicodeDecodeError) as exc:
        raise BankLoadError(f"{file}: cannot read file: {exc}") from exc


def _validate[M: (Bank, Archetype)](model: type[M], data: Any, file: Path) -> M:
    """Build `model` from parsed YAML; schema errors name the file and each invalid field."""
    try:
        return model.model_validate(data)
    except ValidationError as exc:
        problems = "; ".join(
            f"{'.'.join(str(p) for p in err['loc']) or '<root>'}: {err['msg']}"
            for err in exc.errors()
        )
        raise BankLoadError(f"{file}: invalid bank data: {problems}") from exc


def _reject_duplicate_ids(bank: Bank, file: Path) -> None:
    """Experience and project ids must be unique (the schema only checks skills and bullets)."""
    for kind, ids in (
        ("experience", [e.id for e in bank.experiences]),
        ("project", [p.id for p in bank.projects]),
    ):
        for id_, count in Counter(ids).items():
            if count > 1:
                raise BankLoadError(f"{file}: duplicate {kind} id: {id_!r}")


def _check_archetype(archetype: Archetype, file: Path, bank: Bank) -> None:
    """Check file name = id, a non-empty `extends`, and references that exist in the bank."""
    if file.stem != archetype.id:
        raise BankLoadError(f"{file}: archetype id {archetype.id!r} must match the file name")
    if archetype.extends is not None and not archetype.extends.strip():
        raise BankLoadError(f"{file}: extends must not be empty (omit it for a root archetype)")
    try:
        bank.check_archetype(archetype)
    except ValueError as exc:
        raise BankLoadError(f"{file}: {exc}") from exc
