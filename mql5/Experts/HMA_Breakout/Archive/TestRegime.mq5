#property copyright "Manuel"
#property version   "1.00"
#include <RegimeMap.mqh>

int OnInit() {
    Print("Testing GetPrecomputedRegime...");
    
    datetime t1 = D'2022.01.05 15:30:00';
    datetime t2 = D'2022.06.10 08:00:00';
    datetime t3 = D'2024.03.15 12:00:00';
    
    int r1 = GetPrecomputedRegime(t1);
    int r2 = GetPrecomputedRegime(t2);
    int r3 = GetPrecomputedRegime(t3);
    
    PrintFormat("Regime on %s: %d", TimeToString(t1), r1);
    PrintFormat("Regime on %s: %d", TimeToString(t2), r2);
    PrintFormat("Regime on %s: %d", TimeToString(t3), r3);
    
    // Check distribution manually
    int count_0 = 0;
    int count_1 = 0;
    for(int i = 0; i < TOTAL_REGIME_RECORDS; i++) {
        if(RegimeStates[i] == 0) count_0++;
        else count_1++;
    }
    PrintFormat("Total 0s: %d, Total 1s: %d", count_0, count_1);
    
    return INIT_FAILED; // Stop right after init
}