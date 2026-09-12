//+------------------------------------------------------------------+
//| Bot: HMA_Extractor_Orchestrator.mq5                                
//| Familia: Data Engineering & Labeling                      
//|                                                                  
//| [CHANGELOG & EVOLUCION]:                                         
//| Orquestador universal de meta-etiquetado. Registra cinematica para exportar CSV a Python.
//+------------------------------------------------------------------+
//+------------------------------------------------------------------+
//|                                          HMA_ML_Orchestrator.mq5 |
//|        Mass Data Harvester (Meta-Labeling v2.3 - Fase 23)        |
//|        Autor: Manuel                                             |
//|        Multi-Símbolo, Asíncrono, Orientado a Objetos (OOP)       |
//+------------------------------------------------------------------+
#property strict
#property version "2.3"
#property description "HMA Meta-Labeling Mass Data Harvester"

#include <Trade\Trade.mqh>
#include <ML_Logger.mqh>
#include <HMA_FUNCTIONS.mqh>

CTrade trade;

static const double FIXED_LOT = 0.01;

//+------------------------------------------------------------------+
//| Parametros de Entrada                                            |
//+------------------------------------------------------------------+
input string InpHarvestSymbols = "XAUUSD";

input group "== Estrategia HMA =="
input int    InpHMA_Entry_Period = 50;
input int    InpHMA_Exit_Period  = 20;
input int    InpMinBarsToHold    = 3;
input int    LookbackBars        = 7;
input double AntiNoiseATRPct     = 2.0;

input group "== Contexto y Features =="
input int    RsiPeriod           = 14;
input int    RsiLookbackBars     = 15;
input int    RsiOversoldLevel    = 35;
input int    RsiOverboughtLevel  = 65;

input group "== Microestructura =="
input double MaxSpreadPips          = 4.0;
input double InpMaxSpreadPips_Metals = 120.0; // Spread máximo ampliado para XAUUSD/XAGUSD
input int    InpDonchianPeriod      = 20;

input group "== Gestion ML (Triple Barrera) =="
input double InpInitialBalance   = 100000.0;
input double TakeProfitMultiplier = 3.0;
input double InpScaleOutRR       = 1.5;  
input int    InpFastHMA_Exit_Period = 14; 

input group "== Filtros Macro / Cisnes Negros =="
input double InpMaxSignalBarATR  = 2.5;
input double InpMaxSLATR         = 5.0;

// =============================================================================
// PROTOCOLO ALPHA FASE 44.5 / 45: Pruebas de Vida HMA + Split-Core
// =============================================================================
enum ENUM_TRIGGER_MODE {
    TRIGGER_CROSS        = 0, // Modo 0 (LEGACY): Cruce Precio vs HMA
    TRIGGER_INFLECTION   = 1, // Prueba 1: Inflexión (cambio de pendiente — Vértice V-Shape)
    TRIGGER_ADX_SHIELD   = 2, // Prueba 2: Inflexión + Escudo ADX > umbral anti-whipsaw
    TRIGGER_MEAN_REVERT  = 3, // Prueba 3: Reversión a Media Extrema (HMA Bands)
    TRIGGER_ASIAN_SWEEP  = 4, // Fase 45: Barrido de Liquidez del Rango Asiático (Price Action puro)
    TRIGGER_SPECTRUM_DECOMPRESSION = 5
};
input group "== Fase 44.5 / 45: Modo de Gatillo =="
input ENUM_TRIGGER_MODE InpTriggerMode   = TRIGGER_INFLECTION; // Modo de disparo de recolección (sobrescrito por Split-Core en USDJPY/EURUSD/GBPUSD)
input double            InpADXThreshold  = 5.0;                // Umbral ADX mínimo (Prueba 2)
input double            InpHMABandATRMult = 1.5;               // Multiplicador ATR para Banda HMA (Prueba 3)

// Globals
int g_VerticalBarrierBars;

//+------------------------------------------------------------------+
//| Helper: String Split                                             |
//+------------------------------------------------------------------+
int SplitString(const string inStr, const string sep, string &result[]) {
    int count = StringSplit(inStr, StringGetCharacter(sep, 0), result);
    for (int i=0; i<count; i++) {
        StringTrimLeft(result[i]);
        StringTrimRight(result[i]);
    }
    return count;
}

//+------------------------------------------------------------------+
//| CHarvestManager - Encapsula la recolección de 1 símbolo          |
//+------------------------------------------------------------------+
class CHarvestManager {
private:
    string           m_symbol;
    ENUM_TIMEFRAMES  m_macro_tf;

    int hma_entry_handle, hma_exit_handle, rsi_handle, atr_handle, atr100_handle;
    int ema50_handle, ema200_handle, sma20_handle, std_dev_handle;
    int synth_ema20_h4_handle, atr200_handle, synth_atr_d1_handle, synth_adx_d1_handle, synth_ema50_d1_handle;
    int fast_hma_exit_handle;
    int ribbon_hma10, ribbon_hma21, ribbon_hma50, ribbon_hma100, ribbon_hma200;

    CMLDataLogger   *m_logger;
    // CExitDataLogger *m_exit_logger;

    ulong            m_scaled_tickets[];
    datetime         m_lastBarTime;

