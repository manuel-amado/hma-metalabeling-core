//+------------------------------------------------------------------+
//|                                              Hull_Apex_Bot.mq5   |
//|                                   Project_Hull_Apex - NEXUS FORK |
//|                                     Bifurcation from Alpha_Sniper|
//+------------------------------------------------------------------+
#property copyright "NEXUS PROTOCOL"
#property link      ""
#property version   "1.00"

#include "Math/AHMA_Kinematics.mqh"
#include <Trade\Trade.mqh>

//+------------------------------------------------------------------+
//| Input Parameters                                                 |
//+------------------------------------------------------------------+
input group "=== AHMA Core Settings ==="
input int    InpMinPeriod     = 9;         // AHMA Min Period (Trend)
input int    InpMaxPeriod     = 80;        // AHMA Max Period (Range)
input int    InpERPeriod      = 14;        // Kaufman ER Period

input group "=== Institutional Filters ==="
input double InpMinADX                = 20.0; // Minimum ADX (Inertia)
input double InpOversold              = 30.0; // RSI Oversold (Block Sells)
input double InpOverbought            = 70.0; // RSI Overbought (Block Buys)
input ENUM_TIMEFRAMES InpMacroTF      = PERIOD_H4; // MTF Macro Timeframe
input double InpMaxExhaustionRatio    = 3.5;  // Max Pullback Exhaustion (ATR)

input group "=== Risk & Execution ==="
input double InpRiskPercent            = 1.0; // Risk per Trade (%)
input double InpStopLossATRMultiplier  = 2.2; // Stop Loss (ATR Multiplier)

input group "=== Trade Management ==="
input double InpTrailingATR            = 4.0; // Trailing Stop (ATR Multiplier)
input int    InpFastAHMAPeriod         = 15;  // AHMA Fast Period (Exit)
input int    InpBaseAHMAPeriod         = 50;  // AHMA Base Period (Exit)

input group "=== AI Meta-Labeling ==="
input bool   InpMetaLabeling          = true; // Activar IA (Capa 2 ONNX)
input double InpMetaThreshold         = 0.65; // Umbral de Probabilidad ONNX

//+------------------------------------------------------------------+
//| Global Variables                                                 |
//+------------------------------------------------------------------+
input bool   InpDataHarvesting        = false; // [OPT] Meta-Labeling Telemetry

struct TTelemetryRecord {
   ulong    ticket;
   datetime open_time;
   int      signal_type;
   double   micro_velocity;
   double   micro_acceleration;
   double   macro_velocity;
   double   tension_ratio;
   double   hour_of_day;
   double   day_of_week;
   double   dist_sma200_atr;
   double   session_vol_ratio;
};
TTelemetryRecord telemetry_db[];
CAHMA_Kinematics *MathCore;
CAHMA_Kinematics *MathFast;
CAHMA_Kinematics *MathBase;

int sma_d1_handle;
int atr_d1_handle;
int atr_handle;

#resource "OmniApex_MetaModel.onnx" as const uchar ExtModel[]
long metalabel_handle = INVALID_HANDLE;

