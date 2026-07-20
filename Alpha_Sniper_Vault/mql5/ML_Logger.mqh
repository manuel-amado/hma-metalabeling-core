//+------------------------------------------------------------------+
//|                                                    ML_Logger.mqh |
//|          Motor de Persistencia HPC para Meta-Labeling v2.3       |
//|          Fase 23: Multi-Concurrencia | Multi-Símbolo Desacoplado |
//|          Sin trades virtuales — todas las posiciones son reales   |
//|          Autor: Manuel                                            |
//+------------------------------------------------------------------+
#property strict

// Forward declaration removed

//+------------------------------------------------------------------+
//| MarketSnapshot — Feature snapshot de una posicion real           |
//| Soporta N posiciones concurrentes (arrays dinamicos)             |
//+------------------------------------------------------------------+
struct MarketSnapshot {
    // Metadatos
    ulong    ticket;
    datetime time;
    int      signal_type;
    // Features X: Estacionarias
    double   z_score_close;
    double   atr_normalized;
    // Features X: Cinematicas
    double   rsi_val;
    double   rsi_extreme_val;
    int      bars_since_extreme;
    // Features X: Fisicas
    double   hma_norm_angle;
    double   hma_slope_pct;
    double   hma_acceleration;
    double   breakout_force_atr;
    // Features X: Contexto
    int      trend_alignment;
    double   dist_to_macro_ema;
    double   macro_adx;
    int      pullback_duration;
    double   pullback_max_depth_pct;
    // Features X: Riesgo y Microestructura
    double   sl_distance_atr;
    double   sl_dist_price;     // Distancia SL en precio (base para RR)
    double   spread_pips;
    double   sl_pips_reales;
    int      hour_of_day;
    // Features X: Feature Engineering Fase 2
    int      session_time;
    int      h4_trend_align;
    double   vol_spread_ratio;
    // Features X: Alpha Search Fase 2
    double   atr_ratio_high;
    double   rsi_slope_10;
    double   spread_impact_ratio;
    double   hma_distance_ema;
    double   breakout_body_ratio;
    int      day_of_week;
    // Features X: Cinematica HMA Fase 3
    double   hma_velocity;
    double   hma_acceleration_raw;
    double   hma_jerk;
    int      energy_accumulation;
    int      bars_since_asian_sweep;
    int      bars_since_local_sweep;
    int      bars_since_vol_shock;
    // Features X: Phase 8 - Microestructura y Liquidez
    double   dist_asian_high_atr;
    double   dist_asian_low_atr;
    int      is_asian_sweep;
    double   tick_volume_zscore;
    double   spread_expansion_ratio;
    double   candle_dominance;
    // Features X: Phase 10.6 - Soft Features (Geometria temporal dinamica)
    int      regime_consistency_count;
    int      rsi_exhausted;
    // Features X: Phase 14 - Advanced Robustness
    double   mtf_atr_ratio;
    double   trigger_rejection_tail;
    double   bollinger_dev;
    // Features X: Phase 33 - Institutional Math
    double   cross_vol_regime;
    double   vwma_z_score;
    double   fract_diff_return;
    // Features X: Phase 35 - Geometric Alpha Polish
    double   twap_z_score;
    double   breakout_velocity;
    // Features X: Phase 42 - Synthetic Fractal & Volatility
    double   atr_ratio;
    double   bollinger_band_width;
    double   dist_synth_h4_ema;
    double   dist_synth_d1_ema;
    // Features X: Phase 57 - Continuous HMA Spectrum
    double   ribbon_compression_atr;
    double   spectrum_alignment;
    double   price_to_macro_hma_dist;
    double   ribbon_spread_stddev;
    // --- Lifecycle Tracking ---
    double   highest_price;
    double   lowest_price;
    double   entry_price_tracked;
    double   entry_atr_tracked;
    // Targets Y (rellenados al cierre — LEAKAGE si se usan como X)
    int      bars_in_trade;
    double   mae_pct;
    double   mfe_pct;
    double   mae_atr;           // Excursion adversa en unidades ATR
    double   mfe_atr;           // Excursion favorable en unidades ATR
    double   realized_rr;       // = (PrecCierre - PrecApertura) / |PrecAp - SL|
    double   exact_return_pct;
    int      label;
};

