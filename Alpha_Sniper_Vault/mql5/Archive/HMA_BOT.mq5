//+------------------------------------------------------------------+
//|                                                  HMA_BOT.mq5     |
//|                                    Archivo Principal del EA      |
//|           (Version 5.0 - Self-contained, News/Volume purged)     |
//+------------------------------------------------------------------+
#property strict
#property version "5.0"
#property description "Bot HMA50 - Legacy (sin dependencias externas)"

#include <Trade\Trade.mqh>
CTrade trade;


// --- Parametros de riesgo y trade ---
input group "Riesgo y Gestion"
input double InitialRiskPercent    = 0.01;
input double RiskIncrementPercent  = 0;
double       TakeProfitMultiplier  = 2.0;
input int    MaxRsiToCrossMinutes  = 10;
input double DailyLossLimitPercent = 100;
double       currentRiskPercent;

input group "Filtros de Entrada"
input double MaxSpreadPips         = 2.0;
input double MinStopLossPips       = 2;
input double DeviationATRPercent   = 25.0;
input int    MinOppositeBars       = 3;
input int    LookbackBars          = 10;

input group "Indicadores"
input int    ATR_Period            = 14;


//+------------------------------------------------------------------+
//| Variables Globales                                                |
//+------------------------------------------------------------------+
int        currentDay = 0;
double     startOfDayEquity = 0.0;
ulong      posOpenPosIDs[];
int        posOpenHours[];
int        posCount = 0;

double     testerHourPerformance[24];
double     initialBalance;
double     testerFinalResult = 0.0;
int        optimization_pass = 0;
ulong      lastProcessedDeal = 0;

int hmaHandle;
int ema50Handle, ema200Handle;
int rsiHandle;
int atrHandle;


//+------------------------------------------------------------------+
//| Funciones Utilitarias (inlined - antes en HMA_FUNCTIONS.mqh)     |
//+------------------------------------------------------------------+

string GetOptimizationID(int maxRsiMin, double maxSpread, double atrPerc, int minBars, int lookback)
{
    string id = "";
    id += "RSI="       + IntegerToString(maxRsiMin);
    id += "_Spread="   + DoubleToString(maxSpread, 1);
    id += "_ATR="      + DoubleToString(atrPerc, 1);
    id += "_MinBars="  + IntegerToString(minBars);
    id += "_Lookback=" + IntegerToString(lookback);
    return id;
}

void AppendHourlyPerformanceToCSV(string filename, string optimizationID)
{
    int handle = FileOpen(filename, FILE_READ | FILE_WRITE | FILE_CSV | FILE_COMMON);
    bool fileExists = (handle != INVALID_HANDLE);
    if(!fileExists)
    {
        handle = FileOpen(filename, FILE_WRITE | FILE_CSV | FILE_COMMON);
        if(handle == INVALID_HANDLE) return;
        FileWrite(handle, "Parametros","Hora","Rentabilidad (%)");
    }
    FileSeek(handle, 0, SEEK_END);
    for(int h = 0; h < 24; h++)
        FileWrite(handle, optimizationID, StringFormat("%02dH", h), DoubleToString(testerHourPerformance[h], 2));
    FileClose(handle);
}

void RegisterOpenTrade(ulong positionID, datetime openTime)
{
    int newSize = posCount + 1;
    ArrayResize(posOpenPosIDs, newSize);
    ArrayResize(posOpenHours, newSize);
    if(ArraySize(posOpenPosIDs) == newSize)
    {
        MqlDateTime t;
        TimeToStruct(openTime, t);
        posOpenPosIDs[posCount] = positionID;
        posOpenHours[posCount]  = t.hour;
        posCount++;
    }
}

bool CheckDailyLossLimit(double dailyLossLimitPercent)
{
    MqlDateTime dt;
    TimeToStruct(TimeCurrent(), dt);
    if(dt.day != currentDay)
    {
        currentDay = dt.day;
        startOfDayEquity = AccountInfoDouble(ACCOUNT_EQUITY);
    }
    double currentEquity = AccountInfoDouble(ACCOUNT_EQUITY);
    double lossPercent = ((startOfDayEquity - currentEquity) / startOfDayEquity) * 100;
    if(lossPercent >= dailyLossLimitPercent)
    {
        Print("Limite diario de perdida alcanzado: ", lossPercent, "%.");
        return false;
    }
    return true;
}

