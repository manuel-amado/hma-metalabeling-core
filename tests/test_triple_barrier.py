"""
Unit tests for Triple Barrier Labeling module (m2_metalabeling.labeling.triple_barrier).
Validates Requirement R1 / Feature F18: Take-Profit, Stop-Loss, and vertical timeout barriers,
verifying exit_price != entry_price on timeout, and binary label assignments (0 vs 1).
"""

import numpy as np
import pandas as pd
import pytest

from m2_metalabeling.labeling.triple_barrier import (
    get_triple_barrier_labels,
    triple_barrier_labels,
)


@pytest.fixture
def base_price_series():
    """Deterministic hourly price and ATR series spanning 100 bars."""
    dates = pd.date_range("2024-01-01 00:00:00", periods=100, freq="h", tz="UTC")
    # Base price flat at 100.0, ATR fixed at 2.0
    close = pd.Series(100.0, index=dates)
    atr = pd.Series(2.0, index=dates)
    return close, atr, dates


def test_triple_barrier_take_profit_hit(base_price_series):
    """
    Verify that when price exceeds entry + pt_atr * atr,
    label is +1, bin is 1, ret is positive, and t1 records the barrier touch time.
    """
    close, atr, dates = base_price_series
    # Entry at t0 = dates[10], price = 100, atr = 2.0 -> PT = 100 + 2*2 = 104.0
    # Touch at dates[13] with price 105.0
    close = close.copy()
    close.iloc[13] = 105.0

    events = pd.DatetimeIndex([dates[10]])
    labels = get_triple_barrier_labels(close, atr, events, pt_atr=2.0, sl_atr=1.0, max_holding_bars=10)

    assert len(labels) == 1
    row = labels.iloc[0]
    assert row["label"] == 1
    assert row["bin"] == 1
    assert row["ret"] > 0
    assert row["t1"] == dates[13]
    assert row["exit_price"] == 105.0


def test_triple_barrier_stop_loss_hit(base_price_series):
    """
    Verify that when price falls below entry - sl_atr * atr,
    label is -1, bin is 0, ret is negative, and t1 records the barrier touch time.
    """
    close, atr, dates = base_price_series
    # Entry at t0 = dates[10], price = 100, atr = 2.0 -> SL = 100 - 1*2 = 98.0
    # Touch at dates[12] with price 97.0
    close = close.copy()
    close.iloc[12] = 97.0

    events = pd.DatetimeIndex([dates[10]])
    labels = get_triple_barrier_labels(close, atr, events, pt_atr=2.0, sl_atr=1.0, max_holding_bars=10)

    assert len(labels) == 1
    row = labels.iloc[0]
    assert row["label"] == -1
    assert row["bin"] == 0
    assert row["ret"] < 0
    assert row["t1"] == dates[12]
    assert row["exit_price"] == 97.0


def test_triple_barrier_timeout_profitable(base_price_series):
    """
    Regression Test for F03:
    When neither PT nor SL is touched within max_holding_bars,
    label is 0 (timeout), but exit_price MUST equal the closing price at the expiration horizon,
    NEVER reset to entry_price. If the trade gained price, bin must be 1.
    """
    close, atr, dates = base_price_series
    close = close.copy()
    # Entry at dates[10], price = 100.
    # PT is 104, SL is 98.
    # At holding limit (dates[10 + 5] = dates[15]), price closes at 102.5 (+1.25 ATR, profitable timeout).
    for i in range(11, 16):
        close.iloc[i] = 100.0 + (i - 10) * 0.5  # Reaches 102.5 at i=15

    events = pd.DatetimeIndex([dates[10]])
    labels = get_triple_barrier_labels(close, atr, events, pt_atr=2.0, sl_atr=1.0, max_holding_bars=5)

    assert len(labels) == 1
    row = labels.iloc[0]
    assert row["label"] == 0
    assert row["t1"] == dates[15]
    assert row["exit_price"] == pytest.approx(102.5, rel=1e-5)
    assert row["exit_price"] != 100.0  # Crucial regression check
    assert row["ret"] > 0
    assert row["bin"] == 1


def test_triple_barrier_timeout_unprofitable(base_price_series):
    """
    Verify timeout when price moves against trade without hitting SL:
    exit_price reflects lower closing price, ret is negative, and bin is 0.
    """
    close, atr, dates = base_price_series
    close = close.copy()
    # At expiration horizon (dates[15]), price is 99.0 (below 100, above SL 98)
    for i in range(11, 16):
        close.iloc[i] = 100.0 - (i - 10) * 0.2  # Reaches 99.0 at i=15

    events = pd.DatetimeIndex([dates[10]])
    labels = get_triple_barrier_labels(close, atr, events, pt_atr=2.0, sl_atr=1.0, max_holding_bars=5)

    assert len(labels) == 1
    row = labels.iloc[0]
    assert row["label"] == 0
    assert row["t1"] == dates[15]
    assert row["exit_price"] == pytest.approx(99.0, rel=1e-5)
    assert row["ret"] < 0
    assert row["bin"] == 0


def test_triple_barrier_strict_no_lookahead(base_price_series):
    """
    Verify that barrier logic strictly begins at t0 + 1 bar.
    The entry bar t0 price is recorded as entry_price, and subsequent bars (t0+1, t0+2, ...)
    are evaluated sequentially.
    """
    close, atr, dates = base_price_series
    close = close.copy()
    # Entry at dates[10], entry_price = 100.0, pt_level = 104.0
    # Bar at dates[11] is 102.0 (no barrier hit)
    # Bar at dates[12] is 105.0 (hits PT)
    close.iloc[11] = 102.0
    close.iloc[12] = 105.0

    events = pd.DatetimeIndex([dates[10]])
    labels = get_triple_barrier_labels(close, atr, events, pt_atr=2.0, sl_atr=1.0, max_holding_bars=5)

    assert len(labels) == 1
    row = labels.iloc[0]
    # Barrier touched at dates[12], not dates[11] or dates[10]
    assert row["label"] == 1
    assert row["t1"] == dates[12]
    assert row["exit_price"] == 105.0


def test_triple_barrier_missing_event_timestamp(base_price_series):
    """Verify that event timestamps not present in the price series index are skipped gracefully."""
    close, atr, dates = base_price_series
    missing_date = pd.Timestamp("2023-01-01 00:00:00", tz="UTC")
    valid_date = dates[10]

    events = pd.DatetimeIndex([missing_date, valid_date])
    labels = get_triple_barrier_labels(close, atr, events, pt_atr=2.0, sl_atr=1.0, max_holding_bars=5)

    assert len(labels) == 1
    assert labels.index[0] == valid_date


def test_triple_barrier_alias_parity(base_price_series):
    """Verify both function names (get_triple_barrier_labels and triple_barrier_labels) produce identical results."""
    close, atr, dates = base_price_series
    events = pd.DatetimeIndex([dates[10], dates[20]])

    df1 = get_triple_barrier_labels(close, atr, events, pt_atr=2.0, sl_atr=1.0, max_holding_bars=5)
    df2 = triple_barrier_labels(close, atr, events, pt_atr=2.0, sl_atr=1.0, max_holding_bars=5)

    pd.testing.assert_frame_equal(df1, df2)