//+------------------------------------------------------------------+
//| CMLDataLogger — Motor de Persistencia principal                  |
//| Soporta multiples posiciones concurrentes via array dinamico     |
//+------------------------------------------------------------------+
class CMLDataLogger {
private:
    string         m_symbol;
    string         m_filename;
    int            m_file_handle;
    MarketSnapshot m_active_signals[];   // Una entrada por posicion viva

public:
    CMLDataLogger(string symbol) : m_symbol(symbol) {
        m_filename = "Struct_Dataset_" + m_symbol + ".csv";
        m_file_handle = FileOpen(m_filename,
                                 FILE_READ|FILE_WRITE|FILE_CSV|FILE_COMMON|FILE_ANSI, ',');
        if(m_file_handle != INVALID_HANDLE) {
            if(FileSize(m_file_handle) == 0) {
                string h1 = "Symbol,Ticket,Time,Signal,Z_Score,ATR_Norm,RSI,RSI_Extreme,Bars_Since_Ext,HMA_Normalized_Angle,HMA_Slope_Pct,HMA_Accel,Breakout_Force_ATR,Trend_Align,Dist_Macro_EMA,Macro_ADX,Pullback_Dur,Pullback_Depth_Pct,SL_Dist_ATR,Spread_Pips,SL_Pips_Reales,Hour,Session_Time,H4_Trend_Align,Vol_Spread_Ratio,ATR_Ratio_High,RSI_Slope_10,Spread_Impact_Ratio,HMA_Distance_EMA,Breakout_Body_Ratio,Day_Of_Week,HMA_Velocity,HMA_Acceleration,HMA_Jerk,Energy_Accumulation,Bars_Since_Asian_Sweep,Bars_Since_Local_Sweep,Bars_Since_Vol_Shock,Dist_Asian_High_ATR,Dist_Asian_Low_ATR,Is_Asian_Sweep,Tick_Volume_ZScore,Spread_Expansion_Ratio,Candle_Dominance,Regime_Consistency_Count,RSI_Exhausted,MTF_ATR_Ratio,Trigger_Rejection_Tail,Bollinger_Dev,Cross_Vol_Regime,VWMA_Z_Score,Fract_Diff_Return,TWAP_Z_Score,Breakout_Velocity,ATR_Ratio,Bollinger_Band_Width,Dist_Synth_H4_EMA,Dist_Synth_D1_EMA,Ribbon_Compression_ATR,Spectrum_Alignment,Price_to_Macro_HMA_Dist,Ribbon_Spread_StdDev,Bars_In_Trade,MAE_Pct,MFE_Pct,MAE_ATR,MFE_ATR,Realized_RR,Return_Pct,Label\n";
                FileWriteString(m_file_handle, h1);
                FileFlush(m_file_handle);
            }
            FileSeek(m_file_handle, 0, SEEK_END);
        } else {
            Print("ERROR CRITICO: No se pudo abrir CSV. Error: ", GetLastError());
        }
    }

    ~CMLDataLogger() {
        if(m_file_handle != INVALID_HANDLE) FileClose(m_file_handle);
    }

    // Registra el snapshot de entrada de una posicion recien abierta.
    // Se llama UNA VEZ por posicion, justo despues del OrderSend exitoso.
    void RecordSignal(MarketSnapshot &snap) {
        int size = ArraySize(m_active_signals);
        ArrayResize(m_active_signals, size + 1, 500);
        m_active_signals[size] = snap;
    }

    void UpdateExcursions(ulong ticket, double current_high, double current_low) {
        int size = ArraySize(m_active_signals);
        for(int i = 0; i < size; i++) {
            if(m_active_signals[i].ticket == ticket) {
                if(current_high > m_active_signals[i].highest_price) m_active_signals[i].highest_price = current_high;
                if(current_low < m_active_signals[i].lowest_price)   m_active_signals[i].lowest_price = current_low;
                break;
            }
        }
    }

