import sys
import re

def parse_report(filepath):
    try:
        with open(filepath, 'r', encoding='utf-16', errors='ignore') as f:
            content = f.read()
    except:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

    # Clean HTML tags
    text = re.sub(r'<[^>]+>', ' ', content)
    text = re.sub(r'\s+', ' ', text)

    metrics = {}
    
    # regex matches
    m_net = re.search(r'Beneficio Neto:\s*([\-\d\.\s]+)', text)
    if m_net: metrics['Net Profit'] = m_net.group(1).replace(' ','')

    m_pf = re.search(r'Factor de Beneficio:\s*([\-\d\.\s]+)', text)
    if m_pf: metrics['Profit Factor'] = m_pf.group(1).replace(' ','')

    m_dd = re.search(r'Reducci[oó]n m[aá]xima de la equidad:\s*([\d\.\s]+)\s*\(([\d\.\s]+%)\)', text)
    if m_dd: metrics['Max Drawdown'] = f"{m_dd.group(1).replace(' ','')} ({m_dd.group(2).replace(' ','')})"

    m_trades = re.search(r'Total de transacciones:\s*(\d+)', text)
    if m_trades: metrics['Total Trades'] = m_trades.group(1)

    m_win = re.search(r'Posiciones rentables \(% del total\):\s*(\d+)\s*\(([\d\.\s]+%)\)', text)
    if m_win: metrics['Win Rate'] = f"{m_win.group(2).replace(' ','')}"

    print(f"Metrics for {filepath}:")
    for k, v in metrics.items():
        print(f"  {k}: {v}")

if __name__ == '__main__':
    parse_report(sys.argv[1])
