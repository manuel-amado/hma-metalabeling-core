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
input int    InpMaxPeriod     = 70;        // AHMA Max Period (Range)
input int    InpERPeriod      = 14;        // Kaufman ER Period

input group "=== Institutional Filters ==="
input double InpMinADX        = 25.0;      // Minimum ADX (Inertia)
input double InpOversold      = 30.0;      // RSI Oversold (Block Sells)
input double InpOverbought    = 70.0;      // RSI Overbought (Block Buys)
input ENUM_TIMEFRAMES InpMacroTF = PERIOD_H4; // MTF Macro Timeframe

input group "=== Risk & Execution ==="
input double InpRiskPercent            = 1.0; // Risk per Trade (%)
input double InpStopLossATRMultiplier  = 2.2; // Stop Loss (ATR Multiplier)

input group "=== Trade Management ==="
input double InpTrailingATR            = 3.0; // Trailing Stop (ATR Multiplier)
input int    InpFastAHMAPeriod         = 15;  // AHMA Fast Period (Exit)
input int    InpBaseAHMAPeriod         = 50;  // AHMA Base Period (Exit)

//+------------------------------------------------------------------+
//| Global Variables                                                 |
//+------------------------------------------------------------------+
CAHMA_Kinematics *MathCore;
CAHMA_Kinematics *MathFast;
CAHMA_Kinematics *MathBase;

int adx_handle;
int rsi_handle;
int atr_handle;

CTrade trade;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
  {
   // Inicializar Núcleos Matemáticos
   MathCore = new CAHMA_Kinematics(InpMinPeriod, InpMaxPeriod, InpERPeriod);
   
   // Para salidas, creamos dos instancias con base dinámica
   MathFast = new CAHMA_Kinematics(MathMax(2, InpFastAHMAPeriod/2), InpFastAHMAPeriod, InpERPeriod);
   MathBase = new CAHMA_Kinematics(MathMax(5, InpBaseAHMAPeriod/2), InpBaseAHMAPeriod, InpERPeriod);
   
   // Inicializar Handles de Osciladores Estándar
   adx_handle = iADX(_Symbol, _Period, 14);
   rsi_handle = iRSI(_Symbol, _Period, 14, PRICE_CLOSE);
   atr_handle = iATR(_Symbol, _Period, 14);
   
   if(adx_handle == INVALID_HANDLE || rsi_handle == INVALID_HANDLE || atr_handle == INVALID_HANDLE)
     {
      Print("Error: No se pudieron cargar los indicadores.");
      return(INIT_FAILED);
     }
     
   trade.SetExpertMagicNumber(999901); // Nexus Alpha
   
   return(INIT_SUCCEEDED);
  }

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
   if(MathCore != NULL) delete MathCore;
   if(MathFast != NULL) delete MathFast;
   if(MathBase != NULL) delete MathBase;
   
   IndicatorRelease(adx_handle);
   IndicatorRelease(rsi_handle);
   IndicatorRelease(atr_handle);
  }