    int bars_since_asian_sweep_high;
    int bars_since_asian_sweep_low;
    int bars_since_local_sweep_high;
    int bars_since_local_sweep_low;
    int bars_since_vol_shock_bull;
    int bars_since_vol_shock_bear;

public:
    CHarvestManager(string symbol) {
        m_symbol = symbol;
        m_lastBarTime = 0;
        bars_since_asian_sweep_high = 999;
        bars_since_asian_sweep_low  = 999;
        bars_since_local_sweep_high = 999;
        bars_since_local_sweep_low  = 999;
        bars_since_vol_shock_bull   = 999;
        bars_since_vol_shock_bear   = 999;

        if     (_Period == PERIOD_M15) m_macro_tf = PERIOD_H1;
        else if(_Period == PERIOD_H1)  m_macro_tf = PERIOD_H4;
        else if(_Period == PERIOD_H4)  m_macro_tf = PERIOD_D1;
        else if(_Period == PERIOD_D1)  m_macro_tf = PERIOD_W1;
        else                           m_macro_tf = PERIOD_H4;

        int mult_h4 = PeriodSeconds(PERIOD_H4) / PeriodSeconds(_Period);
        if(mult_h4 == 0) mult_h4 = 1;
        int mult_d1 = PeriodSeconds(PERIOD_D1) / PeriodSeconds(_Period);
        if(mult_d1 == 0) mult_d1 = 1;

        int synth_ema20_h4 = 20 * mult_h4;
        int synth_ema50_d1 = 50 * mult_d1;
        int synth_atr14_d1 = 14 * mult_d1;
        int synth_adx14_d1 = 14 * mult_d1;

        m_logger      = new CMLDataLogger(m_symbol);
        // m_exit_logger = new CExitDataLogger(m_symbol);

        hma_entry_handle     = iCustom(m_symbol, _Period, "HMA50", InpHMA_Entry_Period);
        hma_exit_handle      = iCustom(m_symbol, _Period, "HMA50", InpHMA_Exit_Period);
        fast_hma_exit_handle = iCustom(m_symbol, _Period, "HMA50", InpFastHMA_Exit_Period);
        rsi_handle           = iRSI(m_symbol, _Period, RsiPeriod, PRICE_CLOSE);
        ribbon_hma10 = iCustom(m_symbol, _Period, "HMA50", 10);
        ribbon_hma21 = iCustom(m_symbol, _Period, "HMA50", 21);
        ribbon_hma50 = iCustom(m_symbol, _Period, "HMA50", 50);
        ribbon_hma100 = iCustom(m_symbol, _Period, "HMA50", 100);
        ribbon_hma200 = iCustom(m_symbol, _Period, "HMA50", 200);
        atr_handle           = iATR(m_symbol, _Period, 14);
        atr100_handle        = iATR(m_symbol, _Period, 100);
        ema50_handle         = iMA(m_symbol, m_macro_tf, 50,  0, MODE_EMA, PRICE_CLOSE);
        ema200_handle        = iMA(m_symbol, m_macro_tf, 200, 0, MODE_EMA, PRICE_CLOSE);
        sma20_handle         = iMA(m_symbol, _Period, 20, 0, MODE_SMA, PRICE_CLOSE);
        std_dev_handle       = iStdDev(m_symbol, _Period, 20, 0, MODE_SMA, PRICE_CLOSE);
        synth_ema20_h4_handle = iMA(m_symbol, _Period, synth_ema20_h4, 0, MODE_EMA, PRICE_CLOSE);
        synth_ema50_d1_handle = iMA(m_symbol, _Period, synth_ema50_d1, 0, MODE_EMA, PRICE_CLOSE);
        atr200_handle         = iATR(m_symbol, _Period, 200);
        synth_atr_d1_handle   = iATR(m_symbol, _Period, synth_atr14_d1);
        synth_adx_d1_handle   = iADX(m_symbol, _Period, synth_adx14_d1);

        if(hma_entry_handle == INVALID_HANDLE || hma_exit_handle == INVALID_HANDLE || fast_hma_exit_handle == INVALID_HANDLE ||
           rsi_handle == INVALID_HANDLE || atr_handle == INVALID_HANDLE || atr100_handle == INVALID_HANDLE || std_dev_handle == INVALID_HANDLE ||
           synth_ema20_h4_handle == INVALID_HANDLE || atr200_handle == INVALID_HANDLE || synth_atr_d1_handle == INVALID_HANDLE ||
           synth_adx_d1_handle == INVALID_HANDLE || synth_ema50_d1_handle == INVALID_HANDLE || ribbon_hma10 == INVALID_HANDLE || ribbon_hma21 == INVALID_HANDLE || ribbon_hma50 == INVALID_HANDLE || ribbon_hma100 == INVALID_HANDLE || ribbon_hma200 == INVALID_HANDLE)
        {
            PrintFormat("ERROR CRITICO: Indicadores no inicializados para %s.", m_symbol);
        } else {
            PrintFormat("OK: CHarvestManager inicializado para %s.", m_symbol);
            if(m_symbol == _Symbol) {
                ChartIndicatorAdd(0, 0, ribbon_hma10);
                ChartIndicatorAdd(0, 0, ribbon_hma21);
                ChartIndicatorAdd(0, 0, ribbon_hma50);
                ChartIndicatorAdd(0, 0, ribbon_hma100);
                ChartIndicatorAdd(0, 0, ribbon_hma200);
            }
        }
    }