CTrade trade;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
  {
   // Inicializar NÃºcleos MatemÃ¡ticos
   MathCore = new CAHMA_Kinematics(InpMinPeriod, InpMaxPeriod, InpERPeriod);
   
   // Para salidas, creamos dos instancias con base dinÃ¡mica
   MathFast = new CAHMA_Kinematics(MathMax(2, InpFastAHMAPeriod/2), InpFastAHMAPeriod, InpERPeriod);
   MathBase = new CAHMA_Kinematics(MathMax(5, InpBaseAHMAPeriod/2), InpBaseAHMAPeriod, InpERPeriod);
   
   // Inicializar Handles de Osciladores EstÃ¡ndar
   sma_d1_handle = iMA(_Symbol, PERIOD_D1, 200, 0, MODE_SMA, PRICE_CLOSE);
   atr_d1_handle = iATR(_Symbol, PERIOD_D1, 14);
   atr_handle = iATR(_Symbol, _Period, 14);
   
   if(sma_d1_handle == INVALID_HANDLE || atr_d1_handle == INVALID_HANDLE || atr_handle == INVALID_HANDLE)
     {
      Print("Error: No se pudieron cargar los indicadores.");
      return(INIT_FAILED);
     }
     
   trade.SetExpertMagicNumber(999901); // Nexus Alpha
   
   if(InpMetaLabeling)
     {
      metalabel_handle = OnnxCreateFromBuffer(ExtModel, ONNX_DEFAULT);
      if(metalabel_handle == INVALID_HANDLE)
        {
         Print("Error inicializando ONNX: ", GetLastError());
         return(INIT_FAILED);
        }
      long input_shape[] = {1, 8};
      OnnxSetInputShape(metalabel_handle, 0, input_shape);
      
      long label_shape[] = {1};
      OnnxSetOutputShape(metalabel_handle, 0, label_shape);
      
      long output_shape[] = {1, 2};
      OnnxSetOutputShape(metalabel_handle, 1, output_shape);
     }
   
   return(INIT_SUCCEEDED);
  }

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
   if(metalabel_handle != INVALID_HANDLE) OnnxRelease(metalabel_handle);
   if(MathCore != NULL) delete MathCore;
   if(MathFast != NULL) delete MathFast;
   if(MathBase != NULL) delete MathBase;
   
   IndicatorRelease(sma_d1_handle);
   IndicatorRelease(atr_d1_handle);
   IndicatorRelease(atr_handle);
   if(InpDataHarvesting)
     {
      int total = ArraySize(telemetry_db);
      if(total > 0)
        {
         int handle = FileOpen("OmniApex_Dataset.csv", FILE_CSV|FILE_WRITE|FILE_ANSI, ",");
         if(handle != INVALID_HANDLE)
           {
            FileWrite(handle, "Ticket", "Open_Time", "Signal_Type", "Micro_Velocity", "Micro_Acceleration", "Macro_Velocity", "Tension_Ratio", "Hour_of_Day", "Day_of_Week", "Dist_SMA200", "Session_Vol_Ratio", "Profit", "Target_Label");
            HistorySelect(0, TimeCurrent());
            int ones = 0;
            int zeros = 0;
            for(int k=0; k<total; k++)
              {
               double profit = 0.0;
               bool closed = false;
               for(int d=HistoryDealsTotal()-1; d>=0; d--)
                 {
                  ulong deal_ticket = HistoryDealGetTicket(d);
                  long entry_type = HistoryDealGetInteger(deal_ticket, DEAL_ENTRY);
                  ulong pos_id = HistoryDealGetInteger(deal_ticket, DEAL_POSITION_ID);
                  if((entry_type == DEAL_ENTRY_OUT || entry_type == DEAL_ENTRY_OUT_BY) && (pos_id == telemetry_db[k].ticket))
                    {
                     profit = HistoryDealGetDouble(deal_ticket, DEAL_PROFIT);
                     closed = true;
                     break;
                    }
                 }
               if(closed)
                 {
                  int label = (profit > 0) ? 1 : 0;
                  if(label==1) ones++; else zeros++;
                  FileWrite(handle, telemetry_db[k].ticket, TimeToString(telemetry_db[k].open_time), telemetry_db[k].signal_type, telemetry_db[k].micro_velocity, telemetry_db[k].micro_acceleration, telemetry_db[k].macro_velocity, telemetry_db[k].tension_ratio, telemetry_db[k].hour_of_day, telemetry_db[k].day_of_week, telemetry_db[k].dist_sma200_atr, telemetry_db[k].session_vol_ratio, profit, label);
                 }
              }
            FileClose(handle);
            PrintFormat("[META-LABELING] Dataset Exportado. Trades: %d (1s: %d, 0s: %d)", total, ones, zeros);
           }
        }
     }
  }

