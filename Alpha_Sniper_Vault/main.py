#!/usr/bin/env python3
"""
+==============================================================================+
|          A L P H A   Q U A N T   F R A M E W O R K                          |
|          Institutional ML Trading System -- CLI Orchestrator                 |
|          Version: Fase 24.8 (Macro-Fundamental Restore)                      |
+==============================================================================+

Usage:
    python main.py

This CLI acts as the single entry point for the entire Alpha Sniper ecosystem.
All core logic lives in /src/, /api/ and /mql5/ -- this file only orchestrates.
"""

import os
import sys
import subprocess
import shutil
import time
from pathlib import Path

# -- Force UTF-8 output so the banner renders in all Windows terminals --------
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
else:
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# -- Path Configuration -------------------------------------------------------
ROOT = Path(__file__).resolve().parent

# Auto-detect layout: new (src/api/) OR legacy (Python_ML/)
# main.py works BEFORE and AFTER running migrate.py
_LEGACY_DIR = ROOT / "Python_ML"
_LEGACY_MQL = ROOT / "MQL5_Engine"

SRC_DIR  = ROOT / "src"    if (ROOT / "src").is_dir()    else _LEGACY_DIR
API_DIR  = ROOT / "api"    if (ROOT / "api").is_dir()    else _LEGACY_DIR
DATA_DIR = ROOT / "data"   if (ROOT / "data").is_dir()   else _LEGACY_DIR / "data"
OUT_DIR  = ROOT / "models" if (ROOT / "models").is_dir() else _LEGACY_DIR / "output"

# Virtual environment: check both root-level and Python_ML-level .venv
_VENV_ROOT   = ROOT / ".venv" / "Scripts" / "python.exe"
_VENV_LEGACY = _LEGACY_DIR / ".venv" / "Scripts" / "python.exe"
if _VENV_ROOT.exists():
    VENV_PYTHON = _VENV_ROOT
elif _VENV_LEGACY.exists():
    VENV_PYTHON = _VENV_LEGACY
else:
    VENV_PYTHON = None
PYTHON_EXE = str(VENV_PYTHON) if VENV_PYTHON else sys.executable

# MT5 export path (Windows standard)
MT5_COMMON = (
    Path(os.environ.get("APPDATA", "")) / "MetaQuotes" / "Terminal" / "Common" / "Files"
)

# -- ANSI Color Codes (Windows 10+ compatible) --------------------------------
if os.name == "nt":
    os.system("color")   # enable ANSI escape codes on Windows cmd/powershell

RESET   = "\033[0m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
CYAN    = "\033[96m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
RED     = "\033[91m"
BLUE    = "\033[94m"

# -- Helpers ------------------------------------------------------------------

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def pause(msg="  Press ENTER to return to menu..."):
    print(f"\n{DIM}{msg}{RESET}")
    input()

def header(title: str, width: int = 78):
    bar = "=" * width
    print(f"\n{CYAN}{BOLD}+{bar}+")
    print(f"|  {title:<{width-2}}|")
    print(f"+{bar}+{RESET}\n")

def section(title: str = "", width: int = 78):
    print(f"{BLUE}{'-'*width}{RESET}")
    if title:
        print(f"  {BOLD}{title}{RESET}")
        print(f"{BLUE}{'-'*width}{RESET}")

def success(msg: str):
    print(f"{GREEN}  [OK]  {msg}{RESET}")

def warn(msg: str):
    print(f"{YELLOW}  [!]   {msg}{RESET}")

def error(msg: str):
    print(f"{RED}  [X]   {msg}{RESET}")

def info(msg: str):
    print(f"{DIM}  >     {msg}{RESET}")

def resolve_script(name: str) -> Path:
    """
    Locate a script by filename. Searches in order:
      1. SRC_DIR (new layout: /src/ or legacy: /Python_ML/)
      2. API_DIR  (new layout: /api/ or legacy: /Python_ML/)
      3. ROOT     (project root -- for top-level scripts)
    Raises FileNotFoundError with a helpful message if not found.
    """
    for candidate in [SRC_DIR / name, API_DIR / name, ROOT / name]:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(
        f"Script '{name}' not found in src/, api/ or root.\n"
        f"  Searched: {SRC_DIR}, {API_DIR}, {ROOT}\n"
        f"  Have you run 'python migrate.py' yet? (Not required -- legacy paths are also checked.)"
    )


