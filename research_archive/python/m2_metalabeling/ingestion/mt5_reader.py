"""
M2 Meta-Labeling Pipeline — Module: ingestion/mt5_reader.py
==============================================================
Consumes raw CSV files exported by the HMA_Data_Extractors (MQL5) and
returns a clean, indexed DataFrame ready for Feature Engineering.

Output columns (standard):
  open, high, low, close, volume,
  hma, hma_slope, hma_accel, hma_jerk,
  atr, rsi, ema200
  timestamp (index, UTC-aware)
"""

import pandas as pd
from pathlib import Path
from loguru import logger


RAW_DATA_DIR = Path(__file__).parents[3] / "data" / "raw"


def load_mt5_csv(filepath: str | Path, symbol: str = "XAUUSD") -> pd.DataFrame:
    """
    Load and sanitize a raw CSV exported from MetaTrader 5 (HMA_Extractor_*.mq5).

    Args:
        filepath: Path to the raw CSV file.
        symbol: Used only for logging purposes.

    Returns:
        Clean DataFrame indexed by UTC datetime.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"[M2 Ingestion] File not found: {filepath}")

    logger.info(f"Loading {symbol} data from {filepath.name}")

    df = pd.read_csv(
        filepath,
        parse_dates=["timestamp"],
        index_col="timestamp",
    )

    # Enforce UTC timezone-awareness
    if df.index.tzinfo is None:
        df.index = df.index.tz_localize("UTC")

    # Drop duplicates and sort chronologically
    df = df[~df.index.duplicated(keep="first")].sort_index()

    logger.success(f"Loaded {len(df):,} bars for {symbol}.")
    return df
