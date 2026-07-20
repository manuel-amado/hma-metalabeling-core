# Orchestrator Changes History

## Step 543 - Tool Call: multi_replace_file_content
**Instruction:** "Add CalcDynamicLot function before OnTick. Update PositionOpen call to use the calculated dynamic lot. Inject Balance, Lots_Utilizados, and SL_Pips_Reales into the MarketSnapshot array."
**Description:** "Updated MQL5 Orchestrator to use 1% dynamic lot sizing based on Account Balance, replacing the 0.1 hardcoded logic. Injected financial values (Balance, Lots, SL Pips) into the snapshot."

```json
{
  "Description": "\"Updated MQL5 Orchestrator to use 1% dynamic lot sizing based on Account Balance, replacing the 0.1 hardcoded logic. Injected financial values (Balance, Lots, SL Pips) into the snapshot.\"",
  "Instruction": "\"Add CalcDynamicLot function before OnTick. Update PositionOpen call to use the calculated dynamic lot. Inject Balance, Lots_Utilizados, and SL_Pips_Reales into the MarketSnapshot array.\"",
  "ReplacementChunks": "[{\"AllowMultiple\":false,\"EndLine\":136,\"ReplacementContent\":\"    }\\n}\\n\\n//+------------------------------------------------------------------+\\n//| CalcDynamicLot: 1% Risk over Balance                             |\\n//+------------------------------------------------------------------+\\ndouble CalcDynamicLot(double sl_dist_price)\\n{\\n    if(sl_dist_price <= 0) return 0.0;\\n    \\n    double risk_pct = 1.0;\\n    double balance = AccountInfoDouble(ACCOUNT_BALANCE);\\n    double risk_money = balance * (risk_pct / 100.0);\\n    \\n    double tick_size = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);\\n    double tick_value = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);\\n    \\n    if(tick_size <= 0 || tick_value <= 0) return 0.0;\\n    \\n    double ticks = sl_dist_price / tick_size;\\n    double money_per_lot = ticks * tick_value;\\n    \\n    if(money_per_lot <= 0) return 0.0;\\n    \\n    double lots = risk_money / money_per_lot;\\n    \\n    // Normalize lots\\n    double min_lot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);\\n    double max_lot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);\\n    double step_lot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);\\n    \\n    lots = MathRound(lots / step_lot) * step_lot;\\n    if(lots < min_lot) lots = min_lot;\\n    if(lots > max_lot) lots = max_lot;\\n    \\n    return lots;\\n}\\n\\n//+------------------------------------------------------------------+\\n//| OnTick - Motor Principal (Alto Recall, Cero Cliff Effects)       |\\n//+------------------------------------------------------------------+\",\"StartLine\":134,\"TargetContent\":\"    }\\n}\\n\\n\\n//+------------------------------------------------------------------+\\n//| OnTick - Motor Principal (Alto Recall, Cero Cliff Effects)       |\\n//+------------------------------------------------------------------+\"},{\"AllowMultiple\":false,\"EndLine\":273,\"ReplacementContent\":\"    // FASE 1.2: Guardar slDist en pips para calcular Max_RR_Achieved al cerrar\\n    // Se almacena directamente en el snapshot; el Logger lo usa al CommmitTrade\\n   \n<truncated 1463 bytes>",
  "TargetFile": "\"c:\\\\Users\\\\Manuel\\\\Desktop\\\\HMA_MetaLabeling\\\\MQL5_Engine\\\\HMA_ML_Orchestrator.mq5\"",
  "toolAction": "\"Updating MQL5 EA risk dynamics\"",
  "toolSummary": "\"Update MQL5 EA\""
}
```

## Step 544 - Tool Response
```diff
@@ -132,6 +132,40 @@
     }
 }
 
+//+------------------------------------------------------------------+
+//| CalcDynamicLot: 1% Risk over Balance                             |
+//+------------------------------------------------------------------+
+double CalcDynamicLot(double sl_dist_price)
+{
+    if(sl_dist_price <= 0) return 0.0;
+    
+    double risk_pct = 1.0;
+    double balance = AccountInfoDouble(ACCOUNT_BALANCE);
+    double risk_money = balance * (risk_pct / 100.0);
+    
+    double tick_size = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
+    double tick_value = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
+    
+    if(tick_size <= 0 || tick_value <= 0) return 0.0;
+    
+    double ticks = sl_dist_price / tick_size;
+    double money_per_lot = ticks * tick_value;
+    
+    if(money_per_lot <= 0) return 0.0;
+    
+    double lots = risk_money / money_per_lot;
+    
+    // Normalize lots
+    double min_lot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
+    double max_lot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
+    double step_lot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
+    
+    lots = MathRound(lots / step_lot) * step_lot;
+    if(lots < min_lot) lots = min_lot;
+    if(lots > max_lot) lots = max_lot;
+    
+    return lots;
+}
 
 //+------------------------------------------------------------------+
 //| OnTick - Motor Principal (Alto Recall, Cero Cliff Effects)       |
@@ -266,9 +266,12 @@
     // Se almacena directamente en el snapshot; el Logger lo usa al CommmitTrade
     // para calcular: Max_RR = MFE_precio / slDist
 
-    // === EJECUCION: Abrir posicion (lot fijo para dataset) ===
+    // === EJECUCION: Abrir posicion (Lote Dinamico 1%) ===
+    double lots_to_trade = CalcDynamicLot(slDist);
+    if(lots_to_trade <= 0) return;
+
     if(trade.PositionOpen(_Symbol, (ENUM_ORDER_TYPE)signalType,
-                          0.1, entry_price, sl, tp, "HMA_ML"))
+                          lots_to_trade, entry_price, sl, tp, "HMA_ML"))
     {
         ulong pos_ticket = trade.ResultDeal();
 
@@ -300,6 +300,11 @@
         // FASE 1.2: Guardar slDist en precio para Max_RR_Achieved
         snap.sl_dist_price       = slDist;
 
+        // FASE Riesgo Dinámico
+        snap.balance_momento     = AccountInfoDouble(ACCOUNT_BALANCE);
+        snap.lots_utilizados     = lots_to_trade;
+        snap.sl_pips_reales      = slDist / pip;
+
         // Targets Y: se rellenan en CommitTrade (OnTradeTransaction)
 
         logger.RecordSignal(snap);
```

## Step 596 - Tool Call: multi_replace_file_content
**Instruction:** "Update CalcDynamicLot in HMA_ML_Orchestrator.mq5 to include the requested Print statement for Risk debugging."
**Description:** "Added Print debugging and forced minimum lot volume to CalcDynamicLot in HMA_ML_Orchestrator.mq5."

```json
{
  "Description": "\"Added Print debugging and forced minimum lot volume to CalcDynamicLot in HMA_ML_Orchestrator.mq5.\"",
  "Instruction": "\"Update CalcDynamicLot in HMA_ML_Orchestrator.mq5 to include the requested Print statement for Risk debugging.\"",
  "ReplacementChunks": "[{\"AllowMultiple\":false,\"EndLine\":166,\"ReplacementContent\":\"    double min_lot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);\\n    double max_lot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);\\n    double step_lot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);\\n    \\n    lots = MathRound(lots / step_lot) * step_lot;\\n    if(lots < min_lot) lots = min_lot;\\n    if(lots > max_lot) lots = max_lot;\\n    \\n    Print(\\\"[RISK] SL Puntos: \\\", sl_dist_price, \\\" | Lotes Calculados: \\\", lots, \\\" | Balance: \\\", balance);\\n    \\n    return lots;\\n}\",\"StartLine\":157,\"TargetContent\":\"    double min_lot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);\\n    double max_lot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);\\n    double step_lot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);\\n    \\n    lots = MathRound(lots / step_lot) * step_lot;\\n    if(lots < min_lot) lots = min_lot;\\n    if(lots > max_lot) lots = max_lot;\\n    \\n    return lots;\\n}\"}]",
  "TargetFile": "\"c:\\\\Users\\\\Manuel\\\\Desktop\\\\HMA_MetaLabeling\\\\MQL5_Engine\\\\HMA_ML_Orchestrator.mq5\"",
  "toolAction": "\"Adding risk Print to EA\"",
  "toolSummary": "\"Update EA debugging\""
}
```

## Step 597 - Tool Response
```diff
@@ -164,6 +164,8 @@
     if(lots < min_lot) lots = min_lot;
     if(lots > max_lot) lots = max_lot;
     
+    Print("[RISK] SL Puntos: ", sl_dist_price, " | Lotes Calculados: ", lots, " | Balance: ", balance);
+    
     return lots;
 }
```

## Step 605 - Tool Call: multi_replace_file_content
**Instruction:** "Replace the CalcDynamicLot function entirely with the new math structure ensuring target_lots and lots_normalizados use the MathFloor formula correctly."
**Description:** "Replaced CalcDynamicLot in MQL5 to strictly match the requested mathematical formula using MathFloor and precise tick calculations, eliminating mathematical discrepancy."

```json
{
  "Description": "\"Replaced CalcDynamicLot in MQL5 to strictly match the requested mathematical formula using MathFloor and precise tick calculations, eliminating mathematical discrepancy.\"",
  "Instruction": "\"Replace the CalcDynamicLot function entirely with the new math structure ensuring target_lots and lots_normalizados use the MathFloor formula correctly.\"",
  "ReplacementChunks": "[{\"AllowMultiple\":false,\"EndLine\":168,\"ReplacementContent\":\"double CalcDynamicLot(double sl_distancia_precio)\\n{\\n    if(sl_distancia_precio <= 0) return 0.0;\\n    \\n    double balance = AccountInfoDouble(ACCOUNT_BALANCE);\\n    double riesgo_monetario = balance * 0.01;\\n    \\n    double tick_value = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);\\n    double tick_size = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);\\n    \\n    if(tick_size <= 0 || tick_value <= 0) return 0.0;\\n    \\n    double target_lots = riesgo_monetario / ((sl_distancia_precio / tick_size) * tick_value);\\n    \\n    double lot_step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);\\n    double lots_normalizados = MathFloor(target_lots / lot_step) * lot_step;\\n    \\n    double min_lot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);\\n    double max_lot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);\\n    \\n    if(lots_normalizados < min_lot) lots_normalizados = min_lot;\\n    if(lots_normalizados > max_lot) lots_normalizados = max_lot;\\n    \\n    Print(\\\"[RISK] SL Precio: \\\", sl_distancia_precio, \\\" | Lotes Calculados: \\\", lots_normalizados, \\\" | Riesgo (USD): \\\", riesgo_monetario);\\n    \\n    return lots_normalizados;\\n}\",\"StartLine\":138,\"TargetContent\":\"double CalcDynamicLot(double sl_dist_price)\\n{\\n    if(sl_dist_price <= 0) return 0.0;\\n    \\n    double risk_pct = 1.0;\\n    double balance = AccountInfoDouble(ACCOUNT_BALANCE);\\n    double risk_money = balance * (risk_pct / 100.0);\\n    \\n    double tick_size = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);\\n    double tick_value = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);\\n    \\n    if(tick_size <= 0 || tick_value <= 0) return 0.0;\\n    \\n    double ticks = sl_dist_price / tick_size;\\n    double money_per_lot = ticks * tick_value;\\n    \\n    if(money_per_lot <= 0) return 0.0;\\n    \\n    double lots = risk_money / money_per_lot;\\n    \\n    // Normalize lots\\n    double min_lot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);\\n    double max_lot = SymbolInfoDouble(_Symbol, SY\n<truncated 371 bytes>",
  "TargetFile": "\"c:\\\\Users\\\\Manuel\\\\Desktop\\\\HMA_MetaLabeling\\\\MQL5_Engine\\\\HMA_ML_Orchestrator.mq5\"",
  "toolAction": "\"Fixing CalcDynamicLot logic\"",
  "toolSummary": "\"Fix CalcDynamicLot math\""
}
```

## Step 606 - Tool Response
```diff
@@ -135,38 +135,32 @@
 //+------------------------------------------------------------------+
 //| CalcDynamicLot: 1% Risk over Balance                             |
 //+------------------------------------------------------------------+
-double CalcDynamicLot(double sl_dist_price)
-{
-    if(sl_dist_price <= 0) return 0.0;
-    
-    double risk_pct = 1.0;
+double CalcDynamicLot(double sl_distancia_precio)
+{
+    if(sl_distancia_precio <= 0) return 0.0;
+    
     double balance = AccountInfoDouble(ACCOUNT_BALANCE);
-    double risk_money = balance * (risk_pct / 100.0);
-    
-    double tick_size = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
+    double riesgo_monetario = balance * 0.01;
+    
     double tick_value = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
+    double tick_size = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
     
     if(tick_size <= 0 || tick_value <= 0) return 0.0;
     
-    double ticks = sl_dist_price / tick_size;
-    double money_per_lot = ticks * tick_value;
-    
-    if(money_per_lot <= 0) return 0.0;
-    
-    double lots = risk_money / money_per_lot;
-    
-    // Normalize lots
+    double target_lots = riesgo_monetario / ((sl_distancia_precio / tick_size) * tick_value);
+    
+    double lot_step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
+    double lots_normalizados = MathFloor(target_lots / lot_step) * lot_step;
+    
     double min_lot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
     double max_lot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
-    double step_lot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
-    
-    lots = MathRound(lots / step_lot) * step_lot;
-    if(lots < min_lot) lots = min_lot;
-    if(lots > max_lot) lots = max_lot;
-    
-    Print("[RISK] SL Puntos: ", sl_dist_price, " | Lotes Calculados: ", lots, " | Balance: ", balance);
-    
-    return lots;
+    
+    if(lots_normalizados < min_lot) lots_normalizados = min_lot;
+    if(lots_normalizados > max_lot) lots_normalizados = max_lot;
+    
+    Print("[RISK] SL Precio: ", sl_distancia_precio, " | Lotes Calculados: ", lots_normalizados, " | Riesgo (USD): ", riesgo_monetario);
+    
+    return lots_normalizados;
 }
 
 //+------------------------------------------------------------------+
```

## Step 617 - Tool Call: multi_replace_file_content
**Instruction:** "Update slDist calculation to explicitly use (Ask - sl) or (sl - Bid). Remove the TakeProfitMultiplier logic and set tp to 0.0 to prevent premature truncation of the MFE curve."
**Description:** "Fixed the Bid/Ask spread calculation for explicit slDist in HMA_ML_Orchestrator.mq5, and removed the fixed TP limit to allow true MFE calculation up to the Stop Loss or Time Barrier."

```json
{
  "Description": "\"Fixed the Bid/Ask spread calculation for explicit slDist in HMA_ML_Orchestrator.mq5, and removed the fixed TP limit to allow true MFE calculation up to the Stop Loss or Time Barrier.\"",
  "Instruction": "\"Update slDist calculation to explicitly use (Ask - sl) or (sl - Bid). Remove the TakeProfitMultiplier logic and set tp to 0.0 to prevent premature truncation of the MFE curve.\"",
  "ReplacementChunks": "[{\"AllowMultiple\":false,\"EndLine\":295,\"ReplacementContent\":\"    double sl = (signalType == 0)\\n                ? GetLowestLow(LookbackBars)\\n                : GetHighestHigh(LookbackBars);\\n\\n    if(sl == 0) return; // SL invalido\\n\\n    double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);\\n    double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);\\n    double slDist = (signalType == 0) ? (ask - sl) : (sl - bid);\\n    \\n    if(slDist <= 0) return;\\n\\n    // FASE 2: Eliminacion del sesgo del TP fijo (True MFE Discovery)\\n    // Se fuerza el TP a 0 para que la operacion solo se cierre por SL o por la Barrera de Tiempo.\\n    // Esto permite al Logger registrar el verdadero Maximo Recorrido a Favor (MFE) sin truncarlo artificialmente.\\n    double tp = 0.0;\\n\\n    // Feature 15: SL Distance normalizada por ATR\\n    double sl_dist_atr = (current_atr > 0) ? slDist / current_atr : 0.0;\",\"StartLine\":280,\"TargetContent\":\"    double sl = (signalType == 0)\\n                ? GetLowestLow(LookbackBars)\\n                : GetHighestHigh(LookbackBars);\\n\\n    if(sl == 0) return; // SL invalido\\n\\n    double slDist = MathAbs(entry_price - sl);\\n    if(slDist <= 0) return;\\n\\n    double tp = (signalType == 0)\\n                ? entry_price + slDist * TakeProfitMultiplier\\n                : entry_price - slDist * TakeProfitMultiplier;\\n\\n    // Feature 15: SL Distance normalizada por ATR\\n    double sl_dist_atr = (current_atr > 0) ? slDist / current_atr : 0.0;\"}]",
  "TargetFile": "\"c:\\\\Users\\\\Manuel\\\\Desktop\\\\HMA_MetaLabeling\\\\MQL5_Engine\\\\HMA_ML_Orchestrator.mq5\"",
  "toolAction": "\"Fixing TP bias and Bid/Ask spread\"",
  "toolSummary": "\"Fix MFE and Spread logic\""
}
```

## Step 618 - Tool Response
```diff
@@ -283,12 +283,16 @@
 
     if(sl == 0) return; // SL invalido
 
-    double slDist = MathAbs(entry_price - sl);
+    double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
+    double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
+    double slDist = (signalType == 0) ? (ask - sl) : (sl - bid);
+    
     if(slDist <= 0) return;
 
-    double tp = (signalType == 0)
-                ? entry_price + slDist * TakeProfitMultiplier
-                : entry_price - slDist * TakeProfitMultiplier;
+    // FASE 2: Eliminacion del sesgo del TP fijo (True MFE Discovery)
+    // Se fuerza el TP a 0 para que la operacion solo se cierre por SL o por la Barrera de Tiempo.
+    // Esto permite al Logger registrar el verdadero Maximo Recorrido a Favor (MFE) sin truncarlo artificialmente.
+    double tp = 0.0;
 
     // Feature 15: SL Distance normalizada por ATR
     double sl_dist_atr = (current_atr > 0) ? slDist / current_atr : 0.0;
```

## Step 626 - Tool Call: multi_replace_file_content
**Instruction:** "Replace CalcDynamicLot with the new order_type aware signature. Update the lots_to_trade call inside OnTick to pass (ENUM_ORDER_TYPE)signalType and sl."
**Description:** "Updated CalcDynamicLot with the strict exact Ask/Bid rules and exact target logic provided by the user. Updated OrderSend setup to use this new signature."

```json
{
  "Description": "\"Updated CalcDynamicLot with the strict exact Ask/Bid rules and exact target logic provided by the user. Updated OrderSend setup to use this new signature.\"",
  "Instruction": "\"Replace CalcDynamicLot with the new order_type aware signature. Update the lots_to_trade call inside OnTick to pass (ENUM_ORDER_TYPE)signalType and sl.\"",
  "ReplacementChunks": "[{\"AllowMultiple\":false,\"EndLine\":167,\"ReplacementContent\":\"double CalcDynamicLot(ENUM_ORDER_TYPE order_type, double sl_price)\\n{\\n    double sl_dist_price = 0.0;\\n    if(order_type == ORDER_TYPE_BUY) {\\n        sl_dist_price = MathAbs(SymbolInfoDouble(_Symbol, SYMBOL_ASK) - sl_price);\\n    } else {\\n        sl_dist_price = MathAbs(sl_price - SymbolInfoDouble(_Symbol, SYMBOL_BID));\\n    }\\n    \\n    if(sl_dist_price <= 0) return 0.0;\\n    \\n    double risk_money = AccountInfoDouble(ACCOUNT_BALANCE) * 0.01;\\n    double tick_size = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);\\n    double tick_value = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);\\n    \\n    if(tick_size <= 0 || tick_value <= 0) return 0.0;\\n    \\n    double loss_ticks = sl_dist_price / tick_size;\\n    double raw_lots = risk_money / (loss_ticks * tick_value);\\n    \\n    double vol_step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);\\n    double final_lots = MathFloor(raw_lots / vol_step) * vol_step;\\n    \\n    double min_lot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);\\n    double max_lot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);\\n    \\n    if(final_lots < min_lot) final_lots = min_lot;\\n    if(final_lots > max_lot) final_lots = max_lot;\\n    \\n    Print(\\\"[RISK CALC] Type: \\\", EnumToString(order_type), \\\" | Dist Puntos: \\\", loss_ticks, \\\" | Raw Lots (1000$): \\\", raw_lots, \\\" | Lots Truncados (Broker): \\\", final_lots);\\n    \\n    return final_lots;\\n}\",\"StartLine\":138,\"TargetContent\":\"double CalcDynamicLot(double sl_distancia_precio)\\n{\\n    if(sl_distancia_precio <= 0) return 0.0;\\n    \\n    double balance = AccountInfoDouble(ACCOUNT_BALANCE);\\n    double riesgo_monetario = balance * 0.01;\\n    \\n    double tick_value = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);\\n    double tick_size = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);\\n    \\n    if(tick_size <= 0 || tick_value <= 0) return 0.0;\\n    \\n    double target_lots = riesgo_monetario / ((sl_distancia_precio / tick_size) * tick_value);\\n    \\n    double lot_st\n<truncated 1380 bytes>",
  "TargetFile": "\"c:\\\\Users\\\\Manuel\\\\Desktop\\\\HMA_MetaLabeling\\\\MQL5_Engine\\\\HMA_ML_Orchestrator.mq5\"",
  "toolAction": "\"Updating risk functions in EA\"",
  "toolSummary": "\"Update risk calc\""
}
```

## Step 627 - Tool Response
```diff
@@ -135,22 +135,28 @@
 //+------------------------------------------------------------------+
 //| CalcDynamicLot: 1% Risk over Balance                             |
 //+------------------------------------------------------------------+
-double CalcDynamicLot(double sl_distancia_precio)
-{
-    if(sl_distancia_precio <= 0) return 0.0;
-    
-    double balance = AccountInfoDouble(ACCOUNT_BALANCE);
-    double riesgo_monetario = balance * 0.01;
-    
-    double tick_value = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
+double CalcDynamicLot(ENUM_ORDER_TYPE order_type, double sl_price)
+{
+    double sl_dist_price = 0.0;
+    if(order_type == ORDER_TYPE_BUY) {
+        sl_dist_price = MathAbs(SymbolInfoDouble(_Symbol, SYMBOL_ASK) - sl_price);
+    } else {
+        sl_dist_price = MathAbs(sl_price - SymbolInfoDouble(_Symbol, SYMBOL_BID));
+    }
+    
+    if(sl_dist_price <= 0) return 0.0;
+    
+    double risk_money = AccountInfoDouble(ACCOUNT_BALANCE) * 0.01;
     double tick_size = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
+    double tick_value = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
     
     if(tick_size <= 0 || tick_value <= 0) return 0.0;
     
-    double target_lots = riesgo_monetario / ((sl_distancia_precio / tick_size) * tick_value);
-    
-    double lot_step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
-    double lots_normalizados = MathFloor(target_lots / lot_step) * lot_step;
+    double loss_ticks = sl_dist_price / tick_size;
+    double raw_lots = risk_money / (loss_ticks * tick_value);
+    
+    double vol_step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
+    double final_lots = MathFloor(raw_lots / vol_step) * vol_step;
     
     double min_lot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
     double max_lot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
@@ -157,9 +157,9 @@
-    if(lots_normalizados < min_lot) lots_normalizados = min_lot;
-    if(lots_normalizados > max_lot) lots_normalizados = max_lot;
-    
-    Print("[RISK] SL Precio: ", sl_distancia_precio, " | Lotes Calculados: ", lots_normalizados, " | Riesgo (USD): ", riesgo_monetario);
-    
-    return lots_normalizados;
+    if(final_lots < min_lot) final_lots = min_lot;
+    if(final_lots > max_lot) final_lots = max_lot;
+    
+    Print("[RISK CALC] Type: ", EnumToString(order_type), " | Dist Puntos: ", loss_ticks, " | Raw Lots (1000$): ", raw_lots, " | Lots Truncados (Broker): ", final_lots);
+    
+    return final_lots;
 }
 
 //+------------------------------------------------------------------+
@@ -300,7 +300,7 @@
     // para calcular: Max_RR = MFE_precio / slDist
 
     // === EJECUCION: Abrir posicion (Lote Dinamico 1%) ===
-    double lots_to_trade = CalcDynamicLot(slDist);
+    double lots_to_trade = CalcDynamicLot((ENUM_ORDER_TYPE)signalType, sl);
     if(lots_to_trade <= 0) return;
 
     if(trade.PositionOpen(_Symbol, (ENUM_ORDER_TYPE)signalType,
```

## Step 638 - Tool Call: multi_replace_file_content
**Instruction:** "Change the min_lot override rule to return 0.0 and print a risk violation error."
**Description:** "Fixed risk exposure logic by returning 0 (aborting trade) instead of forcing minimum lot when mathematical lot is smaller than broker's minimum."

```json
{
  "Description": "\"Fixed risk exposure logic by returning 0 (aborting trade) instead of forcing minimum lot when mathematical lot is smaller than broker's minimum.\"",
  "Instruction": "\"Change the min_lot override rule to return 0.0 and print a risk violation error.\"",
  "ReplacementChunks": "[{\"AllowMultiple\":false,\"EndLine\":168,\"ReplacementContent\":\"    if(final_lots < min_lot) {\\n        Print(\\\"[RISK CALC] ALERTA: Lote necesario (\\\", final_lots, \\\") menor al minimo del broker (\\\", min_lot, \\\"). Trade abortado para proteger limite del 1%.\\\");\\n        return 0.0;\\n    }\\n    if(final_lots > max_lot) final_lots = max_lot;\\n    \\n    Print(\\\"[RISK CALC] Type: \\\", EnumToString(order_type), \\\" | Dist Puntos: \\\", loss_ticks, \\\" | Raw Lots (1000$): \\\", raw_lots, \\\" | Lots Truncados (Broker): \\\", final_lots);\",\"StartLine\":164,\"TargetContent\":\"    if(final_lots < min_lot) final_lots = min_lot;\\n    if(final_lots > max_lot) final_lots = max_lot;\\n    \\n    Print(\\\"[RISK CALC] Type: \\\", EnumToString(order_type), \\\" | Dist Puntos: \\\", loss_ticks, \\\" | Raw Lots (1000$): \\\", raw_lots, \\\" | Lots Truncados (Broker): \\\", final_lots);\"}]",
  "TargetFile": "\"c:\\\\Users\\\\Manuel\\\\Desktop\\\\HMA_MetaLabeling\\\\MQL5_Engine\\\\HMA_ML_Orchestrator.mq5\"",
  "toolAction": "\"Fix minimum lot risk breach\"",
  "toolSummary": "\"Fix min lot logic\""
}
```

## Step 639 - Tool Response
```diff
@@ -161,7 +161,10 @@
     double min_lot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
     double max_lot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
     
-    if(final_lots < min_lot) final_lots = min_lot;
+    if(final_lots < min_lot) {
+        Print("[RISK CALC] ALERTA: Lote necesario (", final_lots, ") menor al minimo del broker (", min_lot, "). Trade abortado para proteger limite del 1%.");
+        return 0.0;
+    }
     if(final_lots > max_lot) final_lots = max_lot;
     
     Print("[RISK CALC] Type: ", EnumToString(order_type), " | Dist Puntos: ", loss_ticks, " | Raw Lots (1000$): ", raw_lots, " | Lots Truncados (Broker): ", final_lots);
```

## Step 653 - Tool Call: multi_replace_file_content
**Instruction:** "Update CalcDynamicLot logic to match the CalculateLotSize logic provided. Update tp to be 1.5R."
**Description:** "Replaced CalcDynamicLot with the exact lot calculation logic requested by the user, incorporating tick size/value profit and hardcoded 1% risk. Set physical TP at 1.5R."

```json
{
  "Description": "\"Replaced CalcDynamicLot with the exact lot calculation logic requested by the user, incorporating tick size/value profit and hardcoded 1% risk. Set physical TP at 1.5R.\"",
  "Instruction": "\"Update CalcDynamicLot logic to match the CalculateLotSize logic provided. Update tp to be 1.5R.\"",
  "ReplacementChunks": "[{\"AllowMultiple\":false,\"EndLine\":170,\"ReplacementContent\":\"double CalcDynamicLot(ENUM_ORDER_TYPE order_type, double sl_price)\\n{\\n    double sl_dist_price = 0.0;\\n    if(order_type == ORDER_TYPE_BUY) {\\n        sl_dist_price = MathAbs(SymbolInfoDouble(_Symbol, SYMBOL_ASK) - sl_price);\\n    } else {\\n        sl_dist_price = MathAbs(sl_price - SymbolInfoDouble(_Symbol, SYMBOL_BID));\\n    }\\n    \\n    if(sl_dist_price <= 0) return 0.0;\\n    \\n    double riskMoney = AccountInfoDouble(ACCOUNT_BALANCE) * 0.01;\\n    \\n    ENUM_SYMBOL_CALC_MODE calcMode = (ENUM_SYMBOL_CALC_MODE)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_CALC_MODE);\\n    double tickVal;\\n    if(calcMode == SYMBOL_CALC_MODE_FOREX)\\n        tickVal = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE_PROFIT);\\n    else\\n        tickVal = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);\\n        \\n    double tickSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);\\n    \\n    if(tickVal == 0) tickVal = 1.0; \\n    if(tickSize == 0) return 0.0;\\n    \\n    double moneyPerPriceUnit = tickVal / tickSize; \\n    if(sl_dist_price * moneyPerPriceUnit == 0) return 0.0;\\n    \\n    double rawLot = riskMoney / (sl_dist_price * moneyPerPriceUnit);\\n    \\n    double minLot  = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);\\n    double maxLot  = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);\\n    double stepLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);\\n    if(stepLot == 0) stepLot = 0.01;\\n    \\n    double finalLot = MathFloor(rawLot / stepLot) * stepLot;\\n    \\n    if(finalLot < minLot) {\\n        Print(\\\"[RISK CALC] ALERTA: Lote necesario (\\\", finalLot, \\\") menor al minimo del broker (\\\", minLot, \\\"). Trade abortado para proteger limite del 1%.\\\");\\n        return 0.0;\\n    }\\n    if(finalLot > maxLot) finalLot = maxLot;\\n    \\n    Print(\\\"[AUDITORIA RIESGO] Tipo: \\\", order_type, \\\" | SL Distancia: \\\", sl_dist_price, \\\" | Lotes Calculados: \\\", finalLot, \\\" | Riesgo Te\u00f3rico $: \\\", (finalLot * sl_dist_price * moneyPerPriceUnit));\\n    \\n    return finalLot;\\n}\",\"S\n<truncated 2206 bytes>",
  "TargetFile": "\"c:\\\\Users\\\\Manuel\\\\Desktop\\\\HMA_MetaLabeling\\\\MQL5_Engine\\\\HMA_ML_Orchestrator.mq5\"",
  "toolAction": "\"Updating lot formula and TP in EA\"",
  "toolSummary": "\"Update Lot and TP\""
}
```

## Step 654 - Tool Response
```diff
@@ -146,30 +146,41 @@
     
     if(sl_dist_price <= 0) return 0.0;
     
-    double risk_money = AccountInfoDouble(ACCOUNT_BALANCE) * 0.01;
-    double tick_size = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
-    double tick_value = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
-    
-    if(tick_size <= 0 || tick_value <= 0) return 0.0;
-    
-    double loss_ticks = sl_dist_price / tick_size;
-    double raw_lots = risk_money / (loss_ticks * tick_value);
-    
-    double vol_step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
-    double final_lots = MathFloor(raw_lots / vol_step) * vol_step;
-    
-    double min_lot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
-    double max_lot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
-    
-    if(final_lots < min_lot) {
-        Print("[RISK CALC] ALERTA: Lote necesario (", final_lots, ") menor al minimo del broker (", min_lot, "). Trade abortado para proteger limite del 1%.");
+    double riskMoney = AccountInfoDouble(ACCOUNT_BALANCE) * 0.01;
+    
+    ENUM_SYMBOL_CALC_MODE calcMode = (ENUM_SYMBOL_CALC_MODE)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_CALC_MODE);
+    double tickVal;
+    if(calcMode == SYMBOL_CALC_MODE_FOREX)
+        tickVal = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE_PROFIT);
+    else
+        tickVal = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
+        
+    double tickSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
+    
+    if(tickVal == 0) tickVal = 1.0; 
+    if(tickSize == 0) return 0.0;
+    
+    double moneyPerPriceUnit = tickVal / tickSize; 
+    if(sl_dist_price * moneyPerPriceUnit == 0) return 0.0;
+    
+   
<truncated 146 bytes>
  double maxLot  = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
+    double stepLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
+    if(stepLot == 0) stepLot = 0.01;
+    
+    double finalLot = MathFloor(rawLot / stepLot) * stepLot;
+    
+    if(finalLot < minLot) {
+        Print("[RISK CALC] ALERTA: Lote necesario (", finalLot, ") menor al minimo del broker (", minLot, "). Trade abortado para proteger limite del 1%.");
         return 0.0;
     }
-    if(final_lots > max_lot) final_lots = max_lot;
-    
-    Print("[RISK CALC] Type: ", EnumToString(order_type), " | Dist Puntos: ", loss_ticks, " | Raw Lots (1000$): ", raw_lots, " | Lots Truncados (Broker): ", final_lots);
-    
-    return final_lots;
+    if(finalLot > maxLot) finalLot = maxLot;
+    
+    Print("[AUDITORIA RIESGO] Tipo: ", order_type, " | SL Distancia: ", sl_dist_price, " | Lotes Calculados: ", finalLot, " | Riesgo Teórico $: ", (finalLot * sl_dist_price * moneyPerPriceUnit));
+    
+    return finalLot;
 }
 
 //+------------------------------------------------------------------+
@@ -297,10 +297,10 @@
     
     if(slDist <= 0) return;
 
-    // FASE 2: Eliminacion del sesgo del TP fijo (True MFE Discovery)
-    // Se fuerza el TP a 0 para que la operacion solo se cierre por SL o por la Barrera de Tiempo.
-    // Esto permite al Logger registrar el verdadero Maximo Recorrido a Favor (MFE) sin truncarlo artificialmente.
-    double tp = 0.0;
+    // Inyeccion del TP fisico a 1.5R estricto para asegurar cierre por broker
+    double tp = (signalType == 0)
+                ? ask + (slDist * 1.5)
+                : bid - (slDist * 1.5);
 
     // Feature 15: SL Distance normalizada por ATR
     double sl_dist_atr = (current_atr > 0) ? slDist / current_atr : 0.0;
```

## Step 665 - Tool Call: multi_replace_file_content
**Instruction:** "Add InpInitialBalance input parameter. Update CalcDynamicLot to use InpInitialBalance for risk calculation. Change tp back to 0.0 in OnTick."
**Description:** "Reverted TP to 0.0 for pure MFE extraction and swapped AccountBalance for a Fixed Fractional Base (InpInitialBalance) to guarantee linear non-compounding risk."

```json
{
  "Description": "\"Reverted TP to 0.0 for pure MFE extraction and swapped AccountBalance for a Fixed Fractional Base (InpInitialBalance) to guarantee linear non-compounding risk.\"",
  "Instruction": "\"Add InpInitialBalance input parameter. Update CalcDynamicLot to use InpInitialBalance for risk calculation. Change tp back to 0.0 in OnTick.\"",
  "ReplacementChunks": "[{\"AllowMultiple\":false,\"EndLine\":43,\"ReplacementContent\":\"input group \\\"== Gestion ML (Triple Barrera y Riesgo Lineal) ==\\\"\\ninput double InpInitialBalance    = 100000.0; // Balance Inicial (Fijo para Extraccion)\\ninput double TakeProfitMultiplier = 3.0;   // TP Maximo (alto para registrar MFE real antes del SL).\",\"StartLine\":42,\"TargetContent\":\"input group \\\"== Gestion ML (Triple Barrera) ==\\\"\\ninput double TakeProfitMultiplier = 3.0;   // TP Maximo (alto para registrar MFE real antes del SL).\"},{\"AllowMultiple\":false,\"EndLine\":150,\"ReplacementContent\":\"    if(sl_dist_price <= 0) return 0.0;\\n    \\n    double riskMoney = InpInitialBalance * 0.01;\\n    \\n    ENUM_SYMBOL_CALC_MODE calcMode = (ENUM_SYMBOL_CALC_MODE)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_CALC_MODE);\",\"StartLine\":146,\"TargetContent\":\"    if(sl_dist_price <= 0) return 0.0;\\n    \\n    double riskMoney = AccountInfoDouble(ACCOUNT_BALANCE) * 0.01;\\n    \\n    ENUM_SYMBOL_CALC_MODE calcMode = (ENUM_SYMBOL_CALC_MODE)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_CALC_MODE);\"},{\"AllowMultiple\":false,\"EndLine\":303,\"ReplacementContent\":\"    if(slDist <= 0) return;\\n\\n    // FASE 2: Eliminacion del sesgo del TP fijo (True MFE Discovery)\\n    // Se fuerza el TP a 0 para que la operacion solo se cierre por SL o por la Barrera de Tiempo.\\n    // Esto permite al Logger registrar el verdadero Maximo Recorrido a Favor (MFE) sin truncarlo artificialmente.\\n    double tp = 0.0;\\n\\n    // Feature 15: SL Distance normalizada por ATR\",\"StartLine\":298,\"TargetContent\":\"    if(slDist <= 0) return;\\n\\n    // Inyeccion del TP fisico a 1.5R estricto para asegurar cierre por broker\\n    double tp = (signalType == 0)\\n                ? ask + (slDist * 1.5)\\n                : bid - (slDist * 1.5);\\n\\n    // Feature 15: SL Distance normalizada por ATR\"}]",
  "TargetFile": "\"c:\\\\Users\\\\Manuel\\\\Desktop\\\\HMA_MetaLabeling\\\\MQL5_Engine\\\\HMA_ML_Orchestrator.mq5\"",
  "toolAction": "\"Updating risk and TP logic\"",
  "toolSummary": "\"Update Risk and TP\""
}
```

