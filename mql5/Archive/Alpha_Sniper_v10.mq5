//+------------------------------------------------------------------+
//|                                             Alpha_Sniper_v10.mq5 |
//|        Bot de Producción Institucional (Protocolo Omega V10)     |
//|        Autor: Manuel                                             |
//|        Configuración Monolítica Hardcoded Plug & Play            |
//+------------------------------------------------------------------+
#property strict
#property version "10.0"
#property description "Producción Monolítica V10: Riesgo Adaptativo por Equidad y Lote Dinámico (ATR SL)"

#include <Trade\Trade.mqh>
#include "HMA_FUNCTIONS.mqh"

enum ENUM_EXIT_MODE {
   EXIT_IMMEDIATE = 0,
   EXIT_DELAYED = 1,
   EXIT_TRAILING_ATR = 2
};

enum ENUM_DYNAMIC_RISK_MODE {
   RISK_MODE_FIXED           = 0, // 0: Riesgo Fijo / Escalado Nominal (InpRiskPerTrade)
   RISK_MODE_KELLY_FRACTION  = 1, // 1: Criterio de Kelly Fraccionado Asimétrico (InpKellyFractionPct)
   RISK_MODE_EQUITY_ADAPTIVE = 2  // 2: Riesgo Adaptativo por Salud de la Equidad (Expansión vs. Defensa)
};

CTrade trade;

// PROTOCOLO V9.3: DEFINICIÓN DE PARÁMETROS RÍGIDOS (R-MULTIPLES)
#define RR_BREAKEVEN         1.0
#define RR_SCALEOUT          1.5
#define RR_LOCK              0.5
#define TRAILING_ATR_RUNNER  2.5

//+------------------------------------------------------------------+
//| Parametros de Entrada                                            |
//+------------------------------------------------------------------+

// --- CONFIGURACIÓN INSTITUCIONAL V10 (HARDCODED PLUG & PLAY) ---
input group "== Portafolio Multi-Divisa =="
input string InpSymbols          = "XAUUSD,EURUSD,USDJPY,AUDUSD"; // PROTOCOLO V10: Flota 4 Activos Institucionales (XGBoost Nativo)

input group "== Estrategia HMA =="
input int    InpHMA_Entry_Period = 50;
input int    InpHMA_Exit_Period  = 20;
input int    InpMinBarsToHold    = 5;
input int    LookbackBars        = 7;
input double AntiNoiseATRPct     = 0.0;
input int    InpHysteresisBars   = 8; // Fase 87: Filtro Estructural Time-in-State

input group "== Contexto y Features =="
input int    RsiPeriod           = 14;
input int    RsiLookbackBars     = 15;
input int    RsiOversoldLevel    = 35;
input int    RsiOverboughtLevel  = 65;

input group "== Microestructura =="
input double MaxSpreadPips          = 4.0;  // Spread mÃƒÂ¡ximo Forex (Pips)
input double InpMaxSpreadPips_Metals = 120.0; // Spread mÃƒÂ¡ximo Metales (Puntos) [XAUUSD 2dig: 1pt=$0.01, spread=$1.20 max]
input int    InpMaxSlippagePoints   = 20;    // Deslizamiento maximo en puntos
input int    InpStartTradingHour    = 1;     // Hora de inicio (Evitar rollover)
input int    InpEndTradingHour      = 23;    // Hora de fin (Evitar rollover)
input int    InpDonchianPeriod      = 20;    // Filtro volatilidad Donchian

input group "== Meta Labeling =="
input bool InpMetaLabeling = false; // Extraer dataset XGBoost

input group "== Salidas y Geometria Optimizables =="
input ENUM_EXIT_MODE InpExitMode = EXIT_TRAILING_ATR;
input double InpTrailingATR = 3.3;
input double InpMinAngle = 0.0;

input group "== Inteligencia Artificial =="
input double InpCriticalZScoreExhaustion = 1.5; // Fase 36.5: Umbral de Agotamiento ParabÃƒÂ³lico
input double InpEntryThreshold           = 0.540; // XGBoost Entry Probability Threshold (Régimen 2020-2026)
input double InpExitThreshold            = 0.80; // (Obsoleto por HMA_Exit directa)

input group "== Gestion de Riesgo (Protocolo Omega V10) =="
input ENUM_DYNAMIC_RISK_MODE InpDynamicRiskMode = RISK_MODE_EQUITY_ADAPTIVE; // Modo de Riesgo Dinámico V10
input bool   InpUseCompoundInterest = false;   // FASE DE VALIDACIÓN: Riesgo Fijo en Dólares (Balance Inicial)
input double InpFixedBalance        = 100000.0;// Balance base si no se usa interés compuesto
input double InpRiskPerTrade        = 2.0;     // Riesgo Nominal Escalado (%) [V10 Óptimo: 2.0%]
input double InpKellyFractionPct    = 8.06;    // Kelly Fraccionado (%) [Quarter-Kelly Asimétrico]
input double InpDefenseRiskPct      = 1.0;     // Riesgo en Modo Defensa (%) [Reducción en Drawdown]
input double InpDDDefenseThreshold  = 3.0;     // Umbral DD para activar Modo Defensa (%)
input double InpMaxGlobalRisk       = 8.0;     // Riesgo global maximo (%) [Flota 4 activos x 2% max]
input int    InpMaxTradesPerSymbol  = 1;       // Limite de operaciones por Simbolo (FASE 64: Prohibido doblarse)
input int    InpMaxGlobalTrades     = 4;       // Limite Global de Cuenta [4 activos simultaneos max]
input double InpScaleOutRR          = 1.5;     // RR para tomar parciales (Alineacion Meta-Labeling IA)
input int    InpFastHMA_Exit_Period = 14;      // HMA Rápida para Salida anticipada

// --- PROTOCOLO OMEGA V10: CÁLCULO DE RIESGO ADAPTATIVO POR EQUIDAD ---
double g_peak_equity = 0.0;
double g_initial_balance = 0.0;

double GetEffectiveRiskPct() {
    double eq = AccountInfoDouble(ACCOUNT_EQUITY);
    if(eq > g_peak_equity) g_peak_equity = eq;
    if(g_peak_equity <= 0.0) g_peak_equity = eq;
    
    if(InpDynamicRiskMode == RISK_MODE_FIXED) {
        return InpRiskPerTrade;
    }
    else if(InpDynamicRiskMode == RISK_MODE_KELLY_FRACTION) {
        return InpKellyFractionPct;
    }
    else if(InpDynamicRiskMode == RISK_MODE_EQUITY_ADAPTIVE) {
        double current_dd_pct = 0.0;
        if(g_peak_equity > 0.0) current_dd_pct = (g_peak_equity - eq) / g_peak_equity * 100.0;
        if(current_dd_pct >= InpDDDefenseThreshold) {
            return InpDefenseRiskPct; // Modo Defensa (1.0%)
        }
        return InpRiskPerTrade; // Modo Expansión (2.0%)
    }
    return InpRiskPerTrade;
}

int g_VerticalBarrierBars; // Timeout Institucional

// --- FASE 64: GLOBAL THRESHOLD (SNIPER MODE) ---
double GetSymbolThreshold(string symbol_name) {
   return InpEntryThreshold;
}

double GetSymbolExitThreshold(string symbol_name) {
   return InpExitThreshold;
}

input group "== Filtros Macro / Cisnes Negros =="
input double InpMaxSignalBarATR  = 3.0;
input double InpMaxSLATR         = 5.0;
input double InpTPATR            = 4.5; // FASE 69: TP alineado a Python Triple Barrier
input bool   InpEnableEmbargo    = false; // FASE 62: Modo Sombra (Desactivado por defecto)

//+------------------------------------------------------------------+
//| Variables Globales Maestras                                      |
//+------------------------------------------------------------------+
long g_scaled_identifiers[]; // Scale-Out tracking: identifiers que ya han recibido Scale-Out

void AddScaledIdentifier(long identifier) {
    for(int s = 0; s < ArraySize(g_scaled_identifiers); s++) {
        if(g_scaled_identifiers[s] == identifier) return;
    }
    int sz = ArraySize(g_scaled_identifiers);
    ArrayResize(g_scaled_identifiers, sz + 1);
    g_scaled_identifiers[sz] = identifier;
}

bool IsPositionScaledOut(long identifier, double current_volume) {
    string comment = PositionGetString(POSITION_COMMENT);
    if(StringFind(comment, "ScaleOut") >= 0 || StringFind(comment, "Partial") >= 0 || StringFind(comment, "SO_1.5R") >= 0) {
        return true;
    }
    if(HistorySelectByPosition(identifier)) {
        int total_deals = HistoryDealsTotal();
        double initial_volume = 0.0;
        double out_volume = 0.0;
        for(int d = 0; d < total_deals; d++) {
            ulong deal_ticket = HistoryDealGetTicket(d);
            long deal_entry = HistoryDealGetInteger(deal_ticket, DEAL_ENTRY);
            if(deal_entry == DEAL_ENTRY_IN) {
                initial_volume += HistoryDealGetDouble(deal_ticket, DEAL_VOLUME);
            } else if(deal_entry == DEAL_ENTRY_OUT || deal_entry == DEAL_ENTRY_OUT_BY) {
                out_volume += HistoryDealGetDouble(deal_ticket, DEAL_VOLUME);
            }
        }
        if(out_volume > 0.00001 || (initial_volume > 0 && current_volume < initial_volume - 0.00001)) {
            return true;
        }
    }
    return false;
}

// PROTOCOLO STEP-LOCK ASIMÉTRICO (OPCIÓN A): Distancia de Riesgo 1.0R Inmutable
double GetInitialRiskDist(long identifier, double open_price, long type) {
    double initial_sl = 0.0;
    if(HistorySelectByPosition(identifier)) {
        int total_deals = HistoryDealsTotal();
        for(int d = 0; d < total_deals; d++) {
            ulong deal_ticket = HistoryDealGetTicket(d);
            if(HistoryDealGetInteger(deal_ticket, DEAL_ENTRY) == DEAL_ENTRY_IN) {
                initial_sl = HistoryDealGetDouble(deal_ticket, DEAL_SL);
                if(initial_sl > 0) break;
            }
        }
    }
    double dist = 0.0;
    if(initial_sl > 0) {
        dist = MathAbs(open_price - initial_sl);
    }
    if(dist <= 0.00001) {
        // Fallback robusto si DEAL_SL no estuvo presente en el deal inicial
        double point = SymbolInfoDouble(PositionGetString(POSITION_SYMBOL), SYMBOL_POINT);
        dist = point * 100.0 * InpMaxSLATR;
    }
    return dist;
}


#include "XGBoost_Model_XAUUSD_M15.mqh"
#include "XGBoost_Model_EURUSD_M15.mqh"
#include "XGBoost_Model_XAGUSD_M15.mqh"
#include "XGBoost_Model_GBPJPY_M15.mqh"
#include "XGBoost_Model_USDJPY_M15.mqh"
#include "XGBoost_Model_AUDUSD_M15.mqh"
#include "XGBoost_Model_AUDCAD_M15.mqh"

