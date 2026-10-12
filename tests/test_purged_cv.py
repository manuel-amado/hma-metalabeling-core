"""
Unit tests for Purged Cross-Validation module (m2_metalabeling.cross_validation.purged_cv).
Validates Requirement R1 / Feature F19: sample overlap prevention, purge and embargo logic,
regression verification for Fold 0 non-empty training set, and rolling CV protections.
"""

import numpy as np
import pandas as pd
import pytest

from m2_metalabeling.cross_validation.purged_cv import PurgedKFold
from m2_metalabeling.models.sanity_check_factory import TimeBasedRollingPurgedCV


@pytest.fixture
def synthetic_cv_series():
    """
    Generate 100 observations spanning 100 days with 2-day label holding periods.
    """
    n_samples = 100
    dates = pd.date_range("2024-01-01", periods=n_samples, freq="D", tz="UTC")
    X = pd.DataFrame({"feature1": np.linspace(0, 10, n_samples)}, index=dates)
    # Each trade has a label that lasts 2 days into the future (t1 = t0 + 2 days)
    t1 = pd.Series(dates + pd.Timedelta(days=2), index=dates)
    return X, t1


def test_purged_kfold_split_count(synthetic_cv_series):
    """Verify PurgedKFold generates exactly n_splits folds."""
    X, t1 = synthetic_cv_series
    pkf = PurgedKFold(n_splits=5, embargo_pct=0.01)
    splits = list(pkf.split(X, t1=t1))
    assert len(splits) == 5


def test_purged_kfold_fold_0_non_empty(synthetic_cv_series):
    """
    CRITICAL REGRESSION TEST for F02:
    In the legacy bug, line 80 discarded all training samples where t1 >= test_t0_min.
    For Fold 0 (where test is at the beginning), ALL subsequent samples have t1 > test_t0_min,
    which resulted in len(train_idx) == 0.
    This test verifies Fold 0 has a healthy, non-empty training set.
    """
    X, t1 = synthetic_cv_series
    pkf = PurgedKFold(n_splits=5, embargo_pct=0.01)
    splits = list(pkf.split(X, t1=t1))

    fold_0_train, fold_0_test = splits[0]
    assert len(fold_0_train) > 0, "Fold 0 train set must NOT be empty!"
    assert len(fold_0_test) == 20
    # In a 100-sample, 5-fold CV with 2-day horizon and 1% embargo, fold 0 should have ~77-79 train samples
    assert len(fold_0_train) >= 70


def test_purged_kfold_no_train_test_overlap(synthetic_cv_series):
    """Verify that train and test indices are strictly disjoint across every fold."""
    X, t1 = synthetic_cv_series
    pkf = PurgedKFold(n_splits=5, embargo_pct=0.02)

    for fold_num, (train_idx, test_idx) in enumerate(pkf.split(X, t1=t1)):
        intersection = set(train_idx).intersection(set(test_idx))
        assert len(intersection) == 0, f"Fold {fold_num} has overlapping indices: {intersection}"


def test_purged_kfold_pre_test_purging():
    """
    Verify that an observation occurring strictly before the test window is purged
    if and only if its label horizon t1 extends into the test window (t1 >= test_t0_min).
    """
    dates = pd.date_range("2024-01-01", periods=10, freq="D", tz="UTC")
    X = pd.DataFrame({"feat": np.arange(10)}, index=dates)

    # Let fold test set be indices [5, 6, 7] (test_t0_min is dates[5])
    # Pre-test sample at index 3 with t1 = dates[4] (does NOT bleed into test)
    # Pre-test sample at index 4 with t1 = dates[6] (BLEEDS into test!)
    t1_values = [
        dates[1], dates[2], dates[3], dates[4], dates[6],
        dates[7], dates[8], dates[9], dates[9], dates[9],
    ]
    t1 = pd.Series(t1_values, index=dates)

    pkf = PurgedKFold(n_splits=2, embargo_pct=0.0)
    splits = list(pkf.split(X, t1=t1))

    # Fold 1: test is indices 5..9. Pre-test are indices 0..4.
    train_idx, test_idx = splits[1]
    assert 3 in train_idx  # t1 = dates[4] < dates[5], so retained
    assert 4 not in train_idx  # t1 = dates[6] >= dates[5], so purged!