## Step 666 - Tool Response
```diff
@@ -39,7 +39,8 @@
 input group "== Microestructura =="
 input double MaxSpreadPips       = 4.0;    // Anti-broker: 4 pips filtra spreads abusivos sin perder datos.
 
-input group "== Gestion ML (Triple Barrera) =="
+input group "== Gestion ML (Triple Barrera y Riesgo Lineal) =="
+input double InpInitialBalance    = 100000.0; // Balance Inicial (Fijo para Extraccion)
 input double TakeProfitMultiplier = 3.0;   // TP Maximo (alto para registrar MFE real antes del SL).
 input int    VerticalBarrierBars  = 48;    // Barrera vertical: 48 velas (en M15 = 12h para desarrollarse)
 
@@ -145,7 +145,7 @@
     
     if(sl_dist_price <= 0) return 0.0;
     
-    double riskMoney = AccountInfoDouble(ACCOUNT_BALANCE) * 0.01;
+    double riskMoney = InpInitialBalance * 0.01;
     
     ENUM_SYMBOL_CALC_MODE calcMode = (ENUM_SYMBOL_CALC_MODE)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_CALC_MODE);
     double tickVal;
@@ -307,10 +307,10 @@
     
     if(slDist <= 0) return;
 
-    // Inyeccion del TP fisico a 1.5R estricto para asegurar cierre por broker
-    double tp = (signalType == 0)
-                ? ask + (slDist * 1.5)
-                : bid - (slDist * 1.5);
+    // FASE 2: Eliminacion del sesgo del TP fijo (True MFE Discovery)
+    // Se fuerza el TP a 0 para que la operacion solo se cierre por SL o por la Barrera de Tiempo.
+    // Esto permite al Logger registrar el verdadero Maximo Recorrido a Favor (MFE) sin truncarlo artificialmente.
+    double tp = 0.0;
 
     // Feature 15: SL Distance normalizada por ATR
     double sl_dist_atr = (current_atr > 0) ? slDist / current_atr : 0.0;
```

## Step 725 - Tool Response
```diff
@@ -19,8 +19,33 @@
 - Se introdujo el cálculo real del deslizamiento por spread: `penalty = -1.0 - (Spread_Pips / SL_Pips_Reales)`.
 - **Límite de Fricción (`np.clip`)**: Para proteger al XGBoost de anomalías matemáticas (por ejemplo, noticias donde el spread sea superior al Stop Loss y arroje una penalización de `-2.0R`), se fijó un máximo del 50% de daño adicional (`-1.5R`).
 
-## Próximos Pasos
-
-> [!IMPORTANT]
-> Debes descartar los archivos CSV generados anteriormente. Ejecuta el EA `HMA_ML_Orchestrator.ex5` (v2.1 compilada) en el Strategy Tester de MetaTrader 5 (idealmente en marco de tiempo H1, como propusiste) para re-poblar la carpeta `/data` con los nuevos datos, ya formateados con la nueva anatomía transaccional.
+## Auditoría y Verificación de Resultados
+
+### 1. Auditoría Forense de Alineación (MQL5 <-> Python)
+Ejecutamos con éxito `debug_alignment.py` usando el entorno virtual (`.venv`) para verificar la correcta correspondencia de datos:
+- **Estado de Índices Pandas**: Confirmado. Se descartó cualquier error *off-by-one* o desalineación transversal al limpiar filas.
+- **Mapeo de Retornos**: Confirmado. El cálculo del `Max_RR_Achieved` coincide de forma exacta con la dirección del trade, y el retorno penalizado por spread refleja la fricción real del bróker.
+
+### 2. Resultados del Escaneo Walk-Forward (OOS) con XGBoost
+El pipeline funcional `antigravity_scanner.py` procesó con éxito los tres datasets históricos de MetaTrader 5:
+
+| Activo | Total Trades | Umbral IA Óptimo | Win Rate (OOS) | Profit Factor (OOS) |
+| :--- | :---: | :---: | :---: | :---: |
+| **GBPUSD** | 469 | 0.60 | **86.57%** | **9.67** |
+| **USDJPY** | 499 | 0.56 | **84.77%** | **8.35** |
+| **AUDCAD** | 204 | 0.60 | **68.63%** | **3.28** |
+
+> [!TIP]
+> Los Profit Factors en la etapa Out-Of-Sample (OOS) confirman que el filtrado de Meta-Labeling basado en XGBoost añade una capa robusta de protección, descartando operaciones de baja probabilidad y maximizando el factor de beneficio neto.
+
+## Conclusión y Siguientes Pasos
+
+1. **Compilación y Carga en MT5**: Asegúrate de compilar `HMA_ML_Orchestrator.mq5` en MetaTrader 5.
+2. **Entorno de Python**: Al ejecutar los scripts de Python, recuerda usar siempre el intérprete del entorno virtual local para evitar el error `ModuleNotFoundError`:
+   ```powershell
+   # Desde el directorio raíz de HMA_MetaLabeling
+   .\Python_ML\.venv\Scripts\python.exe Python_ML\debug_alignment.py
+   .\Python_ML\.venv\Scripts\python.exe Python_ML\antigravity_scanner.py
+   ```
+
```

## Step 875 - Tool Call: multi_replace_file_content
**Instruction:** "Add atr_sma50_handle in handles, OnInit initialization, OnDeinit cleanup, and the 3 new feature computations with snapshot assignment in OnTick"
**Description:** "Injected 3 new feature calculations in OnInit and OnTick: (1) atr_sma50_handle for Vol_Spread_Ratio; (2) Session_Time from broker hour (Asia/London/NY/Overlap); (3) H4_Trend_Align comparing H4 EMA50 direction with trade direction; (4) Vol_Spread_Ratio = ATR_current / SMA50(ATR). Removed balance_momento and lots_utilizados from snapshot construction. Updated OnDeinit to release new handle."

```json
{
  "Description": "\"Injected 3 new feature calculations in OnInit and OnTick: (1) atr_sma50_handle for Vol_Spread_Ratio; (2) Session_Time from broker hour (Asia/London/NY/Overlap); (3) H4_Trend_Align comparing H4 EMA50 direction with trade direction; (4) Vol_Spread_Ratio = ATR_current / SMA50(ATR). Removed balance_momento and lots_utilizados from snapshot construction. Updated OnDeinit to release new handle.\"",
  "Instruction": "\"Add atr_sma50_handle in handles, OnInit initialization, OnDeinit cleanup, and the 3 new feature computations with snapshot assignment in OnTick\"",
  "ReplacementChunks": "[{\"AllowMultiple\":false,\"EndLine\":4,\"ReplacementContent\":\"//+------------------------------------------------------------------+\\n//|                                          HMA_ML_Orchestrator.mq5 |\\n//|        Generador Cuantitativo de Datasets (Meta-Labeling v2.1)   |\\n//|        Feature Engineering Fase 2: Session_Time, H4_Trend_Align |\\n//|        Vol_Spread_Ratio | Zero-Trust LEAKAGE_COLS aplicado       |\\n//+------------------------------------------------------------------+\\n\",\"StartLine\":1,\"TargetContent\":\"//+------------------------------------------------------------------+\\n//|                                          HMA_ML_Orchestrator.mq5 |\\n//|        Generador Cuantitativo de Datasets (Meta-Labeling v2.0)   |\\n//|        \\\"Tonto pero Valiente\\\" - Alto Recall, Cero Cliff Effects   |\\n//|        Alineado con ARCHITECTURE_MASTER_CONTEXT                  |\\n//+------------------------------------------------------------------+\\n\"},{\"AllowMultiple\":false,\"EndLine\":51,\"ReplacementContent\":\"// === Handles de Indicadores ===\\nint hma_handle, rsi_handle, atr_handle;\\nint ema50_handle, ema200_handle;\\nint sma20_handle, std_dev_handle;\\nint atr_sma50_handle; // SMA(50) sobre ATR para Vol_Spread_Ratio\\nint ema50_h4_handle;  // EMA(50) en H4 para H4_Trend_Align (pendiente de la linea)\\n\\n// TrendTimeframe dinamico (se resuelve en OnInit segun _Period)\\nENUM_TIMEFRAMES g_macro_tf;\\n\",\"StartLine\":47,\"TargetContent\":\"// === Handles de Indicadores ===\\nint hma_handle, rsi_handle, atr_handle;\\nint ema50_handle, ema200_handle;\\nint sma20_handle, std_dev_handle;\\n\\n// TrendTimeframe dinamico (se resuelve en OnInit segun _Period)\\nENUM_TIMEFRAMES g_macro_tf;\"},{\"AllowMultiple\":false,\"EndLine\":94,\"ReplacementContent\":\"    // Cargar Indicadores\\n    hma_handle     = iCustom(_Symbol, _Period, \\\"HMA50\\\", HMAPeriod);\\n    rsi_handle     = iRSI(_Symbol, _Period, RsiPeriod, PRICE_CLOSE);\\n    atr_handle     = iATR(_Symbol, _Period, 14);\\n    ema50_handle   = iMA(_Symbol, g_macro_tf, 50, 0, MODE_EMA, PRICE_CLOSE);\\n    ema2\n<truncated 11306 bytes>",
  "TargetFile": "\"C:\\\\Users\\\\Manuel\\\\Desktop\\\\HMA_MetaLabeling\\\\MQL5_Engine\\\\HMA_ML_Orchestrator.mq5\"",
  "toolAction": "\"Injecting 3 new feature calculations in orchestrator\"",
  "toolSummary": "\"HMA_ML_Orchestrator feature engineering\""
}
```

## Step 876 - Tool Response
```diff
@@ -1,8 +1,8 @@
 //+------------------------------------------------------------------+
 //|                                          HMA_ML_Orchestrator.mq5 |
-//|        Generador Cuantitativo de Datasets (Meta-Labeling v2.0)   |
-//|        "Tonto pero Valiente" - Alto Recall, Cero Cliff Effects   |
-//|        Alineado con ARCHITECTURE_MASTER_CONTEXT                  |
+//|        Generador Cuantitativo de Datasets (Meta-Labeling v2.1)   |
+//|        Feature Engineering Fase 2: Session_Time, H4_Trend_Align |
+//|        Vol_Spread_Ratio | Zero-Trust LEAKAGE_COLS aplicado       |
 //+------------------------------------------------------------------+
 //  ARQUITECTURA:
 //    - Captura TODO cruce HMA con Close (anti-ruido 2% ATR)
@@ -47,6 +47,8 @@
 int hma_handle, rsi_handle, atr_handle;
 int ema50_handle, ema200_handle;
 int sma20_handle, std_dev_handle;
+int atr_sma50_handle; // SMA(50) sobre ATR para Vol_Spread_Ratio
+int ema50_h4_handle;  // EMA(50) en H4 para H4_Trend_Align (pendiente de la linea)
 
 // TrendTimeframe dinamico (se resuelve en OnInit segun _Period)
 ENUM_TIMEFRAMES g_macro_tf;
@@ -53,4 +53,5 @@
 
+
 //+------------------------------------------------------------------+
 //| OnInit                                                           |
 //+------------------------------------------------------------------+
@@ -78,9 +78,16 @@
     ema200_handle  = iMA(_Symbol, g_macro_tf, 200, 0, MODE_EMA, PRICE_CLOSE);
     sma20_handle   = iMA(_Symbol, _Period, 20, 0, MODE_SMA, PRICE_CLOSE);
     std_dev_handle = iStdDev(_Symbol, _Period, 20, 0, MODE_SMA, PRICE_CLOSE);
+    // Feature Fase 2: SMA(ATR, 50) en timeframe operativo para
<truncated 5943 bytes>
 (pasado)
+    double atr_sma50     = (atr_sma50_sum > 0) ? atr_sma50_sum / 50.0 : current_atr;
+    double vol_spread_ratio = (atr_sma50 > 0) ? current_atr / atr_sma50 : 1.0;
+
     // === CALCULO DE SL/TP (AMC 4: High/Low para SL) ===
     double entry_price = (signalType == 0)
                          ? SymbolInfoDouble(_Symbol, SYMBOL_ASK)
@@ -327,7 +327,7 @@
         snap.time                = TimeCurrent();
         snap.signal_type         = signalType;
 
-        // Features X
+        // Features X: Estandar (ya calculadas)
         snap.z_score_close       = z_score;
         snap.atr_normalized      = atr_norm;
         snap.rsi_val             = rsi_val;
@@ -345,14 +345,19 @@
 
         // FASE 1.2: Guardar slDist en precio para Max_RR_Achieved
         snap.sl_dist_price       = slDist;
-
-        // FASE Riesgo Dinámico
-        snap.balance_momento     = AccountInfoDouble(ACCOUNT_BALANCE);
-        snap.lots_utilizados     = lots_to_trade;
         snap.sl_pips_reales      = slDist / pip;
 
+        // Features X: Feature Engineering Fase 2 (NUEVAS)
+        snap.session_time        = session_time;     // 1=Asia, 2=Londres, 3=NY, 0=Solapamiento
+        snap.h4_trend_align      = h4_trend_align;   // +1=a favor H4, -1=contra H4
+        snap.vol_spread_ratio    = vol_spread_ratio;  // ATR_actual / SMA50(ATR)
+
+        // NOTA Zero-Trust: balance_momento y lots_utilizados NO se asignan
+        // (eliminados del struct por ser post-trade/contaminados)
+
         // Targets Y: se rellenan en CommitTrade (OnTradeTransaction)
 
+
         logger.RecordSignal(snap);
         PrintFormat("SIGNAL: %s | Ticket=%I64u | BF_ATR=%.2f | Trend=%d | RSI_Ext=%.1f",
                     (signalType == 0 ? "BUY" : "SELL"), pos_ticket,
```

## Step 879 - Tool Response
```diff
@@ -84,12 +84,12 @@
     ema200_handle  = iMA(_Symbol, g_macro_tf, 200, 0, MODE_EMA, PRICE_CLOSE);
     sma20_handle   = iMA(_Symbol, _Period, 20, 0, MODE_SMA, PRICE_CLOSE);
     std_dev_handle = iStdDev(_Symbol, _Period, 20, 0, MODE_SMA, PRICE_CLOSE);
-    // Feature Fase 2: SMA(ATR, 50) en timeframe operativo para Vol_Spread_Ratio
-    atr_sma50_handle = iMA(_Symbol, _Period, 50, 0, MODE_SMA, PRICE_CLOSE);
-    // Nota: usaremos un buffer ATR de 51 velas para calcular la media de 50 directamente
-    // atr_sma50_handle se reemplaza por calculo manual sobre CopyBuffer(atr_handle, 51)
-    // Feature Fase 2: EMA(50) en PERIOD_H4 para H4_Trend_Align (necesitamos 2 barras para pendiente)
+    // Feature Fase 2: EMA(50) en PERIOD_H4 para H4_Trend_Align (pendiente de la linea)
+    // Necesitamos 2 barras para calcular si la EMA50 H4 sube o baja
     ema50_h4_handle = iMA(_Symbol, PERIOD_H4, 50, 0, MODE_EMA, PRICE_CLOSE);
+    // Nota: Vol_Spread_Ratio se calcula directamente desde CopyBuffer(atr_handle, 51)
+    // No requiere handle adicional (atr_buf[0]=actual, atr_buf[1..50]=SMA50 manual)
+
 
     if(hma_handle == INVALID_HANDLE || rsi_handle == INVALID_HANDLE ||
        atr_handle == INVALID_HANDLE || std_dev_handle == INVALID_HANDLE ||
```

## Step 882 - Tool Response
```diff
@@ -48,8 +48,8 @@
 int hma_handle, rsi_handle, atr_handle;
 int ema50_handle, ema200_handle;
 int sma20_handle, std_dev_handle;
-int atr_sma50_handle; // SMA(50) sobre ATR para Vol_Spread_Ratio
-int ema50_h4_handle;  // EMA(50) en H4 para H4_Trend_Align (pendiente de la linea)
+int ema50_h4_handle;  // EMA(50) fijo en H4 para H4_Trend_Align
+// Nota: Vol_Spread_Ratio no requiere handle propio (calculo manual sobre atr_buf[51])
 
 // TrendTimeframe dinamico (se resuelve en OnInit segun _Period)
 ENUM_TIMEFRAMES g_macro_tf;
```

## Step 902 - Tool Response
```diff
@@ -254,7 +254,7 @@
     if(!crossUp && !crossDn) return; // Sin cruce, nada que hacer
 
     // === ANTI-RUIDO: 2% ATR minimo (AMC 2D) ===
-    double minDev = atr[1] * (AntiNoiseATRPct / 100.0);
+    double minDev = atr_buf[1] * (AntiNoiseATRPct / 100.0);
     double deviation = MathAbs(rates[1].close - hma[1]);
     if(deviation < minDev) return;
```

## Step 904 - Tool Response
```diff
@@ -326,9 +326,9 @@
     int h = dt.hour;
     int session_time;
     if(h >= 13 && h <= 14)      session_time = 0; // Solapamiento Londres+NY (maxima liquidez)
-    else if(h >= 7  && h <= 14) session_time = 2; // Sesion Londres
-    else if(h >= 13 && h <= 20) session_time = 3; // Sesion Nueva York
-    else                        session_time = 1; // Sesion Asia / fuera de sesion
+    else if(h >= 7  && h < 13)  session_time = 2; // Sesion Londres (exclusiva: 7h a 12h)
+    else if(h > 14  && h <= 20) session_time = 3; // Sesion Nueva York (exclusiva: 15h a 20h)
+    else                        session_time = 1; // Sesion Asia / fuera de sesion principal (21h a 6h)
 
     // --- Feature NUEVA 2: H4_Trend_Align ---
     // Compara la PENDIENTE de la EMA50 en H4 con la direccion del trade.
```

## Step 920 - Tool Response
```diff
@@ -2,7 +2,16 @@
 
 ## Resumen de Cambios
 
-Se refactorizaron completamente `pipeline_multi_activo.py` y `backtest_walk_forward_montecarlo.py` para reemplazar la lista estática de 9 features (`FEATURES_ACTIVAS`) por una extracción dinámica basada en filtrado de columnas post-trade (`LEAKAGE_COLS`). Esto unifica la lógica con `antigravity_scanner.py`, eliminando el gap de rendimiento que causaba resultados negativos en los backtests previos.
+1. **Corrección de Error de Compilación MQL5** (`HMA_ML_Orchestrator.mq5`):
+   - Se corrigieron los errores de compilación `undeclared identifier 'atr'` y `'[' - array required` en la línea 257. Durante el enriquecimiento de features de la Fase 2, se renombró el buffer de ATR a `atr_buf[]`, pero quedó un uso remanente de `atr[1]` en la validación de la regla anti-ruido (2% ATR mínimo). Se reemplazó por `atr_buf[1]`, logrando una compilación 100% limpia.
+2. **Saneamiento de la Lógica de Sesiones** (`session_time`):
+   - Se refactorizó la lógica condicional de `session_time` para garantizar condiciones mutuamente excluyentes, eliminando el solapamiento que hacía inaccesibles o ambiguas ciertas horas. La distribución horaria (basada en la hora UTC del broker) quedó estrictamente delimitada:
+     - **Solapamiento Londres + NY (Valor 0)**: de `13:00` a `14:59` (horas 13 y 14).
+     - **Sesión Londres Exclusiva (Valor 2)**: de `07:00` a `12:59` (horas 7 a 12).
+     - **Sesión Nueva York Exclusiva (Valor 3)**: de `15:00` a `20:59` (horas 15 a 20).
+     - **Sesión Asia / Fuera de Sesión (Valor 1)**: de `21:00` a `06:59` (horas 21 a 6).
+3. **Refactorización de Features en Python**:
+   - Se refactorizaron completamente `pipeline_multi_activo.py` y `backtest_walk_forward_montecarlo.py` para reemplazar la lista estática de 9 features (`FEATURES_ACTIVAS`) por una extracción dinámica basada en filtrado de columnas post-trade (`LEAKAGE_COLS`). Esto unifica la lógica con `antigravity_scanner.py`, eliminando el gap de rendimiento que causaba resultados negativos en los backtests previos.
 
 ---
```

## Step 1436 - Tool Call: multi_replace_file_content
**Instruction:** "Refactor `CopyBuffer`/`CopyRates` to start at `shift 1` and use `ArraySetAsSeries(..., true)` to prevent Look-Ahead bias (Repainting). Update the calculation block to use index 0 as shift 1. Capture `real_entry` from `trade.ResultPrice()` post-execution to correct slippage artifacts."
**Description:** "Fix Look-Ahead Bias by enforcing Shift 1, sync H4 timeframe, and capture real execution price to account for slippage."

```json
{
  "Description": "\"Fix Look-Ahead Bias by enforcing Shift 1, sync H4 timeframe, and capture real execution price to account for slippage.\"",
  "Instruction": "\"Refactor `CopyBuffer`/`CopyRates` to start at `shift 1` and use `ArraySetAsSeries(..., true)` to prevent Look-Ahead bias (Repainting). Update the calculation block to use index 0 as shift 1. Capture `real_entry` from `trade.ResultPrice()` post-execution to correct slippage artifacts.\"",
  "ReplacementChunks": "[{\"AllowMultiple\":false,\"EndLine\":244,\"ReplacementContent\":\"    // === EXTRACCION DE DATOS ESTRICTA (SHIFT 1 - CERO LOOK-AHEAD) ===\\n    double hma[], rsi_buf[], atr_buf[], ef[], es[], sma20[], stddev[];\\n    double ema50_h4[]; \\n    MqlRates rates[];\\n    \\n    ArraySetAsSeries(hma, true);\\n    ArraySetAsSeries(rsi_buf, true);\\n    ArraySetAsSeries(atr_buf, true);\\n    ArraySetAsSeries(ef, true);\\n    ArraySetAsSeries(es, true);\\n    ArraySetAsSeries(sma20, true);\\n    ArraySetAsSeries(stddev, true);\\n    ArraySetAsSeries(ema50_h4, true);\\n    ArraySetAsSeries(rates, true);\\n\\n    if(CopyRates(_Symbol, _Period, 1, 3, rates) < 3) return;\\n    if(CopyBuffer(hma_handle, 0, 1, 4, hma) < 4)     return;\\n    if(CopyBuffer(rsi_handle, 0, 1, RsiLookbackBars + 1, rsi_buf) < RsiLookbackBars + 1) return;\\n    if(CopyBuffer(atr_handle, 0, 1, 51, atr_buf) < 51) return;\\n    if(CopyBuffer(sma20_handle, 0, 1, 1, sma20) < 1)  return;\\n    if(CopyBuffer(std_dev_handle, 0, 1, 1, stddev) < 1) return;\\n\\n    // Sincronizacion MTF (Macro y H4): Encontrar vela actual y pedir la anterior (+1)\\n    int macro_shift = iBarShift(_Symbol, g_macro_tf, TimeCurrent());\\n    int h4_shift    = iBarShift(_Symbol, PERIOD_H4, TimeCurrent());\\n    \\n    if(CopyBuffer(ema50_handle, 0, macro_shift + 1, 1, ef) < 1)     return;\\n    if(CopyBuffer(ema200_handle, 0, macro_shift + 1, 1, es) < 1)    return;\\n    if(CopyBuffer(ema50_h4_handle, 0, h4_shift + 1, 2, ema50_h4) < 2) return;\\n\\n    // === DETECCION DE CRUCE HMA (con Close, AMC: Resiliencia a Mechas) ===\\n    // rates[0]/hma[0] es Shift 1 (Cerrada), rates[1]/hma[1] es Shift 2 (Anterior Cerrada)\\n    bool crossUp = (rates[1].close < hma[1] && rates[0].close > hma[0]);\\n    bool crossDn = (rates[1].close > hma[1] && rates[0].close < hma[0]);\",\"StartLine\":224,\"TargetContent\":\"    // === EXTRACCION DE DATOS ===\\n    double hma[4], rsi_buf[], atr_buf[], ef[1], es[1], sma20[1], stddev[1];\\n    double ema50_h4[2]; // 2 barras para calcular pendiente H4\\n    MqlRates rates[3];\\n\\n    if(CopyRates(_Symbol,\n<truncated 8596 bytes>",
  "TargetFile": "\"C:\\\\Users\\\\Manuel\\\\Desktop\\\\HMA_MetaLabeling\\\\MQL5_Engine\\\\HMA_ML_Orchestrator.mq5\"",
  "toolAction": "\"Fixing HMA Orchestrator lookahead and slippage\"",
  "toolSummary": "\"Fix HMA_ML_Orchestrator.mq5\""
}
```

## Step 1437 - Tool Response
```diff
@@ -221,41 +221,44 @@
                    - SymbolInfoDouble(_Symbol, SYMBOL_BID)) / pip;
     if(spread > MaxSpreadPips) return;
 
-    // === EXTRACCION DE DATOS ===
-    double hma[4], rsi_buf[], atr_buf[], ef[1], es[1], sma20[1], stddev[1];
-    double ema50_h4[2]; // 2 barras para calcular pendiente H4
-    MqlRates rates[3];
-
-    if(CopyRates(_Symbol, _Period, 0, 3, rates) < 3) return;
-    if(CopyBuffer(hma_handle, 0, 0, 4, hma) < 4)     return;
-    if(CopyBuffer(rsi_handle, 0, 0, RsiLookbackBars + 1, rsi_buf) < RsiLookbackBars + 1) return;
-    // Copiar 51 barras de ATR: [0]=actual, [1..50]=historico para SMA50
-    ArrayResize(atr_buf, 51);
-    if(CopyBuffer(atr_handle, 0, 0, 51, atr_buf) < 51) return;
-    if(CopyBuffer(ema50_handle, 0, 0, 1, ef) < 1)     return;
-    if(CopyBuffer(ema200_handle, 0, 0, 1, es) < 1)    return;
-    if(CopyBuffer(sma20_handle, 0, 0, 1, sma20) < 1)  return;
-    if(CopyBuffer(std_dev_handle, 0, 0, 1, stddev) < 1) return;
-    if(CopyBuffer(ema50_h4_handle, 0, 0, 2, ema50_h4) < 2) return;
-
+    // === EXTRACCION DE DATOS ESTRICTA (SHIFT 1 - CERO LOOK-AHEAD) ===
+    double hma[], rsi_buf[], atr_buf[], ef[], es[], sma20[], stddev[];
+    double ema50_h4[]; 
+    MqlRates rates[];
+    
+    ArraySetAsSeries(hma, true);
+    ArraySetAsSeries(rsi_buf, true);
+    ArraySetAsSeries(atr_buf, true);
+    ArraySetAsSeries(ef, true);
+    ArraySetAsSeries(es, true);
+    ArraySetAsSeries(sma20, true);
+    ArraySetAsSeries(stddev, true);
+    ArraySetAsSeries(ema50_h4, true);
+    ArraySetAsSeries(rates, true);
+
+    if(CopyRates(_Symbol, _Period, 1, 3, rates) < 3) return;
+    if(CopyBuffer(hma_hand
<truncated 4469 bytes>
 (ema50_h4[1] > ema50_h4[0]);  // EMA50 H4 con pendiente alcista
+    // ema50_h4[0] = vela cerrada (shift 1), ema50_h4[1] = anterior a la cerrada (shift 2)
+    bool h4_rising = (ema50_h4[0] > ema50_h4[1]);  // EMA50 H4 con pendiente alcista
     int  h4_trend_align;
     if( h4_rising && signalType == 0)  h4_trend_align =  1; // BUY en tendencia alcista H4
     else if(!h4_rising && signalType == 1) h4_trend_align = 1; // SELL en tendencia bajista H4
@@ -384,6 +384,14 @@
                           lots_to_trade, entry_price, sl, tp, "HMA_ML"))
     {
         ulong pos_ticket = trade.ResultDeal();
+        
+        // --- Sincronia de Timestamp (Slippage Real) ---
+        double real_entry = trade.ResultPrice(); 
+        if(real_entry <= 0) real_entry = entry_price; // Fallback
+        
+        double real_slDist = (signalType == 0) ? (real_entry - sl) : (sl - real_entry);
+        if(real_slDist <= 0) real_slDist = slDist; // Fallback extremo
+        double sl_dist_atr = (current_atr > 0) ? real_slDist / current_atr : 0.0;
 
         // Construir Snapshot completo (19 Features X + metadatos)
         MarketSnapshot snap;
@@ -410,9 +410,9 @@
         snap.spread_pips         = spread;
         snap.hour_of_day         = dt.hour;
 
-        // FASE 1.2: Guardar slDist en precio para Max_RR_Achieved
-        snap.sl_dist_price       = slDist;
-        snap.sl_pips_reales      = slDist / pip;
+        // FASE 1.2: Guardar slDist en precio para Max_RR_Achieved (Slippage Aplicado)
+        snap.sl_dist_price       = real_slDist;
+        snap.sl_pips_reales      = real_slDist / pip;
 
         // Features X: Feature Engineering Fase 2 (NUEVAS)
         snap.session_time        = session_time;     // 1=Asia, 2=Londres, 3=NY, 0=Solapamiento
```

## Step 1462 - Tool Call: multi_replace_file_content
**Instruction:** "Actualizar `HMA_ML_Orchestrator.mq5` para incluir `atr200_handle`, calcular `ATR_Ratio_High`, `RSI_Slope_10`, `HMA_Distance_EMA`, `Breakout_Body_Ratio`, `Day_Of_Week` en la fase pre-trade, y calcular `Spread_Impact_Ratio` basándose en la distancia final del SL tras ejecución."
**Description:** "Añadir el handle de ATR200, cálculo de las 6 nuevas features predictivas y asignación al snapshot en el Orchestrator."

```json
{
  "Description": "\"A\u00f1adir el handle de ATR200, c\u00e1lculo de las 6 nuevas features predictivas y asignaci\u00f3n al snapshot en el Orchestrator.\"",
  "Instruction": "\"Actualizar `HMA_ML_Orchestrator.mq5` para incluir `atr200_handle`, calcular `ATR_Ratio_High`, `RSI_Slope_10`, `HMA_Distance_EMA`, `Breakout_Body_Ratio`, `Day_Of_Week` en la fase pre-trade, y calcular `Spread_Impact_Ratio` bas\u00e1ndose en la distancia final del SL tras ejecuci\u00f3n.\"",
  "ReplacementChunks": "[{\"AllowMultiple\":false,\"EndLine\":52,\"ReplacementContent\":\"int ema50_h4_handle;  // EMA(50) fijo en H4 para H4_Trend_Align\\nint atr200_handle;    // ATR(200) para ATR_Ratio_High\\n// Nota: Vol_Spread_Ratio no requiere handle propio (calculo manual sobre atr_buf[51])\",\"StartLine\":51,\"TargetContent\":\"int ema50_h4_handle;  // EMA(50) fijo en H4 para H4_Trend_Align\\n// Nota: Vol_Spread_Ratio no requiere handle propio (calculo manual sobre atr_buf[51])\"},{\"AllowMultiple\":false,\"EndLine\":91,\"ReplacementContent\":\"    // Feature Fase 2: EMA(50) en PERIOD_H4 para H4_Trend_Align (pendiente de la linea)\\n    // Necesitamos 2 barras para calcular si la EMA50 H4 sube o baja\\n    ema50_h4_handle = iMA(_Symbol, PERIOD_H4, 50, 0, MODE_EMA, PRICE_CLOSE);\\n    atr200_handle  = iATR(_Symbol, _Period, 200);\\n    // Nota: Vol_Spread_Ratio se calcula directamente desde CopyBuffer(atr_handle, 51)\",\"StartLine\":87,\"TargetContent\":\"    // Feature Fase 2: EMA(50) en PERIOD_H4 para H4_Trend_Align (pendiente de la linea)\\n    // Necesitamos 2 barras para calcular si la EMA50 H4 sube o baja\\n    ema50_h4_handle = iMA(_Symbol, PERIOD_H4, 50, 0, MODE_EMA, PRICE_CLOSE);\\n    // Nota: Vol_Spread_Ratio se calcula directamente desde CopyBuffer(atr_handle, 51)\"},{\"AllowMultiple\":false,\"EndLine\":97,\"ReplacementContent\":\"    if(hma_handle == INVALID_HANDLE || rsi_handle == INVALID_HANDLE ||\\n       atr_handle == INVALID_HANDLE || std_dev_handle == INVALID_HANDLE ||\\n       ema50_h4_handle == INVALID_HANDLE || atr200_handle == INVALID_HANDLE)\",\"StartLine\":94,\"TargetContent\":\"    if(hma_handle == INVALID_HANDLE || rsi_handle == INVALID_HANDLE ||\\n       atr_handle == INVALID_HANDLE || std_dev_handle == INVALID_HANDLE ||\\n       ema50_h4_handle == INVALID_HANDLE)\"},{\"AllowMultiple\":false,\"EndLine\":122,\"ReplacementContent\":\"    IndicatorRelease(std_dev_handle);\\n    IndicatorRelease(ema50_h4_handle);\\n    IndicatorRelease(atr200_handle);\\n    Print(\\\"HMA_ML_Orchestrator desinicializado. Razon: \\\", reason);\",\"StartLine\":120,\"TargetContent\":\"    IndicatorRel\n<truncated 5517 bytes>",
  "TargetFile": "\"C:\\\\Users\\\\Manuel\\\\Desktop\\\\HMA_MetaLabeling\\\\MQL5_Engine\\\\HMA_ML_Orchestrator.mq5\"",
  "toolAction": "\"Updating Orchestrator\"",
  "toolSummary": "\"Update HMA_ML_Orchestrator.mq5\""
}
```

## Step 1463 - Tool Response
```diff
@@ -49,6 +49,7 @@
 int ema50_handle, ema200_handle;
 int sma20_handle, std_dev_handle;
 int ema50_h4_handle;  // EMA(50) fijo en H4 para H4_Trend_Align
+int atr200_handle;    // ATR(200) para ATR_Ratio_High
 // Nota: Vol_Spread_Ratio no requiere handle propio (calculo manual sobre atr_buf[51])
 
 // TrendTimeframe dinamico (se resuelve en OnInit segun _Period)
@@ -86,6 +86,7 @@
     // Feature Fase 2: EMA(50) en PERIOD_H4 para H4_Trend_Align (pendiente de la linea)
     // Necesitamos 2 barras para calcular si la EMA50 H4 sube o baja
     ema50_h4_handle = iMA(_Symbol, PERIOD_H4, 50, 0, MODE_EMA, PRICE_CLOSE);
+    atr200_handle  = iATR(_Symbol, _Period, 200);
     // Nota: Vol_Spread_Ratio se calcula directamente desde CopyBuffer(atr_handle, 51)
     // No requiere handle adicional (atr_buf[0]=actual, atr_buf[1..50]=SMA50 manual)
 
@@ -92,6 +92,6 @@
     if(hma_handle == INVALID_HANDLE || rsi_handle == INVALID_HANDLE ||
        atr_handle == INVALID_HANDLE || std_dev_handle == INVALID_HANDLE ||
-       ema50_h4_handle == INVALID_HANDLE)
+       ema50_h4_handle == INVALID_HANDLE || atr200_handle == INVALID_HANDLE)
     {
         Print("ERROR CRITICO: No se pudieron cargar los indicadores.");
         return(INIT_FAILED);
@@ -116,6 +116,7 @@
     IndicatorRelease(sma20_handle);
     IndicatorRelease(std_dev_handle);
     IndicatorRelease(ema50_h4_handle);
+    IndicatorRelease(atr200_handle);
     Print("HMA_ML_Orchestrator desinicializado. Razon: ", reason);
 }
 
@@ -219,7 +219,7 @@
 
     // === EXTRACCION DE DATOS ESTRICTA (SHIFT 1 - CERO LOOK-AHEAD) ===
     double hma[], rsi_buf[], atr_buf[], ef[], es[], sma20[], stddev[];
-    double e
<truncated 1525 bytes>
le candle_range = rates[0].high - rates[0].low;
+    double breakout_body_ratio = (candle_range > 0) ? candle_body / candle_range : 0.0;
+
+    // --- Feature Alpha 6: Day_Of_Week ---
+    int day_of_week = dt.day_of_week;
+
     // === CALCULO DE SL/TP (AMC 4: High/Low para SL) ===
     double entry_price = (signalType == 0)
                          ? SymbolInfoDouble(_Symbol, SYMBOL_ASK)
@@ -388,6 +388,10 @@
         double real_slDist = (signalType == 0) ? (real_entry - sl) : (sl - real_entry);
         if(real_slDist <= 0) real_slDist = slDist; // Fallback extremo
         double sl_dist_atr = (current_atr > 0) ? real_slDist / current_atr : 0.0;
+        
+        // --- Feature Alpha 3: Spread_Impact_Ratio ---
+        double sl_pips = real_slDist / pip;
+        double spread_impact_ratio = (sl_pips > 0) ? spread / sl_pips : 0.0;
 
         // Construir Snapshot completo (19 Features X + metadatos)
         MarketSnapshot snap;
@@ -422,6 +422,14 @@
         snap.session_time        = session_time;     // 1=Asia, 2=Londres, 3=NY, 0=Solapamiento
         snap.h4_trend_align      = h4_trend_align;   // +1=a favor H4, -1=contra H4
         snap.vol_spread_ratio    = vol_spread_ratio;  // ATR_actual / SMA50(ATR)
+        
+        // --- Features X: Alpha Search Fase 2 (NUEVAS) ---
+        snap.atr_ratio_high      = atr_ratio_high;
+        snap.rsi_slope_10        = rsi_slope_10;
+        snap.spread_impact_ratio = spread_impact_ratio;
+        snap.hma_distance_ema    = hma_distance_ema;
+        snap.breakout_body_ratio = breakout_body_ratio;
+        snap.day_of_week         = day_of_week;
 
         // NOTA Zero-Trust: balance_momento y lots_utilizados NO se asignan
         // (eliminados del struct por ser post-trade/contaminados)
```

## Step 1485 - Tool Call: multi_replace_file_content
**Instruction:** "Modificar `OnTick` en `HMA_ML_Orchestrator.mq5` para que `lastBarTime` solo se actualice *después* de haber cargado con éxito todos los buffers de datos. Si un buffer falla (ej. H4 aún no sincronizado en el primer ms), retornará sin actualizar `lastBarTime` y se reintentará en el siguiente tick, resolviendo el desfase."
**Description:** "Corregir el flujo de OnTick para evitar bloqueos por carga de histórico (H4) y garantizar la ejecución inmediata en el tick 1 de la Vela 0."

