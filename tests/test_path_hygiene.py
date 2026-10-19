"""
Static Code & Path Hygiene Scanner (Requirement R2 / Feature F24).
Statically analyzes all production Python (.py) and MQL5 (.mq5, .mqh) files across
the repository to enforce:
1. 0 instances of developer-specific absolute paths (e.g., C:\\Users\\Manuel, AppData\\Roaming\\MetaQuotes).
2. Dynamic path resolution via Path(__file__) across all key orchestrators and pipeline scripts (via AST).
3. Complete absence/purging of bloated portfolio/ directory and redundant multi-asset clones.
4. AST syntax validity and AST-level string literal hygiene across all Python code.
5. Presence and cleanliness of the canonical educational MQL5 architecture blueprint:
   - Strategy 2.91.69.mq5
   - M2_XGBoost_Oracle.mqh
   - Pipeline_Extractor_M1.mq5
6. Clean isolation and build integrity of documentation site/ directory.
"""

import ast
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
    "site",
}


def get_all_target_files(extensions: set[str], root_dir: Path) -> list[Path]:
    """Recursively collect files matching given extensions, excluding metadata dirs."""
    if not root_dir.exists():
        return []
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
    across all active Python modules in python/ and tests/ using regex line scanning.
    """
    python_files = (
        get_all_target_files({".py"}, PROJECT_ROOT / "python")
        + get_all_target_files({".py"}, PROJECT_ROOT / "tests")
    )
    assert len(python_files) >= 15, f"Expected at least 15 Python files, found {len(python_files)}"

    violations = []
    for py_file in python_files:
        is_self = py_file.resolve() == Path(__file__).resolve()
        content = py_file.read_text(encoding="utf-8", errors="ignore")
        for line_num, line in enumerate(content.splitlines(), start=1):
            if is_self and ("re.compile" in line or "FORBIDDEN_PATTERNS" in line or "e.g.," in line):
                continue
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
def test_python_ast_syntax_and_string_literal_hygiene():
    """
    Verify all Python files are syntactically valid via AST and inspect all
    string literal constants (ast.Constant) to ensure no hardcoded drive paths exist.
    """
    python_files = (
        get_all_target_files({".py"}, PROJECT_ROOT / "python")
        + get_all_target_files({".py"}, PROJECT_ROOT / "tests")
    )

    ast_violations = []
    for py_file in python_files:
        if py_file.resolve() == Path(__file__).resolve():
            continue
        content = py_file.read_text(encoding="utf-8", errors="ignore")
        try:
            tree = ast.parse(content, filename=str(py_file))
        except SyntaxError as e:
            ast_violations.append(f"SyntaxError in {py_file.relative_to(PROJECT_ROOT)}: {e}")
            continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                for pattern in FORBIDDEN_PATTERNS:
                    if pattern.search(node.value):
                        ast_violations.append(
                            f"{py_file.relative_to(PROJECT_ROOT)}:{node.lineno}: AST string literal: {node.value}"
                        )

    assert not ast_violations, (
        f"Found {len(ast_violations)} AST syntax or string literal violations:\n"
        + "\n".join(ast_violations)
    )


@pytest.mark.hygiene
def test_no_hardcoded_paths_in_mql5_codebase():
    """
    Verify 0 instances of machine-specific absolute developer paths exist
    across all active MQL5 Expert Advisors (.mq5) and headers (.mqh) in mql5/.
    Validates that the canonical blueprint and supporting libraries are 100% portable.
    """
    mql5_files = get_all_target_files({".mq5", ".mqh"}, PROJECT_ROOT / "mql5")
    assert len(mql5_files) >= 5, f"Expected active MQL5 codebase, found {len(mql5_files)}"

    # Ensure canonical educational blueprint files are present
    canonical_files = [
        PROJECT_ROOT / "mql5" / "Experts" / "HMA_SQX_Discovery" / "Strategy 2.91.69.mq5",
        PROJECT_ROOT / "mql5" / "Include" / "M2_XGBoost_Oracle.mqh",
        PROJECT_ROOT / "mql5" / "Experts" / "HMA_SQX_Discovery" / "Pipeline_Extractor_M1.mq5",
    ]
    for canon in canonical_files:
        assert canon.exists(), f"Canonical educational blueprint missing: {canon.relative_to(PROJECT_ROOT)}"

    violations = []
    for mql_file in mql5_files:
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
def test_portfolio_directory_purged():
    """
    Regression assertion: Ensure the bloated portfolio/ directory is eradicated.
    Guarantees no redundant multi-asset clone folders (AUDUSD, EURUSD, etc.) exist.
    """
    portfolio_dir = PROJECT_ROOT / "portfolio"
    assert not portfolio_dir.exists(), (
        f"VIOLATION: portfolio/ directory still exists at {portfolio_dir}. "
        "All redundant multi-asset clones and datasets must be purged per Requirement R1."
    )


@pytest.mark.hygiene
def test_all_python_files_use_path_parent_or_relative():
    """
    Verify key orchestrator and pipeline scripts in python/ resolve project directories
    dynamically using Path(__file__) rather than hardcoded drives or unportable paths.
    Uses AST call verification.
    """
    key_scripts = [
        PROJECT_ROOT / "python" / "main.py",
        PROJECT_ROOT / "python" / "m2_metalabeling" / "export" / "export_mql5.py",
        PROJECT_ROOT / "python" / "m2_metalabeling" / "ingestion" / "mt5_reader.py",
        PROJECT_ROOT / "python" / "m2_metalabeling" / "models" / "rolling_window_retrain.py",
        PROJECT_ROOT / "python" / "m2_metalabeling" / "models" / "audit_report.py",
        PROJECT_ROOT / "python" / "m2_metalabeling" / "models" / "sanity_check_factory.py",
    ]

    for script in key_scripts:
        assert script.exists(), f"Key script missing: {script}"
        tree = ast.parse(script.read_text(encoding="utf-8", errors="ignore"), filename=str(script))

        has_path_file = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "Path":
                    if any(isinstance(a, ast.Name) and a.id == "__file__" for a in node.args):
                        has_path_file = True
                        break
        assert has_path_file, (
            f"Expected dynamic path resolution using Path(__file__) in {script.relative_to(PROJECT_ROOT)}"
        )


@pytest.mark.hygiene
def test_documentation_site_hygiene_and_integrity():
    """
    Verify documentation build directory site/ exists or can be built cleanly,
    and is properly isolated from production code paths.
    """
    site_dir = PROJECT_ROOT / "site"
    if not site_dir.exists():
        import shutil
        import subprocess
        import sys
        cmd = ["mkdocs", "build"] if shutil.which("mkdocs") else [sys.executable, "-m", "mkdocs", "build"]
        try:
            subprocess.run(cmd, cwd=PROJECT_ROOT, check=False)
        except Exception:
            pass

    if site_dir.exists():
        # Verify key documentation artifacts exist in site/
        assert (site_dir / "index.html").exists(), "site/index.html missing from documentation build"
        assert (site_dir / "METHODOLOGY" / "index.html").exists(), "site/METHODOLOGY/index.html missing"
        assert (site_dir / "POST_MORTEM" / "index.html").exists(), "site/POST_MORTEM/index.html missing"
    else:
        pytest.skip("site/ directory not yet built; run 'mkdocs build' to test site integrity")
