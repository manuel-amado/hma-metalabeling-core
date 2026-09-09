//+------------------------------------------------------------------+
//|                                          Alpha_Sniper_Deploy.mq5 |
//|        Bot de Producción Institucional (Fase 19 Multi-Divisa)    |
//|        Autor: Manuel                                             |
//|        Entradas/Salidas guiadas por FastAPI (XGBoost)            |
//+------------------------------------------------------------------+
#property strict
#property version "2.0"
#property description "Producción Monolítica: Multi-Activo, Concurrencia Direccional y Riesgo Compuesto"

#include <Trade\Trade.mqh>
#include "HMA_FUNCTIONS.mqh"

#import "wininet.dll"
long InternetOpenW(string agent, int access_type, string proxy_name, string proxy_bypass, int flags);
long InternetConnectW(long internet, string server_name, int server_port, string username, string password, int service, int flags, int context);
long HttpOpenRequestW(long connect, string verb, string object_name, string version, string referer, string accept_types, int flags, int context);
int HttpSendRequestW(long request, string headers, int headers_length, uchar& optional[], int optional_length);
int InternetReadFile(long file, uchar& buffer[], int num_bytes_to_read, int& number_of_bytes_read);
int InternetCloseHandle(long internet);
#import

#define INTERNET_OPEN_TYPE_PRECONFIG 0
#define INTERNET_SERVICE_HTTP 3

CTrade trade;

//+------------------------------------------------------------------+
//| Parametros de Entrada                                            |
//+------------------------------------------------------------------+

input group "== Portafolio Multi-Divisa =="
input string InpSymbols          = "USDJPY,GBPUSD,EURUSD,EURJPY,XAUUSD,XAGUSD";

input group "== Estrategia HMA =="
input int    HMAPeriod           = 50;
input int    InpHMA_ExitPeriod   = 100;
input int    InpMinBarsToHold    = 3;
input int    LookbackBars        = 7;
input double AntiNoiseATRPct     = 2.0;

input group "== Contexto y Features =="
input int    RsiPeriod           = 14;
input int    RsiLookbackBars     = 15;
input int    RsiOversoldLevel    = 35;
input int    RsiOverboughtLevel  = 65;

input group "== Microestructura =="
input double MaxSpreadPips          = 1.5;  // Ajustado para ECN/Raw spread (Broker Sync)
input double InpMaxSpreadPips_Metals = 35.0; // Spread máximo Metales (Puntos)
input int    InpDonchianPeriod      = 20;

input group "== Gestion de Riesgo =="
input bool   InpUseCompoundInterest = false; // Usar Interés Compuesto (Riesgo Dinámico)
input double InpFixedBalance        = 100000; // Balance Fijo Institucional ($100k)
input double InpRiskPerTrade        = 1.0; // % riesgo por trade (1%)
input double InpMaxGlobalRisk       = 3.0; // % maximo simultaneo (3 trades)
input int    InpMaxPortfolioTrades  = 3;    // Bloqueo global de trades de cuenta
input double InpScaleOutRR          = 1.5;  // RR flotante para Scale-Out parcial (50%)
input double InpRunnerTrailingATR   = 3.0;  // Multiplicador ATR para Trailing Stop del Runner
input int    InpFastHMA_Exit_Period  = 14;  // Periodo HMA rapida de salida (Kinematic Trailing)

int g_VerticalBarrierBars; // Timeout Institucional

// Los Umbrales IA ahora están completamente centralizados en el servidor Python
double EntryThreshold = 0.0001; 
double ExitThreshold  = 0.0001; 

input group "== Filtros Macro / Cisnes Negros =="
input double InpMaxSignalBarATR  = 2.5;
input double InpMaxSLATR         = 3.0;

//+------------------------------------------------------------------+
//| Variables Globales Maestras                                      |
//+------------------------------------------------------------------+
ulong g_scaled_tickets[]; // Scale-Out tracking: tickets que ya han recibido Scale-Out

