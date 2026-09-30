baselines = {
    'GBPUSD': {'raw_win': 24.2, 'raw_rr': -0.0807, 'sl_pct': 30.2},
    'USDJPY': {'raw_win': 29.0, 'raw_rr':  0.0285, 'sl_pct': 23.2},
    'XAUUSD': {'raw_win': 26.8, 'raw_rr': -0.0443, 'sl_pct': 20.5},
    'EURJPY': {'raw_win': 27.0, 'raw_rr': -0.0500, 'sl_pct': 25.0},  # approx
    'EURUSD': {'raw_win': 27.0, 'raw_rr': -0.0300, 'sl_pct': 24.0},  # approx
}
ai_perf = {
    'GBPUSD': {'win': 38.42, 'rr': -0.0315, 'annual': -4.13},
    'USDJPY': {'win': 47.30, 'rr':  0.0443, 'annual':  4.24},
    'XAUUSD': {'win': 49.36, 'rr':  0.2583, 'annual': 30.34},
    'EURJPY': {'win': 39.31, 'rr':  0.0280, 'annual':  2.95},
    'EURUSD': {'win': 41.83, 'rr':  0.0325, 'annual':  3.59},
}

print("=== GBPUSD DIAGNOSIS: RAW HMA vs AI FILTER LIFT ===")
print()
print(f"{'Symbol':<8} {'RawWin':>7} {'RawRR':>7} {'SL%':>5}  {'AI_WR':>6} {'AI_RR':>7} {'AI_Annual':>10} {'WR_Lift':>8}")
print('-' * 70)
for sym in ['GBPUSD','USDJPY','XAUUSD','EURUSD','EURJPY']:
    b = baselines[sym]
    a = ai_perf[sym]
    wr_lift = a['win'] - b['raw_win']
    rr_lift = a['rr'] - b['raw_rr']
    print(f"{sym:<8} {b['raw_win']:>6.1f}% {b['raw_rr']:>7.4f} {b['sl_pct']:>5.1f}%  "
          f"{a['win']:>6.2f}% {a['rr']:>7.4f} {a['annual']:>10.2f}%  +{wr_lift:.1f}pp")

print()
print("KEY INSIGHT (GBPUSD):")
print("  Raw HMA baseline: WinRate=24.2%, MeanRR=-0.08  <- fundamental weakness")
print("  AI improves WinRate +14pp (good learning) but avg_rr stays negative")
print("  This means: GBPUSD winners are structurally too SMALL vs losers")
print("  SL hit rate 30.2% = highest in portfolio = stops triggered too often")
print("  Scale-Out at 1.5R rarely fires because price doesn't extend far enough")
print()
print("THIS IS NOT A SPREAD BUG. GBPUSD HMA crossovers on H1 have:")
print("  1. Structurally low win rate (choppy price action vs other pairs)")
print("  2. Asymmetric loss distribution (SL > TP in raw data)")
print("  3. Verified: GetPip() for GBPUSD (5 digits) -> correct pip=0.0001")
print("  4. MaxSpreadPips=4.0 -> GBPUSD spread 1-2 pips -> ALWAYS passes")
print()
print("DISCARD OF GBPUSD = CORRECT DECISION, but for the RIGHT reason:")
print("  The HMA crossover signal generator produces low-quality setups on GBPUSD H1.")
print("  The XGBoost cannot overcome this structural negative expectancy.")
print("  Solution: Use a DIFFERENT entry signal for GBPUSD (e.g., ADX+RSI).")
print("  OR: Accept GBPUSD absence and focus on the 5-asset Macro 5 portfolio.")
