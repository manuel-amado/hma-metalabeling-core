import pandas as pd
import sys

try:
    tables = pd.read_html("C:/Users/Manuel/Documents/BACKTESTS/ReportTester-1514246755.html")
    print(f"Encontradas {len(tables)} tablas.")
    
    # Print the first few tables which usually contain the summary metrics
    for i, t in enumerate(tables[:3]):
        print(f"\n--- TABLA {i} ---")
        print(t.to_string())
except Exception as e:
    print(f"Error: {e}")