//+------------------------------------------------------------------+
//| Calcular Riesgo Flotante Real (Ignorando Break-Even)             |
//+------------------------------------------------------------------+
double CalculateRealFloatingRisk() {
    double risk = 0.0;
    int total = PositionsTotal();
    for(int i = 0; i < total; i++) {
        ulong ticket = PositionGetTicket(i);
        if(PositionGetInteger(POSITION_MAGIC) == 777999) {
            double open_price = PositionGetDouble(POSITION_PRICE_OPEN);
            double sl = PositionGetDouble(POSITION_SL);
            long type = PositionGetInteger(POSITION_TYPE);
            
            if(type == POSITION_TYPE_BUY) {
                if(sl < open_price) risk += GetEffectiveRiskPct();
            } else if(type == POSITION_TYPE_SELL) {
                if(sl > open_price || sl == 0.0) risk += GetEffectiveRiskPct();
            }
        }
    }
    return risk;
}

//+------------------------------------------------------------------+
//| CLASE GESTORA DE SÃƒÂMBOLO (OOP Multi-Activo)                      |
//+------------------------------------------------------------------+
class CSymbolManager
{
private:
    string m_symbol;
    ENUM_TIMEFRAMES m_macro_tf;
    
    int hma_entry_handle, hma_exit_handle, rsi_handle, atr_handle;
    int ema50_handle, ema200_handle, sma20_handle, std_dev_handle;
    int ema50_h4_handle, atr200_handle, atr_d1_handle, adx_handle;
    int ema20_h4_handle, ema50_d1_handle;
    int fast_hma_exit_handle;
    int ribbon_hma10, ribbon_hma21, ribbon_hma50, ribbon_hma100, ribbon_hma200;
    
    datetime lastBarTime;
    datetime lastExitBarTime;
    
    int bars_since_asian_sweep_high;
    int bars_since_asian_sweep_low;
    int bars_since_local_sweep_high;
    int bars_since_local_sweep_low;
    int bars_since_vol_shock_bull;
    int bars_since_vol_shock_bear;

    // --- FASE 38: SHADOW MODE STATE ---
    int m_consecutive_losses;
    bool m_embargo_active;
    bool m_virtual_active;
    long m_virtual_type;
    double m_virtual_open;
    double m_virtual_sl;
    double m_virtual_target;
    datetime m_last_history_check;
    ulong m_last_processed_deal;
    datetime m_last_scaleout_attempt;
    
    // -- Meta Labeling Dataset Variables --
    double m_saved_features[20];
    ulong m_active_ticket;
    double m_saved_entry_price;
    double m_saved_sl_dist;
    int m_saved_signal_type;
    datetime m_saved_open_time;
    int m_csv_handle;

    void CheckRealHistory() {
        if(m_embargo_active) return; // Si ya hay embargo, el historial real queda pausado
        
        datetime now = TimeCurrent();
        if(now - m_last_history_check < 10) return; // Evaluar cada 10 seg
        m_last_history_check = now;

        HistorySelect(0, now);
        int total = HistoryDealsTotal();

        for(int i = 0; i < total; i++) {
            ulong ticket = HistoryDealGetTicket(i);
            if(ticket <= m_last_processed_deal) continue;
            
            if(HistoryDealGetInteger(ticket, DEAL_MAGIC) == 777999 &&
               HistoryDealGetString(ticket, DEAL_SYMBOL) == m_symbol &&
               HistoryDealGetInteger(ticket, DEAL_ENTRY) == DEAL_ENTRY_OUT) 
            {
                double profit = HistoryDealGetDouble(ticket, DEAL_PROFIT);
                double commission = HistoryDealGetDouble(ticket, DEAL_COMMISSION);
                double swap = HistoryDealGetDouble(ticket, DEAL_SWAP);
                double net_profit = profit + commission + swap;
                
                if(net_profit < 0.0) {
                    m_consecutive_losses++;
                    if(m_consecutive_losses >= 3 && InpEnableEmbargo) {
                        m_embargo_active = true;
                        Print("[EMBARGO ACTIVADO] 3 PÃƒÂ©rdidas consecutivas en ", m_symbol, ". Pasando a Modo Sombra.");
                    }
                } else {
                    m_consecutive_losses = 0; // Se rompiÃƒÂ³ la racha perdedora
                }
            }
            // Update last processed deal so we never process it again
            if (ticket > m_last_processed_deal) m_last_processed_deal = ticket;
        }
    }

    // PROTOCOLO V9.2: 1. MAPEO Y RECONEXIÓN DE POSICIONES HUÉRFANAS (STATE RECOVERY)
    void RecoverState() {
        int total = PositionsTotal();
        for(int i = total - 1; i >= 0; i--) {
            ulong ticket = PositionGetTicket(i);
            if(PositionGetString(POSITION_SYMBOL) == m_symbol && PositionGetInteger(POSITION_MAGIC) == 777999) {
                m_active_ticket = ticket;
                m_saved_entry_price = PositionGetDouble(POSITION_PRICE_OPEN);
                m_saved_open_time = (datetime)PositionGetInteger(POSITION_TIME);
                long type = PositionGetInteger(POSITION_TYPE);
                m_saved_signal_type = (type == POSITION_TYPE_BUY) ? 1 : 0;
                
                long identifier = PositionGetInteger(POSITION_IDENTIFIER);
                if(IsPositionScaledOut(identifier, PositionGetDouble(POSITION_VOLUME))) {
                    AddScaledIdentifier(identifier);
                }
                break;
            }
        }
    }

    // PROTOCOLO V9.2: 4. RECALIBRACIÓN RETROACTIVA DE FEATURES XGBOOST (CRASH-PROOF)
    void RecalibrateStateHistory() {
        MqlRates rates[];
        ArraySetAsSeries(rates, true);
        int copied = CopyRates(m_symbol, _Period, 0, 150, rates);
        if(copied < 125) {
            Print("[V9.2 CRASH-PROOF] No hay suficiente historial para recalibrar ", m_symbol, " (velas: ", copied, ").");
            return;
        }
        
        bars_since_vol_shock_bull = 100;
        bars_since_vol_shock_bear = 100;
        bars_since_local_sweep_high = 100;
        bars_since_local_sweep_low = 100;
        
        for(int idx = 100; idx >= 1; idx--) {
            bars_since_vol_shock_bull++;
            bars_since_vol_shock_bear++;
            bars_since_local_sweep_high++;
            bars_since_local_sweep_low++;
            
            double sum_vol = 0;
            for(int k = 1; k < 21; k++) sum_vol += (double)rates[idx + k].tick_volume;
            double mean_vol = sum_vol / 20.0;
            double sq_diff_sum = 0;
            for(int k = 1; k < 21; k++) sq_diff_sum += MathPow((double)rates[idx + k].tick_volume - mean_vol, 2);
            double std_vol = MathSqrt(sq_diff_sum / 20.0);
            double tick_vol_zscore = 0.0;
            if(std_vol > 0) tick_vol_zscore = ((double)rates[idx].tick_volume - mean_vol) / std_vol;
            
            bool is_bull = (rates[idx].close > rates[idx].open);
            bool is_bear = (rates[idx].close < rates[idx].open);
            if(tick_vol_zscore > 0.75 && is_bull) bars_since_vol_shock_bull = 0;
            if(tick_vol_zscore > 0.75 && is_bear) bars_since_vol_shock_bear = 0;
            
            double loc_high = -1.0; double loc_low = 1e9;
            for(int k = 1; k < 21; k++) {
                if(rates[idx + k].high > loc_high) loc_high = rates[idx + k].high;
                if(rates[idx + k].low < loc_low)   loc_low  = rates[idx + k].low;
            }
            if(rates[idx].high > loc_high && rates[idx].close <= loc_high && rates[idx].open <= loc_high) bars_since_local_sweep_high = 0;
            if(rates[idx].low < loc_low && rates[idx].close >= loc_low && rates[idx].open >= loc_low) bars_since_local_sweep_low = 0;
        }
        Print("[V9.2 CRASH-PROOF] Estado de Features retrocalibrado en ", m_symbol, " -> ShockBull:", bars_since_vol_shock_bull, " ShockBear:", bars_since_vol_shock_bear);
    }

    double GetPip() {
        double point = SymbolInfoDouble(m_symbol, SYMBOL_POINT);
        int digits = (int)SymbolInfoInteger(m_symbol, SYMBOL_DIGITS);
        if(digits == 5 || digits == 3) return point * 10.0;
        return point;
    }