```json
{
  "Description": "\"Corregir el flujo de OnTick para evitar bloqueos por carga de hist\u00f3rico (H4) y garantizar la ejecuci\u00f3n inmediata en el tick 1 de la Vela 0.\"",
  "Instruction": "\"Modificar `OnTick` en `HMA_ML_Orchestrator.mq5` para que `lastBarTime` solo se actualice *despu\u00e9s* de haber cargado con \u00e9xito todos los buffers de datos. Si un buffer falla (ej. H4 a\u00fan no sincronizado en el primer ms), retornar\u00e1 sin actualizar `lastBarTime` y se reintentar\u00e1 en el siguiente tick, resolviendo el desfase.\"",
  "ReplacementChunks": "[{\"AllowMultiple\":false,\"EndLine\":262,\"ReplacementContent\":\"void OnTick()\\n{\\n    // === BARRERA CPU: Detecci\u00f3n de Nueva Vela (Vela 0) ===\\n    static datetime lastBarTime = 0;\\n    datetime currentBarTime = iTime(_Symbol, _Period, 0);\\n    if(currentBarTime == lastBarTime) return; // Ya procesamos esta vela o estamos en espera\\n\\n    // === EXTRACCION DE DATOS ESTRICTA (SHIFT 1 - CERO LOOK-AHEAD) ===\\n    // Si alg\u00fan buffer falla (ej. H4 no sincronizado a\u00fan), salimos SIN actualizar lastBarTime.\\n    // Esto garantiza que el EA reintente milisegundos despu\u00e9s en el siguiente tick, sin perder la se\u00f1al.\\n    double hma[], rsi_buf[], atr_buf[], ef[], es[], sma20[], stddev[];\\n    double ema50_h4[], atr200_buf[]; \\n    MqlRates rates[];\\n    \\n    ArraySetAsSeries(hma, true);\\n    ArraySetAsSeries(rsi_buf, true);\\n    ArraySetAsSeries(atr_buf, true);\\n    ArraySetAsSeries(ef, true);\\n    ArraySetAsSeries(es, true);\\n    ArraySetAsSeries(sma20, true);\\n    ArraySetAsSeries(stddev, true);\\n    ArraySetAsSeries(ema50_h4, true);\\n    ArraySetAsSeries(atr200_buf, true);\\n    ArraySetAsSeries(rates, true);\\n\\n    if(CopyRates(_Symbol, _Period, 1, 3, rates) < 3) return;\\n    if(CopyBuffer(hma_handle, 0, 1, 4, hma) < 4)     return;\\n    if(CopyBuffer(rsi_handle, 0, 1, RsiLookbackBars + 1, rsi_buf) < RsiLookbackBars + 1) return;\\n    if(CopyBuffer(atr_handle, 0, 1, 51, atr_buf) < 51) return;\\n    if(CopyBuffer(atr200_handle, 0, 1, 1, atr200_buf) < 1) return;\\n    if(CopyBuffer(sma20_handle, 0, 1, 1, sma20) < 1)  return;\\n    if(CopyBuffer(std_dev_handle, 0, 1, 1, stddev) < 1) return;\\n\\n    // Sincronizacion MTF (Macro y H4): Usamos currentBarTime en vez de TimeCurrent() para ser exactos\\n    int macro_shift = iBarShift(_Symbol, g_macro_tf, currentBarTime);\\n    int h4_shift    = iBarShift(_Symbol, PERIOD_H4, currentBarTime);\\n    \\n    if(CopyBuffer(ema50_handle, 0, macro_shift + 1, 1, ef) < 1)     return;\\n    if(CopyBuffer(ema200_handle, 0, macro_shift + 1, 1, es) < 1)    return;\\n    if(CopyBuffer(ema50_h4_handle, 0, \n<truncated 4590 bytes>",
  "TargetFile": "\"C:\\\\Users\\\\Manuel\\\\Desktop\\\\HMA_MetaLabeling\\\\MQL5_Engine\\\\HMA_ML_Orchestrator.mq5\"",
  "toolAction": "\"Fixing OnTick logic\"",
  "toolSummary": "\"Fix OnTick logic in Orchestrator\""
}
```

## Step 1486 - Tool Response
```diff
@@ -205,26 +205,14 @@
 //+------------------------------------------------------------------+
 void OnTick()
 {
-    // === BARRERA CPU: Solo al cierre de vela ===
+    // === BARRERA CPU: Detección de Nueva Vela (Vela 0) ===
     static datetime lastBarTime = 0;
     datetime currentBarTime = iTime(_Symbol, _Period, 0);
-    if(currentBarTime == lastBarTime) return;
-    lastBarTime = currentBarTime;
-
-    // 1. Gestionar operaciones abiertas (Triple Barrera Vertical)
-    ManageTripleBarrier();
-
-    // 2. Solo 1 operacion a la vez
-    if(PositionSelect(_Symbol)) return;
-
-    // 3. Anti-broker: spread ceiling (AMC 2E - no anti-datos)
-    double pip = (SymbolInfoInteger(_Symbol, SYMBOL_DIGITS) % 2 == 1)
-                 ? 10 * _Point : _Point;
-    double spread = (SymbolInfoDouble(_Symbol, SYMBOL_ASK)
-                   - SymbolInfoDouble(_Symbol, SYMBOL_BID)) / pip;
-    if(spread > MaxSpreadPips) return;
+    if(currentBarTime == lastBarTime) return; // Ya procesamos esta vela o estamos en espera
 
     // === EXTRACCION DE DATOS ESTRICTA (SHIFT 1 - CERO LOOK-AHEAD) ===
+    // Si algún buffer falla (ej. H4 no sincronizado aún), salimos SIN actualizar lastBarTime.
+    // Esto garantiza que el EA reintente milisegundos después en el siguiente tick, sin perder la señal.
     double hma[], rsi_buf[], atr_buf[], ef[], es[], sma20[], stddev[];
     double ema50_h4[], atr200_buf[]; 
     MqlRates rates[];
@@ -247,9 +247,9 @@
     if(CopyBuffer(sma20_handle, 0, 1, 1, sma20) < 1)  return;
     if(CopyBuffer(std_dev_handle, 0, 1, 1, stddev) < 1) return;
 
-    // Sincronizacion MTF (Macro y H4): Encontrar vela actual y pedir la an
<truncated 522 bytes>
, macro_shift + 1, 1, es) < 1)    return;
@@ -259,10 +259,46 @@
     bool crossUp = (rates[1].close < hma[1] && rates[0].close > hma[0]);
     bool crossDn = (rates[1].close > hma[1] && rates[0].close < hma[0]);
 
-    // === ANTI-RUIDO: 2% ATR minimo (AMC 2D) ===
+    if(!crossUp && !crossDn) 
+    {
+        lastBarTime = currentBarTime; // No hay cruce, bloqueamos la vela
+        return;
+    }
+
+    // === GESTIÓN Y FILTROS PRE-TRADE ===
+    
+    // 1. Gestionar operaciones abiertas (Triple Barrera Vertical)
+    ManageTripleBarrier();
+
+    // 2. Solo 1 operacion a la vez
+    if(PositionSelect(_Symbol)) 
+    {
+        lastBarTime = currentBarTime;
+        return;
+    }
+
+    // 3. Anti-broker: spread ceiling (Filtro instantáneo, sin esperas)
+    double pip = (SymbolInfoInteger(_Symbol, SYMBOL_DIGITS) % 2 == 1) ? 10 * _Point : _Point;
+    double spread = (SymbolInfoDouble(_Symbol, SYMBOL_ASK) - SymbolInfoDouble(_Symbol, SYMBOL_BID)) / pip;
+    
+    if(spread > MaxSpreadPips) 
+    {
+        lastBarTime = currentBarTime; // Veto inmediato por coste. No retrasamos la orden.
+        Print("Señal vetada: Spread alto (", spread, " pips) en el momento exacto del cruce.");
+        return;
+    }
+
+    // 4. ANTI-RUIDO: 2% ATR minimo (AMC 2D)
     double minDev = atr_buf[0] * (AntiNoiseATRPct / 100.0);
     double deviation = MathAbs(rates[0].close - hma[0]);
-    if(deviation < minDev) return;
+    if(deviation < minDev) 
+    {
+        lastBarTime = currentBarTime;
+        return;
+    }
+
+    // Aprobado: Bloqueamos la vela para evitar duplicados y procedemos a disparar
+    lastBarTime = currentBarTime;
 
     // === DETERMINAR TIPO DE SENAL ===
     int signalType = crossUp ? 0 : 1; // 0=BUY, 1=SELL
```

## Step 1513 - Tool Call: multi_replace_file_content
**Instruction:** "1. Insertar el grupo de parámetros \"Filtros Macro\". 2. Validar que el tamaño de la vela de señal no exceda `InpMaxSignalBarATR`. 3. Validar que la distancia de SL normalizada por ATR no exceda `InpMaxSLATR`."
**Description:** "Añadir filtros dinámicos de outliers macroeconómicos en MQL5."

```json
{
  "Description": "\"A\u00f1adir filtros din\u00e1micos de outliers macroecon\u00f3micos en MQL5.\"",
  "Instruction": "\"1. Insertar el grupo de par\u00e1metros \\\"Filtros Macro\\\". 2. Validar que el tama\u00f1o de la vela de se\u00f1al no exceda `InpMaxSignalBarATR`. 3. Validar que la distancia de SL normalizada por ATR no exceda `InpMaxSLATR`.\"",
  "ReplacementChunks": "[{\"AllowMultiple\":false,\"EndLine\":45,\"ReplacementContent\":\"input group \\\"== Gestion ML (Triple Barrera y Riesgo Lineal) ==\\\"\\ninput double InpInitialBalance    = 100000.0; // Balance Inicial (Fijo para Extraccion)\\ninput double TakeProfitMultiplier = 3.0;   // TP Maximo (alto para registrar MFE real antes del SL).\\ninput int    VerticalBarrierBars  = 48;    // Barrera vertical: 48 velas (en M15 = 12h para desarrollarse)\\n\\ninput group \\\"== Filtros Macro / Cisnes Negros ==\\\"\\ninput double InpMaxSignalBarATR  = 2.5;    // Maximo tama\u00f1o de vela de senal en unidades ATR\\ninput double InpMaxSLATR         = 3.0;    // Distancia maxima permitida de SL en ATR\",\"StartLine\":42,\"TargetContent\":\"input group \\\"== Gestion ML (Triple Barrera y Riesgo Lineal) ==\\\"\\ninput double InpInitialBalance    = 100000.0; // Balance Inicial (Fijo para Extraccion)\\ninput double TakeProfitMultiplier = 3.0;   // TP Maximo (alto para registrar MFE real antes del SL).\\ninput int    VerticalBarrierBars  = 48;    // Barrera vertical: 48 velas (en M15 = 12h para desarrollarse)\"},{\"AllowMultiple\":false,\"EndLine\":288,\"ReplacementContent\":\"    // 4. ANTI-RUIDO: 2% ATR minimo (AMC 2D)\\n    double minDev = atr_buf[0] * (AntiNoiseATRPct / 100.0);\\n    double deviation = MathAbs(rates[0].close - hma[0]);\\n    if(deviation < minDev) \\n    {\\n        lastBarTime = currentBarTime;\\n        return;\\n    }\\n\\n    // 5. FILTRO MACRO: Expansi\u00f3n an\u00f3mala por Noticia (Cisne Negro)\\n    double candle_size = rates[0].high - rates[0].low;\\n    if(candle_size > (atr_buf[0] * InpMaxSignalBarATR))\\n    {\\n        lastBarTime = currentBarTime;\\n        Print(\\\"[RECHAZO NOTICIA] Vela de senal anomala por volatilidad extrema (\\\", candle_size/_Point, \\\" pts).\\\");\\n        return;\\n    }\",\"StartLine\":281,\"TargetContent\":\"    // 4. ANTI-RUIDO: 2% ATR minimo (AMC 2D)\\n    double minDev = atr_buf[0] * (AntiNoiseATRPct / 100.0);\\n    double deviation = MathAbs(rates[0].close - hma[0]);\\n    if(deviation < minDev) \\n    {\\n        lastBarTime = currentBarTime;\\n        return;\\\n<truncated 2290 bytes>",
  "TargetFile": "\"C:\\\\Users\\\\Manuel\\\\Desktop\\\\HMA_MetaLabeling\\\\MQL5_Engine\\\\HMA_ML_Orchestrator.mq5\"",
  "toolAction": "\"Adding Hard Filters to EA\"",
  "toolSummary": "\"Modify HMA_ML_Orchestrator.mq5\""
}
```

## Step 1514 - Tool Response
```diff
@@ -44,6 +44,10 @@
 input double TakeProfitMultiplier = 3.0;   // TP Maximo (alto para registrar MFE real antes del SL).
 input int    VerticalBarrierBars  = 48;    // Barrera vertical: 48 velas (en M15 = 12h para desarrollarse)
 
+input group "== Filtros Macro / Cisnes Negros =="
+input double InpMaxSignalBarATR  = 2.5;    // Maximo tamaño de vela de senal en unidades ATR
+input double InpMaxSLATR         = 3.0;    // Distancia maxima permitida de SL en ATR
+
 // === Handles de Indicadores ===
 int hma_handle, rsi_handle, atr_handle;
 int ema50_handle, ema200_handle;
@@ -286,6 +286,15 @@
         return;
     }
 
+    // 5. FILTRO MACRO: Expansión anómala por Noticia (Cisne Negro)
+    double candle_size = rates[0].high - rates[0].low;
+    if(candle_size > (atr_buf[0] * InpMaxSignalBarATR))
+    {
+        lastBarTime = currentBarTime;
+        Print("[RECHAZO NOTICIA] Vela de senal anomala por volatilidad extrema (", candle_size/_Point, " pts).");
+        return;
+    }
+
     // Aprobado: Bloqueamos la vela para evitar duplicados y procedemos a disparar
     lastBarTime = currentBarTime;
 
@@ -413,6 +413,17 @@
     
     if(slDist <= 0) return;
 
+    // Feature 15: SL Distance normalizada por ATR (para rechazo si es extrema)
+    double sl_dist_atr = (current_atr > 0) ? slDist / current_atr : 0.0;
+    
+    // 6. FILTRO ESTRUCTURAL: Stop Loss excesivamente holgado
+    if(sl_dist_atr > InpMaxSLATR)
+    {
+        // Cancelamos la orden para no destrozar el Sharpe
+        Print("[RECHAZO ESTRUCTURA] SL propuesto (", sl_dist_atr, " ATR) supera el limite maximo de ", InpMaxSLATR, " ATR.");
+        return;
+    }
+
     // FASE 2: Eliminacion del sesgo del TP fijo (True MFE Discovery)
     // Se fuerza el TP a 0 para que la operacion solo se cierre por SL o por la Barrera de Tiempo.
     // Esto permite al Logger registrar el verdadero Maximo Recorrido a Favor (MFE) sin truncarlo artificialmente.
@@ -419,7 +419,4 @@
 
-    // Feature 15: SL Distance normalizada por ATR
-    double sl_dist_atr = (current_atr > 0) ? slDist / current_atr : 0.0;
-
     // FASE 1.2: Guardar slDist en pips para calcular Max_RR_Achieved al cerrar
     // Se almacena directamente en el snapshot; el Logger lo usa al CommmitTrade
     // para calcular: Max_RR = MFE_precio / slDist
```

## Step 1535 - Tool Call: multi_replace_file_content
**Instruction:** "1. Change CopyRates and CopyBuffer for HMA to request 52 bars (with minimum 4). 2. Add HMA Velocity/Acceleration/Jerk and Energy_Accumulation calculations after Day_Of_Week. 3. Assign new features to the snapshot struct."
**Description:** "Expand CopyRates/CopyBuffer to 52 bars for energy accumulation, add kinematic feature calculations, and assign to snapshot."

```json
{
  "Description": "\"Expand CopyRates/CopyBuffer to 52 bars for energy accumulation, add kinematic feature calculations, and assign to snapshot.\"",
  "Instruction": "\"1. Change CopyRates and CopyBuffer for HMA to request 52 bars (with minimum 4). 2. Add HMA Velocity/Acceleration/Jerk and Energy_Accumulation calculations after Day_Of_Week. 3. Assign new features to the snapshot struct.\"",
  "ReplacementChunks": "[{\"AllowMultiple\":false,\"EndLine\":236,\"ReplacementContent\":\"    int rates_copied = CopyRates(_Symbol, _Period, 1, 52, rates);\\n    if(rates_copied < 4) return;  // Minimo 4 para Jerk (3ra derivada)\\n    int hma_copied = CopyBuffer(hma_handle, 0, 1, 52, hma);\\n    if(hma_copied < 4) return;    // Minimo 4 para Jerk (3ra derivada)\",\"StartLine\":235,\"TargetContent\":\"    if(CopyRates(_Symbol, _Period, 1, 3, rates) < 3) return;\\n    if(CopyBuffer(hma_handle, 0, 1, 4, hma) < 4)     return;\"},{\"AllowMultiple\":false,\"EndLine\":412,\"ReplacementContent\":\"    // --- Feature Alpha 6: Day_Of_Week ---\\n    int day_of_week = dt.day_of_week;\\n\\n    // ==========================================================================\\n    // CINEM\u00c1TICA HMA FASE 3: Derivadas de alto orden y energ\u00eda acumulada\\n    // ==========================================================================\\n    \\n    // HMA Velocity: Raw 1st derivative (velocidad del giro en precio)\\n    double hma_vel = hma[0] - hma[1];\\n    \\n    // HMA Acceleration: Raw 2nd derivative (fuerza de aceleraci\u00f3n)\\n    double vel_prev_k = hma[1] - hma[2];\\n    double hma_accel_v2 = hma_vel - vel_prev_k;\\n    \\n    // HMA Jerk: 3rd derivative (shock estructural del giro)\\n    double vel_prev2_k = hma[2] - hma[3];\\n    double accel_prev_k = vel_prev_k - vel_prev2_k;\\n    double hma_jerk_val = hma_accel_v2 - accel_prev_k;\\n    \\n    // Energy Accumulation: Velas consecutivas en el lado opuesto antes del cruce\\n    int energy_accum = 0;\\n    int max_energy_bars = MathMin(rates_copied, hma_copied);\\n    if(signalType == 0) { // BUY: price was below HMA before cross\\n        for(int k = 1; k < max_energy_bars; k++) {\\n            if(rates[k].close < hma[k]) energy_accum++;\\n            else break;\\n        }\\n    } else { // SELL: price was above HMA before cross\\n        for(int k = 1; k < max_energy_bars; k++) {\\n            if(rates[k].close > hma[k]) energy_accum++;\\n            else break;\\n        }\\n    }\",\"StartLine\":411,\"TargetContent\":\"    // --- Feature Alpha 6: Day_Of\n<truncated 527 bytes>",
  "TargetFile": "\"C:\\\\Users\\\\Manuel\\\\Desktop\\\\HMA_MetaLabeling\\\\MQL5_Engine\\\\HMA_ML_Orchestrator.mq5\"",
  "toolAction": "\"Adding kinematic features\"",
  "toolSummary": "\"Update HMA_ML_Orchestrator.mq5\""
}
```

## Step 1537 - Tool Response
```diff
@@ -232,8 +232,10 @@
     ArraySetAsSeries(atr200_buf, true);
     ArraySetAsSeries(rates, true);
 
-    if(CopyRates(_Symbol, _Period, 1, 3, rates) < 3) return;
-    if(CopyBuffer(hma_handle, 0, 1, 4, hma) < 4)     return;
+    int rates_copied = CopyRates(_Symbol, _Period, 1, 52, rates);
+    if(rates_copied < 4) return;  // Minimo 4 para Jerk (3ra derivada)
+    int hma_copied = CopyBuffer(hma_handle, 0, 1, 52, hma);
+    if(hma_copied < 4) return;    // Minimo 4 para Jerk (3ra derivada)
     if(CopyBuffer(rsi_handle, 0, 1, RsiLookbackBars + 1, rsi_buf) < RsiLookbackBars + 1) return;
     if(CopyBuffer(atr_handle, 0, 1, 51, atr_buf) < 51) return;
     if(CopyBuffer(atr200_handle, 0, 1, 1, atr200_buf) < 1) return;
@@ -410,6 +410,37 @@
     // --- Feature Alpha 6: Day_Of_Week ---
     int day_of_week = dt.day_of_week;
 
+    // ==========================================================================
+    // CINEMÁTICA HMA FASE 3: Derivadas de alto orden y energía acumulada
+    // ==========================================================================
+    
+    // HMA Velocity: Raw 1st derivative (velocidad del giro en precio)
+    double hma_vel = hma[0] - hma[1];
+    
+    // HMA Acceleration: Raw 2nd derivative (fuerza de aceleración)
+    double vel_prev_k = hma[1] - hma[2];
+    double hma_accel_v2 = hma_vel - vel_prev_k;
+    
+    // HMA Jerk: 3rd derivative (shock estructural del giro)
+    double vel_prev2_k = hma[2] - hma[3];
+    double accel_prev_k = vel_prev_k - vel_prev2_k;
+    double hma_jerk_val = hma_accel_v2 - accel_prev_k;
+    
+    // Energy Accumulation: Velas consecutivas en el lado opuesto antes del cruce
+    int energy_accum = 0;
+    int max_energy_bars = MathMin(rates_copied, hma_copied);
+    if(signalType == 0) { // BUY: price was below HMA before cross
+        for(int k = 1; k < max_energy_bars; k++) {
+            if(rates[k].close < hma[k]) energy_accum++;
+            else break;
+        }
+    } else { // SELL: price was above HMA before cross
+        for(int k = 1; k < max_energy_bars; k++) {
+            if(rates[k].close > hma[k]) energy_accum++;
+            else break;
+        }
+    }
+
     // === CALCULO DE SL/TP (AMC 4: High/Low para SL) ===
     double entry_price = (signalType == 0)
                          ? SymbolInfoDouble(_Symbol, SYMBOL_ASK)
@@ -509,6 +509,12 @@
         snap.hma_distance_ema    = hma_distance_ema;
         snap.breakout_body_ratio = breakout_body_ratio;
         snap.day_of_week         = day_of_week;
+        
+        // --- Features X: Cinemática HMA Fase 3 (NUEVAS) ---
+        snap.hma_velocity            = hma_vel;
+        snap.hma_acceleration_raw    = hma_accel_v2;
+        snap.hma_jerk                = hma_jerk_val;
+        snap.energy_accumulation     = energy_accum;
 
         // NOTA Zero-Trust: balance_momento y lots_utilizados NO se asignan
         // (eliminados del struct por ser post-trade/contaminados)
```

## Step 1564 - Tool Call: multi_replace_file_content
**Instruction:** "Reorganize OnTick so that dynamic exits and Triple Barrier are evaluated for open positions BEFORE the new cross filter returns. If a position is open, check if it should be closed via HMA dynamic logic or barrier, close it if necessary, and return."
**Description:** "Refactor OnTick for Dynamic Exit and correct Triple Barrier execution."

```json
{
  "Description": "\"Refactor OnTick for Dynamic Exit and correct Triple Barrier execution.\"",
  "Instruction": "\"Reorganize OnTick so that dynamic exits and Triple Barrier are evaluated for open positions BEFORE the new cross filter returns. If a position is open, check if it should be closed via HMA dynamic logic or barrier, close it if necessary, and return.\"",
  "ReplacementChunks": "[{\"AllowMultiple\":false,\"EndLine\":275,\"ReplacementContent\":\"    // === DETECCION DE CRUCE HMA (con Close, AMC: Resiliencia a Mechas) ===\\n    // rates[0]/hma[0] es Shift 1 (Cerrada), rates[1]/hma[1] es Shift 2 (Anterior Cerrada)\\n    bool crossUp = (rates[1].close < hma[1] && rates[0].close > hma[0]);\\n    bool crossDn = (rates[1].close > hma[1] && rates[0].close < hma[0]);\\n\\n    // === GESTI\u00d3N DE POSICIONES ABIERTAS (EXIT DIN\u00c1MICO Y BARRERA) ===\\n    if(PositionSelect(_Symbol)) \\n    {\\n        ulong ticket = PositionGetTicket(0);\\n        long pos_type = PositionGetInteger(POSITION_TYPE);\\n        bool should_close = false;\\n        \\n        // 1. Cierre Din\u00e1mico por HMA (Trend-Following Exit)\\n        // Se cierra si ocurre el cruce opuesto o la pendiente de la HMA se vuelve adversa\\n        if(pos_type == POSITION_TYPE_BUY && (crossDn || hma[0] < hma[1])) should_close = true;\\n        if(pos_type == POSITION_TYPE_SELL && (crossUp || hma[0] > hma[1])) should_close = true;\\n        \\n        if(should_close) {\\n            PrintFormat(\\\"Cierre dinamico por HMA. Ticket: %I64u\\\", ticket);\\n            trade.PositionClose(ticket);\\n        } else {\\n            // 2. Triple Barrera Vertical (solo si no se cerr\u00f3 din\u00e1micamente)\\n            datetime open_time = (datetime)PositionGetInteger(POSITION_TIME);\\n            int current_bar = iBarShift(_Symbol, _Period, currentBarTime);\\n            int open_bar    = iBarShift(_Symbol, _Period, open_time);\\n            if((open_bar - current_bar) >= VerticalBarrierBars) {\\n                PrintFormat(\\\"Cierre por Triple Barrera. Ticket: %I64u\\\", ticket);\\n                trade.PositionClose(ticket);\\n            }\\n        }\\n        \\n        lastBarTime = currentBarTime; // Bloqueamos la vela para no abrir otra inmediatamente\\n        return;\\n    }\\n\\n    if(!crossUp && !crossDn) \\n    {\\n        lastBarTime = currentBarTime; // No hay cruce, bloqueamos la vela\\n        return;\\n    }\\n\\n    // === GESTI\u00d3N Y FILTROS PRE-TRADE ===\",\"StartLine\":253,\"TargetContent\"\n<truncated 752 bytes>",
  "TargetFile": "\"C:\\\\Users\\\\Manuel\\\\Desktop\\\\HMA_MetaLabeling\\\\MQL5_Engine\\\\HMA_ML_Orchestrator.mq5\"",
  "toolAction": "\"Refactoring OnTick exit logic\"",
  "toolSummary": "\"Update OnTick for Dynamic Exit\""
}
```

## Step 1565 - Tool Response
```diff
@@ -255,6 +255,36 @@
     bool crossUp = (rates[1].close < hma[1] && rates[0].close > hma[0]);
     bool crossDn = (rates[1].close > hma[1] && rates[0].close < hma[0]);
 
+    // === GESTIÓN DE POSICIONES ABIERTAS (EXIT DINÁMICO Y BARRERA) ===
+    if(PositionSelect(_Symbol)) 
+    {
+        ulong ticket = PositionGetTicket(0);
+        long pos_type = PositionGetInteger(POSITION_TYPE);
+        bool should_close = false;
+        
+        // 1. Cierre Dinámico por HMA (Trend-Following Exit)
+        // Se cierra si ocurre el cruce opuesto o la pendiente de la HMA se vuelve adversa
+        if(pos_type == POSITION_TYPE_BUY && (crossDn || hma[0] < hma[1])) should_close = true;
+        if(pos_type == POSITION_TYPE_SELL && (crossUp || hma[0] > hma[1])) should_close = true;
+        
+        if(should_close) {
+            PrintFormat("Cierre dinamico por HMA. Ticket: %I64u", ticket);
+            trade.PositionClose(ticket);
+        } else {
+            // 2. Triple Barrera Vertical (solo si no se cerró dinámicamente)
+            datetime open_time = (datetime)PositionGetInteger(POSITION_TIME);
+            int current_bar = iBarShift(_Symbol, _Period, currentBarTime);
+            int open_bar    = iBarShift(_Symbol, _Period, open_time);
+            if((open_bar - current_bar) >= VerticalBarrierBars) {
+                PrintFormat("Cierre por Triple Barrera. Ticket: %I64u", ticket);
+                trade.PositionClose(ticket);
+            }
+        }
+        
+        lastBarTime = currentBarTime; // Bloqueamos la vela para no abrir otra inmediatamente
+        return;
+    }
+
     if(!crossUp && !crossDn) 
     {
         lastBarTime = currentBarTime; // No hay cruce, bloqueamos la vela
@@ -261,16 +261,6 @@
     }
 
     // === GESTIÓN Y FILTROS PRE-TRADE ===
-    
-    // 1. Gestionar operaciones abiertas (Triple Barrera Vertical)
-    ManageTripleBarrier();
-
-    // 2. Solo 1 operacion a la vez
-    if(PositionSelect(_Symbol)) 
-    {
-        lastBarTime = currentBarTime;
-        return;
-    }
 
     // 3. Anti-broker: spread ceiling (Filtro instantáneo, sin esperas)
     double pip = (SymbolInfoInteger(_Symbol, SYMBOL_DIGITS) % 2 == 1) ? 10 * _Point : _Point;
```

## Step 1700 - Tool Response
```diff
@@ -268,7 +268,17 @@
         if(pos_type == POSITION_TYPE_SELL && (crossUp || hma[0] > hma[1])) should_close = true;
         
         if(should_close) {
-            PrintFormat("Cierre dinamico por HMA. Ticket: %I64u", ticket);
+            double open_price = PositionGetDouble(POSITION_PRICE_OPEN);
+            double current_price = PositionGetDouble(POSITION_PRICE_CURRENT);
+            string tipo_str = (pos_type == POSITION_TYPE_BUY) ? "BUY" : "SELL";
+            double _pip_val = (SymbolInfoInteger(_Symbol, SYMBOL_DIGITS) % 2 == 1) ? 10 * _Point : _Point;
+            double pips_ganados = (pos_type == POSITION_TYPE_BUY) ? (current_price - open_price) / _pip_val : (open_price - current_price) / _pip_val;
+            double sl_level = PositionGetDouble(POSITION_SL);
+            double sl_dist = MathAbs(open_price - sl_level);
+            double realized_rr = (sl_dist > 0) ? ((pos_type == POSITION_TYPE_BUY) ? (current_price - open_price) / sl_dist : (open_price - current_price) / sl_dist) : 0.0;
+            
+            PrintFormat("[AUDITORIA HMA EXIT] Ticket: %I64u | Tipo: %s | Precio Apertura: %.5f | Precio Cierre: %.5f | Estado HMA_Vela_1: %.5f | Estado HMA_Vela_2: %.5f | Pips Ganados: %.1f | Realized_RR: %.2f",
+                        ticket, tipo_str, open_price, current_price, hma[0], hma[1], pips_ganados, realized_rr);
             trade.PositionClose(ticket);
         } else {
             // 2. Triple Barrera Vertical (solo si no se cerró dinámicamente)
```

## Step 1711 - Tool Call: multi_replace_file_content
**Instruction:** "Add CheckDynamicHMAExit above OnTick and call it from inside OnTick."
**Description:** "Implement CheckDynamicHMAExit function and replace inline logic."

```json
{
  "Description": "\"Implement CheckDynamicHMAExit function and replace inline logic.\"",
  "Instruction": "\"Add CheckDynamicHMAExit above OnTick and call it from inside OnTick.\"",
  "ReplacementChunks": "[{\"AllowMultiple\":false,\"EndLine\":211,\"ReplacementContent\":\"//+------------------------------------------------------------------+\\n//| CheckDynamicHMAExit: Cierre din\u00e1mico por HMA con auditor\u00eda forense |\\n//+------------------------------------------------------------------+\\nbool CheckDynamicHMAExit(double hma_1, double hma_2)\\n{\\n    bool has_positions = PositionSelect(_Symbol);\\n    if(has_positions)\\n    {\\n        long type = PositionGetInteger(POSITION_TYPE);\\n        ulong ticket = PositionGetInteger(POSITION_TICKET);\\n        double open_price = PositionGetDouble(POSITION_PRICE_OPEN);\\n        double sl_price = PositionGetDouble(POSITION_SL);\\n        \\n        double current_price = 0.0;\\n        if(type == POSITION_TYPE_BUY) current_price = SymbolInfoDouble(_Symbol, SYMBOL_BID);\\n        if(type == POSITION_TYPE_SELL) current_price = SymbolInfoDouble(_Symbol, SYMBOL_ASK);\\n        \\n        bool close_buy = (type == POSITION_TYPE_BUY && hma_1 < hma_2);\\n        bool close_sell = (type == POSITION_TYPE_SELL && hma_1 > hma_2);\\n        \\n        if(close_buy || close_sell)\\n        {\\n            double risk = MathAbs(open_price - sl_price);\\n            double profit = 0.0;\\n            \\n            if(type == POSITION_TYPE_BUY) profit = current_price - open_price;\\n            if(type == POSITION_TYPE_SELL) profit = open_price - current_price;\\n            \\n            double realized_rr = 0.0;\\n            if(risk > 0) realized_rr = profit / risk;\\n            \\n            double pip_val = (SymbolInfoInteger(_Symbol, SYMBOL_DIGITS) % 2 == 1) ? 10 * _Point : _Point;\\n            double pips = profit / pip_val;\\n            string tipo_str = (type == POSITION_TYPE_BUY) ? \\\"BUY\\\" : \\\"SELL\\\";\\n            \\n            PrintFormat(\\\"[AUDITORIA HMA EXIT] Ticket: %I64u | Tipo: %s | Precio Apertura: %.5f | Precio Cierre: %.5f | Estado HMA_Vela_1: %.5f | Estado HMA_Vela_2: %.5f | Pips Ganados: %.1f | Realized_RR: %.2f\\\",\\n                        ticket, tipo_str, open_price, current_price, hma_1, hma_2, \n<truncated 4246 bytes>",
  "TargetFile": "\"c:\\\\Users\\\\Manuel\\\\Desktop\\\\HMA_MetaLabeling\\\\MQL5_Engine\\\\HMA_ML_Orchestrator.mq5\"",
  "toolAction": "\"Implementing CheckDynamicHMAExit and refactoring OnTick\"",
  "toolSummary": "\"Implement CheckDynamicHMAExit\""
}
```

## Step 1712 - Tool Response
```diff
@@ -205,6 +205,51 @@
 }
 
 //+------------------------------------------------------------------+
+//| CheckDynamicHMAExit: Cierre dinámico por HMA con auditoría forense |
+//+------------------------------------------------------------------+
+bool CheckDynamicHMAExit(double hma_1, double hma_2)
+{
+    bool has_positions = PositionSelect(_Symbol);
+    if(has_positions)
+    {
+        long type = PositionGetInteger(POSITION_TYPE);
+        ulong ticket = PositionGetInteger(POSITION_TICKET);
+        double open_price = PositionGetDouble(POSITION_PRICE_OPEN);
+        double sl_price = PositionGetDouble(POSITION_SL);
+        
+        double current_price = 0.0;
+        if(type == POSITION_TYPE_BUY) current_price = SymbolInfoDouble(_Symbol, SYMBOL_BID);
+        if(type == POSITION_TYPE_SELL) current_price = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
+        
+        bool close_buy = (type == POSITION_TYPE_BUY && hma_1 < hma_2);
+        bool close_sell = (type == POSITION_TYPE_SELL && hma_1 > hma_2);
+        
+        if(close_buy || close_sell)
+        {
+            double risk = MathAbs(open_price - sl_price);
+            double profit = 0.0;
+            
+            if(type == POSITION_TYPE_BUY) profit = current_price - open_price;
+            if(type == POSITION_TYPE_SELL) profit = open_price - current_price;
+            
+            double realized_rr = 0.0;
+            if(risk > 0) realized_rr = profit / risk;
+            
+            double pip_val = (SymbolInfoInteger(_Symbol, SYMBOL_DIGITS) % 2 == 1) ? 10 * _Point : _Point;
+            double pips = profit / pip_val;
+            string tipo_str = (type == POSI
<truncated 1297 bytes>
(pos_type == POSITION_TYPE_SELL && (crossUp || hma[0] > hma[1])) should_close = true;
-        
-        if(should_close) {
-            double open_price = PositionGetDouble(POSITION_PRICE_OPEN);
-            double current_price = PositionGetDouble(POSITION_PRICE_CURRENT);
-            string tipo_str = (pos_type == POSITION_TYPE_BUY) ? "BUY" : "SELL";
-            double _pip_val = (SymbolInfoInteger(_Symbol, SYMBOL_DIGITS) % 2 == 1) ? 10 * _Point : _Point;
-            double pips_ganados = (pos_type == POSITION_TYPE_BUY) ? (current_price - open_price) / _pip_val : (open_price - current_price) / _pip_val;
-            double sl_level = PositionGetDouble(POSITION_SL);
-            double sl_dist = MathAbs(open_price - sl_level);
-            double realized_rr = (sl_dist > 0) ? ((pos_type == POSITION_TYPE_BUY) ? (current_price - open_price) / sl_dist : (open_price - current_price) / sl_dist) : 0.0;
-            
-            PrintFormat("[AUDITORIA HMA EXIT] Ticket: %I64u | Tipo: %s | Precio Apertura: %.5f | Precio Cierre: %.5f | Estado HMA_Vela_1: %.5f | Estado HMA_Vela_2: %.5f | Pips Ganados: %.1f | Realized_RR: %.2f",
-                        ticket, tipo_str, open_price, current_price, hma[0], hma[1], pips_ganados, realized_rr);
-            trade.PositionClose(ticket);
-        } else {
+        bool closed_by_hma = CheckDynamicHMAExit(hma[0], hma[1]);
+        
+        if(!closed_by_hma) {
             // 2. Triple Barrera Vertical (solo si no se cerró dinámicamente)
+            ulong ticket = PositionGetTicket(0);
             datetime open_time = (datetime)PositionGetInteger(POSITION_TIME);
             int current_bar = iBarShift(_Symbol, _Period, currentBarTime);
             int open_bar    = iBarShift(_Symbol, _Period, open_time);
```

## Step 1736 - Tool Call: multi_replace_file_content
**Instruction:** "Add new variables, initialize a new HMA indicator for the exit, copy its buffer, and update CheckDynamicHMAExit with the Time-Stop condition."
**Description:** "Add Slow HMA Exit and Time-Stop Filter to solve Whipsawing."

```json
{
  "Description": "\"Add Slow HMA Exit and Time-Stop Filter to solve Whipsawing.\"",
  "Instruction": "\"Add new variables, initialize a new HMA indicator for the exit, copy its buffer, and update CheckDynamicHMAExit with the Time-Stop condition.\"",
  "ReplacementChunks": "[{\"AllowMultiple\":false,\"EndLine\":30,\"ReplacementContent\":\"input group \\\"== Estrategia HMA ==\\\"\\ninput int    HMAPeriod           = 50;     // HMA50: estandar para swing intradiario. No tocar.\\ninput int    InpHMA_ExitPeriod   = 100;    // HMA Lenta exclusiva para el Cierre Din\u00e1mico.\\ninput int    InpMinBarsToHold    = 3;      // Filtro Time-Stop: Minimo de velas a aguantar antes de salir.\\ninput int    LookbackBars        = 7;      // Ventana SL/Pullback: 7 velas (en M15 = ~1h45m de estructura)\\ninput double AntiNoiseATRPct     = 2.0;    // Anti-ruido: 2% ATR. Permisivo para Alto Recall.\",\"StartLine\":27,\"TargetContent\":\"input group \\\"== Estrategia HMA ==\\\"\\ninput int    HMAPeriod           = 50;     // HMA50: estandar para swing intradiario. No tocar.\\ninput int    LookbackBars        = 7;      // Ventana SL/Pullback: 7 velas (en M15 = ~1h45m de estructura)\\ninput double AntiNoiseATRPct     = 2.0;    // Anti-ruido: 2% ATR. Permisivo para Alto Recall.\"},{\"AllowMultiple\":false,\"EndLine\":52,\"ReplacementContent\":\"// === Handles de Indicadores ===\\nint hma_handle, hma_exit_handle, rsi_handle, atr_handle;\",\"StartLine\":51,\"TargetContent\":\"// === Handles de Indicadores ===\\nint hma_handle, rsi_handle, atr_handle;\"},{\"AllowMultiple\":false,\"EndLine\":87,\"ReplacementContent\":\"    // Cargar Indicadores\\n    hma_handle     = iCustom(_Symbol, _Period, \\\"HMA50\\\", HMAPeriod);\\n    hma_exit_handle= iCustom(_Symbol, _Period, \\\"HMA50\\\", InpHMA_ExitPeriod);\\n    rsi_handle     = iRSI(_Symbol, _Period, RsiPeriod, PRICE_CLOSE);\\n    atr_handle     = iATR(_Symbol, _Period, 14);\",\"StartLine\":84,\"TargetContent\":\"    // Cargar Indicadores\\n    hma_handle     = iCustom(_Symbol, _Period, \\\"HMA50\\\", HMAPeriod);\\n    rsi_handle     = iRSI(_Symbol, _Period, RsiPeriod, PRICE_CLOSE);\\n    atr_handle     = iATR(_Symbol, _Period, 14);\"},{\"AllowMultiple\":false,\"EndLine\":101,\"ReplacementContent\":\"    if(hma_handle == INVALID_HANDLE || hma_exit_handle == INVALID_HANDLE || rsi_handle == INVALID_HANDLE ||\\n       atr_handle == INVALID_HANDLE || std_de\n<truncated 3727 bytes>",
  "TargetFile": "\"c:\\\\Users\\\\Manuel\\\\Desktop\\\\HMA_MetaLabeling\\\\MQL5_Engine\\\\HMA_ML_Orchestrator.mq5\"",
  "toolAction": "\"Adding HMA exit logic variables and rules\"",
  "toolSummary": "\"Add HMA Exit rules in MQL5\""
}
```

