import configparser

config = configparser.ConfigParser()
config.optionxform = str
config['Tester'] = {
    'Expert': r'Alpha_Sniper\TestHarvest_Massive_V2.ex5',
    'Symbol': 'XAUUSD',
    'Period': 'H1',
    'Optimization': '0',
    'Model': '1',
    'Deposit': '100000',
    'Currency': 'USD',
    'Leverage': '100',
    'FromDate': '2015.01.01',
    'ToDate': '2026.06.30',
    'Report': 'HarvestReport',
    'ReplaceReport': '1',
    'ShutdownTerminal': '1',
    'Login': '0'
}

config['TesterInputs'] = {
    'InpMinAngle': '0.5',
    'AntiNoiseATRPct': '0.0',
    'InpMaxSignalBarATR': '3.0',
    'InpMaxSLATR': '100.0',
    'InpScaleOutRR': '999.0',
    'InpMinBarsToHold': '99999',
    'InpExitMode': '2',
    'InpTrailingATR': '3.0',
    'InpEntryThreshold': '0.0',
    'InpMetaLabeling': '1'
}

with open(r'c:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5\tester_harvest_hybrid_v2.ini', 'w', encoding='utf-8') as configfile:
    config.write(configfile)