def run_script(script_path: Path, *args, cwd: Path = None):
    """Run a Python script in a subprocess, streaming its output live."""
    # Always resolve cwd to the script's parent -- avoids WinError 267
    resolved_cwd = cwd if (cwd and cwd.is_dir()) else script_path.parent
    if not resolved_cwd.is_dir():
        error(f"Working directory does not exist: {resolved_cwd}")
        return
    if not script_path.is_file():
        error(f"Script not found: {script_path}")
        return
    cmd = [PYTHON_EXE, str(script_path)] + [str(a) for a in args]
    try:
        proc = subprocess.run(cmd, cwd=str(resolved_cwd))
        if proc.returncode != 0:
            error(f"Script exited with code {proc.returncode}.")
    except FileNotFoundError:
        error(f"Python interpreter not found: {PYTHON_EXE}")
    except KeyboardInterrupt:
        print(f"\n{YELLOW}  Interrupted by user.{RESET}")


def discover_assets() -> list:
    """Return a sorted list of assets that have a Struct_Dataset_*.csv."""
    search_dirs = [DATA_DIR, _LEGACY_DIR / "data"]
    seen = set()
    for d in search_dirs:
        if d.is_dir():
            for p in d.glob("Struct_Dataset_*.csv"):
                seen.add(p.stem.replace("Struct_Dataset_", ""))
    return sorted(seen)

# =============================================================================
#  BANNER
# =============================================================================

BANNER = f"""{CYAN}{BOLD}
  +--------------------------------------------------------------------------+
  |                                                                          |
  |     /\\ |    |===\\ |  |  /\\ ___     / \\  |  |  /\\ |\\  | ====            |
  |    /--\\|    |---' |--| /--\\  |    | O | |  | /--\\| \\ | |               |
  |   /    \\|___|    \\|  |/    \\ |     \\ /  |__|/    ||  \\| ====            |
  |                                                                          |
  |         Q U A N T   F R A M E W O R K  --  Institutional Edition        |
  |         Macro-Fundamental Restore  |  Dual XGBoost  |  Regime Engine    |
  |         Fase 24.8                                                        |
  |                                                                          |
  +--------------------------------------------------------------------------+
{RESET}"""

# =============================================================================
#  MENU ACTIONS
# =============================================================================

def action_sanitize():
    """[1] Run Data Sanitization."""
    clear()
    header("DATA SANITIZATION  -  Forensic Deduplication & Chronological Sort")
    info(f"Target directory : {DATA_DIR}")
    try:
        script = resolve_script("data_sanitizer.py")
        info(f"Script           : {script.relative_to(ROOT)}")
        print()
        run_script(script)
    except FileNotFoundError as e:
        error(str(e))
    pause()


def action_train():
    """[2] Train Global Optimizer Pipeline (per asset or all)."""
    clear()
    header("ML PIPELINE  -  Train Entry / Exit / Regime Models")

    assets = discover_assets()
    if not assets:
        warn(f"No Struct_Dataset_*.csv found in {DATA_DIR}")
        warn("Run option [I] first to import data from MT5.")
        pause()
        return

    try:
        script = resolve_script("pipeline_global_optimizer.py")
    except FileNotFoundError as e:
        error(str(e))
        pause()
        return

    print(f"  {BOLD}Available assets:{RESET}")
    for i, a in enumerate(assets, 1):
        print(f"  {CYAN}[{i:>2}]{RESET}  {a.upper()}")
    print(f"  {CYAN}[ A]{RESET}  Train ALL assets sequentially")
    print(f"  {CYAN}[ 0]{RESET}  Back")
    section()

    choice = input(f"  {BOLD}Select:{RESET} ").strip().upper()

    if choice == "0":
        return
    elif choice == "A":
        for a in assets:
            clear()
            header(f"TRAINING  >>  {a.upper()}")
            run_script(script, a)
        success("All assets trained.")
    elif choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(assets):
            clear()
            header(f"TRAINING  >>  {assets[idx].upper()}")
            run_script(script, assets[idx])
        else:
            error("Invalid selection.")
    else:
        error("Invalid selection.")

    pause()