    double CalcDynamicLotSize(int signalType, double open_price, double sl_price) {
        double base_capital = InpUseCompoundInterest ? AccountInfoDouble(ACCOUNT_EQUITY) : g_initial_balance;
        if(base_capital <= 0.0) base_capital = InpFixedBalance;
        
        double effective_risk_pct = GetEffectiveRiskPct();
        double risk_amount = base_capital * (effective_risk_pct / 100.0);
        
        ENUM_ORDER_TYPE order_type = (signalType == 0) ? ORDER_TYPE_BUY : ORDER_TYPE_SELL;
        double expected_loss = 0.0;
        
        // FASE 68: Proteccion absoluta contra TickValue erroneos en Metales.
        if(!OrderCalcProfit(order_type, m_symbol, 1.0, open_price, sl_price, expected_loss)) {
            Print("ERROR: OrderCalcProfit fallo en ", m_symbol, " Error: ", GetLastError());
            return 0.0;
        }
        
        double risk_per_lot = MathAbs(expected_loss);
        if(risk_per_lot <= 0) return 0.0;
        
        double lots = risk_amount / risk_per_lot;
        
        double min_lot = SymbolInfoDouble(m_symbol, SYMBOL_VOLUME_MIN);
        double max_lot = SymbolInfoDouble(m_symbol, SYMBOL_VOLUME_MAX);
        double step_lot = SymbolInfoDouble(m_symbol, SYMBOL_VOLUME_STEP);
        
        lots = MathFloor(lots / step_lot) * step_lot;
        if(lots < min_lot) return 0.0;
        if(lots > max_lot) lots = max_lot;
        
        return lots;
    }

public:
    void TickLevelManagement() {
        if(InpMetaLabeling && m_active_ticket != 0) {
            if(!PositionSelectByTicket(m_active_ticket)) {
                if(HistorySelectByPosition(m_active_ticket)) {
                    int deals = HistoryDealsTotal();
                    double profit = 0;
                    double close_price = 0;
                    for(int d = 0; d < deals; d++) {
                        ulong deal_ticket = HistoryDealGetTicket(d);
                        if(HistoryDealGetInteger(deal_ticket, DEAL_ENTRY) == DEAL_ENTRY_OUT || HistoryDealGetInteger(deal_ticket, DEAL_ENTRY) == DEAL_ENTRY_INOUT) {
                            profit += HistoryDealGetDouble(deal_ticket, DEAL_PROFIT);
                            close_price = HistoryDealGetDouble(deal_ticket, DEAL_PRICE);
                        }
                    }
                    if (m_saved_entry_price > 0) {
                        double return_pct = ((close_price - m_saved_entry_price) / m_saved_entry_price) * 100.0;
                        if(m_saved_signal_type == 1) return_pct *= -1.0;
                        int label = (profit > 0) ? 1 : 0;
                        if(m_csv_handle != INVALID_HANDLE) {
                            string row = "";
                            for(int f = 0; f < 19; f++) row += StringFormat("%f,", m_saved_features[f]);
                            row += StringFormat("%f,%d\n", return_pct, label);
                            FileWriteString(m_csv_handle, row);
                            FileFlush(m_csv_handle);
                        }
                    }
                }
                m_active_ticket = 0;
            }
        }
        
        // --- EVITAR SPAM DE 'MARKET CLOSED' EN FINES DE SEMANA ---
        MqlDateTime dt;
        TimeToStruct(TimeCurrent(), dt);
        if(dt.day_of_week == 6) return; // Sabado cerrado
        if(dt.day_of_week == 0 && dt.hour < 21) return; // Domingo antes de apertura
        if(dt.day_of_week == 5 && dt.hour >= 23) return; // Viernes despues de cierre
        
        // --- SHADOW MODE TICK MANAGEMENT ---
        if(m_embargo_active && m_virtual_active) {
            double ask = SymbolInfoDouble(m_symbol, SYMBOL_ASK);
            double bid = SymbolInfoDouble(m_symbol, SYMBOL_BID);
            
            bool virtual_won = false;
            bool virtual_lost = false;
            
            if(m_virtual_type == POSITION_TYPE_BUY) {
                if(bid <= m_virtual_sl) virtual_lost = true;
                else if(bid >= m_virtual_target) virtual_won = true;
            } else if(m_virtual_type == POSITION_TYPE_SELL) {
                if(ask >= m_virtual_sl) virtual_lost = true;
                else if(ask <= m_virtual_target) virtual_won = true;
            }
            
            if(virtual_lost) {
                Print("[TRADE FANTASMA PERDIDO] Modelo en racha perdedora para ", m_symbol, ". Embargo continÃƒÂºa.");
                m_virtual_active = false;
            } else if(virtual_won) {
                Print("[EMBARGO LEVANTADO] Trade Fantasma alcanzÃƒÂ³ +1.5R en ", m_symbol, ". Reactivando Fuego Real.");
                m_virtual_active = false;
                m_embargo_active = false;
                m_consecutive_losses = 0;
            }
        }
        // ------------------------------------
        
        // --- GESTIÃƒâ€œN TÃƒÂCTICA: SCALE-OUT 1.5R Y BREAKEVEN ---

        double pip = GetPip();
        double vol_min  = SymbolInfoDouble(m_symbol, SYMBOL_VOLUME_MIN);
        double vol_step = SymbolInfoDouble(m_symbol, SYMBOL_VOLUME_STEP);
        
        int total = PositionsTotal();
        for(int i = total - 1; i >= 0; i--) {
            ulong ticket = PositionGetTicket(i);
            if(PositionGetString(POSITION_SYMBOL) == m_symbol && PositionGetInteger(POSITION_MAGIC) == 777999) {
                long identifier     = PositionGetInteger(POSITION_IDENTIFIER);
                double open_price   = PositionGetDouble(POSITION_PRICE_OPEN);
                double current_price = PositionGetDouble(POSITION_PRICE_CURRENT);
                double sl           = PositionGetDouble(POSITION_SL);
                double tp           = PositionGetDouble(POSITION_TP);
                double current_lots = PositionGetDouble(POSITION_VOLUME);
                long type = PositionGetInteger(POSITION_TYPE);
                
                double dist_sl_pips = 0.0;
                double floating_rr  = 0.0;
                
                double initial_r_dist = GetInitialRiskDist(identifier, open_price, type);
                if(type == POSITION_TYPE_BUY) {
                    dist_sl_pips = (current_price - sl) / pip;
                    if(initial_r_dist > 0) floating_rr = (current_price - open_price) / initial_r_dist;
                } else {
                    dist_sl_pips = (sl - current_price) / pip;
                    if(initial_r_dist > 0) floating_rr = (open_price - current_price) / initial_r_dist;
                }
                
                bool already_scaled = IsPositionScaledOut(identifier, current_lots);
                for(int s = 0; s < ArraySize(g_scaled_identifiers); s++) {
                    if(g_scaled_identifiers[s] == identifier) { already_scaled = true; } // Removed break to follow rules
                }
                
                // HIGH FREQUENCY TICK EVALUATION: Scale-Out intra-bar
                if(!already_scaled && floating_rr >= RR_SCALEOUT) {
                    if (TimeCurrent() - m_last_scaleout_attempt >= 60) { // Cooldown de 60s si falla
                        double close_lots = MathFloor((current_lots * 0.5) / vol_step) * vol_step;
                        if(current_lots <= vol_min) {
                            Print("[SCALE-OUT ABORTED] Lote actual <= minimo del broker. Esperando cierre total. Ticket: ", ticket);
                        } else if(close_lots < vol_min) {
                            if(!trade.PositionClose(ticket)) {
                                m_last_scaleout_attempt = TimeCurrent();
                            } else {
                                Print("[SCALE-OUT] Lote residual < minimo. Cierre total. Ticket: ", ticket);
                            }
                        } else {
                            if(trade.PositionClosePartial(ticket, close_lots)) {
                                AddScaledIdentifier(identifier);
                                Print("[SCALE-OUT] 50% cerrado a ", close_lots, " lots. Identifier: ", identifier);
                                already_scaled = true; 
                            } else {
                                m_last_scaleout_attempt = TimeCurrent();
                            }
                        }
                    }
                }
                
                // --- PROTOCOLO V9.3 STEP-LOCK ASIMÉTRICO ---
                // FASE 2: En +1.5R (RR_SCALEOUT), asegurar +0.5R (RR_LOCK) en el lote residual
                if(floating_rr >= RR_SCALEOUT && initial_r_dist > 0) {
                    double target_sl = (type == POSITION_TYPE_BUY) ? (open_price + RR_LOCK * initial_r_dist) : (open_price - RR_LOCK * initial_r_dist);
                    if(type == POSITION_TYPE_BUY && sl < target_sl - 0.00001) {
                        trade.PositionModify(ticket, target_sl, tp);
                        Print("[V9.3 STEP-LOCK FASE 2] Beneficio asegurado +0.5R (RR_LOCK) en Ticket: ", ticket, " SL: ", target_sl);
                    } else if(type == POSITION_TYPE_SELL && (sl > target_sl + 0.00001 || sl == 0)) {
                        trade.PositionModify(ticket, target_sl, tp);
                        Print("[V9.3 STEP-LOCK FASE 2] Beneficio asegurado +0.5R (RR_LOCK) en Ticket: ", ticket, " SL: ", target_sl);
                    }
                }
                // FASE 1: En +1.0R (RR_BREAKEVEN), asegurar Breakeven + Comisión (+0.05R / 2 pips)
                else if(floating_rr >= RR_BREAKEVEN && initial_r_dist > 0) {
                    double target_sl = (type == POSITION_TYPE_BUY) ? (open_price + pip * 2.0) : (open_price - pip * 2.0);
                    if(type == POSITION_TYPE_BUY && sl < target_sl - 0.00001) {
                        trade.PositionModify(ticket, target_sl, tp);
                        Print("[V9.3 STEP-LOCK FASE 1] Breakeven Seguro en Ticket: ", ticket, " SL: ", target_sl);
                    } else if(type == POSITION_TYPE_SELL && (sl > target_sl + 0.00001 || sl == 0)) {
                        trade.PositionModify(ticket, target_sl, tp);
                        Print("[V9.3 STEP-LOCK FASE 1] Breakeven Seguro en Ticket: ", ticket, " SL: ", target_sl);
                    }
                }
                
            }
        }
    }

