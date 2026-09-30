"""
M2 Meta-Labeling Pipeline — Module: cross_validation/purged_cv.py
===================================================================
Implements Purged K-Fold + Embargo strictly following
López de Prado (Advances in Financial Machine Learning, Ch. 7).

WHY THIS EXISTS:
    Standard K-Fold cross-validation causes catastrophic data leakage
    in financial time series because:
      1. Labels from bar t0 span FORWARD in time (via Triple Barrier).
         A bar in the TRAIN set may have its label overlapping with
         observations in the TEST set → the model "sees the future".
      2. Consecutive bars are highly auto-correlated → shuffled splits
         overstate test-set performance massively.

SOLUTION — Two-step protection:
    PURGING:   Remove from TRAIN any sample whose label period (t0→t1)
               overlaps with any bar in the TEST set.
    EMBARGOING: Remove from TRAIN an additional buffer of `embargo_pct`
               bars AFTER the test set ends (to prevent leakage from
               serialcorrelation at the split boundary).
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import KFold
from loguru import logger


class PurgedKFold:
    """
    Purged + Embargoed K-Fold splitter for financial time series.

    Args:
        n_splits:      Number of folds.
        embargo_pct:   Fraction of total bars to embargo after each test set.
                       Typical: 0.01 (1% of total observations).
    """

    def __init__(self, n_splits: int = 5, embargo_pct: float = 0.01):
        self.n_splits = n_splits
        self.embargo_pct = embargo_pct

    def split(
        self,
        X: pd.DataFrame,
        y: pd.Series | None = None,
        t1: pd.Series | None = None,
    ):
        """
        Yield (train_indices, test_indices) pairs with purging & embargo.

        Args:
            X:   Feature matrix (index = t0 datetimes).
            y:   Labels (ignored, kept for sklearn API compat).
            t1:  Series of label-end timestamps (t0 → t1, Triple Barrier output).
                 Required for purging. If None, falls back to standard KFold.
        """
        if t1 is None:
            logger.warning("t1 not provided — falling back to standard KFold (no purging).")
            kf = KFold(n_splits=self.n_splits)
            yield from kf.split(X)
            return

        n_obs = len(X)
        embargo_size = int(n_obs * self.embargo_pct)
        indices = np.arange(n_obs)
        test_ranges = [(i[0], i[-1] + 1) for i in np.array_split(indices, self.n_splits)]

        for test_start, test_end in test_ranges:
            test_idx = indices[test_start:test_end]
            test_t0_min = X.index[test_start]
            test_t0_max = X.index[test_end - 1]

            # PURGING: remove train samples whose t1 overlaps the test window
            train_idx = []
            for i in indices:
                if i in test_idx:
                    continue
                if t1.iloc[i] >= test_t0_min:   # label end bleeds into test
                    continue
                train_idx.append(i)

            # EMBARGO: remove the `embargo_size` bars after the test set
            embargo_start = test_end
            embargo_end = min(test_end + embargo_size, n_obs)
            embargoed = set(range(embargo_start, embargo_end))
            train_idx = [i for i in train_idx if i not in embargoed]

            logger.debug(
                f"Fold | train={len(train_idx)}, test={len(test_idx)}, embargoed={len(embargoed)}"
            )
            yield np.array(train_idx), test_idx