def action_simulate():
    """[3] Run Portfolio Equity Simulator."""
    clear()
    header("EQUITY SIMULATOR  -  Portfolio-Level Backtesting (Macro 6)")
    info("Simulates the combined equity curve for all trained assets.")
    try:
        script = resolve_script("portfolio_equity_simulator.py")
        info(f"Script : {script.relative_to(ROOT)}")
        print()
        run_script(script)
    except FileNotFoundError as e:
        error(str(e))
    pause()


def action_montecarlo():
    """[4] Run Walk-Forward + Monte Carlo Analysis."""
    clear()
    header("WALK-FORWARD & MONTE CARLO  -  Statistical Robustness Audit")

    assets = discover_assets()
    if not assets:
        warn(f"No assets found in {DATA_DIR}")
        pause()
        return

    try:
        script = resolve_script("backtest_walk_forward_montecarlo.py")
    except FileNotFoundError as e:
        error(str(e))
        pause()
        return

    print(f"  {BOLD}Select asset:{RESET}")
    for i, a in enumerate(assets, 1):
        print(f"  {CYAN}[{i}]{RESET}  {a.upper()}")
    section()
    choice = input(f"  {BOLD}Select:{RESET} ").strip()

    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(assets):
            clear()
            header(f"MONTE CARLO  >>  {assets[idx].upper()}")
            run_script(script, assets[idx])
        else:
            error("Invalid selection.")
    else:
        error("Invalid selection.")

    pause()


def action_server():
    """[5] Launch Production Inference Server (Flask)."""
    clear()
    header("PRODUCTION SERVER  -  Flask Inference API  @  http://0.0.0.0:8000")
    info("Press CTRL+C to stop the server.")
    print()
    section("Endpoints")
    print(f"  {GREEN}POST /predict_entry{RESET}  --  Entry Model inference + Regime filter")
    print(f"  {GREEN}POST /predict_exit {RESET}  --  Exit Model inference")
    print(f"  {GREEN}POST /reload       {RESET}  --  Hot-reload all .pkl models")
    section()
    print()

    try:
        script = resolve_script("produccion_flask_server.py")
    except FileNotFoundError as e:
        error(str(e))
        pause()
        return

    try:
        subprocess.run([PYTHON_EXE, str(script)], cwd=str(script.parent))
    except KeyboardInterrupt:
        print(f"\n{YELLOW}  Server stopped.{RESET}")
    except Exception as e:
        error(str(e))

    pause()


def action_import_mt5():
    """[I] Import CSVs from MetaTrader 5 Common/Files folder."""
    clear()
    header("DATA IMPORT  -  MetaTrader 5  >>  /data/")

    if not MT5_COMMON.exists():
        error(f"MT5 Common/Files not found at:\n  {MT5_COMMON}")
        warn("Make sure MT5 is installed and the HMA_ML_Orchestrator EA has run.")
        pause()
        return

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    copied = 0
    patterns = ["Struct_Dataset_*.csv", "Struct_Exit_Dataset_*.csv"]

    for pat in patterns:
        for src_file in MT5_COMMON.glob(pat):
            dst = DATA_DIR / src_file.name
            shutil.copy2(src_file, dst)
            success(f"Copied: {src_file.name}")
            copied += 1

    if copied == 0:
        warn("No matching CSV files found in MT5 Common/Files.")
        warn("Ensure the HMA_ML_Orchestrator is running and has logged data.")
    else:
        print()
        success(f"Total: {copied} files imported to {DATA_DIR}")

    pause()