## Step 1737 - Tool Response
```diff
@@ -26,6 +26,8 @@
 
 input group "== Estrategia HMA =="
 input int    HMAPeriod           = 50;     // HMA50: estandar para swing intradiario. No tocar.
+input int    InpHMA_ExitPeriod   = 100;    // HMA Lenta exclusiva para el Cierre Dinámico.
+input int    InpMinBarsToHold    = 3;      // Filtro Time-Stop: Minimo de velas a aguantar antes de salir.
 input int    LookbackBars        = 7;      // Ventana SL/Pullback: 7 velas (en M15 = ~1h45m de estructura)
 input double AntiNoiseATRPct     = 2.0;    // Anti-ruido: 2% ATR. Permisivo para Alto Recall.
 
@@ -48,7 +48,7 @@
 input double InpMaxSLATR         = 3.0;    // Distancia maxima permitida de SL en ATR
 
 // === Handles de Indicadores ===
-int hma_handle, rsi_handle, atr_handle;
+int hma_handle, hma_exit_handle, rsi_handle, atr_handle;
 int ema50_handle, ema200_handle;
 int sma20_handle, std_dev_handle;
 int ema50_h4_handle;  // EMA(50) fijo en H4 para H4_Trend_Align
@@ -81,6 +81,7 @@
 
     // Cargar Indicadores
     hma_handle     = iCustom(_Symbol, _Period, "HMA50", HMAPeriod);
+    hma_exit_handle= iCustom(_Symbol, _Period, "HMA50", InpHMA_ExitPeriod);
     rsi_handle     = iRSI(_Symbol, _Period, RsiPeriod, PRICE_CLOSE);
     atr_handle     = iATR(_Symbol, _Period, 14);
     ema50_handle   = iMA(_Symbol, g_macro_tf, 50, 0, MODE_EMA, PRICE_CLOSE);
@@ -94,7 +94,7 @@
     // No requiere handle adicional (atr_buf[0]=actual, atr_buf[1..50]=SMA50 manual)
 
 
-    if(hma_handle == INVALID_HANDLE || rsi_handle == INVALID_HANDLE ||
+    if(hma_handle == INVALID_HANDLE || hma_exit_handle == INVALID_HANDLE || rsi_handle == INVALID_HANDLE ||
        atr_handle == INVALID_HANDLE || std_dev_handle == 
<truncated 1122 bytes>
S ESTRICTA (SHIFT 1 - CERO LOOK-AHEAD) ===
     // Si algún buffer falla (ej. H4 no sincronizado aún), salimos SIN actualizar lastBarTime.
     // Esto garantiza que el EA reintente milisegundos después en el siguiente tick, sin perder la señal.
-    double hma[], rsi_buf[], atr_buf[], ef[], es[], sma20[], stddev[];
+    double hma[], hma_exit_buf[], rsi_buf[], atr_buf[], ef[], es[], sma20[], stddev[];
     double ema50_h4[], atr200_buf[]; 
     MqlRates rates[];
     
@@ -263,3 +263,4 @@
+    ArraySetAsSeries(hma_exit_buf, true);
     ArraySetAsSeries(rsi_buf, true);
     ArraySetAsSeries(atr_buf, true);
     ArraySetAsSeries(ef, true);
@@ -273,6 +273,8 @@
     if(rates_copied < 4) return;  // Minimo 4 para Jerk (3ra derivada)
     int hma_copied = CopyBuffer(hma_handle, 0, 1, 52, hma);
     if(hma_copied < 4) return;    // Minimo 4 para Jerk (3ra derivada)
+    int hma_exit_copied = CopyBuffer(hma_exit_handle, 0, 1, 2, hma_exit_buf);
+    if(hma_exit_copied < 2) return;
     if(CopyBuffer(rsi_handle, 0, 1, RsiLookbackBars + 1, rsi_buf) < RsiLookbackBars + 1) return;
     if(CopyBuffer(atr_handle, 0, 1, 51, atr_buf) < 51) return;
     if(CopyBuffer(atr200_handle, 0, 1, 1, atr200_buf) < 1) return;
@@ -294,8 +294,8 @@
     // === GESTIÓN DE POSICIONES ABIERTAS (EXIT DINÁMICO Y BARRERA) ===
     if(PositionSelect(_Symbol)) 
     {
-        // 1. Cierre Dinámico por HMA (Trend-Following Exit)
-        bool closed_by_hma = CheckDynamicHMAExit(hma[0], hma[1]);
+        // 1. Cierre Dinámico por HMA Lenta (Trend-Following Exit) con respiro
+        bool closed_by_hma = CheckDynamicHMAExit(hma_exit_buf[0], hma_exit_buf[1]);
         
         if(!closed_by_hma) {
             // 2. Triple Barrera Vertical (solo si no se cerró dinámicamente)
```

## Step 1773 - Tool Call: multi_replace_file_content
**Instruction:** "Update global variables, initialize exit_logger, update CheckDynamicHMAExit signature and body to log exits instead of closing trades."
**Description:** "Integrate CExitDataLogger and update CheckDynamicHMAExit"

```json
{
  "Description": "\"Integrate CExitDataLogger and update CheckDynamicHMAExit\"",
  "Instruction": "\"Update global variables, initialize exit_logger, update CheckDynamicHMAExit signature and body to log exits instead of closing trades.\"",
  "ReplacementChunks": "[{\"AllowMultiple\":false,\"EndLine\":24,\"ReplacementContent\":\"CTrade trade;\\nCMLDataLogger *logger;\\nCExitDataLogger *exit_logger;\\n\\n// === Parametros de Entrada (Defaults optimizados para Meta-Labeling) ===\",\"StartLine\":22,\"TargetContent\":\"CTrade trade;\\nCMLDataLogger *logger;\\n\\n// === Parametros de Entrada (Defaults optimizados para Meta-Labeling) ===\"},{\"AllowMultiple\":false,\"EndLine\":85,\"ReplacementContent\":\"    // Inicializar Motor de Persistencia ML\\n    string filename = \\\"HMA_Dataset_\\\" + _Symbol + \\\".csv\\\";\\n    logger = new CMLDataLogger(filename);\\n    exit_logger = new CExitDataLogger(_Symbol);\\n\\n    // Cargar Indicadores\",\"StartLine\":82,\"TargetContent\":\"    // Inicializar Motor de Persistencia ML\\n    string filename = \\\"HMA_Dataset_\\\" + _Symbol + \\\".csv\\\";\\n    logger = new CMLDataLogger(filename);\\n\\n    // Cargar Indicadores\"},{\"AllowMultiple\":false,\"EndLine\":122,\"ReplacementContent\":\"{\\n    delete logger;\\n    delete exit_logger;\",\"StartLine\":121,\"TargetContent\":\"{\\n    delete logger;\"},{\"AllowMultiple\":false,\"EndLine\":250,\"ReplacementContent\":\"//+------------------------------------------------------------------+\\n//| CheckDynamicHMAExit: Cierre din\u00e1mico por HMA con auditor\u00eda forense |\\n//+------------------------------------------------------------------+\\nbool CheckDynamicHMAExit(double hma_1, double hma_2, double hma_3, double current_rsi, double current_atr, double atr_sma50, double spread)\\n{\\n    bool has_positions = PositionSelect(_Symbol);\\n    if(has_positions)\\n    {\\n        ulong ticket = PositionGetInteger(POSITION_TICKET);\\n        datetime open_time = (datetime)PositionGetInteger(POSITION_TIME);\\n        int bars_in_trade = iBarShift(_Symbol, _Period, open_time);\\n        \\n        // Filtro Time-Stop: Darle respiro al trade antes de salir por HMA lenta\\n        if(bars_in_trade < InpMinBarsToHold) return false;\\n        \\n        long type = PositionGetInteger(POSITION_TYPE);\\n        double open_price = PositionGetDouble(POSITION_PRICE_OPEN);\\n        double sl_price = Positio\n<truncated 7693 bytes>",
  "TargetFile": "\"c:\\\\Users\\\\Manuel\\\\Desktop\\\\HMA_MetaLabeling\\\\MQL5_Engine\\\\HMA_ML_Orchestrator.mq5\"",
  "toolAction": "\"Inject CExitDataLogger and modify CheckDynamicHMAExit\"",
  "toolSummary": "\"Integrate CExitDataLogger\""
}
```

## Step 1774 - Tool Response
```diff
@@ -21,6 +21,7 @@
 
 CTrade trade;
 CMLDataLogger *logger;
+CExitDataLogger *exit_logger;
 
 // === Parametros de Entrada (Defaults optimizados para Meta-Labeling) ===
 
@@ -81,6 +81,7 @@
     // Inicializar Motor de Persistencia ML
     string filename = "HMA_Dataset_" + _Symbol + ".csv";
     logger = new CMLDataLogger(filename);
+    exit_logger = new CExitDataLogger(_Symbol);
 
     // Cargar Indicadores
     hma_handle     = iCustom(_Symbol, _Period, "HMA50", HMAPeriod);
@@ -118,6 +118,7 @@
 void OnDeinit(const int reason)
 {
     delete logger;
+    delete exit_logger;
     IndicatorRelease(hma_handle);
     IndicatorRelease(hma_exit_handle);
     IndicatorRelease(rsi_handle);
@@ -208,7 +208,7 @@
 //+------------------------------------------------------------------+
 //| CheckDynamicHMAExit: Cierre dinámico por HMA con auditoría forense |
 //+------------------------------------------------------------------+
-bool CheckDynamicHMAExit(double hma_1, double hma_2)
+bool CheckDynamicHMAExit(double hma_1, double hma_2, double hma_3, double current_rsi, double current_atr, double atr_sma50, double spread)
 {
     bool has_positions = PositionSelect(_Symbol);
     if(has_positions)
@@ -227,8 +227,9 @@
         if(type == POSITION_TYPE_BUY) current_price = SymbolInfoDouble(_Symbol, SYMBOL_BID);
         if(type == POSITION_TYPE_SELL) current_price = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
         
-        bool close_buy = (type == POSITION_TYPE_BUY && hma_1 < hma_2);
-        bool close_sell = (type == POSITION_TYPE_SELL && hma_1 > hma_2);
+        // Edge Detection: Solo logueamos en el instante exacto en que la pendiente cruza
+    
<truncated 3501 bytes>
emporal para entrenar el modelo.
+            return false;
         }
     }
     return false;
@@ -285,8 +285,8 @@
     if(rates_copied < 4) return;  // Minimo 4 para Jerk (3ra derivada)
     int hma_copied = CopyBuffer(hma_handle, 0, 1, 52, hma);
     if(hma_copied < 4) return;    // Minimo 4 para Jerk (3ra derivada)
-    int hma_exit_copied = CopyBuffer(hma_exit_handle, 0, 1, 2, hma_exit_buf);
-    if(hma_exit_copied < 2) return;
+    int hma_exit_copied = CopyBuffer(hma_exit_handle, 0, 1, 3, hma_exit_buf);
+    if(hma_exit_copied < 3) return;
     if(CopyBuffer(rsi_handle, 0, 1, RsiLookbackBars + 1, rsi_buf) < RsiLookbackBars + 1) return;
     if(CopyBuffer(atr_handle, 0, 1, 51, atr_buf) < 51) return;
     if(CopyBuffer(atr200_handle, 0, 1, 1, atr200_buf) < 1) return;
@@ -308,8 +308,15 @@
     // === GESTIÓN DE POSICIONES ABIERTAS (EXIT DINÁMICO Y BARRERA) ===
     if(PositionSelect(_Symbol)) 
     {
+        double pip = (SymbolInfoInteger(_Symbol, SYMBOL_DIGITS) % 2 == 1) ? 10 * _Point : _Point;
+        double spread = (SymbolInfoDouble(_Symbol, SYMBOL_ASK) - SymbolInfoDouble(_Symbol, SYMBOL_BID)) / pip;
+        
+        double atr_sma50_sum = 0.0;
+        for(int k = 1; k <= 50; k++) atr_sma50_sum += atr_buf[k];
+        double atr_sma50 = (atr_sma50_sum > 0) ? atr_sma50_sum / 50.0 : atr_buf[0];
+        
         // 1. Cierre Dinámico por HMA Lenta (Trend-Following Exit) con respiro
-        bool closed_by_hma = CheckDynamicHMAExit(hma_exit_buf[0], hma_exit_buf[1]);
+        bool closed_by_hma = CheckDynamicHMAExit(hma_exit_buf[0], hma_exit_buf[1], hma_exit_buf[2], rsi_buf[0], atr_buf[0], atr_sma50, spread);
         
         if(!closed_by_hma) {
             // 2. Triple Barrera Vertical (solo si no se cerró dinámicamente)
```

## Step 1831 - Tool Response
```diff
@@ -5,6 +5,16 @@
   - `[x]` Implement CSV creation (`HMA_Exit_Dataset_SYMBOL.csv`)
   - `[x]` Implement `RecordExitAttempt` (Add to pending array)
   - `[x]` Implement `CommitExitsForTrade` (Calculate Missed Profit & flush to CSV)
+- `[x]` Develop CExitDataLogger in MQL5 to record dynamic exit decisions without executing them.
+- `[x]` Refactor MQL5 logic to allow trades to reach Triple Barrier or physical SL, computing Missed_Profit_R.
+- `[x]` Create Python dataset verification to check label distributions (MFE vs SL).
+
+## Phase 5.1: Dataset Expansion & Multi-Node Triggers
+- `[/]` Implement One-Hot Encoding for triggers (`Is_Trigger_Fast`, `Is_Trigger_Slow`, `Is_Trigger_RSI`, `Is_Trigger_Profit`).
+- `[/]` Define dynamic `VerticalBarrierBars = InpHMA_ExitPeriod * 1.5`.
+- `[/]` Comply with Strict MQL5 Rules (No `break`/`continue`/`pass`, No `HistoryPositionGetInteger`, Author: "Manuel").
+- `[ ]` Train XGBoost Secondary Model.
+
 - `[x]` Integrate `CExitDataLogger` in `HMA_ML_Orchestrator.mq5`
   - `[x]` Initialize and de-initialize `exit_logger`
   - `[x]` Modify `CheckDynamicHMAExit` to generate `ExitSnapshot` instead of closing physically
```

## Step 1839 - Tool Call: write_to_file

```json
{
  "ArtifactMetadata": "{\"ArtifactType\":\"other\",\"RequestFeedback\":false,\"Summary\":\"Rewrote HMA_ML_Orchestrator.mq5 according to strict Phase 5.1 rules (Multi-Node Triggers, Dynamic Vertical Barrier, Author Manuel).\"}",
  "CodeContent": "\"//+------------------------------------------------------------------+\\n//|                                          HMA_ML_Orchestrator.mq5 |\\n//|        Generador Cuantitativo de Datasets (Meta-Labeling v2.1)   |\\n//|        Autor: Manuel                                             |\\n//|        Fase 5.1: Multi-Node Triggers, Profit Trailing, Strict    |\\n//+------------------------------------------------------------------+\\n#property strict\\n#property version \\\"2.1\\\"\\n#property description \\\"HMA Meta-Labeling Dataset Generator - Phase 5.1\\\"\\n\\n#include <Trade\\\\Trade.mqh>\\n#include \\\"ML_Logger.mqh\\\"\\n#include \\\"HMA_FUNCTIONS.mqh\\\"\\n\\nCTrade trade;\\nCMLDataLogger *logger;\\nCExitDataLogger *exit_logger;\\n\\n// === Parametros de Entrada ===\\n\\ninput group \\\"== Estrategia HMA ==\\\"\\ninput int    HMAPeriod           = 50;     \\ninput int    InpHMA_ExitPeriod   = 100;    \\ninput int    InpMinBarsToHold    = 3;      \\ninput int    LookbackBars        = 7;      \\ninput double AntiNoiseATRPct     = 2.0;    \\n\\ninput group \\\"== Contexto y Features ==\\\"\\ninput int    RsiPeriod           = 14;     \\ninput int    RsiLookbackBars     = 15;     \\ninput int    RsiOversoldLevel    = 35;     \\ninput int    RsiOverboughtLevel  = 65;     \\n\\ninput group \\\"== Microestructura ==\\\"\\ninput double MaxSpreadPips       = 4.0;    \\n\\ninput group \\\"== Gestion ML (Triple Barrera y Riesgo Lineal) ==\\\"\\ninput double InpInitialBalance    = 100000.0; \\ninput double TakeProfitMultiplier = 3.0;   \\n// VerticalBarrierBars es ahora dinamico.\\n\\ninput group \\\"== Filtros Macro / Cisnes Negros ==\\\"\\ninput double InpMaxSignalBarATR  = 2.5;    \\ninput double InpMaxSLATR         = 3.0;    \\n\\n// === Variables Globales ===\\nint g_VerticalBarrierBars;\\nENUM_TIMEFRAMES g_macro_tf;\\n\\nint hma_handle, hma_exit_handle, rsi_handle, atr_handle;\\nint ema50_handle, ema200_handle;\\nint sma20_handle, std_dev_handle;\\nint ema50_h4_handle;  \\nint atr200_handle;    \\n\\nint OnInit()\\n{\\n    trade.SetExpertMagicNumber(777888);\\n\\n    if     (_Period == PERIOD_M15) g_macr\n<truncated 23052 bytes>",
  "IsArtifact": "false",
  "Overwrite": "true",
  "TargetFile": "\"C:\\\\Users\\\\Manuel\\\\Desktop\\\\HMA_MetaLabeling\\\\MQL5_Engine\\\\HMA_ML_Orchestrator.mq5\"",
  "toolAction": "\"Rewriting HMA_ML_Orchestrator.mq5\"",
  "toolSummary": "\"Rewrite Orchestrator\""
}
```

## Step 1840 - Tool Response
```
Created At: 2026-06-01T01:01:20Z
Completed At: 2026-06-01T01:01:20Z
Created file file:///C:/Users/Manuel/Desktop/HMA_MetaLabeling/MQL5_Engine/HMA_ML_Orchestrator.mq5 with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission....
```

## Step 1848 - Tool Response
```diff
@@ -10,9 +10,9 @@
 - `[x]` Create Python dataset verification to check label distributions (MFE vs SL).
 
 ## Phase 5.1: Dataset Expansion & Multi-Node Triggers
-- `[/]` Implement One-Hot Encoding for triggers (`Is_Trigger_Fast`, `Is_Trigger_Slow`, `Is_Trigger_RSI`, `Is_Trigger_Profit`).
-- `[/]` Define dynamic `VerticalBarrierBars = InpHMA_ExitPeriod * 1.5`.
-- `[/]` Comply with Strict MQL5 Rules (No `break`/`continue`/`pass`, No `HistoryPositionGetInteger`, Author: "Manuel").
+- `[x]` Implement One-Hot Encoding for triggers (`Is_Trigger_Fast`, `Is_Trigger_Slow`, `Is_Trigger_RSI`, `Is_Trigger_Profit`).
+- `[x]` Define dynamic `VerticalBarrierBars = InpHMA_ExitPeriod * 1.5`.
+- `[x]` Comply with Strict MQL5 Rules (No `break`/`continue`/`pass`, No `HistoryPositionGetInteger`, Author: "Manuel").
 - `[ ]` Train XGBoost Secondary Model.
 
 - `[x]` Integrate `CExitDataLogger` in `HMA_ML_Orchestrator.mq5`
```

## Step 1861 - Tool Call: write_to_file
**Description:** "Full rewrite of HMA_ML_Orchestrator.mq5 with Virtual Shadow Harvesting (Phase 6): VirtualTrade tracking, hybrid trigger, ManageVirtualShadows, cooldown per direction, strict MQL5 rules, Author: Manuel."

```json
{
  "CodeContent": "\"//+------------------------------------------------------------------+\\n//|                                          HMA_ML_Orchestrator.mq5 |\\n//|        Generador Cuantitativo de Datasets (Meta-Labeling v2.2)   |\\n//|        Autor: Manuel                                             |\\n//|        Fase 6: Virtual Shadow Harvesting \u2014 Hybrid Trigger Engine |\\n//+------------------------------------------------------------------+\\n#property strict\\n#property version \\\"2.2\\\"\\n#property description \\\"HMA Meta-Labeling Dataset Generator - Phase 6\\\"\\n\\n#include <Trade\\\\Trade.mqh>\\n#include \\\"ML_Logger.mqh\\\"\\n#include \\\"HMA_FUNCTIONS.mqh\\\"\\n\\nCTrade         trade;\\nCMLDataLogger  *logger;\\nCExitDataLogger *exit_logger;\\n\\n//+------------------------------------------------------------------+\\n//| Parametros de Entrada                                            |\\n//+------------------------------------------------------------------+\\n\\ninput group \\\"== Estrategia HMA ==\\\"\\ninput int    HMAPeriod           = 50;\\ninput int    InpHMA_ExitPeriod   = 100;\\ninput int    InpMinBarsToHold    = 3;\\ninput int    LookbackBars        = 7;\\ninput double AntiNoiseATRPct     = 2.0;\\n\\ninput group \\\"== Concurrencia Virtual ==\\\"\\ninput int    InpMaxConcurrentTrades = 5;   // Max trades (fisicos + virtuales)\\n\\ninput group \\\"== Contexto y Features ==\\\"\\ninput int    RsiPeriod           = 14;\\ninput int    RsiLookbackBars     = 15;\\ninput int    RsiOversoldLevel    = 35;\\ninput int    RsiOverboughtLevel  = 65;\\n\\ninput group \\\"== Microestructura ==\\\"\\ninput double MaxSpreadPips       = 4.0;\\n\\ninput group \\\"== Gestion ML (Triple Barrera) ==\\\"\\ninput double InpInitialBalance   = 100000.0;\\ninput double TakeProfitMultiplier = 3.0;\\n// VerticalBarrierBars es dinamico: InpHMA_ExitPeriod * 1.5\\n\\ninput group \\\"== Filtros Macro / Cisnes Negros ==\\\"\\ninput double InpMaxSignalBarATR  = 2.5;\\ninput double InpMaxSLATR         = 3.0;\\n\\n//+------------------------------------------------------------------+\\n//| Variables Globales                 \n<truncated 34752 bytes>",
  "Description": "\"Full rewrite of HMA_ML_Orchestrator.mq5 with Virtual Shadow Harvesting (Phase 6): VirtualTrade tracking, hybrid trigger, ManageVirtualShadows, cooldown per direction, strict MQL5 rules, Author: Manuel.\"",
  "IsArtifact": "false",
  "Overwrite": "true",
  "TargetFile": "\"C:\\\\Users\\\\Manuel\\\\Desktop\\\\HMA_MetaLabeling\\\\MQL5_Engine\\\\HMA_ML_Orchestrator.mq5\"",
  "toolAction": "\"Rewriting Orchestrator with Virtual Shadow Engine\"",
  "toolSummary": "\"Rewrite Orchestrator Phase 6\""
}
```

## Step 1862 - Tool Response
```
Created At: 2026-06-03T17:23:35Z
Completed At: 2026-06-03T17:23:35Z
Created file file:///C:/Users/Manuel/Desktop/HMA_MetaLabeling/MQL5_Engine/HMA_ML_Orchestrator.mq5 with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission....
```

## Step 1864 - Tool Response
```diff
@@ -15,6 +15,15 @@
 - `[x]` Comply with Strict MQL5 Rules (No `break`/`continue`/`pass`, No `HistoryPositionGetInteger`, Author: "Manuel").
 - `[ ]` Train XGBoost Secondary Model.
 
+## Phase 6: Virtual Shadow Harvesting
+- `[x]` Define `VirtualTrade` struct in ML_Logger.mqh with feature snapshot + tracking fields.
+- `[x]` Implement `CommitVirtualTrade()` method — same CSV, zero distinction.
+- `[x]` Implement `ManageVirtualShadows()` — per-tick life simulation, MAE/MFE update, SL/barrier exit.
+- `[x]` Implement hybrid trigger: Physical (Dummy) if no open positions, Virtual (Shadow) otherwise.
+- `[x]` Implement `InpMaxConcurrentTrades` concurrency ceiling (physical + virtual).
+- `[x]` Implement cooldown per direction (prohibit same-bar re-entry for same signal type).
+- `[x]` Multi-Node Triggers (One-Hot) preserved and extended to virtual trades.
+
 - `[x]` Integrate `CExitDataLogger` in `HMA_ML_Orchestrator.mq5`
   - `[x]` Initialize and de-initialize `exit_logger`
   - `[x]` Modify `CheckDynamicHMAExit` to generate `ExitSnapshot` instead of closing physically
```

## Step 1870 - Tool Response
```diff
@@ -335,6 +335,12 @@
             if(active_shadows[i].signal_type == 0) close_price_v = bid_now;
             else                                    close_price_v = ask_now;
 
+            // Cachear datos ANTES del ArrayRemove para evitar out-of-range
+            ulong  cached_vid   = active_shadows[i].virtual_id;
+            bool   cached_sl    = sl_hit;
+            bool   cached_tb    = time_barrier_hit;
+            int    cached_bars  = bars_in_trade_v;
+
             logger.CommitVirtualTrade(
                 active_shadows[i],
                 close_price_v,
@@ -341,4 +341,4 @@
-                bars_in_trade_v,
+                cached_bars,
                 g_VerticalBarrierBars,
                 pip);
 
@@ -345,9 +345,9 @@
 
             PrintFormat("[SHADOW CLOSED] VirtualID=%I64u | Bars=%d | SL=%s | TimeBar=%s",
-                        active_shadows[i > 0 ? i-1 : 0].virtual_id,
-                        bars_in_trade_v,
-                        sl_hit ? "SI" : "NO",
-                        time_barrier_hit ? "SI" : "NO");
+                        cached_vid,
+                        cached_bars,
+                        cached_sl ? "SI" : "NO",
+                        cached_tb ? "SI" : "NO");
         }
     }
 }
```

## Step 1933 - Tool Call: write_to_file
**Description:** "HMA_ML_Orchestrator v2.3: Removed all shadow harvesting. Fixed 0.01L for all orders. ManageAllPhysicalPositions() iterates over ALL concurrent positions. No concurrency limit. One-Hot trigger system preserved. Strict MQL5 rules enforced. Author: Manuel."

```json
{
  "CodeContent": "\"//+------------------------------------------------------------------+\\n//|                                          HMA_ML_Orchestrator.mq5 |\\n//|        Generador Cuantitativo de Datasets (Meta-Labeling v2.3)   |\\n//|        Autor: Manuel                                             |\\n//|        Fase 7.5: Multi-Concurrencia 0.01L \u2014 Sin Shadow Harvest  |\\n//|        Todas las posiciones son fisicas. Micro-Pyramiding activo.|\\n//+------------------------------------------------------------------+\\n#property strict\\n#property version \\\"2.3\\\"\\n#property description \\\"HMA Meta-Labeling Dataset Generator - Phase 7.5\\\"\\n\\n#include <Trade\\\\Trade.mqh>\\n#include \\\"ML_Logger.mqh\\\"\\n#include \\\"HMA_FUNCTIONS.mqh\\\"\\n\\nCTrade          trade;\\nCMLDataLogger  *logger;\\nCExitDataLogger *exit_logger;\\n\\n// Volumen fijo inmutable \u2014 protege el balance del simulador\\n// mientras permite inspecci\u00f3n visual de TODAS las se\u00f1ales.\\nstatic const double FIXED_LOT = 0.01;\\n\\n//+------------------------------------------------------------------+\\n//| Parametros de Entrada                                            |\\n//+------------------------------------------------------------------+\\n\\ninput group \\\"== Estrategia HMA ==\\\"\\ninput int    HMAPeriod           = 50;\\ninput int    InpHMA_ExitPeriod   = 100;\\ninput int    InpMinBarsToHold    = 3;\\ninput int    LookbackBars        = 7;\\ninput double AntiNoiseATRPct     = 2.0;\\n\\ninput group \\\"== Contexto y Features ==\\\"\\ninput int    RsiPeriod           = 14;\\ninput int    RsiLookbackBars     = 15;\\ninput int    RsiOversoldLevel    = 35;\\ninput int    RsiOverboughtLevel  = 65;\\n\\ninput group \\\"== Microestructura ==\\\"\\ninput double MaxSpreadPips       = 4.0;\\n\\ninput group \\\"== Gestion ML (Triple Barrera) ==\\\"\\ninput double InpInitialBalance   = 100000.0;\\ninput double TakeProfitMultiplier = 3.0;\\n// VerticalBarrierBars es dinamico: InpHMA_ExitPeriod * 1.5\\n\\ninput group \\\"== Filtros Macro / Cisnes Negros ==\\\"\\ninput double InpMaxSignalBarATR  = 2.5;\\ninput double InpMaxSLATR         = 3.0\n<truncated 26155 bytes>",
  "Description": "\"HMA_ML_Orchestrator v2.3: Removed all shadow harvesting. Fixed 0.01L for all orders. ManageAllPhysicalPositions() iterates over ALL concurrent positions. No concurrency limit. One-Hot trigger system preserved. Strict MQL5 rules enforced. Author: Manuel.\"",
  "IsArtifact": "false",
  "Overwrite": "true",
  "TargetFile": "\"C:\\\\Users\\\\Manuel\\\\Desktop\\\\HMA_MetaLabeling\\\\MQL5_Engine\\\\HMA_ML_Orchestrator.mq5\"",
  "toolAction": "\"Rewriting Orchestrator v2.3 with multi-concurrency\"",
  "toolSummary": "\"Rewrite Orchestrator v2.3\""
}
```

## Step 1934 - Tool Response
```
Created At: 2026-06-03T21:01:56Z
Completed At: 2026-06-03T21:01:56Z
Created file file:///C:/Users/Manuel/Desktop/HMA_MetaLabeling/MQL5_Engine/HMA_ML_Orchestrator.mq5 with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission....
```

## Step 1989 - Tool Call: multi_replace_file_content
**Instruction:** "Insert Phase 8 Liquidity and Microstructure feature calculation before Step 6, and assign them to the snap struct."
**Description:** "Added Phase 8 features to Orchestrator OnTick"

```json
{
  "Description": "\"Added Phase 8 features to Orchestrator OnTick\"",
  "Instruction": "\"Insert Phase 8 Liquidity and Microstructure feature calculation before Step 6, and assign them to the snap struct.\"",
  "ReplacementChunks": "[{\"AllowMultiple\":false,\"EndLine\":555,\"ReplacementContent\":\"    // === PASO 5.5: FASE 8 - MICROESTRUCTURA Y LIQUIDEZ ===\\n    // 1. Asian Range (00:00 - 08:00)\\n    MqlDateTime dt_start = dt;\\n    dt_start.hour = 0; dt_start.min = 0; dt_start.sec = 0;\\n    datetime asian_start = StructToTime(dt_start);\\n    MqlDateTime dt_end = dt_start;\\n    dt_end.hour = 8;\\n    datetime asian_end = StructToTime(dt_end);\\n    \\n    double asian_high = 0.0, asian_low = 0.0;\\n    int bars_asian = iBars(_Symbol, _Period, asian_start, asian_end);\\n    if(bars_asian > 0) {\\n        double ah[], al[];\\n        if(CopyHigh(_Symbol, _Period, asian_start, asian_end, ah) > 0) {\\n            asian_high = ah[0];\\n            int s = ArraySize(ah);\\n            for(int k=1; k<s; k++) { if(ah[k] > asian_high) asian_high = ah[k]; }\\n        }\\n        if(CopyLow(_Symbol, _Period, asian_start, asian_end, al) > 0) {\\n            asian_low = al[0];\\n            int s = ArraySize(al);\\n            for(int k=1; k<s; k++) { if(al[k] < asian_low) asian_low = al[k]; }\\n        }\\n    }\\n    \\n    double dist_asian_high_atr = 0.0;\\n    double dist_asian_low_atr  = 0.0;\\n    if(current_atr > 0 && asian_high > 0 && asian_low > 0) {\\n        dist_asian_high_atr = MathAbs(asian_high - current_close) / current_atr;\\n        dist_asian_low_atr  = MathAbs(current_close - asian_low) / current_atr;\\n    }\\n    \\n    int is_asian_sweep = 0;\\n    if(asian_high > 0 && asian_low > 0) {\\n        for(int k=0; k<=2; k++) {\\n            if(k < rates_copied) {\\n                bool swept_high = (rates[k].high > asian_high) && (rates[k].close <= asian_high) && (rates[k].open <= asian_high);\\n                bool swept_low  = (rates[k].low < asian_low)   && (rates[k].close >= asian_low)  && (rates[k].open >= asian_low);\\n                if(swept_high || swept_low) is_asian_sweep = 1;\\n            }\\n        }\\n    }\\n    \\n    // 2. Tick Volume Z-Score\\n    double tick_vol_zscore = 0.0;\\n    if(rates_copied >= 20) {\\n        double sum_vol = 0;\\n        for(int k=0; k<20\n<truncated 2023 bytes>",
  "TargetFile": "\"C:\\\\Users\\\\Manuel\\\\Desktop\\\\HMA_MetaLabeling\\\\MQL5_Engine\\\\HMA_ML_Orchestrator.mq5\"",
  "toolAction": "\"Adding Phase 8 features to Orchestrator\"",
  "toolSummary": "\"Update Orchestrator Phase 8\""
}
```

## Step 1990 - Tool Response
```diff
@@ -552,6 +552,76 @@
     double spread_impact_ratio = 0.0;
     if(sl_pips > 0) spread_impact_ratio = spread / sl_pips;
 
+    // === PASO 5.5: FASE 8 - MICROESTRUCTURA Y LIQUIDEZ ===
+    // 1. Asian Range (00:00 - 08:00)
+    MqlDateTime dt_start = dt;
+    dt_start.hour = 0; dt_start.min = 0; dt_start.sec = 0;
+    datetime asian_start = StructToTime(dt_start);
+    MqlDateTime dt_end = dt_start;
+    dt_end.hour = 8;
+    datetime asian_end = StructToTime(dt_end);
+    
+    double asian_high = 0.0, asian_low = 0.0;
+    int bars_asian = iBars(_Symbol, _Period, asian_start, asian_end);
+    if(bars_asian > 0) {
+        double ah[], al[];
+        if(CopyHigh(_Symbol, _Period, asian_start, asian_end, ah) > 0) {
+            asian_high = ah[0];
+            int s = ArraySize(ah);
+            for(int k=1; k<s; k++) { if(ah[k] > asian_high) asian_high = ah[k]; }
+        }
+        if(CopyLow(_Symbol, _Period, asian_start, asian_end, al) > 0) {
+            asian_low = al[0];
+            int s = ArraySize(al);
+            for(int k=1; k<s; k++) { if(al[k] < asian_low) asian_low = al[k]; }
+        }
+    }
+    
+    double dist_asian_high_atr = 0.0;
+    double dist_asian_low_atr  = 0.0;
+    if(current_atr > 0 && asian_high > 0 && asian_low > 0) {
+        dist_asian_high_atr = MathAbs(asian_high - current_close) / current_atr;
+        dist_asian_low_atr  = MathAbs(current_close - asian_low) / current_atr;
+    }
+    
+    int is_asian_sweep = 0;
+    if(asian_high > 0 && asian_low > 0) {
+        for(int k=0; k<=2; k++) {
+            if(k < rates_copied) {
+                bool swept_high = (rates[k].high > asian_high) && (rates[k].close <= asian_high) && (rate
<truncated 327 bytes>
+    if(rates_copied >= 20) {
+        double sum_vol = 0;
+        for(int k=0; k<20; k++) sum_vol += (double)rates[k].tick_volume;
+        double mean_vol = sum_vol / 20.0;
+        double sq_diff_sum = 0;
+        for(int k=0; k<20; k++) sq_diff_sum += MathPow((double)rates[k].tick_volume - mean_vol, 2);
+        double std_vol = MathSqrt(sq_diff_sum / 20.0);
+        if(std_vol > 0) tick_vol_zscore = ((double)rates[0].tick_volume - mean_vol) / std_vol;
+    }
+    
+    // 3. Spread Expansion Ratio
+    double spread_exp_ratio = 1.0;
+    int spread_array[];
+    if(CopySpread(_Symbol, _Period, 0, 20, spread_array) >= 20) {
+        ArraySetAsSeries(spread_array, true);
+        double sum_spread = 0;
+        for(int k=0; k<20; k++) sum_spread += (double)spread_array[k];
+        double mean_spread = sum_spread / 20.0;
+        if(mean_spread > 0) spread_exp_ratio = (double)spread_array[0] / mean_spread;
+    }
+    
+    // 4. Candle Dominance
+    double candle_dominance = 0.0;
+    if(candle_range > 0) candle_dominance = candle_body / candle_range;
+
     // === PASO 6: APERTURA A 0.01 LOTES — SIN LIMITE DE CONCURRENCIA ===
     lastBarTime = currentBarTime;  // Bloquear la vela ANTES del OrderSend
 
@@ -612,6 +612,12 @@
         snap.hma_acceleration_raw    = hma_accel_v2;
         snap.hma_jerk                = hma_jerk_val;
         snap.energy_accumulation     = energy_accum;
+        snap.dist_asian_high_atr     = dist_asian_high_atr;
+        snap.dist_asian_low_atr      = dist_asian_low_atr;
+        snap.is_asian_sweep          = is_asian_sweep;
+        snap.tick_volume_zscore      = tick_vol_zscore;
+        snap.spread_expansion_ratio  = spread_exp_ratio;
+        snap.candle_dominance        = candle_dominance;
 
         logger.RecordSignal(snap);
```

