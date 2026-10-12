"""
Static Code Hygiene Scanner (Requirement R2 / Feature F24).
Statically analyzes all production Python (.py) and MQL5 (.mq5, .mqh) files across
the repository to enforce 0 instances of developer-specific absolute paths
(e.g., C:\\Users\\Manuel, AppData\\Roaming\\MetaQuotes, Documents\\BACKTESTS).
"""

from pathlib import Path
import re
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Patterns that indicate unportable, machine-specific hardcoded developer paths
FORBIDDEN_PATTERNS = [
    re.compile(r"c:[\\/]users[\\/]manuel", re.IGNORECASE),
    re.compile(r"c:[\\/]users[\\/][a-z0-9_]+[\\/]desktop", re.IGNORECASE),
    re.compile(r"appdata[\\/]roaming[\\/]metaquotes", re.IGNORECASE),
    re.compile(r"documents[\\/]backtests", re.IGNORECASE),
    re.compile(r"agent-127\.0\.0\.1", re.IGNORECASE),
]

# Directories excluded from static production code scanning
EXCLUDED_DIRS = {
    ".git",
    ".pytest_cache",
    ".agents",
    "__pycache__",
    "build",
    "dist",
    ".venv",
}


def get_all_target_files(extensions: set[str], root_dir: Path) -> list[Path]:
    """Recursively collect files matching given extensions, excluding metadata dirs."""
    target_files = []
    for p in root_dir.rglob("*"):
        if any(excluded in p.parts for excluded in EXCLUDED_DIRS):
            continue
        if p.is_file() and p.suffix.lower() in extensions:
            target_files.append(p)
    return target_files


@pytest.mark.hygiene
def test_no_hardcoded_paths_in_python_codebase():
    """
    Verify 0 instances of machine-specific absolute developer paths exist
    across all active Python modules in python/ and tests/.
    """
    python_files = get_all_target_files({".py"}, PROJECT_ROOT / "python")
    assert len(python_files) >= 10, f"Expected at least 10 Python files, found {len(python_files)}"

    violations = []
    for py_file in python_files:
        content = py_file.read_text(encoding="utf-8", errors="ignore")
        for line_num, line in enumerate(content.splitlines(), start=1):
            for pattern in FORBIDDEN_PATTERNS:
                if pattern.search(line):
                    violations.append(
                        f"{py_file.relative_to(PROJECT_ROOT)}:{line_num}: {line.strip()}"
                    )

    assert not violations, (
        f"Found {len(violations)} hardcoded developer absolute paths in Python code:\n"
        + "\n".join(violations)
    )


@pytest.mark.hygiene
def test_no_hardcoded_paths_in_mql5_codebase():
    """
    Verify 0 instances of machine-specific absolute developer paths exist
    across all active MQL5 Expert Advisors (.mq5) and headers (.mqh) in mql5/ and portfolio/.
    """
    mql5_files = get_all_target_files({".mq5", ".mqh"}, PROJECT_ROOT / "mql5")
    portfolio_files = get_all_target_files({".mq5", ".mqh"}, PROJECT_ROOT / "portfolio")
    all_mql_files = mql5_files + portfolio_files

    assert len(all_mql_files) >= 15, f"Expected at least 15 MQL5 files, found {len(all_mql_files)}"

    violations = []
    for mql_file in all_mql_files:
        content = mql_file.read_text(encoding="utf-8", errors="ignore")
        for line_num, line in enumerate(content.splitlines(), start=1):
            for pattern in FORBIDDEN_PATTERNS:
                if pattern.search(line):
                    violations.append(
                        f"{mql_file.relative_to(PROJECT_ROOT)}:{line_num}: {line.strip()}"
                    )

    assert not violations, (
        f"Found {len(violations)} hardcoded developer absolute paths in MQL5 code:\n"
        + "\n".join(violations)
    )


@pytest.mark.hygiene
def test_all_python_files_use_path_parent_or_relative():
    """
    Verify key orchestrator scripts in python/ resolve project directories dynamically
    using Path(__file__) or relative navigation rather than hardcoded drives.
    """
    key_scripts = [
        PROJECT_ROOT / "python" / "main.py",
        PROJECT_ROOT / "python" / "m2_metalabeling" / "export" / "export_mql5.py",
        PROJECT_ROOT / "python" / "m2_metalabeling" / "ingestion" / "mt5_reader.py",
    ]

    for script in key_scripts:
        assert script.exists(), f"Key script missing: {script}"
        content = script.read_text(encoding="utf-8", errors="ignore")
        assert "Path(__file__)" in content, (
            f"Expected dynamic path resolution using Path(__file__) in {script.name}"
        )