// Helper: WebRequest to FastAPI
double RequestFastAPI(string endpoint, string json_payload) {
    if(!MQLInfoInteger(MQL_TESTER)) {
        char post[], result[];
        string headers = "Content-Type: application/json"; 
        string url = "http://127.0.0.1:8000" + endpoint;
        
        ArrayResize(result, 0);
        StringToCharArray(json_payload, post, 0, WHOLE_ARRAY, CP_UTF8);
        int size = ArraySize(post);
        if(size > 0 && post[size-1] == 0) ArrayResize(post, size-1);
        
        string res_headers;
        ResetLastError();
        int res = WebRequest("POST", url, headers, 3000, post, result, res_headers);
        
        if(res == 200) {
            string res_str = CharArrayToString(result);
            int idx = StringFind(res_str, "\"probability\":");
            if(idx != -1) {
                string valStr = StringSubstr(res_str, idx + 14);
                int end_idx = StringFind(valStr, "}");
                if(end_idx != -1) valStr = StringSubstr(valStr, 0, end_idx);
                return StringToDouble(valStr);
            }
        } else {
            Print("FastAPI Error: ", res, " | MT5 ErrorCode: ", GetLastError());
        }
        return -1.0;
    } else {
        long hInternet = InternetOpenW("MT5", INTERNET_OPEN_TYPE_PRECONFIG, NULL, NULL, 0);
        if(hInternet == 0) return -1.0;
        
        long hConnect = InternetConnectW(hInternet, "127.0.0.1", 8000, NULL, NULL, INTERNET_SERVICE_HTTP, 0, 0);
        if(hConnect == 0) { InternetCloseHandle(hInternet); return -1.0; }
        
        static int request_counter = 0;
        request_counter++;
        string endpoint_ts = endpoint + "?t=" + IntegerToString(request_counter);
        
        long hRequest = HttpOpenRequestW(hConnect, "POST", endpoint_ts, "HTTP/1.1", NULL, NULL, (int)0x84000100, 0);
        if(hRequest == 0) { InternetCloseHandle(hConnect); InternetCloseHandle(hInternet); return -1.0; }
        
        string headers = "Content-Type: application/json\r\n";
        uchar post_data[];
        StringToCharArray(json_payload, post_data, 0, WHOLE_ARRAY, CP_UTF8);
        int post_len = ArraySize(post_data);
        if(post_len > 0 && post_data[post_len-1] == 0) post_len -= 1;
        
        int res = HttpSendRequestW(hRequest, headers, StringLen(headers), post_data, post_len);
        if(res == 0) { 
            InternetCloseHandle(hRequest); InternetCloseHandle(hConnect); InternetCloseHandle(hInternet); 
            return -1.0; 
        }
        
        uchar buffer[1024];
        int bytes_read = 0;
        string response = "";
        
        while(InternetReadFile(hRequest, buffer, 1024, bytes_read)) {
            if(bytes_read == 0) break;
            response += CharArrayToString(buffer, 0, bytes_read);
        }
        
        InternetCloseHandle(hRequest);
        InternetCloseHandle(hConnect);
        InternetCloseHandle(hInternet);
        
        int idx = StringFind(response, "\"probability\":");
        if(idx != -1) {
            string valStr = StringSubstr(response, idx + 14);
            int end_idx = StringFind(valStr, "}");
            if(end_idx != -1) valStr = StringSubstr(valStr, 0, end_idx);
            return StringToDouble(valStr);
        }
        return -1.0;
    }
}

//+------------------------------------------------------------------+
//| CLASE GESTORA DE SÍMBOLO (OOP Multi-Activo)                      |
//+------------------------------------------------------------------+
class CSymbolManager
{
private:
    string m_symbol;
    ENUM_TIMEFRAMES m_macro_tf;
    
    int hma_handle, hma_exit_handle, rsi_handle, atr_handle;
    int ema50_handle, ema200_handle, sma20_handle, std_dev_handle;
    int ema50_h4_handle, atr200_handle, atr_d1_handle, adx_handle;
    int fast_hma_exit_handle;
    
    datetime lastBarTime;
    datetime lastExitBarTime;
    
    int bars_since_asian_sweep_high;
    int bars_since_asian_sweep_low;
    int bars_since_local_sweep_high;
    int bars_since_local_sweep_low;
    int bars_since_vol_shock_bull;
    int bars_since_vol_shock_bear;

    double GetPip() {
        double point = SymbolInfoDouble(m_symbol, SYMBOL_POINT);
        int digits = (int)SymbolInfoInteger(m_symbol, SYMBOL_DIGITS);
        if(digits == 5 || digits == 3) return point * 10.0;
        return point;
    }

    double CalcDynamicLotSize(double sl_distance_points) {
        double balance = AccountInfoDouble(ACCOUNT_BALANCE);
        if(!InpUseCompoundInterest) balance = InpFixedBalance;
        
        double risk_amount = balance * (InpRiskPerTrade / 100.0);
        double tick_value = SymbolInfoDouble(m_symbol, SYMBOL_TRADE_TICK_VALUE);
        double tick_size = SymbolInfoDouble(m_symbol, SYMBOL_TRADE_TICK_SIZE);
        
        if(sl_distance_points <= 0 || tick_value <= 0) return 0.0;
        
        double point_val = tick_value / (tick_size / SymbolInfoDouble(m_symbol, SYMBOL_POINT));
        double risk_per_lot = sl_distance_points * point_val;
        
        if(risk_per_lot <= 0) return 0.0;
        
        double lots = risk_amount / risk_per_lot;
        
        double min_lot = SymbolInfoDouble(m_symbol, SYMBOL_VOLUME_MIN);
        double max_lot = SymbolInfoDouble(m_symbol, SYMBOL_VOLUME_MAX);
        double step_lot = SymbolInfoDouble(m_symbol, SYMBOL_VOLUME_STEP);
        
        lots = MathFloor(lots / step_lot) * step_lot;
        if(lots < min_lot) lots = min_lot;
        if(lots > max_lot) lots = max_lot;
        
        return lots;
    }

