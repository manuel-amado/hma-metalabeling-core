"""
M2 Meta-Labeling Pipeline — Module: calibration/probability_calibration.py
============================================================================
Calibrates raw XGBoost probability outputs before converting them to
position sizes in MetaTrader 5.

WHY CALIBRATION IS CRITICAL:
    XGBoost (and ensemble trees in general) produce DISCRIMINATIVE scores,
    not true probabilities. A raw XGBoost output of 0.7 does NOT mean
    "70% chance of winning". Studies show tree models are systematically
    overconfident in intermediate ranges and poorly calibrated near 0/1.

    In a real trading context, the model's output drives SIZE:
        size = f(p_predicted)    where p > threshold → trade, p < threshold → skip
    An uncalibrated model will generate trades with distorted confidence,
    leading to miscalibrated risk and ultimately drawdowns that exceed
    the theoretical model.

SOLUTION:
    Isotonic Regression calibration (non-parametric, better than Platt/Sigmoid
    for tree-based models) fitted on a HELD-OUT calibration set (never trained on).
"""

import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from loguru import logger
import matplotlib.pyplot as plt


MODELS_DIR = Path(__file__).parents[3] / "models"


def calibrate_model(
    base_model,
    X_calib: pd.DataFrame,
    y_calib: pd.Series,
    method: str = "isotonic",
    cv: str = "prefit",
) -> CalibratedClassifierCV:
    """
    Wrap a pre-fitted XGBoost model with Isotonic calibration.

    Args:
        base_model:  Fitted XGBClassifier instance.
        X_calib:     Held-out calibration features (NEVER seen during training).
        y_calib:     True binary labels for calibration set.
        method:      'isotonic' (recommended for trees) or 'sigmoid' (Platt).
        cv:          'prefit' means base_model is already fitted.

    Returns:
        CalibratedClassifierCV instance ready for production inference.
    """
    logger.info(f"Calibrating model with method='{method}' on {len(X_calib)} samples.")
    calibrated = CalibratedClassifierCV(
        estimator=base_model,
        method=method,
        cv=cv,
    )
    calibrated.fit(X_calib, y_calib)
    logger.success("Model calibration complete.")
    return calibrated


def plot_reliability_diagram(
    model,
    X_val: pd.DataFrame,
    y_val: pd.Series,
    label: str = "Model",
    n_bins: int = 10,
    output_path: Path | None = None,
) -> None:
    """
    Generate a Reliability (Calibration) Diagram to visually verify
    how well predicted probabilities match observed frequencies.

    A perfectly calibrated model produces a straight diagonal line.
    Points above diagonal → underconfident. Below → overconfident.
    """
    y_prob = model.predict_proba(X_val)[:, 1]
    fraction_of_positives, mean_predicted_value = calibration_curve(
        y_val, y_prob, n_bins=n_bins
    )

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot([0, 1], [0, 1], "k--", label="Perfect calibration")
    ax.plot(mean_predicted_value, fraction_of_positives, "s-", label=label)
    ax.set_xlabel("Mean Predicted Probability")
    ax.set_ylabel("Fraction of Positives")
    ax.set_title(f"Reliability Diagram — {label}")
    ax.legend()
    ax.grid(True, alpha=0.3)

    if output_path:
        fig.savefig(output_path, dpi=150, bbox_inches="tight")
        logger.info(f"Reliability diagram saved to {output_path}")
    plt.close(fig)


def apply_size_mapping(
    proba: np.ndarray,
    threshold: float = 0.54,
    scale: bool = False,
) -> np.ndarray:
    """
    Convert calibrated probability to binary position size (0 or 1).
    Optionally scale size proportionally to confidence above threshold.

    Args:
        proba:      Array of calibrated probabilities in [0, 1].
        threshold:  Minimum probability to open a trade.
        scale:      If True, size = (p - threshold) / (1 - threshold).
                    If False, size is strictly binary: 0 or 1.

    Returns:
        Array of sizes (float in [0,1] if scale=True, else 0 or 1).
    """
    if scale:
        sizes = np.where(proba >= threshold, (proba - threshold) / (1 - threshold), 0.0)
    else:
        sizes = (proba >= threshold).astype(float)
    return sizes
