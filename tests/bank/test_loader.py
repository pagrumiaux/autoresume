"""Tests for the bank loader (P0.S17).

Goal: Functions that read a bank directory (the layout chosen in P0.S5) from YAML into your
models, with errors that say which file and what is wrong.

Contract assumed (the task leaves it open): `load_bank(path)` returns `(bank, archetypes)`
with `archetypes` a dict keyed by archetype id; every failure raises `BankLoadError`
(from `autoresume.bank.loader`) whose message names the file.
"""

from pathlib import Path

import pytest

from autoresume.bank import Archetype, Bank
from autoresume.bank.loader import BankLoadError, load_bank

EXPERIENCE = """\
  - id: acme-2022
    org: Acme Labs
    role: {fr: Ingénieur, en: Engineer}
    start: 2022-03-01
    end: 2024-08-01
    bullets:
      - id: acme-denoiser
        tags: [pytorch]
        text: {fr: Débruiteur., en: Denoiser.}
"""

PROJECT = """\
  - id: toy-synth
    name: Toy Synth
    bullets:
      - id: toy-synth-vst
        tags: [pytorch]
        text: {fr: Synthé., en: Synth.}
"""

SKILLS = """\
skills:
  - id: pytorch
    label: {fr: PyTorch, en: PyTorch}
    category: ml
"""

BANK_YAML = f"{SKILLS}experiences:\n{EXPERIENCE}projects:\n{PROJECT}"

ROOT_ARCHETYPE = """\
id: research
description: Research roles
headline: {fr: Chercheur, en: Researcher}
skills_order: [pytorch]
bullets: [acme-denoiser]
projects: [toy-synth]
signals: [paper]
"""

VARIANT_ARCHETYPE = """\
id: research-audio
extends: research
description: Audio research
"""


def make_bank(
    tmp_path: Path, bank: str = BANK_YAML, archetypes: dict[str, str] | None = None
) -> Path:
    """Build a bank directory in tmp_path and return its path."""
    (tmp_path / "bank.yaml").write_text(bank, encoding="utf-8")
    (tmp_path / "archetypes").mkdir()
    for name, content in (archetypes or {"research": ROOT_ARCHETYPE}).items():
        (tmp_path / "archetypes" / f"{name}.yaml").write_text(content, encoding="utf-8")
    return tmp_path


def test_load_bank_returns_bank_and_archetypes_for_valid_directory(tmp_path):
    make_bank(
        tmp_path, archetypes={"research": ROOT_ARCHETYPE, "research-audio": VARIANT_ARCHETYPE}
    )
    bank, archetypes = load_bank(tmp_path)
    assert isinstance(bank, Bank)
    assert [b.id for b in bank.bullets()] == ["acme-denoiser", "toy-synth-vst"]
    assert set(archetypes) == {"research", "research-audio"}
    assert all(isinstance(a, Archetype) for a in archetypes.values())
    assert archetypes["research-audio"].extends == "research"


def test_load_bank_accepts_directory_without_archetypes(tmp_path):
    (tmp_path / "bank.yaml").write_text(BANK_YAML, encoding="utf-8")
    bank, archetypes = load_bank(tmp_path)
    assert isinstance(bank, Bank)
    assert archetypes == {}


def test_yaml_syntax_error_names_file_and_line(tmp_path):
    make_bank(tmp_path, bank="skills: [\nexperiences: {oops\n")
    with pytest.raises(BankLoadError, match=r"bank\.yaml") as exc:
        load_bank(tmp_path)
    assert "line" in str(exc.value).lower()


def test_yaml_syntax_error_in_archetype_names_that_file(tmp_path):
    make_bank(tmp_path, archetypes={"research": "id: research\nbullets: [a\n"})
    with pytest.raises(BankLoadError, match=r"research\.yaml"):
        load_bank(tmp_path)


def test_schema_violation_names_file_and_field(tmp_path):
    make_bank(tmp_path, bank=BANK_YAML.replace("category: ml", "categroy: ml"))
    with pytest.raises(BankLoadError, match=r"bank\.yaml") as exc:
        load_bank(tmp_path)
    assert "categroy" in str(exc.value) or "category" in str(exc.value)


def test_schema_violation_in_archetype_names_file_and_field(tmp_path):
    bad = ROOT_ARCHETYPE.replace("headline: {fr: Chercheur, en: Researcher}\n", "")
    make_bank(tmp_path, archetypes={"research": bad})
    with pytest.raises(BankLoadError, match=r"research\.yaml") as exc:
        load_bank(tmp_path)
    assert "headline" in str(exc.value)


def test_archetype_referencing_unknown_bullet_names_file_and_id(tmp_path):
    bad = ROOT_ARCHETYPE.replace("[acme-denoiser]", "[ghost-bullet]")
    make_bank(tmp_path, archetypes={"research": bad})
    with pytest.raises(BankLoadError, match=r"research\.yaml") as exc:
        load_bank(tmp_path)
    assert "ghost-bullet" in str(exc.value)


def test_missing_directory_raises_clear_error(tmp_path):
    with pytest.raises(BankLoadError, match="missing-dir"):
        load_bank(tmp_path / "missing-dir")


def test_missing_bank_yaml_raises_clear_error(tmp_path):
    (tmp_path / "archetypes").mkdir()
    with pytest.raises(BankLoadError, match=r"bank\.yaml"):
        load_bank(tmp_path)


def test_duplicate_experience_ids_rejected_naming_file_and_id(tmp_path):
    second = EXPERIENCE.replace("acme-denoiser", "other-bullet")  # same experience id
    bank = f"{SKILLS}experiences:\n{EXPERIENCE}{second}projects:\n{PROJECT}"
    make_bank(tmp_path, bank=bank, archetypes={})
    with pytest.raises(BankLoadError, match=r"bank\.yaml") as exc:
        load_bank(tmp_path)
    assert "acme-2022" in str(exc.value)


def test_duplicate_project_ids_rejected_naming_file_and_id(tmp_path):
    second = PROJECT.replace("toy-synth-vst", "other-bullet")  # same project id
    bank = f"{SKILLS}experiences:\n{EXPERIENCE}projects:\n{PROJECT}{second}"
    make_bank(tmp_path, bank=bank, archetypes={})
    with pytest.raises(BankLoadError, match=r"bank\.yaml") as exc:
        load_bank(tmp_path)
    assert "toy-synth" in str(exc.value)


def test_empty_extends_rejected_naming_file(tmp_path):
    bad = VARIANT_ARCHETYPE.replace("extends: research", 'extends: ""')
    make_bank(tmp_path, archetypes={"research": ROOT_ARCHETYPE, "research-audio": bad})
    with pytest.raises(BankLoadError, match=r"research-audio\.yaml") as exc:
        load_bank(tmp_path)
    assert "extends" in str(exc.value)
