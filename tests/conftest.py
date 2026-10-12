"""
Reusable pytest fixtures for the HMA Meta-Labeling test suite.
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import pytest
import xgboost as xgb

# Ensure python root is importable
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PYTHON_DIR = PROJECT_ROOT / "python"
if str(PYTHON_DIR) not in sys.path:
    sys.path.insert(0, str(PYTHON_DIR))


@pytest.fixture
def synthetic_ohlcv_data() -> pd.DataFrame:
    """
    Generate 300 bars of synthetic financial OHLCV data with technical indicators.
    Uses UTC DatetimeIndex and deterministic random walk.
    """
    np.random.seed(42)
    n_bars = 300
    timestamps = pd.date_range("2024-01-01 00:00:00", periods=n_bars, freq="h", tz="UTC")
    
    # Deterministic price series
    returns = np.random.normal(0.0002, 0.008, size=n_bars)
    price_curve = 2000.0 * np.cumprod(1.0 + returns)
    
    opens = price_curve * (1.0 + np.random.uniform(-0.001, 0.001, size=n_bars))
    closes = price_curve * (1.0 + np.random.uniform(-0.001, 0.001, size=n_bars))
    highs = np.maximum(opens, closes) * (1.0 + np.random.uniform(0.0, 0.004, size=n_bars))
    lows = np.minimum(opens, closes) * (1.0 - np.random.uniform(0.0, 0.004, size=n_bars))
    volumes = np.random.randint(100, 5000, size=n_bars).astype(float)
    
    # Synthetic technical indicators
    atr = (highs - lows) * 1.2
    rsi = np.clip(50.0 + np.cumsum(np.random.normal(0, 2, size=n_bars)), 10.0, 90.0)
    ema200 = pd.Series(closes).ewm(span=200, adjust=False).mean().values

    df = pd.DataFrame(
        {
            "open": opens,
            "high": highs,
            "low": lows,
            "close": closes,
            "volume": volumes,
            "hma": closes * 1.001,
            "hma_slope": np.gradient(closes),
            "hma_accel": np.gradient(np.gradient(closes)),
            "hma_jerk": np.zeros(n_bars),
            "atr": atr,
            "rsi": rsi,
            "ema200": ema200,
        },
        index=timestamps,
    )
    df.index.name = "timestamp"
    return df


@pytest.fixture
def synthetic_mt5_csv_path(tmp_path: Path, synthetic_ohlcv_data: pd.DataFrame) -> Path:
    """
    Export synthetic OHLCV data to a CSV file matching the MT5 extractor format.
    """
    csv_file = tmp_path / "EURUSD_H1_test.csv"
    synthetic_ohlcv_data.to_csv(csv_file, index=True)
    return csv_file


@pytest.fixture
def synthetic_features_dataset() -> pd.DataFrame:
    """
    Generate synthetic dataset matching the institutional 7-feature schema:
    Keltner_Bandwidth_H4, ATR_Ratio_H1_D1, ADX_Value_H4, ADX_Slope_H4,
    Dist_EMA200_H4, Bollinger_Width_H1, Daily_Exhaustion, Target, Signal_Dir, Time.
    """
    np.random.seed(42)
    n_samples = 250
    dates = pd.date_range("2024-01-01", periods=n_samples, freq="4h", tz="UTC")
    
    keltner = np.random.uniform(0.005, 0.025, size=n_samples)
    atr_ratio = np.random.uniform(0.10, 0.35, size=n_samples)
    adx_val = np.random.uniform(15.0, 45.0, size=n_samples)
    adx_slope = np.random.uniform(-5.0, 5.0, size=n_samples)
    dist_ema = np.random.uniform(-0.05, 0.05, size=n_samples)
    bb_width = np.random.uniform(0.004, 0.020, size=n_samples)
    daily_exh = np.random.uniform(0.4, 1.8, size=n_samples)
    
    # Ground truth logistic signal
    latent = (
        2.5 * keltner
        + 1.2 * atr_ratio
        + 0.05 * (adx_val - 25.0)
        + 0.15 * adx_slope
        + 5.0 * dist_ema
        + np.random.normal(0, 0.3, size=n_samples)
    )
    prob = 1.0 / (1.0 + np.exp(-latent))
    target = (prob > 0.5).astype(int)
    profit = np.where(target == 1, np.random.uniform(100, 1500, size=n_samples), np.random.uniform(-1500, -100, size=n_samples))

    df = pd.DataFrame(
        {
            "Ticket": np.arange(1000, 1000 + n_samples),
            "Time": dates,
            "Signal_Dir": np.ones(n_samples),
            "Keltner_Bandwidth_H4": keltner,
            "ATR_Ratio_H1_D1": atr_ratio,
            "ADX_Value_H4": adx_val,
            "ADX_Slope_H4": adx_slope,
            "Dist_EMA200_H4": dist_ema,
            "Bollinger_Width_H1": bb_width,
            "Daily_Exhaustion": daily_exh,
            "Profit": profit,
            "Target": target,
        }
    )
    return df


@pytest.fixture
def feature_columns() -> list[str]:
    """Canonical 7 features used across all M2 Meta-Labeling models."""
    return [
        "Keltner_Bandwidth_H4",
        "ATR_Ratio_H1_D1",
        "ADX_Value_H4",
        "ADX_Slope_H4",
        "Dist_EMA200_H4",
        "Bollinger_Width_H1",
        "Daily_Exhaustion",
    ]


@pytest.fixture
def fitted_xgb_model(synthetic_features_dataset: pd.DataFrame, feature_columns: list[str]) -> xgb.XGBClassifier:
    """
    Produce a deterministic, lightweight fitted XGBClassifier with base_score=0.5.
    """
    X = synthetic_features_dataset[feature_columns]
    y = synthetic_features_dataset["Target"]
    
    model = xgb.XGBClassifier(
        n_estimators=10,
        max_depth=3,
        learning_rate=0.1,
        subsample=0.9,
        colsample_bytree=0.9,
        random_state=42,
        base_score=0.5,
        eval_metric="logloss",
    )
    model.fit(X, y)
    return model


@pytest.fixture
def sample_feature_vector() -> np.ndarray:
    """Sample 7-feature numerical vector for inference tests."""
    return np.array([0.012, 0.185, 29.5, -1.25, 0.025, 0.008, 1.15], dtype=np.float64)
