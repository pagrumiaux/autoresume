"""Tests for the data guard.

Task P0.S3 goal: Pre-commit runs ruff and blocks any commit that stages a file from the data
dir, and GitHub Actions runs ruff and pytest on every PR, so personal data can't leak and main
stays green.

Assumed interface: `python scripts/check_no_data.py <file>...` (pre-commit passes the staged
file names as arguments); exit 1 and name the offending file on failure, exit 0 otherwise.
"""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "check_no_data.py"


def run_guard(files: list[Path], data_dir: Path | None) -> subprocess.CompletedProcess[str]:
    assert SCRIPT.exists(), "scripts/check_no_data.py is missing"
    env = {k: v for k, v in os.environ.items() if k != "AUTORESUME_DATA_DIR"}
    if data_dir is not None:
        env["AUTORESUME_DATA_DIR"] = str(data_dir)
    return subprocess.run(
        [sys.executable, str(SCRIPT), *map(str, files)],
        capture_output=True,
        text=True,
        env=env,
        cwd=ROOT,
    )


def test_guard_fails_and_names_file_under_data_dir(tmp_path: Path) -> None:
    data = tmp_path / "data"
    data.mkdir()
    leaked = data / "bank.yaml"
    leaked.write_text("secret: 1\n")
    result = run_guard([leaked], data)
    assert result.returncode != 0
    assert "bank.yaml" in result.stdout + result.stderr


def test_guard_fails_for_nested_file_in_data_dir(tmp_path: Path) -> None:
    data = tmp_path / "data"
    (data / "apps" / "acme").mkdir(parents=True)
    leaked = data / "apps" / "acme" / "letter.md"
    leaked.write_text("x")
    result = run_guard([leaked], data)
    assert result.returncode != 0
    assert "letter.md" in result.stdout + result.stderr


def test_guard_fails_when_path_resolves_into_data_dir_via_symlink(tmp_path: Path) -> None:
    data = tmp_path / "data"
    data.mkdir()
    (data / "cv.yaml").write_text("x")
    link = tmp_path / "innocent.yaml"
    link.symlink_to(data / "cv.yaml")
    result = run_guard([link], data)
    assert result.returncode != 0


def test_guard_fails_when_only_one_of_several_files_is_under_data_dir(tmp_path: Path) -> None:
    data = tmp_path / "data"
    data.mkdir()
    leaked = data / "lessons.yaml"
    leaked.write_text("x")
    ok = tmp_path / "other.py"
    ok.write_text("x")
    result = run_guard([ok, leaked], data)
    assert result.returncode != 0
    assert "lessons.yaml" in result.stdout + result.stderr


def test_guard_passes_when_no_file_is_under_data_dir(tmp_path: Path) -> None:
    data = tmp_path / "data"
    data.mkdir()
    other = tmp_path / "repo" / "a.py"
    other.parent.mkdir()
    other.write_text("x")
    assert run_guard([other], data).returncode == 0


def test_guard_does_not_confuse_sibling_dir_sharing_name_prefix(tmp_path: Path) -> None:
    data = tmp_path / "data"
    data.mkdir()
    sibling = tmp_path / "data-public" / "a.txt"
    sibling.parent.mkdir()
    sibling.write_text("x")
    assert run_guard([sibling], data).returncode == 0


def test_guard_passes_when_data_dir_env_var_is_unset(tmp_path: Path) -> None:
    f = tmp_path / "a.py"
    f.write_text("x")
    assert run_guard([f], None).returncode == 0


def test_guard_passes_with_no_files() -> None:
    assert run_guard([], None).returncode == 0


def test_precommit_config_runs_ruff_check_ruff_format_and_guard() -> None:
    text = (ROOT / ".pre-commit-config.yaml").read_text()
    assert "ruff-check" in text or "ruff" in text
    assert "ruff-format" in text
    assert "check_no_data.py" in text


def test_ci_workflow_runs_ruff_and_pytest_on_pull_requests_to_main() -> None:
    workflows = list((ROOT / ".github" / "workflows").glob("*.y*ml"))
    assert workflows, "no workflow found"
    text = "\n".join(w.read_text() for w in workflows)
    assert "pull_request" in text
    assert "main" in text
    assert "uv run ruff check" in text
    assert "uv run ruff format --check" in text
    assert "uv run pytest" in text
