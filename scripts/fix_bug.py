import sys
with open(r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\python\training\Normal_Breakout\train_wfo_v20.py', 'r') as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    if "for tree_idx, tree_str in enumerate(trees):" in line and "    // Tree" in lines[i+1]:
        skip = True
        continue
    if skip and "Simplified Tree Parser" in line:
        skip = False
    
    if not skip:
        new_lines.append(line)

with open(r'C:\Users\Manuel\Desktop\HMA_MetaLabeling\python\training\Normal_Breakout\train_wfo_v20.py', 'w') as f:
    f.writelines(new_lines)
