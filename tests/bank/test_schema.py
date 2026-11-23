"""Spec for the bank and archetype schemas (docs/decisions/2026-11-23-bank-schema.md).

Spec for the schema; every test passes.
"""

import copy
from datetime import date
from typing import Any

import pytest
from pydantic import ValidationError

from autoresume.bank import Archetype, Bank, Text

BANK: dict[str, Any] = {
    "skills": [
        {"id": "pytorch", "label": {"fr": "PyTorch", "en": "PyTorch"}, "category": "ml"},
        {
            "id": "dsp",
            "label": {"fr": "Traitement du signal", "en": "Signal processing"},
            "category": "audio",
        },
    ],
    "experiences": [
        {
            "id": "acme-2022",
            "org": "Acme Labs",
            "role": {"fr": "Ingénieur recherche", "en": "Research engineer"},
            "start": date(2022, 3, 1),
            "end": date(2024, 8, 1),
            "bullets": [
                {
                    "id": "acme-2022-denoiser",
                    "tags": ["pytorch", "dsp"],
                    "text": {"fr": "Conception d'un débruiteur.", "en": "Designed a denoiser."},
                }
            ],
        }
    ],
    "projects": [
        {
            "id": "toy-synth",
            "name": "Toy Synth",
            "bullets": [
                {
                    "id": "toy-synth-vst",
                    "tags": ["dsp"],
                    "text": {"fr": "Synthé VST.", "en": "VST synth."},
                }
            ],
        }
    ],
}

ARCHETYPE: dict[str, Any] = {
    "id": "audio-ml",
    "description": "Audio ML research engineer roles.",
    "headline": {"fr": "Ingénieur ML audio", "en": "Audio ML research engineer"},
    "skills_order": ["pytorch", "dsp"],
    "bullets": ["acme-2022-denoiser"],
    "projects": ["toy-synth"],
    "signals": ["speech enhancement", "real-time"],
}


def bank_dict() -> dict[str, Any]:
    return copy.deepcopy(BANK)


def archetype_dict(**changes: Any) -> dict[str, Any]:
    return {**copy.deepcopy(ARCHETYPE), **changes}


# --- Bank: valid input ---


def test_valid_bank_parses_into_typed_models() -> None:
    """A valid bank dict parses and exposes nested typed entries."""
    bank = Bank.model_validate(bank_dict())
    assert bank.experiences[0].bullets[0].text.en == "Designed a denoiser."
    assert bank.projects[0].name == "Toy Synth"
    assert bank.skills[0].category == "ml"


def test_bullets_helper_flattens_jobs_and_projects() -> None:
    """bank.bullets() returns the bullets of jobs then projects, in file order."""
    bank = Bank.model_validate(bank_dict())
    assert [b.id for b in bank.bullets()] == ["acme-2022-denoiser", "toy-synth-vst"]


# --- Bank: bilingual text ---


def test_text_requires_french_and_english() -> None:
    """Every Text has both fr and en."""
    with pytest.raises(ValidationError):
        Text.model_validate({"fr": "Bonjour"})


def test_text_rejects_empty_string() -> None:
    """A Text with an empty fr or en string is rejected."""
    with pytest.raises(ValidationError):
        Text.model_validate({"fr": "", "en": "Hello"})


def test_bullet_without_english_text_is_rejected() -> None:
    """Every bullet has FR and EN text: a missing en is rejected."""
    data = bank_dict()
    del data["experiences"][0]["bullets"][0]["text"]["en"]
    with pytest.raises(ValidationError):
        Bank.model_validate(data)


def test_bullet_without_french_text_is_rejected() -> None:
    """Every bullet has FR and EN text: a missing fr is rejected."""
    data = bank_dict()
    del data["projects"][0]["bullets"][0]["text"]["fr"]
    with pytest.raises(ValidationError):
        Bank.model_validate(data)


def test_skill_label_requires_both_languages() -> None:
    """A skill label has FR and EN."""
    data = bank_dict()
    del data["skills"][0]["label"]["fr"]
    with pytest.raises(ValidationError):
        Bank.model_validate(data)


def test_experience_role_requires_both_languages() -> None:
    """An experience role has FR and EN."""
    data = bank_dict()
    del data["experiences"][0]["role"]["en"]
    with pytest.raises(ValidationError):
        Bank.model_validate(data)


# --- Bank: ids and tags ---


def test_duplicate_bullet_id_within_one_job_is_rejected() -> None:
    """Bullet ids are unique: two bullets of one job with the same id are rejected."""
    data = bank_dict()
    bullets = data["experiences"][0]["bullets"]
    bullets.append(copy.deepcopy(bullets[0]))
    with pytest.raises(ValidationError):
        Bank.model_validate(data)


def test_duplicate_bullet_id_across_job_and_project_is_rejected() -> None:
    """Bullet ids are unique across the whole bank, jobs and projects included."""
    data = bank_dict()
    data["projects"][0]["bullets"][0]["id"] = "acme-2022-denoiser"
    with pytest.raises(ValidationError):
        Bank.model_validate(data)