//+------------------------------------------------------------------+
//| Cálculo de Lotaje Dinámico                                       |
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
   
   // Normalización según el broker
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
   // Evitar abrir si ya tenemos posición
   if(PositionsTotal() > 0) return;
   
   int count = InpMaxPeriod + InpERPeriod + 10;
   
   // 1. Cinemática MICRO
   double prices_micro[];
   if(CopyClose(_Symbol, _Period, 0, count + 2, prices_micro) <= 0) return;
   ArraySetAsSeries(prices_micro, true);
   
   double ahma_0 = MathCore.GetAHMA(0, prices_micro);
   double ahma_1 = MathCore.GetAHMA(1, prices_micro);
   double ahma_2 = MathCore.GetAHMA(2, prices_micro);
   
   double micro_vel_current = MathCore.GetVelocity(ahma_0, ahma_1);
   double micro_vel_prev = MathCore.GetVelocity(ahma_1, ahma_2);
   double micro_accel = MathCore.GetAcceleration(micro_vel_current, micro_vel_prev);
   
   // 2. Cinemática MACRO
   double prices_macro[];
   if(CopyClose(_Symbol, InpMacroTF, 0, count + 1, prices_macro) <= 0) return;
   ArraySetAsSeries(prices_macro, true);
   
   double macro_ahma_0 = MathCore.GetAHMA(0, prices_macro);
   double macro_ahma_1 = MathCore.GetAHMA(1, prices_macro);
   double macro_vel_current = MathCore.GetVelocity(macro_ahma_0, macro_ahma_1);
   
   // 3. Extracción de Osciladores
   double adx_buffer[1], rsi_buffer[1], atr_buffer[1];
   if(CopyBuffer(adx_handle, 0, 0, 1, adx_buffer) <= 0) return;
   if(CopyBuffer(rsi_handle, 0, 0, 1, rsi_buffer) <= 0) return;
   if(CopyBuffer(atr_handle, 0, 0, 1, atr_buffer) <= 0) return;
   
   double current_adx = adx_buffer[0];
   double current_rsi = rsi_buffer[0];
   double current_atr = atr_buffer[0];
   
   // 4. Matriz de Filtrado
   bool filter_mtf = MathCore.Filter_MTF_Alignment(micro_vel_current, macro_vel_current);
   bool filter_adx = MathCore.Filter_ADX_Momentum(current_adx, InpMinADX);
   
   // Parche Atómico: Captura de Tick sin lag
   MqlTick latest_tick;
   if(!SymbolInfoTick(_Symbol, latest_tick)) return;
   
   double sl_dist_points = (current_atr * InpStopLossATRMultiplier) / _Point;
   
   // 5. Máquina de Estados (Ejecución Real)
   
   // LONG: Velocidad > 0 Y Aceleración > 0
   if(micro_vel_current > 0 && micro_accel > 0)
     {
      bool filter_rsi = MathCore.Filter_RSI_FOMO(current_rsi, 1, InpOversold, InpOverbought);
      if(filter_mtf && filter_adx && filter_rsi)
        {
         double sl_price = latest_tick.ask - (current_atr * InpStopLossATRMultiplier);
         double volume = CalculateDynamicLot(sl_dist_points);
         trade.Buy(volume, _Symbol, latest_tick.ask, sl_price, 0, "Nexus LONG");
        }
     }
     
   // SHORT: Velocidad < 0 Y Aceleración < 0
   else if(micro_vel_current < 0 && micro_accel < 0)
     {
      bool filter_rsi = MathCore.Filter_RSI_FOMO(current_rsi, -1, InpOversold, InpOverbought);
      if(filter_mtf && filter_adx && filter_rsi)
        {
         double sl_price = latest_tick.bid + (current_atr * InpStopLossATRMultiplier);
         double volume = CalculateDynamicLot(sl_dist_points);
         trade.Sell(volume, _Symbol, latest_tick.bid, sl_price, 0, "Nexus SHORT");
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
   
   // Parche Atómico para precios actuales
   MqlTick latest_tick;
   if(!SymbolInfoTick(_Symbol, latest_tick)) return;
   
   // Pre-calcular AHMAs para la Salida Cinemática
   int count = InpBaseAHMAPeriod + InpERPeriod + 10;
   double prices_micro[];
   if(CopyClose(_Symbol, _Period, 0, count, prices_micro) <= 0) return;
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
      
      // Escudo Guardián: Beneficio flotante > 1.0x ATR
      bool guardian_shield_active = false;
      
      if(type == POSITION_TYPE_BUY)
        {
         if((latest_tick.bid - open_price) > current_atr) guardian_shield_active = true;
         
         // 1. Salida Cinemática Inter-Dimensional
         if(guardian_shield_active && fast_ahma < base_ahma)
           {
            trade.PositionClose(ticket);
            continue;
           }
           
         // 2. Trailing Stop
         double new_sl = latest_tick.bid - (current_atr * InpTrailingATR);
         if(new_sl > current_sl || current_sl == 0)
           {
            trade.PositionModify(ticket, new_sl, 0);
           }
        }
      else if(type == POSITION_TYPE_SELL)
        {
         if((open_price - latest_tick.ask) > current_atr) guardian_shield_active = true;
         
         // 1. Salida Cinemática Inter-Dimensional
         if(guardian_shield_active && fast_ahma > base_ahma)
           {
            trade.PositionClose(ticket);
            continue;
           }
           
         // 2. Trailing Stop Asimétrico (Modificador de Gravedad 0.6x)
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
   // 1. Gestión constante por cada tick (Trailing y Salidas Rápidas)
   ManageOpenPositions();
   
   // 2. Evaluación de nuevas entradas solo al cierre de vela
   static datetime last_time = 0;
   datetime current_time = iTime(_Symbol, _Period, 0);
   
   if(current_time != last_time)
     {
      last_time = current_time;
      EvaluateEntrySignal();
     }
  }
//+------------------------------------------------------------------+
