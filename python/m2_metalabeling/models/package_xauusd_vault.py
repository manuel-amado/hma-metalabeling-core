import os
import shutil
import re
import pandas as pd

# Paths
base_dir = r'C:\Users\Manuel\Desktop\HMA_MetaLabeling'
portfolio_dir = os.path.join(base_dir, 'portfolio', 'XAUUSD')
os.makedirs(portfolio_dir, exist_ok=True)

mql_experts_dir = os.path.join(base_dir, 'mql5', 'Experts', 'HMA_SQX_Discovery')
mql_include_dir = os.path.join(base_dir, 'mql5', 'Include')

# 1. Duplicate & Freeze Oracle as M2_XGBoost_Oracle_XAUUSD.mqh
oracle_src = os.path.join(mql_experts_dir, 'M2_XGBoost_Oracle.mqh')
oracle_xauusd_expert = os.path.join(mql_experts_dir, 'M2_XGBoost_Oracle_XAUUSD.mqh')
oracle_xauusd_include = os.path.join(mql_include_dir, 'M2_XGBoost_Oracle_XAUUSD.mqh')
oracle_xauusd_vault = os.path.join(portfolio_dir, 'M2_XGBoost_Oracle_XAUUSD.mqh')

if os.path.exists(oracle_src):
    shutil.copy(oracle_src, oracle_xauusd_expert)
    shutil.copy(oracle_src, oracle_xauusd_include)
    shutil.copy(oracle_src, oracle_xauusd_vault)
    print("Oracle packaged as M2_XGBoost_Oracle_XAUUSD.mqh")

# 2. Create Production EA: Strategy_XAUUSD_Production.mq5
ea_src = os.path.join(mql_experts_dir, 'Strategy 2.91.69.mq5')
ea_xauusd = os.path.join(mql_experts_dir, 'Strategy_XAUUSD_Production.mq5')
ea_xauusd_vault = os.path.join(portfolio_dir, 'Strategy_XAUUSD_Production.mq5')

with open(ea_src, 'r', encoding='utf-8', errors='ignore') as f:
    ea_code = f.read()

# Update include to point strictly to M2_XGBoost_Oracle_XAUUSD.mqh
ea_code_xauusd = re.sub(
    r'#include\s*[\"<]M2_XGBoost_Oracle\.mqh[\">]',
    '#include "M2_XGBoost_Oracle_XAUUSD.mqh"',
    ea_code
)

with open(ea_xauusd, 'w', encoding='utf-8') as f:
    f.write(ea_code_xauusd)

shutil.copy(ea_xauusd, ea_xauusd_vault)
print("Production EA created: Strategy_XAUUSD_Production.mq5")

# 3. Save Clean Merged Dataset for XAUUSD
features_path = r'C:\Users\Manuel\AppData\Roaming\MetaQuotes\Terminal\Common\Files\XGBoost_Features_M1.csv'
deals_path = r'C:\Users\Manuel\AppData\Roaming\MetaQuotes\Tester\D0E8209F77C8CF37AD8BF550E51FF075\Agent-127.0.0.1-3000\MQL5\Files\Pipeline_Extractor_M1.csv'

if os.path.exists(features_path) and os.path.exists(deals_path):
    features = pd.read_csv(features_path)
    features['Time'] = pd.to_datetime(features['Time'].str.replace('.', '-'))

    deal_rows = []
    with open(deals_path, 'r', encoding='utf-16') as f:
        for line in f.readlines():
            parts = line.strip().split(';')
            if len(parts) >= 14 and parts[8] == 'out' and parts[7] == 'sell':
                try:
                    position_id = int(parts[1])
                    profit = float(parts[12])
                    deal_rows.append({'PositionId': position_id, 'Profit': profit})
                except: pass

    deals = pd.DataFrame(deal_rows)
    df = pd.merge(features[features['Signal_Dir'] == 1.0], deals, left_on='Ticket', right_on='PositionId', how='inner')
    df = df.sort_values('Time').reset_index(drop=True)
    df['Target'] = (df['Profit'] > 0).astype(int)

    dataset_vault = os.path.join(portfolio_dir, 'XGBoost_Dataset_XAUUSD.csv')
    df.to_csv(dataset_vault, index=False)
    print(f"XAUUSD Dataset archived: {len(df)} rows -> {dataset_vault}")

# 4. Save Metadata Audit File
metadata = """==================================================
VAULT ARTIFACT: XAUUSD QUANT MODEL
==================================================
Asset: XAUUSD (Gold)
Timeframe: H1 (Feature Engine: H1/H4/D1)
Window: 2024-01-01 to Present (Rolling Window 2 Years)
Purged Walk-Forward AUC OOS: 0.609
Base Strategy Win Rate: 61.22%
XGBoost Threshold: 0.55
Regime Filter: ADX D1 > 25.0
Risk Management: Fixed Risk Parity (UseCompounding=false default)
Direction: Longs Only (TradeLongs=true, TradeShorts=false)
==================================================
"""
with open(os.path.join(portfolio_dir, 'XAUUSD_Audit_Report.txt'), 'w', encoding='utf-8') as f:
    f.write(metadata)

print("Vault packaging completed successfully!")
