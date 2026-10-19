"""
M2 Meta-Labeling Pipeline — Module: models/audit_report.py
============================================================
HTML backtest tester report parsing and institutional audit metrics.
"""

import os
from pathlib import Path
from typing import Optional
import numpy as np
import pandas as pd
from loguru import logger

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def parse_profit(x):
    if pd.isna(x):
        return 0.0
    try:
        return float(str(x).replace(" ", ""))
    except Exception:
        return 0.0


def analyze_subset(subset: pd.DataFrame, name: str) -> dict:
    if len(subset) == 0:
        print(f"{name:<22} No trades")
        return {}
    n = len(subset)
    wins = int(subset["Target"].sum())
    wr = wins / n
    gross_p = float(subset[subset["Profit"] > 0]["Profit"].sum())
    gross_l = float(abs(subset[subset["Profit"] < 0]["Profit"].sum()))
    pf = gross_p / gross_l if gross_l > 0 else 0.0
    ev = float(subset["Profit"].sum() / n)
    total = float(subset["Profit"].sum())
    avg_win = float(subset[subset["Profit"] > 0]["Profit"].mean()) if wins > 0 else 0.0
    avg_loss = float(subset[subset["Profit"] < 0]["Profit"].mean()) if (n - wins) > 0 else 0.0
    rr = abs(avg_win / avg_loss) if avg_loss != 0 else 0.0
    print(
        f"{name:<22} | Trades:{n:<4} | WR:{wr:.1%} | "
        f"Profit:{total:>9.2f} | PF:{pf:.2f} | EV:{ev:>7.2f} | R:R:{rr:.2f}"
    )
    return {
        "trades": n,
        "win_rate": wr,
        "profit": total,
        "profit_factor": pf,
        "ev": ev,
        "rr": rr,
    }


def generate_audit_report(file_path: Optional[str | Path] = None) -> dict:
    """
    Parse an MT5 Strategy Tester HTML report, or compute audit metrics from repository datasets.
    """
    outs = None

    if file_path is None:
        env_path = os.environ.get("MT5_TESTER_REPORT")
        if env_path and Path(env_path).exists():
            file_path = Path(env_path)
        else:
            candidates = list(PROJECT_ROOT.glob("**/ReportTester*.html"))
            if candidates:
                file_path = candidates[0]

    if file_path is not None and Path(file_path).exists():
        logger.info(f"Parsing MT5 HTML report from: {file_path}")
        tables = pd.read_html(str(file_path))
        df = tables[1] if len(tables) > 1 else tables[0]
        idx_deals = df[df[0].astype(str).str.contains("Transacciones", na=False)].index.tolist()
        if idx_deals:
            deals = df.iloc[idx_deals[0] + 2 :].copy()
            deals.columns = [
                "Time", "Deal", "Symbol", "Type", "Dir", "Volume",
                "Price", "Order", "Commission", "Swap", "Profit", "Balance", "Comment"
            ][: len(deals.columns)]
            deals = deals.dropna(subset=["Dir"])
            outs = deals[deals["Dir"] == "out"].copy()
            outs["Profit"] = outs["Profit"].apply(parse_profit)
            outs["Time"] = pd.to_datetime(outs["Time"])
            outs["TradeType"] = np.where(outs["Type"] == "sell", "Long", "Short")
            outs["Target"] = (outs["Profit"] > 0).astype(int)

    if outs is None or len(outs) == 0:
        logger.info("No MT5 HTML report available; generating audit metrics from repository dataset...")
        dataset_path = PROJECT_ROOT / "data" / "processed" / "XGBoost_Dataset_XAUUSD.csv"
        if not dataset_path.exists():
            raise FileNotFoundError(
                f"Neither HTML report ({file_path}) nor dataset ({dataset_path}) found."
            )
        ds = pd.read_csv(dataset_path)
        outs = pd.DataFrame()
        outs["Time"] = pd.to_datetime(ds["Time"])
        outs["Profit"] = ds["Profit"]
        outs["TradeType"] = np.where(ds["Signal_Dir"] == 1.0, "Long", "Short") if "Signal_Dir" in ds.columns else "Long"
        outs["Target"] = (outs["Profit"] > 0).astype(int)

    outs["Zone"] = np.where(outs["Time"] < pd.to_datetime("2023-01-01"), "IS", "OOS")

    print("\n=== REPORTE COMPLETO DE AUDITORÍA INSTITUCIONAL ===")
    print("\n--- DIRECCIONALIDAD ---")
    metrics_global = analyze_subset(outs, "GLOBAL")
    analyze_subset(outs[outs["TradeType"] == "Long"], "LONGS")
    analyze_subset(outs[outs["TradeType"] == "Short"], "SHORTS")

    print("\n--- IS vs OOS ---")
    is_set = outs[outs["Zone"] == "IS"]
    oos_set = outs[outs["Zone"] == "OOS"]
    analyze_subset(is_set, "IN-SAMPLE (2015-2022)")
    analyze_subset(oos_set, "OUT-OF-SAMPLE (2023+)")

    print("\n--- DEGRADACION IS->OOS ---")
    if len(is_set) > 0 and len(oos_set) > 0:
        gross_p_is = is_set[is_set["Profit"] > 0]["Profit"].sum()
        gross_l_is = abs(is_set[is_set["Profit"] < 0]["Profit"].sum())
        is_pf = gross_p_is / gross_l_is if gross_l_is > 0 else 0.0

        gross_p_oos = oos_set[oos_set["Profit"] > 0]["Profit"].sum()
        gross_l_oos = abs(oos_set[oos_set["Profit"] < 0]["Profit"].sum())
        oos_pf = gross_p_oos / gross_l_oos if gross_l_oos > 0 else 0.0

        is_wr = is_set["Target"].mean()
        oos_wr = oos_set["Target"].mean()
        print(f"  WR: IS={is_wr:.1%} -> OOS={oos_wr:.1%} | Degradacion: {(oos_wr - is_wr) * 100:+.1f} pp")
        pf_deg = ((oos_pf / is_pf) - 1) * 100 if is_pf > 0 else 0.0
        print(f"  PF: IS={is_pf:.2f} -> OOS={oos_pf:.2f} | Degradacion: {pf_deg:+.1f}%")

    print("\n--- DRAWDOWN Y CONSISTENCIA TEMPORAL ---")
    outs_sorted = outs.sort_values("Time").copy()
    outs_sorted["Cumulative"] = outs_sorted["Profit"].cumsum()
    outs_sorted["Running_Max"] = outs_sorted["Cumulative"].cummax()
    outs_sorted["Drawdown"] = outs_sorted["Cumulative"] - outs_sorted["Running_Max"]
    max_dd = float(outs_sorted["Drawdown"].min())
    print(f"  Max Drawdown (en beneficio acumulado): {max_dd:.2f}")

    print("\n--- CONSISTENCIA ANUAL ---")
    outs_sorted["Year"] = outs_sorted["Time"].dt.year
    for yr, grp in outs_sorted.groupby("Year"):
        tag = " [OOS]" if yr >= 2023 else " [IS] "
        g_p = grp[grp["Profit"] > 0]["Profit"].sum()
        g_l = abs(grp[grp["Profit"] < 0]["Profit"].sum())
        pf = g_p / g_l if g_l > 0 else 0.0
        print(
            f"  {yr}{tag} Trades:{len(grp):<3} WR:{grp.Target.mean():.1%} "
            f"Profit:{grp.Profit.sum():>9.2f} PF:{pf:.2f}"
        )

    return metrics_global


if __name__ == "__main__":
    generate_audit_report()