    ~CHarvestManager() {
        delete m_logger;
        // delete m_exit_logger;
        IndicatorRelease(hma_entry_handle);
        IndicatorRelease(hma_exit_handle);
        IndicatorRelease(fast_hma_exit_handle);
        IndicatorRelease(rsi_handle);
        IndicatorRelease(ribbon_hma10);
        IndicatorRelease(ribbon_hma21);
        IndicatorRelease(ribbon_hma50);
        IndicatorRelease(ribbon_hma100);
        IndicatorRelease(ribbon_hma200);
        IndicatorRelease(atr_handle);
        IndicatorRelease(atr100_handle);
        IndicatorRelease(ema50_handle);
        IndicatorRelease(ema200_handle);
        IndicatorRelease(sma20_handle);
        IndicatorRelease(std_dev_handle);
        IndicatorRelease(synth_adx_d1_handle);
        IndicatorRelease(synth_ema20_h4_handle);
        IndicatorRelease(synth_ema50_d1_handle);
        IndicatorRelease(atr200_handle);
        IndicatorRelease(synth_atr_d1_handle);
        ArrayFree(m_scaled_tickets);
    }

    string GetSymbol() const { return m_symbol; }

    double GetPip() {
        return (SymbolInfoInteger(m_symbol, SYMBOL_DIGITS) % 2 == 1) ? 10.0 * SymbolInfoDouble(m_symbol, SYMBOL_POINT) : SymbolInfoDouble(m_symbol, SYMBOL_POINT);
    }

    // HandleTradeTransaction has been removed in favor of strict physical tracking

    void ManageAllPhysicalPositions(
        double hma_entry_0, double hma_entry_1,
        datetime currentBarTime, const MqlRates &r[])
    {
        int total = PositionsTotal();
        for(int i = total - 1; i >= 0; i--) {
            ulong ticket = PositionGetTicket(i);
            if(ticket != 0) {
                if(PositionGetInteger(POSITION_MAGIC) == 777888 && PositionGetString(POSITION_SYMBOL) == m_symbol) {
                    m_logger.UpdateExcursions(ticket, r[1].high, r[1].low);

                    ENUM_POSITION_TYPE pos_type = (ENUM_POSITION_TYPE)PositionGetInteger(POSITION_TYPE);
                    double   open_p   = PositionGetDouble(POSITION_PRICE_OPEN);
                    datetime open_t   = (datetime)PositionGetInteger(POSITION_TIME);
                    
                    double current_price = (pos_type == POSITION_TYPE_BUY) ? SymbolInfoDouble(m_symbol, SYMBOL_BID) : SymbolInfoDouble(m_symbol, SYMBOL_ASK);
                    double raw_profit = (pos_type == POSITION_TYPE_BUY) ? (current_price - open_p) : (open_p - current_price);
                    
                    bool hard_close = false;
                    if(pos_type == POSITION_TYPE_BUY && hma_entry_0 < hma_entry_1) hard_close = true;
                    if(pos_type == POSITION_TYPE_SELL && hma_entry_0 > hma_entry_1) hard_close = true;
                    
                    if(hard_close) {
                        m_logger.CommitTrade(ticket, raw_profit, TimeCurrent(), open_p, current_price, 99999, open_t, (int)pos_type);
                        trade.PositionClose(ticket);
                    }
                }
            }
        }
    }

