"""Render a bank and an archetype to a PDF through the Typst template."""

import json
from pathlib import Path

import typst
from pypdf import PdfReader

from autoresume.bank.schema import Archetype, Bank
from autoresume.render.headings import category_heading

TEMPLATE = Path(__file__).resolve().parent / "templates" / "resume.typ"
ROOT = TEMPLATE.parent

# Skills of this category only tag bullets: never printed
# (docs/decisions/2026-11-24-soft-skills-not-rendered.md).
HIDDEN_CATEGORY = "soft"


def _build_data(bank: Bank, archetype: Archetype, lang: str) -> dict:
    """Resolve the bank and archetype to the one-language data the template reads."""
    chosen = archetype.bullets if isinstance(archetype.bullets, list) else []
    by_id = {s.id: s for s in bank.skills}
    skills = [
        by_id[i] for i in archetype.skills_order or [] if by_id[i].category != HIDDEN_CATEGORY
    ]
    experiences = []
    for exp in bank.experiences:
        bullets = [getattr(b.text, lang) for b in exp.bullets if b.id in chosen]
        if bullets:
            experiences.append(
                {
                    "org": exp.org,
                    "role": getattr(exp.role, lang),
                    "start": exp.start.year,
                    "end": exp.end.year if exp.end else None,
                    "bullets": bullets,
                }
            )
    projects = [
        {"name": p.name, "bullets": [getattr(b.text, lang) for b in p.bullets if b.id in chosen]}
        for p in bank.projects
        if p.id in (archetype.projects or [])
    ]
    categories = dict.fromkeys(s.category for s in skills)
    return {
        "lang": lang,
        # No identity in the bank yet: the template needs these keys, so they are blank.
        "name": "",
        "title": "",
        "phone": None,
        "website": None,
        "github": None,
        "scholar": None,
        "music": None,
        "headline": getattr(archetype.headline, lang) if archetype.headline else "",
        "skills": [{"label": getattr(s.label, lang), "category": s.category} for s in skills],
        "category_titles": {c: category_heading(c, lang) for c in categories},
        "education": [
            {
                "institution": e.institution,
                "degree": getattr(e.degree, lang),
                "topic": getattr(e.topic, lang) if e.topic else None,
                "start": e.start,
                "end": e.end,
            }
            for e in bank.education
        ],
        "experiences": experiences,
        "projects": projects,
    }


def render(bank: Bank, archetype: Archetype, lang: str, out: Path) -> None:
    """Write the resume PDF of `archetype` in `lang` ("fr" or "en") to `out`."""
    data = _build_data(bank, archetype, lang)
    typst.compile(
        str(TEMPLATE),
        output=str(out),
        root=str(ROOT),
        sys_inputs={"data": json.dumps(data)},
    )


def page_count(pdf: Path) -> int:
    """Return the number of pages of the PDF at `pdf`."""
    return len(PdfReader(pdf).pages)
