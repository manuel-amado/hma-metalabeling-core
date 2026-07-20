with open("C:/Users/Manuel/Desktop/HMA_MetaLabeling/Alpha_Sniper_Vault/mql5/Alpha_Sniper_v5.mq5", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines[1100:1300]):
    print(f"{1100 + i}: {line.strip()}")
