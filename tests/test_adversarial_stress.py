"""
Adversarial Stress Test Suite for HMA Meta-Labeling Core
=========================================================
Empirical verification conducted by Challenger 1 (Specialist & Critic).

Scope:
1. PurgedKFold boundary stress testing (N=10..2000, K=2..10, embargo=0..0.20, nested/overlapping events, zero-leakage invariant, fold 0 non-empty).
2. Triple Barrier Labeling edge cases (zero ATR, runaway trends, flatline markets, simultaneous expiry, timeout market return fidelity).
3. CLI python/main.py automated headless execution and exit code assertions.
"""

import os
import subprocess
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from m2_metalabeling.cross_validation.purged_cv import PurgedKFold
from m2_metalabeling.labeling.triple_barrier import get_triple_barrier_labels, triple_barrier_labels

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MAIN_PY = PROJECT_ROOT / "python" / "main.py"


# =====================================================================
# 1. PURGED K-FOLD ADVERSARIAL STRESS TESTS
# =====================================================================

class TestPurgedKFoldAdversarial:
    """Adversarial stress harness for PurgedKFold cross-validation."""

    @pytest.mark.parametrize("N", [10, 50, 500, 2000])
    @pytest.mark.parametrize("K", [2, 5, 10])
    @pytest.mark.parametrize("embargo_pct", [0.0, 0.05, 0.20])
    def test_purged_kfold_parameter_sweep_invariants(self, N: int, K: int, embargo_pct: float):
        """
        Stress test PurgedKFold across a 36-combination parameter sweep.
        Invariants checked on every single fold:
        1. Fold 0 train set is strictly non-empty.
        2. Train and test sets are strictly disjoint.
        3. No pre-test training observation label horizon (t1) extends into the test window (t0_min).
        4. No post-test training observation starts (t0) within open test-set holding horizons (max(test_t1)).
        5. No training observation falls within the embargo window immediately following the test set.
        """
        dates = pd.date_range("2024-01-01 00:00:00", periods=N, freq="h", tz="UTC")
        X = pd.DataFrame({"feature": np.linspace(0, 100, N)}, index=dates)

        # Realistic holding horizon: 3% of series or at least 2 bars
        holding_bars = max(2, int(N * 0.03))
        t1_indices = [min(i + holding_bars, N - 1) for i in range(N)]
        t1 = pd.Series([dates[idx] for idx in t1_indices], index=dates)

        pkf = PurgedKFold(n_splits=K, embargo_pct=embargo_pct)
        splits = list(pkf.split(X, t1=t1))

        assert len(splits) == K, f"Expected {K} folds, got {len(splits)}"

        fold_0_train, fold_0_test = splits[0]
        assert len(fold_0_train) > 0, (
            f"VIOLATION: Fold 0 train set is empty for N={N}, K={K}, embargo={embargo_pct}"
        )

        embargo_size = int(N * embargo_pct)

        for fold_idx, (train_idx, test_idx) in enumerate(splits):
            train_set = set(train_idx)
            test_set = set(test_idx)

            # Invariant 2: Strictly disjoint
            overlap = train_set.intersection(test_set)
            assert len(overlap) == 0, f"Fold {fold_idx}: Train and test sets overlap: {overlap}"

            test_start = test_idx[0]
            test_end = test_idx[-1] + 1
            test_t0_min = dates[test_start]
            test_t1_max = t1.iloc[test_idx].dropna().max()

            # Invariant 3: Pre-test samples do not bleed into test
            for tr in train_idx:
                if tr < test_start:
                    tr_t1 = t1.iloc[tr]
                    assert tr_t1 < test_t0_min, (
                        f"Fold {fold_idx}: Pre-test leakage! Train sample {tr} (t1={tr_t1}) "
                        f"bleeds into test window starting at {test_t0_min}"
                    )

            # Invariant 4: Post-test samples do not start within open test holding horizons
            for tr in train_idx:
                if tr >= test_end:
                    tr_t0 = dates[tr]
                    assert tr_t0 > test_t1_max, (
                        f"Fold {fold_idx}: Post-test leakage! Train sample {tr} (t0={tr_t0}) "
                        f"falls within open test holding horizon ending at {test_t1_max}"
                    )

            # Invariant 5: Embargo window exclusion
            embargo_window = set(range(test_end, min(test_end + embargo_size, N)))
            embargo_leakage = train_set.intersection(embargo_window)
            assert len(embargo_leakage) == 0, (
                f"Fold {fold_idx}: Embargo violation! Train samples {embargo_leakage} in embargo window"
            )

    def test_purged_kfold_nested_and_overlapping_events(self):
        """
        Adversarial test with irregular, highly overlapping, and nested events:
        - Long 'parent' event spanning across multiple subsequent short 'child' events.
        - Events ending simultaneously.
        - Irregular burst intervals.
        """
        N = 100
        dates = pd.date_range("2024-01-01", periods=N, freq="D", tz="UTC")
        X = pd.DataFrame({"val": np.arange(N)}, index=dates)

        # Create nested structure:
        # Event 10 spans until bar 40 (long parent)
        # Events 11..25 are short (span 1-2 bars)
        # Event 45 spans until bar 80
        t1_list = []
        for i in range(N):
            if i == 10:
                t1_list.append(dates[min(40, N - 1)])
            elif 11 <= i <= 25:
                t1_list.append(dates[min(i + 2, N - 1)])
            elif i == 45:
                t1_list.append(dates[min(80, N - 1)])
            else:
                t1_list.append(dates[min(i + 4, N - 1)])
        t1 = pd.Series(t1_list, index=dates)

        pkf = PurgedKFold(n_splits=5, embargo_pct=0.05)
        splits = list(pkf.split(X, t1=t1))

        assert len(splits) == 5
        for fold_idx, (train_idx, test_idx) in enumerate(splits):
            test_start = test_idx[0]
            test_end = test_idx[-1] + 1
            test_t0_min = dates[test_start]
            test_t1_max = t1.iloc[test_idx].dropna().max()

            # Verify no train observation interval intersects test interval
            for tr in train_idx:
                tr_t0 = dates[tr]
                tr_t1 = t1.iloc[tr]
                if tr < test_start:
                    assert tr_t1 < test_t0_min
                elif tr >= test_end:
                    assert tr_t0 > test_t1_max

    def test_purged_kfold_extreme_boundary_n_equals_k(self):
        """
        Boundary condition: N=10, K=10 (Leave-One-Out style).
        Each fold has 1 test sample.
        """
        N = 10
        dates = pd.date_range("2024-01-01", periods=N, freq="h", tz="UTC")
        X = pd.DataFrame({"val": np.arange(N)}, index=dates)
        t1 = pd.Series([dates[min(i + 1, N - 1)] for i in range(N)], index=dates)

        pkf = PurgedKFold(n_splits=10, embargo_pct=0.0)
        splits = list(pkf.split(X, t1=t1))

        assert len(splits) == 10
        for fold_idx, (train_idx, test_idx) in enumerate(splits):
            assert len(test_idx) == 1
            assert len(set(train_idx).intersection(set(test_idx))) == 0

    def test_purged_kfold_missing_and_nan_t1_graceful_handling(self):
        """
        Stress test: Some observations have NaN in t1 (e.g. censored or unclosed positions).
        PurgedKFold must not raise unhandled exceptions and maintain partition integrity.
        """
        N = 50
        dates = pd.date_range("2024-01-01", periods=N, freq="h", tz="UTC")
        X = pd.DataFrame({"feat": np.arange(N)}, index=dates)
        t1 = pd.Series([dates[min(i + 2, N - 1)] for i in range(N)], index=dates)
        # Inject NaNs at irregular indices
        t1.iloc[5] = pd.NaT
        t1.iloc[15] = pd.NaT
        t1.iloc[30] = pd.NaT

        pkf = PurgedKFold(n_splits=5, embargo_pct=0.02)
        splits = list(pkf.split(X, t1=t1))
        assert len(splits) == 5
        for train_idx, test_idx in splits:
            assert len(train_idx) > 0
            assert len(test_idx) > 0
            assert set(train_idx).isdisjoint(set(test_idx))


