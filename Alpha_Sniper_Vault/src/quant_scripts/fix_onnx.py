import re
import subprocess

onnx_path = r"C:\Users\Manuel\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Experts\Alpha_Sniper\Alpha_Sniper_Master6_ONNX.mq5"

with open(onnx_path, "r", encoding="utf-8") as f:
    text = f.read()

# Fix Init
old_init = """            const long output_shape[] = {1};
            OnnxSetOutputShape(onnx_handle, 0, output_shape);
            ML_Active = true;"""

new_init = """            const long output_shape[] = {1};
            OnnxSetOutputShape(onnx_handle, 0, output_shape);
            const long output_shape_prob[] = {1, 2};
            OnnxSetOutputShape(onnx_handle, 1, output_shape_prob);
            ML_Active = true;"""

text = text.replace(old_init, new_init)

# Fix Inference
old_run = """              long ml_prediction[1];
              if(OnnxRun(onnx_handle, ONNX_NO_CONVERSION, features, ml_prediction)) {"""

new_run = """              long ml_prediction[1];
              float ml_probabilities[2];
              if(OnnxRun(onnx_handle, ONNX_NO_CONVERSION, features, ml_prediction, ml_probabilities)) {"""

text = text.replace(old_run, new_run)

with open(onnx_path, "w", encoding="utf-8") as f:
    f.write(text)

metaeditor = r"C:\Program Files\MetaTrader 5\metaeditor64.exe"
log_path = r"C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\comp_onnx_fix.log"
subprocess.run([metaeditor, f"/compile:{onnx_path}", f"/log:{log_path}"], capture_output=True)

try:
    with open(log_path, "r", encoding="utf-16") as f:
        print(f.read())
except Exception as e:
    print(f"Log error: {e}")