    void TickLevelManagement() {
        double pip = GetPip();
        double vol_min  = SymbolInfoDouble(m_symbol, SYMBOL_VOLUME_MIN);
        double vol_step = SymbolInfoDouble(m_symbol, SYMBOL_VOLUME_STEP);
        
        int total = PositionsTotal();
        for(int i = total - 1; i >= 0; i--) {
            ulong ticket = PositionGetTicket(i);
            if(PositionGetString(POSITION_SYMBOL) == m_symbol && PositionGetInteger(POSITION_MAGIC) == 777999) {
                double open_price   = PositionGetDouble(POSITION_PRICE_OPEN);
                double current_price = PositionGetDouble(POSITION_PRICE_CURRENT);
                double sl           = PositionGetDouble(POSITION_SL);
                double tp           = PositionGetDouble(POSITION_TP);
                double current_lots = PositionGetDouble(POSITION_VOLUME);
                long type = PositionGetInteger(POSITION_TYPE);
                
                double dist_sl_pips = 0.0;
                double floating_rr  = 0.0;
                
                if(type == POSITION_TYPE_BUY) {
                    dist_sl_pips = (current_price - sl) / pip;
                    if(open_price - sl > 0) floating_rr = (current_price - open_price) / (open_price - sl);
                } else {
                    dist_sl_pips = (sl - current_price) / pip;
                    if(sl - open_price > 0) floating_rr = (open_price - current_price) / (sl - open_price);
                }
                
                bool already_scaled = false;
                for(int s = 0; s < ArraySize(g_scaled_tickets); s++) {
                    if(g_scaled_tickets[s] == ticket) { already_scaled = true; break; }
                }
                
                // HIGH FREQUENCY TICK EVALUATION: Scale-Out intra-bar
                if(!already_scaled && floating_rr >= InpScaleOutRR) {
                    double close_lots = MathFloor((current_lots * 0.5) / vol_step) * vol_step;
                    if(close_lots < vol_min) {
                        trade.PositionClose(ticket);
                        Print("[SCALE-OUT] Lote residual < mínimo. Cierre total. Ticket: ", ticket);
                        continue;
                    }
                    trade.PositionClosePartial(ticket, close_lots);
                    trade.PositionModify(ticket, open_price, tp);
                    int sz = ArraySize(g_scaled_tickets);
                    ArrayResize(g_scaled_tickets, sz + 1);
                    g_scaled_tickets[sz] = ticket;
                    Print("[SCALE-OUT] 50% cerrado a ", close_lots, " lots. BE movido a ", open_price, " Ticket: ", ticket);
                    already_scaled = true; // Acaba de ser escalado en este tick
                }
                
                // TRAILING STOP PARA EL RUNNER (GIVEBACK MITIGATION)
                if(already_scaled) {
                    double atr_value = 0.0;
                    double atr_buf[1];
                    if(CopyBuffer(atr_handle, 0, 0, 1, atr_buf) > 0) atr_value = atr_buf[0];
                    
                    if(atr_value > 0) {
                        double trailing_dist = atr_value * InpRunnerTrailingATR;
                        if(type == POSITION_TYPE_BUY) {
                            double high = SymbolInfoDouble(m_symbol, SYMBOL_ASK); // O iHigh, pero Ask es más seguro
                            double new_sl = high - trailing_dist;
                            if(new_sl > sl + (pip * 2)) { // Solo mover si mejora el SL anterior por al menos 2 pips
                                trade.PositionModify(ticket, new_sl, tp);
                                Print("[TRAILING STOP] Runner BUY SL ajustado a ", new_sl, " Ticket: ", ticket);
                            }
                        } else if(type == POSITION_TYPE_SELL) {
                            double low = SymbolInfoDouble(m_symbol, SYMBOL_BID);
                            double new_sl = low + trailing_dist;
                            if(sl == 0 || new_sl < sl - (pip * 2)) {
                                trade.PositionModify(ticket, new_sl, tp);
                                Print("[TRAILING STOP] Runner SELL SL ajustado a ", new_sl, " Ticket: ", ticket);
                            }
                        }
                    }
                }
            }
        }
    }

