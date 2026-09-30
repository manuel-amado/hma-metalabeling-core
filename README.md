# HMA Meta-Labeling Project (Archived)

![Status](https://img.shields.io/badge/Status-Archived%20%2F%20Post--Mortem-red)
![Type](https://img.shields.io/badge/Type-Quantitative%20Research-blue)

This repository contains the rigorous quantitative research, machine learning framework, and ultimate post-mortem of an algorithmic trading strategy based on the **Hull Moving Average (HMA)** combined with **XGBoost Meta-Labeling**.

> **⚠️ WARNING:** This strategy failed Out-of-Sample (OOS) validation and is structurally unprofitable. This repository has been open-sourced strictly for educational purposes to demonstrate advanced Walk-Forward validation, the dangers of over-optimization, and how to properly kill a trading strategy before risking capital.

## 📂 Repository Structure

- `/docs`: Extensive documentation, methodologies, and the quantitative autopsy.
  - [Post Mortem (Why the strategy failed)](docs/POST_MORTEM.md)
  - [Methodology (ML pipeline & validation)](docs/METHODOLOGY.md)
- `/src`: Cleaned source code.
  - `/mql5`: The MT5 Expert Advisors (Strategy chassis & feature extractor).
  - `/python`: The core Machine Learning pipeline.
- `/research_archive`: History of iterations, patches, failed experiments, and data pipelines.

## 🧠 Key Takeaways
1. **Beta vs. Alpha:** A long-only strategy performing well during a massive secular bull market (e.g., Gold 2023-2026) is capturing Market Beta, not Alpha.
2. **The MT5 Cartesian Bug:** Appending to CSV files in MetaTrader 5 without clearing them causes overlapping Cartesian products when merging features and labels, leading to fake machine learning metrics.
3. **Purged Walk-Forward ML:** Using a strict *Time-Based Rolling Purged Cross-Validation* destroyed the strategy's edge, proving that the HMA indicator lacks predictive power out-of-sample in Forex.

## 🤝 Collaboration
Feel free to fork this repository. While the HMA chassis was discarded, the **XGBoost Meta-Labeling Pipeline** and **MQL5 Extractor architecture** are highly valuable and can be adapted to test Mean Reversion or Volatility-based structural inefficiencies.