    string GetCleanSymbol() {
        string clean = m_symbol;
        int dot_idx = StringFind(clean, ".");
        if(dot_idx != -1) {
            clean = StringSubstr(clean, 0, dot_idx);
        }
        return clean;
    }

private:
    void ManageOpenTrades(double current_atr, double spread, double close_1, double close_2,
                          double hma_1, double macro_adx,
                          double fast_hma_close_1, double fast_hma_close_2) {
        // --- PROTOCOLO ALPHA FASE 31: AISLACION CLINICA (Exit model reactivado) ---
        // -----------------------------------------------------------
        datetime currentBarTime = iTime(m_symbol, _Period, 0);
        bool is_new_bar = (currentBarTime != lastExitBarTime);
        
        if(!is_new_bar) return;
        
        double hma_exit[2], rsi_buf[1], stddev[1], sma20[1], atr_d1_buf[1];
        MqlRates rates[];
        ArraySetAsSeries(rates, true);
        
        if(CopyBuffer(hma_exit_handle, 0, 0, 2, hma_exit) < 2) return;
        if(CopyBuffer(rsi_handle, 0, 0, 1, rsi_buf) < 1) return;
        if(CopyRates(m_symbol, _Period, 0, 2, rates) < 2) return;
        
        CopyBuffer(std_dev_handle, 0, 0, 1, stddev);
        CopyBuffer(sma20_handle, 0, 0, 1, sma20);
        CopyBuffer(atr_d1_handle, 0, 0, 1, atr_d1_buf);
        
        double mtf_atr_ratio = 0.0;
        if (atr_d1_buf[0] > 0) mtf_atr_ratio = current_atr / atr_d1_buf[0];
        
        double bollinger_dev = 0.0;
        if(stddev[0] > 0) bollinger_dev = (rates[0].close - sma20[0]) / stddev[0];
        
        double exit_hma_velocity = 0.0;
        if(current_atr > 0) exit_hma_velocity = (hma_exit[0] - hma_exit[1]) / current_atr;
        double exit_hma_accel = 0.0;
        
        double pip = GetPip();
        
        int total = PositionsTotal();
        for(int i = total - 1; i >= 0; i--) {
            ulong ticket = PositionGetTicket(i);
            if(PositionGetString(POSITION_SYMBOL) == m_symbol && PositionGetInteger(POSITION_MAGIC) == 777999) {
                long pos_time = PositionGetInteger(POSITION_TIME);
                int bars_in_trade = Bars(m_symbol, _Period, (datetime)pos_time, currentBarTime);
                long type = PositionGetInteger(POSITION_TYPE);
                
                bool is_eurusd_gbpusd = (m_symbol == "EURUSD" || m_symbol == "EURUSD+" || m_symbol == "EURUSDm" ||
                                         m_symbol == "GBPUSD" || m_symbol == "GBPUSD+" || m_symbol == "GBPUSDm");
                bool hard_close = false;
                if(InpExitMode == EXIT_IMMEDIATE) {
                    if(type == POSITION_TYPE_BUY && hma_exit[0] < hma_exit[1]) hard_close = true;
                    if(type == POSITION_TYPE_SELL && hma_exit[0] > hma_exit[1]) hard_close = true;
                } else if(InpExitMode == EXIT_DELAYED) {
                    if(type == POSITION_TYPE_BUY && hma_exit[0] < hma_exit[1] && hma_exit[1] < hma_exit[2]) hard_close = true;
                    if(type == POSITION_TYPE_SELL && hma_exit[0] > hma_exit[1] && hma_exit[1] > hma_exit[2]) hard_close = true;
                } else if(InpExitMode == EXIT_TRAILING_ATR) {
                    double atr_vals[1]; CopyBuffer(atr_handle, 0, 0, 1, atr_vals); double current_atr = atr_vals[0];
                    double open_price_m = PositionGetDouble(POSITION_PRICE_OPEN);
                    long identifier_m = PositionGetInteger(POSITION_IDENTIFIER);
                    double initial_r_dist_m = GetInitialRiskDist(identifier_m, open_price_m, type);
                    double current_price_m = PositionGetDouble(POSITION_PRICE_CURRENT);
                    double floating_rr_m = 0.0;
                    if(initial_r_dist_m > 0) {
                        floating_rr_m = (type == POSITION_TYPE_BUY) ? (current_price_m - open_price_m) / initial_r_dist_m : (open_price_m - current_price_m) / initial_r_dist_m;
                    }
                    // PROTOCOLO V9.3 STEP-LOCK ASIMÉTRICO (FASE 3): Trailing Dinámico del "Runner"
                    bool is_runner = IsPositionScaledOut(identifier_m, PositionGetDouble(POSITION_VOLUME));
                    for(int s = 0; s < ArraySize(g_scaled_identifiers); s++) {
                        if(g_scaled_identifiers[s] == identifier_m) is_runner = true;
                    }
                    double effective_atr_mult = is_runner ? TRAILING_ATR_RUNNER : InpTrailingATR;
                    double sl_dist = effective_atr_mult * current_atr;
                    double pip = GetPip();
                    
                    if(type == POSITION_TYPE_BUY) {
                        double current_price = PositionGetDouble(POSITION_PRICE_CURRENT);
                        double sl = PositionGetDouble(POSITION_SL);
                        double tp = PositionGetDouble(POSITION_TP);
                        if(current_price - sl_dist > sl + pip) {
                            trade.PositionModify(ticket, current_price - sl_dist, tp);
                        }
                    } else if(type == POSITION_TYPE_SELL) {
                        double current_price = PositionGetDouble(POSITION_PRICE_CURRENT);
                        double sl = PositionGetDouble(POSITION_SL);
                        double tp = PositionGetDouble(POSITION_TP);
                        if(current_price + sl_dist < sl - pip || sl == 0) {
                            trade.PositionModify(ticket, current_price + sl_dist, tp);
                        }
                    }
                }
                
                if(hard_close) {
                    trade.PositionClose(ticket);
                    Print("[HARD EXIT] FISICA ESTRUCTURAL ROTA. ABORTANDO. Ticket: ", ticket);
                } else if(false && bars_in_trade >= g_VerticalBarrierBars) {
                    trade.PositionClose(ticket);
                    Print("[TIMEOUT] Barrera vertical superada. Ticket: ", ticket);
                } else if(bars_in_trade >= InpMinBarsToHold) {
                    double open_price   = PositionGetDouble(POSITION_PRICE_OPEN);
                    double current_price = PositionGetDouble(POSITION_PRICE_CURRENT);
                    double sl           = PositionGetDouble(POSITION_SL);
                    
                    double floating_rr  = 0.0;
                    if(type == POSITION_TYPE_BUY) {
                        if(open_price - sl > 0) floating_rr = (current_price - open_price) / (open_price - sl);
                    } else {
                        if(sl - open_price > 0) floating_rr = (open_price - current_price) / (sl - open_price);
                    }
                    
                    double current_stretch = 0.0;
                    if(current_atr > 0) current_stretch = MathAbs(current_price - fast_hma_close_1) / current_atr;
                    UpdatePeakStretch(ticket, current_stretch);
                    double peak_stretch = GetPeakStretch(ticket);
                    double elastic_pct = 0.0;
                    if(peak_stretch > 0) elastic_pct = (peak_stretch - current_stretch) / peak_stretch;
                    
                    double spread_pips = SymbolInfoInteger(m_symbol, SYMBOL_SPREAD) * _Point / pip;
                    double sl_pips = MathAbs(open_price - sl) / pip;
                    double spread_impact_exit = (sl_pips > 0) ? (spread_pips / sl_pips) : 0.0;
                    
                    double trigger_rejection_tail = 0.0;
                    double cdl_range = rates[1].high - rates[1].low;
                    if(cdl_range > 0) {
                        if(type == POSITION_TYPE_BUY) {
                            trigger_rejection_tail = (MathMin(rates[1].open, rates[1].close) - rates[1].low) / cdl_range;
                        } else {
                            trigger_rejection_tail = (rates[1].high - MathMax(rates[1].open, rates[1].close)) / cdl_range;
                        }
                    }
                    
                    double fast_hma_buf[], hma_exit_buf[], rsi_eval_buf[];
                    ArraySetAsSeries(fast_hma_buf,  true);
                    ArraySetAsSeries(hma_exit_buf,  true);
                    ArraySetAsSeries(rsi_eval_buf,  true);
                    
                    if(CopyBuffer(hma_entry_handle,      0, 0, 4, fast_hma_buf)  < 4) return;
                    if(CopyBuffer(hma_exit_handle, 0, 0, 4, hma_exit_buf)  < 4) return;
                    if(CopyBuffer(rsi_handle,      0, 0, 3, rsi_eval_buf)  < 3) return;
                    
                    int is_trigger_fast   = 0;
                    int is_trigger_slow   = 0;
                    int is_trigger_rsi    = 0;
                    int is_trigger_profit = 0;
                    int is_trigger_fast_hma_cross = 0;
                    
                    if(type == POSITION_TYPE_BUY) {
                        if(fast_hma_buf[1] < fast_hma_buf[2] && fast_hma_buf[2] >= fast_hma_buf[3]) is_trigger_fast = 1;
                        if(hma_exit_buf[1] < hma_exit_buf[2] && hma_exit_buf[2] >= hma_exit_buf[3]) is_trigger_slow = 1;
                        if(rsi_eval_buf[1] < 50.0 && rsi_eval_buf[2] >= 50.0) is_trigger_rsi = 1;
                        if(fast_hma_close_2 > 0 && close_1 < fast_hma_close_1 && close_2 >= fast_hma_close_2)
                            is_trigger_fast_hma_cross = 1;
                    } else if(type == POSITION_TYPE_SELL) {
                        if(fast_hma_buf[1] > fast_hma_buf[2] && fast_hma_buf[2] <= fast_hma_buf[3]) is_trigger_fast = 1;
                        if(hma_exit_buf[1] > hma_exit_buf[2] && hma_exit_buf[2] <= hma_exit_buf[3]) is_trigger_slow = 1;
                        if(rsi_eval_buf[1] > 50.0 && rsi_eval_buf[2] <= 50.0) is_trigger_rsi = 1;
                        if(fast_hma_close_2 > 0 && close_1 > fast_hma_close_1 && close_2 <= fast_hma_close_2)
                            is_trigger_fast_hma_cross = 1;
                    }
                    
                    if(bars_in_trade > 0 && bars_in_trade % 5 == 0 && floating_rr >= 1.0) {
                        is_trigger_profit = 1;
                    }
                    
                    // Exit managed by hard_close only (Phase 72)
                }
            }
        }
        CleanTicketStates();
        lastExitBarTime = currentBarTime;
    }

public:
    CSymbolManager() {
        lastBarTime = 0;
        lastExitBarTime = 0;
        bars_since_asian_sweep_high = 999;
        m_active_ticket = 0;
        m_csv_handle = INVALID_HANDLE;
        bars_since_asian_sweep_low = 999;
        bars_since_local_sweep_high = 999;
        bars_since_local_sweep_low = 999;
        bars_since_vol_shock_bull = 999;
        bars_since_vol_shock_bear = 999;
        
        m_consecutive_losses = 0;
        m_embargo_active = false;
        m_virtual_active = false;
        m_virtual_type = 0;
        m_virtual_open = 0;
        m_virtual_sl = 0;
        m_virtual_target = 0;
        m_last_history_check = 0;
        m_last_processed_deal = 0;
        
        hma_entry_handle = INVALID_HANDLE;
        hma_exit_handle = INVALID_HANDLE;
        rsi_handle = INVALID_HANDLE;
        atr_handle = INVALID_HANDLE;
        ema50_handle = INVALID_HANDLE;
        ema200_handle = INVALID_HANDLE;
        sma20_handle = INVALID_HANDLE;
        std_dev_handle = INVALID_HANDLE;
        ema20_h4_handle = INVALID_HANDLE;
        ema50_d1_handle = INVALID_HANDLE;
        atr200_handle = INVALID_HANDLE;
        atr_d1_handle = INVALID_HANDLE;
        adx_handle = INVALID_HANDLE;
        fast_hma_exit_handle = INVALID_HANDLE;
        ribbon_hma10 = INVALID_HANDLE;
        ribbon_hma21 = INVALID_HANDLE;
        ribbon_hma50 = INVALID_HANDLE;
        ribbon_hma100 = INVALID_HANDLE;
        ribbon_hma200 = INVALID_HANDLE;
    }

    bool Init(string sym) {
        m_symbol = sym;
        
        if(true) {
            string fname = "Alpha_Sweep_Dataset_" + m_symbol + ".csv";
            FileDelete(fname);
            m_csv_handle = FileOpen(fname, FILE_WRITE|FILE_CSV|FILE_ANSI, ",");
            if(m_csv_handle != INVALID_HANDLE) {
                FileWriteString(m_csv_handle, "SignalType,HMAAccelF,MTFATRRatio,DistSynthH4,BarsVolShock,TWAPZScore,ATRRatioH,RSI,DistAsianHigh,DistAsianLow,RSIExt,VolSpreadRatio,Spread,TrigRejTail,RibbonSpreadStd,Feature_RibbonAlign,Feature_VPivotMonotonic,RSI_Memory_State,OppositeBarsCount,ReturnPct,Label\n");
                FileFlush(m_csv_handle);
                Print("MetaLabeling: CSV successfully opened -> ", fname, " Handle: ", m_csv_handle);
            } else {
                Print("MetaLabeling: FAILED to open CSV. Error: ", GetLastError(), " File: ", fname);
            }
        }
        
        if     (_Period == PERIOD_M15) m_macro_tf = PERIOD_H1;
        else if(_Period == PERIOD_H1)  m_macro_tf = PERIOD_H4;
        else if(_Period == PERIOD_H4)  m_macro_tf = PERIOD_D1;
        else if(_Period == PERIOD_D1)  m_macro_tf = PERIOD_W1;
        else                           m_macro_tf = PERIOD_H4;
        
        hma_entry_handle = iCustom(m_symbol, _Period, "HMA50", InpHMA_Entry_Period);
        hma_exit_handle  = iCustom(m_symbol, _Period, "HMA50", InpHMA_Exit_Period);
        fast_hma_exit_handle = iCustom(m_symbol, _Period, "HMA50", InpFastHMA_Exit_Period);
        rsi_handle      = iRSI(m_symbol, _Period, RsiPeriod, PRICE_CLOSE);
        ribbon_hma10    = iCustom(m_symbol, _Period, "HMA50", 10);
        ribbon_hma21    = iCustom(m_symbol, _Period, "HMA50", 21);
        ribbon_hma50    = iCustom(m_symbol, _Period, "HMA50", 50);
        ribbon_hma100   = iCustom(m_symbol, _Period, "HMA50", 100);
        ribbon_hma200   = iCustom(m_symbol, _Period, "HMA50", 200);
        atr_handle      = iATR(m_symbol, _Period, 14);
        ema50_handle    = iMA(m_symbol, m_macro_tf, 50,  0, MODE_EMA, PRICE_CLOSE);
        ema200_handle   = iMA(m_symbol, m_macro_tf, 200, 0, MODE_EMA, PRICE_CLOSE);
        sma20_handle    = iMA(m_symbol, _Period, 20, 0, MODE_SMA, PRICE_CLOSE);
        std_dev_handle  = iStdDev(m_symbol, _Period, 20, 0, MODE_SMA, PRICE_CLOSE);
        ema20_h4_handle = iMA(m_symbol, PERIOD_H4, 50, 0, MODE_EMA, PRICE_CLOSE);
        ema50_d1_handle = iMA(m_symbol, PERIOD_D1, 50, 0, MODE_EMA, PRICE_CLOSE);
        atr200_handle   = iATR(m_symbol, _Period, 200);
        atr_d1_handle   = iATR(m_symbol, PERIOD_D1, 14);
        adx_handle      = iADX(m_symbol, PERIOD_H1, 14);

        if(hma_entry_handle == INVALID_HANDLE || hma_exit_handle == INVALID_HANDLE || fast_hma_exit_handle == INVALID_HANDLE ||
           rsi_handle == INVALID_HANDLE || atr_handle == INVALID_HANDLE || std_dev_handle == INVALID_HANDLE ||
           ema20_h4_handle == INVALID_HANDLE || ema50_d1_handle == INVALID_HANDLE || atr200_handle == INVALID_HANDLE || atr_d1_handle == INVALID_HANDLE || adx_handle == INVALID_HANDLE ||
           ribbon_hma10 == INVALID_HANDLE || ribbon_hma21 == INVALID_HANDLE || ribbon_hma50 == INVALID_HANDLE || ribbon_hma100 == INVALID_HANDLE || ribbon_hma200 == INVALID_HANDLE)
        {
            Print("ERROR CRITICO: Indicadores no inicializados para ", m_symbol);
            return false;
        }

        if(m_symbol == _Symbol) {
            ChartIndicatorAdd(0, 0, ribbon_hma10);
            ChartIndicatorAdd(0, 0, ribbon_hma21);
            ChartIndicatorAdd(0, 0, ribbon_hma50);
            ChartIndicatorAdd(0, 0, ribbon_hma100);
            ChartIndicatorAdd(0, 0, ribbon_hma200);
        }
        
        // PROTOCOLO V9.2: RESILIENCIA CRASH-PROOF (RECALIBRACIÓN DE FEATURES Y MAPEO DE POSICIONES)
        RecalibrateStateHistory();
        RecoverState();
        return true;
    }

