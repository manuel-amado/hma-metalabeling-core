import re

file_path = "mql5/HMA_ML_Orchestrator.mq5"

with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

# 1. Add TRIGGER_SPECTRUM_DECOMPRESSION to enum
content = re.sub(
    r'(TRIGGER_ASIAN_SWEEP\s*=\s*4.*?)\n};',
    r'\1,\n    TRIGGER_SPECTRUM_DECOMPRESSION = 5\n};',
    content,
    flags=re.DOTALL
)

# 2. Add ribbon handles to CHarvestManager
content = re.sub(
    r'(int fast_hma_exit_handle;)',
    r'\1\n    int ribbon_hma10, ribbon_hma21, ribbon_hma50, ribbon_hma100, ribbon_hma200;',
    content
)

# 3. Initialize ribbon handles in CHarvestManager constructor
content = re.sub(
    r'(rsi_handle\s*=\s*iRSI\(.*?;\n)',
    r'\1        ribbon_hma10 = iCustom(m_symbol, _Period, "HMA50", 10);\n        ribbon_hma21 = iCustom(m_symbol, _Period, "HMA50", 21);\n        ribbon_hma50 = iCustom(m_symbol, _Period, "HMA50", 50);\n        ribbon_hma100 = iCustom(m_symbol, _Period, "HMA50", 100);\n        ribbon_hma200 = iCustom(m_symbol, _Period, "HMA50", 200);\n',
    content
)

# 4. Check init
content = re.sub(
    r'(synth_adx_d1_handle == INVALID_HANDLE \|\| synth_ema50_d1_handle == INVALID_HANDLE)',
    r'\1 || ribbon_hma10 == INVALID_HANDLE || ribbon_hma21 == INVALID_HANDLE || ribbon_hma50 == INVALID_HANDLE || ribbon_hma100 == INVALID_HANDLE || ribbon_hma200 == INVALID_HANDLE',
    content
)

# 5. Release handles
content = re.sub(
    r'(IndicatorRelease\(rsi_handle\);)',
    r'\1\n        IndicatorRelease(ribbon_hma10);\n        IndicatorRelease(ribbon_hma21);\n        IndicatorRelease(ribbon_hma50);\n        IndicatorRelease(ribbon_hma100);\n        IndicatorRelease(ribbon_hma200);',
    content
)

# 6. Change effectiveTrigger to TRIGGER_SPECTRUM_DECOMPRESSION for all symbols
content = re.sub(
    r'(ENUM_TRIGGER_MODE effectiveTrigger = InpTriggerMode;.*?)\n        bool triggerBUY  = false;',
    r'ENUM_TRIGGER_MODE effectiveTrigger = TRIGGER_SPECTRUM_DECOMPRESSION;\n        bool triggerBUY  = false;',
    content,
    flags=re.DOTALL
)

# 7. Add Buffer copies and Spectrum Feature calculations right after hma buffer
buffer_logic = """        if(CopyBuffer(hma_handle, 0, 0, 150, hma) < 4) return;
        
        double hma10_buf[], hma21_buf[], hma50_buf[], hma100_buf[], hma200_buf[];
        ArraySetAsSeries(hma10_buf, true); ArraySetAsSeries(hma21_buf, true); ArraySetAsSeries(hma50_buf, true); ArraySetAsSeries(hma100_buf, true); ArraySetAsSeries(hma200_buf, true);
        if(CopyBuffer(ribbon_hma10, 0, 0, 3, hma10_buf) < 3) return;
        if(CopyBuffer(ribbon_hma21, 0, 0, 3, hma21_buf) < 3) return;
        if(CopyBuffer(ribbon_hma50, 0, 0, 3, hma50_buf) < 3) return;
        if(CopyBuffer(ribbon_hma100, 0, 0, 3, hma100_buf) < 3) return;
        if(CopyBuffer(ribbon_hma200, 0, 0, 3, hma200_buf) < 3) return;
"""
content = re.sub(
    r'        if\(CopyBuffer\(hma_handle, 0, 0, 150, hma\) < 4\) return;\n',
    buffer_logic,
    content
)

