"""
M2 Meta-Labeling Pipeline — Module: labeling/triple_barrier.py
================================================================
Implements López de Prado's Triple Barrier Method with strict
Data Leakage protection (no look-ahead bias).

The three barriers:
  - Upper (Profit Taking):  price rises by pt_atr * ATR above entry
  - Lower (Stop Loss):      price falls by sl_atr * ATR below entry
  - Vertical (Timeout):     t_events + max_holding_bars
"""

import numpy as np
import pandas as pd
from loguru import logger


def get_triple_barrier_labels(
    close: pd.Series,
    atr: pd.Series,
    events: pd.DatetimeIndex,
    pt_atr: float = 2.0,
    sl_atr: float = 1.0,
    max_holding_bars: int = 48,
) -> pd.DataFrame:
    """
    Compute Triple Barrier labels strictly avoiding look-ahead.

    Args:
        close:             Price series (H1 OHLCV close).
        atr:               ATR series aligned with close.
        events:            Index of bar-open signals to label.
        pt_atr:            Profit-Taking multiplier (in ATR units).
        sl_atr:            Stop-Loss multiplier (in ATR units).
        max_holding_bars:  Maximum bars before vertical barrier fires.

    Returns:
        DataFrame with columns:
            t1       (datetime): when the barrier was touched
            ret      (float):    log-return at touch
            label    (int):      +1 (profit), -1 (stop loss), 0 (timeout)
            bin      (int):      meta-label: 1 if profitable, 0 otherwise
    """
    results = []

    for t0 in events:
        if t0 not in close.index:
            continue

        entry_price = close.loc[t0]
        entry_atr = atr.loc[t0]

        pt_level = entry_price + pt_atr * entry_atr
        sl_level = entry_price - sl_atr * entry_atr

        # Slice forward (strict: t0 is NOT included)
        future = close.loc[t0:].iloc[1: max_holding_bars + 1]

        label, t1, exit_price = 0, future.index[-1] if len(future) else t0, entry_price

        for t_bar, price in future.items():
            if price >= pt_level:
                label, t1, exit_price = 1, t_bar, price
                break
            elif price <= sl_level:
                label, t1, exit_price = -1, t_bar, price
                break

        log_ret = np.log(exit_price / entry_price)
        results.append({
            "t0": t0,
            "t1": t1,
            "ret": log_ret,
            "label": label,
            "bin": int(log_ret > 0),   # Meta-label: did the PRIMARY model make money?
        })

    df_labels = pd.DataFrame(results).set_index("t0")
    logger.info(f"Labels: +1={( df_labels.label==1).sum()}, "
                f"-1={(df_labels.label==-1).sum()}, "
                f"0={(df_labels.label==0).sum()}")
    return df_labels
