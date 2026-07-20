Remove-Item "C:\Users\Manuel\AppData\Roaming\MetaQuotes\Terminal\Common\Files\Alpha_Sweep_Results*.csv" -ErrorAction SilentlyContinue

for ($i = 1; $i -le 5; $i++) {
    $content = Get-Content "c:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5\Alpha_Sniper_Deploy.mq5"
    $content = $content -replace "input int    InpTestID           = 0;", "input int    InpTestID           = $i;"
    Set-Content "c:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5\Alpha_Sniper_Deploy_$i.mq5" $content
    & "C:\Program Files\MetaTrader 5\metaeditor64.exe" "/compile:c:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5\Alpha_Sniper_Deploy_$i.mq5" "/log"
}

$angles = @(3.0, 3.5, 4.0, 4.5, 5.0)
$trailing_atrs = @(2.0, 2.5, 3.0, 3.5, 4.0)
$modes = @(0, 1, 2)

$combinations = @()
foreach($angle in $angles) {
    foreach($atr in $trailing_atrs) {
        foreach($mode in $modes) {
            $combinations += @{Angle=$angle; ATR=$atr; Mode=$mode}
        }
    }
}

$chunkSize = [math]::Ceiling($combinations.Count / 5)
$chunks = @()
for ($i = 0; $i -lt 5; $i++) {
    $chunks += ,@($combinations[($i * $chunkSize)..([math]::Min(($i + 1) * $chunkSize - 1, $combinations.Count - 1))])
}

$jobs = @()
for ($i = 0; $i -lt 5; $i++) {
    $jobChunk = $chunks[$i]
    $jobId = $i + 1
    
    $scriptBlock = {
        param($chunk, $id)
        
        $total = $chunk.Count
        $current = 0
        $iniFile = "c:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper_Vault\mql5\tester_oos_sweep_$id.ini"
        
        foreach($comb in $chunk) {
            $current++
            $angle = $comb.Angle
            $atr = $comb.ATR
            $mode = $comb.Mode
            
            $iniContent = @"
[Tester]
Expert=Alpha_Sniper\Alpha_Sniper_Deploy_$id.ex5
Symbol=XAUUSD
Period=H1
Optimization=0
Model=1
Deposit=100000
Currency=USD
Leverage=100
FromDate=2023.01.01
ToDate=2026.06.30
Report=AlphaSweep_$id
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
InpMaxSLATR=10.0
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
            Set-Content -Path $iniFile -Value $iniContent
            Start-Process -FilePath "C:\Program Files\MetaTrader 5\terminal64.exe" -ArgumentList "/config:$iniFile" -Wait
        }
    }
    
    $jobs += Start-Job -ScriptBlock $scriptBlock -ArgumentList $jobChunk, $jobId
}

Wait-Job $jobs
Receive-Job $jobs

# Merge CSVs
$outPath = "C:\Users\Manuel\AppData\Roaming\MetaQuotes\Terminal\Common\Files\Alpha_Sweep_Results_Final.csv"
Get-Content $outPath -ErrorAction SilentlyContinue | Out-Null
foreach($c in Get-ChildItem "C:\Users\Manuel\AppData\Roaming\MetaQuotes\Terminal\Common\Files\Alpha_Sweep_Results_*.csv") {
    if ($c.Name -ne "Alpha_Sweep_Results_Final.csv") {
        Get-Content $c.FullName | Add-Content $outPath
    }
}
Write-Host "Parallel Sweep V2 Completed!"