    void Release() {
        if(m_csv_handle != INVALID_HANDLE) FileClose(m_csv_handle);
        if(hma_entry_handle != INVALID_HANDLE) IndicatorRelease(hma_entry_handle);
        if(hma_exit_handle != INVALID_HANDLE) IndicatorRelease(hma_exit_handle);
        if(fast_hma_exit_handle != INVALID_HANDLE) IndicatorRelease(fast_hma_exit_handle);
        if(rsi_handle != INVALID_HANDLE) IndicatorRelease(rsi_handle);
        if(ribbon_hma10 != INVALID_HANDLE) IndicatorRelease(ribbon_hma10);
        if(ribbon_hma21 != INVALID_HANDLE) IndicatorRelease(ribbon_hma21);
        if(ribbon_hma50 != INVALID_HANDLE) IndicatorRelease(ribbon_hma50);
        if(ribbon_hma100 != INVALID_HANDLE) IndicatorRelease(ribbon_hma100);
        if(ribbon_hma200 != INVALID_HANDLE) IndicatorRelease(ribbon_hma200);
        if(atr_handle != INVALID_HANDLE) IndicatorRelease(atr_handle);
        if(ema50_handle != INVALID_HANDLE) IndicatorRelease(ema50_handle);
        if(ema200_handle != INVALID_HANDLE) IndicatorRelease(ema200_handle);
        if(sma20_handle != INVALID_HANDLE) IndicatorRelease(sma20_handle);
        if(std_dev_handle != INVALID_HANDLE) IndicatorRelease(std_dev_handle);
        if(ema20_h4_handle != INVALID_HANDLE) IndicatorRelease(ema20_h4_handle);
        if(ema50_d1_handle != INVALID_HANDLE) IndicatorRelease(ema50_d1_handle);
        if(atr200_handle != INVALID_HANDLE) IndicatorRelease(atr200_handle);
        if(atr_d1_handle != INVALID_HANDLE) IndicatorRelease(atr_d1_handle);
        if(adx_handle != INVALID_HANDLE) IndicatorRelease(adx_handle);
    }