## Step 2008 - Tool Response
```diff
@@ -562,7 +562,7 @@
     datetime asian_end = StructToTime(dt_end);
     
     double asian_high = 0.0, asian_low = 0.0;
-    int bars_asian = iBars(_Symbol, _Period, asian_start, asian_end);
+    int bars_asian = Bars(_Symbol, _Period, asian_start, asian_end);
     if(bars_asian > 0) {
         double ah[], al[];
         if(CopyHigh(_Symbol, _Period, asian_start, asian_end, ah) > 0) {
```

## Step 2046 - Tool Response
```diff
@@ -393,21 +393,104 @@
         current_atr, atr_sma50, spread,
         currentBarTime);
 
-    // === PASO 2: DETECCION DE CRUCE HMA ===
-    bool crossUp = false;
-    if(rates[1].close < hma[1]) {
-        if(rates[0].close > hma[0]) crossUp = true;
-    }
-    bool crossDn = false;
-    if(rates[1].close > hma[1]) {
-        if(rates[0].close < hma[0]) crossDn = true;
-    }
-
-    bool has_cross = false;
-    if(crossUp) has_cross = true;
-    if(crossDn) has_cross = true;
-
-    if(!has_cross) {
+    // === PASO 2: DETECCION DE GATILLO ESTRUCTURAL (FASE 9) ===
+    MqlDateTime dt;
+    TimeToStruct(currentBarTime, dt);
+
+    // 1. Asian Range (00:00 - 08:00)
+    MqlDateTime dt_start = dt;
+    dt_start.hour = 0; dt_start.min = 0; dt_start.sec = 0;
+    datetime asian_start = StructToTime(dt_start);
+    MqlDateTime dt_end = dt_start;
+    dt_end.hour = 8;
+    datetime asian_end = StructToTime(dt_end);
+    
+    double asian_high = 0.0, asian_low = 0.0;
+    int bars_asian = Bars(_Symbol, _Period, asian_start, asian_end);
+    if(bars_asian > 0) {
+        double ah[], al[];
+        if(CopyHigh(_Symbol, _Period, asian_start, asian_end, ah) > 0) {
+            asian_high = ah[0];
+            int s = ArraySize(ah);
+            for(int k=1; k<s; k++) { if(ah[k] > asian_high) asian_high = ah[k]; }
+        }
+        if(CopyLow(_Symbol, _Period, asian_start, asian_end, al) > 0) {
+            asian_low = al[0];
+            int s = ArraySize(al);
+            for(int k=1; k<s; k++) { if(al[k] < asian_low) asian_low = al[k]; }
+        }
+    }
+    
+    double current_close = rates[0].close;
+    double dist_asian_high_atr = 0.0;
+    double dist_asian_low_atr  = 0.0;
<truncated 1060 bytes>
 sum_vol = 0;
+        for(int k=0; k<20; k++) sum_vol += (double)rates[k].tick_volume;
+        double mean_vol = sum_vol / 20.0;
+        double sq_diff_sum = 0;
+        for(int k=0; k<20; k++) sq_diff_sum += MathPow((double)rates[k].tick_volume - mean_vol, 2);
+        double std_vol = MathSqrt(sq_diff_sum / 20.0);
+        if(std_vol > 0) tick_vol_zscore = ((double)rates[0].tick_volume - mean_vol) / std_vol;
+    }
+    
+    // 3. Spread Expansion Ratio
+    double spread_exp_ratio = 1.0;
+    int spread_array[];
+    if(CopySpread(_Symbol, _Period, 0, 20, spread_array) >= 20) {
+        ArraySetAsSeries(spread_array, true);
+        double sum_spread = 0;
+        for(int k=0; k<20; k++) sum_spread += (double)spread_array[k];
+        double mean_spread = sum_spread / 20.0;
+        if(mean_spread > 0) spread_exp_ratio = (double)spread_array[0] / mean_spread;
+    }
+    
+    // 4. Candle Dominance
+    double candle_body  = MathAbs(rates[0].open - rates[0].close);
+    double candle_range = rates[0].high - rates[0].low;
+    double candle_dominance = 0.0;
+    if(candle_range > 0) candle_dominance = candle_body / candle_range;
+
+    bool is_bullish = (rates[0].close > rates[0].open);
+    bool is_bearish = (rates[0].close < rates[0].open);
+
+    bool triggerBUY = false;
+    if(is_asian_sweep_low || (tick_vol_zscore > 2.0 && is_bullish && candle_dominance > 0.7)) {
+        triggerBUY = true;
+    }
+
+    bool triggerSELL = false;
+    if(is_asian_sweep_high || (tick_vol_zscore > 2.0 && is_bearish && candle_dominance > 0.7)) {
+        triggerSELL = true;
+    }
+
+    bool has_trigger = false;
+    if(triggerBUY) has_trigger = true;
+    if(triggerSELL) has_trigger = true;
+
+    if(!has_trigger) {
         lastBarTime = currentBarTime;
         return;
     }
```

## Step 2049 - Tool Response
```diff
@@ -515,8 +515,8 @@
     }
 
     // === PASO 4: TIPO DE SEÑAL Y SL ESTRUCTURAL ===
-    int signalType = 1;        // 1=SELL por defecto (crossDn)
-    if(crossUp) signalType = 0; // 0=BUY
+    int signalType = 1;        // 1=SELL por defecto
+    if(triggerBUY) signalType = 0; // 0=BUY
 
     double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
     double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
```

## Step 2051 - Tool Call: multi_replace_file_content
**Instruction:** "Remove current_close, dt, candle_body redefinitions and delete Paso 5.5 block"
**Description:** "Cleaned up duplicate variables and old Paso 5.5"

```json
{
  "Description": "\"Cleaned up duplicate variables and old Paso 5.5\"",
  "Instruction": "\"Remove current_close, dt, candle_body redefinitions and delete Paso 5.5 block\"",
  "ReplacementChunks": "[{\"AllowMultiple\":false,\"EndLine\":458,\"ReplacementContent\":\"    // === PASO 5: CALCULO DE FEATURES ===\\n    // double current_close already defined in Paso 2\",\"StartLine\":456,\"TargetContent\":\"    // === PASO 5: CALCULO DE FEATURES ===\\n    double current_close = rates[0].close;\"},{\"AllowMultiple\":false,\"EndLine\":487,\"ReplacementContent\":\"    // dt ya declarado en Paso 2\\n    TimeToStruct(TimeCurrent(), dt);\",\"StartLine\":486,\"TargetContent\":\"    MqlDateTime dt;\\n    TimeToStruct(TimeCurrent(), dt);\"},{\"AllowMultiple\":false,\"EndLine\":520,\"ReplacementContent\":\"    // candle_body y candle_range ya declarados en Paso 2\\n    double breakout_body_ratio = 0.0;\\n    if(candle_range > 0) breakout_body_ratio = candle_body / candle_range;\",\"StartLine\":517,\"TargetContent\":\"    double candle_body  = MathAbs(rates[0].open - rates[0].close);\\n    double candle_range = rates[0].high - rates[0].low;\\n    double breakout_body_ratio = 0.0;\\n    if(candle_range > 0) breakout_body_ratio = candle_body / candle_range;\"},{\"AllowMultiple\":false,\"EndLine\":624,\"ReplacementContent\":\"\",\"StartLine\":555,\"TargetContent\":\"    // === PASO 5.5: FASE 8 - MICROESTRUCTURA Y LIQUIDEZ ===\\n    // 1. Asian Range (00:00 - 08:00)\\n    MqlDateTime dt_start = dt;\\n    dt_start.hour = 0; dt_start.min = 0; dt_start.sec = 0;\\n    datetime asian_start = StructToTime(dt_start);\\n    MqlDateTime dt_end = dt_start;\\n    dt_end.hour = 8;\\n    datetime asian_end = StructToTime(dt_end);\\n    \\n    double asian_high = 0.0, asian_low = 0.0;\\n    int bars_asian = Bars(_Symbol, _Period, asian_start, asian_end);\\n    if(bars_asian > 0) {\\n        double ah[], al[];\\n        if(CopyHigh(_Symbol, _Period, asian_start, asian_end, ah) > 0) {\\n            asian_high = ah[0];\\n            int s = ArraySize(ah);\\n            for(int k=1; k<s; k++) { if(ah[k] > asian_high) asian_high = ah[k]; }\\n        }\\n        if(CopyLow(_Symbol, _Period, asian_start, asian_end, al) > 0) {\\n            asian_low = al[0];\\n            int s = ArraySize(al);\\n            for(int k=1; k<s; k++) {\n<truncated 2038 bytes>",
  "TargetFile": "\"C:\\\\Users\\\\Manuel\\\\Desktop\\\\HMA_MetaLabeling\\\\MQL5_Engine\\\\HMA_ML_Orchestrator.mq5\"",
  "toolAction": "\"Cleaning up old variables\"",
  "toolSummary": "\"Cleanup Paso 5\""
}
```

## Step 2052 - Tool Response
```diff
@@ -537,7 +537,7 @@
     if(sl_dist_atr > InpMaxSLATR) { lastBarTime = currentBarTime; return; }
 
     // === PASO 5: CALCULO DE FEATURES ===
-    double current_close = rates[0].close;
+    // double current_close already defined in Paso 2
 
     double z_score = 0.0;
     if(stddev[0] > 0) z_score = (current_close - sma20[0]) / stddev[0];
@@ -565,7 +565,7 @@
     double pb_depth    = 0.0;
     CalcPullbackMetrics(hma_handle, LookbackBars, current_atr, pb_duration, pb_depth);
 
-    MqlDateTime dt;
+    // dt ya declarado en Paso 2
     TimeToStruct(TimeCurrent(), dt);
     int h = dt.hour;
     int session_time = 1;
@@ -595,8 +595,7 @@
     double hma_distance_ema = 0.0;
     if(pip > 0) hma_distance_ema = (current_close - es[0]) / pip;
 
-    double candle_body  = MathAbs(rates[0].open - rates[0].close);
-    double candle_range = rates[0].high - rates[0].low;
+    // candle_body y candle_range ya declarados en Paso 2
     double breakout_body_ratio = 0.0;
     if(candle_range > 0) breakout_body_ratio = candle_body / candle_range;
 
@@ -632,75 +632,6 @@
     double spread_impact_ratio = 0.0;
     if(sl_pips > 0) spread_impact_ratio = spread / sl_pips;
 
-    // === PASO 5.5: FASE 8 - MICROESTRUCTURA Y LIQUIDEZ ===
-    // 1. Asian Range (00:00 - 08:00)
-    MqlDateTime dt_start = dt;
-    dt_start.hour = 0; dt_start.min = 0; dt_start.sec = 0;
-    datetime asian_start = StructToTime(dt_start);
-    MqlDateTime dt_end = dt_start;
-    dt_end.hour = 8;
-    datetime asian_end = StructToTime(dt_end);
-    
-    double asian_high = 0.0, asian_low = 0.0;
-    int bars_asian = Bars(_Symbol, _Period, asian_start, asian_end);
-    if(bars_asian > 0) {
-        double ah[], al
<truncated 804 bytes>
    int is_asian_sweep = 0;
-    if(asian_high > 0 && asian_low > 0) {
-        for(int k=0; k<=2; k++) {
-            if(k < rates_copied) {
-                bool swept_high = (rates[k].high > asian_high) && (rates[k].close <= asian_high) && (rates[k].open <= asian_high);
-                bool swept_low  = (rates[k].low < asian_low)   && (rates[k].close >= asian_low)  && (rates[k].open >= asian_low);
-                if(swept_high || swept_low) is_asian_sweep = 1;
-            }
-        }
-    }
-    
-    // 2. Tick Volume Z-Score
-    double tick_vol_zscore = 0.0;
-    if(rates_copied >= 20) {
-        double sum_vol = 0;
-        for(int k=0; k<20; k++) sum_vol += (double)rates[k].tick_volume;
-        double mean_vol = sum_vol / 20.0;
-        double sq_diff_sum = 0;
-        for(int k=0; k<20; k++) sq_diff_sum += MathPow((double)rates[k].tick_volume - mean_vol, 2);
-        double std_vol = MathSqrt(sq_diff_sum / 20.0);
-        if(std_vol > 0) tick_vol_zscore = ((double)rates[0].tick_volume - mean_vol) / std_vol;
-    }
-    
-    // 3. Spread Expansion Ratio
-    double spread_exp_ratio = 1.0;
-    int spread_array[];
-    if(CopySpread(_Symbol, _Period, 0, 20, spread_array) >= 20) {
-        ArraySetAsSeries(spread_array, true);
-        double sum_spread = 0;
-        for(int k=0; k<20; k++) sum_spread += (double)spread_array[k];
-        double mean_spread = sum_spread / 20.0;
-        if(mean_spread > 0) spread_exp_ratio = (double)spread_array[0] / mean_spread;
-    }
-    
-    // 4. Candle Dominance
-    double candle_dominance = 0.0;
-    if(candle_range > 0) candle_dominance = candle_body / candle_range;
 
     // === PASO 6: APERTURA A 0.01 LOTES — SIN LIMITE DE CONCURRENCIA ===
     lastBarTime = currentBarTime;  // Bloquear la vela ANTES del OrderSend
```

## Step 2064 - Tool Response
```diff
@@ -82,7 +82,7 @@
     PrintFormat("[INIT] Lote fijo: %.2f | Barrier: %d velas | Micro-Pyramiding: ACTIVO",
                 FIXED_LOT, g_VerticalBarrierBars);
 
-    string filename = "HMA_Dataset_" + _Symbol + ".csv";
+    string filename = "Struct_Dataset_" + _Symbol + ".csv";
     logger      = new CMLDataLogger(filename);
     exit_logger = new CExitDataLogger(_Symbol);
```

## Step 2155 - Tool Call: multi_replace_file_content
**Instruction:** "Add Donchian input parameter, declare and initialize adx_handle"
**Description:** "Added Donchian input and ADX handle in top section"

```json
{
  "Description": "\"Added Donchian input and ADX handle in top section\"",
  "Instruction": "\"Add Donchian input parameter, declare and initialize adx_handle\"",
  "ReplacementChunks": "[{\"AllowMultiple\":false,\"EndLine\":43,\"ReplacementContent\":\"input group \\\"== Microestructura ==\\\"\\ninput double MaxSpreadPips       = 4.0;\\ninput int    InpDonchianPeriod   = 20;\",\"StartLine\":41,\"TargetContent\":\"input group \\\"== Microestructura ==\\\"\\ninput double MaxSpreadPips       = 4.0;\"},{\"AllowMultiple\":false,\"EndLine\":64,\"ReplacementContent\":\"int ema50_h4_handle;\\nint atr200_handle;\\nint adx_handle;\",\"StartLine\":63,\"TargetContent\":\"int ema50_h4_handle;\\nint atr200_handle;\"},{\"AllowMultiple\":false,\"EndLine\":98,\"ReplacementContent\":\"    ema50_h4_handle = iMA(_Symbol, PERIOD_H4, 50, 0, MODE_EMA, PRICE_CLOSE);\\n    atr200_handle   = iATR(_Symbol, _Period, 200);\\n    adx_handle      = iADX(_Symbol, PERIOD_D1, 14);\",\"StartLine\":97,\"TargetContent\":\"    ema50_h4_handle = iMA(_Symbol, PERIOD_H4, 50, 0, MODE_EMA, PRICE_CLOSE);\\n    atr200_handle   = iATR(_Symbol, _Period, 200);\"},{\"AllowMultiple\":false,\"EndLine\":106,\"ReplacementContent\":\"       std_dev_handle  == INVALID_HANDLE ||\\n       ema50_h4_handle == INVALID_HANDLE ||\\n       atr200_handle   == INVALID_HANDLE ||\\n       adx_handle      == INVALID_HANDLE)\",\"StartLine\":104,\"TargetContent\":\"       std_dev_handle  == INVALID_HANDLE ||\\n       ema50_h4_handle == INVALID_HANDLE ||\\n       atr200_handle   == INVALID_HANDLE)\"},{\"AllowMultiple\":false,\"EndLine\":130,\"ReplacementContent\":\"    IndicatorRelease(sma20_handle);\\n    IndicatorRelease(std_dev_handle);\\n    IndicatorRelease(adx_handle);\",\"StartLine\":129,\"TargetContent\":\"    IndicatorRelease(sma20_handle);\\n    IndicatorRelease(std_dev_handle);\"}]",
  "TargetFile": "\"C:\\\\Users\\\\Manuel\\\\Desktop\\\\HMA_MetaLabeling\\\\MQL5_Engine\\\\HMA_ML_Orchestrator.mq5\"",
  "toolAction": "\"Adding ADX and Donchian variables\"",
  "toolSummary": "\"Add variables top section\""
}
```

## Step 2156 - Tool Response
```diff
@@ -40,6 +40,7 @@
 
 input group "== Microestructura =="
 input double MaxSpreadPips       = 4.0;
+input int    InpDonchianPeriod   = 20;
 
 input group "== Gestion ML (Triple Barrera) =="
 input double InpInitialBalance   = 100000.0;
@@ -61,6 +61,7 @@
 int sma20_handle, std_dev_handle;
 int ema50_h4_handle;
 int atr200_handle;
+int adx_handle;
 
 //+------------------------------------------------------------------+
 //| OnInit                                                           |
@@ -94,6 +94,7 @@
     std_dev_handle  = iStdDev(_Symbol, _Period, 20, 0, MODE_SMA, PRICE_CLOSE);
     ema50_h4_handle = iMA(_Symbol, PERIOD_H4, 50, 0, MODE_EMA, PRICE_CLOSE);
     atr200_handle   = iATR(_Symbol, _Period, 200);
+    adx_handle      = iADX(_Symbol, PERIOD_D1, 14);
 
     if(hma_handle      == INVALID_HANDLE ||
        hma_exit_handle == INVALID_HANDLE ||
@@ -100,7 +100,8 @@
        atr_handle      == INVALID_HANDLE ||
        std_dev_handle  == INVALID_HANDLE ||
        ema50_h4_handle == INVALID_HANDLE ||
-       atr200_handle   == INVALID_HANDLE)
+       atr200_handle   == INVALID_HANDLE ||
+       adx_handle      == INVALID_HANDLE)
     {
         Print("ERROR CRITICO: Indicadores no inicializados.");
         return(INIT_FAILED);
@@ -124,6 +124,7 @@
     IndicatorRelease(ema200_handle);
     IndicatorRelease(sma20_handle);
     IndicatorRelease(std_dev_handle);
+    IndicatorRelease(adx_handle);
     IndicatorRelease(ema50_h4_handle);
     IndicatorRelease(atr200_handle);
 }
```

## Step 2161 - Tool Call: multi_replace_file_content
**Instruction:** "Update Paso 2 logic to handle Donchian channel, ADX, and relaxed triggers"
**Description:** "Added Donchian logic, ADX retrieval, and hybrid triggers"

```json
{
  "Description": "\"Added Donchian logic, ADX retrieval, and hybrid triggers\"",
  "Instruction": "\"Update Paso 2 logic to handle Donchian channel, ADX, and relaxed triggers\"",
  "ReplacementChunks": "[{\"AllowMultiple\":false,\"EndLine\":381,\"ReplacementContent\":\"    int macro_shift = iBarShift(_Symbol, g_macro_tf, currentBarTime);\\n    int h4_shift    = iBarShift(_Symbol, PERIOD_H4,  currentBarTime);\\n    int d1_shift    = iBarShift(_Symbol, PERIOD_D1,  currentBarTime);\\n    if(CopyBuffer(ema50_handle,    0, macro_shift + 1, 1, ef)       < 1) return;\\n    if(CopyBuffer(ema200_handle,   0, macro_shift + 1, 1, es)       < 1) return;\\n    if(CopyBuffer(ema50_h4_handle, 0, h4_shift    + 1, 2, ema50_h4) < 2) return;\\n    \\n    double adx_buf[];\\n    if(CopyBuffer(adx_handle, 0, d1_shift + 1, 1, adx_buf) < 1) return;\\n    double macro_adx = adx_buf[0];\",\"StartLine\":377,\"TargetContent\":\"    int macro_shift = iBarShift(_Symbol, g_macro_tf, currentBarTime);\\n    int h4_shift    = iBarShift(_Symbol, PERIOD_H4,  currentBarTime);\\n    if(CopyBuffer(ema50_handle,    0, macro_shift + 1, 1, ef)       < 1) return;\\n    if(CopyBuffer(ema200_handle,   0, macro_shift + 1, 1, es)       < 1) return;\\n    if(CopyBuffer(ema50_h4_handle, 0, h4_shift    + 1, 2, ema50_h4) < 2) return;\"},{\"AllowMultiple\":false,\"EndLine\":450,\"ReplacementContent\":\"    if(is_asian_sweep_high || is_asian_sweep_low) is_asian_sweep = 1;\\n\\n    // 1.5 Donchian Local Sweep (Multi-Session)\\n    double local_high = rates[1].high;\\n    double local_low  = rates[1].low;\\n    int max_dc = MathMin(rates_copied, InpDonchianPeriod + 1);\\n    for(int k=2; k<max_dc; k++) {\\n        if(rates[k].high > local_high) local_high = rates[k].high;\\n        if(rates[k].low < local_low)   local_low  = rates[k].low;\\n    }\\n    \\n    bool is_local_sweep_high = (rates[0].high > local_high) && (rates[0].close <= local_high) && (rates[0].open <= local_high);\\n    bool is_local_sweep_low  = (rates[0].low < local_low)   && (rates[0].close >= local_low)  && (rates[0].open >= local_low);\",\"StartLine\":450,\"TargetContent\":\"    if(is_asian_sweep_high || is_asian_sweep_low) is_asian_sweep = 1;\"},{\"AllowMultiple\":false,\"EndLine\":492,\"ReplacementContent\":\"    // Hybrid HMA Cross Logic\\n    bool h\n<truncated 1216 bytes>",
  "TargetFile": "\"C:\\\\Users\\\\Manuel\\\\Desktop\\\\HMA_MetaLabeling\\\\MQL5_Engine\\\\HMA_ML_Orchestrator.mq5\"",
  "toolAction": "\"Updating Paso 2 triggers\"",
  "toolSummary": "\"Update Paso 2 logic\""
}
```

## Step 2162 - Tool Response
```diff
@@ -376,9 +376,14 @@
 
     int macro_shift = iBarShift(_Symbol, g_macro_tf, currentBarTime);
     int h4_shift    = iBarShift(_Symbol, PERIOD_H4,  currentBarTime);
+    int d1_shift    = iBarShift(_Symbol, PERIOD_D1,  currentBarTime);
     if(CopyBuffer(ema50_handle,    0, macro_shift + 1, 1, ef)       < 1) return;
     if(CopyBuffer(ema200_handle,   0, macro_shift + 1, 1, es)       < 1) return;
     if(CopyBuffer(ema50_h4_handle, 0, h4_shift    + 1, 2, ema50_h4) < 2) return;
+    
+    double adx_buf[];
+    if(CopyBuffer(adx_handle, 0, d1_shift + 1, 1, adx_buf) < 1) return;
+    double macro_adx = adx_buf[0];
 
     // === METRICAS COMUNES ===
     double pip        = GetPip();
@@ -448,6 +448,18 @@
     }
     if(is_asian_sweep_high || is_asian_sweep_low) is_asian_sweep = 1;
 
+    // 1.5 Donchian Local Sweep (Multi-Session)
+    double local_high = rates[1].high;
+    double local_low  = rates[1].low;
+    int max_dc = MathMin(rates_copied, InpDonchianPeriod + 1);
+    for(int k=2; k<max_dc; k++) {
+        if(rates[k].high > local_high) local_high = rates[k].high;
+        if(rates[k].low < local_low)   local_low  = rates[k].low;
+    }
+    
+    bool is_local_sweep_high = (rates[0].high > local_high) && (rates[0].close <= local_high) && (rates[0].open <= local_high);
+    bool is_local_sweep_low  = (rates[0].low < local_low)   && (rates[0].close >= local_low)  && (rates[0].open >= local_low);
+
     // 2. Tick Volume Z-Score
     double tick_vol_zscore = 0.0;
     if(rates_copied >= 20) {
@@ -479,8 +479,20 @@
     bool is_bullish = (rates[0].close > rates[0].open);
     bool is_bearish = (rates[0].close < rates[0].open);
 
+    // Hybrid HMA Cross Logic
+    bool hma_cross_up = (rates[1].close < hma[1] && rates[0].close > hma[0]);
+    bool hma_cross_dn = (rates[1].close > hma[1] && rates[0].close < hma[0]);
+    bool is_macro_bull = (ef[0] > es[0]);
+    bool is_macro_bear = (ef[0] < es[0]);
+
+    bool valid_hma_buy  = hma_cross_up && (macro_adx > 25) && is_macro_bull;
+    bool valid_hma_sell = hma_cross_dn && (macro_adx > 25) && is_macro_bear;
+
+    bool is_vol_shock_bull = (tick_vol_zscore > 0.75 && is_bullish);
+    bool is_vol_shock_bear = (tick_vol_zscore > 0.75 && is_bearish);
+
     bool triggerBUY = false;
-    if(is_asian_sweep_low || (tick_vol_zscore > 2.0 && is_bullish && candle_dominance > 0.7)) {
+    if(is_asian_sweep_low || is_local_sweep_low || is_vol_shock_bull || valid_hma_buy) {
         triggerBUY = true;
     }
 
@@ -487,4 +487,4 @@
-    if(is_asian_sweep_high || (tick_vol_zscore > 2.0 && is_bearish && candle_dominance > 0.7)) {
+    if(is_asian_sweep_high || is_local_sweep_high || is_vol_shock_bear || valid_hma_sell) {
         triggerSELL = true;
     }
```

## Step 2612 - Tool Call: multi_replace_file_content
**Instruction:** "Update ManageAllPhysicalPositions signature to accept close_1 and implement hard close logic. Update the function call in OnTick."
**Description:** "Added Hard Close logic to ManageAllPhysicalPositions in HMA_ML_Orchestrator.mq5."

```json
{
  "Description": "\"Added Hard Close logic to ManageAllPhysicalPositions in HMA_ML_Orchestrator.mq5.\"",
  "Instruction": "\"Update ManageAllPhysicalPositions signature to accept close_1 and implement hard close logic. Update the function call in OnTick.\"",
  "ReplacementChunks": "[{\"AllowMultiple\":false,\"EndLine\":276,\"ReplacementContent\":\"void ManageAllPhysicalPositions(\\n    double hma_exit_1, double hma_exit_2, double hma_exit_3,\\n    double fast_hma_1, double fast_hma_2, double fast_hma_3,\\n    double rsi_1, double rsi_2,\\n    double current_atr, double atr_sma50, double spread,\\n    datetime currentBarTime, double close_1)\",\"StartLine\":271,\"TargetContent\":\"void ManageAllPhysicalPositions(\\n    double hma_exit_1, double hma_exit_2, double hma_exit_3,\\n    double fast_hma_1, double fast_hma_2, double fast_hma_3,\\n    double rsi_1, double rsi_2,\\n    double current_atr, double atr_sma50, double spread,\\n    datetime currentBarTime)\"},{\"AllowMultiple\":false,\"EndLine\":329,\"ReplacementContent\":\"                // HARD CLOSE: Invalidador f\u00edsico innegociable\\n                bool hard_close = false;\\n                if(pos_type == POSITION_TYPE_BUY && close_1 < fast_hma_1) hard_close = true;\\n                if(pos_type == POSITION_TYPE_SELL && close_1 > fast_hma_1) hard_close = true;\\n                \\n                if(hard_close) {\\n                    trade.PositionClose(ticket);\\n                    PrintFormat(\\\"[HARD EXIT] FISICA ESTRUCTURAL ROTA. ABORTANDO. Ticket: %I64u\\\", ticket);\\n                } else {\\n                    // Disparo de dilema de salida (One-Hot, sin cierre fisico)\\n                    CheckAndFireExitDilemma(\\n                        ticket, pos_type, open_p, sl_p, open_t,\\n                        hma_exit_1, hma_exit_2, hma_exit_3,\\n                        fast_hma_1, fast_hma_2, fast_hma_3,\\n                        rsi_1, rsi_2,\\n                        current_atr, atr_sma50, spread,\\n                        mfe_price);\\n\\n                    // Barrera Temporal: cierra si supera el limite de barras\\n                    int open_bar    = iBarShift(_Symbol, _Period, open_t);\\n                    int current_bar = iBarShift(_Symbol, _Period, currentBarTime);\\n                    if((open_bar - current_bar) >= g_VerticalBarrierBars) {\\n                       \n<truncated 1832 bytes>",
  "TargetFile": "\"c:\\\\Users\\\\Manuel\\\\Desktop\\\\HMA_MetaLabeling\\\\MQL5_Engine\\\\HMA_ML_Orchestrator.mq5\"",
  "toolAction": "\"Adding Hard Close to Orchestrator\"",
  "toolSummary": "\"Editing HMA_ML_Orchestrator.mq5\""
}
```

## Step 2613 - Tool Response
```diff
@@ -273,7 +273,7 @@
     double fast_hma_1, double fast_hma_2, double fast_hma_3,
     double rsi_1, double rsi_2,
     double current_atr, double atr_sma50, double spread,
-    datetime currentBarTime)
+    datetime currentBarTime, double close_1)
 {
     int total = PositionsTotal();
     for(int i = total - 1; i >= 0; i--)
@@ -308,22 +308,32 @@
                 if(pos_type == POSITION_TYPE_BUY)  mfe_price = max_high - open_p;
                 if(pos_type == POSITION_TYPE_SELL) mfe_price = open_p   - min_low;
 
-                // Disparo de dilema de salida (One-Hot, sin cierre fisico)
-                CheckAndFireExitDilemma(
-                    ticket, pos_type, open_p, sl_p, open_t,
-                    hma_exit_1, hma_exit_2, hma_exit_3,
-                    fast_hma_1, fast_hma_2, fast_hma_3,
-                    rsi_1, rsi_2,
-                    current_atr, atr_sma50, spread,
-                    mfe_price);
-
-                // Barrera Temporal: cierra si supera el limite de barras
-                int open_bar    = iBarShift(_Symbol, _Period, open_t);
-                int current_bar = iBarShift(_Symbol, _Period, currentBarTime);
-                if((open_bar - current_bar) >= g_VerticalBarrierBars) {
+                // HARD CLOSE: Invalidador físico innegociable
+                bool hard_close = false;
+                if(pos_type == POSITION_TYPE_BUY && close_1 < fast_hma_1) hard_close = true;
+                if(pos_type == POSITION_TYPE_SELL && close_1 > fast_hma_1) hard_close = true;
+                
+                if(hard_close) {
                     trade.PositionClose(ticket);
-                    PrintFormat("[BARRIER] Ticket=%I64u cerrado por barrera temporal (%d barras)",
-                                ticket, (open_bar - current_bar));
+                    PrintFormat("[HARD EXIT] FISICA ESTRUCTURAL ROTA. ABORTANDO. Ticket: %I64u", ticket);
+                } else {
+                    // Disparo de dilema de salida (One-Hot, sin cierre fisico)
+                    CheckAndFireExitDilemma(
+                        ticket, pos_type, open_p, sl_p, open_t,
+                        hma_exit_1, hma_exit_2, hma_exit_3,
+                        fast_hma_1, fast_hma_2, fast_hma_3,
+                        rsi_1, rsi_2,
+                        current_atr, atr_sma50, spread,
+                        mfe_price);
+
+                    // Barrera Temporal: cierra si supera el limite de barras
+                    int open_bar    = iBarShift(_Symbol, _Period, open_t);
+                    int current_bar = iBarShift(_Symbol, _Period, currentBarTime);
+                    if((open_bar - current_bar) >= g_VerticalBarrierBars) {
+                        trade.PositionClose(ticket);
+                        PrintFormat("[BARRIER] Ticket=%I64u cerrado por barrera temporal (%d barras)",
+                                    ticket, (open_bar - current_bar));
+                    }
                 }
             }
         }
@@ -399,7 +399,7 @@
         hma[0], hma[1], hma[2],
         rsi_buf[0], rsi_buf[1],
         current_atr, atr_sma50, spread,
-        currentBarTime);
+        currentBarTime, rates[0].close);
 
     // === PASO 2: DETECCION DE GATILLO ESTRUCTURAL (FASE 9) ===
     MqlDateTime dt;
```

## Step 2615 - Tool Call: multi_replace_file_content
**Instruction:** "Replace the trigger detection section in HMA_ML_Orchestrator.mq5 with the Lookback Window architecture and Shift 1 validation."
**Description:** "Implemented Lookback Window tracking and asynchronous trigger coupling in HMA_ML_Orchestrator.mq5."

```json
{
  "Description": "\"Implemented Lookback Window tracking and asynchronous trigger coupling in HMA_ML_Orchestrator.mq5.\"",
  "Instruction": "\"Replace the trigger detection section in HMA_ML_Orchestrator.mq5 with the Lookback Window architecture and Shift 1 validation.\"",
  "ReplacementChunks": "[{\"AllowMultiple\":false,\"EndLine\":407,\"ReplacementContent\":\"    // === PASO 2: DETECCION DE GATILLOS EN SHIFT 1 (Cero Repintado) ===\\n    // RASTREADORES ESTRUCTURALES EST\u00c1TICOS\\n    static int bars_since_asian_sweep_high = 999;\\n    static int bars_since_asian_sweep_low  = 999;\\n    static int bars_since_local_sweep_high = 999;\\n    static int bars_since_local_sweep_low  = 999;\\n    static int bars_since_vol_shock_bull   = 999;\\n    static int bars_since_vol_shock_bear   = 999;\\n\\n    bars_since_asian_sweep_high++;\\n    bars_since_asian_sweep_low++;\\n    bars_since_local_sweep_high++;\\n    bars_since_local_sweep_low++;\\n    bars_since_vol_shock_bull++;\\n    bars_since_vol_shock_bear++;\\n\\n    MqlDateTime dt;\\n    TimeToStruct(currentBarTime, dt);\",\"StartLine\":406,\"TargetContent\":\"    // === PASO 2: DETECCION DE GATILLO ESTRUCTURAL (FASE 9) ===\\n    MqlDateTime dt;\\n    TimeToStruct(currentBarTime, dt);\"},{\"AllowMultiple\":false,\"EndLine\":499,\"ReplacementContent\":\"    double current_close = rates[1].close; // Shift 1 para el dataset!\\n    double dist_asian_high_atr = 0.0;\\n    double dist_asian_low_atr  = 0.0;\\n    if(current_atr > 0 && asian_high > 0 && asian_low > 0) {\\n        dist_asian_high_atr = MathAbs(asian_high - current_close) / current_atr;\\n        dist_asian_low_atr  = MathAbs(current_close - asian_low) / current_atr;\\n    }\\n    \\n    int is_asian_sweep = 0;\\n    if(asian_high > 0 && asian_low > 0) {\\n        bool swept_asian_high = (rates[1].high > asian_high) && (rates[1].close <= asian_high) && (rates[1].open <= asian_high);\\n        bool swept_asian_low  = (rates[1].low < asian_low)   && (rates[1].close >= asian_low)  && (rates[1].open >= asian_low);\\n        if(swept_asian_high) bars_since_asian_sweep_high = 0;\\n        if(swept_asian_low)  bars_since_asian_sweep_low  = 0;\\n        if(swept_asian_high && swept_asian_low) is_asian_sweep = 3;\\n        else if(swept_asian_high) is_asian_sweep = 1;\\n        else if(swept_asian_low)  is_asian_sweep = -1;\\n    }\\n\\n    double local_high = rates[2].hi\n<truncated 6375 bytes>",
  "TargetFile": "\"c:\\\\Users\\\\Manuel\\\\Desktop\\\\HMA_MetaLabeling\\\\MQL5_Engine\\\\HMA_ML_Orchestrator.mq5\"",
  "toolAction": "\"Implementing Lookback logic in Orchestrator\"",
  "toolSummary": "\"Editing HMA_ML_Orchestrator.mq5\""
}
```

## Step 2616 - Tool Response
```diff
@@ -413,7 +413,22 @@
         current_atr, atr_sma50, spread,
         currentBarTime, rates[0].close);
 
-    // === PASO 2: DETECCION DE GATILLO ESTRUCTURAL (FASE 9) ===
+    // === PASO 2: DETECCION DE GATILLOS EN SHIFT 1 (Cero Repintado) ===
+    // RASTREADORES ESTRUCTURALES ESTÁTICOS
+    static int bars_since_asian_sweep_high = 999;
+    static int bars_since_asian_sweep_low  = 999;
+    static int bars_since_local_sweep_high = 999;
+    static int bars_since_local_sweep_low  = 999;
+    static int bars_since_vol_shock_bull   = 999;
+    static int bars_since_vol_shock_bear   = 999;
+
+    bars_since_asian_sweep_high++;
+    bars_since_asian_sweep_low++;
+    bars_since_local_sweep_high++;
+    bars_since_local_sweep_low++;
+    bars_since_vol_shock_bull++;
+    bars_since_vol_shock_bear++;
+
     MqlDateTime dt;
     TimeToStruct(currentBarTime, dt);
 
@@ -439,8 +439,7 @@
             for(int k=1; k<s; k++) { if(al[k] < asian_low) asian_low = al[k]; }
         }
     }
-    
-    double current_close = rates[0].close;
+        double current_close = rates[1].close; // Shift 1 para el dataset!
     double dist_asian_high_atr = 0.0;
     double dist_asian_low_atr  = 0.0;
     if(current_atr > 0 && asian_high > 0 && asian_low > 0) {
@@ -447,26 +447,21 @@
         dist_asian_low_atr  = MathAbs(current_close - asian_low) / current_atr;
     }
     
-    bool is_asian_sweep_high = false;
-    bool is_asian_sweep_low  = false;
     int is_asian_sweep = 0;
     if(asian_high > 0 && asian_low > 0) {
-        for(int k=0; k<=2; k++) {
-            if(k < rates_copied) {
-                bool swept_high = (rates[k].high > asian_high) && (rates[k].close <= asian_high) && (ra
<truncated 4235 bytes>
 is_bearish = (rates[1].close < rates[1].open);
+    if(tick_vol_zscore > 0.75 && is_bullish) bars_since_vol_shock_bull = 0;
+    if(tick_vol_zscore > 0.75 && is_bearish) bars_since_vol_shock_bear = 0;
+
+    // ACOPLAMIENTO ASÍNCRONO EN BARRAS CERRADAS (Shift 2 y Shift 1)
+    bool hma_cross_up = (rates[2].close < hma[2] && rates[1].close > hma[1]);
+    bool hma_cross_dn = (rates[2].close > hma[2] && rates[1].close < hma[1]);
     bool is_macro_bull = (ef[0] > es[0]);
     bool is_macro_bear = (ef[0] < es[0]);
 
@@ -514,21 +514,21 @@
     bool valid_hma_sell = hma_cross_dn && (macro_adx > 25) && is_macro_bear;
 
-    bool is_vol_shock_bull = (tick_vol_zscore > 0.75 && is_bullish);
-    bool is_vol_shock_bear = (tick_vol_zscore > 0.75 && is_bearish);
-
     bool triggerBUY = false;
-    if(is_asian_sweep_low || is_local_sweep_low || is_vol_shock_bull || valid_hma_buy) {
-        triggerBUY = true;
+    if(valid_hma_buy) {
+        if(bars_since_asian_sweep_low <= 4 || bars_since_local_sweep_low <= 4 || bars_since_vol_shock_bull <= 4) {
+            triggerBUY = true;
+        }
     }
 
     bool triggerSELL = false;
-    if(is_asian_sweep_high || is_local_sweep_high || is_vol_shock_bear || valid_hma_sell) {
-        triggerSELL = true;
+    if(valid_hma_sell) {
+        if(bars_since_asian_sweep_high <= 4 || bars_since_local_sweep_high <= 4 || bars_since_vol_shock_bear <= 4) {
+            triggerSELL = true;
+        }
     }
 
     bool has_trigger = false;
-    if(triggerBUY) has_trigger = true;
-    if(triggerSELL) has_trigger = true;
+    if(triggerBUY || triggerSELL) has_trigger = true;
 
     if(!has_trigger) {
         lastBarTime = currentBarTime;
```