def test_purged_kfold_post_test_purging():
    """
    Verify that post-test samples whose t0 overlaps open test-set holding horizons
    (t0 <= max(test_t1)) are purged from training.
    """
    dates = pd.date_range("2024-01-01", periods=10, freq="D", tz="UTC")
    X = pd.DataFrame({"feat": np.arange(10)}, index=dates)

    # Fold 0: test is indices 0..4 (test_end = 5, dates[4] is last test sample)
    # Suppose test sample at index 4 has a long holding period until dates[6]
    t1_values = [
        dates[1], dates[2], dates[3], dates[4], dates[6],  # index 4 holds until dates[6]
        dates[7], dates[8], dates[9], dates[9], dates[9],
    ]
    t1 = pd.Series(t1_values, index=dates)

    pkf = PurgedKFold(n_splits=2, embargo_pct=0.0)
    splits = list(pkf.split(X, t1=t1))

    train_idx, test_idx = splits[0]
    # Post-test samples are indices 5..9 (dates[5] to dates[9])
    # Sample at index 5 has t0 = dates[5] <= test_t1_max (dates[6]) -> MUST BE PURGED
    assert 5 not in train_idx
    # Sample at index 6 has t0 = dates[6] <= test_t1_max (dates[6]) -> MUST BE PURGED
    assert 6 not in train_idx
    # Sample at index 7 has t0 = dates[7] > test_t1_max (dates[6]) -> MUST BE RETAINED
    assert 7 in train_idx


def test_purged_kfold_embargo_logic(synthetic_cv_series):
    """
    Verify that increasing embargo_pct removes additional samples immediately after the test window.
    """
    X, t1 = synthetic_cv_series  # 100 samples
    pkf_no_embargo = PurgedKFold(n_splits=5, embargo_pct=0.0)
    pkf_with_embargo = PurgedKFold(n_splits=5, embargo_pct=0.05)  # 5 samples embargoed

    splits_no = list(pkf_no_embargo.split(X, t1=t1))
    splits_emb = list(pkf_with_embargo.split(X, t1=t1))

    # Fold 0: test is 0..20. Embargo removes samples 20..25.
    train_no_emb, _ = splits_no[0]
    train_emb, _ = splits_emb[0]

    assert len(train_emb) < len(train_no_emb)
    # Check that indices 20..24 are NOT in train_emb
    for embargoed_idx in range(20, 25):
        assert embargoed_idx not in train_emb


def test_purged_kfold_fallback_when_t1_none(synthetic_cv_series):
    """Verify fallback to standard KFold when t1 is None."""
    X, _ = synthetic_cv_series
    pkf = PurgedKFold(n_splits=4)
    splits = list(pkf.split(X, t1=None))

    assert len(splits) == 4
    for train_idx, test_idx in splits:
        assert len(train_idx) == 75
        assert len(test_idx) == 25


def test_time_based_rolling_purged_cv():
    """
    Verify TimeBasedRollingPurgedCV correctly splits chronologically with
    purge buffer before test set and embargo buffer after test set start.
    """
    # 4 years of monthly trade records
    dates = pd.date_range("2020-01-01", "2024-01-01", freq="W")
    df = pd.DataFrame({"Time": dates, "Target": np.random.randint(0, 2, size=len(dates))})

    cv = TimeBasedRollingPurgedCV(train_months=24, test_months=6, purge_days=7, embargo_days=5)
    splits = list(cv.split(df, time_col="Time"))

    assert len(splits) > 0

    for train_idx, test_idx, t_start_str, t_end_str in splits:
        assert len(train_idx) > 0
        assert len(test_idx) > 0
        # No index overlap
        assert set(train_idx).isdisjoint(set(test_idx))

        train_times = df.loc[train_idx, "Time"]
        test_times = df.loc[test_idx, "Time"]

        # Purge and embargo separation: train_times and test_times must be separated by at least 12 days (7 days purge + 5 days embargo)
        assert test_times.min() - train_times.max() >= pd.Timedelta(days=12)
