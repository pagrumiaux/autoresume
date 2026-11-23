"""Tests for the fake example data (P0.S8).

Goal: A small fake bank and fake archetypes for a fictional person, valid against the schema,
for tests and demos without personal data.
"""

import re
from pathlib import Path

import pytest

from autoresume.bank.loader import load_bank

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / "examples" / "bank"
FIXTURES = ROOT / "tests" / "fixtures"
BANK_DIRS = [EXAMPLES, FIXTURES]


def _bank_dirs_under(base: Path) -> list[Path]:
    """Every directory below `base` (or `base` itself) holding a bank.yaml."""
    return sorted(p.parent for p in base.rglob("bank.yaml"))


def test_examples_bank_directory_exists_and_loads():
    bank, _ = load_bank(EXAMPLES)
    assert bank.experiences


def test_fixtures_directory_has_a_bank_that_loads():
    dirs = _bank_dirs_under(FIXTURES)
    assert dirs, "tests/fixtures/ holds no bank.yaml"
    bank, _ = load_bank(dirs[0])
    assert bank.experiences


def test_every_bank_under_examples_and_fixtures_loads_without_error():
    dirs = _bank_dirs_under(ROOT / "examples") + _bank_dirs_under(FIXTURES)
    assert EXAMPLES in dirs
    for d in dirs:
        load_bank(d)


def test_examples_bank_has_three_experiences_and_two_projects():
    bank, _ = load_bank(EXAMPLES)
    assert len(bank.experiences) == 3
    assert len(bank.projects) == 2


def test_examples_bank_has_fifteen_to_twenty_bullets():
    bank, _ = load_bank(EXAMPLES)
    assert 15 <= len(bank.bullets()) <= 20


def test_examples_bank_has_twelve_to_fifteen_skills_in_three_categories():
    bank, _ = load_bank(EXAMPLES)
    assert 12 <= len(bank.skills) <= 15
    assert len({s.category for s in bank.skills}) == 3


def test_examples_bank_has_fr_and_en_text_on_every_entry():
    bank, _ = load_bank(EXAMPLES)
    texts = [s.label for s in bank.skills]
    texts += [e.role for e in bank.experiences]
    texts += [b.text for b in bank.bullets()]
    assert texts
    for text in texts:
        assert text.fr.strip()
        assert text.en.strip()


def test_examples_bullets_are_really_translated_not_copied():
    bank, _ = load_bank(EXAMPLES)
    for bullet in bank.bullets():
        assert bullet.text.fr != bullet.text.en, bullet.id


def test_examples_bank_has_two_archetypes():
    _, archetypes = load_bank(EXAMPLES)
    assert len(archetypes) == 2


def test_examples_archetypes_have_a_headline_in_both_languages():
    _, archetypes = load_bank(EXAMPLES)
    for archetype in archetypes.values():
        if archetype.extends is None:
            assert archetype.headline is not None
            assert archetype.headline.fr and archetype.headline.en


def test_fixtures_bank_has_exactly_one_archetype():
    dirs = _bank_dirs_under(FIXTURES)
    assert dirs
    _, archetypes = load_bank(dirs[0])
    assert len(archetypes) == 1


def test_fixtures_bank_is_smaller_than_examples_bank():
    dirs = _bank_dirs_under(FIXTURES)
    assert dirs
    small, _ = load_bank(dirs[0])
    big, _ = load_bank(EXAMPLES)
    assert small.experiences
    assert len(small.bullets()) < len(big.bullets())
    assert len(small.experiences) <= len(big.experiences)


def _all_strings(base: Path) -> list[str]:
    return [p.read_text(encoding="utf-8") for p in base.rglob("*.yaml")]


@pytest.mark.parametrize("base", BANK_DIRS, ids=["examples", "fixtures"])
def test_fake_data_has_no_contact_details(base):
    """Fictional content: no emails, phone numbers or URLs of a real person."""
    files = _all_strings(base)
    assert files, f"no YAML under {base}"
    for content in files:
        assert not re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", content), "email address"
        assert not re.search(r"https?://|www\.|linkedin\.com|github\.com", content), "URL"
        assert not re.search(r"\+\d[\d .-]{7,}\d|\b0\d([ .-]?\d{2}){4}\b", content), "phone number"
