"""Soft skills of the fake banks never reach the PDF (Q-soft-category, issue #20)."""

import pytest
from test_template import BANK_DIRS, _build_data, _compile, _text

from autoresume.bank.loader import load_bank


@pytest.mark.parametrize("bank_dir", BANK_DIRS, ids=lambda p: p.parent.name)
@pytest.mark.parametrize("lang", ["fr", "en"])
def test_fake_bank_soft_skills_are_absent_from_the_pdf(bank_dir, lang):
    bank, archetypes = load_bank(bank_dir)
    soft = [s for s in bank.skills if s.category == "soft"]
    assert soft, "fake bank has no skill of category 'soft'"
    assert not any(s.category == "soft-skills" for s in bank.skills)
    for archetype in archetypes.values():
        data = _build_data(bank, archetype, lang)
        assert any(s["category"] == "soft" for s in data["skills"])
        text = " ".join(_text(_compile(data)).split())
        for skill in soft:
            assert skill.label.model_dump()[lang] not in text
