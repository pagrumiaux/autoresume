"""Spec for the bank `education` list (P0.S18, docs/decisions/2026-11-24-education-on-bank.md).

Goal: The bank has an `education` list (institution, degree, optional topic, start and end
years), so the resume template prints degrees from the bank like everything else.
"""

import copy
from datetime import date
from typing import Any

import pytest
from pydantic import ValidationError

from autoresume.bank import Bank

INSTITUTION = "Université d'Exemple"

BANK: dict[str, Any] = {
    "skills": [{"id": "pytorch", "label": {"fr": "PyTorch", "en": "PyTorch"}, "category": "ml"}],
    "education": [
        {
            "institution": INSTITUTION,
            "degree": {"fr": "Master informatique", "en": "MSc Computer Science"},
            "start": 2018,
            "end": 2020,
        }
    ],
    "experiences": [],
    "projects": [],
}


def bank_dict() -> dict[str, Any]:
    return copy.deepcopy(BANK)


def with_education(**changes: Any) -> dict[str, Any]:
    data = bank_dict()
    data["education"][0].update(changes)
    return data


def test_education_entry_parses_with_typed_fields() -> None:
    """A valid entry exposes institution, FR/EN degree and integer years."""
    entry = Bank.model_validate(bank_dict()).education[0]
    assert entry.institution == INSTITUTION
    assert entry.degree.fr == "Master informatique"
    assert entry.degree.en == "MSc Computer Science"
    assert (entry.start, entry.end) == (2018, 2020)
    assert entry.topic is None


def test_education_topic_is_optional_fr_en_text() -> None:
    """A topic given in FR and EN is kept."""
    topic = {"fr": "Apprentissage profond", "en": "Deep learning"}
    entry = Bank.model_validate(with_education(topic=topic)).education[0]
    assert entry.topic is not None
    assert entry.topic.en == "Deep learning"


def test_education_topic_missing_one_language_is_rejected() -> None:
    """A topic must have both fr and en."""
    with pytest.raises(ValidationError, match="en"):
        Bank.model_validate(with_education(topic={"fr": "Apprentissage"}))


def test_education_end_can_be_omitted_for_ongoing_programme() -> None:
    """An ongoing programme has no end year."""
    data = bank_dict()
    del data["education"][0]["end"]
    assert Bank.model_validate(data).education[0].end is None


def test_education_empty_list_is_accepted() -> None:
    """The field is required, but an explicit empty list is a valid value."""
    data = bank_dict()
    data["education"] = []
    assert Bank.model_validate(data).education == []


def test_education_empty_institution_is_rejected() -> None:
    """The institution cannot be an empty string."""
    with pytest.raises(ValidationError, match="institution"):
        Bank.model_validate(with_education(institution=""))


def test_education_degree_missing_one_language_is_rejected() -> None:
    """The degree must have both fr and en."""
    with pytest.raises(ValidationError, match="en"):
        Bank.model_validate(with_education(degree={"fr": "Master"}))


def test_education_start_is_required() -> None:
    """An entry without a start year is rejected."""
    data = bank_dict()
    del data["education"][0]["start"]
    with pytest.raises(ValidationError, match="start"):
        Bank.model_validate(data)


def test_education_year_must_be_an_integer_not_a_full_date() -> None:
    """Years are integers: a YYYY-MM-DD date is rejected."""
    with pytest.raises(ValidationError, match="start"):
        Bank.model_validate(with_education(start=date(2018, 9, 1)))


@pytest.mark.parametrize("field", ["start", "end"])
@pytest.mark.parametrize("year", [1899, 2101])
def test_education_year_outside_1900_2100_is_rejected_naming_institution(
    field: str, year: int
) -> None:
    """A year out of range is rejected, and the error names the institution."""
    changes: dict[str, Any] = {field: year}
    if field == "start":
        changes["end"] = None
    with pytest.raises(ValidationError, match=INSTITUTION):
        Bank.model_validate(with_education(**changes))


@pytest.mark.parametrize("year", [1900, 2100])
def test_education_year_bounds_are_inclusive(year: int) -> None:
    """1900 and 2100 are accepted."""
    Bank.model_validate(with_education(start=year, end=year))


def test_education_start_after_end_is_rejected_naming_institution() -> None:
    """start > end is rejected, and the error names the institution."""
    with pytest.raises(ValidationError, match=INSTITUTION):
        Bank.model_validate(with_education(start=2021, end=2020))


def test_education_start_equal_to_end_is_accepted() -> None:
    """A one-year programme (start == end) is valid."""
    Bank.model_validate(with_education(start=2020, end=2020))


def test_education_unknown_key_is_rejected() -> None:
    """Typos in an education entry are errors, like everywhere else in the bank."""
    with pytest.raises(ValidationError, match="degre"):
        Bank.model_validate(with_education(degre="x"))


def test_bank_without_education_is_rejected_naming_the_field() -> None:
    """The education list is required."""
    data = bank_dict()
    del data["education"]
    with pytest.raises(ValidationError, match="education"):
        Bank.model_validate(data)
