$angles = @(3.0, 3.5, 4.0, 4.5, 5.0)
$trailing_atrs = @(2.0, 2.5, 3.0, 3.5, 4.0)
$modes = @(0, 1, 2)

$total = $angles.Length * $trailing_atrs.Length * $modes.Length
$current = 0

Remove-Item "C:\Users\Manuel\AppData\Roaming\MetaQuotes\Terminal\Common\Files\Alpha_Sweep_Results.csv" -ErrorAction SilentlyContinue

foreach($angle in $angles) {
    foreach($atr in $trailing_atrs) {
        foreach($mode in $modes) {
            $current++
            Write-Host "Running pass $current / $total (Angle=$angle, ATR=$atr, Mode=$mode)..."
            $iniContent = @"
[Tester]
Expert=Alpha_Sniper\Alpha_Sniper_Deploy.ex5
Symbol=XAUUSD
Period=H1
Optimization=0
Model=1
Deposit=100000
Currency=USD
Leverage=100
FromDate=2023.01.01
ToDate=2026.06.30
Report=AlphaSweep
ReplaceReport=1
ShutdownTerminal=1
Login=0

[TesterInputs]
InpSymbols=XAUUSD
InpHMA_Entry_Period=50
InpHMA_Exit_Period=20
InpMinBarsToHold=3
LookbackBars=7
AntiNoiseATRPct=2.0
InpMaxSLATR=5.0
RsiPeriod=14
RsiLookbackBars=15
RsiOversoldLevel=35
RsiOverboughtLevel=65
MaxSpreadPips=4.0
InpMaxSpreadPips_Metals=120.0
InpMaxSlippagePoints=20
InpStartTradingHour=1
InpEndTradingHour=23
InpDonchianPeriod=20
InpExitMode=$mode
InpTrailingATR=$atr
InpMinAngle=$angle
InpCriticalZScoreExhaustion=1.5
InpEntryThreshold=0.0
InpExitThreshold=0.8
InpUseCompoundInterest=false
InpFixedBalance=100000.0
InpRiskPerTrade=1.0
InpMaxGlobalRisk=10.0
InpMaxTradesPerSymbol=1
InpMaxGlobalTrades=10
InpScaleOutRR=1.5
InpFastHMA_Exit_Period=14
"@
            Set-Content -Path "tester_oos_sweep.ini" -Value $iniContent
            Start-Process -FilePath "C:\Program Files\MetaTrader 5\terminal64.exe" -ArgumentList "/config:c:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5\tester_oos_sweep.ini" -Wait
        }
    }
}
Write-Host "Sweep Completed!"