//+------------------------------------------------------------------+
//| CÃ¡lculo de Lotaje DinÃ¡mico                                       |
//+------------------------------------------------------------------+
double CalculateDynamicLot(double stop_loss_points)
  {
   if(stop_loss_points <= 0) return 0.01;
   
   double balance = AccountInfoDouble(ACCOUNT_BALANCE);
   double risk_amount = balance * (InpRiskPercent / 100.0);
   
   double tick_value = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   double tick_size = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   
   if(tick_size == 0) return 0.01;
   
   double point_value = tick_value / (tick_size / _Point);
   double volume = risk_amount / (stop_loss_points * point_value);
   
   // NormalizaciÃ³n segÃºn el broker
   double vol_min = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double vol_max = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   double vol_step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   
   volume = MathRound(volume / vol_step) * vol_step;
   
   if(volume < vol_min) volume = vol_min;
   if(volume > vol_max) volume = vol_max;
   
   return volume;
  }

//+------------------------------------------------------------------+
//| Central Evaluation Function (State Machine)                      |
//+------------------------------------------------------------------+
void EvaluateEntrySignal()
  {
   // Evitar abrir si ya tenemos posicion
   if(PositionsTotal() > 0) return;
   
   int count = InpMaxPeriod + InpERPeriod + 10;
   
   // 1. Cinematica MICRO
   double prices_micro[];
   if(CopyClose(_Symbol, _Period, 0, count + 2, prices_micro) <= 0) return;
   ArraySetAsSeries(prices_micro, true);
   
   double ahma_0 = MathCore.GetAHMA(0, prices_micro);
   double ahma_1 = MathCore.GetAHMA(1, prices_micro);
   double ahma_2 = MathCore.GetAHMA(2, prices_micro);
   
   double micro_vel_current = MathCore.GetVelocity(ahma_0, ahma_1);
   double micro_vel_prev = MathCore.GetVelocity(ahma_1, ahma_2);
   double micro_accel = MathCore.GetAcceleration(micro_vel_current, micro_vel_prev);
   
   // 2. Cinematica MACRO
   double prices_macro[];
   if(CopyClose(_Symbol, InpMacroTF, 0, count + 1, prices_macro) <= 0) return;
   ArraySetAsSeries(prices_macro, true);
   
   double macro_ahma_0 = MathCore.GetAHMA(0, prices_macro);
   double macro_ahma_1 = MathCore.GetAHMA(1, prices_macro);
   double macro_ahma_2 = MathCore.GetAHMA(2, prices_macro);
   double macro_vel_current = MathCore.GetVelocity(macro_ahma_0, macro_ahma_1);
   double macro_vel_prev = MathCore.GetVelocity(macro_ahma_1, macro_ahma_2);
   double macro_accel = MathCore.GetAcceleration(macro_vel_current, macro_vel_prev);
   
   // 3. Extraccion de Osciladores
   double sma_d1_buffer[1];
   if(CopyBuffer(sma_d1_handle, 0, 0, 1, sma_d1_buffer) <= 0) return;
   
   double atr_d1_buffer[1];
   if(CopyBuffer(atr_d1_handle, 0, 0, 1, atr_d1_buffer) <= 0) return;
   
   double atr_buffer[1];
   if(CopyBuffer(atr_handle, 0, 0, 1, atr_buffer) <= 0) return;
   
   double current_sma_d1 = sma_d1_buffer[0];
   double current_atr_d1 = atr_d1_buffer[0];
   double current_atr = atr_buffer[0];
   
   MqlDateTime dt;
   TimeToStruct(TimeCurrent(), dt);
   double hour_of_day = (double)dt.hour;
   double day_of_week = (double)dt.day_of_week;
   
   double dist_sma200 = 0.0;
   if(current_atr_d1 != 0) dist_sma200 = (prices_micro[0] - current_sma_d1) / current_atr_d1;
   
   double session_vol_ratio = 0.0;
   if(current_atr_d1 != 0) session_vol_ratio = current_atr / current_atr_d1;
   
   // 4. Matriz de Filtrado
   bool filter_mtf = MathCore.Filter_MTF_Alignment(micro_vel_current, macro_vel_current, macro_accel);
   
   // Filtro de Exhaustion
   bool filter_exhaustion = MathCore.Filter_Kinematic_Exhaustion(prices_micro[0], macro_ahma_0, current_atr, InpMaxExhaustionRatio);
   if(!filter_exhaustion)
     {
      double ratio = MathAbs(prices_micro[0] - macro_ahma_0) / current_atr;
      PrintFormat("Señal abortada por Exhaustion Estructural - Ratio: %.2f", ratio);
     }
   
   // Parche Atomico: Captura de Tick sin lag
   MqlTick latest_tick;
   if(!SymbolInfoTick(_Symbol, latest_tick)) return;
   
   double sl_dist_points = (current_atr * InpStopLossATRMultiplier) / _Point;
   
   // 5. Maquina de Estados (Ejecucion Real)
   
   float norm_micro_vel = (float)(micro_vel_current / current_atr);
   float norm_micro_acc = (float)(micro_accel / current_atr);
   float norm_macro_vel = (float)(macro_vel_current / current_atr);
   
   // LONG: Velocidad > 0 Y Aceleracion > 0
   if(micro_vel_current > 0 && micro_accel > 0)
     {
      if(filter_mtf && filter_exhaustion)
        {
         double sl_price = latest_tick.ask - (current_atr * InpStopLossATRMultiplier);
         double volume = CalculateDynamicLot(sl_dist_points);
         if(InpMetaLabeling && metalabel_handle != INVALID_HANDLE)
           {
            float features[8] = {(float)1, norm_micro_vel, norm_micro_acc, norm_macro_vel, (float)((latest_tick.ask - macro_ahma_1) / current_atr), (float)hour_of_day, (float)day_of_week, (float)dist_sma200, (float)session_vol_ratio};
            long label[1];
            float probs[2];
            if(OnnxRun(metalabel_handle, ONNX_NO_CONVERSION, features, label, probs))
              {
               if(probs[1] < InpMetaThreshold) { PrintFormat("[META-LABELING] BUY VETADO (Prob: %.2f)", probs[1]); return; }
              }
           }
         if(trade.Buy(volume, _Symbol, latest_tick.ask, sl_price, 0, "Nexus LONG"))
           {
            if(InpDataHarvesting)
              {
               int size = ArraySize(telemetry_db);
               ArrayResize(telemetry_db, size + 1);
               telemetry_db[size].ticket = trade.ResultOrder();
               telemetry_db[size].open_time = TimeCurrent();
               telemetry_db[size].signal_type = 1;
               telemetry_db[size].micro_velocity = norm_micro_vel;
               telemetry_db[size].micro_acceleration = norm_micro_acc;
               telemetry_db[size].macro_velocity = norm_macro_vel;
               telemetry_db[size].tension_ratio = (latest_tick.ask - macro_ahma_1) / current_atr;
               telemetry_db[size].hour_of_day = hour_of_day;
               telemetry_db[size].day_of_week = day_of_week;
               telemetry_db[size].dist_sma200_atr = dist_sma200;
               telemetry_db[size].session_vol_ratio = session_vol_ratio;
              }
           }
        }
     }
     
   // SHORT: Velocidad < 0 Y Aceleracion < 0
   else if(micro_vel_current < 0 && micro_accel < 0)
     {
      if(filter_mtf && filter_exhaustion)
        {
         double sl_price = latest_tick.bid + (current_atr * InpStopLossATRMultiplier);
         double volume = CalculateDynamicLot(sl_dist_points);
         if(InpMetaLabeling && metalabel_handle != INVALID_HANDLE)
           {
            float features[8] = {(float)-1, norm_micro_vel, norm_micro_acc, norm_macro_vel, (float)((macro_ahma_1 - latest_tick.bid) / current_atr), (float)hour_of_day, (float)day_of_week, (float)dist_sma200, (float)session_vol_ratio};
            long label[1];
            float probs[2];
            if(OnnxRun(metalabel_handle, ONNX_NO_CONVERSION, features, label, probs))
              {
               if(probs[1] < InpMetaThreshold) { PrintFormat("[META-LABELING] SELL VETADO (Prob: %.2f)", probs[1]); return; }
              }
           }
         if(trade.Sell(volume, _Symbol, latest_tick.bid, sl_price, 0, "Nexus SHORT"))
           {
            if(InpDataHarvesting)
              {
               int size = ArraySize(telemetry_db);
               ArrayResize(telemetry_db, size + 1);
               telemetry_db[size].ticket = trade.ResultOrder();
               telemetry_db[size].open_time = TimeCurrent();
               telemetry_db[size].signal_type = -1;
               telemetry_db[size].micro_velocity = norm_micro_vel;
               telemetry_db[size].micro_acceleration = norm_micro_acc;
               telemetry_db[size].macro_velocity = norm_macro_vel;
               telemetry_db[size].tension_ratio = (macro_ahma_1 - latest_tick.bid) / current_atr;
               telemetry_db[size].hour_of_day = hour_of_day;
               telemetry_db[size].day_of_week = day_of_week;
               telemetry_db[size].dist_sma200_atr = dist_sma200;
               telemetry_db[size].session_vol_ratio = session_vol_ratio;
              }
           }
        }
     }
  }

