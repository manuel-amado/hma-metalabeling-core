"""
Subprocess and Unit tests for CLI Orchestrator (python/main.py).
Validates Requirement R1 / Feature F23: argparse interface, non-interactive execution,
--help verification, graceful handling of invalid inputs without blocking or hanging.
"""

import os
import subprocess
import sys
from pathlib import Path
import pytest

from main import print_header, print_menu, run_script, execute_step


PROJECT_ROOT = Path(__file__).resolve().parent.parent
MAIN_PY = PROJECT_ROOT / "python" / "main.py"
PORTFOLIO_FACTORY_PY = PROJECT_ROOT / "python" / "m2_metalabeling" / "models" / "portfolio_factory.py"


def test_cli_header_and_menu_display(capsys):
    """Verify print_header and print_menu render formatted text without errors."""
    print_header()
    out = capsys.readouterr().out
    assert "M2 QUANT PIPELINE" in out
    assert "Lopez de Prado" in out

    print_menu()
    out2 = capsys.readouterr().out
    assert "FLUJO DE EJECUCION" in out2
    assert "0. Salir" in out2


def test_cli_run_script_missing_file(tmp_path: Path):
    """Verify run_script gracefully returns False when target file does not exist."""
    ghost_script = tmp_path / "ghost_script.py"
    success = run_script(ghost_script)
    assert success is False


@pytest.mark.cli
def test_cli_subprocess_help_flag():
    """Verify python main.py --help returns exit code 0 with usage documentation."""
    res = subprocess.run(
        [sys.executable, str(MAIN_PY), "--help"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert res.returncode == 0
    assert "M2 Meta-Labeling Institutional CLI" in res.stdout
    assert "--step" in res.stdout
    assert "--non-interactive" in res.stdout


@pytest.mark.cli
def test_cli_subprocess_invalid_flag():
    """Verify python main.py rejects invalid flags with non-zero exit code without hanging."""
    res = subprocess.run(
        [sys.executable, str(MAIN_PY), "--unrecognized-bogus-flag"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert res.returncode != 0
    assert "unrecognized arguments" in res.stderr.lower() or "error" in res.stderr.lower()


@pytest.mark.cli
def test_cli_subprocess_eof_stdin_graceful_exit():
    """Verify interactive mode handles closed stdin (EOF) gracefully without hanging."""
    res = subprocess.run(
        [sys.executable, str(MAIN_PY)],
        input="",  # Immediate EOF
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert res.returncode == 0
    assert "M2 QUANT PIPELINE" in res.stdout


@pytest.mark.cli
def test_cli_subprocess_step_execution():
    """Verify python main.py --step 1 --non-interactive runs headlessly without input prompts."""
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT / "python")

    res = subprocess.run(
        [sys.executable, str(MAIN_PY), "--step", "1", "--non-interactive"],
        env=env,
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert "[MODO NO-INTERACTIVO] Ejecutando paso: 1" in res.stdout
    # Must exit cleanly (code 0 or non-zero depending on step scripts, but without hanging)
    assert res.returncode in (0, 1)


@pytest.mark.cli
def test_portfolio_factory_cli_help():
    """Verify portfolio_factory.py --help exposes --audit-only flag with exit code 0."""
    res = subprocess.run(
        [sys.executable, str(PORTFOLIO_FACTORY_PY), "--help"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert res.returncode == 0
    assert "--audit-only" in res.stdout
    assert "Cross-Asset Research & Out-of-Sample Degradation Auditor" in res.stdout


@pytest.mark.cli
def test_portfolio_factory_cli_audit_only():
    """Verify portfolio_factory.py --audit-only runs headless audit with exit code 0."""
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT / "python")

    res = subprocess.run(
        [sys.executable, str(PORTFOLIO_FACTORY_PY), "--audit-only", "--symbols", "XAUUSD"],
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert res.returncode == 0
    assert "CROSS-ASSET OOS DEGRADATION AUDIT REPORT" in res.stdout
    assert "XAUUSD" in res.stdout