double CalculateLotSize(double slDistance)
{
    double riskAmount = AccountInfoDouble(ACCOUNT_BALANCE) * (currentRiskPercent / 100);
    int    dig        = (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS);
    double pip        = (dig == 3 || dig == 5) ? 10 * _Point : _Point;
    double slPips     = slDistance / pip;
    double tickSize   = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
    double tickValue  = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
    if(tickSize == 0 || tickValue == 0 || slPips <= 0) return 0;
    double pipValue = tickValue * (pip / tickSize);
    if(pipValue <= 0) return 0;
    double lotSize = riskAmount / (slPips * pipValue);
    double minLot  = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
    double maxLot  = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
    double stepLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
    lotSize = MathFloor(lotSize / stepLot) * stepLot;
    if(lotSize < minLot) lotSize = minLot;
    if(lotSize > maxLot) lotSize = maxLot;
    int lotDigits = (int)MathRound(-MathLog10(stepLot));
    return NormalizeDouble(lotSize, lotDigits);
}

double GetLowestLow(int bars)
{
    double lowest = DBL_MAX;
    for(int i = 1; i <= bars; i++)
    {
        double low = iLow(_Symbol, _Period, i);
        if(low < lowest) lowest = low;
    }
    return (lowest == DBL_MAX) ? 0 : lowest;
}

double GetHighestHigh(int bars)
{
    double highest = -DBL_MAX;
    for(int i = 1; i <= bars; i++)
    {
        double high = iHigh(_Symbol, _Period, i);
        if(high > highest) highest = high;
    }
    return (highest == -DBL_MAX) ? 0 : highest;
}


//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
    Print("Inicializando HMA50 Bot (v5.0 Self-contained)...");
    MqlDateTime dt;
    TimeToStruct(TimeCurrent(), dt);
    currentDay = dt.day;
    startOfDayEquity = AccountInfoDouble(ACCOUNT_EQUITY);
    currentRiskPercent = InitialRiskPercent;
    ArrayResize(posOpenPosIDs, 0);
    ArrayResize(posOpenHours, 0);
    posCount = 0;

    ArrayInitialize(testerHourPerformance, 0.0);

    hmaHandle    = iCustom(_Symbol, _Period, "HMA50");
    ema50Handle  = iMA(_Symbol, PERIOD_H4, 50, 0, MODE_EMA, PRICE_CLOSE);
    ema200Handle = iMA(_Symbol, PERIOD_H4, 200, 0, MODE_EMA, PRICE_CLOSE);
    rsiHandle    = iRSI(_Symbol, _Period, 14, PRICE_CLOSE);
    atrHandle    = iATR(_Symbol, _Period, ATR_Period);

    if(hmaHandle == INVALID_HANDLE || ema50Handle == INVALID_HANDLE ||
       ema200Handle == INVALID_HANDLE || rsiHandle == INVALID_HANDLE ||
       atrHandle == INVALID_HANDLE)
    {
        Print("ERROR: Indicadores no cargados. HMA_Handle: ", hmaHandle);
        return(INIT_FAILED);
    }

    Print("OK: OnInit completado. EA listo.");
    return(INIT_SUCCEEDED);
}

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
    string optimizationID = GetOptimizationID(MaxRsiToCrossMinutes, MaxSpreadPips,
                                              DeviationATRPercent, MinOppositeBars, LookbackBars);
    AppendHourlyPerformanceToCSV("HourlyPerformance.csv", optimizationID);

    if(hmaHandle != INVALID_HANDLE)    IndicatorRelease(hmaHandle);
    if(ema50Handle != INVALID_HANDLE)  IndicatorRelease(ema50Handle);
    if(ema200Handle != INVALID_HANDLE) IndicatorRelease(ema200Handle);
    if(rsiHandle != INVALID_HANDLE)    IndicatorRelease(rsiHandle);
    if(atrHandle != INVALID_HANDLE)    IndicatorRelease(atrHandle);
    Print("EA Desinicializado. Razon: ", reason);
}

