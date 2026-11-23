from typer.testing import CliRunner

from autoresume.cli import app

runner = CliRunner()


def test_help_exits_zero() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "resume" in result.output.lower()