## Step 2721 - Tool Call: multi_replace_file_content
**Instruction:** "Add InpConsistencyBars to inputs, and use the new helper functions for signal validation in OnTick."
**Description:** "Added InpConsistencyBars input and implemented Consistency/RSI Memory logic in HMA_ML_Orchestrator.mq5."

```json
{
  "Description": "\"Added InpConsistencyBars input and implemented Consistency/RSI Memory logic in HMA_ML_Orchestrator.mq5.\"",
  "Instruction": "\"Add InpConsistencyBars to inputs, and use the new helper functions for signal validation in OnTick.\"",
  "ReplacementChunks": "[{\"AllowMultiple\":false,\"EndLine\":43,\"ReplacementContent\":\"input group \\\"== Microestructura ==\\\"\\ninput int    InpConsistencyBars  = 7;\\ninput double MaxSpreadPips       = 4.0;\",\"StartLine\":41,\"TargetContent\":\"input group \\\"== Microestructura ==\\\"\\ninput double MaxSpreadPips       = 4.0;\"},{\"AllowMultiple\":false,\"EndLine\":489,\"ReplacementContent\":\"    // ACOPLAMIENTO AS\u00cdNCRONO EN BARRAS CERRADAS (Shift 2 y Shift 1)\\n    bool hma_cross_up = (rates[2].close < hma[2] && rates[1].close > hma[1]);\\n    bool hma_cross_dn = (rates[2].close > hma[2] && rates[1].close < hma[1]);\\n    bool is_macro_bull = (ef[0] > es[0]);\\n    bool is_macro_bear = (ef[0] < es[0]);\\n\\n    // Validaci\u00f3n Geom\u00e9trica (Consistencia de Inmersi\u00f3n)\\n    bool is_consistent_buy  = IsConsistentlyBelowHMA(rates, hma, 3, InpConsistencyBars);\\n    bool is_consistent_sell = IsConsistentlyAboveHMA(rates, hma, 3, InpConsistencyBars);\\n\\n    // Validaci\u00f3n de Memoria Estructural (Agotamiento RSI)\\n    bool rsi_oversold   = WasRSIOversold(rsi_buf, 1, RsiLookbackBars, (double)RsiOversoldLevel);\\n    bool rsi_overbought = WasRSIOverbought(rsi_buf, 1, RsiLookbackBars, (double)RsiOverboughtLevel);\\n\\n    bool valid_hma_buy  = hma_cross_up && is_consistent_buy && rsi_oversold && (macro_adx > 25) && is_macro_bull;\\n    bool valid_hma_sell = hma_cross_dn && is_consistent_sell && rsi_overbought && (macro_adx > 25) && is_macro_bear;\",\"StartLine\":481,\"TargetContent\":\"    // ACOPLAMIENTO AS\u00cdNCRONO EN BARRAS CERRADAS (Shift 2 y Shift 1)\\n    bool hma_cross_up = (rates[2].close < hma[2] && rates[1].close > hma[1]);\\n    bool hma_cross_dn = (rates[2].close > hma[2] && rates[1].close < hma[1]);\\n    bool is_macro_bull = (ef[0] > es[0]);\\n    bool is_macro_bear = (ef[0] < es[0]);\\n\\n    bool valid_hma_buy  = hma_cross_up && (macro_adx > 25) && is_macro_bull;\\n    bool valid_hma_sell = hma_cross_dn && (macro_adx > 25) && is_macro_bear;\"}]",
  "TargetFile": "\"c:\\\\Users\\\\Manuel\\\\Desktop\\\\HMA_MetaLabeling\\\\MQL5_Engine\\\\HMA_ML_Orchestrator.mq5\"",
  "toolAction": "\"Adding inputs and logic to Orchestrator\"",
  "toolSummary": "\"Editing HMA_ML_Orchestrator.mq5\""
}
```

## Step 2722 - Tool Response
```diff
@@ -39,6 +39,7 @@
 input int    RsiOverboughtLevel  = 65;
 
 input group "== Microestructura =="
+input int    InpConsistencyBars  = 7;
 input double MaxSpreadPips       = 4.0;
 input int    InpDonchianPeriod   = 20;
 
@@ -514,8 +514,16 @@
     bool is_macro_bull = (ef[0] > es[0]);
     bool is_macro_bear = (ef[0] < es[0]);
 
-    bool valid_hma_buy  = hma_cross_up && (macro_adx > 25) && is_macro_bull;
-    bool valid_hma_sell = hma_cross_dn && (macro_adx > 25) && is_macro_bear;
+    // Validación Geométrica (Consistencia de Inmersión)
+    bool is_consistent_buy  = IsConsistentlyBelowHMA(rates, hma, 3, InpConsistencyBars);
+    bool is_consistent_sell = IsConsistentlyAboveHMA(rates, hma, 3, InpConsistencyBars);
+
+    // Validación de Memoria Estructural (Agotamiento RSI)
+    bool rsi_oversold   = WasRSIOversold(rsi_buf, 1, RsiLookbackBars, (double)RsiOversoldLevel);
+    bool rsi_overbought = WasRSIOverbought(rsi_buf, 1, RsiLookbackBars, (double)RsiOverboughtLevel);
+
+    bool valid_hma_buy  = hma_cross_up && is_consistent_buy && rsi_oversold && (macro_adx > 25) && is_macro_bull;
+    bool valid_hma_sell = hma_cross_dn && is_consistent_sell && rsi_overbought && (macro_adx > 25) && is_macro_bear;
 
     bool triggerBUY = false;
     if(valid_hma_buy) {
```

## Step 2780 - Tool Call: multi_replace_file_content
**Instruction:** "Remove strict conditions from valid_hma_buy/sell and map them to snap fields."
**Description:** "Transitioned Consistency and RSI rules to Soft Features in Orchestrator."

```json
{
  "Description": "\"Transitioned Consistency and RSI rules to Soft Features in Orchestrator.\"",
  "Instruction": "\"Remove strict conditions from valid_hma_buy/sell and map them to snap fields.\"",
  "ReplacementChunks": "[{\"AllowMultiple\":false,\"EndLine\":525,\"ReplacementContent\":\"    bool rsi_oversold   = WasRSIOversold(rsi_buf, 1, RsiLookbackBars, (double)RsiOversoldLevel);\\n    bool rsi_overbought = WasRSIOverbought(rsi_buf, 1, RsiLookbackBars, (double)RsiOverboughtLevel);\\n\\n    bool valid_hma_buy  = hma_cross_up && (macro_adx > 25) && is_macro_bull;\\n    bool valid_hma_sell = hma_cross_dn && (macro_adx > 25) && is_macro_bear;\",\"StartLine\":520,\"TargetContent\":\"    bool rsi_oversold   = WasRSIOversold(rsi_buf, 1, RsiLookbackBars, (double)RsiOversoldLevel);\\n    bool rsi_overbought = WasRSIOverbought(rsi_buf, 1, RsiLookbackBars, (double)RsiOverboughtLevel);\\n\\n    bool valid_hma_buy  = hma_cross_up && is_consistent_buy && rsi_oversold && (macro_adx > 25) && is_macro_bull;\\n    bool valid_hma_sell = hma_cross_dn && is_consistent_sell && rsi_overbought && (macro_adx > 25) && is_macro_bear;\"},{\"AllowMultiple\":false,\"EndLine\":745,\"ReplacementContent\":\"        snap.breakout_force_atr  = breakout_force;\\n        snap.regime_consistent   = (signalType == 0) ? (int)is_consistent_buy : (int)is_consistent_sell;\\n        snap.rsi_exhausted       = (signalType == 0) ? (int)rsi_oversold : (int)rsi_overbought;\",\"StartLine\":744,\"TargetContent\":\"        snap.breakout_force_atr  = breakout_force;\"}]",
  "TargetFile": "\"c:\\\\Users\\\\Manuel\\\\Desktop\\\\HMA_MetaLabeling\\\\MQL5_Engine\\\\HMA_ML_Orchestrator.mq5\"",
  "toolAction": "\"Transitioning to Soft Features in Orchestrator\"",
  "toolSummary": "\"Editing HMA_ML_Orchestrator.mq5\""
}
```

## Step 2781 - Tool Response
```diff
@@ -524,8 +524,8 @@
     bool rsi_oversold   = WasRSIOversold(rsi_buf, 1, RsiLookbackBars, (double)RsiOversoldLevel);
     bool rsi_overbought = WasRSIOverbought(rsi_buf, 1, RsiLookbackBars, (double)RsiOverboughtLevel);
 
-    bool valid_hma_buy  = hma_cross_up && is_consistent_buy && rsi_oversold && (macro_adx > 25) && is_macro_bull;
-    bool valid_hma_sell = hma_cross_dn && is_consistent_sell && rsi_overbought && (macro_adx > 25) && is_macro_bear;
+    bool valid_hma_buy  = hma_cross_up && (macro_adx > 25) && is_macro_bull;
+    bool valid_hma_sell = hma_cross_dn && (macro_adx > 25) && is_macro_bear;
 
     bool triggerBUY = false;
     if(valid_hma_buy) {
@@ -727,6 +727,8 @@
         snap.hma_slope_pct       = hma_slope;
         snap.hma_acceleration    = hma_accel_feat;
         snap.breakout_force_atr  = breakout_force;
+        snap.regime_consistent   = (signalType == 0) ? (int)is_consistent_buy : (int)is_consistent_sell;
+        snap.rsi_exhausted       = (signalType == 0) ? (int)rsi_oversold : (int)rsi_overbought;
         snap.trend_alignment     = trend_align;
         snap.dist_to_macro_ema   = dist_macro;
         snap.pullback_duration   = pb_duration;
```

## Step 2816 - Tool Call: multi_replace_file_content
**Instruction:** "Remove InpConsistencyBars input, use dynamic count, and update struct mapping."
**Description:** "Updated HMA_ML_Orchestrator to use CountConsistentlyBelowHMA and CountConsistentlyAboveHMA instead of boolean functions."

```json
{
  "Description": "\"Updated HMA_ML_Orchestrator to use CountConsistentlyBelowHMA and CountConsistentlyAboveHMA instead of boolean functions.\"",
  "Instruction": "\"Remove InpConsistencyBars input, use dynamic count, and update struct mapping.\"",
  "ReplacementChunks": "[{\"AllowMultiple\":false,\"EndLine\":45,\"ReplacementContent\":\"input group \\\"== Microestructura ==\\\"\\ninput double MaxSpreadPips       = 4.0;\\ninput int    InpDonchianPeriod   = 20;\",\"StartLine\":42,\"TargetContent\":\"input group \\\"== Microestructura ==\\\"\\ninput int    InpConsistencyBars  = 7;\\ninput double MaxSpreadPips       = 4.0;\\ninput int    InpDonchianPeriod   = 20;\"},{\"AllowMultiple\":false,\"EndLine\":520,\"ReplacementContent\":\"    // Validaci\u00f3n Geom\u00e9trica (Consistencia de Inmersi\u00f3n Num\u00e9rica)\\n    int count_consistent_buy  = CountConsistentlyBelowHMA(rates, hma, 3);\\n    int count_consistent_sell = CountConsistentlyAboveHMA(rates, hma, 3);\",\"StartLine\":517,\"TargetContent\":\"    // Validaci\u00f3n Geom\u00e9trica (Consistencia de Inmersi\u00f3n)\\n    bool is_consistent_buy  = IsConsistentlyBelowHMA(rates, hma, 3, InpConsistencyBars);\\n    bool is_consistent_sell = IsConsistentlyAboveHMA(rates, hma, 3, InpConsistencyBars);\"},{\"AllowMultiple\":false,\"EndLine\":730,\"ReplacementContent\":\"        snap.regime_consistency_count = (signalType == 0) ? count_consistent_buy : count_consistent_sell;\\n        snap.rsi_exhausted            = (signalType == 0) ? (int)rsi_oversold : (int)rsi_overbought;\",\"StartLine\":729,\"TargetContent\":\"        snap.regime_consistent   = (signalType == 0) ? (int)is_consistent_buy : (int)is_consistent_sell;\\n        snap.rsi_exhausted       = (signalType == 0) ? (int)rsi_oversold : (int)rsi_overbought;\"}]",
  "TargetFile": "\"c:\\\\Users\\\\Manuel\\\\Desktop\\\\HMA_MetaLabeling\\\\MQL5_Engine\\\\HMA_ML_Orchestrator.mq5\"",
  "toolAction": "\"Updating dynamic count in Orchestrator\"",
  "toolSummary": "\"Editing HMA_ML_Orchestrator.mq5\""
}
```

## Step 2817 - Tool Response
```diff
@@ -39,7 +39,6 @@
 input int    RsiOverboughtLevel  = 65;
 
 input group "== Microestructura =="
-input int    InpConsistencyBars  = 7;
 input double MaxSpreadPips       = 4.0;
 input int    InpDonchianPeriod   = 20;
 
@@ -515,9 +515,9 @@
     bool is_macro_bull = (ef[0] > es[0]);
     bool is_macro_bear = (ef[0] < es[0]);
 
-    // Validación Geométrica (Consistencia de Inmersión)
-    bool is_consistent_buy  = IsConsistentlyBelowHMA(rates, hma, 3, InpConsistencyBars);
-    bool is_consistent_sell = IsConsistentlyAboveHMA(rates, hma, 3, InpConsistencyBars);
+    // Validación Geométrica (Consistencia de Inmersión Numérica)
+    int count_consistent_buy  = CountConsistentlyBelowHMA(rates, hma, 3);
+    int count_consistent_sell = CountConsistentlyAboveHMA(rates, hma, 3);
 
     // Validación de Memoria Estructural (Agotamiento RSI)
     bool rsi_oversold   = WasRSIOversold(rsi_buf, 1, RsiLookbackBars, (double)RsiOversoldLevel);
@@ -726,8 +726,8 @@
         snap.hma_slope_pct       = hma_slope;
         snap.hma_acceleration    = hma_accel_feat;
         snap.breakout_force_atr  = breakout_force;
-        snap.regime_consistent   = (signalType == 0) ? (int)is_consistent_buy : (int)is_consistent_sell;
-        snap.rsi_exhausted       = (signalType == 0) ? (int)rsi_oversold : (int)rsi_overbought;
+        snap.regime_consistency_count = (signalType == 0) ? count_consistent_buy : count_consistent_sell;
+        snap.rsi_exhausted            = (signalType == 0) ? (int)rsi_oversold : (int)rsi_overbought;
         snap.trend_alignment     = trend_align;
         snap.dist_to_macro_ema   = dist_macro;
         snap.pullback_duration   = pb_duration;
```

## Step 2887 - Tool Call: multi_replace_file_content
**Instruction:** "1. Decouple entry filters. 2. Pass macro_adx to ManageAllPhysicalPositions. 3. Update ExitSnapshot fields."
**Description:** "Updated HMA_ML_Orchestrator.mq5 entry filters and exit snapshot mapping for Phase 10.7."

```json
{
  "Description": "\"Updated HMA_ML_Orchestrator.mq5 entry filters and exit snapshot mapping for Phase 10.7.\"",
  "Instruction": "\"1. Decouple entry filters. 2. Pass macro_adx to ManageAllPhysicalPositions. 3. Update ExitSnapshot fields.\"",
  "ReplacementChunks": "[{\"AllowMultiple\":false,\"EndLine\":141,\"ReplacementContent\":\"void CheckAndFireExitDilemma(ulong ticket_id, ENUM_POSITION_TYPE pos_type, int bars_in_trade,\\n                             double open_price, double risk, double historical_mfe_price,\\n                             double hma_exit_1, double hma_exit_2, double hma_exit_3,\\n                             double fast_hma_1, double fast_hma_2, double fast_hma_3,\\n                             double rsi_1, double rsi_2,\\n                             double current_atr, double atr_sma50, double spread,\\n                             double macro_adx)\\n{\",\"StartLine\":135,\"TargetContent\":\"void CheckAndFireExitDilemma(ulong ticket_id, ENUM_POSITION_TYPE pos_type, int bars_in_trade,\\n                             double open_price, double risk, double historical_mfe_price,\\n                             double hma_exit_1, double hma_exit_2, double hma_exit_3,\\n                             double fast_hma_1, double fast_hma_2, double fast_hma_3,\\n                             double rsi_1, double rsi_2,\\n                             double current_atr, double atr_sma50, double spread)\\n{\"},{\"AllowMultiple\":false,\"EndLine\":244,\"ReplacementContent\":\"    snap.ticket               = ticket_id;\\n    snap.signal_type          = pos_type;\\n    snap.exit_signal_time     = TimeCurrent();\\n    snap.bars_in_trade        = bars_in_trade;\\n    snap.open_profit_r        = floating_rr;\\n    snap.drawdown_from_peak_r = dd_from_peak_r;\\n    snap.macro_adx_exit       = macro_adx;\\n    snap.exit_hma_velocity    = hma_vel;\",\"StartLine\":238,\"TargetContent\":\"    snap.ticket               = ticket_id;\\n    snap.signal_type          = pos_type;\\n    snap.exit_signal_time     = TimeCurrent();\\n    snap.bars_in_trade        = bars_in_trade;\\n    snap.floating_rr          = floating_rr;\\n    snap.drawdown_from_peak_r = dd_from_peak_r;\\n    snap.exit_hma_velocity    = hma_vel;\"},{\"AllowMultiple\":false,\"EndLine\":278,\"ReplacementContent\":\"    double fast_hma_1, double fast_hma_2, double fast_hma_3,\\n\n<truncated 4832 bytes>",
  "TargetFile": "\"c:\\\\Users\\\\Manuel\\\\Desktop\\\\HMA_MetaLabeling\\\\MQL5_Engine\\\\HMA_ML_Orchestrator.mq5\"",
  "toolAction": "\"Applying Phase 10.7 changes to Orchestrator\"",
  "toolSummary": "\"Editing HMA_ML_Orchestrator.mq5\""
}
```

## Step 2888 - Tool Response
```diff
@@ -153,23 +153,17 @@
 //| Parametros de posicion pasados explicitamente para soportar      |
 //| N posiciones concurrentes en el loop de gestion.                |
 //+------------------------------------------------------------------+
-void CheckAndFireExitDilemma(
-    ulong    ticket_id,
-    long     pos_type,
-    double   open_price,
-    double   sl_price,
-    datetime open_time,
-    double   hma_exit_1, double hma_exit_2, double hma_exit_3,
-    double   fast_hma_1, double fast_hma_2, double fast_hma_3,
-    double   rsi_1, double rsi_2,
-    double   current_atr, double atr_sma50, double spread,
-    double   historical_mfe_price)
+void CheckAndFireExitDilemma(ulong ticket_id, ENUM_POSITION_TYPE pos_type, int bars_in_trade,
+                             double open_price, double risk, double historical_mfe_price,
+                             double hma_exit_1, double hma_exit_2, double hma_exit_3,
+                             double fast_hma_1, double fast_hma_2, double fast_hma_3,
+                             double rsi_1, double rsi_2,
+                             double current_atr, double atr_sma50, double spread,
+                             double macro_adx)
 {
     double pip  = GetPip();
-    double risk = MathAbs(open_price - sl_price);
 
     // Barrera minima de barras — no evaluar si el trade acaba de abrir
-    int bars_in_trade = iBarShift(_Symbol, _Period, open_time);
     if(bars_in_trade < InpMinBarsToHold) return;
 
     // Precio actual segun direccion
@@ -238,8 +238,9 @@
     snap.signal_type          = pos_type;
     snap.exit_signal_time     = TimeCurrent();
     snap.bars_in_trade        = bars_in_trade;
-    snap.floating_rr     
<truncated 2315 bytes>
O 2: DETECCION DE GATILLOS EN SHIFT 1 (Cero Repintado) ===
     // RASTREADORES ESTRUCTURALES ESTÁTICOS
@@ -517,12 +517,12 @@
     bool rsi_oversold   = WasRSIOversold(rsi_buf, 1, RsiLookbackBars, (double)RsiOversoldLevel);
     bool rsi_overbought = WasRSIOverbought(rsi_buf, 1, RsiLookbackBars, (double)RsiOverboughtLevel);
 
-    bool valid_hma_buy  = hma_cross_up && (macro_adx > 25) && is_macro_bull;
-    bool valid_hma_sell = hma_cross_dn && (macro_adx > 25) && is_macro_bear;
+    bool valid_hma_buy  = hma_cross_up;
+    bool valid_hma_sell = hma_cross_dn;
 
     bool triggerBUY = false;
     if(valid_hma_buy) {
-        if(bars_since_asian_sweep_low <= 4 || bars_since_local_sweep_low <= 4 || bars_since_vol_shock_bull <= 4) {
+        if(bars_since_asian_sweep_low <= 8 || bars_since_local_sweep_low <= 8 || bars_since_vol_shock_bull <= 8) {
             triggerBUY = true;
         }
     }
@@ -529,6 +529,6 @@
     bool triggerSELL = false;
     if(valid_hma_sell) {
-        if(bars_since_asian_sweep_high <= 4 || bars_since_local_sweep_high <= 4 || bars_since_vol_shock_bear <= 4) {
+        if(bars_since_asian_sweep_high <= 8 || bars_since_local_sweep_high <= 8 || bars_since_vol_shock_bear <= 8) {
             triggerSELL = true;
         }
     }
@@ -723,6 +723,7 @@
         snap.rsi_exhausted            = (signalType == 0) ? (int)rsi_oversold : (int)rsi_overbought;
         snap.trend_alignment     = trend_align;
         snap.dist_to_macro_ema   = dist_macro;
+        snap.macro_adx           = macro_adx;
         snap.pullback_duration   = pb_duration;
         snap.pullback_max_depth_pct = pb_depth;
         snap.sl_distance_atr     = real_sl_dist_atr;
```

## Step 3422 - Tool Call: multi_replace_file_content
**Instruction:** "Change '52' to '60' in CopyRates and CopyBuffer for the main arrays."
**Description:** "Fixing array out of bounds crash by increasing buffer sizes from 52 to 60."

```json
{
  "Description": "\"Fixing array out of bounds crash by increasing buffer sizes from 52 to 60.\"",
  "Instruction": "\"Change '52' to '60' in CopyRates and CopyBuffer for the main arrays.\"",
  "ReplacementChunks": "[{\"AllowMultiple\":false,\"EndLine\":284,\"ReplacementContent\":\"    int rates_copied    = CopyRates(_Symbol, _Period, 1, 60, rates);\\n    if(rates_copied < 4) return;\\n    int hma_copied      = CopyBuffer(hma_handle,      0, 1, 60, hma);\\n    if(hma_copied < 4)   return;\",\"StartLine\":281,\"TargetContent\":\"    int rates_copied    = CopyRates(_Symbol, _Period, 1, 52, rates);\\n    if(rates_copied < 4) return;\\n    int hma_copied      = CopyBuffer(hma_handle,      0, 1, 52, hma);\\n    if(hma_copied < 4)   return;\"}]",
  "TargetFile": "\"C:\\\\Users\\\\Manuel\\\\Desktop\\\\HMA_MetaLabeling\\\\MQL5_Engine\\\\HMA_ML_Orchestrator.mq5\"",
  "toolAction": "\"Updating bounds in Orchestrator\"",
  "toolSummary": "\"Editing HMA_ML_Orchestrator.mq5\""
}
```

## Step 3423 - Tool Response
```diff
@@ -367,9 +367,9 @@
     ArraySetAsSeries(atr200_buf,   true);
     ArraySetAsSeries(rates,        true);
 
-    int rates_copied    = CopyRates(_Symbol, _Period, 1, 52, rates);
+    int rates_copied    = CopyRates(_Symbol, _Period, 1, 60, rates);
     if(rates_copied < 4) return;
-    int hma_copied      = CopyBuffer(hma_handle,      0, 1, 52, hma);
+    int hma_copied      = CopyBuffer(hma_handle,      0, 1, 60, hma);
     if(hma_copied < 4)   return;
     int hma_exit_copied = CopyBuffer(hma_exit_handle, 0, 1, 3, hma_exit_buf);
     if(hma_exit_copied < 3) return;
```

## Step 3855 - Tool Call: multi_replace_file_content
**Instruction:** "Update CopyRates, CopyBuffer calls to use start_pos = 0. Remove +1 from macro shifts. Update trigger variables."
**Description:** "Fixing shifts in CopyRates, CopyBuffer, and triggers in HMA_ML_Orchestrator.mq5"

```json
{
  "Description": "\"Fixing shifts in CopyRates, CopyBuffer, and triggers in HMA_ML_Orchestrator.mq5\"",
  "Instruction": "\"Update CopyRates, CopyBuffer calls to use start_pos = 0. Remove +1 from macro shifts. Update trigger variables.\"",
  "ReplacementChunks": "[{\"AllowMultiple\":false,\"EndLine\":392,\"ReplacementContent\":\"    int rates_copied    = CopyRates(_Symbol, _Period, 0, 60, rates);\\n    if(rates_copied < 4) return;\\n    int hma_copied      = CopyBuffer(hma_handle,      0, 0, 60, hma);\\n    if(hma_copied < 4)   return;\\n    int hma_exit_copied = CopyBuffer(hma_exit_handle, 0, 0, 3, hma_exit_buf);\\n    if(hma_exit_copied < 3) return;\\n    if(CopyBuffer(rsi_handle,     0, 0, RsiLookbackBars + 1, rsi_buf) < RsiLookbackBars + 1) return;\\n    if(CopyBuffer(atr_handle,     0, 0, 51, atr_buf)  < 51) return;\\n    if(CopyBuffer(atr200_handle,  0, 0, 1,  atr200_buf) < 1) return;\\n    if(CopyBuffer(sma20_handle,   0, 0, 1,  sma20)    < 1)  return;\\n    if(CopyBuffer(std_dev_handle, 0, 0, 1,  stddev)   < 1)  return;\\n\\n    int macro_shift = iBarShift(_Symbol, g_macro_tf, currentBarTime);\\n    int h4_shift    = iBarShift(_Symbol, PERIOD_H4,  currentBarTime);\\n    int d1_shift    = iBarShift(_Symbol, PERIOD_D1,  currentBarTime);\\n    if(CopyBuffer(ema50_handle,    0, macro_shift, 1, ef)       < 1) return;\\n    if(CopyBuffer(ema200_handle,   0, macro_shift, 1, es)       < 1) return;\\n    if(CopyBuffer(ema50_h4_handle, 0, h4_shift, 2, ema50_h4) < 2) return;\\n    \\n    double adx_buf[];\\n    if(CopyBuffer(adx_handle, 0, d1_shift, 1, adx_buf) < 1) return;\",\"StartLine\":370,\"TargetContent\":\"    int rates_copied    = CopyRates(_Symbol, _Period, 1, 60, rates);\\n    if(rates_copied < 4) return;\\n    int hma_copied      = CopyBuffer(hma_handle,      0, 1, 60, hma);\\n    if(hma_copied < 4)   return;\\n    int hma_exit_copied = CopyBuffer(hma_exit_handle, 0, 1, 3, hma_exit_buf);\\n    if(hma_exit_copied < 3) return;\\n    if(CopyBuffer(rsi_handle,     0, 1, RsiLookbackBars + 1, rsi_buf) < RsiLookbackBars + 1) return;\\n    if(CopyBuffer(atr_handle,     0, 1, 51, atr_buf)  < 51) return;\\n    if(CopyBuffer(atr200_handle,  0, 1, 1,  atr200_buf) < 1) return;\\n    if(CopyBuffer(sma20_handle,   0, 1, 1,  sma20)    < 1)  return;\\n    if(CopyBuffer(std_dev_handle, 0, 1, 1,  stddev)   < 1)  return;\\n\\n \n<truncated 2977 bytes>",
  "TargetFile": "\"C:\\\\Users\\\\Manuel\\\\Desktop\\\\HMA_MetaLabeling\\\\MQL5_Engine\\\\HMA_ML_Orchestrator.mq5\"",
  "toolAction": "\"Applying Oboe Hotfix to Orchestrator\"",
  "toolSummary": "\"Editing HMA_ML_Orchestrator.mq5\""
}
```

## Step 3856 - Tool Response
```diff
@@ -367,17 +367,17 @@
     ArraySetAsSeries(atr200_buf,   true);
     ArraySetAsSeries(rates,        true);
 
-    int rates_copied    = CopyRates(_Symbol, _Period, 1, 60, rates);
+    int rates_copied    = CopyRates(_Symbol, _Period, 0, 60, rates);
     if(rates_copied < 4) return;
-    int hma_copied      = CopyBuffer(hma_handle,      0, 1, 60, hma);
+    int hma_copied      = CopyBuffer(hma_handle,      0, 0, 60, hma);
     if(hma_copied < 4)   return;
-    int hma_exit_copied = CopyBuffer(hma_exit_handle, 0, 1, 3, hma_exit_buf);
+    int hma_exit_copied = CopyBuffer(hma_exit_handle, 0, 0, 3, hma_exit_buf);
     if(hma_exit_copied < 3) return;
-    if(CopyBuffer(rsi_handle,     0, 1, RsiLookbackBars + 1, rsi_buf) < RsiLookbackBars + 1) return;
-    if(CopyBuffer(atr_handle,     0, 1, 51, atr_buf)  < 51) return;
-    if(CopyBuffer(atr200_handle,  0, 1, 1,  atr200_buf) < 1) return;
-    if(CopyBuffer(sma20_handle,   0, 1, 1,  sma20)    < 1)  return;
-    if(CopyBuffer(std_dev_handle, 0, 1, 1,  stddev)   < 1)  return;
+    if(CopyBuffer(rsi_handle,     0, 0, RsiLookbackBars + 1, rsi_buf) < RsiLookbackBars + 1) return;
+    if(CopyBuffer(atr_handle,     0, 0, 51, atr_buf)  < 51) return;
+    if(CopyBuffer(atr200_handle,  0, 0, 1,  atr200_buf) < 1) return;
+    if(CopyBuffer(sma20_handle,   0, 0, 1,  sma20)    < 1)  return;
+    if(CopyBuffer(std_dev_handle, 0, 0, 1,  stddev)   < 1)  return;
 
     int macro_shift = iBarShift(_Symbol, g_macro_tf, currentBarTime);
     int h4_shift    = iBarShift(_Symbol, PERIOD_H4,  currentBarTime);
@@ -384,9 +384,9 @@
-    if(CopyBuffer(ema50_handle,    0, macro_shift + 1, 1, ef)       < 1) return;
-    if(CopyBuffer(ema200_handle,   0, ma
<truncated 476 bytes>
dx_handle, 0, d1_shift, 1, adx_buf) < 1) return;
     double macro_adx = adx_buf[0];
 
     // === METRICAS COMUNES ===
@@ -519,23 +519,10 @@
     bool valid_hma_buy  = hma_cross_up;
     bool valid_hma_sell = hma_cross_dn;
 
-    bool triggerBUY = false;
-    if(valid_hma_buy) {
-        if(bars_since_asian_sweep_low <= 8 || bars_since_local_sweep_low <= 8 || bars_since_vol_shock_bull <= 8) {
-            triggerBUY = true;
-        }
-    }
-
-    bool triggerSELL = false;
-    if(valid_hma_sell) {
-        if(bars_since_asian_sweep_high <= 8 || bars_since_local_sweep_high <= 8 || bars_since_vol_shock_bear <= 8) {
-            triggerSELL = true;
-        }
-    }
-
-    bool has_trigger = false;
-    if(triggerBUY || triggerSELL) has_trigger = true;
-
+    bool triggerBUY = valid_hma_buy;
+    bool triggerSELL = valid_hma_sell;
+
+    bool has_trigger = (triggerBUY || triggerSELL);
     if(!has_trigger) {
         lastBarTime = currentBarTime;
         return;
@@ -744,6 +744,9 @@
         snap.hma_acceleration_raw    = hma_accel_v2;
         snap.hma_jerk                = hma_jerk_val;
         snap.energy_accumulation     = energy_accum;
+        snap.bars_since_asian_sweep  = (signalType == 0) ? bars_since_asian_sweep_low : bars_since_asian_sweep_high;
+        snap.bars_since_local_sweep  = (signalType == 0) ? bars_since_local_sweep_low : bars_since_local_sweep_high;
+        snap.bars_since_vol_shock    = (signalType == 0) ? bars_since_vol_shock_bull : bars_since_vol_shock_bear;
         snap.dist_asian_high_atr     = dist_asian_high_atr;
         snap.dist_asian_low_atr      = dist_asian_low_atr;
         snap.is_asian_sweep          = is_asian_sweep;
```

## Step 3948 - Tool Response
```diff
@@ -1,8 +1,8 @@
-- `[/]` Execute Phase 11: Oboe Hotfix and Global Retraining
-  - `[ ]` Update `ML_Logger.mqh` (Schema)
-  - `[ ]` Update `HMA_ML_Orchestrator.mq5` (Shift fix, Trigger unlock, Feature mapping)
-  - `[ ]` Update `Alpha_Sniper_Deploy.mq5` (Shift fix, JSON payload)
-  - `[ ]` Update `pipeline_global_optimizer.py` (Concept Drift weights, Feature Schema)
-  - `[ ]` Update `produccion_flask_server.py` (if needed for Schema sync)
-  - `[ ]` Compile `.mq5` files and verify no errors.
+- `[x]` Execute Phase 11: Oboe Hotfix and Global Retraining
+  - `[x]` Update `ML_Logger.mqh` (Schema)
+  - `[x]` Update `HMA_ML_Orchestrator.mq5` (Shift fix, Trigger unlock, Feature mapping)
+  - `[x]` Update `Alpha_Sniper_Deploy.mq5` (Shift fix, JSON payload)
+  - `[x]` Update `pipeline_global_optimizer.py` (Concept Drift weights, Feature Schema)
+  - `[x]` Update `produccion_flask_server.py` (if needed for Schema sync)
+  - `[x]` Compile `.mq5` files and verify no errors.
```

## Step 4082 - Tool Call: multi_replace_file_content
**Instruction:** "Inject InpScaleOutRR, InpFastHMA_Exit_Period, fast_hma_exit_handle, g_scaled_tickets[] array, and handle initialization."
**Description:** "Phase 12: Add inputs, globals, handle init/deinit in Orchestrator."

```json
{
  "Description": "\"Phase 12: Add inputs, globals, handle init/deinit in Orchestrator.\"",
  "Instruction": "\"Inject InpScaleOutRR, InpFastHMA_Exit_Period, fast_hma_exit_handle, g_scaled_tickets[] array, and handle initialization.\"",
  "ReplacementChunks": "[{\"AllowMultiple\":false,\"EndLine\":48,\"ReplacementContent\":\"input group \\\"== Gestion ML (Triple Barrera) ==\\\"\\ninput double InpInitialBalance   = 100000.0;\\ninput double TakeProfitMultiplier = 3.0;\\ninput double InpScaleOutRR       = 1.5;  // RR flotante para Scale-Out parcial (50%)\\ninput int    InpFastHMA_Exit_Period = 14; // Periodo HMA rapida de salida (Kinematic Trailing)\\n// VerticalBarrierBars es dinamico: InpHMA_ExitPeriod * 1.5\",\"StartLine\":45,\"TargetContent\":\"input group \\\"== Gestion ML (Triple Barrera) ==\\\"\\ninput double InpInitialBalance   = 100000.0;\\ninput double TakeProfitMultiplier = 3.0;\\n// VerticalBarrierBars es dinamico: InpHMA_ExitPeriod * 1.5\"},{\"AllowMultiple\":false,\"EndLine\":66,\"ReplacementContent\":\"int ema50_h4_handle;\\nint atr200_handle;\\nint adx_handle;\\nint fast_hma_exit_handle;  // Fase 12: HMA rapida para Kinematic Trailing\\n\\n// Scale-Out tracking: tickets que ya han recibido Scale-Out\\nulong g_scaled_tickets[];\",\"StartLine\":64,\"TargetContent\":\"int ema50_h4_handle;\\nint atr200_handle;\\nint adx_handle;\"},{\"AllowMultiple\":false,\"EndLine\":99,\"ReplacementContent\":\"    hma_handle      = iCustom(_Symbol, _Period, \\\"HMA50\\\", HMAPeriod);\\n    hma_exit_handle = iCustom(_Symbol, _Period, \\\"HMA50\\\", InpHMA_ExitPeriod);\\n    fast_hma_exit_handle = iCustom(_Symbol, _Period, \\\"HMA50\\\", InpFastHMA_Exit_Period);\\n    rsi_handle      = iRSI(_Symbol, _Period, RsiPeriod, PRICE_CLOSE);\\n    atr_handle      = iATR(_Symbol, _Period, 14);\\n    ema50_handle    = iMA(_Symbol, g_macro_tf, 50,  0, MODE_EMA, PRICE_CLOSE);\\n    ema200_handle   = iMA(_Symbol, g_macro_tf, 200, 0, MODE_EMA, PRICE_CLOSE);\\n    sma20_handle    = iMA(_Symbol, _Period, 20, 0, MODE_SMA, PRICE_CLOSE);\\n    std_dev_handle  = iStdDev(_Symbol, _Period, 20, 0, MODE_SMA, PRICE_CLOSE);\\n    ema50_h4_handle = iMA(_Symbol, PERIOD_H4, 50, 0, MODE_EMA, PRICE_CLOSE);\",\"StartLine\":91,\"TargetContent\":\"    hma_handle      = iCustom(_Symbol, _Period, \\\"HMA50\\\", HMAPeriod);\\n    hma_exit_handle = iCustom(_Symbol, _Period, \\\"HMA50\\\", InpHMA_ExitPeriod);\\\n<truncated 2367 bytes>",
  "TargetFile": "\"C:\\\\Users\\\\Manuel\\\\Desktop\\\\HMA_MetaLabeling\\\\MQL5_Engine\\\\HMA_ML_Orchestrator.mq5\"",
  "toolAction": "\"Injecting inputs and globals to Orchestrator\"",
  "toolSummary": "\"Editing HMA_ML_Orchestrator.mq5\""
}
```

