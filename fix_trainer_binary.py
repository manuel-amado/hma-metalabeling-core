filepath = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\training\train_wfo_v19.py'
with open(filepath, 'r') as f:
    content = f.read()

import re

old_gen = '''def generate_tree_code(booster, features, scaler, func_name):
    code = f"double {func_name}(double &raw_f[]) {{\\n    double f[29];\\n"
    for i, col in enumerate(features):
        mean = scaler.center_[i]
        scale = scaler.scale_[i]
        code += f"    f[{i}] = (raw_f[{i}] - ({mean})) / {scale};\\n"
    code += "\\n    double sum = 0.0;\\n\\n"
    tree_df = booster.trees_to_dataframe()
    for tree_id in tree_df['Tree'].unique():
        code += f"    // Tree {tree_id}\\n"
        code += build_node(f"{tree_id}-0", 1, tree_df, features)
        code += "\\n"
    code += "    return 1.0 / (1.0 + MathExp(-(sum + 0.5)));\\n}\\n"
    return code'''

new_gen = '''def generate_tree_code(booster, features, scaler, func_name):
    import json
    import math
    code = f"double {func_name}(double &raw_f[]) {{\\n    double f[29];\\n"
    for i, col in enumerate(features):
        mean = scaler.center_[i]
        scale = scaler.scale_[i]
        code += f"    f[{i}] = (raw_f[{i}] - ({mean})) / {scale};\\n"
    code += "\\n    double sum = 0.0;\\n\\n"
    tree_df = booster.trees_to_dataframe()
    for tree_id in tree_df['Tree'].unique():
        code += f"    // Tree {tree_id}\\n"
        code += build_node(f"{tree_id}-0", 1, tree_df, features)
        code += "\\n"
        
    bs_str = json.loads(booster.save_config())['learner']['learner_model_param']['base_score']
    bs_val = float(bs_str[0]) if isinstance(bs_str, list) else float(bs_str.strip('[]'))
    # convert probability to log odds margin
    margin = 0.0 if bs_val == 0.5 else -math.log(1.0 / bs_val - 1.0)
    code += f"    return 1.0 / (1.0 + MathExp(-(sum + ({margin}))));\\n}}\\n"
    return code'''

content = content.replace(old_gen, new_gen)
with open(filepath, 'w') as f:
    f.write(content)
print("Binary Transpiler Fixed")