def test_unknown_skill_tag_is_rejected() -> None:
    """A bullet tag must be an existing skill id."""
    data = bank_dict()
    data["experiences"][0]["bullets"][0]["tags"].append("cobol")
    with pytest.raises(ValidationError):
        Bank.model_validate(data)


def test_duplicate_skill_id_is_rejected() -> None:
    """Skill ids are unique."""
    data = bank_dict()
    data["skills"].append(copy.deepcopy(data["skills"][0]))
    with pytest.raises(ValidationError):
        Bank.model_validate(data)


# --- Bank: dates and structure ---


def test_end_date_is_optional_for_ongoing_role() -> None:
    """An experience without end is valid and has end None."""
    data = bank_dict()
    del data["experiences"][0]["end"]
    bank = Bank.model_validate(data)
    assert bank.experiences[0].end is None


def test_start_date_is_required() -> None:
    """An experience must have a start date."""
    data = bank_dict()
    del data["experiences"][0]["start"]
    with pytest.raises(ValidationError):
        Bank.model_validate(data)


def test_dates_must_be_full_dates() -> None:
    """Dates are full YYYY-MM-DD: a bare year-month string is rejected."""
    data = bank_dict()
    data["experiences"][0]["start"] = "2022-03"
    with pytest.raises(ValidationError):
        Bank.model_validate(data)


def test_skill_has_no_level_field() -> None:
    """Skills have no levels: an unexpected `level` key is rejected."""
    data = bank_dict()
    data["skills"][0]["level"] = 5
    with pytest.raises(ValidationError):
        Bank.model_validate(data)


# --- Archetypes ---


def test_valid_archetype_parses() -> None:
    """A complete root archetype parses and exposes its fields."""
    arch = Archetype.model_validate(archetype_dict())
    assert arch.id == "audio-ml"
    assert arch.headline.en == "Audio ML research engineer"


def test_root_archetype_must_set_every_field() -> None:
    """A root archetype (no extends) with a missing field is rejected."""
    data = archetype_dict()
    del data["skills_order"]
    with pytest.raises(ValidationError):
        Archetype.model_validate(data)


def test_variant_archetype_may_set_only_differences() -> None:
    """A variant (extends set) may omit fields it inherits."""
    arch = Archetype.model_validate(
        {"id": "edge-audio", "extends": "audio-ml", "bullets": {"add": ["toy-synth-vst"]}}
    )
    assert arch.extends == "audio-ml"


def test_archetype_bullets_accept_add_remove_delta() -> None:
    """Archetype bullets accept an {add, remove} edit of the parent's list."""
    arch = Archetype.model_validate(
        {
            "id": "edge-audio",
            "extends": "audio-ml",
            "bullets": {"add": ["toy-synth-vst"], "remove": ["acme-2022-denoiser"]},
        }
    )
    assert arch.bullets.add == ["toy-synth-vst"]
    assert arch.bullets.remove == ["acme-2022-denoiser"]


def test_archetype_headline_requires_both_languages() -> None:
    """An archetype headline has FR and EN."""
    with pytest.raises(ValidationError):
        Archetype.model_validate(archetype_dict(headline={"en": "Audio ML"}))


def test_archetype_with_known_ids_passes_bank_check() -> None:
    """An archetype whose ids all exist in the bank passes check_archetype."""
    bank = Bank.model_validate(bank_dict())
    bank.check_archetype(Archetype.model_validate(archetype_dict()))


def test_archetype_with_unknown_bullet_id_is_rejected() -> None:
    """An archetype referencing an unknown bullet id is rejected."""
    bank = Bank.model_validate(bank_dict())
    arch = Archetype.model_validate(archetype_dict(bullets=["no-such-bullet"]))
    with pytest.raises(ValueError, match="no-such-bullet"):
        bank.check_archetype(arch)


def test_archetype_delta_with_unknown_bullet_id_is_rejected() -> None:
    """Ids inside an {add} delta are checked against the bank too."""
    bank = Bank.model_validate(bank_dict())
    arch = Archetype.model_validate(
        {"id": "v", "extends": "audio-ml", "bullets": {"add": ["no-such-bullet"]}}
    )
    with pytest.raises(ValueError, match="no-such-bullet"):
        bank.check_archetype(arch)


def test_archetype_with_unknown_skill_id_is_rejected() -> None:
    """An archetype skills_order entry must be an existing skill id."""
    bank = Bank.model_validate(bank_dict())
    arch = Archetype.model_validate(archetype_dict(skills_order=["cobol"]))
    with pytest.raises(ValueError, match="cobol"):
        bank.check_archetype(arch)


def test_archetype_with_unknown_project_id_is_rejected() -> None:
    """An archetype projects entry must be an existing project id."""
    bank = Bank.model_validate(bank_dict())
    arch = Archetype.model_validate(archetype_dict(projects=["no-such-project"]))
    with pytest.raises(ValueError, match="no-such-project"):
        bank.check_archetype(arch)
