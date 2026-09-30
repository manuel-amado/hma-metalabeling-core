# 🔬 METHODOLOGY: Meta-Labeling Framework

## 1. The Core Architecture
This project utilizes the **Meta-Labeling** paradigm proposed by Marcos López de Prado in *Advances in Financial Machine Learning*. 
* **Model 1 (Primary Model):** A standard algorithmic chassis (MQL5 EA based on HMA crossovers) that identifies trading opportunities (Entries & Exits) and sizes positions using the Kelly Criterion.
* **Model 2 (Meta-Model):** A Machine Learning algorithm (XGBoost) that observes the market state at the time of Model 1's signal and predicts the probability of the trade being profitable. It acts as a binary filter (0 = Skip, 1 = Execute).

## 2. Feature Engineering
When Model 1 triggers a signal, the EA extracts the following macro and micro-structural features into a CSV:
1. `Keltner_Bandwidth_H4`
2. `ATR_Ratio_H1_D1`
3. `ADX_Value_H4`
4. `ADX_Slope_H4`
5. `Dist_EMA200_H4`
6. `Bollinger_Width_H1`
7. `Daily_Exhaustion`

## 3. Data Pipeline & Labeling
* Features are logged in MT5 (`XGBoost_Features_M1_Symbol.csv`).
* The final trade outcomes (Profits) are logged in a Deals file (`Pipeline_Extractor_M1_Symbol.csv`).
* Python merges these files on `Ticket_ID`.
* **Labeling:** Trades with Profit > 0 are labeled `1` (True Positive). Trades with Profit < 0 are labeled `0` (False Positive).

## 4. Time-Based Rolling Purged Cross-Validation
To prevent Data Leakage (lookahead bias) and Overfitting, we evaluate the XGBoost model using a strict continuous Walk-Forward approach:
1. **Train Window:** 24 months of data.
2. **Purge:** 7 days removed to prevent autocorrelation between train and test boundaries.
3. **Test Window (Out-Of-Sample):** 6 months of data.
4. **Embargo:** 5 days removed after the test set before the next training block begins.

This simulates realistic production deployment where an algorithm is re-trained periodically but only trades the unknown future.