    void ManageOpenTrades(double current_atr, double spread, double close_1, double close_2,
                          double hma_1, double macro_adx,
                          double fast_hma_close_1, double fast_hma_close_2) {
        datetime currentBarTime = iTime(m_symbol, _Period, 0);
        bool is_new_bar = (currentBarTime != lastExitBarTime);
        
        if(!is_new_bar) return;
        
        double hma_exit[2], rsi_buf[1];
        if(CopyBuffer(hma_exit_handle, 0, 0, 2, hma_exit) < 2) return;
        if(CopyBuffer(rsi_handle, 0, 0, 1, rsi_buf) < 1) return;
        
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
                
                bool hard_close = false;
                if(type == POSITION_TYPE_BUY  && close_1 < hma_1) hard_close = true;
                if(type == POSITION_TYPE_SELL && close_1 > hma_1) hard_close = true;
                
                if(hard_close) {
                    trade.PositionClose(ticket);
                    Print("[HARD EXIT] FISICA ESTRUCTURAL ROTA. ABORTANDO. Ticket: ", ticket);
                } else if(bars_in_trade >= g_VerticalBarrierBars) {
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
                    double elastic_pct = (peak_stretch > 0) ? ((peak_stretch - current_stretch) / peak_stretch) : 0.0;
                    
                    double fast_hma_buf[], hma_exit_buf[], rsi_eval_buf[];
                    ArraySetAsSeries(fast_hma_buf,  true);
                    ArraySetAsSeries(hma_exit_buf,  true);
                    ArraySetAsSeries(rsi_eval_buf,  true);
                    
                    if(CopyBuffer(hma_handle,      0, 0, 4, fast_hma_buf)  < 4) return;
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
                    
                    bool any_trigger = (is_trigger_fast == 1 || is_trigger_slow == 1 || is_trigger_rsi == 1 ||
                                        is_trigger_profit == 1 || is_trigger_fast_hma_cross == 1);
                    
                    if(!any_trigger) continue;
                    
                    string json = "{";
                    json += "\"activo\":\"" + m_symbol + "\",";
                    json += "\"Bars_In_Trade\":" + IntegerToString(bars_in_trade) + ",";
                    json += "\"Open_Profit_R\":" + DoubleToString(floating_rr, 4) + ",";
                    json += "\"Drawdown_From_Peak_R\":0.0,";
                    json += "\"Exit_HMA_Velocity\":" + DoubleToString(exit_hma_velocity, 4) + ",";
                    json += "\"Exit_HMA_Accel\":" + DoubleToString(exit_hma_accel, 4) + ",";
                    json += "\"Exit_RSI\":" + DoubleToString(rsi_buf[0], 2) + ",";
                    json += "\"Exit_Volatility_Ratio\":1.0,";
                    json += "\"Spread_Impact_Exit\":" + DoubleToString(spread/10.0, 4) + ",";
                    json += "\"Is_Trigger_Fast\":" + IntegerToString(is_trigger_fast) + ".0,";
                    json += "\"Is_Trigger_Slow\":" + IntegerToString(is_trigger_slow) + ".0,";
                    json += "\"Is_Trigger_RSI\":" + IntegerToString(is_trigger_rsi) + ".0,";
                    json += "\"Is_Trigger_Profit\":" + IntegerToString(is_trigger_profit) + ".0,";
                    json += "\"Is_Trigger_Fast_HMA_Cross\":" + IntegerToString(is_trigger_fast_hma_cross) + ".0,";
                    json += "\"Macro_ADX_Exit\":" + DoubleToString(macro_adx, 2) + ",";
                    json += "\"Peak_HMA_Stretch_ATR\":" + DoubleToString(peak_stretch, 4) + ",";
                    json += "\"Current_HMA_Stretch_ATR\":" + DoubleToString(current_stretch, 4) + ",";
                    json += "\"Elastic_Retracement_Pct\":" + DoubleToString(elastic_pct, 4);
                    json += "}";
                    
                    double exit_proba = RequestFastAPI("/predict_exit", json);
                    
                    if(exit_proba >= ExitThreshold) {
                        trade.PositionClose(ticket);
                        Print("[CERRADO] Predict_Exit: ", exit_proba, " Ticket: ", ticket, " | Sym: ", m_symbol);
                    }
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
        bars_since_asian_sweep_low = 999;
        bars_since_local_sweep_high = 999;
        bars_since_local_sweep_low = 999;
        bars_since_vol_shock_bull = 999;
        bars_since_vol_shock_bear = 999;
        
        hma_handle = INVALID_HANDLE;
        hma_exit_handle = INVALID_HANDLE;
        rsi_handle = INVALID_HANDLE;
        atr_handle = INVALID_HANDLE;
        ema50_handle = INVALID_HANDLE;
        ema200_handle = INVALID_HANDLE;
        sma20_handle = INVALID_HANDLE;
        std_dev_handle = INVALID_HANDLE;
        ema50_h4_handle = INVALID_HANDLE;
        atr200_handle = INVALID_HANDLE;
        atr_d1_handle = INVALID_HANDLE;
        adx_handle = INVALID_HANDLE;
        fast_hma_exit_handle = INVALID_HANDLE;
    }

    bool Init(string sym) {
        m_symbol = sym;
        
        if     (_Period == PERIOD_M15) m_macro_tf = PERIOD_H1;
        else if(_Period == PERIOD_H1)  m_macro_tf = PERIOD_H4;
        else if(_Period == PERIOD_H4)  m_macro_tf = PERIOD_D1;
        else if(_Period == PERIOD_D1)  m_macro_tf = PERIOD_W1;
        else                           m_macro_tf = PERIOD_H4;
        
        hma_handle      = iCustom(m_symbol, _Period, "HMA50", HMAPeriod);
        hma_exit_handle = iCustom(m_symbol, _Period, "HMA50", InpHMA_ExitPeriod);
        fast_hma_exit_handle = iCustom(m_symbol, _Period, "HMA50", InpFastHMA_Exit_Period);
        rsi_handle      = iRSI(m_symbol, _Period, RsiPeriod, PRICE_CLOSE);
        atr_handle      = iATR(m_symbol, _Period, 14);
        ema50_handle    = iMA(m_symbol, m_macro_tf, 50,  0, MODE_EMA, PRICE_CLOSE);
        ema200_handle   = iMA(m_symbol, m_macro_tf, 200, 0, MODE_EMA, PRICE_CLOSE);
        sma20_handle    = iMA(m_symbol, _Period, 20, 0, MODE_SMA, PRICE_CLOSE);
        std_dev_handle  = iStdDev(m_symbol, _Period, 20, 0, MODE_SMA, PRICE_CLOSE);
        ema50_h4_handle = iMA(m_symbol, PERIOD_H4, 50, 0, MODE_EMA, PRICE_CLOSE);
        atr200_handle   = iATR(m_symbol, _Period, 200);
        atr_d1_handle   = iATR(m_symbol, PERIOD_D1, 14);
        adx_handle      = iADX(m_symbol, PERIOD_D1, 14);

        if(hma_handle == INVALID_HANDLE || hma_exit_handle == INVALID_HANDLE || fast_hma_exit_handle == INVALID_HANDLE ||
           rsi_handle == INVALID_HANDLE || atr_handle == INVALID_HANDLE || std_dev_handle == INVALID_HANDLE ||
           ema50_h4_handle == INVALID_HANDLE || atr200_handle == INVALID_HANDLE || atr_d1_handle == INVALID_HANDLE || adx_handle == INVALID_HANDLE)
        {
            Print("ERROR CRITICO: Indicadores no inicializados para ", m_symbol);
            return false;
        }
        return true;
    }

    void Release() {
        if(hma_handle != INVALID_HANDLE) IndicatorRelease(hma_handle);
        if(hma_exit_handle != INVALID_HANDLE) IndicatorRelease(hma_exit_handle);
        if(fast_hma_exit_handle != INVALID_HANDLE) IndicatorRelease(fast_hma_exit_handle);
        if(rsi_handle != INVALID_HANDLE) IndicatorRelease(rsi_handle);
        if(atr_handle != INVALID_HANDLE) IndicatorRelease(atr_handle);
        if(ema50_handle != INVALID_HANDLE) IndicatorRelease(ema50_handle);
        if(ema200_handle != INVALID_HANDLE) IndicatorRelease(ema200_handle);
        if(sma20_handle != INVALID_HANDLE) IndicatorRelease(sma20_handle);
        if(std_dev_handle != INVALID_HANDLE) IndicatorRelease(std_dev_handle);
        if(ema50_h4_handle != INVALID_HANDLE) IndicatorRelease(ema50_h4_handle);
        if(atr200_handle != INVALID_HANDLE) IndicatorRelease(atr200_handle);
        if(atr_d1_handle != INVALID_HANDLE) IndicatorRelease(atr_d1_handle);
        if(adx_handle != INVALID_HANDLE) IndicatorRelease(adx_handle);
    }

    void ProcessTick() {
        TickLevelManagement();
        
        datetime currentBarTime = iTime(m_symbol, _Period, 0);
        if(currentBarTime == lastBarTime || currentBarTime == 0) return;

        double hma[], hma_exit_buf[], rsi_buf[], atr_buf[];
        double ef[], es[], sma20[], stddev[], ema50_h4[], atr200_buf[], adx_buf[], atr_d1_buf[];
        MqlRates rates[];

        ArraySetAsSeries(hma,          true);
        ArraySetAsSeries(hma_exit_buf, true);
        ArraySetAsSeries(rsi_buf,      true);
        ArraySetAsSeries(atr_buf,      true);
        ArraySetAsSeries(ef,           true);
        ArraySetAsSeries(es,           true);
        ArraySetAsSeries(sma20,        true);
        ArraySetAsSeries(stddev,       true);
        ArraySetAsSeries(ema50_h4,     true);
        ArraySetAsSeries(atr200_buf,   true);
        ArraySetAsSeries(adx_buf,      true);
        ArraySetAsSeries(atr_d1_buf,   true);
        ArraySetAsSeries(rates,        true);

        int rates_copied    = CopyRates(m_symbol, _Period, 0, 60, rates);
        if(rates_copied < 4) return;
        int hma_copied      = CopyBuffer(hma_handle,      0, 0, 60, hma);
        if(hma_copied < 4)   return;
        int hma_exit_copied = CopyBuffer(hma_exit_handle, 0, 0, 3, hma_exit_buf);
        if(hma_exit_copied < 3) return;
        if(CopyBuffer(rsi_handle,     0, 0, RsiLookbackBars + 1, rsi_buf) < RsiLookbackBars + 1) return;
        if(CopyBuffer(atr_handle,     0, 0, 51, atr_buf)  < 51) return;
        if(CopyBuffer(atr200_handle,  0, 0, 1,  atr200_buf) < 1) return;
        if(CopyBuffer(atr_d1_handle,  0, 0, 1,  atr_d1_buf) < 1) return;
        if(CopyBuffer(sma20_handle,   0, 0, 1,  sma20)    < 1)  return;
        if(CopyBuffer(std_dev_handle, 0, 0, 1,  stddev)   < 1)  return;

        int macro_shift = iBarShift(m_symbol, m_macro_tf, currentBarTime);
        int h4_shift    = iBarShift(m_symbol, PERIOD_H4,  currentBarTime);
        int d1_shift    = iBarShift(m_symbol, PERIOD_D1,  currentBarTime);
        if(CopyBuffer(ema50_handle,    0, macro_shift, 1, ef)       < 1) return;
        if(CopyBuffer(ema200_handle,   0, macro_shift, 1, es)       < 1) return;
        if(CopyBuffer(ema50_h4_handle, 0, h4_shift, 2, ema50_h4) < 2) return;
        
        if(CopyBuffer(adx_handle, 0, d1_shift, 1, adx_buf) < 1) return;
        double macro_adx = adx_buf[0];

        double pip        = GetPip();
        double spread     = 0.0;
        if(pip > 0) spread = (SymbolInfoDouble(m_symbol, SYMBOL_ASK) - SymbolInfoDouble(m_symbol, SYMBOL_BID)) / pip;

        double current_atr = atr_buf[0];

        double fast_hma_k[];
        ArraySetAsSeries(fast_hma_k, true);
        if(CopyBuffer(fast_hma_exit_handle, 0, 0, 4, fast_hma_k) < 4) return;

        // PASO 1: GESTION DE SALIDAS
        ManageOpenTrades(current_atr, spread, rates[1].close, rates[2].close, hma[1], macro_adx,
                         fast_hma_k[1], fast_hma_k[2]);

        // CONCURRENCIA LOCK GLOBAL INMEDIATO
        if(PositionsTotal() >= InpMaxPortfolioTrades) {
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
            bool swept_asian_high = (rates[1].high > asian_high) && (rates[1].close <= asian_high) && (rates[1].open <= asian_high);
            bool swept_asian_low  = (rates[1].low < asian_low)   && (rates[1].close >= asian_low)  && (rates[1].open >= asian_low);
            if(swept_asian_high) { bars_since_asian_sweep_high = 0; is_asian_sweep_high = true; }
            if(swept_asian_low)  { bars_since_asian_sweep_low = 0; is_asian_sweep_low = true; }
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

        bool hma_cross_up = (rates[2].close < hma[2] && rates[1].close > hma[1]);
        bool hma_cross_dn = (rates[2].close > hma[2] && rates[1].close < hma[1]);

        int count_consistent_buy  = CountConsistentlyBelowHMA(rates, hma, 3);
        int count_consistent_sell = CountConsistentlyAboveHMA(rates, hma, 3);

        bool rsi_oversold   = WasRSIOversold(rsi_buf, 0, RsiLookbackBars, (double)RsiOversoldLevel);
        bool rsi_overbought = WasRSIOverbought(rsi_buf, 0, RsiLookbackBars, (double)RsiOverboughtLevel);

        bool valid_hma_buy  = hma_cross_up;
        bool valid_hma_sell = hma_cross_dn;

        bool has_trigger = (valid_hma_buy || valid_hma_sell);

        if(!has_trigger) {
            lastBarTime = currentBarTime;
            return;
        }

        double max_allowed_spread = MaxSpreadPips;
        string symbol_upper = m_symbol;
        StringToUpper(symbol_upper);
        if(StringFind(symbol_upper, "XAU") >= 0 || StringFind(symbol_upper, "GOLD") >= 0 || StringFind(symbol_upper, "XAG") >= 0) {
            max_allowed_spread = InpMaxSpreadPips_Metals;
        }

        
        if(spread > max_allowed_spread) {
            lastBarTime = currentBarTime;
            return;
        }

        double minDev = current_atr * (AntiNoiseATRPct / 100.0);
        double deviation = MathAbs(rates[0].close - hma[0]);
        if(deviation < minDev) {
            lastBarTime = currentBarTime;
            return;
        }

        double candle_size = rates[0].high - rates[0].low;
        if(candle_size > (current_atr * InpMaxSignalBarATR)) {
            lastBarTime = currentBarTime;
            return;
        }

        int signalType = 1;        // 1=SELL
        if(valid_hma_buy) signalType = 0; // 0=BUY

        double ask = SymbolInfoDouble(m_symbol, SYMBOL_ASK);
        double bid = SymbolInfoDouble(m_symbol, SYMBOL_BID);

        double sl = GetHighestHigh(m_symbol, LookbackBars);
        if(signalType == 0) sl = GetLowestLow(m_symbol, LookbackBars);
        if(sl == 0.0) { Print(Abortando , m_symbol,  en linea , __LINE__); lastBarTime = currentBarTime; return; }

        double slDist = sl - bid;
        if(signalType == 0) slDist = ask - sl;
        if(slDist <= 0.0) { Print(Abortando , m_symbol,  en linea , __LINE__); lastBarTime = currentBarTime; return; }

        double sl_dist_atr = 0.0;
        if(current_atr > 0) sl_dist_atr = slDist / current_atr;
        if(sl_dist_atr > InpMaxSLATR) { Print(Abortando , m_symbol,  en linea , __LINE__); lastBarTime = currentBarTime; return; }
        
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
        
        bool limit_reached = false;
        if(count_dir >= InpMaxPortfolioTrades) limit_reached = true;
        
        bool risk_exceeded = false;
        double expected_risk = (count_dir + 1) * InpRiskPerTrade;
        if(expected_risk > InpMaxGlobalRisk) risk_exceeded = true;
        
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
        if(current_atr > 0) hma_slope = (hma[0] - hma[1]) / current_atr;

        double hma_accel_feat = CalcHmaAcceleration(hma_handle, current_atr);
        double breakout_force = CalcBreakoutForceATR(current_close, hma[0], current_atr);

        int    trend_align = -1;
        if(ef[0] > es[0]) trend_align = 1;
        double dist_macro = CalcDistToMacroEMA(current_close, es[0], current_atr);

        int    pb_duration = 0;
        double pb_depth    = 0.0;
        CalcPullbackMetrics(m_symbol, hma_handle, LookbackBars, current_atr, pb_duration, pb_depth);

        int h = dt.hour;
        int session_time = 1;
        if(h >= 13) {
            if(h <= 14) session_time = 0;
            else if(h <= 20) session_time = 3;
        } else {
            if(h >= 7) session_time = 2;
        }

        bool h4_rising = false;
        if(ema50_h4[0] > ema50_h4[1]) h4_rising = true;
        int h4_trend_align = -1;
        if(h4_rising) {
            if(signalType == 0) h4_trend_align = 1;
        } else {
            if(signalType == 1) h4_trend_align = 1;
        }

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

        double hma_vel        = (hma[0] - hma[1]) / current_atr;
        double vel_prev_k     = (hma[1] - hma[2]) / current_atr;
        double hma_accel_v2   = hma_vel - vel_prev_k;
        double vel_prev2_k    = (hma[2] - hma[3]) / current_atr;
        double accel_prev_k   = vel_prev_k - vel_prev2_k;
        double hma_jerk_val   = hma_accel_v2 - accel_prev_k;

        int  energy_accum  = 0;
        int  max_eb        = MathMin(rates_copied, hma_copied);
        bool stop_count    = false;
        if(signalType == 0) {
            for(int k = 1; k < max_eb; k++) {
                if(!stop_count) {
                    if(rates[k].close < hma[k]) energy_accum++;
                    else stop_count = true;
                }
            }
        } else {
            for(int k = 1; k < max_eb; k++) {
                if(!stop_count) {
                    if(rates[k].close > hma[k]) energy_accum++;
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

        string json = "{";
        json += "\"activo\":\"" + m_symbol + "\",";
        json += "\"Z_Score\":" + DoubleToString(z_score, 4) + ",";
        json += "\"ATR_Norm\":" + DoubleToString(atr_norm, 4) + ",";
        json += "\"RSI\":" + DoubleToString(rsi_val, 2) + ",";
        json += "\"RSI_Extreme\":" + DoubleToString(rsi_extreme, 2) + ",";
        json += "\"Bars_Since_Ext\":" + IntegerToString(bars_since) + ".0,";
        json += "\"HMA_Slope_Pct\":" + DoubleToString(hma_slope, 4) + ",";
        json += "\"HMA_Accel\":" + DoubleToString(hma_accel_feat, 4) + ",";
        json += "\"Breakout_Force_ATR\":" + DoubleToString(breakout_force, 4) + ",";
        json += "\"Trend_Align\":" + IntegerToString(trend_align) + ".0,";
        json += "\"Dist_Macro_EMA\":" + DoubleToString(dist_macro, 4) + ",";
        json += "\"Macro_ADX\":" + DoubleToString(macro_adx, 2) + ",";
        json += "\"Pullback_Dur\":" + IntegerToString(pb_duration) + ".0,";
        json += "\"Pullback_Depth_Pct\":" + DoubleToString(pb_depth, 4) + ",";
        json += "\"SL_Dist_ATR\":" + DoubleToString(sl_dist_atr, 4) + ",";
        json += "\"Hour\":" + IntegerToString(dt.hour) + ".0,";
        json += "\"Session_Time\":" + IntegerToString(session_time) + ".0,";
        json += "\"H4_Trend_Align\":" + IntegerToString(h4_trend_align) + ".0,";
        json += "\"Vol_Spread_Ratio\":" + DoubleToString(vol_spread_ratio, 4) + ",";
        json += "\"ATR_Ratio_High\":" + DoubleToString(atr_ratio_high, 4) + ",";
        json += "\"RSI_Slope_10\":" + DoubleToString(rsi_slope_10, 4) + ",";
        json += "\"Spread_Impact_Ratio\":" + DoubleToString(spread_impact_ratio, 4) + ",";
        json += "\"HMA_Velocity\":" + DoubleToString(hma_vel, 5) + ",";
        json += "\"HMA_Acceleration\":" + DoubleToString(hma_accel_v2, 5) + ",";
        json += "\"HMA_Jerk\":" + DoubleToString(hma_jerk_val, 5) + ",";
        json += "\"Energy_Accumulation\":" + IntegerToString(energy_accum) + ".0,";
        
        double bars_since_asian_sweep = (signalType == 0) ? bars_since_asian_sweep_low : bars_since_asian_sweep_high;
        double bars_since_local_sweep = (signalType == 0) ? bars_since_local_sweep_low : bars_since_local_sweep_high;
        double bars_since_vol_shock   = (signalType == 0) ? bars_since_vol_shock_bull : bars_since_vol_shock_bear;
        
        json += "\"Bars_Since_Asian_Sweep\":" + DoubleToString(bars_since_asian_sweep, 1) + ",";
        json += "\"Bars_Since_Local_Sweep\":" + DoubleToString(bars_since_local_sweep, 1) + ",";
        json += "\"Bars_Since_Vol_Shock\":" + DoubleToString(bars_since_vol_shock, 1) + ",";
        
        double dist_asian_high_atr = 0;
        double dist_asian_low_atr = 0;
        if(current_atr > 0) {
            if(asian_high > 0) dist_asian_high_atr = (asian_high - current_close)/current_atr;
            if(asian_low > 0) dist_asian_low_atr = (current_close - asian_low)/current_atr;
        }
        json += "\"Dist_Asian_High_ATR\":" + DoubleToString(dist_asian_high_atr, 4) + ",";
        json += "\"Dist_Asian_Low_ATR\":" + DoubleToString(dist_asian_low_atr, 4) + ",";
        
        double is_asian = 0.0;
        if(is_asian_sweep_high || is_asian_sweep_low) is_asian = 1.0;
        json += "\"Is_Asian_Sweep\":" + DoubleToString(is_asian, 1) + ",";
        json += "\"Tick_Volume_ZScore\":" + DoubleToString(tick_vol_zscore, 4) + ",";
        json += "\"Spread_Expansion_Ratio\":" + DoubleToString(spread_exp_ratio, 4) + ",";
        json += "\"Candle_Dominance\":" + DoubleToString(candle_dominance, 4) + ",";
        json += "\"Regime_Consistency_Count\":" + IntegerToString((signalType == 0) ? count_consistent_buy : count_consistent_sell) + ".0,";
        json += "\"RSI_Exhausted\":" + IntegerToString((signalType == 0) ? (int)rsi_oversold : (int)rsi_overbought) + ".0,";
        json += "\"MTF_ATR_Ratio\":" + DoubleToString(mtf_atr_ratio, 4) + ",";
        json += "\"Trigger_Rejection_Tail\":" + DoubleToString(trigger_rejection_tail, 4) + ",";
        json += "\"Bollinger_Dev\":" + DoubleToString(bollinger_dev, 4);
        json += "}";

        double entry_proba = RequestFastAPI("/predict_entry", json);
        
        bool execute_trade = false;
        if(entry_proba >= EntryThreshold) {
            if(count_dir == 0) {
                execute_trade = true;
            } else {
                if(entry_proba > max_proba_open) {
                    execute_trade = true;
                } else {
                    Print("Rechazado: Probabilidad marginal menor. Nueva: ", entry_proba, " Max Abierta: ", max_proba_open);
                }
            }
        }
        
        if(execute_trade) {
            double lots = CalcDynamicLotSize(sl_distance_points);
            string comment = "AI_" + DoubleToString(entry_proba, 2);
            
            if(lots > 0) {
                if(signalType == 0) trade.Buy(lots, m_symbol, ask, sl, 0, comment);
                else trade.Sell(lots, m_symbol, bid, sl, 0, comment);
                Print("ORDEN ENVIADA - Sym: ", m_symbol, " Proba: ", entry_proba, " Lotes: ", lots);
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
    trade.SetExpertMagicNumber(777999);
    g_VerticalBarrierBars = (int)(InpHMA_ExitPeriod * 1.5);

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
    
    // Iniciar temporizador asíncrono para bucle de escaneo
    EventSetMillisecondTimer(500);

    Print("OK: Alpha Sniper Deploy Multi-Divisa (Fase 19) — Autor: Manuel");
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
    ArrayFree(g_scaled_tickets);
}

//+------------------------------------------------------------------+
//| OnTimer (Bucle Asíncrono Maestro)                                |
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
    // El trabajo real de escaneo se hace en OnTimer de forma balanceada.
    // Mantenemos OnTick vacio pero puede usarse para reaccionar a 
    // movimientos muy violentos del simbolo base si fuera necesario.
}