//+------------------------------------------------------------------+
//| Trade Management (Trailing Stop & Inter-Dimensional Exits)       |
//+------------------------------------------------------------------+
void ManageOpenPositions()
  {
   if(PositionsTotal() == 0) return;
   
   double atr_buffer[1];
   if(CopyBuffer(atr_handle, 0, 0, 1, atr_buffer) <= 0) return;
   double current_atr = atr_buffer[0];
   
   MqlTick latest_tick;
   if(!SymbolInfoTick(_Symbol, latest_tick)) return;
   
   int count = InpBaseAHMAPeriod + InpERPeriod + 10;
   double prices_micro[];
   if(CopyClose(_Symbol, _Period, 1, count, prices_micro) <= 0) return;
   ArraySetAsSeries(prices_micro, true);
   
   double fast_ahma = MathFast.GetAHMA(0, prices_micro);
   double base_ahma = MathBase.GetAHMA(0, prices_micro);
   
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      string symbol = PositionGetSymbol(i);
      if(symbol != _Symbol) continue;
      
      ulong ticket = PositionGetInteger(POSITION_TICKET);
      double open_price = PositionGetDouble(POSITION_PRICE_OPEN);
      double current_sl = PositionGetDouble(POSITION_SL);
      long type = PositionGetInteger(POSITION_TYPE);
      
      bool guardian_shield_active = false;
      
      if(type == POSITION_TYPE_BUY)
        {
         if((latest_tick.bid - open_price) > current_atr) guardian_shield_active = true;
         
         if(guardian_shield_active && fast_ahma < base_ahma)
           {
            trade.PositionClose(ticket);
            continue;
           }
           
         double new_sl = latest_tick.bid - (current_atr * InpTrailingATR);
         if(new_sl > current_sl || current_sl == 0)
           {
            trade.PositionModify(ticket, new_sl, 0);
           }
        }
      else if(type == POSITION_TYPE_SELL)
        {
         if((open_price - latest_tick.ask) > current_atr) guardian_shield_active = true;
         
         if(guardian_shield_active && fast_ahma > base_ahma)
           {
            trade.PositionClose(ticket);
            continue;
           }
           
         double new_sl = latest_tick.ask + (current_atr * InpTrailingATR * 0.6);
         if(new_sl < current_sl || current_sl == 0)
           {
            trade.PositionModify(ticket, new_sl, 0);
           }
        }
     }
  }

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
  {
   ManageOpenPositions();
   
   static datetime last_time = 0;
   datetime current_time = iTime(_Symbol, _Period, 0);
   
   if(current_time != last_time)
     {
      last_time = current_time;
      EvaluateEntrySignal();
     }
  }
//+------------------------------------------------------------------+