# 8. Add spectrum feature calculations before ManageAllPhysicalPositions
feature_logic = """
        // --- FASE 57: Feature Engineering Espectral ---
        double ribbon_compression_atr = 0;
        if(current_atr > 0) ribbon_compression_atr = MathAbs(hma10_buf[1] - hma200_buf[1]) / current_atr;
        
        double price_to_macro_hma_dist = 0;
        if(current_atr > 0) price_to_macro_hma_dist = (rates[1].close - hma200_buf[1]) / current_atr;
        
        // Spectrum Alignment Score (-1.0 a 1.0)
        double spectrum_alignment = 0;
        double align_score[3];
        for(int k=0; k<3; k++) {
            double sc = 0;
            if(hma10_buf[k] > hma21_buf[k]) sc += 0.25; else sc -= 0.25;
            if(hma21_buf[k] > hma50_buf[k]) sc += 0.25; else sc -= 0.25;
            if(hma50_buf[k] > hma100_buf[k]) sc += 0.25; else sc -= 0.25;
            if(hma100_buf[k] > hma200_buf[k]) sc += 0.25; else sc -= 0.25;
            align_score[k] = sc;
        }
        spectrum_alignment = align_score[1];
        
        // Ribbon Spread StdDev
        double mean_ribbon = (hma10_buf[1] + hma21_buf[1] + hma50_buf[1] + hma100_buf[1] + hma200_buf[1]) / 5.0;
        double variance = (MathPow(hma10_buf[1] - mean_ribbon, 2) + MathPow(hma21_buf[1] - mean_ribbon, 2) + MathPow(hma50_buf[1] - mean_ribbon, 2) + MathPow(hma100_buf[1] - mean_ribbon, 2) + MathPow(hma200_buf[1] - mean_ribbon, 2)) / 5.0;
        double ribbon_spread_stddev = 0;
        if(current_atr > 0) ribbon_spread_stddev = MathSqrt(variance) / current_atr;
        
"""
content = re.sub(
    r'(        double mtf_atr_ratio = \(atr_d1_buf\[0\] > 0\) \? \(current_atr / atr_d1_buf\[0\]\) : 0\.0;)',
    feature_logic + r'\1',
    content
)

# 9. Modify trigger logic for SPECTRUM_DECOMPRESSION
trigger_logic = """        } else if(effectiveTrigger == TRIGGER_SPECTRUM_DECOMPRESSION) {
            // Gatillo Fase 57: Descompresión Espectral (Breakout del Ribbon)
            double max_hma1 = MathMax(hma10_buf[1], MathMax(hma21_buf[1], MathMax(hma50_buf[1], MathMax(hma100_buf[1], hma200_buf[1]))));
            double min_hma1 = MathMin(hma10_buf[1], MathMin(hma21_buf[1], MathMin(hma50_buf[1], MathMin(hma100_buf[1], hma200_buf[1]))));
            
            bool break_up = (rates[1].close > max_hma1) && (rates[2].close <= MathMax(hma10_buf[2], MathMax(hma21_buf[2], MathMax(hma50_buf[2], MathMax(hma100_buf[2], hma200_buf[2])))));
            bool break_dn = (rates[1].close < min_hma1) && (rates[2].close >= MathMin(hma10_buf[2], MathMin(hma21_buf[2], MathMin(hma50_buf[2], MathMin(hma100_buf[2], hma200_buf[2])))));
            
            triggerBUY = break_up;
            triggerSELL = break_dn;
        }

        if(!(triggerBUY || triggerSELL)) {"""
content = re.sub(
    r'        } else if\(effectiveTrigger == TRIGGER_ASIAN_SWEEP\) \{.*?\n        }\n\n        if\(!\(triggerBUY \|\| triggerSELL\)\) \{',
    trigger_logic,
    content,
    flags=re.DOTALL
)

# 10. Pass new features to MarketSnapshot snap
snap_logic = """            snap.sl_distance_atr = (current_atr > 0) ? (real_slDist / current_atr) : 0.0;
            snap.ribbon_compression_atr = ribbon_compression_atr;
            snap.spectrum_alignment = spectrum_alignment;
            snap.price_to_macro_hma_dist = price_to_macro_hma_dist;
            snap.ribbon_spread_stddev = ribbon_spread_stddev;"""
content = re.sub(
    r'            snap\.sl_distance_atr = \(current_atr > 0\) \? \(real_slDist / current_atr\) : 0\.0;',
    snap_logic,
    content
)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patch applied.")
