import os

file_path = r"c:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5\AlphaSweep_9999.mq5"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add InpMetaLabeling
content = content.replace(
    "input group \"== Salidas y Geometria Optimizables ==\"\ninput ENUM_EXIT_MODE InpExitMode = EXIT_IMMEDIATE;",
    "input group \"== Meta Labeling ==\"\ninput bool InpMetaLabeling = true; // Extraer dataset XGBoost\n\ninput group \"== Salidas y Geometria Optimizables ==\"\ninput ENUM_EXIT_MODE InpExitMode = EXIT_IMMEDIATE;"
)

# 2. Add variables to CSymbolManager
content = content.replace(
    "    datetime m_last_scaleout_attempt;\n\n    void CheckRealHistory() {",
    "    datetime m_last_scaleout_attempt;\n    \n    // -- Meta Labeling Dataset Variables --\n    double m_saved_features[58];\n    ulong m_active_ticket;\n    double m_saved_entry_price;\n    double m_saved_sl_dist;\n    int m_saved_signal_type;\n    datetime m_saved_open_time;\n    int m_csv_handle;\n\n    void CheckRealHistory() {"
)

# 3. Initialize variables in constructor
content = content.replace(
    "        bars_since_asian_sweep_high = 999;",
    "        bars_since_asian_sweep_high = 999;\n        m_active_ticket = 0;\n        m_csv_handle = INVALID_HANDLE;"
)

# 4. Open CSV in Init()
content = content.replace(
    "    bool Init(string sym) {\n        m_symbol = sym;\n        \n        if     (_Period == PERIOD_M15) m_macro_tf = PERIOD_H1;",
    "    bool Init(string sym) {\n        m_symbol = sym;\n        \n        if(InpMetaLabeling) {\n            string fname = \"Alpha_Sweep_Dataset_\" + m_symbol + \".csv\";\n            FileDelete(fname, FILE_COMMON);\n            m_csv_handle = FileOpen(fname, FILE_WRITE|FILE_CSV|FILE_ANSI|FILE_COMMON, \",\");\n            if(m_csv_handle != INVALID_HANDLE) {\n                FileWriteString(m_csv_handle, \"SignalType,ZScore,ATRNorm,RSI,RSIExt,BarsSinceExt,HMASlope,HMAAccelF,BreakoutF,TrendAlign,DistMacro,MacroADX,PBDur,PBDepth,SLDistATR,Spread,SLDistPts,Hour,SessionTime,H4TrendAlign,VolSpreadRatio,ATRRatioH,RSISlope10,SpreadImpact,HMADistEMA,BreakoutBody,Dow,HMAVel,HMAAccelV2,HMAJerk,EnergyAccum,BarsAsianSweep,BarsLocalSweep,BarsVolShock,DistAsianHigh,DistAsianLow,IsAsianSweep,TickVolZScore,SpreadExpRatio,CandleDom,RegConsist,RSIExhaust,MTFATRRatio,TrigRejTail,BollDev,CrossVol,VWMAZScore,FractDiff,TWAPZScore,BreakVel,ATRRatio47,BBWidth47,DistSynthH4,DistSynthD1,RibbonComp,SpecAlign,PriceMacroHMA,RibbonSpreadStd,ReturnPct,Label\\n\");\n                FileFlush(m_csv_handle);\n            }\n        }\n        \n        if     (_Period == PERIOD_M15) m_macro_tf = PERIOD_H1;"
)

# 5. Close CSV in Release()
content = content.replace(
    "    void Release() {\n        if(hma_entry_handle != INVALID_HANDLE) IndicatorRelease(hma_entry_handle);",
    "    void Release() {\n        if(m_csv_handle != INVALID_HANDLE) FileClose(m_csv_handle);\n        if(hma_entry_handle != INVALID_HANDLE) IndicatorRelease(hma_entry_handle);"
)

# 6. Save features after entry
content = content.replace(
    "                    else trade.Sell(lots, m_symbol, bid, sl, tp, comment);\n                    Print(\"ORDEN ENVIADA - Sym: \", m_symbol, \" Proba: \", entry_proba, \" Lotes: \", lots);\n                }\n            }",
    "                    else trade.Sell(lots, m_symbol, bid, sl, tp, comment);\n                    Print(\"ORDEN ENVIADA - Sym: \", m_symbol, \" Proba: \", entry_proba, \" Lotes: \", lots);\n                    \n                    if(InpMetaLabeling && trade.ResultRetcode() == TRADE_RETCODE_DONE) {\n                        ArrayCopy(m_saved_features, features);\n                        m_saved_signal_type = signalType;\n                        m_active_ticket = trade.ResultDeal();\n                        if(m_active_ticket == 0) m_active_ticket = trade.ResultOrder();\n                        for(int k = 0; k < PositionsTotal(); k++) {\n                            if(PositionGetSymbol(k) == m_symbol && PositionGetInteger(POSITION_MAGIC) == 777999) {\n                                m_active_ticket = PositionGetTicket(k);\n                                m_saved_entry_price = PositionGetDouble(POSITION_PRICE_OPEN);\n                                m_saved_sl_dist = MathAbs(m_saved_entry_price - sl);\n                                m_saved_open_time = (datetime)PositionGetInteger(POSITION_TIME);\n                                break;\n                            }\n                        }\n                    }\n                }\n            }"
)

# 7. Write to CSV on Exit
content = content.replace(
    "    void TickLevelManagement() {\n        // --- EVITAR SPAM DE 'MARKET CLOSED' EN FINES DE SEMANA ---",
    "    void TickLevelManagement() {\n        if(InpMetaLabeling && m_active_ticket != 0) {\n            if(!PositionSelectByTicket(m_active_ticket)) {\n                if(HistorySelectByPosition(m_active_ticket)) {\n                    int deals = HistoryDealsTotal();\n                    double profit = 0;\n                    double close_price = 0;\n                    for(int d = 0; d < deals; d++) {\n                        ulong deal_ticket = HistoryDealGetTicket(d);\n                        if(HistoryDealGetInteger(deal_ticket, DEAL_ENTRY) == DEAL_ENTRY_OUT || HistoryDealGetInteger(deal_ticket, DEAL_ENTRY) == DEAL_ENTRY_INOUT) {\n                            profit += HistoryDealGetDouble(deal_ticket, DEAL_PROFIT);\n                            close_price = HistoryDealGetDouble(deal_ticket, DEAL_PRICE);\n                        }\n                    }\n                    if (m_saved_entry_price > 0) {\n                        double return_pct = ((close_price - m_saved_entry_price) / m_saved_entry_price) * 100.0;\n                        if(m_saved_signal_type == 1) return_pct *= -1.0;\n                        int label = (profit > 0) ? 1 : 0;\n                        if(m_csv_handle != INVALID_HANDLE) {\n                            string row = \"\";\n                            for(int f = 0; f < 58; f++) row += StringFormat(\"%f,\", m_saved_features[f]);\n                            row += StringFormat(\"%f,%d\\n\", return_pct, label);\n                            FileWriteString(m_csv_handle, row);\n                            FileFlush(m_csv_handle);\n                        }\n                    }\n                }\n                m_active_ticket = 0;\n            }\n        }\n        \n        // --- EVITAR SPAM DE 'MARKET CLOSED' EN FINES DE SEMANA ---"
)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Patch applied successfully.")