def action_status():
    """[S] System Status -- show which assets have trained models."""
    clear()
    header("SYSTEM STATUS  -  Asset & Model Inventory")

    # Layout info
    layout = "NEW (src/ api/ models/)" if (ROOT / "src").is_dir() else "LEGACY (Python_ML/)"
    info(f"Layout detected : {layout}")
    info(f"Scripts dir     : {SRC_DIR}")
    info(f"Data dir        : {DATA_DIR}")
    info(f"Models dir      : {OUT_DIR}")
    print()

    assets = discover_assets()
    if not assets:
        warn("No datasets found.")
        pause()
        return

    # Search models in both new and legacy output directories
    model_dirs = [OUT_DIR]
    _leg_out = _LEGACY_DIR / "output"
    if _leg_out.is_dir() and _leg_out != OUT_DIR:
        model_dirs.append(_leg_out)

    def has_model(name: str) -> bool:
        return any((d / name).exists() for d in model_dirs)

    def has_data_file(name: str) -> bool:
        search = [DATA_DIR, _LEGACY_DIR / "data"]
        return any((d / name).exists() for d in search)

    W = {"asset": 10, "data": 8, "entry": 8, "exit": 8, "regime": 8, "thresh": 12}
    print(f"  {BOLD}{'ASSET':<{W['asset']}} {'DATASET':<{W['data']}} "
          f"{'ENTRY':<{W['entry']}} {'EXIT':<{W['exit']}} "
          f"{'REGIME':<{W['regime']}} {'THRESHOLDS':<{W['thresh']}}{RESET}")
    section()

    for a in assets:
        AU = a.upper()
        has_d = has_data_file(f"Struct_Dataset_{AU}.csv")
        has_e = has_model(f"entry_model_{AU}.pkl")
        has_x = has_model(f"exit_model_{AU}.pkl")
        has_r = has_model(f"regime_model_{AU}.pkl")
        has_t = has_model(f"production_thresholds_{AU}.json")

        def tick(b): return f"{GREEN}OK{RESET}  " if b else f"{RED}--{RESET}  "

        print(f"  {CYAN}{AU:<{W['asset']}}{RESET}"
              f"  {tick(has_d):<{W['data']+6}}"
              f"  {tick(has_e):<{W['entry']+6}}"
              f"  {tick(has_x):<{W['exit']+6}}"
              f"  {tick(has_r):<{W['regime']+6}}"
              f"  {tick(has_t):<{W['thresh']+6}}")

    pause()


# =============================================================================
#  MAIN MENU
# =============================================================================

MENU_SEP = "SEP"

MENU_ITEMS = [
    ("1", "Run Data Sanitization",                action_sanitize),
    ("2", "Train Global Optimizer Pipeline",       action_train),
    ("3", "Run Portfolio Equity Simulator",        action_simulate),
    ("4", "Run Walk-Forward & Monte Carlo Audit",  action_montecarlo),
    ("5", "Launch Production Inference Server",    action_server),
    (MENU_SEP, None, None),
    ("I", "Import CSVs from MetaTrader 5",         action_import_mt5),
    ("S", "System Status & Model Inventory",       action_status),
    (MENU_SEP, None, None),
    ("0", "Exit",                                  None),
]


def main_menu():
    while True:
        clear()
        print(BANNER)

        assets = discover_assets()
        if assets:
            print(f"  {DIM}Loaded assets: {', '.join(a.upper() for a in assets)}{RESET}\n")
        else:
            print(f"  {YELLOW}  [!] No datasets found. Use [I] to import data from MT5.{RESET}\n")

        section("MAIN MENU")
        for key, label, _ in MENU_ITEMS:
            if key == MENU_SEP:
                print(f"  {DIM}{'.' * 60}{RESET}")
            elif key == "0":
                print(f"  {RED}[{key}]{RESET}  {label}")
            else:
                print(f"  {CYAN}[{key}]{RESET}  {label}")
        section()

        choice = input(f"\n  {BOLD}Select option:{RESET} ").strip().upper()

        # Dispatch
        for key, label, fn in MENU_ITEMS:
            if key == MENU_SEP:
                continue
            if choice == key.upper():
                if fn is None:
                    clear()
                    print(f"\n{CYAN}  Shutting down Alpha Quant Framework. Goodbye.{RESET}\n")
                    sys.exit(0)
                fn()
                break
        else:
            error("Invalid option -- please try again.")
            time.sleep(0.8)


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n{CYAN}  Interrupted. Goodbye.{RESET}\n")
        sys.exit(0)
