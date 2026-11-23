"""Tests for P0.S9.

Goal: Three one-page resume layouts in Typst with hard-coded fake content, rendered to PDF,
so you can pick a design before the real template is built.
"""

import re
from pathlib import Path

import pytest
from pypdf import PdfReader

LAYOUTS = Path(__file__).resolve().parents[2] / "examples" / "layouts"


def _typ_files() -> list[Path]:
    return sorted(LAYOUTS.glob("*.typ"))


def test_three_typ_files_exist():
    assert len(_typ_files()) == 3


def test_each_typ_has_a_rendered_pdf():
    typs = _typ_files()
    assert typs
    for typ in typs:
        assert typ.with_suffix(".pdf").is_file(), f"missing PDF for {typ.name}"


@pytest.mark.parametrize("index", range(3))
def test_each_pdf_is_one_page(index):
    pdfs = sorted(LAYOUTS.glob("*.pdf"))
    assert len(pdfs) == 3
    assert len(PdfReader(pdfs[index]).pages) == 1


@pytest.mark.parametrize("index", range(3))
def test_each_pdf_text_is_extractable(index):
    pdfs = sorted(LAYOUTS.glob("*.pdf"))
    assert len(pdfs) == 3
    text = PdfReader(pdfs[index]).pages[0].extract_text()
    assert len(re.findall(r"[A-Za-z]{3,}", text)) >= 50


def test_readme_describes_each_direction():
    readme = LAYOUTS / "README.md"
    assert readme.is_file()
    text = readme.read_text()
    typs = _typ_files()
    assert len(typs) == 3
    for typ in typs:
        assert typ.stem in text, f"README does not mention {typ.stem}"