# =====================================================================
# 2. TRIPLE BARRIER LABELING ADVERSARIAL STRESS TESTS
# =====================================================================

class TestTripleBarrierAdversarial:
    """Adversarial stress harness for Triple Barrier Labeling."""

    def test_triple_barrier_zero_volatility(self):
        """
        Stress test: ATR = 0.0 (Zero Volatility).
        When ATR is 0, pt_level == entry_price and sl_level == entry_price.
        At the first future bar, price >= pt_level evaluates to True if price is unchanged or higher.
        Module must compute cleanly without ZeroDivisionError or floating point crash.
        """
        dates = pd.date_range("2024-01-01 00:00:00", periods=50, freq="h", tz="UTC")
        close = pd.Series(100.0, index=dates)
        atr_zero = pd.Series(0.0, index=dates)
        events = pd.DatetimeIndex([dates[5], dates[10], dates[20]])

        labels = get_triple_barrier_labels(
            close, atr_zero, events, pt_atr=2.0, sl_atr=1.0, max_holding_bars=10
        )

        assert len(labels) == 3
        # Since price unchanged at 100.0 and pt_level = 100.0, price >= pt_level triggers on the first future bar
        for t0, row in labels.iterrows():
            assert row["exit_price"] == 100.0
            assert row["ret"] == 0.0
            assert row["label"] in (-1, 0, 1)

    def test_triple_barrier_flatline_market_timeout_behavior(self):
        """
        Stress test: Completely flat market (price never moves, ATR > 0).
        Neither PT nor SL can ever be triggered.
        All events MUST result in vertical timeout (label = 0).
        exit_price must be exactly entry_price, ret == 0.0, and bin == 0.
        """
        dates = pd.date_range("2024-01-01 00:00:00", periods=50, freq="h", tz="UTC")
        close = pd.Series(100.0, index=dates)
        atr = pd.Series(2.5, index=dates)
        events = pd.DatetimeIndex([dates[5], dates[15]])

        labels = get_triple_barrier_labels(
            close, atr, events, pt_atr=2.0, sl_atr=1.0, max_holding_bars=10
        )

        assert len(labels) == 2
        for t0, row in labels.iterrows():
            assert row["label"] == 0, "Flatline market must result in vertical timeout (label 0)"
            assert row["bin"] == 0, "Zero return must result in bin = 0"
            assert row["exit_price"] == 100.0
            assert row["ret"] == 0.0
            # Expiration should occur exactly at t0 + max_holding_bars
            assert row["t1"] == dates[dates.get_loc(t0) + 10]

    def test_triple_barrier_timeout_genuine_market_log_returns(self):
        """
        F03 CRITICAL REGRESSION & STRESS:
        Timeout returns must reflect genuine market price movements, NOT reset to entry_price.
        Verify with both positive and negative moves inside the barrier corridor.
        """
        dates = pd.date_range("2024-01-01 00:00:00", periods=50, freq="h", tz="UTC")
        close = pd.Series(100.0, index=dates)
        atr = pd.Series(5.0, index=dates)  # PT = 110.0, SL = 95.0

        # Scenario A: Profitable move within corridor (+3.5, below PT 110.0)
        # Entry at dates[5], holding=10 bars -> expires at dates[15]
        close_a = close.copy()
        for idx in range(6, 16):
            close_a.iloc[idx] = 100.0 + (idx - 5) * 0.35  # reaches 103.5 at idx=15

        events_a = pd.DatetimeIndex([dates[5]])
        labels_a = get_triple_barrier_labels(close_a, atr, events_a, pt_atr=2.0, sl_atr=1.0, max_holding_bars=10)
        assert len(labels_a) == 1
        res_a = labels_a.iloc[0]
        assert res_a["label"] == 0
        assert res_a["exit_price"] == pytest.approx(103.5, rel=1e-5)
        assert res_a["exit_price"] != 100.0
        assert res_a["ret"] == pytest.approx(np.log(103.5 / 100.0), rel=1e-5)
        assert res_a["ret"] > 0
        assert res_a["bin"] == 1

        # Scenario B: Unprofitable move within corridor (-2.0, above SL 95.0)
        # Entry at dates[20], holding=10 bars -> expires at dates[30]
        close_b = close.copy()
        for idx in range(21, 31):
            close_b.iloc[idx] = 100.0 - (idx - 20) * 0.20  # reaches 98.0 at idx=30

        events_b = pd.DatetimeIndex([dates[20]])
        labels_b = get_triple_barrier_labels(close_b, atr, events_b, pt_atr=2.0, sl_atr=1.0, max_holding_bars=10)
        assert len(labels_b) == 1
        res_b = labels_b.iloc[0]
        assert res_b["label"] == 0
        assert res_b["exit_price"] == pytest.approx(98.0, rel=1e-5)
        assert res_b["exit_price"] != 100.0
        assert res_b["ret"] == pytest.approx(np.log(98.0 / 100.0), rel=1e-5)
        assert res_b["ret"] < 0
        assert res_b["bin"] == 0

    def test_triple_barrier_extreme_runaway_trends(self):
        """
        Stress test: Exponential parabolic explosion and crash.
        Barriers must trigger instantly at the first bar that violates thresholds.
        """
        dates = pd.date_range("2024-01-01 00:00:00", periods=30, freq="h", tz="UTC")
        # Exponential runaway: 100, 200, 400, ...
        close_up = pd.Series([100.0 * (2.0 ** i) for i in range(30)], index=dates)
        atr = pd.Series(5.0, index=dates)
        events = pd.DatetimeIndex([dates[0]])

        labels_up = get_triple_barrier_labels(close_up, atr, events, pt_atr=2.0, sl_atr=1.0, max_holding_bars=10)
        assert len(labels_up) == 1
        assert labels_up.iloc[0]["label"] == 1
        assert labels_up.iloc[0]["t1"] == dates[1]
        assert labels_up.iloc[0]["exit_price"] == 200.0
        assert labels_up.iloc[0]["ret"] == pytest.approx(np.log(2.0), rel=1e-5)
        assert labels_up.iloc[0]["bin"] == 1

        # Exponential crash: 100, 50, 25, ...
        close_down = pd.Series([100.0 * (0.5 ** i) for i in range(30)], index=dates)
        labels_down = get_triple_barrier_labels(close_down, atr, events, pt_atr=2.0, sl_atr=1.0, max_holding_bars=10)
        assert len(labels_down) == 1
        assert labels_down.iloc[0]["label"] == -1
        assert labels_down.iloc[0]["t1"] == dates[1]
        assert labels_down.iloc[0]["exit_price"] == 50.0
        assert labels_down.iloc[0]["ret"] == pytest.approx(np.log(0.5), rel=1e-5)
        assert labels_down.iloc[0]["bin"] == 0

    def test_triple_barrier_simultaneous_expiration_at_tail(self):
        """
        Stress test: Event triggered at the very last bar of the series, where future data has length 0.
        Must handle gracefully: t1=t0, exit_price=entry_price, ret=0.0.
        """
        dates = pd.date_range("2024-01-01 00:00:00", periods=20, freq="h", tz="UTC")
        close = pd.Series(100.0, index=dates)
        atr = pd.Series(2.0, index=dates)
        # Event at the very final available timestamp
        last_date = dates[-1]
        events = pd.DatetimeIndex([last_date])

        labels = get_triple_barrier_labels(close, atr, events, pt_atr=2.0, sl_atr=1.0, max_holding_bars=10)
        assert len(labels) == 1
        assert labels.iloc[0]["t1"] == last_date
        assert labels.iloc[0]["exit_price"] == 100.0
        assert labels.iloc[0]["ret"] == 0.0
        assert labels.iloc[0]["label"] == 0
        assert labels.iloc[0]["bin"] == 0