    void ProcessTick() {
        CheckRealHistory(); // Fase 38: Monitorear racha perdedora antes de gestionar ticks
        RecoverState();     // PROTOCOLO V9.2: Mapeo y reconexión continua de posiciones huérfanas
        TickLevelManagement();
        
        datetime currentBarTime = iTime(m_symbol, _Period, 0);
        if(currentBarTime == lastBarTime || currentBarTime == 0) return;

        double hma_entry[], hma_exit_buf[], rsi_buf[], atr_buf[];
        double ef[], es[], sma20[], stddev[], ema20_h4[], ema50_d1[], atr200_buf[], adx_buf[], atr_d1_buf[];
        double hma10_buf[], hma21_buf[], hma50_buf[], hma100_buf[], hma200_buf[];
        MqlRates rates[];

        ArraySetAsSeries(hma_entry,    true);
        ArraySetAsSeries(hma_exit_buf, true);
        ArraySetAsSeries(rsi_buf,      true);
        ArraySetAsSeries(atr_buf,      true);
        ArraySetAsSeries(ef,           true);
        ArraySetAsSeries(es,           true);
        ArraySetAsSeries(sma20,        true);
        ArraySetAsSeries(stddev,       true);
        ArraySetAsSeries(ema20_h4,     true);
        ArraySetAsSeries(ema50_d1,     true);
        ArraySetAsSeries(atr200_buf,   true);
        ArraySetAsSeries(adx_buf,      true);
        ArraySetAsSeries(atr_d1_buf,   true);
        ArraySetAsSeries(hma10_buf,    true);
        ArraySetAsSeries(hma21_buf,    true);
        ArraySetAsSeries(hma50_buf,    true);
        ArraySetAsSeries(hma100_buf,   true);
        ArraySetAsSeries(hma200_buf,   true);
        ArraySetAsSeries(rates,        true);

        int rates_copied    = CopyRates(m_symbol, _Period, 0, 60, rates);
        if(rates_copied < 4) return;
        ArraySetAsSeries(rates, true); // ANCLAJE FORZOSO PARA MANTENER LA SERIE TEMPORAL
        
        int hma_copied      = CopyBuffer(hma_entry_handle,      0, 0, 60, hma_entry);
        if(hma_copied < 4)   return;
        ArraySetAsSeries(hma_entry, true);   // ANCLAJE FORZOSO PARA MANTENER LA SERIE TEMPORAL
        int hma_exit_copied = CopyBuffer(hma_exit_handle, 0, 0, 3, hma_exit_buf);
        if(hma_exit_copied < 3) return;
        
        if(CopyBuffer(ribbon_hma10, 0, 0, 20, hma10_buf) < 20) return; ArraySetAsSeries(hma10_buf, true);
        if(CopyBuffer(ribbon_hma21, 0, 0, 20, hma21_buf) < 20) return; ArraySetAsSeries(hma21_buf, true);
        if(CopyBuffer(ribbon_hma50, 0, 0, 20, hma50_buf) < 20) return; ArraySetAsSeries(hma50_buf, true);
        if(CopyBuffer(ribbon_hma100, 0, 0, 20, hma100_buf) < 20) return; ArraySetAsSeries(hma100_buf, true);
        if(CopyBuffer(ribbon_hma200, 0, 0, 20, hma200_buf) < 20) return; ArraySetAsSeries(hma200_buf, true);
        if(CopyBuffer(rsi_handle,     0, 1, RsiLookbackBars + 1, rsi_buf) < RsiLookbackBars + 1) return;
        if(CopyBuffer(atr_handle,     0, 1, 51, atr_buf)  < 51) return;
        if(CopyBuffer(atr200_handle,  0, 1, 1,  atr200_buf) < 1) return;
        if(CopyBuffer(atr_d1_handle,  0, 1, 1,  atr_d1_buf) < 1) return;
        if(CopyBuffer(sma20_handle,   0, 1, 1,  sma20)    < 1)  return;
        if(CopyBuffer(std_dev_handle, 0, 1, 1,  stddev)   < 1)  return;

        int macro_shift = iBarShift(m_symbol, m_macro_tf, currentBarTime);
        int h4_shift    = iBarShift(m_symbol, PERIOD_H4,  currentBarTime);
        int d1_shift    = iBarShift(m_symbol, PERIOD_D1,  currentBarTime);
        int h1_shift    = iBarShift(m_symbol, PERIOD_H1,  currentBarTime);
        if(CopyBuffer(ema50_handle,    0, macro_shift + 1, 1, ef)       < 1) return;
        if(CopyBuffer(ema200_handle,   0, macro_shift + 1, 1, es)       < 1) return;
        if(CopyBuffer(ema20_h4_handle, 0, h4_shift + 1, 2, ema20_h4) < 2) return;
        if(CopyBuffer(ema50_d1_handle, 0, d1_shift + 1, 1, ema50_d1) < 1) return;
        
        if(CopyBuffer(adx_handle, 0, h1_shift + 1, 1, adx_buf) < 1) return;
        double macro_adx = adx_buf[0];

        double pip        = GetPip();
        double spread     = 0.0;
        if(pip > 0) spread = (SymbolInfoDouble(m_symbol, SYMBOL_ASK) - SymbolInfoDouble(m_symbol, SYMBOL_BID)) / pip;

        double atr_vals[1]; CopyBuffer(atr_handle, 0, 0, 1, atr_vals); double current_atr = atr_vals[0];

        double fast_hma_k[];
        ArraySetAsSeries(fast_hma_k, true);
        if(CopyBuffer(fast_hma_exit_handle, 0, 0, 4, fast_hma_k) < 4) return;

        // PASO 1: GESTION DE SALIDAS
        ManageOpenTrades(current_atr, spread, rates[1].close, rates[2].close, hma_entry[1], macro_adx, fast_hma_k[1], fast_hma_k[2]);

        // CONCURRENCIA LOCK GLOBAL INMEDIATO
        int total_magic_pos = 0;
        int sym_magic_pos = 0;
        for(int i = PositionsTotal() - 1; i >= 0; i--) {
            ulong t = PositionGetTicket(i);
            if(t > 0 && PositionGetInteger(POSITION_MAGIC) == 777999) {
                total_magic_pos++;
                if(PositionGetString(POSITION_SYMBOL) == m_symbol) sym_magic_pos++;
            }
        }

        if(sym_magic_pos >= InpMaxTradesPerSymbol) {
            lastBarTime = currentBarTime;
            return;
        }

        bars_since_asian_sweep_high++;
        bars_since_asian_sweep_low++;
        bars_since_local_sweep_high++;
        bars_since_local_sweep_low++;
        bars_since_vol_shock_bull++;
        bars_since_vol_shock_bear++;

        // PASO 2: DETECCION DE GATILLOS
        MqlDateTime dt;
        TimeToStruct(currentBarTime, dt);
        
        if(dt.hour < InpStartTradingHour || dt.hour >= InpEndTradingHour) {
            lastBarTime = currentBarTime;
            return;
        }

        MqlDateTime dt_start = dt;
        dt_start.hour = 0; dt_start.min = 0; dt_start.sec = 0;
        datetime asian_start = StructToTime(dt_start);
        MqlDateTime dt_end = dt_start;
        dt_end.hour = 8;
        datetime asian_end = StructToTime(dt_end);
        
        double asian_high = 0.0, asian_low = 0.0;
        int bars_asian = Bars(m_symbol, _Period, asian_start, asian_end);
        if(bars_asian > 0) {
            double ah[], al[];
            if(CopyHigh(m_symbol, _Period, asian_start, asian_end, ah) > 0) {
                asian_high = ah[0];
                for(int k=1; k<ArraySize(ah); k++) { if(ah[k] > asian_high) asian_high = ah[k]; }
            }
            if(CopyLow(m_symbol, _Period, asian_start, asian_end, al) > 0) {
                asian_low = al[0];
                for(int k=1; k<ArraySize(al); k++) { if(al[k] < asian_low) asian_low = al[k]; }
            }
        }
        
        double current_close = rates[1].close;
        bool is_asian_sweep_high = false;
        bool is_asian_sweep_low = false;
        if(asian_high > 0 && asian_low > 0) {
            if(ObjectFind(0, "Asian_High") < 0) ObjectCreate(0, "Asian_High", OBJ_HLINE, 0, 0, asian_high);
            else ObjectMove(0, "Asian_High", 0, 0, asian_high);
            ObjectSetInteger(0, "Asian_High", OBJPROP_STYLE, STYLE_DASH);
            ObjectSetInteger(0, "Asian_High", OBJPROP_COLOR, clrDodgerBlue);
            
            if(ObjectFind(0, "Asian_Low") < 0) ObjectCreate(0, "Asian_Low", OBJ_HLINE, 0, 0, asian_low);
            else ObjectMove(0, "Asian_Low", 0, 0, asian_low);
            ObjectSetInteger(0, "Asian_Low", OBJPROP_STYLE, STYLE_DASH);
            ObjectSetInteger(0, "Asian_Low", OBJPROP_COLOR, clrOrange);
            
            bool swept_asian_high = (rates[1].high > asian_high) && (rates[1].close <= asian_high) && (rates[1].open <= asian_high);
            bool swept_asian_low  = (rates[1].low < asian_low)   && (rates[1].close >= asian_low)  && (rates[1].open >= asian_low);
            if(swept_asian_high) { bars_since_asian_sweep_high = 0; is_asian_sweep_high = true; }
            if(swept_asian_low)  { bars_since_asian_sweep_low = 0; is_asian_sweep_low = true; }
        }

        int pb_duration = 0;
        double pb_depth    = 0.0;
        CalcPullbackMetrics(m_symbol, hma_entry_handle, LookbackBars, current_atr, pb_duration, pb_depth);

        int offset = (int)(TimeCurrent() - TimeGMT());
        datetime utc_time = currentBarTime - offset;
        MqlDateTime dt_utc;
        TimeToStruct(utc_time, dt_utc);

        int h = dt_utc.hour;
        int session_time = 1;
        if(h >= 13) {
            if(h <= 14) session_time = 0;
            else if(h <= 20) session_time = 3;
        } else {
            if(h >= 7) session_time = 2;
        }

        double local_high = rates[2].high;
        double local_low  = rates[2].low;
        int max_dc = MathMin(rates_copied, InpDonchianPeriod + 2);
        for(int k=3; k<max_dc; k++) {
            if(rates[k].high > local_high) local_high = rates[k].high;
            if(rates[k].low < local_low)   local_low  = rates[k].low;
        }
        
        bool swept_local_high = (rates[1].high > local_high) && (rates[1].close <= local_high) && (rates[1].open <= local_high);
        bool swept_local_low  = (rates[1].low < local_low)   && (rates[1].close >= local_low)  && (rates[1].open >= local_low);
        if(swept_local_high) bars_since_local_sweep_high = 0;
        if(swept_local_low)  bars_since_local_sweep_low  = 0;

        double tick_vol_zscore = 0.0;
        if(rates_copied >= 22) {
            double sum_vol = 0;
            for(int k=1; k<21; k++) sum_vol += (double)rates[k].tick_volume;
            double mean_vol = sum_vol / 20.0;
            double sq_diff_sum = 0;
            for(int k=1; k<21; k++) sq_diff_sum += MathPow((double)rates[k].tick_volume - mean_vol, 2);
            double std_vol = MathSqrt(sq_diff_sum / 20.0);
            if(std_vol > 0) tick_vol_zscore = ((double)rates[1].tick_volume - mean_vol) / std_vol;
        }
        
        double spread_exp_ratio = 1.0; 
        double candle_body  = MathAbs(rates[1].open - rates[1].close);
        double candle_range = rates[1].high - rates[1].low;
        double candle_dominance = 0.0;
        if(candle_range > 0) candle_dominance = candle_body / candle_range;

        bool is_bullish = (rates[1].close > rates[1].open);
        bool is_bearish = (rates[1].close < rates[1].open);
        if(tick_vol_zscore > 0.75 && is_bullish) bars_since_vol_shock_bull = 0;
        if(tick_vol_zscore > 0.75 && is_bearish) bars_since_vol_shock_bear = 0;

        // =====================================================================
        // FASE 55: THE MAGNIFICENT 5 - SPLIT-CORE DINAMICO
        // =====================================================================
        bool triggerBUY  = false;
        bool triggerSELL = false;

        // PROTOCOLO ALPHA FASE 87: MULTI-HMA RIBBON & HYSTERESIS RE-ARCHITECTURE
        bool cross_up = false;
        bool cross_dn = false;

        // Gatillo Legacy: Precio vs HMA
        triggerBUY  = (rates[2].close < hma_entry[2] && rates[1].close > hma_entry[1]);
        triggerSELL = (rates[2].close > hma_entry[2] && rates[1].close < hma_entry[1]);

        int feat_ribbon_align = 0;
        int feat_vpivot_monotonic = 0;
        int feat_rsi_memory = 0;
        int feat_opposite_bars = 0;
        double feat_price_dev_atr = 0.0;

        if (triggerBUY) {
            cross_up = true;
            
            // 1. Ribbon Align
            if (hma21_buf[1] > hma50_buf[1] && hma50_buf[1] > hma100_buf[1]) {
                feat_ribbon_align = 1;
            }
            
            // 2. V-Pivot Monotonic
            int pivot_idx = -1;
            for(int j = 2; j <= 2 + InpHysteresisBars; j++) {
                if (hma21_buf[j] < hma21_buf[j+1] && hma21_buf[j] < hma21_buf[j-1]) {
                    pivot_idx = j; break;
                }
            }
            if (pivot_idx != -1) {
                bool monotonic = true;
                for(int k = pivot_idx - 1; k >= 1; k--) {
                    if (hma21_buf[k] <= hma21_buf[k+1]) { monotonic = false; break; }
                }
                if (monotonic) feat_vpivot_monotonic = 1;
            }
            
            // 3. RSI Memory State
            for(int i = 1; i <= 10; i++) {
                if(rsi_buf[i] < 35.0) { feat_rsi_memory = 1; break; }
            }
            
            // 4. Opposite Bars Count
            for(int i = 2; i < 60; i++) {
                if(rates[i].close < rates[i].open) feat_opposite_bars++;
                else break;
            }
            
            // 5. Price Deviation ATR
            if(current_atr > 0) {
                double max_dev = 0;
                for(int i = 1; i < 60; i++) {
                    if(rates[i].close > hma_entry[i]) break; // Wave ended
                    double dev = hma_entry[i] - rates[i].low;
                    if(dev > max_dev) max_dev = dev;
                }
                feat_price_dev_atr = max_dev / current_atr;
            }
            
        } else if (triggerSELL) {
            cross_dn = true;
            
            // 1. Ribbon Align
            if (hma21_buf[1] < hma50_buf[1] && hma50_buf[1] < hma100_buf[1]) {
                feat_ribbon_align = 1;
            }
            
            // 2. V-Pivot Monotonic
            int pivot_idx = -1;
            for(int j = 2; j <= 2 + InpHysteresisBars; j++) {
                if (hma21_buf[j] > hma21_buf[j+1] && hma21_buf[j] > hma21_buf[j-1]) {
                    pivot_idx = j; break;
                }
            }
            if (pivot_idx != -1) {
                bool monotonic = true;
                for(int k = pivot_idx - 1; k >= 1; k--) {
                    if (hma21_buf[k] >= hma21_buf[k+1]) { monotonic = false; break; }
                }
                if (monotonic) feat_vpivot_monotonic = 1;
            }
            
            // 3. RSI Memory State
            for(int i = 1; i <= 10; i++) {
                if(rsi_buf[i] > 65.0) { feat_rsi_memory = 1; break; }
            }
            
            // 4. Opposite Bars Count
            for(int i = 2; i < 60; i++) {
                if(rates[i].close > rates[i].open) feat_opposite_bars++;
                else break;
            }
            
            // 5. Price Deviation ATR
            if(current_atr > 0) {
                double max_dev = 0;
                for(int i = 1; i < 60; i++) {
                    if(rates[i].close < hma_entry[i]) break; // Wave ended
                    double dev = rates[i].high - hma_entry[i];
                    if(dev > max_dev) max_dev = dev;
                }
                feat_price_dev_atr = max_dev / current_atr;
            }
        }

        int count_consistent_buy  = CountConsistentlyBelowHMA(rates, hma_entry, 3);
        int count_consistent_sell = CountConsistentlyAboveHMA(rates, hma_entry, 3);

        bool rsi_oversold   = WasRSIOversold(rsi_buf, 0, RsiLookbackBars, (double)RsiOversoldLevel);
        bool rsi_overbought = WasRSIOverbought(rsi_buf, 0, RsiLookbackBars, (double)RsiOverboughtLevel);

        bool has_trigger = false;
        if (triggerBUY) {
            has_trigger = true;
        } else if (triggerSELL) {
            has_trigger = true;
        }

        if(!has_trigger) {
            lastBarTime = currentBarTime;
            return;
        }

        int signalType = 1;          // 1=SELL
        if(triggerBUY) {
            signalType = 0;          // 0=BUY
        }

        string symbol_upper = m_symbol;
        StringToUpper(symbol_upper);
        double max_allowed_spread = MaxSpreadPips;
        if(StringFind(symbol_upper, "XAU") >= 0 || StringFind(symbol_upper, "GOLD") >= 0 || StringFind(symbol_upper, "XAG") >= 0) {
            max_allowed_spread = InpMaxSpreadPips_Metals;
        }

        
        if(false) {
            Print("ABORT: Spread demasiado alto en ", m_symbol, " - Spread: ", spread, " Max: ", max_allowed_spread);
            lastBarTime = currentBarTime;
            return;
        }

        double minDev = current_atr * (AntiNoiseATRPct / 100.0);
        double deviation = MathAbs(rates[1].close - hma_entry[1]);
        if(deviation < minDev) {
            // Silenciado por ser muy comun
            lastBarTime = currentBarTime;
            return;
        }

        double candle_size = rates[1].high - rates[1].low;
        if(candle_size > (current_atr * InpMaxSignalBarATR)) {
            Print("ABORT: Vela de senal demasiado grande en ", m_symbol);
            lastBarTime = currentBarTime;
            return;
        }


        // --- FASE 36.5: GEOMETRÃƒÂA Y EMBARGO DIRECCIONAL ---
        int start_bar = iBarShift(m_symbol, _Period, iTime(m_symbol, PERIOD_D1, 0));
        double twap_z_score = 0.0;
        if(start_bar >= 0) {
            double closes[];
            if(CopyClose(m_symbol, _Period, 0, start_bar + 1, closes) > 0) {
                double sum_price = 0;
                int count = ArraySize(closes);
                for(int i = 0; i < count; i++) sum_price += closes[i];
                double twap = sum_price / count;
                if(current_atr > 0) twap_z_score = (current_close - twap) / current_atr;
            }
        }
        
        double body_size = MathAbs(rates[1].close - rates[1].open);
        double breakout_velocity = (body_size / PeriodSeconds(_Period)) * 60.0;
        
        bool has_opposite_runner = false;
        for(int i = 0; i < PositionsTotal(); i++) {
            if(PositionGetSymbol(i) == m_symbol && PositionGetInteger(POSITION_MAGIC) == 777999) {
                long pType = PositionGetInteger(POSITION_TYPE);
                if(signalType == 0 && pType == POSITION_TYPE_SELL) has_opposite_runner = true;
                if(signalType == 1 && pType == POSITION_TYPE_BUY) has_opposite_runner = true;
            }
        }

        if(has_opposite_runner) {
            Print("EMBARGO DIRECCIONAL PERMANENTE: Bloqueando SAR. Dejando que la posicion opuesta respire en ", m_symbol);
            lastBarTime = currentBarTime;
            return;
        }
        // ----------------------------------------------------

        double ask = SymbolInfoDouble(m_symbol, SYMBOL_ASK);
        double bid = SymbolInfoDouble(m_symbol, SYMBOL_BID);

        // FASE 68: ALINEACION PERFECTA CON BASELINE DE PYTHON
        // El Baseline simula un Hard Stop absoluto en MAX_SL_ATR (5.0) y deja que
        // la Red Neuronal de Salida cierre la operacion cuando se agote la tendencia.
        double sl = 0.0;
        if(signalType == 0) sl = ask - (current_atr * InpMaxSLATR);
        else sl = bid + (current_atr * InpMaxSLATR);
        
        if(sl == DBL_MAX || sl == -DBL_MAX) { 
            Print("ABORT: SL invalido (DBL_MAX) en ", m_symbol);
            lastBarTime = currentBarTime; return; 
        }

        double slDist = sl - bid;
        if(signalType == 0) slDist = ask - sl;
        
        if(slDist <= 0.0) { 
            Print("ABORT: SL Distancia <= 0 en ", m_symbol, " SL:", sl, " Bid/Ask:", bid, "/", ask);
            lastBarTime = currentBarTime; return; 
        }

        double sl_dist_atr = 0.0;
        if(current_atr > 0) sl_dist_atr = slDist / current_atr;
        
        if(false) { 
            Print("ABORT: SL_ATR excedido en ", m_symbol, " - SL_ATR: ", sl_dist_atr, " Max: ", InpMaxSLATR);
            lastBarTime = currentBarTime; return; 
        }
        
        double sl_distance_points = slDist / SymbolInfoDouble(m_symbol, SYMBOL_POINT);

        int count_dir = 0;
        double max_proba_open = 0.0;
        int total_positions = PositionsTotal();
        
        for(int i = 0; i < total_positions; i++) {
            if(PositionGetSymbol(i) == m_symbol && PositionGetInteger(POSITION_MAGIC) == 777999) {
                long pType = PositionGetInteger(POSITION_TYPE);
                bool is_same_dir = false;
                if(signalType == 0 && pType == POSITION_TYPE_BUY) is_same_dir = true;
                if(signalType == 1 && pType == POSITION_TYPE_SELL) is_same_dir = true;
                
                if(is_same_dir) {
                    count_dir++;
                    string comment = PositionGetString(POSITION_COMMENT);
                    int ai_idx = StringFind(comment, "AI_");
                    if(ai_idx != -1) {
                        double prb = StringToDouble(StringSubstr(comment, ai_idx + 3));
                        if(prb > max_proba_open) max_proba_open = prb;
                    }
                }
            }
        }
        
        // PROTOCOLO V9.2: ESCUDO ANTI-DUPLICACIÓN DE ENTRADAS (CRASH-PROOF)
        if(count_dir > 0 || sym_magic_pos >= InpMaxTradesPerSymbol) {
            Print("[V9.2 CRASH-PROOF] Ya existe una posición abierta en ", m_symbol, " (dirección coincidente o límite alcanzado). Bloqueando duplicación.");
            lastBarTime = currentBarTime;
            return;
        }
        
        bool limit_reached = false;
        // sym_magic_pos is already checked at the lock, but we enforce risk here
        
        bool risk_exceeded = false;
        double current_portfolio_risk = CalculateRealFloatingRisk();
        if((current_portfolio_risk + GetEffectiveRiskPct()) > InpMaxGlobalRisk) risk_exceeded = true;
        
        if(limit_reached || risk_exceeded) {
            lastBarTime = currentBarTime;
            return;
        }

        double z_score = 0.0;
        if(stddev[0] > 0) z_score = (current_close - sma20[0]) / stddev[0];

        double atr_sum = 0.0;
        for(int k = 0; k < 10; k++) atr_sum += atr_buf[k];
        double atr_norm = 1.0;
        if(atr_sum > 0) atr_norm = current_atr / (atr_sum / 10.0);

        double rsi_val     = rsi_buf[0];
        double rsi_extreme = 50.0;
        int    bars_since  = RsiLookbackBars;
        CalcRsiExtremeMetrics(rsi_handle, RsiLookbackBars, signalType, rsi_extreme, bars_since);

        double hma_slope = 0.0;
        if(current_atr > 0) hma_slope = (hma_entry[1] - hma_entry[2]) / current_atr;

        double hma_accel_feat = CalcHmaAcceleration(hma_entry_handle, current_atr);
        double breakout_force = CalcBreakoutForceATR(current_close, hma_entry[1], current_atr);

        int    trend_align = -1;
        if(ef[0] > es[0]) trend_align = 1;
        double dist_macro = CalcDistToMacroEMA(current_close, es[0], current_atr);


        int h4_trend_align = (rates[1].close > ema20_h4[0]) ? 1 : -1;

        double atr_sma50 = 0.0;
        for(int k=0; k<50; k++) atr_sma50 += atr_buf[k];
        atr_sma50 /= 50.0;

        double vol_spread_ratio = 1.0;
        if(atr_sma50 > 0) vol_spread_ratio = current_atr / atr_sma50;

        double atr_ratio_high = 1.0;
        if(atr200_buf[0] > 0) atr_ratio_high = current_atr / atr200_buf[0];

        double rsi_slope_10 = rsi_buf[0] - rsi_buf[10];
        
        double sl_pips = slDist / pip;
        double spread_impact_ratio = 0.0;
        if(sl_pips > 0) spread_impact_ratio = spread / sl_pips;

        double hma_vel        = (hma_entry[1] - hma_entry[2]) / current_atr;
        double vel_prev_k     = (hma_entry[2] - hma_entry[3]) / current_atr;
        double hma_accel_v2   = hma_vel - vel_prev_k;
        double vel_prev2_k    = (hma_entry[3] - hma_entry[4]) / current_atr;
        double accel_prev_k   = vel_prev_k - vel_prev2_k;
        double hma_jerk_val   = hma_accel_v2 - accel_prev_k;

        int  energy_accum  = 0;
        int  max_eb        = MathMin(rates_copied, hma_copied);
        bool stop_count    = false;
        if(signalType == 0) {
            for(int k = 1; k < max_eb; k++) {
                if(!stop_count) {
                    if(rates[k].close < hma_entry[k]) energy_accum++;
                    else stop_count = true;
                }
            }
        } else {
            for(int k = 1; k < max_eb; k++) {
                if(!stop_count) {
                    if(rates[k].close > hma_entry[k]) energy_accum++;
                    else stop_count = true;
                }
            }
        }

        double mtf_atr_ratio = 0.0;
        if (atr_d1_buf[0] > 0) mtf_atr_ratio = current_atr / atr_d1_buf[0];

        double trigger_rejection_tail = 0.0;
        double cdl_range = rates[1].high - rates[1].low;
        if(cdl_range > 0) {
            if(signalType == 0) {
                trigger_rejection_tail = (MathMin(rates[1].open, rates[1].close) - rates[1].low) / cdl_range;
            } else {
                trigger_rejection_tail = (rates[1].high - MathMax(rates[1].open, rates[1].close)) / cdl_range;
            }
        }

        double bollinger_dev = 0.0;
        if(stddev[0] > 0) {
            bollinger_dev = (current_close - sma20[0]) / stddev[0];
        }

        // --- FASE 69: MQL5 NATIVE XGBOOST INFERENCE ---
        double hma_dist_ema = 0.0;
        if(current_atr > 0 && ef[0] > 0) hma_dist_ema = (hma_entry[0] - ef[0]) / current_atr;

        double bars_since_asian_sweep = (signalType == 0) ? bars_since_asian_sweep_low : bars_since_asian_sweep_high;
        double bars_since_local_sweep = (signalType == 0) ? bars_since_local_sweep_low : bars_since_local_sweep_high;
        
        double dist_asian_high_atr = 0;
        double dist_asian_low_atr = 0;
        if(current_atr > 0) {
            if(asian_high > 0) dist_asian_high_atr = (asian_high - current_close)/current_atr;
            if(asian_low > 0) dist_asian_low_atr = (current_close - asian_low)/current_atr;
        }
        
        int is_asian_sweep = (signalType == 0) ? (is_asian_sweep_low ? 1 : 0) : (is_asian_sweep_high ? 1 : 0);
        
        int reg_consist = (signalType == 0) ? count_consistent_buy : count_consistent_sell;
        
        double atr_ratio_47 = 0.0;
        if(atr_sma50 > 0) atr_ratio_47 = current_atr / atr_sma50;
        
        double bb_width_47 = 0.0;
        if(sma20[0] > 0) bb_width_47 = (stddev[0] * 4.0) / sma20[0];
        
        double dist_synth_h4 = 0.0;
        if(current_atr > 0) dist_synth_h4 = (current_close - ema20_h4[0]) / current_atr;
        
        double dist_synth_d1 = 0.0;
        if(current_atr > 0) dist_synth_d1 = (current_close - ema50_d1[0]) / current_atr;

        double ribbon_compression_atr = 0;
        if(current_atr > 0) ribbon_compression_atr = MathAbs(hma10_buf[1] - hma200_buf[1]) / current_atr;
        
        double price_to_macro_hma_dist = 0;
        if(current_atr > 0) price_to_macro_hma_dist = (rates[1].close - hma200_buf[1]) / current_atr;
        
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
        
        double mean_ribbon = (hma10_buf[1] + hma21_buf[1] + hma50_buf[1] + hma100_buf[1] + hma200_buf[1]) / 5.0;
        double variance = (MathPow(hma10_buf[1] - mean_ribbon, 2) + MathPow(hma21_buf[1] - mean_ribbon, 2) + MathPow(hma50_buf[1] - mean_ribbon, 2) + MathPow(hma100_buf[1] - mean_ribbon, 2) + MathPow(hma200_buf[1] - mean_ribbon, 2)) / 5.0;
        double ribbon_spread_stddev = 0;
        if(current_atr > 0) ribbon_spread_stddev = MathSqrt(variance) / current_atr;

        int pandas_dow = (dt.day_of_week == 0) ? 6 : (dt.day_of_week - 1);

        double features[19];
        features[0] = signalType;
        features[1] = hma_accel_feat;
        features[2] = mtf_atr_ratio;
        features[3] = dist_synth_h4;
        features[4] = (signalType == 0) ? bars_since_vol_shock_bull : bars_since_vol_shock_bear;
        features[5] = twap_z_score;
        features[6] = atr_ratio_high;
        features[7] = rsi_buf[0];
        features[8] = dist_asian_high_atr;
        features[9] = dist_asian_low_atr;
        features[10] = rsi_extreme;
        features[11] = vol_spread_ratio;
        features[12] = spread;
        features[13] = trigger_rejection_tail;
        features[14] = ribbon_spread_stddev;
        features[15] = feat_ribbon_align;
        features[16] = feat_vpivot_monotonic;
        features[17] = feat_rsi_memory;
        features[18] = feat_opposite_bars;


        double entry_proba = 0.0;
        if(m_symbol == "XAUUSD")      entry_proba = XGBoost_Predict_XAUUSD(features);
        else if(m_symbol == "EURUSD") entry_proba = XGBoost_Predict_EURUSD(features);
        else if(m_symbol == "USDJPY") entry_proba = XGBoost_Predict_USDJPY(features);
        else if(m_symbol == "AUDUSD") entry_proba = XGBoost_Predict_AUDUSD(features);
        else if(m_symbol == "AUDCAD") entry_proba = XGBoost_Predict_AUDCAD(features);
        else if(m_symbol == "GBPJPY") entry_proba = XGBoost_Predict_GBPJPY(features);
        else if(m_symbol == "XAGUSD") entry_proba = XGBoost_Predict_XAGUSD(features);
        else {
            PrintFormat("🚨 [PROTOCOLO V9.1] ABORTO CRÍTICO: Símbolo [%s] NO posee modelo XGBoost nativo. Fallback a XAUUSD bloqueado por seguridad.", m_symbol);
            lastBarTime = currentBarTime;
            return;
        }
        
        bool execute_trade = false;
        double sym_entry_thresh = GetSymbolThreshold(m_symbol);
        
        string dir_str = (signalType == 0) ? "COMPRA" : "VENTA";
        string estado_str = "";
        
        if(InpMetaLabeling || entry_proba >= sym_entry_thresh) {
            if(count_dir == 0) {
                execute_trade = true;
                estado_str = "APROBADO -> Orden Ejecutada";
            } else {
                Print("Rechazado: Ya hay una operacion en esta direccion.");
                estado_str = "RECHAZADO -> Orden Existente";
            }
        } else {
             Print("Rechazado por XGBoost. Proba: ", entry_proba, " < ", sym_entry_thresh);
             estado_str = "RECHAZADO -> Probabilidad Baja";
        }
        
        string telemetria = StringFormat("[ÃƒÅ¡ltimo Gatillo Evaluado]\nDirecciÃƒÂ³n: %s\nXGBoost Probability: %.2f\nThreshold: %.2f\nEstado: %s", dir_str, entry_proba, sym_entry_thresh, estado_str);
        Comment(telemetria);
        
        if(execute_trade) {
            if(m_embargo_active) {
                if(!m_virtual_active) {
                    m_virtual_type = signalType == 0 ? POSITION_TYPE_BUY : POSITION_TYPE_SELL;
                    m_virtual_open = signalType == 0 ? ask : bid;
                    m_virtual_sl = sl;
                    
                    double risk_dist = MathAbs(m_virtual_open - m_virtual_sl);
                    m_virtual_target = (m_virtual_type == POSITION_TYPE_BUY) ? 
                                       (m_virtual_open + risk_dist * 1.5) : 
                                       (m_virtual_open - risk_dist * 1.5);
                    
                    m_virtual_active = true;
                    string vTypeStr = (m_virtual_type == POSITION_TYPE_BUY) ? "BUY" : "SELL";
                    Print("[TRADE FANTASMA] Abierto ", vTypeStr, " Virtual en ", m_virtual_open, " | SL: ", m_virtual_sl, " | TP (1.5R): ", m_virtual_target);
                } else {
                    Print("[SHADOW MODE] Ignorando seÃƒÂ±al real. Ya hay un trade virtual activo en ", m_symbol);
                }
            } else {
                double open_p = (signalType == 0) ? ask : bid;
                double lots = CalcDynamicLotSize(signalType, open_p, sl);
                string comment = "AI_" + DoubleToString(entry_proba, 2);
                
                if(lots > 0) {
                    double tp = 0.0;
                    if(InpTPATR > 0) {
                        if(signalType == 0) tp = ask + (current_atr * InpTPATR);
                        else tp = bid - (current_atr * InpTPATR);
                    }
                    double required_margin = 0.0;
                    if(OrderCalcMargin(signalType == 0 ? ORDER_TYPE_BUY : ORDER_TYPE_SELL, m_symbol, lots, signalType == 0 ? ask : bid, required_margin)) {
                        if(AccountInfoDouble(ACCOUNT_MARGIN_FREE) < required_margin * 1.5) {
                            Print("ABORT: Margen libre insuficiente. Free: ", AccountInfoDouble(ACCOUNT_MARGIN_FREE), " Req: ", required_margin);
                            return;
                        }
                    }
                    if(signalType == 0) trade.Buy(lots, m_symbol, ask, sl, tp, comment);
                    else trade.Sell(lots, m_symbol, bid, sl, tp, comment);
                    Print("ORDEN ENVIADA - Sym: ", m_symbol, " Proba: ", entry_proba, " Lotes: ", lots);
                    
                    if(true && trade.ResultRetcode() == TRADE_RETCODE_DONE) {
                        ArrayCopy(m_saved_features, features);
                        m_saved_signal_type = signalType;
                        m_active_ticket = trade.ResultDeal();
                        if(m_active_ticket == 0) m_active_ticket = trade.ResultOrder();
                        for(int k = 0; k < PositionsTotal(); k++) {
                            if(PositionGetSymbol(k) == m_symbol && PositionGetInteger(POSITION_MAGIC) == 777999) {
                                m_active_ticket = PositionGetTicket(k);
                                m_saved_entry_price = PositionGetDouble(POSITION_PRICE_OPEN);
                                m_saved_sl_dist = MathAbs(m_saved_entry_price - sl);
                                m_saved_open_time = (datetime)PositionGetInteger(POSITION_TIME);
                                break;
                            }
                        }
                    }
                }
            }
        }
        
        lastBarTime = currentBarTime;
    }
};