//+------------------------------------------------------------------+
//| Expert tick function (Algoritmo Principal)                       |
//+------------------------------------------------------------------+
void OnTick()
{
    static datetime lastTime = 0;
    MqlRates rates[3];
    if(CopyRates(_Symbol, _Period, 0, 3, rates) < 3) return;
    if(rates[0].time == lastTime) return;
    lastTime = rates[0].time;

    if(!CheckDailyLossLimit(DailyLossLimitPercent)) return;
    if(PositionSelect(_Symbol)) return;

    int digits = (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS);
    double pip = (digits == 3 || digits == 5) ? 10 * _Point : _Point;
    double spreadPips = (SymbolInfoDouble(_Symbol, SYMBOL_ASK) - SymbolInfoDouble(_Symbol, SYMBOL_BID)) / pip;
    if(spreadPips > MaxSpreadPips) return;

    double ema50[], ema200[], rsi[], hma50[], atr[];
    if(CopyBuffer(ema50Handle, 0, 0, 3, ema50) < 3) return;
    if(CopyBuffer(ema200Handle, 0, 0, 3, ema200) < 3) return;
    if(CopyBuffer(rsiHandle, 0, 0, 3, rsi) < 3) return;
    if(CopyBuffer(hmaHandle, 0, 0, 3, hma50) < 3) return;
    if(CopyBuffer(atrHandle, 0, 0, 2, atr) < 2) return;

    bool tendenciaAlcista = (ema50[1] > ema200[1]);
    bool tendenciaBajista = (ema50[1] < ema200[1]);
    ENUM_ORDER_TYPE signal = WRONG_VALUE;
    static datetime rsiValidTime = 0;

    if(rsi[1] < 35 && tendenciaAlcista)
        rsiValidTime = rates[1].time;
    else if(rsi[1] > 65 && tendenciaBajista)
        rsiValidTime = rates[1].time;

    bool rsiWindowActive = (rsiValidTime > 0 && (rates[1].time - rsiValidTime) <= MaxRsiToCrossMinutes * 60);

    if(rsiWindowActive)
    {
        double minDeviation = atr[1] * (DeviationATRPercent / 100.0);
        // BUY
        if(rates[1].open < hma50[1] && rates[1].close > hma50[1] && tendenciaAlcista)
        {
            double deviation = MathAbs(rates[1].close - hma50[1]);
            if(deviation >= minDeviation)
                signal = ORDER_TYPE_BUY;
        }
        // SELL
        else if(rates[1].open > hma50[1] && rates[1].close < hma50[1] && tendenciaBajista)
        {
            double deviation = MathAbs(hma50[1] - rates[1].close);
            if(deviation >= minDeviation)
                signal = ORDER_TYPE_SELL;
        }
    }

    if(signal == WRONG_VALUE) return;

    double entry = (signal == ORDER_TYPE_BUY) ? SymbolInfoDouble(_Symbol, SYMBOL_ASK)
                                              : SymbolInfoDouble(_Symbol, SYMBOL_BID);
    double sl = 0, tp = 0;

    if(signal == ORDER_TYPE_BUY)
    {
        sl = GetLowestLow(LookbackBars);
        if(sl == 0) return;
        tp = entry + (entry - sl) * TakeProfitMultiplier;
    }
    else
    {
        sl = GetHighestHigh(LookbackBars);
        if(sl == 0) return;
        tp = entry - (sl - entry) * TakeProfitMultiplier;
    }

    double slDistance = MathAbs(entry - sl);
    if(slDistance <= 0 || slDistance / pip < MinStopLossPips) return;

    double lotSize = CalculateLotSize(slDistance);
    if(lotSize <= 0) return;

    double ask = NormalizeDouble(SymbolInfoDouble(_Symbol, SYMBOL_ASK), _Digits);
    double bid = NormalizeDouble(SymbolInfoDouble(_Symbol, SYMBOL_BID), _Digits);

    bool tradeOk = false;
    if(signal == ORDER_TYPE_BUY)
        tradeOk = trade.Buy(lotSize, _Symbol, ask, sl, tp);
    else
        tradeOk = trade.Sell(lotSize, _Symbol, bid, sl, tp);

    if(tradeOk && (trade.ResultRetcode() == TRADE_RETCODE_DONE || trade.ResultRetcode() == TRADE_RETCODE_PLACED))
    {
        ulong positionID = trade.ResultDeal();
        datetime openTime = TimeCurrent();
        RegisterOpenTrade(positionID, openTime);

        PrintFormat("OK: %s | Lots=%.2f | Risk=%.2f%%",
                    (signal == ORDER_TYPE_BUY ? "BUY" : "SELL"), lotSize, currentRiskPercent);
        rsiValidTime = 0;
    }
    else
    {
        PrintFormat("ERROR: %s - %s (Retcode: %d)",
                    (signal == ORDER_TYPE_BUY ? "BUY" : "SELL"),
                    trade.ResultComment(), trade.ResultRetcode());
    }
}