## Step 4083 - Tool Response
```diff
@@ -45,6 +45,8 @@
 input group "== Gestion ML (Triple Barrera) =="
 input double InpInitialBalance   = 100000.0;
 input double TakeProfitMultiplier = 3.0;
+input double InpScaleOutRR       = 1.5;  // RR flotante para Scale-Out parcial (50%)
+input int    InpFastHMA_Exit_Period = 14; // Periodo HMA rapida de salida (Kinematic Trailing)
 // VerticalBarrierBars es dinamico: InpHMA_ExitPeriod * 1.5
 
 input group "== Filtros Macro / Cisnes Negros =="
@@ -63,6 +63,10 @@
 int ema50_h4_handle;
 int atr200_handle;
 int adx_handle;
+int fast_hma_exit_handle;  // Fase 12: HMA rapida para Kinematic Trailing
+
+// Scale-Out tracking: tickets que ya han recibido Scale-Out
+ulong g_scaled_tickets[];
 
 //+------------------------------------------------------------------+
 //| OnInit                                                           |
@@ -88,6 +88,7 @@
 
     hma_handle      = iCustom(_Symbol, _Period, "HMA50", HMAPeriod);
     hma_exit_handle = iCustom(_Symbol, _Period, "HMA50", InpHMA_ExitPeriod);
+    fast_hma_exit_handle = iCustom(_Symbol, _Period, "HMA50", InpFastHMA_Exit_Period);
     rsi_handle      = iRSI(_Symbol, _Period, RsiPeriod, PRICE_CLOSE);
     atr_handle      = iATR(_Symbol, _Period, 14);
     ema50_handle    = iMA(_Symbol, g_macro_tf, 50,  0, MODE_EMA, PRICE_CLOSE);
@@ -99,6 +99,7 @@
 
     if(hma_handle      == INVALID_HANDLE ||
        hma_exit_handle == INVALID_HANDLE ||
+       fast_hma_exit_handle == INVALID_HANDLE ||
        rsi_handle      == INVALID_HANDLE ||
        atr_handle      == INVALID_HANDLE ||
        std_dev_handle  == INVALID_HANDLE ||
@@ -122,6 +122,7 @@
     delete exit_logger;
     IndicatorRelease(hma_handle);
     IndicatorRelease(hma_exit_handle);
+    IndicatorRelease(fast_hma_exit_handle);
     IndicatorRelease(rsi_handle);
     IndicatorRelease(atr_handle);
     IndicatorRelease(ema50_handle);
@@ -130,6 +130,7 @@
     IndicatorRelease(adx_handle);
     IndicatorRelease(ema50_h4_handle);
     IndicatorRelease(atr200_handle);
+    ArrayFree(g_scaled_tickets);
 }
 
 //+------------------------------------------------------------------+
```

## Step 4085 - Tool Call: multi_replace_file_content
**Instruction:** "Add the Scale-Out logic and the Fast HMA Cross trigger to Orchestrator functions."
**Description:** "Phase 12: Update CheckAndFireExitDilemma to include is_trigger_fast_hma_cross and explicit close_1, close_2. Add Scale-Out to ManageAllPhysicalPositions. Read fast_hma_k in OnTick."

```json
{
  "Description": "\"Phase 12: Update CheckAndFireExitDilemma to include is_trigger_fast_hma_cross and explicit close_1, close_2. Add Scale-Out to ManageAllPhysicalPositions. Read fast_hma_k in OnTick.\"",
  "Instruction": "\"Add the Scale-Out logic and the Fast HMA Cross trigger to Orchestrator functions.\"",
  "ReplacementChunks": "[{\"AllowMultiple\":false,\"EndLine\":162,\"ReplacementContent\":\"                             double hma_exit_1, double hma_exit_2, double hma_exit_3,\\n                             double fast_hma_1, double fast_hma_2, double fast_hma_3,\\n                             double rsi_1, double rsi_2,\\n                             double current_atr, double atr_sma50, double spread,\\n                             double macro_adx,\\n                             double close_1, double close_2, double fast_hma_k_1, double fast_hma_k_2)\",\"StartLine\":158,\"TargetContent\":\"                             double hma_exit_1, double hma_exit_2, double hma_exit_3,\\n                             double fast_hma_1, double fast_hma_2, double fast_hma_3,\\n                             double rsi_1, double rsi_2,\\n                             double current_atr, double atr_sma50, double spread,\\n                             double macro_adx)\"},{\"AllowMultiple\":false,\"EndLine\":197,\"ReplacementContent\":\"    // === Evaluacion One-Hot de los 4 Triggers ===\\n    int is_trigger_fast   = 0;\\n    int is_trigger_slow   = 0;\\n    int is_trigger_rsi    = 0;\\n    int is_trigger_profit = 0;\\n    int is_trigger_fast_hma_cross = 0; // Fase 12\\n\\n    if(pos_type == POSITION_TYPE_BUY) {\\n        if(fast_hma_1 < fast_hma_2 && fast_hma_2 >= fast_hma_3) is_trigger_fast   = 1;\\n        if(hma_exit_1 < hma_exit_2 && hma_exit_2 >= hma_exit_3) is_trigger_slow   = 1;\\n        if(rsi_1 < 50.0 && rsi_2 >= 50.0)                        is_trigger_rsi    = 1;\\n        if(fast_hma_k_2 > 0 && close_1 < fast_hma_k_1 && close_2 >= fast_hma_k_2)\\n            is_trigger_fast_hma_cross = 1;\\n    } else {\\n        if(pos_type == POSITION_TYPE_SELL) {\\n            if(fast_hma_1 > fast_hma_2 && fast_hma_2 <= fast_hma_3) is_trigger_fast   = 1;\\n            if(hma_exit_1 > hma_exit_2 && hma_exit_2 <= hma_exit_3) is_trigger_slow   = 1;\\n            if(rsi_1 > 50.0 && rsi_2 <= 50.0)                        is_trigger_rsi    = 1;\\n            if(fast_hma_k_2 > 0 && close_1 > fast_hma_k_1 && \n<truncated 8625 bytes>",
  "TargetFile": "\"C:\\\\Users\\\\Manuel\\\\Desktop\\\\HMA_MetaLabeling\\\\MQL5_Engine\\\\HMA_ML_Orchestrator.mq5\"",
  "toolAction": "\"Injecting logic into Orchestrator functions\"",
  "toolSummary": "\"Editing HMA_ML_Orchestrator.mq5\""
}
```

## Step 4086 - Tool Response
```diff
@@ -169,7 +169,8 @@
                              double fast_hma_1, double fast_hma_2, double fast_hma_3,
                              double rsi_1, double rsi_2,
                              double current_atr, double atr_sma50, double spread,
-                             double macro_adx)
+                             double macro_adx,
+                             double close_1, double close_2, double fast_hma_k_1, double fast_hma_k_2)
 {
     double pip  = GetPip();
 
@@ -192,6 +192,7 @@
     int is_trigger_slow   = 0;
     int is_trigger_rsi    = 0;
     int is_trigger_profit = 0;
+    int is_trigger_fast_hma_cross = 0; // Fase 12
 
     if(pos_type == POSITION_TYPE_BUY) {
         if(fast_hma_1 < fast_hma_2 && fast_hma_2 >= fast_hma_3) is_trigger_fast   = 1;
@@ -198,4 +198,6 @@
         if(rsi_1 < 50.0 && rsi_2 >= 50.0)                        is_trigger_rsi    = 1;
+        if(fast_hma_k_2 > 0 && close_1 < fast_hma_k_1 && close_2 >= fast_hma_k_2)
+            is_trigger_fast_hma_cross = 1;
     } else {
         if(pos_type == POSITION_TYPE_SELL) {
             if(fast_hma_1 > fast_hma_2 && fast_hma_2 <= fast_hma_3) is_trigger_fast   = 1;
@@ -202,4 +202,6 @@
             if(rsi_1 > 50.0 && rsi_2 <= 50.0)                        is_trigger_rsi    = 1;
+            if(fast_hma_k_2 > 0 && close_1 > fast_hma_k_1 && close_2 <= fast_hma_k_2)
+                is_trigger_fast_hma_cross = 1;
         }
     }
 
@@ -214,6 +214,7 @@
     if(is_trigger_slow   == 1) any_trigger = true;
     if(is_trigger_rsi    == 1) any_trigger = true;
     if(is_trigger_profit == 1) any_trigger = true;
+    if(is_trigger_fast_hma_cross == 1) any_trigger = true;
 
     if(!any_trigger) retu
<truncated 3582 bytes>
             PrintFormat("[SCALE-OUT] 50%% cerrado. BE movido a %.5f. Ticket: %I64u", open_p, ticket);
+                }
 
                 // HARD CLOSE: Invalidador físico innegociable
                 bool hard_close = false;
@@ -322,7 +322,8 @@
                         hma_exit_1, hma_exit_2, hma_exit_3,
                         fast_hma_1, fast_hma_2, fast_hma_3,
                         rsi_1, rsi_2,
-                        current_atr, atr_sma50, spread, macro_adx);
+                        current_atr, atr_sma50, spread, macro_adx,
+                        close_1, close_2, fast_hma_k_1, fast_hma_k_2);
 
                     // Barrera Temporal: cierra si supera el limite de barras
                     int open_bar    = iBarShift(_Symbol, _Period, open_t);
@@ -374,6 +374,12 @@
     if(hma_copied < 4)   return;
     int hma_exit_copied = CopyBuffer(hma_exit_handle, 0, 0, 3, hma_exit_buf);
     if(hma_exit_copied < 3) return;
+    
+    // Fase 12: Fast HMA para Kinematic Trailing
+    double fast_hma_k[];
+    ArraySetAsSeries(fast_hma_k, true);
+    if(CopyBuffer(fast_hma_exit_handle, 0, 0, 4, fast_hma_k) < 4) return;
+    
     if(CopyBuffer(rsi_handle,     0, 0, RsiLookbackBars + 1, rsi_buf) < RsiLookbackBars + 1) return;
     if(CopyBuffer(atr_handle,     0, 0, 51, atr_buf)  < 51) return;
     if(CopyBuffer(atr200_handle,  0, 0, 1,  atr200_buf) < 1) return;
@@ -406,7 +406,8 @@
         hma[0], hma[1], hma[2],
         rsi_buf[0], rsi_buf[1],
         current_atr, atr_sma50, spread,
-        currentBarTime, rates[0].close, macro_adx);
+        currentBarTime, rates[0].close, rates[1].close, macro_adx,
+        fast_hma_k[0], fast_hma_k[1]);
 
     // === PASO 2: DETECCION DE GATILLOS EN SHIFT 1 (Cero Repintado) ===
     // RASTREADORES ESTRUCTURALES ESTÁTICOS
```

## Step 4282 - Tool Call: multi_replace_file_content
**Instruction:** "Declara handles, cópialos en OnTick y asígnalos al snapshot"
**Description:** "Inyectar variables MTF y BB en Orchestrator"

```json
{
  "Description": "\"Inyectar variables MTF y BB en Orchestrator\"",
  "Instruction": "\"Declara handles, c\u00f3pialos en OnTick y as\u00edgnalos al snapshot\"",
  "ReplacementChunks": "[{\"AllowMultiple\":false,\"EndLine\":67,\"ReplacementContent\":\"int ema50_h4_handle;\\nint atr200_handle;\\nint atr_d1_handle;\",\"StartLine\":66,\"TargetContent\":\"int ema50_h4_handle;\\nint atr200_handle;\"},{\"AllowMultiple\":false,\"EndLine\":108,\"ReplacementContent\":\"    atr200_handle   = iATR(_Symbol, _Period, 200);\\n    atr_d1_handle   = iATR(_Symbol, PERIOD_D1, 14);\\n    adx_handle      = iADX(_Symbol, PERIOD_D1, 14);\",\"StartLine\":107,\"TargetContent\":\"    atr200_handle   = iATR(_Symbol, _Period, 200);\\n    adx_handle      = iADX(_Symbol, PERIOD_D1, 14);\"},{\"AllowMultiple\":false,\"EndLine\":118,\"ReplacementContent\":\"       ema50_h4_handle == INVALID_HANDLE ||\\n       atr200_handle   == INVALID_HANDLE ||\\n       atr_d1_handle   == INVALID_HANDLE ||\\n       adx_handle      == INVALID_HANDLE)\",\"StartLine\":116,\"TargetContent\":\"       ema50_h4_handle == INVALID_HANDLE ||\\n       atr200_handle   == INVALID_HANDLE ||\\n       adx_handle      == INVALID_HANDLE)\"},{\"AllowMultiple\":false,\"EndLine\":146,\"ReplacementContent\":\"    IndicatorRelease(ema50_h4_handle);\\n    IndicatorRelease(atr200_handle);\\n    IndicatorRelease(atr_d1_handle);\",\"StartLine\":145,\"TargetContent\":\"    IndicatorRelease(ema50_h4_handle);\\n    IndicatorRelease(atr200_handle);\"},{\"AllowMultiple\":false,\"EndLine\":430,\"ReplacementContent\":\"    double atr200_buf[], adx_buf[], sma20[], std_dev[];\\n    double atr_d1_buf[];\",\"StartLine\":429,\"TargetContent\":\"    double atr200_buf[], adx_buf[], sma20[], std_dev[];\"},{\"AllowMultiple\":false,\"EndLine\":444,\"ReplacementContent\":\"    if(CopyBuffer(atr_handle,     0, 0, 51, atr_buf)  < 51) return;\\n    if(CopyBuffer(atr200_handle,  0, 0, 1,  atr200_buf) < 1) return;\\n    if(CopyBuffer(atr_d1_handle,  0, 0, 1,  atr_d1_buf) < 1) return;\\n    if(CopyBuffer(sma20_handle,   0, 0, 1,  sma20)    < 1)  return;\",\"StartLine\":442,\"TargetContent\":\"    if(CopyBuffer(atr_handle,     0, 0, 51, atr_buf)  < 51) return;\\n    if(CopyBuffer(atr200_handle,  0, 0, 1,  atr200_buf) < 1) return;\\n    if(CopyBuffer(sma20_handle,   0, 0, 1,  sma20)    < 1)  ret\n<truncated 1756 bytes>",
  "TargetFile": "\"C:\\\\Users\\\\Manuel\\\\Desktop\\\\HMA_MetaLabeling\\\\MQL5_Engine\\\\HMA_ML_Orchestrator.mq5\"",
  "toolAction": "\"Modificando HMA_ML_Orchestrator\"",
  "toolSummary": "\"Editing HMA_ML_Orchestrator.mq5\""
}
```

## Step 4283 - Tool Response
```diff
@@ -65,6 +65,7 @@
 int sma20_handle, std_dev_handle;
 int ema50_h4_handle;
 int atr200_handle;
+int atr_d1_handle;
 int adx_handle;
 int fast_hma_exit_handle;  // Fase 12: HMA rapida para Kinematic Trailing
 
@@ -104,6 +104,7 @@
     std_dev_handle  = iStdDev(_Symbol, _Period, 20, 0, MODE_SMA, PRICE_CLOSE);
     ema50_h4_handle = iMA(_Symbol, PERIOD_H4, 50, 0, MODE_EMA, PRICE_CLOSE);
     atr200_handle   = iATR(_Symbol, _Period, 200);
+    atr_d1_handle   = iATR(_Symbol, PERIOD_D1, 14);
     adx_handle      = iADX(_Symbol, PERIOD_D1, 14);
 
     if(hma_handle      == INVALID_HANDLE ||
@@ -113,6 +113,7 @@
        std_dev_handle  == INVALID_HANDLE ||
        ema50_h4_handle == INVALID_HANDLE ||
        atr200_handle   == INVALID_HANDLE ||
+       atr_d1_handle   == INVALID_HANDLE ||
        adx_handle      == INVALID_HANDLE)
     {
         Print("ERROR CRITICO: Indicadores no inicializados.");
@@ -141,6 +141,7 @@
     IndicatorRelease(adx_handle);
     IndicatorRelease(ema50_h4_handle);
     IndicatorRelease(atr200_handle);
+    IndicatorRelease(atr_d1_handle);
     ArrayFree(g_scaled_tickets);
 }
 
@@ -407,7 +407,7 @@
 
     // === EXTRACCION DE BUFFERS (velas cerradas — shift >= 1) ===
     double hma[], hma_exit_buf[], rsi_buf[], atr_buf[];
-    double ef[], es[], sma20[], stddev[], ema50_h4[], atr200_buf[];
+    double ef[], es[], sma20[], std_dev[], ema50_h4[], atr200_buf[], adx_buf[], atr_d1_buf[];
     MqlRates rates[];
 
     ArraySetAsSeries(hma,          true);
@@ -416,9 +416,11 @@
     ArraySetAsSeries(ef,           true);
     ArraySetAsSeries(es,           true);
     ArraySetAsSeries(sma20,        true);
-    ArraySetAsSeries(stddev,       true);
+    Array
<truncated 1479 bytes>
tddev[0];
+    if(std_dev[0] > 0) z_score = (current_close - sma20[0]) / std_dev[0];
 
     double atr_sum = 0.0;
     for(int k = 0; k < 10; k++) atr_sum += atr_buf[k];
@@ -751,6 +751,27 @@
         double real_spread_impact = 0.0;
         if(real_sl_pips > 0) real_spread_impact = spread / real_sl_pips;
 
+        // Fase 14: Advanced Robustness
+        double mtf_atr_ratio = 0.0;
+        if (atr_d1_buf[0] > 0) mtf_atr_ratio = current_atr / atr_d1_buf[0];
+
+        double trigger_rejection_tail = 0.0;
+        double candle_range = rates[1].high - rates[1].low;
+        if(candle_range > 0) {
+            if(signalType == 0) {
+                // Buy: rechazo inferior
+                trigger_rejection_tail = (MathMin(rates[1].open, rates[1].close) - rates[1].low) / candle_range;
+            } else {
+                // Sell: rechazo superior
+                trigger_rejection_tail = (rates[1].high - MathMax(rates[1].open, rates[1].close)) / candle_range;
+            }
+        }
+
+        double bollinger_dev = 0.0;
+        if(std_dev[0] > 0) {
+            bollinger_dev = (rates[1].close - sma20[0]) / std_dev[0];
+        }
+
         // Construir snapshot de entrada y registrarlo en el logger
         MarketSnapshot snap;
         ZeroMemory(snap);
@@ -799,6 +799,9 @@
         snap.tick_volume_zscore      = tick_vol_zscore;
         snap.spread_expansion_ratio  = spread_exp_ratio;
         snap.candle_dominance        = candle_dominance;
+        snap.mtf_atr_ratio           = mtf_atr_ratio;
+        snap.trigger_rejection_tail  = trigger_rejection_tail;
+        snap.bollinger_dev           = bollinger_dev;
 
         logger.RecordSignal(snap);
```

## Step 4367 - Tool Call: multi_replace_file_content
**Instruction:** "Pasa mtf_atr_ratio, trigger_rejection_tail, bollinger_dev a CheckAndFireExitDilemma y ManageAllPhysicalPositions"
**Description:** "Pasando features al Exit Model en HMA_ML_Orchestrator.mq5"

```json
{
  "Description": "\"Pasando features al Exit Model en HMA_ML_Orchestrator.mq5\"",
  "Instruction": "\"Pasa mtf_atr_ratio, trigger_rejection_tail, bollinger_dev a CheckAndFireExitDilemma y ManageAllPhysicalPositions\"",
  "ReplacementChunks": "[{\"AllowMultiple\":false,\"EndLine\":220,\"ReplacementContent\":\"                               double current_atr, double atr_sma50, double spread,\\n                               double macro_adx,\\n                               double close_1, double close_2, double fast_hma_k_1, double fast_hma_k_2,\\n                               double mtf_atr_ratio, double trigger_rejection_tail, double bollinger_dev)\",\"StartLine\":217,\"TargetContent\":\"                               double current_atr, double atr_sma50, double spread,\\n                               double macro_adx,\\n                               double close_1, double close_2, double fast_hma_k_1, double fast_hma_k_2)\"},{\"AllowMultiple\":false,\"EndLine\":273,\"ReplacementContent\":\"    snap.is_trigger_profit    = is_trigger_profit;\\n    snap.is_trigger_fast_hma_cross = is_trigger_fast_hma_cross;\\n    snap.mtf_atr_ratio        = mtf_atr_ratio;\\n    snap.trigger_rejection_tail = trigger_rejection_tail;\\n    snap.bollinger_dev        = bollinger_dev;\\n    snap.missed_profit_r      = 0.0;\\n    snap.label                = -1;\",\"StartLine\":270,\"TargetContent\":\"    snap.is_trigger_profit    = is_trigger_profit;\\n    snap.is_trigger_fast_hma_cross = is_trigger_fast_hma_cross;\\n    snap.missed_profit_r      = 0.0;\\n    snap.label                = -1;\"},{\"AllowMultiple\":false,\"EndLine\":291,\"ReplacementContent\":\"      double rsi_1, double rsi_2,\\n      double current_atr, double atr_sma50, double spread,\\n      datetime currentBarTime, double close_1, double close_2, double macro_adx,\\n      double fast_hma_k_1, double fast_hma_k_2,\\n      double mtf_atr_ratio, double bollinger_dev, const MqlRates &r[])\",\"StartLine\":288,\"TargetContent\":\"      double rsi_1, double rsi_2,\\n      double current_atr, double atr_sma50, double spread,\\n      datetime currentBarTime, double close_1, double close_2, double macro_adx,\\n      double fast_hma_k_1, double fast_hma_k_2)\"},{\"AllowMultiple\":false,\"EndLine\":373,\"ReplacementContent\":\"                  double   sl_p     = PositionGetDouble(P\n<truncated 4751 bytes>",
  "TargetFile": "\"C:\\\\Users\\\\Manuel\\\\Desktop\\\\HMA_MetaLabeling\\\\MQL5_Engine\\\\HMA_ML_Orchestrator.mq5\"",
  "toolAction": "\"Inyectando exit features en el EA\"",
  "toolSummary": "\"Editing Orchestrator.mq5\""
}
```

## Step 4368 - Tool Response
```diff
@@ -174,7 +174,8 @@
                              double rsi_1, double rsi_2,
                              double current_atr, double atr_sma50, double spread,
                              double macro_adx,
-                             double close_1, double close_2, double fast_hma_k_1, double fast_hma_k_2)
+                             double close_1, double close_2, double fast_hma_k_1, double fast_hma_k_2,
+                             double mtf_atr_ratio, double trigger_rejection_tail, double bollinger_dev)
 {
     double pip  = GetPip();
 
@@ -268,6 +268,9 @@
     snap.is_trigger_rsi       = is_trigger_rsi;
     snap.is_trigger_profit    = is_trigger_profit;
     snap.is_trigger_fast_hma_cross = is_trigger_fast_hma_cross;
+    snap.mtf_atr_ratio        = mtf_atr_ratio;
+    snap.trigger_rejection_tail = trigger_rejection_tail;
+    snap.bollinger_dev        = bollinger_dev;
     snap.missed_profit_r      = 0.0;
     snap.label                = -1;
 
@@ -289,7 +289,8 @@
     double rsi_1, double rsi_2,
     double current_atr, double atr_sma50, double spread,
     datetime currentBarTime, double close_1, double close_2, double macro_adx,
-    double fast_hma_k_1, double fast_hma_k_2)
+    double fast_hma_k_1, double fast_hma_k_2,
+    double mtf_atr_ratio, double bollinger_dev, const MqlRates &r[])
 {
     int total = PositionsTotal();
     for(int i = total - 1; i >= 0; i--)
@@ -306,6 +306,16 @@
                 double   sl_p     = PositionGetDouble(POSITION_SL);
                 datetime open_t   = (datetime)PositionGetInteger(POSITION_TIME);
 
+                double trigger_rejection_tail = 0.0;
+                double cdl_range = r[1].high - r[1].low;
+     
<truncated 1262 bytes>
atr = atr_buf[0];
 
+    // Fase 14: Compute Advanced Robustness for Exit Model (will also be used for Entry Model)
+    double mtf_atr_ratio = 0.0;
+    if (atr_d1_buf[0] > 0) mtf_atr_ratio = current_atr / atr_d1_buf[0];
+
+    double bollinger_dev = 0.0;
+    if(std_dev[0] > 0) {
+        bollinger_dev = (rates[1].close - sma20[0]) / std_dev[0];
+    }
+
     // === PASO 1: GESTION DE TODAS LAS POSICIONES ABIERTAS ===
     ManageAllPhysicalPositions(
         hma_exit_buf[0], hma_exit_buf[1], hma_exit_buf[2],
@@ -472,7 +472,8 @@
         rsi_buf[0], rsi_buf[1],
         current_atr, atr_sma50, spread,
         currentBarTime, rates[0].close, rates[1].close, macro_adx,
-        fast_hma_k[0], fast_hma_k[1]);
+        fast_hma_k[0], fast_hma_k[1],
+        mtf_atr_ratio, bollinger_dev, rates);
 
     // === PASO 2: DETECCION DE GATILLOS EN SHIFT 1 (Cero Repintado) ===
     // RASTREADORES ESTRUCTURALES ESTÁTICOS
@@ -759,10 +759,6 @@
         double real_spread_impact = 0.0;
         if(real_sl_pips > 0) real_spread_impact = spread / real_sl_pips;
 
-        // Fase 14: Advanced Robustness
-        double mtf_atr_ratio = 0.0;
-        if (atr_d1_buf[0] > 0) mtf_atr_ratio = current_atr / atr_d1_buf[0];
-
         double trigger_rejection_tail = 0.0;
         double candle_range = rates[1].high - rates[1].low;
         if(candle_range > 0) {
@@ -774,11 +774,6 @@
             }
         }
 
-        double bollinger_dev = 0.0;
-        if(std_dev[0] > 0) {
-            bollinger_dev = (rates[1].close - sma20[0]) / std_dev[0];
-        }
-
         // Construir snapshot de entrada y registrarlo en el logger
         MarketSnapshot snap;
         ZeroMemory(snap);
```

## Step 4530 - Tool Call: multi_replace_file_content
**Instruction:** "Normalize hma_vel, hma_accel, hma_slope, exit_hma_velocity by current_atr"
**Description:** "Normalizing kinematics in Orchestrator by ATR"

```json
{
  "Description": "\"Normalizing kinematics in Orchestrator by ATR\"",
  "Instruction": "\"Normalize hma_vel, hma_accel, hma_slope, exit_hma_velocity by current_atr\"",
  "ReplacementChunks": "[{\"AllowMultiple\":false,\"EndLine\":244,\"ReplacementContent\":\"    double hma_vel   = (hma_exit_1 - hma_exit_2) / current_atr;\\n    double vel_prev  = (hma_exit_2 - hma_exit_3) / current_atr;\\n    double hma_accel = hma_vel - vel_prev;\",\"StartLine\":241,\"TargetContent\":\"    double hma_vel   = hma_exit_1 - hma_exit_2;\\n    double vel_prev  = hma_exit_2 - hma_exit_3;\\n    double hma_accel = hma_vel - vel_prev;\"},{\"AllowMultiple\":false,\"EndLine\":689,\"ReplacementContent\":\"    double hma_slope = 0.0;\\n    if(current_atr > 0) hma_slope = (hma[0] - hma[1]) / current_atr;\",\"StartLine\":688,\"TargetContent\":\"    double hma_slope = 0.0;\\n    if(hma[1] != 0) hma_slope = ((hma[0] - hma[1]) / hma[1]) * 100.0;\"},{\"AllowMultiple\":false,\"EndLine\":691,\"ReplacementContent\":\"    double hma_accel_feat = CalcHmaAcceleration(hma_handle, current_atr);\",\"StartLine\":691,\"TargetContent\":\"    double hma_accel_feat = CalcHmaAcceleration(hma_handle);\"},{\"AllowMultiple\":false,\"EndLine\":743,\"ReplacementContent\":\"    double hma_vel        = (hma[0] - hma[1]) / current_atr;\\n    double vel_prev_k     = (hma[1] - hma[2]) / current_atr;\\n    double hma_accel_v2   = hma_vel - vel_prev_k;\\n    double vel_prev2_k    = (hma[2] - hma[3]) / current_atr;\\n    double accel_prev_k   = vel_prev_k - vel_prev2_k;\",\"StartLine\":739,\"TargetContent\":\"    double hma_vel        = hma[0] - hma[1];\\n    double vel_prev_k     = hma[1] - hma[2];\\n    double hma_accel_v2   = hma_vel - vel_prev_k;\\n    double vel_prev2_k    = hma[2] - hma[3];\\n    double accel_prev_k   = vel_prev_k - vel_prev2_k;\"}]",
  "TargetFile": "\"C:\\\\Users\\\\Manuel\\\\Desktop\\\\HMA_MetaLabeling\\\\MQL5_Engine\\\\HMA_ML_Orchestrator.mq5\"",
  "toolAction": "\"Normalizing MQL5 Orchestrator\"",
  "toolSummary": "\"Normalizing Orchestrator physics\""
}
```

## Step 4531 - Tool Response
```diff
@@ -238,8 +238,8 @@
     double dd_from_peak_r = 0.0;
     if(risk > 0) dd_from_peak_r = dd_from_peak_price / risk;
 
-    double hma_vel   = hma_exit_1 - hma_exit_2;
-    double vel_prev  = hma_exit_2 - hma_exit_3;
+    double hma_vel   = (hma_exit_1 - hma_exit_2) / current_atr;
+    double vel_prev  = (hma_exit_2 - hma_exit_3) / current_atr;
     double hma_accel = hma_vel - vel_prev;
 
     double sl_pips = 0.0;
@@ -685,9 +685,9 @@
     CalcRsiExtremeMetrics(rsi_handle, RsiLookbackBars, signalType, rsi_extreme, bars_since);
 
     double hma_slope = 0.0;
-    if(hma[1] != 0) hma_slope = ((hma[0] - hma[1]) / hma[1]) * 100.0;
-
-    double hma_accel_feat = CalcHmaAcceleration(hma_handle);
+    if(current_atr > 0) hma_slope = (hma[0] - hma[1]) / current_atr;
+
+    double hma_accel_feat = CalcHmaAcceleration(hma_handle, current_atr);
     double breakout_force = CalcBreakoutForceATR(current_close, hma[0], current_atr);
 
     int    trend_align = -1;
@@ -734,10 +734,10 @@
 
     int day_of_week = dt.day_of_week;
 
-    double hma_vel        = hma[0] - hma[1];
-    double vel_prev_k     = hma[1] - hma[2];
+    double hma_vel        = (hma[0] - hma[1]) / current_atr;
+    double vel_prev_k     = (hma[1] - hma[2]) / current_atr;
     double hma_accel_v2   = hma_vel - vel_prev_k;
-    double vel_prev2_k    = hma[2] - hma[3];
+    double vel_prev2_k    = (hma[2] - hma[3]) / current_atr;
     double accel_prev_k   = vel_prev_k - vel_prev2_k;
     double hma_jerk_val   = hma_accel_v2 - accel_prev_k;
```

## Step 4691 - Tool Call: multi_replace_file_content
**Instruction:** "Update CheckAndFireExitDilemma and ManageAllPhysicalPositions to compute and pass the Phase 16 features"
**Description:** "Injecting Rubber Band features into Orchestrator"

```json
{
  "Description": "\"Injecting Rubber Band features into Orchestrator\"",
  "Instruction": "\"Update CheckAndFireExitDilemma and ManageAllPhysicalPositions to compute and pass the Phase 16 features\"",
  "ReplacementChunks": "[{\"AllowMultiple\":false,\"EndLine\":179,\"ReplacementContent\":\"                             double close_1, double close_2, double fast_hma_k_1, double fast_hma_k_2,\\n                             double mtf_atr_ratio, double trigger_rejection_tail, double bollinger_dev,\\n                             double peak_hma_stretch_atr, double current_hma_stretch_atr, double elastic_retracement_pct)\\n{\",\"StartLine\":177,\"TargetContent\":\"                             double close_1, double close_2, double fast_hma_k_1, double fast_hma_k_2,\\n                             double mtf_atr_ratio, double trigger_rejection_tail, double bollinger_dev)\\n{\"},{\"AllowMultiple\":false,\"EndLine\":278,\"ReplacementContent\":\"    snap.bollinger_dev        = bollinger_dev;\\n    snap.peak_hma_stretch_atr    = peak_hma_stretch_atr;\\n    snap.current_hma_stretch_atr = current_hma_stretch_atr;\\n    snap.elastic_retracement_pct = elastic_retracement_pct;\\n    snap.missed_profit_r      = 0.0;\\n    snap.label                = -1;\",\"StartLine\":275,\"TargetContent\":\"    snap.bollinger_dev        = bollinger_dev;\\n    snap.missed_profit_r      = 0.0;\\n    snap.label                = -1;\"},{\"AllowMultiple\":false,\"EndLine\":373,\"ReplacementContent\":\"                double mtf_atr_ratio = current_atr / atr_d1_val;\\n\\n                // Phase 16 Tracker\\n                double current_stretch = 0.0;\\n                if(current_atr > 0) current_stretch = MathAbs(rates[0].close - hma[0]) / current_atr;\\n                UpdatePeakStretch(ticket, current_stretch);\\n                double peak_stretch = GetPeakStretch(ticket);\\n                double elastic_pct = (peak_stretch > 0) ? ((peak_stretch - current_stretch) / peak_stretch) : 0.0;\\n\\n                // Check Triggers y Reportar Snapshot\\n                CheckAndFireExitDilemma(\\n                    ticket, pos_type, bars_in_trade,\\n                    open_price, risk, historical_mfe_price,\\n                    hma_exit_1, hma_exit_2, hma_exit_3,\\n                    fast_hma_1, fast_hma_2, fast_hma_3,\\n      \n<truncated 1356 bytes>",
  "TargetFile": "\"C:\\\\Users\\\\Manuel\\\\Desktop\\\\HMA_MetaLabeling\\\\MQL5_Engine\\\\HMA_ML_Orchestrator.mq5\"",
  "toolAction": "\"Actualizando Orchestrator\"",
  "toolSummary": "\"Editing HMA_ML_Orchestrator.mq5\""
}
```

## Step 4692 - Tool Response
```diff
@@ -175,7 +175,8 @@
                              double current_atr, double atr_sma50, double spread,
                              double macro_adx,
                              double close_1, double close_2, double fast_hma_k_1, double fast_hma_k_2,
-                             double mtf_atr_ratio, double trigger_rejection_tail, double bollinger_dev)
+                             double mtf_atr_ratio, double trigger_rejection_tail, double bollinger_dev,
+                             double peak_hma_stretch_atr, double current_hma_stretch_atr, double elastic_retracement_pct)
 {
     double pip  = GetPip();
 
@@ -272,6 +272,9 @@
     snap.mtf_atr_ratio        = mtf_atr_ratio;
     snap.trigger_rejection_tail = trigger_rejection_tail;
     snap.bollinger_dev        = bollinger_dev;
+    snap.peak_hma_stretch_atr    = peak_hma_stretch_atr;
+    snap.current_hma_stretch_atr = current_hma_stretch_atr;
+    snap.elastic_retracement_pct = elastic_retracement_pct;
     snap.missed_profit_r      = 0.0;
     snap.label                = -1;
 
@@ -389,6 +389,13 @@
                     trade.PositionClose(ticket);
                     PrintFormat("[HARD EXIT] FISICA ESTRUCTURAL ROTA. ABORTANDO. Ticket: %I64u", ticket);
                 } else {
+                    // Phase 16 Tracker
+                    double current_stretch = 0.0;
+                    if(current_atr > 0) current_stretch = MathAbs(r[0].close - fast_hma_1) / current_atr;
+                    UpdatePeakStretch(ticket, current_stretch);
+                    double peak_stretch = GetPeakStretch(ticket);
+                    double elastic_pct = (peak_stretch > 0) ? ((peak_stretch - current_stretch) / peak_stretch) : 0.0;
+
                     // Disparo de dilema de salida (One-Hot, sin cierre fisico)
                     CheckAndFireExitDilemma(
                         ticket, pos_type, bars_in_t, open_p, MathAbs(open_p - sl_p), mfe_price,
@@ -396,7 +396,8 @@
                         rsi_1, rsi_2,
                         current_atr, atr_sma50, spread, macro_adx,
                         close_1, close_2, fast_hma_k_1, fast_hma_k_2,
-                        mtf_atr_ratio, trigger_rejection_tail, bollinger_dev);
+                        mtf_atr_ratio, trigger_rejection_tail, bollinger_dev,
+                        peak_stretch, current_stretch, elastic_pct);
 
                     // Barrera Temporal: cierra si supera el limite de barras
                     int open_bar    = iBarShift(_Symbol, _Period, open_t);
@@ -409,6 +409,7 @@
             }
         }
     }
+    CleanTicketStates();
 }
 
 //+------------------------------------------------------------------+
```

## Step 4742 - Tool Response
```diff
@@ -1,10 +1,10 @@
 # Phase 16: Dynamic Excursion & Rubber Band Effect
 
-- `[ ]` Inyectar el tracker global `g_ticket_states` en `Alpha_Sniper_Deploy.mq5` (incluyendo limpieza en memoria).
-- `[ ]` Modificar `Alpha_Sniper_Deploy.mq5` para calcular y añadir `Peak_HMA_Stretch_ATR`, `Current_HMA_Stretch_ATR`, `Elastic_Retracement_Pct` al JSON de salida.
-- `[ ]` Inyectar el tracker global `g_ticket_states` en `HMA_ML_Orchestrator.mq5` (incluyendo limpieza tras cierre).
-- `[ ]` Modificar `ManageAllPhysicalPositions` y `CheckAndFireExitDilemma` en `HMA_ML_Orchestrator.mq5` para calcular y pasar las 3 nuevas features al `ExitSnapshot`.
-- `[ ]` Actualizar `ML_Logger.mqh`: Añadir las 3 features a `ExitSnapshot` y a las cabeceras/exportación del CSV.
-- `[ ]` Modificar `pipeline_global_optimizer.py`: Añadir las 3 features a `EXIT_FEATURES`.
-- `[ ]` Compilar los ejecutables `.ex5` de `HMA_ML_Orchestrator.mq5` y `Alpha_Sniper_Deploy.mq5` (0 errores).
+- `[x]` Inyectar el tracker global `g_ticket_states` en `Alpha_Sniper_Deploy.mq5` (incluyendo limpieza en memoria).
+- `[x]` Modificar `Alpha_Sniper_Deploy.mq5` para calcular y añadir `Peak_HMA_Stretch_ATR`, `Current_HMA_Stretch_ATR`, `Elastic_Retracement_Pct` al JSON de salida.
+- `[x]` Inyectar el tracker global `g_ticket_states` en `HMA_ML_Orchestrator.mq5` (incluyendo limpieza tras cierre).
+- `[x]` Modificar `ManageAllPhysicalPositions` y `CheckAndFireExitDilemma` en `HMA_ML_Orchestrator.mq5` para calcular y pasar las 3 nuevas features al `ExitSnapshot`.
+- `[x]` Actualizar `ML_Logger.mqh`: Añadir las 3 features a `ExitSnapshot` y a las cabeceras/exportación del CSV.
+- `[x]` Modificar `pipeline_global_optimizer.py`: Añadir las 3 features a `EXIT_FEATURES`.
+- `[x]` Compilar los ejecutables `.ex5` de `HMA_ML_Orchestrator.mq5` y `Alpha_Sniper_Deploy.mq5` (0 errores).
```

