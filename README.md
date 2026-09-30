# 🏛️ M2 Quant Pipeline: Meta-Labeling Framework

![Status](https://img.shields.io/badge/Status-Production_Ready-brightgreen)
![Architecture](https://img.shields.io/badge/Architecture-Python%20%7C%20C%2B%2B%20%7C%20MQL5-blue)
![Validation](https://img.shields.io/badge/Validation-Purged_WFM-orange)
![Execution](https://img.shields.io/badge/Latency-0ms_Native-success)

> **Overview:** This repository houses a production-grade, institutional Machine Learning pipeline designed for **MetaTrader 5**. Originally built to test a Hull Moving Average (HMA) breakout anomaly, the repository has evolved into a masterclass in quantitative infrastructure. 

While the specific HMA strategy suffered from *Alpha Decay* and was rigorously discarded, the **infrastructure built here is highly robust and reusable** for any future structural anomalies or trading algorithms.

---

## 🚀 The True Asset: The M2 Pipeline

In Quantitative Finance, a pipeline capable of strictly falsifying a bad strategy (preventing catastrophic loss of capital) is just as valuable as the strategy itself. This repository serves as a blueprint for implementing Marcos López de Prado's **Meta-Labeling** paradigm in retail and institutional forex trading.

### 🧠 Core Features & Full Potential
1. **Multi-Asset Ingestion (MQL5 ➡️ Python):** 
   - Synchronous, multi-timeframe feature extraction (OHLCV, Volatility, Kinematics) executed dynamically from MetaTrader 5 into clean CSV datasets.
2. **Triple-Barrier Method & Meta-Labeling:**
   - Instead of predicting price direction, the Machine Learning model (XGBoost) predicts the *probability of a trade succeeding*, acting as a risk-governor overlaying any base strategy (Model 1 + Model 2).
3. **Institutional Validation (Purged WFM):**
   - Strict Time-Based Rolling Walk-Forward Montecarlo validation.
   - Built-in `Embargo` and `Purging` rules to completely eliminate Data Leakage and serial correlation (Look-ahead bias).
4. **Zero-Latency Deployment (Python ➡️ C++ ➡️ MQL5):**
   - Python-trained XGBoost arrays are natively transpiled into C++ (`.mqh`) using `m2cgen`.
   - The models execute inside MT5 in under **0 milliseconds** locally, eliminating the need for slow Python REST APIs or external sockets.

---

## 📂 Repository Structure

The repository is strictly divided into the two core languages of the pipeline:

- 🐍 **`/python/m2_metalabeling/`**: The core ML Engine.
  - `labeling/`: Triple Barrier logic.
  - `models/`: Orchestrators (`portfolio_factory.py`), WFM training (`rolling_window_retrain.py`), and sanity audits (`audit_report.py`).
  - `export/`: C++ transpilation logic (`export_factory_oracle.py`).
- 📈 **`/mql5/`**: MetaTrader 5 Source Code.
  - `Experts/`: The Data Extractors and isolated Production Vaults (`Strategy_XAUUSD_Production.mq5`).
  - `Include/`: The transpiled C++ XGBoost Oracles ready for live execution.
- 📚 **`/docs/`**: Quantitative Research & Autopsies.
  - `CRONOLOGIA_PROYECTO_HMA.md`: The evolutionary timeline of the HMA experiment.
  - `POST_MORTEM.md`: A detailed explanation of Alpha Decay, Mathematical Lag, and why Moving Averages fail as entry triggers in modern HFT markets.

---

## 🔬 Research Conclusion: HMA Alpha Decay

Although the pipeline itself is a triumph, the original **Hull Moving Average (HMA)** strategy it was built for is **structurally unprofitable**.

The advanced Walk-Forward Montecarlo engine proved that Moving Averages suffer from severe **Mathematical Lag**. By the time the MA pivots, institutional algorithms (Mean-Reversion & HFT) are already fading the movement, turning retail MA-bots into exit liquidity. We openly document this failure in the `/docs` as an educational warning against over-optimization and the illusion of *Beta as Alpha*.

---

## 🤝 Usage & Adaptation

This repository is pristine, heavily documented, and stripped of all legacy noise. You can fork this M2 Pipeline and attach it to **any** base algorithmic strategy (Mean Reversion, Volatility breakouts, Statistical Arbitrage) by simply swapping the MQL5 Extractor logic and running the Python orchestrator.