    void ProcessTick() {
        datetime currentBarTime = iTime(m_symbol, _Period, 0);
        if(currentBarTime == m_lastBarTime || currentBarTime == 0) return;

        double hma_entry[], hma_exit_buf[], rsi_buf[], atr_buf[];
        double ef[], es[], sma20[], std_dev[], ema20_h4[], ema50_d1[], atr100_buf[], atr200_buf[], adx_buf[], atr_d1_buf[];
        double hma10_buf[], hma21_buf[], hma50_buf[], hma100_buf[], hma200_buf[];
        MqlRates rates[];

        ArraySetAsSeries(hma_entry,    true);
        ArraySetAsSeries(hma_exit_buf, true);
        ArraySetAsSeries(rsi_buf,      true);
        ArraySetAsSeries(atr_buf,      true);
        ArraySetAsSeries(ef,           true);
        ArraySetAsSeries(es,           true);
        ArraySetAsSeries(sma20,        true);
        ArraySetAsSeries(std_dev,      true);
        ArraySetAsSeries(ema20_h4,     true);
        ArraySetAsSeries(ema50_d1,     true);
        ArraySetAsSeries(atr100_buf, true);
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
        
        int hma_copied      = CopyBuffer(hma_entry_handle, 0, 0, 60, hma_entry);
        if(hma_copied < 4)   return;
        int hma_exit_copied = CopyBuffer(hma_exit_handle, 0, 0, 3, hma_exit_buf);
        if(hma_exit_copied < 3) return;
        
        if(CopyBuffer(ribbon_hma10, 0, 0, 3, hma10_buf) < 3) return;
        if(CopyBuffer(ribbon_hma21, 0, 0, 3, hma21_buf) < 3) return;
        if(CopyBuffer(ribbon_hma50, 0, 0, 3, hma50_buf) < 3) return;
        if(CopyBuffer(ribbon_hma100, 0, 0, 3, hma100_buf) < 3) return;
        if(CopyBuffer(ribbon_hma200, 0, 0, 3, hma200_buf) < 3) return;
        if(CopyBuffer(rsi_handle,     0, 0, RsiLookbackBars + 1, rsi_buf) < RsiLookbackBars + 1) return;
        if(CopyBuffer(atr_handle,     0, 0, 51, atr_buf)  < 51) return;
        if(CopyBuffer(atr100_handle,  0, 0, 1,  atr100_buf) < 1) return;
        if(CopyBuffer(atr200_handle,  0, 0, 1,  atr200_buf) < 1) return;
        if(CopyBuffer(synth_atr_d1_handle,  0, 0, 1,  atr_d1_buf) < 1) return;
        if(CopyBuffer(sma20_handle,   0, 0, 1,  sma20)    < 1)  return;
        if(CopyBuffer(std_dev_handle, 0, 0, 1,  std_dev)   < 1)  return;

        int macro_shift = iBarShift(m_symbol, m_macro_tf, currentBarTime);
        int h4_shift    = iBarShift(m_symbol, PERIOD_H4,  currentBarTime);
        int d1_shift    = iBarShift(m_symbol, PERIOD_D1,  currentBarTime);
        if(CopyBuffer(ema50_handle,    0, macro_shift, 1, ef)       < 1) return;
        if(CopyBuffer(ema200_handle,   0, macro_shift, 1, es)       < 1) return;
        if(CopyBuffer(synth_ema20_h4_handle, 0, h4_shift, 2, ema20_h4) < 2) return;
        if(CopyBuffer(synth_ema50_d1_handle, 0, d1_shift, 1, ema50_d1) < 1) return;
        
        if(CopyBuffer(synth_adx_d1_handle, 0, d1_shift, 1, adx_buf) < 1) return;
        double macro_adx = adx_buf[0];

        double pip        = GetPip();
        double spread     = 0.0;
        if(pip > 0) spread = (SymbolInfoDouble(m_symbol, SYMBOL_ASK) - SymbolInfoDouble(m_symbol, SYMBOL_BID)) / pip;

        double current_atr = atr_buf[0];

        double fast_hma_k[];
        ArraySetAsSeries(fast_hma_k, true);
        if(CopyBuffer(fast_hma_exit_handle, 0, 0, 4, fast_hma_k) < 4) return;

        double atr_sma50 = 0;
        for(int k=0; k<50; k++) atr_sma50 += atr_buf[k];
        atr_sma50 /= 50.0;

        double mtf_atr_ratio = (atr_d1_buf[0] > 0) ? (current_atr / atr_d1_buf[0]) : 0.0;
        double bollinger_dev = (std_dev[0] > 0) ? ((rates[1].close - sma20[0]) / std_dev[0]) : 0.0;

        ManageAllPhysicalPositions(hma_entry[0], hma_entry[1], currentBarTime, rates);

        bars_since_asian_sweep_high++;
        bars_since_asian_sweep_low++;
        bars_since_local_sweep_high++;
        bars_since_local_sweep_low++;
        bars_since_vol_shock_bull++;
        bars_since_vol_shock_bear++;

        // Variables de Cinta HMA
        double ribbon_arr[5] = {hma10_buf[0], hma21_buf[0], hma50_buf[0], hma100_buf[0], hma200_buf[0]};
        double sum_ribbon = 0.0;
        double max_r = ribbon_arr[0], min_r = ribbon_arr[0];
        for(int k=0; k<5; k++) {
            sum_ribbon += ribbon_arr[k];
            if(ribbon_arr[k] > max_r) max_r = ribbon_arr[k];
            if(ribbon_arr[k] < min_r) min_r = ribbon_arr[k];
        }
        double mean_ribbon = sum_ribbon / 5.0;
        double sq_sum = 0.0;
        for(int k=0; k<5; k++) sq_sum += MathPow(ribbon_arr[k] - mean_ribbon, 2);
        
        double ribbon_spread_stddev = (current_atr > 0) ? (MathSqrt(sq_sum / 5.0) / current_atr) : 0.0;
        double ribbon_compression_atr = (current_atr > 0) ? ((max_r - min_r) / current_atr) : 0.0;
        double price_to_macro_hma_dist = (current_atr > 0) ? ((rates[1].close - hma200_buf[0]) / current_atr) : 0.0;
        
        int spectrum_alignment = 0;
        if(hma10_buf[0] > hma21_buf[0] && hma21_buf[0] > hma50_buf[0] && hma50_buf[0] > hma100_buf[0] && hma100_buf[0] > hma200_buf[0]) spectrum_alignment = 1;
        else if(hma10_buf[0] < hma21_buf[0] && hma21_buf[0] < hma50_buf[0] && hma50_buf[0] < hma100_buf[0] && hma100_buf[0] < hma200_buf[0]) spectrum_alignment = -1;

        MqlDateTime dt;
        TimeToStruct(currentBarTime, dt);

        int gmt_offset = (int)(TimeCurrent() - TimeGMT());
        MqlDateTime dt_utc;
        TimeToStruct(currentBarTime - gmt_offset, dt_utc);

        MqlDateTime dt_start = dt;
        dt_start.hour = 0; dt_start.min = 0; dt_start.sec = 0;
        datetime asian_start = StructToTime(dt_start);
        MqlDateTime dt_end = dt_start; dt_end.hour = 8;
        datetime asian_end = StructToTime(dt_end);
        
        double asian_high = 0.0, asian_low = 0.0;
        int bars_asian = Bars(m_symbol, _Period, asian_start, asian_end);
        if(bars_asian > 0) {
            double ah[], al[];
            if(CopyHigh(m_symbol, _Period, asian_start, asian_end, ah) > 0) {
                asian_high = ah[0];
                for(int k=1; k<ArraySize(ah); k++) if(ah[k] > asian_high) asian_high = ah[k];
            }
            if(CopyLow(m_symbol, _Period, asian_start, asian_end, al) > 0) {
                asian_low = al[0];
                for(int k=1; k<ArraySize(al); k++) if(al[k] < asian_low) asian_low = al[k];
            }
        }
        
        double current_close = rates[1].close; 
        double dist_asian_high_atr = (current_atr > 0 && asian_high > 0) ? MathAbs(asian_high - current_close) / current_atr : 0.0;
        double dist_asian_low_atr  = (current_atr > 0 && asian_low > 0) ? MathAbs(current_close - asian_low) / current_atr : 0.0;
        
        int is_asian_sweep = 0;
        if(asian_high > 0 && asian_low > 0) {
            bool swept_asian_high = (rates[1].high > asian_high) && (rates[1].close <= asian_high) && (rates[1].open <= asian_high);
            bool swept_asian_low  = (rates[1].low < asian_low)   && (rates[1].close >= asian_low)  && (rates[1].open >= asian_low);
            if(swept_asian_high) bars_since_asian_sweep_high = 0;
            if(swept_asian_low)  bars_since_asian_sweep_low  = 0;
            if(swept_asian_high && swept_asian_low) is_asian_sweep = 3;
            else if(swept_asian_high) is_asian_sweep = 1;
            else if(swept_asian_low)  is_asian_sweep = -1;
        }

        double local_high = rates[2].high;
        double local_low  = rates[2].low;
        int max_dc = MathMin(60, InpDonchianPeriod + 2);
        for(int k=3; k<max_dc; k++) {
            if(rates[k].high > local_high) local_high = rates[k].high;
            if(rates[k].low < local_low)   local_low  = rates[k].low;
        }
        
        bool swept_local_high = (rates[1].high > local_high) && (rates[1].close <= local_high) && (rates[1].open <= local_high);
        bool swept_local_low  = (rates[1].low < local_low)   && (rates[1].close >= local_low)  && (rates[1].open >= local_low);
        if(swept_local_high) bars_since_local_sweep_high = 0;
        if(swept_local_low)  bars_since_local_sweep_low  = 0;

        double tick_vol_zscore = 0.0;
        if(ArraySize(rates) >= 22) {
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
        double candle_dominance = (candle_range > 0) ? (candle_body / candle_range) : 0.0;
        
        // Phase 33: VWMA Z-Score
        double sum_vol = 0.0;
        double sum_vol_price = 0.0;
        for(int k=1; k<=20; k++) {
            sum_vol += (double)rates[k].tick_volume;
            sum_vol_price += rates[k].close * (double)rates[k].tick_volume;
        }
        double vwma_20 = (sum_vol > 0) ? (sum_vol_price / sum_vol) : rates[1].close;
        double vwma_z_score = (std_dev[0] > 0) ? ((current_close - vwma_20) / std_dev[0]) : 0.0;
        
        // Phase 33: Fract Diff Return (Log-Return 10 periodos)
        double fract_diff_return = (rates[11].close > 0) ? MathLog(rates[1].close / rates[11].close) : 0.0;
        
        // Phase 33: Cross Volatility Regime
        double cross_vol_regime = (atr100_buf[0] > 0) ? (current_atr / atr100_buf[0]) : 1.0;

        // Phase 35: Geometric Alpha Polish (TWAP Z-Score & Breakout Velocity) - Optimizada
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

        bool is_bullish = (rates[1].close > rates[1].open);
        bool is_bearish = (rates[1].close < rates[1].open);
        if(tick_vol_zscore > 0.75 && is_bullish) bars_since_vol_shock_bull = 0;
        if(tick_vol_zscore > 0.75 && is_bearish) bars_since_vol_shock_bear = 0;

        // =====================================================================
        // LEY ABSOLUTA: RUPTURA ESTRICTA DE PRECIO VS HMA
        // =====================================================================
        bool triggerBUY  = false;
        bool triggerSELL = false;

        // NUEVA LOGICA ESTRICTA DE CRUCE PRECIO vs HMA_ENTRY (Cuerpo Fisico + Telemetria)
        bool cross_up = false;
        if (rates[1].open < hma_entry[1] && rates[1].close > hma_entry[1] && rates[2].close < hma_entry[2] && hma_entry[2] < hma_entry[3]) {
            PrintFormat("LONG TRIGGER | Vela 2 Close: %f | Vela 1 Open: %f | Vela 1 Close: %f | HMA_ENTRY[3]: %f | HMA_ENTRY[2]: %f | HMA_ENTRY[1]: %f", rates[2].close, rates[1].open, rates[1].close, hma_entry[3], hma_entry[2], hma_entry[1]);
            cross_up = true;
        }
        
        bool cross_dn = false;
        if (rates[1].open > hma_entry[1] && rates[1].close < hma_entry[1] && rates[2].close > hma_entry[2] && hma_entry[2] > hma_entry[3]) {
            PrintFormat("SHORT TRIGGER | Vela 2 Close: %f | Vela 1 Open: %f | Vela 1 Close: %f | HMA_ENTRY[3]: %f | HMA_ENTRY[2]: %f | HMA_ENTRY[1]: %f", rates[2].close, rates[1].open, rates[1].close, hma_entry[3], hma_entry[2], hma_entry[1]);
            cross_dn = true;
        }

        
        triggerBUY  = cross_up;
        triggerSELL = cross_dn;
        
        // HMA Normalized Angle Hard Filter
        double hma_norm_angle = Calculate_HMA_Normalized_Angle(hma_entry[2], hma_entry[3], current_atr);
        
        double required_angle = 5.0;
        
        if(triggerBUY || triggerSELL) {
            if(MathAbs(hma_norm_angle) < required_angle) {
                PrintFormat("FILTRO HARD: Angulo HMA %.2f menor a %.1f. ABORTANDO SENAL (Whipsaw lateral).", hma_norm_angle, required_angle);
                triggerBUY = false;
                triggerSELL = false;
            }
        }


        if(!(triggerBUY || triggerSELL)) {
            m_lastBarTime = currentBarTime;
            return;
        }

        // Lógica de escalado dinámico de spread
        double max_allowed_spread = MaxSpreadPips;
        string symbol_upper = m_symbol;
        StringToUpper(symbol_upper);
        bool is_metal = (StringFind(symbol_upper, "XAU") >= 0 || StringFind(symbol_upper, "GOLD") >= 0 || StringFind(symbol_upper, "XAG") >= 0);
        
        if(is_metal) {
            max_allowed_spread = InpMaxSpreadPips_Metals;
        }
        
        if(spread > max_allowed_spread) {
            m_lastBarTime = currentBarTime; return;
        }

        double minDev = current_atr * (AntiNoiseATRPct / 100.0);
        if(MathAbs(rates[0].close - hma_entry[0]) < minDev) {
            m_lastBarTime = currentBarTime; return;
        }

        if(candle_range > (current_atr * InpMaxSignalBarATR)) {
            m_lastBarTime = currentBarTime; return;
        }

        int signalType = triggerBUY ? 0 : 1;

        bool has_opposite_runner = false;
        for(int i = 0; i < PositionsTotal(); i++) {
            if(PositionGetSymbol(i) == m_symbol && PositionGetInteger(POSITION_MAGIC) == 777888) {
                long pType = PositionGetInteger(POSITION_TYPE);
                if(signalType == 0 && pType == POSITION_TYPE_SELL) has_opposite_runner = true;
                if(signalType == 1 && pType == POSITION_TYPE_BUY) has_opposite_runner = true;
            }
        }

        if(has_opposite_runner) {
            Print("EMBARGO DIRECCIONAL PERMANENTE: Bloqueando SAR. Dejando que la posicion opuesta respire en ", m_symbol);
            m_lastBarTime = currentBarTime;
            return;
        }

        double ask = SymbolInfoDouble(m_symbol, SYMBOL_ASK);
        double bid = SymbolInfoDouble(m_symbol, SYMBOL_BID);
        double sl = (signalType == 0) ? (ask - 5.0 * current_atr) : (bid + 5.0 * current_atr);
        if(sl == 0.0) { m_lastBarTime = currentBarTime; return; }

        double entry_price = (signalType == 0) ? ask : bid;
        double slDist = (signalType == 0) ? (entry_price - sl) : (sl - entry_price);
        if(slDist <= 0.0) { m_lastBarTime = currentBarTime; return; }

        double sl_dist_atr = (current_atr > 0) ? (slDist / current_atr) : 0.0;
        if(sl_dist_atr > InpMaxSLATR) { m_lastBarTime = currentBarTime; return; }

        double z_score = (std_dev[0] > 0) ? ((current_close - sma20[0]) / std_dev[0]) : 0.0;

        double atr_sum = 0.0;
        for(int k = 0; k < 10; k++) atr_sum += atr_buf[k];
        double atr_norm = (atr_sum > 0) ? (current_atr / (atr_sum / 10.0)) : 1.0;

        double rsi_extreme = 50.0;
        int bars_since = RsiLookbackBars;
        CalcRsiExtremeMetrics(rsi_handle, RsiLookbackBars, signalType, rsi_extreme, bars_since);

        double hma_slope = (current_atr > 0) ? ((hma_entry[0] - hma_entry[1]) / current_atr) : 0.0;
        double hma_accel_feat = CalcHmaAcceleration(hma_entry_handle, current_atr);
        double breakout_force = CalcBreakoutForceATR(current_close, hma_entry[0], current_atr);

        int trend_align = (ef[0] > es[0]) ? 1 : -1;
        double dist_macro = CalcDistToMacroEMA(current_close, es[0], current_atr);

        int pb_duration = 0; double pb_depth = 0.0;
        CalcPullbackMetrics(m_symbol, hma_entry_handle, LookbackBars, current_atr, pb_duration, pb_depth);

        int h = dt_utc.hour;
        int session_time = 1;
        if(h >= 13) session_time = (h <= 14) ? 0 : ((h <= 20) ? 3 : 1);
        else if(h >= 7) session_time = 2;

        int h4_trend_align = -1;
        if(ema20_h4[0] > ema20_h4[1] && signalType == 0) h4_trend_align = 1;
        else if(ema20_h4[0] <= ema20_h4[1] && signalType == 1) h4_trend_align = 1;

        double atr_ratio_high = (atr200_buf[0] > 0) ? (current_atr / atr200_buf[0]) : 1.0;
        double hma_distance_ema = (pip > 0) ? ((current_close - es[0]) / pip) : 0.0;

        double hma_vel = (hma_entry[0] - hma_entry[1]) / current_atr;
        double vel_prev_k = (hma_entry[1] - hma_entry[2]) / current_atr;
        double hma_accel_v2 = hma_vel - vel_prev_k;
        double hma_jerk_val = hma_accel_v2 - (vel_prev_k - ((hma_entry[2] - hma_entry[3]) / current_atr));

        int energy_accum = 0;
        bool stop_count = false;
        for(int k = 1; k < 60; k++) {
            if(!stop_count) {
                if(signalType == 0 && rates[k].close < hma_entry[k]) energy_accum++;
                else if(signalType == 1 && rates[k].close > hma_entry[k]) energy_accum++;
                else stop_count = true;
            }
        }

        m_lastBarTime = currentBarTime;  // Bloquear antes de lanzar orden

        // Métricas secundarias que dependen de signalType
        int count_consistent_buy  = CountConsistentlyBelowHMA(rates, hma_entry, 3);
        int count_consistent_sell = CountConsistentlyAboveHMA(rates, hma_entry, 3);
        bool rsi_oversold   = WasRSIOversold(rsi_buf, 1, RsiLookbackBars, (double)RsiOversoldLevel);
        bool rsi_overbought = WasRSIOverbought(rsi_buf, 1, RsiLookbackBars, (double)RsiOverboughtLevel);

        double min_volume = SymbolInfoDouble(m_symbol, SYMBOL_VOLUME_MIN);

        if(trade.PositionOpen(m_symbol, (ENUM_ORDER_TYPE)signalType, min_volume, entry_price, sl, 0.0, "HMA_ML")) {
            ulong pos_ticket = trade.ResultDeal();
            double real_entry = trade.ResultPrice();
            if(real_entry <= 0.0) real_entry = entry_price;

            double real_slDist = (signalType == 0) ? (real_entry - sl) : (sl - real_entry);
            if(real_slDist <= 0.0) real_slDist = slDist;
            
            double real_sl_pips = (pip > 0) ? (real_slDist / pip) : 0.0;

            MarketSnapshot snap;
            ZeroMemory(snap);
            snap.ticket = pos_ticket;
            snap.time = TimeCurrent();
            snap.signal_type = signalType;
            snap.highest_price = real_entry;
            snap.lowest_price = real_entry;
            snap.entry_price_tracked = real_entry;
            snap.entry_atr_tracked = current_atr;
            snap.z_score_close = z_score;
            snap.atr_normalized = atr_norm;
            snap.rsi_val = rsi_buf[0];
            snap.rsi_extreme_val = rsi_extreme;
            snap.bars_since_extreme = bars_since;
            snap.hma_norm_angle = hma_norm_angle;
            snap.hma_slope_pct = hma_slope;
            snap.hma_acceleration = hma_accel_feat;
            snap.breakout_force_atr = breakout_force;
            snap.regime_consistency_count = (signalType == 0) ? count_consistent_buy : count_consistent_sell;
            snap.rsi_exhausted = (signalType == 0) ? (int)rsi_oversold : (int)rsi_overbought;
            snap.trend_alignment = trend_align;
            snap.dist_to_macro_ema = dist_macro;
            snap.macro_adx = macro_adx;
            snap.pullback_duration = pb_duration;
            snap.pullback_max_depth_pct = pb_depth;
            snap.sl_distance_atr = (current_atr > 0) ? (real_slDist / current_atr) : 0.0;
            snap.ribbon_compression_atr = ribbon_compression_atr;
            snap.spectrum_alignment = spectrum_alignment;
            snap.price_to_macro_hma_dist = price_to_macro_hma_dist;
            snap.ribbon_spread_stddev = ribbon_spread_stddev;
            snap.sl_dist_price = real_slDist;
            snap.spread_pips = spread;
            snap.sl_pips_reales = real_sl_pips;
            snap.hour_of_day = dt_utc.hour;
            snap.session_time = session_time;
            snap.h4_trend_align = h4_trend_align;
            snap.vol_spread_ratio = (atr_sma50 > 0) ? (current_atr / atr_sma50) : 1.0;
            snap.atr_ratio_high = atr_ratio_high;
            snap.rsi_slope_10 = rsi_buf[0] - rsi_buf[10];
            snap.spread_impact_ratio = (real_sl_pips > 0) ? (spread / real_sl_pips) : 0.0;
            snap.hma_distance_ema = hma_distance_ema;
            snap.breakout_body_ratio = (candle_range > 0) ? (candle_body / candle_range) : 0.0;
            snap.day_of_week = dt_utc.day_of_week;
            snap.hma_velocity = hma_vel;
            snap.hma_acceleration_raw = hma_accel_v2;
            snap.hma_jerk = hma_jerk_val;
            snap.energy_accumulation = energy_accum;
            snap.bars_since_asian_sweep = (signalType == 0) ? bars_since_asian_sweep_low : bars_since_asian_sweep_high;
            snap.bars_since_local_sweep = (signalType == 0) ? bars_since_local_sweep_low : bars_since_local_sweep_high;
            snap.bars_since_vol_shock = (signalType == 0) ? bars_since_vol_shock_bull : bars_since_vol_shock_bear;
            snap.dist_asian_high_atr = dist_asian_high_atr;
            snap.dist_asian_low_atr = dist_asian_low_atr;
            snap.is_asian_sweep = is_asian_sweep;
            snap.tick_volume_zscore = tick_vol_zscore;
            snap.spread_expansion_ratio = spread_exp_ratio;
            snap.candle_dominance = candle_dominance;
            snap.mtf_atr_ratio = mtf_atr_ratio;
        
            snap.cross_vol_regime = cross_vol_regime;
            snap.vwma_z_score = vwma_z_score;
            snap.fract_diff_return = fract_diff_return;
            
            // Phase 35
            snap.twap_z_score = twap_z_score;
            snap.breakout_velocity = breakout_velocity;

            // Phase 42
            snap.atr_ratio = (atr100_buf[0] > 0) ? (current_atr / atr100_buf[0]) : 1.0;
            snap.bollinger_band_width = (sma20[0] > 0) ? ((4.0 * std_dev[0]) / sma20[0]) : 0.0;
            snap.dist_synth_h4_ema = (current_atr > 0) ? ((current_close - ema20_h4[0]) / current_atr) : 0.0;
            snap.dist_synth_d1_ema = (current_atr > 0) ? ((current_close - ema50_d1[0]) / current_atr) : 0.0;
            
            double trigger_rejection_tail = 0.0;
            if(candle_range > 0) {
                if(signalType == 0) trigger_rejection_tail = (MathMin(rates[1].open, rates[1].close) - rates[1].low) / candle_range;
                else trigger_rejection_tail = (rates[1].high - MathMax(rates[1].open, rates[1].close)) / candle_range;
            }
            snap.trigger_rejection_tail = trigger_rejection_tail;
            snap.bollinger_dev = bollinger_dev;

            m_logger.RecordSignal(snap);
        }
    }
};

//+------------------------------------------------------------------+
//| Variables Globales                                               |
//+------------------------------------------------------------------+
CHarvestManager *Managers[];

//+------------------------------------------------------------------+
//| OnInit                                                           |
//+------------------------------------------------------------------+
int OnInit()
{
    trade.SetExpertMagicNumber(777888);
    g_VerticalBarrierBars = (int)(InpHMA_Exit_Period * 1.5);

    string symbols[];
    int count = SplitString(InpHarvestSymbols, ",", symbols);
    if(count == 0) {
        Print("ERROR: No se definieron simbolos para harvest.");
        return INIT_FAILED;
    }

    int valid_managers = 0;
    ArrayResize(Managers, count);
    for(int i=0; i<count; i++) {
        ResetLastError();
        if(SymbolSelect(symbols[i], true)) {
            FileDelete("Struct_Dataset_" + symbols[i] + ".csv", FILE_COMMON);
            FileDelete("Struct_Exit_Dataset_" + symbols[i] + ".csv", FILE_COMMON);
            Managers[valid_managers] = new CHarvestManager(symbols[i]);
            valid_managers++;
        } else {
            PrintFormat("[WARN] Símbolo %s inválido o no soportado por el Broker/Tester. Ignorando.", symbols[i]);
        }
    }

    if(valid_managers == 0) {
        Print("ERROR CRÍTICO: Ningún símbolo válido para operar.");
        return INIT_FAILED;
    }

    ArrayResize(Managers, valid_managers);

    EventSetMillisecondTimer(500);
    PrintFormat("[INIT] Harvester Listo. Simbolos Activos: %d / %d | Timer: 500ms", valid_managers, count);

    return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| OnDeinit                                                         |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
    EventKillTimer();
    for(int i=0; i<ArraySize(Managers); i++) {
        if(CheckPointer(Managers[i]) != POINTER_INVALID) {
            delete Managers[i];
        }
    }
    ArrayFree(Managers);
}

//+------------------------------------------------------------------+
//| OnTimer                                                          |
//+------------------------------------------------------------------+
void OnTimer()
{
    for(int i=0; i<ArraySize(Managers); i++) {
        if(CheckPointer(Managers[i]) != POINTER_INVALID) {
            Managers[i].ProcessTick();
        }
    }
    CleanTicketStates();
}

//+------------------------------------------------------------------+
//| OnTradeTransaction - ELIMINADO PARA CONTROL FISICO ESTRICTO      |
//+------------------------------------------------------------------+
