"""
Unit tests for MT5 CSV data ingestion module (m2_metalabeling.ingestion.mt5_reader).
Validates Requirement R1 / Feature F17: schema validation, timestamp localization,
chronological sorting, deduplication, and error handling.
"""

from pathlib import Path
import pandas as pd
import pytest

from m2_metalabeling.ingestion.mt5_reader import load_mt5_csv


def test_load_mt5_csv_success(synthetic_mt5_csv_path: Path):
    """Verify loading a valid MT5 CSV returns a sanitized, UTC-indexed DataFrame."""
    df = load_mt5_csv(synthetic_mt5_csv_path, symbol="EURUSD")
    
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert len(df) == 300
    assert isinstance(df.index, pd.DatetimeIndex)
    assert str(df.index.tz) == "UTC"
    assert df.index.is_monotonic_increasing
    assert not df.index.has_duplicates
    
    expected_cols = {"open", "high", "low", "close", "volume", "atr", "rsi", "ema200"}
    assert expected_cols.issubset(set(df.columns))


def test_load_mt5_csv_file_not_found(tmp_path: Path):
    """Verify FileNotFoundError is raised when target CSV does not exist."""
    missing_path = tmp_path / "ghost_file_missing.csv"
    with pytest.raises(FileNotFoundError, match="File not found"):
        load_mt5_csv(missing_path, symbol="XAUUSD")


def test_load_mt5_csv_deduplication(tmp_path: Path):
    """Verify duplicate bar timestamps are eliminated keeping the first record."""
    csv_file = tmp_path / "duplicates.csv"
    content = (
        "timestamp,open,high,low,close,volume\n"
        "2024-01-01 00:00:00,100,105,95,102,500\n"
        "2024-01-01 00:00:00,101,106,96,103,600\n"  # Duplicate timestamp
        "2024-01-01 01:00:00,102,107,97,104,700\n"
    )
    csv_file.write_text(content, encoding="utf-8")

    df = load_mt5_csv(csv_file)
    assert len(df) == 2
    assert not df.index.has_duplicates
    assert df.iloc[0]["close"] == 102  # Kept the first occurrence


def test_load_mt5_csv_chronological_ordering(tmp_path: Path):
    """Verify bars appearing out of order are sorted chronologically."""
    csv_file = tmp_path / "unsorted.csv"
    content = (
        "timestamp,open,high,low,close,volume\n"
        "2024-01-01 03:00:00,103,108,98,105,500\n"
        "2024-01-01 01:00:00,101,106,96,102,500\n"
        "2024-01-01 02:00:00,102,107,97,104,500\n"
    )
    csv_file.write_text(content, encoding="utf-8")

    df = load_mt5_csv(csv_file)
    assert df.index.is_monotonic_increasing
    assert df.index[0] == pd.Timestamp("2024-01-01 01:00:00", tz="UTC")
    assert df.index[-1] == pd.Timestamp("2024-01-01 03:00:00", tz="UTC")


def test_load_mt5_csv_tz_aware_inputs(tmp_path: Path):
    """Verify CSV with pre-existing timezone offsets parses cleanly to UTC."""
    csv_file = tmp_path / "tz_aware.csv"
    content = (
        "timestamp,open,high,low,close,volume\n"
        "2024-01-01 00:00:00+00:00,100,105,95,102,500\n"
        "2024-01-01 01:00:00+00:00,102,107,97,104,700\n"
    )
    csv_file.write_text(content, encoding="utf-8")

    df = load_mt5_csv(csv_file)
    assert str(df.index.tz) == "UTC"
    assert len(df) == 2


def test_load_mt5_csv_missing_timestamp_column(tmp_path: Path):
    """Verify ValueError or KeyError occurs if CSV lacks the required timestamp column."""
    csv_file = tmp_path / "no_timestamp.csv"
    content = (
        "date,open,high,low,close,volume\n"
        "2024-01-01,100,105,95,102,500\n"
    )
    csv_file.write_text(content, encoding="utf-8")

    with pytest.raises((ValueError, KeyError)):
        load_mt5_csv(csv_file)


def test_load_mt5_csv_empty_file(tmp_path: Path):
    """Verify pd.errors.EmptyDataError is raised when reading an empty file."""
    csv_file = tmp_path / "empty.csv"
    csv_file.write_text("", encoding="utf-8")

    with pytest.raises(pd.errors.EmptyDataError):
        load_mt5_csv(csv_file)
