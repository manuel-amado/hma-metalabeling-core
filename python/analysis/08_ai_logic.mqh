bool IsTradeAllowedByAI(double RSI, double ATR, double Dist_EMA, int Hour, int DayOfWeek, int Signal) {
    if (Hour <= 14.5000) {
        if (RSI <= 44.3391) {
            if (ATR <= 2.3229) {
                return false; // Prob Win: 0.0%
            } else {
                return false; // Prob Win: 39.3%
            }
        } else {
            if (RSI <= 52.1705) {
                if (ATR <= 2.0954) {
                    return false; // Prob Win: 41.1%
                } else {
                    return true; // Prob Win: 65.8%
                }
            } else {
                if (ATR <= 2.5179) {
                    return false; // Prob Win: 40.9%
                } else {
                    return false; // Prob Win: 9.0%
                }
            }
        }
    } else {
        if (RSI <= 40.6987) {
            if (Dist_EMA <= -1.2106) {
                if (RSI <= 38.8086) {
                    return true; // Prob Win: 56.1%
                } else {
                    return false; // Prob Win: 24.2%
                }
            } else {
                if (ATR <= 3.3679) {
                    return false; // Prob Win: 0.0%
                } else {
                    return false; // Prob Win: 28.9%
                }
            }
        } else {
            if (RSI <= 42.0663) {
                return true; // Prob Win: 78.6%
            } else {
                if (RSI <= 44.7370) {
                    return false; // Prob Win: 37.4%
                } else {
                    return true; // Prob Win: 56.9%
                }
            }
        }
    }
}
