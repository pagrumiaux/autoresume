"""Tests for the resume Typst template (P0.S11).

Goal: The chosen layout as a Typst template that reads resume data instead of hard-coded text,
in FR or EN.

Contract assumed here (the task does not fix it; P0.S12 builds this data from a bank):
- the template is `src/autoresume/render/templates/resume.typ`;
- it reads one JSON string from the Typst input `data` (`sys.inputs.data`);
- the data is already resolved to one language (plain strings, not {fr, en} pairs), with
  `lang` ("fr" or "en") used for section titles. Shape: see `_build_data`.
"""

import io
import json
from pathlib import Path

import pytest
import typst
from pypdf import PdfReader

from autoresume.bank.loader import load_bank
from autoresume.bank.schema import Archetype, Bank

ROOT = Path(__file__).resolve().parent.parent.parent
TEMPLATE = ROOT / "src" / "autoresume" / "render" / "templates" / "resume.typ"
BANK_DIRS = [ROOT / "examples" / "bank", ROOT / "tests" / "fixtures" / "bank"]

IDENTITY = {
    "name": "Jane Doe",
    "title": "Data Engineer",
    "phone": "+33 6 00 00 00 00",
    "website": "janedoe.example.org",
    "github": "github.com/janedoe",
    "scholar": "scholar.example.org/janedoe",
    "music": "music.example.org/janedoe",
}


def _build_data(bank: Bank, archetype: Archetype, lang: str) -> dict:
    """Hand-build template data from a bank and an archetype (what P0.S12 will automate)."""
    chosen = list(archetype.bullets or [])
    skills = {s.id: s for s in bank.skills}
    experiences = []
    for exp in bank.experiences:
        bullets = [b.text.model_dump()[lang] for b in exp.bullets if b.id in chosen]
        if bullets:
            experiences.append(
                {
                    "org": exp.org,
                    "role": exp.role.model_dump()[lang],
                    "start": exp.start.year,
                    "end": exp.end.year if exp.end else None,
                    "bullets": bullets,
                }
            )
    projects = [
        {
            "name": p.name,
            "bullets": [b.text.model_dump()[lang] for b in p.bullets if b.id in chosen],
        }
        for p in bank.projects
        if p.id in (archetype.projects or [])
    ]
    return {
        "lang": lang,
        **IDENTITY,
        "headline": archetype.headline.model_dump()[lang],
        "skills": [
            {"label": skills[i].label.model_dump()[lang], "category": skills[i].category}
            for i in (archetype.skills_order or [])
        ],
        "education": [
            {
                "institution": e.institution,
                "degree": e.degree.model_dump()[lang],
                "topic": e.topic.model_dump()[lang] if e.topic else None,
                "start": e.start,
                "end": e.end,
            }
            for e in bank.education
        ],
        "experiences": experiences,
        "projects": projects,
    }


def _compile(data: dict) -> PdfReader:
    assert TEMPLATE.is_file(), f"template missing: {TEMPLATE}"
    pdf = typst.compile(str(TEMPLATE), root=str(ROOT), sys_inputs={"data": json.dumps(data)})
    return PdfReader(io.BytesIO(pdf))


def _text(reader: PdfReader) -> str:
    return "\n".join(page.extract_text() for page in reader.pages)


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


def _example_data(lang: str = "en") -> dict:
    bank, archetypes = load_bank(BANK_DIRS[0])
    return _build_data(bank, archetypes["data-engineer"], lang)


@pytest.mark.parametrize(("bank", "archetype", "lang"), _cases())
def test_fake_bank_and_each_archetype_compile_to_one_page_in_fr_and_en(bank, archetype, lang):
    reader = _compile(_build_data(bank, archetype, lang))
    assert len(reader.pages) == 1