# =====================================================================
# 3. CLI MAIN.PY ADVERSARIAL STRESS TESTS
# =====================================================================

class TestCLIAdversarial:
    """Adversarial stress harness for CLI Orchestrator python/main.py."""

    @pytest.mark.cli
    @pytest.mark.parametrize("flag", ["--help", "-h"])
    def test_cli_help_flags(self, flag: str):
        """Assert CLI displays help and exits with status 0 within 10 seconds."""
        res = subprocess.run(
            [sys.executable, str(MAIN_PY), flag],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
        )
        assert res.returncode == 0
        assert "M2 Meta-Labeling" in (res.stdout or "")
        assert "--step" in (res.stdout or "")

    @pytest.mark.cli
    @pytest.mark.parametrize("bad_arg", ["--unrecognized-arg", "--step=99", "--invalid_param"])
    def test_cli_invalid_arguments_exit_code(self, bad_arg: str):
        """Assert CLI rejects illegal flags without hanging and exits with non-zero code."""
        res = subprocess.run(
            [sys.executable, str(MAIN_PY), bad_arg],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
        )
        assert res.returncode != 0
        assert res.returncode in (1, 2)

    @pytest.mark.cli
    def test_cli_non_interactive_step_1_no_hang(self):
        """
        Assert python main.py --step 1 --non-interactive runs fully automated
        without prompting for stdin, completing within reasonable timeout.
        """
        env = os.environ.copy()
        env["PYTHONPATH"] = str(PROJECT_ROOT / "python")

        res = subprocess.run(
            [sys.executable, str(MAIN_PY), "--step", "1", "--non-interactive"],
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=25,
        )
        # Must execute non-interactively without stdin block
        assert "[MODO NO-INTERACTIVO] Ejecutando paso: 1" in (res.stdout or "")
        assert res.returncode in (0, 1)

    @pytest.mark.cli
    def test_cli_non_interactive_step_all_no_hang(self):
        """
        Assert python main.py --non-interactive (defaulting to step all)
        launches headlessly without blocking on console prompt.
        """
        env = os.environ.copy()
        env["PYTHONPATH"] = str(PROJECT_ROOT / "python")

        res = subprocess.run(
            [sys.executable, str(MAIN_PY), "--non-interactive"],
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=40,
        )
        assert "[MODO NO-INTERACTIVO] Ejecutando paso: all" in (res.stdout or "")
