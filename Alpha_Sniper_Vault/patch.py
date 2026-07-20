with open("C:/Users/Manuel/Desktop/HMA_MetaLabeling/Alpha_Sniper_Vault/mql5/Alpha_Sniper_v5.mq5", "r", encoding="utf-8") as f:
    c = f.read()

c = c.replace(
    'PriceDeviationATR,OppositeBarsCount',
    'OppositeBarsCount'
)

c = c.replace(
    'feat_price_dev_atr, feat_opposite_bars',
    'feat_opposite_bars'
)

c = c.replace(
    '%.5f,%.0f,%.5f,%d',
    '%.0f,%.5f,%d'
)

c = c.replace(
    'double features[20];',
    'double features[19];'
)

c = c.replace(
    'features[18] = feat_price_dev_atr;\n        features[19] = feat_opposite_bars;',
    'features[18] = feat_opposite_bars;'
)

with open("C:/Users/Manuel/Desktop/HMA_MetaLabeling/Alpha_Sniper_Vault/mql5/Alpha_Sniper_v5.mq5", "w", encoding="utf-8") as f:
    f.write(c)
