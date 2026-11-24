"""Tests for render() and page_count() (P0.S12).

Goal: A function that turns a bank and an archetype into a PDF through the template, with a proper
FR/EN heading for every skill category, and a function that returns a PDF's page count, which later
agents use to check the one-page limit.

Assumptions: `render(bank, archetype, lang, out)` and `page_count(pdf)` are importable from
`autoresume.render`; paths are `pathlib.Path`; render compiles through `typst.compile(...)` with the
template data as JSON in `sys_inputs["data"]` (the P0.S11 contract), which some tests capture.
"""

import io
import json
import logging
from pathlib import Path

import pytest
import typst
from pypdf import PdfReader

from autoresume.bank.loader import load_bank
from autoresume.bank.schema import Archetype, Bank
from autoresume.render import page_count, render

ROOT = Path(__file__).resolve().parent.parent.parent
BANK_DIRS = [ROOT / "examples" / "bank", ROOT / "tests" / "fixtures" / "bank"]

HEADINGS = {
    "audio": ("Audio", "Audio"),
    "ml": ("Machine learning", "Machine learning"),
    "mlops": ("MLOps & engineering", "MLOps et ingénierie"),
    "programming": ("Programming", "Programmation"),
    "music": ("Music", "Musique"),
    "languages": ("Languages", "Langues"),
    "data": ("Data", "Données"),
}


def _cases() -> list:
    cases = []
    for bank_dir in BANK_DIRS:
        bank, archetypes = load_bank(bank_dir)
        for arch_id, arch in archetypes.items():
            for lang in ("fr", "en"):
                cases.append(
                    pytest.param(bank, arch, lang, id=f"{bank_dir.parent.name}-{arch_id}-{lang}")
                )
    return cases


def _text(pdf: Path) -> str:
    reader = PdfReader(io.BytesIO(pdf.read_bytes()))
    return " ".join(" ".join(p.extract_text() for p in reader.pages).split())


def _bank(skills: list[dict], bullets: int = 1, bullet_words: int = 8) -> tuple[Bank, Archetype]:
    """A small bank the test builds itself, with one skill per given {id, category}."""
    sentence = " ".join(["word"] * bullet_words)
    bullet_list = [
        {
            "id": f"b{i}",
            "tags": [],
            "text": {"fr": f"Puce {i} {sentence}.", "en": f"Bullet {i} {sentence}."},
        }
        for i in range(bullets)
    ]
    bank = Bank.model_validate(
        {
            "skills": [
                {"id": s["id"], "label": {"fr": s["id"], "en": s["id"]}, "category": s["category"]}
                for s in skills
            ],
            "education": [],
            "experiences": [
                {
                    "id": "exp",
                    "org": "Acme",
                    "role": {"fr": "Dev", "en": "Dev"},
                    "start": "2020-01-01",
                    "bullets": bullet_list,
                }
            ],
            "projects": [],
        }
    )
    archetype = Archetype.model_validate(
        {
            "id": "arch",
            "description": "Test archetype",
            "signals": [],
            "headline": {"fr": "Titre", "en": "Headline"},
            "skills_order": [s["id"] for s in skills],
            "bullets": [b["id"] for b in bullet_list],
            "projects": [],
        }
    )
    return bank, archetype


@pytest.fixture
def captured(monkeypatch):
    """Template data passed to typst.compile by render()."""
    seen: list[dict] = []
    real = typst.compile

    def spy(*args, **kwargs):
        seen.append(json.loads(kwargs["sys_inputs"]["data"]))
        return real(*args, **kwargs)

    monkeypatch.setattr(typst, "compile", spy)
    return seen


@pytest.mark.parametrize(("bank", "archetype", "lang"), _cases())
def test_render_writes_a_pdf_for_each_fake_archetype_in_fr_and_en(bank, archetype, lang, tmp_path):
    out = tmp_path / "resume.pdf"
    render(bank, archetype, lang, out)
    assert out.read_bytes().startswith(b"%PDF")


@pytest.mark.parametrize(("bank", "archetype", "lang"), _cases())
def test_rendered_pdf_contains_each_education_entry(bank, archetype, lang, tmp_path):
    out = tmp_path / "resume.pdf"
    render(bank, archetype, lang, out)
    text = _text(out)
    assert bank.education
    for edu in bank.education:
        assert edu.institution in text
        assert getattr(edu.degree, lang) in text


@pytest.mark.parametrize(("bank", "archetype", "lang"), _cases())
def test_page_count_is_one_for_fake_bank_outputs(bank, archetype, lang, tmp_path):
    out = tmp_path / "resume.pdf"
    render(bank, archetype, lang, out)
    assert page_count(out) == 1


def test_page_count_is_two_for_a_resume_that_overflows_the_page(tmp_path):
    bank, archetype = _bank([{"id": "python", "category": "languages"}], bullets=80)
    out = tmp_path / "long.pdf"
    render(bank, archetype, "en", out)
    assert page_count(out) == 2


@pytest.mark.parametrize("lang", ["fr", "en"])
def test_category_titles_cover_every_known_category_in_the_requested_language(
    lang, captured, tmp_path
):
    skills = [{"id": f"s-{c}", "category": c} for c in HEADINGS]
    bank, archetype = _bank(skills)
    render(bank, archetype, lang, tmp_path / "r.pdf")
    titles = captured[-1]["category_titles"]
    idx = 0 if lang == "en" else 1
    for category, headings in HEADINGS.items():
        assert titles[category] == headings[idx]


def test_unknown_category_gets_a_tidied_heading_and_a_warning(captured, tmp_path, caplog):
    bank, archetype = _bank([{"id": "teamwork", "category": "soft-skills"}])
    out = tmp_path / "r.pdf"
    with caplog.at_level(logging.WARNING):
        render(bank, archetype, "en", out)
    assert captured[-1]["category_titles"]["soft-skills"] == "Soft skills"
    assert any(
        r.levelno >= logging.WARNING and "soft-skills" in r.getMessage() for r in caplog.records
    )
    assert out.read_bytes().startswith(b"%PDF")


def test_known_categories_log_no_warning(captured, tmp_path, caplog):
    bank, archetype = _bank([{"id": "python", "category": "languages"}])
    with caplog.at_level(logging.WARNING):
        render(bank, archetype, "en", tmp_path / "r.pdf")
    assert not [r for r in caplog.records if r.levelno >= logging.WARNING]


def test_soft_skill_is_left_out_of_the_template_data(captured, tmp_path):
    bank, archetype = _bank(
        [{"id": "python", "category": "languages"}, {"id": "mentoring", "category": "soft"}]
    )
    render(bank, archetype, "en", tmp_path / "r.pdf")
    data = captured[-1]
    labels = [s["label"] for s in data["skills"]]
    assert "python" in labels
    assert "mentoring" not in labels
    assert "soft" not in {s["category"] for s in data["skills"]}
    assert "soft" not in data.get("category_titles", {})
