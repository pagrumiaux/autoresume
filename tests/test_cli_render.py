"""Tests for the `render` command (P0.S13).

Goal: `autoresume render` exposes the render function on the command line, reading the bank from
`AUTORESUME_DATA_DIR` by default.
"""

from pathlib import Path

from typer.testing import CliRunner

from autoresume.cli import app
from autoresume.render import page_count

runner = CliRunner()
EXAMPLES = Path(__file__).resolve().parents[1] / "examples" / "bank"


def test_render_with_bank_option_writes_one_page_pdf(tmp_path, monkeypatch):
    monkeypatch.delenv("AUTORESUME_DATA_DIR", raising=False)
    out = tmp_path / "cv.pdf"
    result = runner.invoke(
        app,
        [
            "render",
            "--bank",
            str(EXAMPLES),
            "--archetype",
            "data-scientist",
            "--lang",
            "en",
            "--out",
            str(out),
        ],
    )
    assert result.exit_code == 0, result.output
    assert out.read_bytes().startswith(b"%PDF")
    assert page_count(out) == 1


def test_render_without_bank_reads_autoresume_data_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTORESUME_DATA_DIR", str(EXAMPLES))
    out = tmp_path / "cv.pdf"
    result = runner.invoke(
        app, ["render", "--archetype", "data-engineer", "--lang", "fr", "--out", str(out)]
    )
    assert result.exit_code == 0, result.output
    assert page_count(out) == 1


def test_render_without_bank_and_unset_env_exits_with_clear_message(tmp_path, monkeypatch):
    monkeypatch.delenv("AUTORESUME_DATA_DIR", raising=False)
    out = tmp_path / "cv.pdf"
    result = runner.invoke(
        app, ["render", "--archetype", "data-scientist", "--lang", "en", "--out", str(out)]
    )
    assert result.exit_code != 0
    assert "AUTORESUME_DATA_DIR" in result.output
    assert "Traceback" not in result.output
    assert isinstance(result.exception, SystemExit)
    assert not out.exists()


def test_render_invalid_bank_exits_nonzero_and_prints_error(tmp_path):
    bad = tmp_path / "bank"
    bad.mkdir()
    (bad / "bank.yaml").write_text("experiences: not-a-list\n", encoding="utf-8")
    out = tmp_path / "cv.pdf"
    result = runner.invoke(
        app,
        ["render", "--bank", str(bad), "--archetype", "x", "--lang", "en", "--out", str(out)],
    )
    assert result.exit_code != 0
    assert "bank.yaml" in result.output
    assert "Traceback" not in result.output
    assert isinstance(result.exception, SystemExit)
    assert not out.exists()