    //+------------------------------------------------------------------+
    //| CommitTrade: busca el snapshot por position_id, calcula RR/MAE/  |
    //| MFE y escribe la fila completa al CSV. Elimina el snapshot del   |
    //| array activo. Llamado desde OnTradeTransaction (DEAL_ENTRY_OUT). |
    //+------------------------------------------------------------------+
    void CommitTrade(ulong position_id, double profit, datetime close_time,
                     double open_price, double close_price, int max_bars,
                     datetime open_time, int signal_type)
    {
        int  size  = ArraySize(m_active_signals);
        bool found = false;
        for(int i = 0; i < size; i++) {
            if(!found) {
                if(m_active_signals[i].ticket == position_id) {
                    found = true;
                    _FillAndCommit(i, profit, close_time, open_price, close_price,
                                   max_bars, open_time, signal_type);
                    ArrayRemove(m_active_signals, i, 1);
                }
            }
        }
        if(!found) {
            PrintFormat("[WARN] CommitTrade: no se encontro snapshot para posicion %I64u", position_id);
        }
    }

private:
    //+------------------------------------------------------------------+
    //| _FillAndCommit: calcula metricas de cierre y escribe a CSV       |
    //| Realized_RR = (precio_cierre - precio_apertura) / |ap - SL|     |
    //| MAE/MFE en porcentaje sobre el precio de entrada                 |
    //+------------------------------------------------------------------+
    void _FillAndCommit(int idx, double profit, datetime close_time,
                        double open_price, double close_price, int max_bars,
                        datetime open_time, int signal_type)
    {
        // Return porcentual simple (positivo = ganancia para la direccion)
        double return_pct = ((close_price - open_price) / open_price) * 100.0;
        if(signal_type == 1) return_pct *= -1.0;

        // Duracion en barras
        int bar_open     = iBarShift(m_symbol, Period(), open_time);
        int bar_close    = iBarShift(m_symbol, Period(), close_time);
        int bars_elapsed = MathAbs(bar_open - bar_close);

        // Etiqueta Triple Barrera: 1=bueno(profit+tiempo), 0=malo(loss+tiempo), -1=timeout
        int lbl = -1;
        if(profit > 0 && bars_elapsed < max_bars)  lbl = 1;
        if(profit <= 0 && bars_elapsed < max_bars) lbl = 0;

        // MAE / MFE estrictos calculados con Lifecycle Tracking
        double mae_atr = 0.0;
        double mfe_atr = 0.0;
        double mae_pct = 0.0;
        double mfe_pct = 0.0;
        double mfe_price = 0.0;
        
        double entry = m_active_signals[idx].entry_price_tracked;
        double atr_val = m_active_signals[idx].entry_atr_tracked;
        double h_price = m_active_signals[idx].highest_price;
        double l_price = m_active_signals[idx].lowest_price;

        if(signal_type == 0) { // BUY
            mfe_price = h_price - entry;
            double mae_price = entry - l_price;
            
            if(atr_val > 0) {
                mfe_atr = mfe_price / atr_val;
                mae_atr = mae_price / atr_val; // Distancia en contra absoluta
            }
            if(entry > 0) {
                mfe_pct = (mfe_price / entry) * 100.0;
                mae_pct = (-mae_price / entry) * 100.0; // Negativo para indicar contra
            }
        } else { // SELL
            mfe_price = entry - l_price;
            double mae_price = h_price - entry;
            
            if(atr_val > 0) {
                mfe_atr = mfe_price / atr_val;
                mae_atr = mae_price / atr_val;
            }
            if(entry > 0) {
                mfe_pct = (mfe_price / entry) * 100.0;
                mae_pct = (-mae_price / entry) * 100.0;
            }
        }

        // Notificar al exit_logger eliminado

        // Realized RR estrictamente en unidades de riesgo inicial (R)
        double sl_dist = m_active_signals[idx].sl_dist_price;
        double realized_rr = 0.0;
        if(sl_dist > 0) {
            if(signal_type == 0) realized_rr = (close_price - open_price) / sl_dist;
            else                 realized_rr = (open_price - close_price) / sl_dist;
        }

        m_active_signals[idx].bars_in_trade    = bars_elapsed;
        m_active_signals[idx].mae_pct          = mae_pct;
        m_active_signals[idx].mfe_pct          = mfe_pct;
        m_active_signals[idx].mae_atr          = mae_atr;
        m_active_signals[idx].mfe_atr          = mfe_atr;
        m_active_signals[idx].realized_rr      = realized_rr;
        m_active_signals[idx].exact_return_pct = return_pct;
        m_active_signals[idx].label            = lbl;

        _WriteToFile(m_active_signals[idx]);
    }