## Step 5205 - Tool Call: multi_replace_file_content
**Instruction:** "Añadir InpMaxSpreadPips_Metals y la lógica de validación"
**Description:** "Escalado dinámico de spread para oro en Orchestrator"

```json
{
  "Description": "\"Escalado din\u00e1mico de spread para oro en Orchestrator\"",
  "Instruction": "\"A\u00f1adir InpMaxSpreadPips_Metals y la l\u00f3gica de validaci\u00f3n\"",
  "ReplacementChunks": "[{\"AllowMultiple\":false,\"EndLine\":64,\"ReplacementContent\":\"input group \\\"== Microestructura ==\\\"\\ninput double MaxSpreadPips          = 4.0;\\ninput double InpMaxSpreadPips_Metals = 35.0; // Spread m\u00e1ximo ampliado para XAUUSD/XAGUSD\\ninput int    InpDonchianPeriod      = 20;\",\"StartLine\":63,\"TargetContent\":\"input group \\\"== Microestructura ==\\\"\\ninput double MaxSpreadPips       = 4.0;\\ninput int    InpDonchianPeriod   = 20;\"},{\"AllowMultiple\":false,\"EndLine\":585,\"ReplacementContent\":\"    // === PASO 3: FILTROS DE CALIDAD DE SE\u00d1AL ===\\n    double max_allowed_spread = MaxSpreadPips;\\n    string symbol_upper = _Symbol;\\n    StringToUpper(symbol_upper);\\n    if(StringFind(symbol_upper, \\\"XAU\\\") >= 0 || StringFind(symbol_upper, \\\"GOLD\\\") >= 0 || StringFind(symbol_upper, \\\"XAG\\\") >= 0) {\\n        max_allowed_spread = InpMaxSpreadPips_Metals;\\n    }\\n    \\n    if(spread > max_allowed_spread) {\\n        lastBarTime = currentBarTime;\\n        return;\\n    }\",\"StartLine\":584,\"TargetContent\":\"    // === PASO 3: FILTROS DE CALIDAD DE SE\u00d1AL ===\\n    if(spread > MaxSpreadPips) {\\n        lastBarTime = currentBarTime;\\n        return;\\n    }\"}]",
  "TargetFile": "\"C:\\\\Users\\\\Manuel\\\\Desktop\\\\HMA_MetaLabeling\\\\MQL5_Engine\\\\HMA_ML_Orchestrator.mq5\"",
  "toolAction": "\"Parcheando HMA_ML_Orchestrator.mq5\"",
  "toolSummary": "\"Patching HMA_ML_Orchestrator.mq5 for XAUUSD spread\""
}
```

## Step 5206 - Tool Response
```diff
@@ -39,8 +39,9 @@
 input int    RsiOverboughtLevel  = 65;
 
 input group "== Microestructura =="
-input double MaxSpreadPips       = 4.0;
-input int    InpDonchianPeriod   = 20;
+input double MaxSpreadPips          = 4.0;
+input double InpMaxSpreadPips_Metals = 35.0; // Spread máximo ampliado para XAUUSD/XAGUSD
+input int    InpDonchianPeriod      = 20;
 
 input group "== Gestion ML (Triple Barrera) =="
 input double InpInitialBalance   = 100000.0;
@@ -641,7 +641,14 @@
     }
 
     // === PASO 3: FILTROS DE CALIDAD DE SEÑAL ===
-    if(spread > MaxSpreadPips) {
+    double max_allowed_spread = MaxSpreadPips;
+    string symbol_upper = _Symbol;
+    StringToUpper(symbol_upper);
+    if(StringFind(symbol_upper, "XAU") >= 0 || StringFind(symbol_upper, "GOLD") >= 0 || StringFind(symbol_upper, "XAG") >= 0) {
+        max_allowed_spread = InpMaxSpreadPips_Metals;
+    }
+    
+    if(spread > max_allowed_spread) {
         lastBarTime = currentBarTime;
         return;
     }
```

## Step 5347 - Tool Call: multi_replace_file_content
**Instruction:** "Añadir _Symbol a GetHighestHigh, GetLowestLow y CalcPullbackMetrics en HMA_ML_Orchestrator.mq5"
**Description:** "Parcheando Orchestrator para usar el nuevo formato de HMA_FUNCTIONS"

```json
{
  "Description": "\"Parcheando Orchestrator para usar el nuevo formato de HMA_FUNCTIONS\"",
  "Instruction": "\"A\u00f1adir _Symbol a GetHighestHigh, GetLowestLow y CalcPullbackMetrics en HMA_ML_Orchestrator.mq5\"",
  "ReplacementChunks": "[{\"AllowMultiple\":false,\"EndLine\":679,\"ReplacementContent\":\"    double sl = GetHighestHigh(_Symbol, LookbackBars);   // SL para SELL\\n    if(signalType == 0) sl = GetLowestLow(_Symbol, LookbackBars);  // SL para BUY\",\"StartLine\":678,\"TargetContent\":\"    double sl = GetHighestHigh(LookbackBars);   // SL para SELL\\n    if(signalType == 0) sl = GetLowestLow(LookbackBars);  // SL para BUY\"},{\"AllowMultiple\":false,\"EndLine\":721,\"ReplacementContent\":\"    CalcPullbackMetrics(_Symbol, hma_handle, LookbackBars, current_atr, pb_duration, pb_depth);\",\"StartLine\":721,\"TargetContent\":\"    CalcPullbackMetrics(hma_handle, LookbackBars, current_atr, pb_duration, pb_depth);\"}]",
  "TargetFile": "\"C:\\\\Users\\\\Manuel\\\\Desktop\\\\HMA_MetaLabeling\\\\MQL5_Engine\\\\HMA_ML_Orchestrator.mq5\"",
  "toolAction": "\"Parcheando dependencias en Orchestrator\"",
  "toolSummary": "\"Fixing compilation errors in HMA_ML_Orchestrator.mq5\""
}
```

## Step 5348 - Tool Response
```diff
@@ -675,8 +675,8 @@
     double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
     double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
 
-    double sl = GetHighestHigh(LookbackBars);   // SL para SELL
-    if(signalType == 0) sl = GetLowestLow(LookbackBars);  // SL para BUY
+    double sl = GetHighestHigh(_Symbol, LookbackBars);   // SL para SELL
+    if(signalType == 0) sl = GetLowestLow(_Symbol, LookbackBars);  // SL para BUY
     if(sl == 0.0) { lastBarTime = currentBarTime; return; }
 
     double entry_price = bid;
@@ -717,7 +717,7 @@
 
     int    pb_duration = 0;
     double pb_depth    = 0.0;
-    CalcPullbackMetrics(hma_handle, LookbackBars, current_atr, pb_duration, pb_depth);
+    CalcPullbackMetrics(_Symbol, hma_handle, LookbackBars, current_atr, pb_duration, pb_depth);
 
     // dt ya declarado en Paso 2
     TimeToStruct(TimeCurrent(), dt);
```

## Step 5816 - Tool Call: write_to_file
**Description:** "Reestructuración del Orchestrator para el procesamiento de múltiples símbolos concurrentes"

```json
{
  "CodeContent": "\"//+------------------------------------------------------------------+\\n//|                                          HMA_ML_Orchestrator.mq5 |\\n//|        Mass Data Harvester (Meta-Labeling v2.3 - Fase 23)        |\\n//|        Autor: Manuel                                             |\\n//|        Multi-S\u00edmbolo, As\u00edncrono, Orientado a Objetos (OOP)       |\\n//+------------------------------------------------------------------+\\n#property strict\\n#property version \\\"2.3\\\"\\n#property description \\\"HMA Meta-Labeling Mass Data Harvester\\\"\\n\\n#include <Trade\\\\Trade.mqh>\\n#include \\\"ML_Logger.mqh\\\"\\n#include \\\"HMA_FUNCTIONS.mqh\\\"\\n\\nCTrade trade;\\n\\nstatic const double FIXED_LOT = 0.01;\\n\\n//+------------------------------------------------------------------+\\n//| Parametros de Entrada                                            |\\n//+------------------------------------------------------------------+\\ninput string InpHarvestSymbols = \\\"AUDUSD,USDCAD,USDCHF,NZDUSD,EURGBP,EURAUD,GBPAUD,GBPCAD,AUDJPY,CHFJPY,US30,NAS100,XAGUSD\\\";\\n\\ninput group \\\"== Estrategia HMA ==\\\"\\ninput int    HMAPeriod           = 50;\\ninput int    InpHMA_ExitPeriod   = 100;\\ninput int    InpMinBarsToHold    = 3;\\ninput int    LookbackBars        = 7;\\ninput double AntiNoiseATRPct     = 2.0;\\n\\ninput group \\\"== Contexto y Features ==\\\"\\ninput int    RsiPeriod           = 14;\\ninput int    RsiLookbackBars     = 15;\\ninput int    RsiOversoldLevel    = 35;\\ninput int    RsiOverboughtLevel  = 65;\\n\\ninput group \\\"== Microestructura ==\\\"\\ninput double MaxSpreadPips          = 4.0;\\ninput double InpMaxSpreadPips_Metals = 35.0; // Spread m\u00e1ximo ampliado para XAUUSD/XAGUSD/Indices\\ninput int    InpDonchianPeriod      = 20;\\n\\ninput group \\\"== Gestion ML (Triple Barrera) ==\\\"\\ninput double InpInitialBalance   = 100000.0;\\ninput double TakeProfitMultiplier = 3.0;\\ninput double InpScaleOutRR       = 1.5;  \\ninput int    InpFastHMA_Exit_Period = 14; \\n\\ninput group \\\"== Filtros Macro / Cisnes Negros ==\\\"\\ninput double InpMaxSignalBarATR  = 2.5;\\ninput doubl\n<truncated 36229 bytes>",
  "Description": "\"Reestructuraci\u00f3n del Orchestrator para el procesamiento de m\u00faltiples s\u00edmbolos concurrentes\"",
  "IsArtifact": "false",
  "Overwrite": "true",
  "TargetFile": "\"C:\\\\Users\\\\Manuel\\\\Desktop\\\\HMA_MetaLabeling\\\\MQL5_Engine\\\\HMA_ML_Orchestrator.mq5\"",
  "toolAction": "\"Refactorizando Orchestrator MQL5\"",
  "toolSummary": "\"Rewriting HMA_ML_Orchestrator.mq5 to encapsulate the logic inside CHarvestManager, utilizing EventTimer to process multiple symbols asynchronously\""
}
```

## Step 5817 - Tool Response
```
Created At: 2026-06-08T14:31:54Z
Completed At: 2026-06-08T14:31:54Z
Created file file:///C:/Users/Manuel/Desktop/HMA_MetaLabeling/MQL5_Engine/HMA_ML_Orchestrator.mq5 with requested content.
If relevant, proactively run terminal commands to execute this code for the USER. Don't ask for permission....
```

## Step 5839 - Tool Call: multi_replace_file_content
**Instruction:** "Change the argument name 'input' to 'inStr' in SplitString function"
**Description:** "Fixing MQL5 syntax errors caused by using reserved keyword 'input' as a variable name"

```json
{
  "Description": "\"Fixing MQL5 syntax errors caused by using reserved keyword 'input' as a variable name\"",
  "Instruction": "\"Change the argument name 'input' to 'inStr' in SplitString function\"",
  "ReplacementChunks": "[{\"AllowMultiple\":false,\"EndLine\":64,\"ReplacementContent\":\"int SplitString(const string inStr, const string sep, string &result[]) {\\n    int count = StringSplit(inStr, StringGetCharacter(sep, 0), result);\\n    for (int i=0; i<count; i++) {\\n        StringTrimLeft(result[i]);\\n        StringTrimRight(result[i]);\\n    }\\n    return count;\\n}\",\"StartLine\":58,\"TargetContent\":\"int SplitString(const string input, const string sep, string &result[]) {\\n    int count = StringSplit(input, StringGetCharacter(sep, 0), result);\\n    for (int i=0; i<count; i++) {\\n        StringTrimLeft(result[i]);\\n        StringTrimRight(result[i]);\\n    }\\n    return count;\\n}\"}]",
  "TargetFile": "\"C:\\\\Users\\\\Manuel\\\\Desktop\\\\HMA_MetaLabeling\\\\MQL5_Engine\\\\HMA_ML_Orchestrator.mq5\"",
  "toolAction": "\"Corrigiendo keyword input\"",
  "toolSummary": "\"Fixing the 'unexpected token' error by renaming the 'input' argument to 'inStr' in the SplitString function\""
}
```

## Step 5840 - Tool Response
```diff
@@ -55,8 +55,8 @@
 //+------------------------------------------------------------------+
 //| Helper: String Split                                             |
 //+------------------------------------------------------------------+
-int SplitString(const string input, const string sep, string &result[]) {
-    int count = StringSplit(input, StringGetCharacter(sep, 0), result);
+int SplitString(const string inStr, const string sep, string &result[]) {
+    int count = StringSplit(inStr, StringGetCharacter(sep, 0), result);
     for (int i=0; i<count; i++) {
         StringTrimLeft(result[i]);
         StringTrimRight(result[i]);
```

## Step 5857 - Tool Call: multi_replace_file_content
**Instruction:** "Reemplazar el bucle de inicialización en OnInit para validar con SymbolSelect antes de crear CHarvestManager"
**Description:** "Añadiendo validación de símbolos en OnInit para evitar cuelgues del Tester con símbolos inválidos o faltantes."

```json
{
  "Description": "\"A\u00f1adiendo validaci\u00f3n de s\u00edmbolos en OnInit para evitar cuelgues del Tester con s\u00edmbolos inv\u00e1lidos o faltantes.\"",
  "Instruction": "\"Reemplazar el bucle de inicializaci\u00f3n en OnInit para validar con SymbolSelect antes de crear CHarvestManager\"",
  "ReplacementChunks": "[{\"AllowMultiple\":false,\"EndLine\":691,\"ReplacementContent\":\"    int valid_managers = 0;\\n    ArrayResize(Managers, count);\\n    for(int i=0; i<count; i++) {\\n        ResetLastError();\\n        if(SymbolSelect(symbols[i], true)) {\\n            Managers[valid_managers] = new CHarvestManager(symbols[i]);\\n            valid_managers++;\\n        } else {\\n            PrintFormat(\\\"[WARN] S\u00edmbolo %s inv\u00e1lido o no soportado por el Broker/Tester. Ignorando.\\\", symbols[i]);\\n        }\\n    }\\n\\n    if(valid_managers == 0) {\\n        Print(\\\"ERROR CR\u00cdTICO: Ning\u00fan s\u00edmbolo v\u00e1lido para operar.\\\");\\n        return INIT_FAILED;\\n    }\\n\\n    ArrayResize(Managers, valid_managers);\\n\\n    EventSetMillisecondTimer(500);\\n    PrintFormat(\\\"[INIT] Harvester Listo. Simbolos Activos: %d / %d | Timer: 500ms\\\", valid_managers, count);\\n\\n    return(INIT_SUCCEEDED);\",\"StartLine\":683,\"TargetContent\":\"    ArrayResize(Managers, count);\\n    for(int i=0; i<count; i++) {\\n        Managers[i] = new CHarvestManager(symbols[i]);\\n    }\\n\\n    EventSetMillisecondTimer(500);\\n    PrintFormat(\\\"[INIT] Harvester Listo. Simbolos: %d | Timer: 500ms\\\", count);\\n\\n    return(INIT_SUCCEEDED);\"}]",
  "TargetFile": "\"C:\\\\Users\\\\Manuel\\\\Desktop\\\\HMA_MetaLabeling\\\\MQL5_Engine\\\\HMA_ML_Orchestrator.mq5\"",
  "toolAction": "\"Evitando cuelgues del Tester\"",
  "toolSummary": "\"Fixing the Strategy Tester crash by validating that symbols exist before calling iCustom inside CHarvestManager\""
}
```

## Step 5858 - Tool Response
```diff
@@ -680,13 +680,27 @@
         return INIT_FAILED;
     }
 
+    int valid_managers = 0;
     ArrayResize(Managers, count);
     for(int i=0; i<count; i++) {
-        Managers[i] = new CHarvestManager(symbols[i]);
-    }
+        ResetLastError();
+        if(SymbolSelect(symbols[i], true)) {
+            Managers[valid_managers] = new CHarvestManager(symbols[i]);
+            valid_managers++;
+        } else {
+            PrintFormat("[WARN] Símbolo %s inválido o no soportado por el Broker/Tester. Ignorando.", symbols[i]);
+        }
+    }
+
+    if(valid_managers == 0) {
+        Print("ERROR CRÍTICO: Ningún símbolo válido para operar.");
+        return INIT_FAILED;
+    }
+
+    ArrayResize(Managers, valid_managers);
 
     EventSetMillisecondTimer(500);
-    PrintFormat("[INIT] Harvester Listo. Simbolos: %d | Timer: 500ms", count);
+    PrintFormat("[INIT] Harvester Listo. Simbolos Activos: %d / %d | Timer: 500ms", valid_managers, count);
 
     return(INIT_SUCCEEDED);
 }
```

## Step 6567 - Tool Response
```diff
@@ -588,7 +588,8 @@
 
         m_lastBarTime = currentBarTime;  // Bloquear antes de lanzar orden
 
-        if(trade.PositionOpen(m_symbol, (ENUM_ORDER_TYPE)signalType, FIXED_LOT, entry_price, sl, 0.0, "HMA_ML")) {
+        double min_volume = SymbolInfoDouble(m_symbol, SYMBOL_VOLUME_MIN);
+        if(trade.PositionOpen(m_symbol, (ENUM_ORDER_TYPE)signalType, min_volume, entry_price, sl, 0.0, "HMA_ML")) {
             ulong pos_ticket = trade.ResultDeal();
             double real_entry = trade.ResultPrice();
             if(real_entry <= 0.0) real_entry = entry_price;
```

## Step 6663 - Tool Call: multi_replace_file_content
**Instruction:** "Modify the spread logic in HMA_ML_Orchestrator.mq5. Add a bypass for all indices (US30, US500, NAS, SPX, DE40) setting max_allowed_spread = 99999.0. Indices have wildly different point scalings across brokers, and a fixed pip limit will randomly block 100% of trades after a certain date if the broker changes the contract specifications. The Machine Learning pipeline will naturally discard toxic spread regimes anyway via the Spread_Impact_Ratio feature."
**Description:** "Parche para el filtro de spread estricto en Índices"

```json
{
  "Description": "\"Parche para el filtro de spread estricto en \u00cdndices\"",
  "Instruction": "\"Modify the spread logic in HMA_ML_Orchestrator.mq5. Add a bypass for all indices (US30, US500, NAS, SPX, DE40) setting max_allowed_spread = 99999.0. Indices have wildly different point scalings across brokers, and a fixed pip limit will randomly block 100% of trades after a certain date if the broker changes the contract specifications. The Machine Learning pipeline will naturally discard toxic spread regimes anyway via the Spread_Impact_Ratio feature.\"",
  "ReplacementChunks": "[{\"AllowMultiple\":false,\"EndLine\":513,\"ReplacementContent\":\"        bool is_metal = (StringFind(symbol_upper, \\\"XAU\\\") >= 0 || StringFind(symbol_upper, \\\"GOLD\\\") >= 0 || StringFind(symbol_upper, \\\"XAG\\\") >= 0);\\n        bool is_index = (StringFind(symbol_upper, \\\"US30\\\") >= 0 || StringFind(symbol_upper, \\\"NAS\\\") >= 0 || StringFind(symbol_upper, \\\"US500\\\") >= 0 || StringFind(symbol_upper, \\\"SPX\\\") >= 0 || StringFind(symbol_upper, \\\"DE40\\\") >= 0 || StringFind(symbol_upper, \\\"DJI\\\") >= 0);\\n        \\n        if(is_metal) {\\n            max_allowed_spread = InpMaxSpreadPips_Metals;\\n        } else if (is_index) {\\n            max_allowed_spread = 99999.0; // By-pass spread filter for indices. ML will learn toxic spread impact.\\n        }\",\"StartLine\":511,\"TargetContent\":\"        if(StringFind(symbol_upper, \\\"XAU\\\") >= 0 || StringFind(symbol_upper, \\\"GOLD\\\") >= 0 || StringFind(symbol_upper, \\\"XAG\\\") >= 0 || StringFind(symbol_upper, \\\"US30\\\") >= 0 || StringFind(symbol_upper, \\\"NAS\\\") >= 0) {\\n            max_allowed_spread = InpMaxSpreadPips_Metals;\\n        }\"}]",
  "TargetFile": "\"C:\\\\Users\\\\Manuel\\\\Desktop\\\\HMA_MetaLabeling\\\\Alpha_Sniper_Vault\\\\mql5\\\\HMA_ML_Orchestrator.mq5\"",
  "toolAction": "\"Actualizando filtro de spread MQL5\"",
  "toolSummary": "\"Updating the MQL5 Harvester code to bypass the strict max_allowed_spread filter for indices like US30 and US500, as varying broker point scalings were prematurely terminating data harvesting after 2018\""
}
```

## Step 6664 - Tool Response
```diff
@@ -508,8 +508,13 @@
         double max_allowed_spread = MaxSpreadPips;
         string symbol_upper = m_symbol;
         StringToUpper(symbol_upper);
-        if(StringFind(symbol_upper, "XAU") >= 0 || StringFind(symbol_upper, "GOLD") >= 0 || StringFind(symbol_upper, "XAG") >= 0 || StringFind(symbol_upper, "US30") >= 0 || StringFind(symbol_upper, "NAS") >= 0) {
+        bool is_metal = (StringFind(symbol_upper, "XAU") >= 0 || StringFind(symbol_upper, "GOLD") >= 0 || StringFind(symbol_upper, "XAG") >= 0);
+        bool is_index = (StringFind(symbol_upper, "US30") >= 0 || StringFind(symbol_upper, "NAS") >= 0 || StringFind(symbol_upper, "US500") >= 0 || StringFind(symbol_upper, "SPX") >= 0 || StringFind(symbol_upper, "DE40") >= 0 || StringFind(symbol_upper, "DJI") >= 0);
+        
+        if(is_metal) {
             max_allowed_spread = InpMaxSpreadPips_Metals;
+        } else if (is_index) {
+            max_allowed_spread = 99999.0; // By-pass spread filter for indices. ML will learn toxic spread impact.
         }
         
         if(spread > max_allowed_spread) {
```

## Step 7322 - Tool Call: multi_replace_file_content
**Instruction:** "Refactorizar HMA_ML_Orchestrator.mq5 para obtener y exportar dt_utc.hour y dt_utc.day_of_week."
**Description:** "Calculando dt_utc dinámicamente y usándolo para hour_of_day, day_of_week y session_time en MQL5"

```json
{
  "Description": "\"Calculando dt_utc din\u00e1micamente y us\u00e1ndolo para hour_of_day, day_of_week y session_time en MQL5\"",
  "Instruction": "\"Refactorizar HMA_ML_Orchestrator.mq5 para obtener y exportar dt_utc.hour y dt_utc.day_of_week.\"",
  "ReplacementChunks": "[{\"AllowMultiple\":false,\"EndLine\":421,\"ReplacementContent\":\"        MqlDateTime dt;\\n        TimeToStruct(currentBarTime, dt);\\n\\n        int gmt_offset = (int)(TimeCurrent() - TimeGMT());\\n        MqlDateTime dt_utc;\\n        TimeToStruct(currentBarTime - gmt_offset, dt_utc);\\n\",\"StartLine\":419,\"TargetContent\":\"        MqlDateTime dt;\\n        TimeToStruct(currentBarTime, dt);\\n\"},{\"AllowMultiple\":false,\"EndLine\":567,\"ReplacementContent\":\"        int h = dt_utc.hour;\",\"StartLine\":567,\"TargetContent\":\"        int h = dt.hour;\"},{\"AllowMultiple\":false,\"EndLine\":631,\"ReplacementContent\":\"            snap.hour_of_day = dt_utc.hour;\",\"StartLine\":631,\"TargetContent\":\"            snap.hour_of_day = dt.hour;\"},{\"AllowMultiple\":false,\"EndLine\":640,\"ReplacementContent\":\"            snap.day_of_week = dt_utc.day_of_week;\",\"StartLine\":640,\"TargetContent\":\"            snap.day_of_week = dt.day_of_week;\"}]",
  "TargetFile": "\"c:\\\\Users\\\\Manuel\\\\Desktop\\\\HMA_MetaLabeling\\\\Alpha_Sniper_Vault\\\\mql5\\\\HMA_ML_Orchestrator.mq5\"",
  "toolAction": "\"Editing HMA_ML_Orchestrator.mq5\"",
  "toolSummary": "\"Update UTC time logic in MQL5\""
}
```

## Step 7323 - Tool Response
```diff
@@ -419,6 +419,10 @@
         MqlDateTime dt;
         TimeToStruct(currentBarTime, dt);
 
+        int gmt_offset = (int)(TimeCurrent() - TimeGMT());
+        MqlDateTime dt_utc;
+        TimeToStruct(currentBarTime - gmt_offset, dt_utc);
+
         MqlDateTime dt_start = dt;
         dt_start.hour = 0; dt_start.min = 0; dt_start.sec = 0;
         datetime asian_start = StructToTime(dt_start);
@@ -563,7 +563,7 @@
         int pb_duration = 0; double pb_depth = 0.0;
         CalcPullbackMetrics(m_symbol, hma_handle, LookbackBars, current_atr, pb_duration, pb_depth);
 
-        int h = dt.hour;
+        int h = dt_utc.hour;
         int session_time = 1;
         if(h >= 13) session_time = (h <= 14) ? 0 : ((h <= 20) ? 3 : 1);
         else if(h >= 7) session_time = 2;
@@ -626,7 +626,7 @@
             snap.sl_dist_price = real_slDist;
             snap.spread_pips = spread;
             snap.sl_pips_reales = real_sl_pips;
-            snap.hour_of_day = dt.hour;
+            snap.hour_of_day = dt_utc.hour;
             snap.session_time = session_time;
             snap.h4_trend_align = h4_trend_align;
             snap.vol_spread_ratio = (atr_sma50 > 0) ? (current_atr / atr_sma50) : 1.0;
@@ -634,7 +634,7 @@
             snap.spread_impact_ratio = (real_sl_pips > 0) ? (spread / real_sl_pips) : 0.0;
             snap.hma_distance_ema = hma_distance_ema;
             snap.breakout_body_ratio = (candle_range > 0) ? (candle_body / candle_range) : 0.0;
-            snap.day_of_week = dt.day_of_week;
+            snap.day_of_week = dt_utc.day_of_week;
             snap.hma_velocity = hma_vel;
             snap.hma_acceleration_raw = hma_accel_v2;
             snap.hma_jerk = hma_jerk_val;
```

## Step 7413 - Tool Response
```diff
@@ -12,7 +12,8 @@
   - Crear `README.md` y `.gitignore` para `Alpha_Sniper_Vault`.
   - Crear `README.md` y `.gitignore` para `Alpha_Sniper_Showcase`.
 
-- `[ ]` Re-Cosecha (Acción de Usuario):
-  - Compilar `HMA_ML_Orchestrator.mq5`.
-  - Correr sobre los activos *The Master 8* en un broker desde el 2015.
+- `[x]` Re-Cosecha y Entrenamiento Unificado:
+  - Generación de CSVs en UTC completada por el orquestador.
+  - Ejecución de `run_all_assets.py` exitosa.
+  - Generación de Modelos Universales XGBoost, Umbrales y Clusters (K-Means) para *The Master 8*.
```

## Step 8048 - Tool Call: multi_replace_file_content
**Instruction:** "Remove index bypass logic"
**Description:** "Revert index additions in orchestrator"

```json
{
  "Description": "\"Revert index additions in orchestrator\"",
  "Instruction": "\"Remove index bypass logic\"",
  "ReplacementChunks": "[{\"AllowMultiple\":false,\"EndLine\":23,\"ReplacementContent\":\"input string InpHarvestSymbols = \\\"AUDUSD,USDCAD,USDCHF,NZDUSD,EURGBP,EURAUD,GBPAUD,GBPCAD,AUDJPY,CHFJPY\\\";\",\"StartLine\":22,\"TargetContent\":\"input string InpHarvestSymbols = \\\"AUDUSD,USDCAD,USDCHF,NZDUSD,EURGBP,EURAUD,GBPAUD,GBPCAD,AUDJPY,CHFJPY,US30,NAS100,XAGUSD\\\";\"},{\"AllowMultiple\":false,\"EndLine\":39,\"ReplacementContent\":\"input double InpMaxSpreadPips_Metals = 35.0; // Spread m\u00e1ximo ampliado para XAUUSD/XAGUSD\",\"StartLine\":39,\"TargetContent\":\"input double InpMaxSpreadPips_Metals = 35.0; // Spread m\u00e1ximo ampliado para XAUUSD/XAGUSD/Indices\"},{\"AllowMultiple\":false,\"EndLine\":524,\"ReplacementContent\":\"        double max_allowed_spread = MaxSpreadPips;\\n        string symbol_upper = m_symbol;\\n        StringToUpper(symbol_upper);\\n        bool is_metal = (StringFind(symbol_upper, \\\"XAU\\\") >= 0 || StringFind(symbol_upper, \\\"GOLD\\\") >= 0 || StringFind(symbol_upper, \\\"XAG\\\") >= 0);\\n        \\n        if(is_metal) {\\n            max_allowed_spread = InpMaxSpreadPips_Metals;\\n        }\\n        \\n        if(spread > max_allowed_spread) {\",\"StartLine\":512,\"TargetContent\":\"        double max_allowed_spread = MaxSpreadPips;\\n        string symbol_upper = m_symbol;\\n        StringToUpper(symbol_upper);\\n        bool is_metal = (StringFind(symbol_upper, \\\"XAU\\\") >= 0 || StringFind(symbol_upper, \\\"GOLD\\\") >= 0 || StringFind(symbol_upper, \\\"XAG\\\") >= 0);\\n        bool is_index = (StringFind(symbol_upper, \\\"US30\\\") >= 0 || StringFind(symbol_upper, \\\"NAS\\\") >= 0 || StringFind(symbol_upper, \\\"US500\\\") >= 0 || StringFind(symbol_upper, \\\"SPX\\\") >= 0 || StringFind(symbol_upper, \\\"DE40\\\") >= 0 || StringFind(symbol_upper, \\\"DJI\\\") >= 0);\\n        \\n        if(is_metal) {\\n            max_allowed_spread = InpMaxSpreadPips_Metals;\\n        } else if (is_index) {\\n            max_allowed_spread = 99999.0; // By-pass spread filter for indices. ML will learn toxic spread impact.\\n        }\\n        \\n        if(spread > max_allowed_spread) {\"}]",
  "TargetFile": "\"c:\\\\Users\\\\Manuel\\\\Desktop\\\\HMA_MetaLabeling\\\\Alpha_Sniper_Vault\\\\mql5\\\\HMA_ML_Orchestrator.mq5\"",
  "toolAction": "\"Modifying HMA_ML_Orchestrator.mq5\"",
  "toolSummary": "\"Revert index logic orchestrator\""
}
```

## Step 8049 - Tool Response
```diff
@@ -19,7 +19,7 @@
 //+------------------------------------------------------------------+
 //| Parametros de Entrada                                            |
 //+------------------------------------------------------------------+
-input string InpHarvestSymbols = "AUDUSD,USDCAD,USDCHF,NZDUSD,EURGBP,EURAUD,GBPAUD,GBPCAD,AUDJPY,CHFJPY,US30,NAS100,XAGUSD";
+input string InpHarvestSymbols = "AUDUSD,USDCAD,USDCHF,NZDUSD,EURGBP,EURAUD,GBPAUD,GBPCAD,AUDJPY,CHFJPY";
 
 input group "== Estrategia HMA =="
 input int    HMAPeriod           = 50;
@@ -35,7 +35,7 @@
 
 input group "== Microestructura =="
 input double MaxSpreadPips          = 4.0;
-input double InpMaxSpreadPips_Metals = 35.0; // Spread máximo ampliado para XAUUSD/XAGUSD/Indices
+input double InpMaxSpreadPips_Metals = 35.0; // Spread máximo ampliado para XAUUSD/XAGUSD
 input int    InpDonchianPeriod      = 20;
 
 input group "== Gestion ML (Triple Barrera) =="
@@ -511,12 +511,9 @@
         string symbol_upper = m_symbol;
         StringToUpper(symbol_upper);
         bool is_metal = (StringFind(symbol_upper, "XAU") >= 0 || StringFind(symbol_upper, "GOLD") >= 0 || StringFind(symbol_upper, "XAG") >= 0);
-        bool is_index = (StringFind(symbol_upper, "US30") >= 0 || StringFind(symbol_upper, "NAS") >= 0 || StringFind(symbol_upper, "US500") >= 0 || StringFind(symbol_upper, "SPX") >= 0 || StringFind(symbol_upper, "DE40") >= 0 || StringFind(symbol_upper, "DJI") >= 0);
         
         if(is_metal) {
             max_allowed_spread = InpMaxSpreadPips_Metals;
-        } else if (is_index) {
-            max_allowed_spread = 99999.0; // By-pass spread filter for indices. ML will learn toxic spread impact.
         }
         
         if(spread > max_allowed_spread) {
```

## Step 8240 - Tool Call: multi_replace_file_content
**Instruction:** "Replace the default value of InpHarvestSymbols with the validated Macro 6 portfolio assets"
**Description:** "Set default portfolio assets in Orchestrator"

```json
{
  "Description": "\"Set default portfolio assets in Orchestrator\"",
  "Instruction": "\"Replace the default value of InpHarvestSymbols with the validated Macro 6 portfolio assets\"",
  "ReplacementChunks": "[{\"AllowMultiple\":false,\"EndLine\":22,\"ReplacementContent\":\"input string InpHarvestSymbols = \\\"USDJPY,GBPUSD,EURUSD,EURJPY,XAUUSD,XAGUSD\\\";\",\"StartLine\":22,\"TargetContent\":\"input string InpHarvestSymbols = \\\"AUDUSD,USDCAD,USDCHF,NZDUSD,EURGBP,EURAUD,GBPAUD,GBPCAD,AUDJPY,CHFJPY\\\";\"}]",
  "TargetFile": "\"c:\\\\Users\\\\Manuel\\\\Desktop\\\\HMA_MetaLabeling\\\\Alpha_Sniper_Vault\\\\mql5\\\\HMA_ML_Orchestrator.mq5\"",
  "toolAction": "\"Setting default Orchestrator symbols\"",
  "toolSummary": "\"Update InpHarvestSymbols in Orchestrator\""
}
```

## Step 8241 - Tool Response
```diff
@@ -19,7 +19,7 @@
 //+------------------------------------------------------------------+
 //| Parametros de Entrada                                            |
 //+------------------------------------------------------------------+
-input string InpHarvestSymbols = "AUDUSD,USDCAD,USDCHF,NZDUSD,EURGBP,EURAUD,GBPAUD,GBPCAD,AUDJPY,CHFJPY";
+input string InpHarvestSymbols = "USDJPY,GBPUSD,EURUSD,EURJPY,XAUUSD,XAGUSD";
 
 input group "== Estrategia HMA =="
 input int    HMAPeriod           = 50;
```

## Step 8469 - Tool Call: multi_replace_file_content
**Instruction:** "Insert FileDelete calls in the initialization loop of the Orchestrator."
**Description:** "Add FileDelete in OnInit to clear old datasets"

```json
{
  "Description": "\"Add FileDelete in OnInit to clear old datasets\"",
  "Instruction": "\"Insert FileDelete calls in the initialization loop of the Orchestrator.\"",
  "ReplacementChunks": "[{\"AllowMultiple\":false,\"EndLine\":696,\"ReplacementContent\":\"    int valid_managers = 0;\\n    ArrayResize(Managers, count);\\n    for(int i=0; i<count; i++) {\\n        ResetLastError();\\n        if(SymbolSelect(symbols[i], true)) {\\n            FileDelete(\\\"Struct_Dataset_\\\" + symbols[i] + \\\".csv\\\", FILE_COMMON);\\n            FileDelete(\\\"Struct_Exit_Dataset_\\\" + symbols[i] + \\\".csv\\\", FILE_COMMON);\\n            Managers[valid_managers] = new CHarvestManager(symbols[i]);\\n            valid_managers++;\",\"StartLine\":690,\"TargetContent\":\"    int valid_managers = 0;\\n    ArrayResize(Managers, count);\\n    for(int i=0; i<count; i++) {\\n        ResetLastError();\\n        if(SymbolSelect(symbols[i], true)) {\\n            Managers[valid_managers] = new CHarvestManager(symbols[i]);\\n            valid_managers++;\"}]",
  "TargetFile": "\"C:\\\\Users\\\\Manuel\\\\Desktop\\\\HMA_MetaLabeling\\\\Alpha_Sniper_Vault\\\\mql5\\\\HMA_ML_Orchestrator.mq5\"",
  "toolAction": "\"Adding FileDelete to Orchestrator\"",
  "toolSummary": "\"Update Orchestrator file initialization\""
}
```

## Step 8470 - Tool Response
```diff
@@ -692,6 +692,8 @@
     for(int i=0; i<count; i++) {
         ResetLastError();
         if(SymbolSelect(symbols[i], true)) {
+            FileDelete("Struct_Dataset_" + symbols[i] + ".csv", FILE_COMMON);
+            FileDelete("Struct_Exit_Dataset_" + symbols[i] + ".csv", FILE_COMMON);
             Managers[valid_managers] = new CHarvestManager(symbols[i]);
             valid_managers++;
         } else {
```