// Array de managers
CSymbolManager* g_managers[];

//+------------------------------------------------------------------+
//| OnInit                                                           |
//+------------------------------------------------------------------+
int OnInit()
{
    // FASE 68: Lobo Solitario Check
    // if(StringFind(InpSymbols, _Symbol) < 0) {
    //     Print("FASE 68 LOBO SOLITARIO: El EA Alpha Sniper esta limitado a ", InpSymbols, ". Apagando EA en ", _Symbol);
    //     ExpertRemove();
    //     return INIT_FAILED;
    // }

    // if(!LoadXGBoostModel()) {
    //    Print("CRITICAL ERROR: No se pudo cargar el modelo XGBoost desde JSON. Corriendo en modo geometria pura.");
    //    // return INIT_FAILED;
    // }

    trade.SetExpertMagicNumber(777999);
    trade.SetDeviationInPoints(InpMaxSlippagePoints);
    g_VerticalBarrierBars = (int)(InpHMA_Exit_Period * 1.5);
    
    g_initial_balance = AccountInfoDouble(ACCOUNT_BALANCE);
    if(g_initial_balance <= 0.0) g_initial_balance = InpFixedBalance;
    g_peak_equity = AccountInfoDouble(ACCOUNT_EQUITY);

    string symbols[];
    ushort sep = StringGetCharacter(",", 0);
    int num_symbols = StringSplit(InpSymbols, sep, symbols);
    
    if(num_symbols == 0) {
        Print("ERROR: No se han especificado simbolos en InpSymbols.");
        return INIT_FAILED;
    }
    
    ArrayResize(g_managers, num_symbols);
    for(int i = 0; i < num_symbols; i++) {
        string sym = symbols[i];
        StringTrimLeft(sym);
        StringTrimRight(sym);
        
        if(false && sym != "USDJPY" && sym != "EURJPY" && sym != "XAUUSD" && sym != "GBPUSD" && sym != "EURUSD" && sym != "XAGUSD" && sym != "GBPJPY") {
            Alert("ALERTA (FASE 94): Activo no autorizado. Alpha Sniper solo opera en Los Magnificos (USDJPY, EURJPY, XAUUSD, GBPUSD, EURUSD, XAGUSD, GBPJPY).");
            ExpertRemove();
            return INIT_FAILED;
        }
        
        if(!SymbolSelect(sym, true)) {
            Print("ERROR: No se pudo seleccionar el simbolo en Market Watch: ", sym);
            return INIT_FAILED;
        }
        
        g_managers[i] = new CSymbolManager();
        if(!g_managers[i].Init(sym)) {
            Print("ERROR: Fallo al inicializar CSymbolManager para ", sym);
            return INIT_FAILED;
        }
    }
    
    // Iniciar temporizador asÃƒÂ­ncrono para bucle de escaneo
    EventSetMillisecondTimer(500);

    Print("OK: Alpha Sniper Deploy Multi-Divisa (Fase 19) Ã¢â‚¬â€ Autor: Manuel");
    return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| OnDeinit                                                         |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
    EventKillTimer();
    
    int num_managers = ArraySize(g_managers);
    for(int i = 0; i < num_managers; i++) {
        if(CheckPointer(g_managers[i]) != POINTER_INVALID) {
            g_managers[i].Release();
            delete g_managers[i];
        }
    }
    ArrayFree(g_managers);
    ArrayFree(g_scaled_identifiers);
}