    public:
    void ReconcileClosedPositions(int max_bars) {
        int size = ArraySize(m_active_signals);
        for(int i = size - 1; i >= 0; i--) {
            ulong tkt = m_active_signals[i].ticket;
            if(!PositionSelectByTicket(tkt)) {
                if(HistorySelectByPosition(tkt)) {
                    int deals = HistoryDealsTotal();
                    double profit = 0;
                    double close_price = 0;
                    datetime close_time = 0;
                    bool out_deal_found = false;
                    for(int d = 0; d < deals; d++) {
                        ulong d_ticket = HistoryDealGetTicket(d);
                        if(HistoryDealGetInteger(d_ticket, DEAL_ENTRY) == DEAL_ENTRY_OUT || HistoryDealGetInteger(d_ticket, DEAL_ENTRY) == DEAL_ENTRY_INOUT) {
                            profit += HistoryDealGetDouble(d_ticket, DEAL_PROFIT) + HistoryDealGetDouble(d_ticket, DEAL_SWAP) + HistoryDealGetDouble(d_ticket, DEAL_COMMISSION);
                            close_price = HistoryDealGetDouble(d_ticket, DEAL_PRICE);
                            close_time = (datetime)HistoryDealGetInteger(d_ticket, DEAL_TIME);
                            out_deal_found = true;
                        }
                    }
                    if(out_deal_found) {
                        CommitTrade(tkt, profit, close_time, m_active_signals[i].entry_price_tracked, close_price, max_bars, m_active_signals[i].time, m_active_signals[i].signal_type);
                    }
                }
            }
        }
    }

    private:
    void _WriteToFile(const MarketSnapshot &s) {
        if(m_file_handle == INVALID_HANDLE) return;
        string part1 = StringFormat("%s,%I64u,%s,%d,%f,%f,%f,%f,%d,%f,%f,%f,%f,%d,%f,%f,%d,%f,%f,%f,%f,%d,%d,%d,%f,%f,%f,%f,%f,%f,%d",
            m_symbol, s.ticket, TimeToString(s.time), s.signal_type, s.z_score_close, s.atr_normalized,
            s.rsi_val, s.rsi_extreme_val, s.bars_since_extreme,
            s.hma_norm_angle,
            s.hma_slope_pct, s.hma_acceleration, s.breakout_force_atr,
            s.trend_alignment, s.dist_to_macro_ema, s.macro_adx,
            s.pullback_duration, s.pullback_max_depth_pct,
            s.sl_distance_atr, s.spread_pips, s.sl_pips_reales, s.hour_of_day,
            s.session_time, s.h4_trend_align, s.vol_spread_ratio,
            s.atr_ratio_high, s.rsi_slope_10, s.spread_impact_ratio,
            s.hma_distance_ema, s.breakout_body_ratio, s.day_of_week);

        string part2 = StringFormat(",%f,%f,%f,%d,%d,%d,%d,%f,%f,%d,%f,%f,%f,%d,%d,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f",
            s.hma_velocity, s.hma_acceleration_raw, s.hma_jerk, s.energy_accumulation,
            s.bars_since_asian_sweep, s.bars_since_local_sweep, s.bars_since_vol_shock,
            s.dist_asian_high_atr, s.dist_asian_low_atr, s.is_asian_sweep,
            s.tick_volume_zscore, s.spread_expansion_ratio, s.candle_dominance,
            s.regime_consistency_count, s.rsi_exhausted,
            s.mtf_atr_ratio, s.trigger_rejection_tail, s.bollinger_dev,
            s.cross_vol_regime, s.vwma_z_score, s.fract_diff_return,
            s.twap_z_score, s.breakout_velocity,
            s.atr_ratio, s.bollinger_band_width, s.dist_synth_h4_ema, s.dist_synth_d1_ema,
            s.ribbon_compression_atr, s.spectrum_alignment, s.price_to_macro_hma_dist, s.ribbon_spread_stddev);

        string part3 = StringFormat(",%d,%f,%f,%f,%f,%f,%f,%d\n",
            s.bars_in_trade, s.mae_pct, s.mfe_pct,
            s.mae_atr, s.mfe_atr, s.realized_rr, s.exact_return_pct, s.label);

        FileWriteString(m_file_handle, part1 + part2 + part3);
        FileFlush(m_file_handle);
    }
};

// Exit logging removed for Phase 72