import re

with open('Hull_Apex_Bot.mq5', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# Buscamos donde empieza EvaluateEntrySignal
start_idx = text.find('void EvaluateEntrySignal()')

# Buscamos donde empieza ManageOpenPositions
end_idx = text.find('void ManageOpenPositions()')

if start_idx == -1 or end_idx == -1:
    print('No se encontro EvaluateEntrySignal o ManageOpenPositions')
    exit()

# Buscamos la cabecera de ManageOpenPositions
end_idx = text.rfind('//+', 0, end_idx)

replacement = '''void EvaluateEntrySignal()
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
   double adx_buffer[1], rsi_buffer[1], atr_buffer[1];
   if(CopyBuffer(adx_handle, 0, 0, 1, adx_buffer) <= 0) return;
   if(CopyBuffer(rsi_handle, 0, 0, 1, rsi_buffer) <= 0) return;
   if(CopyBuffer(atr_handle, 0, 0, 1, atr_buffer) <= 0) return;
   
   double current_adx = adx_buffer[0];
   double current_rsi = rsi_buffer[0];
   double current_atr = atr_buffer[0];
   
   // 4. Matriz de Filtrado
   bool filter_mtf = MathCore.Filter_MTF_Alignment(micro_vel_current, macro_vel_current, macro_accel);
   bool filter_adx = MathCore.Filter_ADX_Momentum(current_adx, InpMinADX);
   
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
      bool filter_rsi = MathCore.Filter_RSI_FOMO(current_rsi, 1, InpOversold, InpOverbought);
      if(filter_mtf && filter_adx && filter_rsi && filter_exhaustion)
        {
         double sl_price = latest_tick.ask - (current_atr * InpStopLossATRMultiplier);
         double volume = CalculateDynamicLot(sl_dist_points);
         if(InpMetaLabeling && metalabel_handle != INVALID_HANDLE)
           {
            float features[8] = {(float)1, norm_micro_vel, norm_micro_acc, norm_macro_vel, (float)((latest_tick.ask - macro_ahma_1) / current_atr), (float)0.0, (float)current_adx, (float)current_rsi};
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
               telemetry_db[size].er_kaufman = 0.0;
               telemetry_db[size].adx_value = current_adx;
               telemetry_db[size].rsi_value = current_rsi;
              }
           }
        }
     }
     
   // SHORT: Velocidad < 0 Y Aceleracion < 0
   else if(micro_vel_current < 0 && micro_accel < 0)
     {
      bool filter_rsi = MathCore.Filter_RSI_FOMO(current_rsi, -1, InpOversold, InpOverbought);
      if(filter_mtf && filter_adx && filter_rsi && filter_exhaustion)
        {
         double sl_price = latest_tick.bid + (current_atr * InpStopLossATRMultiplier);
         double volume = CalculateDynamicLot(sl_dist_points);
         if(InpMetaLabeling && metalabel_handle != INVALID_HANDLE)
           {
            float features[8] = {(float)-1, norm_micro_vel, norm_micro_acc, norm_macro_vel, (float)((macro_ahma_1 - latest_tick.bid) / current_atr), (float)0.0, (float)current_adx, (float)current_rsi};
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
               telemetry_db[size].er_kaufman = 0.0;
               telemetry_db[size].adx_value = current_adx;
               telemetry_db[size].rsi_value = current_rsi;
              }
           }
        }
     }
  }

'''

new_text = text[:start_idx] + replacement + text[end_idx:]

with open('Hull_Apex_Bot.mq5', 'w', encoding='utf-8') as f:
    f.write(new_text)

print('Arreglado!')