//+------------------------------------------------------------------+
//| OnTradeTransaction (Tester + Risk Management)                    |
//+------------------------------------------------------------------+
void OnTradeTransaction(const MqlTradeTransaction &trans,
                        const MqlTradeRequest &request,
                        const MqlTradeResult &result)
{
    if(trans.type == TRADE_TRANSACTION_DEAL_ADD)
    {
        ulong dealTicket = trans.deal;
        if(HistoryDealGetInteger(dealTicket, DEAL_ENTRY) != DEAL_ENTRY_OUT)
            return;

        double profit = HistoryDealGetDouble(dealTicket, DEAL_PROFIT);
        ulong positionID = HistoryDealGetInteger(dealTicket, DEAL_POSITION_ID);

        for(int i = 0; i < posCount; i++)
        {
            if(posOpenPosIDs[i] == positionID)
            {
                int openHour = posOpenHours[i];
                double changePercent = (profit > 0 ? +2.0 : (profit < 0 ? -1.0 : 0.0));
                testerHourPerformance[openHour] += changePercent;
                break;
            }
        }

        if(profit < 0.0)
        {
            currentRiskPercent += RiskIncrementPercent;
            Print("SL Hit. Risk: ", DoubleToString(currentRiskPercent, 3), "%");
        }
        else if(profit > 0.0)
        {
            currentRiskPercent = InitialRiskPercent;
            Print("TP Hit. Risk reset: ", DoubleToString(currentRiskPercent, 3), "%");
        }
    }
}


//+------------------------------------------------------------------+
//| OnTester (Optimizacion)                                          |
//+------------------------------------------------------------------+
double OnTester()
{
    ArrayInitialize(testerHourPerformance, 0.0);
    if(!HistorySelect(0, TimeCurrent())) return 0.0;

    int totalDeals = HistoryDealsTotal();
    datetime full_from = 0, full_to = TimeCurrent();

    for(int i = 0; i < totalDeals; i++)
    {
        ulong dealTicket = HistoryDealGetTicket(i);
        if(dealTicket == 0) continue;

        if(HistoryDealGetInteger(dealTicket, DEAL_ENTRY) == DEAL_ENTRY_OUT)
        {
            double profit = HistoryDealGetDouble(dealTicket, DEAL_PROFIT);
            ulong positionID = HistoryDealGetInteger(dealTicket, DEAL_POSITION_ID);
            datetime openTime = 0;

            if(HistorySelectByPosition(positionID))
            {
                for(int j = 0; j < HistoryDealsTotal(); j++)
                {
                    ulong tk = HistoryDealGetTicket(j);
                    if(tk == 0) continue;
                    if(HistoryDealGetInteger(tk, DEAL_ENTRY) == DEAL_ENTRY_IN)
                    {
                        openTime = (datetime)HistoryDealGetInteger(tk, DEAL_TIME);
                        break;
                    }
                }
            }

            if(openTime > 0)
            {
                MqlDateTime t;
                TimeToStruct(openTime, t);
                if(profit > 0.0)      testerHourPerformance[t.hour] += 2.0;
                else if(profit < 0.0) testerHourPerformance[t.hour] -= 1.0;
            }

            HistorySelect(full_from, full_to);
        }
    }

    testerFinalResult = 0.0;
    for(int h = 0; h < 24; h++)
        testerFinalResult += testerHourPerformance[h];

    string optID = GetOptimizationID(MaxRsiToCrossMinutes, MaxSpreadPips,
                                     DeviationATRPercent, MinOppositeBars, LookbackBars);
    AppendHourlyPerformanceToCSV("HourlyPerformance.csv", optID);
    return testerFinalResult;
}


//+------------------------------------------------------------------+
//| OnTesterPass / OnTesterDeinit                                    |
//+------------------------------------------------------------------+
void OnTesterPass()
{
    optimization_pass++;
    PrintFormat("Pass #%d: %.2f", optimization_pass, testerFinalResult);
}

void OnTesterDeinit()
{
    Print("Optimization finished.");
}
//+------------------------------------------------------------------+