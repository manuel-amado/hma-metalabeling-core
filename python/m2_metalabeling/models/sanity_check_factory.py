"""
M2 Meta-Labeling Pipeline — Module: models/sanity_check_factory.py
===================================================================
Institutional OOS Rolling Walk-Forward sanity check (2015-2026).
"""

from pathlib import Path
from typing import Optional
import warnings
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import roc_auc_score
from loguru import logger

warnings.filterwarnings("ignore")

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATASET = PROJECT_ROOT / "portfolio" / "XAUUSD" / "XGBoost_Dataset_XAUUSD.csv"


class TimeBasedRollingPurgedCV:
    """Time-based rolling window cross-validation with purging and embargo."""

    def __init__(self, train_months=24, test_months=6, purge_days=7, embargo_days=5):
        self.train_offset = pd.DateOffset(months=train_months)
        self.test_offset = pd.DateOffset(months=test_months)
        self.purge_offset = pd.Timedelta(days=purge_days)
        self.embargo_offset = pd.Timedelta(days=embargo_days)

    def split(self, df, time_col="Time"):
        times = pd.to_datetime(df[time_col])
        start_date = times.min()
        end_date = times.max()

        current_train_start = start_date

        while True:
            current_train_end = current_train_start + self.train_offset
            current_test_start = current_train_end
            current_test_end = current_test_start + self.test_offset

            if current_test_start >= end_date:
                break

            purge_cut = current_train_end - self.purge_offset
            embargo_cut = current_test_start + self.embargo_offset

            train_mask = (times >= current_train_start) & (times <= purge_cut)
            test_mask = (times >= embargo_cut) & (times < current_test_end) & (times <= end_date)

            train_idx = df.index[train_mask].tolist()
            test_idx = df.index[test_mask].tolist()

            if len(train_idx) > 0 and len(test_idx) > 0:
                yield (
                    train_idx,
                    test_idx,
                    current_test_start.strftime("%Y-%m"),
                    current_test_end.strftime("%Y-%m"),
                )

            current_train_start += self.test_offset


def run_sanity_check(
    dataset_path: Optional[Path] = None,
    random_state: int = 42,
) -> float:
    """
    Run rolling walk-forward sanity check on the specified dataset.

    Returns:
        Mean OOS AUC score across folds.
    """
    if dataset_path is None or not Path(dataset_path).exists():
        dataset_path = DEFAULT_DATASET

    dataset_path = Path(dataset_path)
    if not dataset_path.exists():
        raise FileNotFoundError(f"Sanity check dataset not found at: {dataset_path}")

    logger.info(f"Loading dataset from {dataset_path}...")
    df = pd.read_csv(dataset_path)
    df["Time"] = pd.to_datetime(df["Time"])

    logger.info("=== BACKTEST INSTITUCIONAL: PURGED ROLLING WALK-FORWARD (2015-2026) ===")
    logger.info(f"Trades totales en Bóveda: {len(df)}")
    if "Target" in df.columns:
        logger.info(f"Win Rate base histórico: {df.Target.mean():.2%}")

    feature_cols = [
        "Keltner_Bandwidth_H4",
        "ATR_Ratio_H1_D1",
        "ADX_Value_H4",
        "ADX_Slope_H4",
        "Dist_EMA200_H4",
        "Bollinger_Width_H1",
        "Daily_Exhaustion",
    ]
    available_cols = [c for c in feature_cols if c in df.columns]

    cv = TimeBasedRollingPurgedCV(train_months=24, test_months=6, purge_days=7, embargo_days=5)

    model_params = dict(
        n_estimators=100,
        max_depth=3,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=random_state,
        eval_metric="logloss",
        base_score=0.5,
    )

    fold_aucs = []
    fold = 1
    for tr_idx, te_idx, test_start_str, test_end_str in cv.split(df):
        Xtr = df.iloc[tr_idx][available_cols]
        ytr = df.iloc[tr_idx]["Target"]
        Xte = df.iloc[te_idx][available_cols]
        yte = df.iloc[te_idx]["Target"]

        if len(np.unique(ytr)) < 2 or len(np.unique(yte)) < 2:
            logger.debug(f"[Fold {fold}] OOS: {test_start_str} to {test_end_str} | Omitido (Clase Única)")
            fold += 1
            continue

        m = xgb.XGBClassifier(**model_params)
        m.fit(Xtr, ytr)
        preds = m.predict_proba(Xte)[:, 1]

        try:
            auc = roc_auc_score(yte, preds)
            fold_aucs.append(auc)
            logger.info(
                f"[Fold {fold:<2}] OOS: {test_start_str} to {test_end_str} | "
                f"Train: {len(Xtr):<3} | Test: {len(Xte):<2} | AUC: {auc:.3f}"
            )
        except Exception:
            logger.warning(f"[Fold {fold:<2}] OOS: {test_start_str} to {test_end_str} | Error AUC")

        fold += 1

    if len(fold_aucs) > 0:
        mean_auc = float(np.mean(fold_aucs))
        logger.success(f"[RESULTADO DEFINITIVO GLOBAL] AUC Medio Histórico (OOS Puro): {mean_auc:.3f}")
        return mean_auc
    else:
        logger.warning("[ALERTA] No se pudieron calcular AUCs válidos.")
        return 0.0


if __name__ == "__main__":
    run_sanity_check()