@pytest.mark.parametrize(("bank", "archetype", "lang"), _cases())
def test_pdf_text_is_extractable_with_pypdf(bank, archetype, lang):
    data = _build_data(bank, archetype, lang)
    text = " ".join(_text(_compile(data)).split())
    assert data["name"] in text
    for exp in data["experiences"]:
        assert exp["org"] in text
        # extraction may re-wrap lines; compare on the first words of the first bullet
        assert " ".join(exp["bullets"][0].split()[:4]) in text


@pytest.mark.parametrize("lang", ["fr", "en"])
def test_template_prints_each_education_entry(lang):
    data = _example_data(lang)
    assert len(data["education"]) >= 2
    text = " ".join(_text(_compile(data)).split())
    for edu in data["education"]:
        assert edu["institution"] in text
        assert edu["degree"] in text
        assert str(edu["start"]) in text
        if edu["end"] is not None:
            assert str(edu["end"]) in text


def test_education_without_end_year_prints_start_and_no_placeholder():
    data = _example_data()
    data["education"] = [
        {
            "institution": "Ongoing Institute",
            "degree": "PhD Examples",
            "topic": None,
            "start": 2031,
            "end": None,
        }
    ]
    text = _text(_compile(data))
    assert "Ongoing Institute" in text
    assert "PhD Examples" in text
    assert "2031" in text
    assert "None" not in text
    assert "null" not in text


def test_empty_education_list_still_compiles_to_one_page():
    data = _example_data()
    data["education"] = []
    assert len(_compile(data).pages) == 1


def test_soft_skills_are_never_rendered():
    data = _example_data()
    data["skills"] = [
        {"label": "VisibleHardSkill", "category": "languages"},
        {"label": "HiddenSoftSkillXyz", "category": "soft"},
    ]
    text = _text(_compile(data))
    assert "VisibleHardSkill" in text
    assert "HiddenSoftSkillXyz" not in text


def test_soft_skills_are_hidden_in_fr_too():
    data = _example_data("fr")
    data["skills"] = [
        {"label": "CompetenceDure", "category": "languages"},
        {"label": "CompetenceSouplesseQwx", "category": "soft"},
    ]
    text = _text(_compile(data))
    assert "CompetenceDure" in text
    assert "CompetenceSouplesseQwx" not in text


def test_identity_card_prints_name_title_phone_website_and_links():
    text = " ".join(_text(_compile(_example_data())).split())
    for key in ("name", "title", "phone", "website", "github", "scholar", "music"):
        assert IDENTITY[key] in text, key


def test_identity_card_omits_a_link_that_is_not_given():
    data = _example_data()
    data["scholar"] = None
    text = " ".join(_text(_compile(data)).split())
    assert IDENTITY["scholar"] not in text
    assert "None" not in text
    assert "null" not in text


@pytest.mark.parametrize(
    ("lang", "present", "absent"),
    [
        ("en", ["Skills", "Education", "Experience", "Projects"], ["Compétences", "Formation"]),
        ("fr", ["Compétences", "Formation", "Expérience", "Projets"], ["Skills", "Education"]),
    ],
)
def test_section_titles_follow_the_language(lang, present, absent):
    data = _example_data(lang)
    data["category_titles"] = {"soft-skills": "Savoir-etre" if lang == "fr" else "Interpersonal"}
    text = _text(_compile(data)).lower()
    assert ("savoir-etre" if lang == "fr" else "interpersonal") in text
    for title in present:
        assert title.lower() in text
    for title in absent:
        assert title.lower() not in text


def test_template_prints_data_it_is_given_not_hard_coded_text():
    data = _example_data()
    data["name"] = "Zed Quuxington"
    text = _text(_compile(data))
    assert "Zed Quuxington" in text
    assert "Jane Doe" not in text


def test_category_heading_comes_from_category_titles_else_raw_id():
    data = _example_data()
    data["skills"] = [
        {"label": "Kubeflow", "category": "mlops"},
        {"label": "Zebra", "category": "rawcat"},
    ]
    data["category_titles"] = {"mlops": "ML Operations"}
    text = _text(_compile(data))
    assert "ML Operations" in text
    assert "rawcat" in text
