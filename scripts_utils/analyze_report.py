import re
import datetime

html_path = r"C:\Users\Manuel\Documents\BACKTESTS\ReportTester-1514246755.html"
try:
    with open(html_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Extract all rows with symbol and profit
    # MT5 trade rows usually look like:
    # <td>2015.01.02 11:15:00</td><td>XAUUSD</td>...<td class="mspt">profit</td>
    
    # Let's find the closing deals. A closing deal has a profit/loss.
    # We can match rows that have a symbol, type (buy/sell), and a profit amount.
    # Actually, simpler: in MT5 report, deals that close positions have the profit at the end of the row.
    # Let's extract blocks of <tr>...</tr>
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', content, re.IGNORECASE | re.DOTALL)
    
    trades = []
    
    for row in rows:
        # Clean tags to get raw columns separated by '|'
        clean_row = re.sub(r'<td[^>]*>', '|', row)
        clean_row = re.sub(r'<[^>]+>', '', clean_row)
        cols = [c.strip() for c in clean_row.split('|') if c.strip()]
        
        # A valid closed trade usually has Date, Ticket, Symbol, Type, Dir, Volume, Price, S/L, T/P, Time, Price, Comm, Swap, Profit
        # We can just look for known symbols: XAUUSD, EURUSD, USDJPY, AUDUSD
        symbol = None
        for sym in ["XAUUSD", "EURUSD", "USDJPY", "AUDUSD"]:
            if sym in cols:
                symbol = sym
                break
                
        if symbol:
            # Profit is usually the last column or second to last.
            # But wait, Orders and Deals are mixed. We only want Deals that have a non-zero profit/loss or we can just parse the "Profit" column.
            # To avoid complexity, let's look for "filled" or "tp"/"sl" or closed deals.
            # Often, MT5 reports list the profit in the very last column if it's a closed deal.
            try:
                # Try to parse the last column as a float (profit)
                profit_str = cols[-1].replace(' ', '')
                profit = float(profit_str)
                # Ignore 0.0 profit deals if they are just order openings
                if profit != 0.0:
                    
                    # Try to parse the date from the first column
                    date_str = cols[0]
                    date_obj = datetime.datetime.strptime(date_str, "%Y.%m.%d %H:%M:%S")
                    
                    trades.append({
                        'symbol': symbol,
                        'profit': profit,
                        'date': date_obj
                    })
            except:
                pass

    print(f"Total extracted trades: {len(trades)}")
    
    # Calculate stats per symbol
    symbols = set([t['symbol'] for t in trades])
    
    print("\nMETRICAS POR ACTIVO:")
    for sym in symbols:
        sym_trades = [t for t in trades if t['symbol'] == sym]
        profits = [t['profit'] for t in sym_trades if t['profit'] > 0]
        losses = [abs(t['profit']) for t in sym_trades if t['profit'] < 0]
        
        gross_profit = sum(profits)
        gross_loss = sum(losses)
        net = gross_profit - gross_loss
        pf = gross_profit / gross_loss if gross_loss > 0 else 999
        wr = len(profits) / len(sym_trades) if len(sym_trades) > 0 else 0
        
        print(f"[{sym}] Trades: {len(sym_trades)} | Net: ${net:.2f} | PF: {pf:.2f} | WinRate: {wr*100:.1f}%")
        
except Exception as e:
    print(f"Error: {e}")