//+------------------------------------------------------------------+
//| OnTimer (Bucle AsÃƒÂ­ncrono Maestro)                                |
//+------------------------------------------------------------------+
void OnTimer()
{
    int num_managers = ArraySize(g_managers);
    for(int i = 0; i < num_managers; i++) {
        if(CheckPointer(g_managers[i]) != POINTER_INVALID) {
            g_managers[i].ProcessTick();
        }
    }
}

//+------------------------------------------------------------------+
//| OnTick (Fallback / Mantenimiento)                                |
//+------------------------------------------------------------------+
void OnTick()
{
    // Asegurar que el Shadow TP reaccione de inmediato en Strategy Tester y Produccin
    int num_managers = ArraySize(g_managers);
    for(int i = 0; i < num_managers; i++) {
        if(CheckPointer(g_managers[i]) != POINTER_INVALID) {
            g_managers[i].TickLevelManagement();
        }
    }
}







//+------------------------------------------------------------------+
//| OnTester - Para Extraccion Python                                 |
//+------------------------------------------------------------------+
double OnTester() {
    double net_profit = TesterStatistics(STAT_PROFIT);
    double dd_cash = TesterStatistics(STAT_EQUITY_DD);
    double profit_factor = TesterStatistics(STAT_PROFIT_FACTOR);
    
    Print("===========================");
    Print("Net Profit:      ", net_profit);
    Print("Max Drawdown ($): ", dd_cash);
    Print("Profit Factor:   ", profit_factor);
    Print("===========================");
    return net_profit;
}
