import re
import subprocess
import shutil

source_path = r"C:\Users\Manuel\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Experts\Alpha_Sniper\Alpha_Sniper_Master6.mq5"
onnx_path = r"C:\Users\Manuel\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Experts\Alpha_Sniper\Alpha_Sniper_Master6_ONNX.mq5"

shutil.copyfile(source_path, onnx_path)

with open(onnx_path, "r", encoding="utf-8") as f:
    text = f.read()

# INJECT ONNX DIRECTIVES
onnx_globals = """
#resource "FatTail_Model.onnx" as const uchar ExtModel[]
long onnx_handle = INVALID_HANDLE;
input bool InpUseMLFilter = true; // [IA] Usar filtro Fat-Tail ONNX
bool ML_Active = false;
"""
text = text.replace('int csv_handle = INVALID_HANDLE;', 'int csv_handle = INVALID_HANDLE;\n' + onnx_globals)

# INJECT ONNX INIT
onnx_init = """
    if(InpUseMLFilter) {
        onnx_handle = OnnxCreateFromBuffer(ExtModel, ONNX_DEFAULT);
        if(onnx_handle == INVALID_HANDLE) {
            Print("ERROR: No se pudo cargar FatTail_Model.onnx. ML Desactivado.");
        } else {
            const long input_shape[] = {1, 9};
            OnnxSetInputShape(onnx_handle, 0, input_shape);
            const long output_shape[] = {1};
            OnnxSetOutputShape(onnx_handle, 0, output_shape);
            ML_Active = true;
        }
    }
"""
text = text.replace('if(InpExportMetaLabeling && MQLInfoInteger(MQL_TESTER)) {', onnx_init + '\n    if(InpExportMetaLabeling && MQLInfoInteger(MQL_TESTER)) {')

# INJECT ONNX DEINIT
text = text.replace('if(csv_handle != INVALID_HANDLE) FileClose(csv_handle);', 'if(csv_handle != INVALID_HANDLE) FileClose(csv_handle);\n    if(onnx_handle != INVALID_HANDLE) OnnxRelease(onnx_handle);')

# INJECT ONNX INFERENCE
onnx_inference = """
          // --- ML FAT-TAIL INFERENCE ---
          bool ml_approved = true;
          if(ML_Active && onnx_handle != INVALID_HANDLE) {
              float features[9];
              features[0] = (float)signal;
              features[1] = (float)current_rsi;
              features[2] = (float)dist_ema_atr;
              features[3] = (float)breakout_atr;
              features[4] = valid_buildup ? 1.0f : 0.0f;
              features[5] = (float)impulse_atr;
              features[6] = (float)loss_streak;
              features[7] = (float)(candle_size / current_atr);
              features[8] = (float)atr_d1[1];
              
              long ml_prediction[1];
              if(OnnxRun(onnx_handle, ONNX_NO_CONVERSION, features, ml_prediction)) {
                  if(ml_prediction[0] == 0) {
                      ml_approved = false;
                      Print("ML Filter: Operacion bloqueada por XGBoost (Ruido esperado).");
                  } else {
                      Print("ML Filter: FAT-TAIL IDENTIFICADO. Aprobando operacion.");
                  }
              } else {
                  Print("ERROR: OnnxRun fallo. Operacion aprobada por defecto.");
              }
          }
          
          if(ml_approved && lots > 0) {
"""

text = text.replace('if(lots > 0) {', onnx_inference)

with open(onnx_path, "w", encoding="utf-8") as f:
    f.write(text)

metaeditor = r"C:\Program Files\MetaTrader 5\metaeditor64.exe"
log_path = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\comp_onnx2.log"
subprocess.run([metaeditor, f"/compile:{onnx_path}", f"/log:{log_path}"], capture_output=True)

try:
    with open(log_path, "r", encoding="utf-16") as f:
        print(f.read())
except Exception as e:
    print(f"Log error: {e}")