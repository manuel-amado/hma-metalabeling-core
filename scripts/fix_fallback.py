import os
filepath = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\src\training\train_wfo_v19.py'
with open(filepath, 'r') as f:
    content = f.read()

old_str = 'routing_code += f"    // Fallback para OOS puro / Live trading\\n    return {func_name}(features);\\n}\\n"'
new_str = 'routing_code += f"    // Fallback para OOS puro / Live trading\\n    return {func_name}(features);\\n}}\\n"'

content = content.replace(old_str, new_str)
with open(filepath, 'w') as f:
    f.write(content)
print("Fallback fixed syntax")
