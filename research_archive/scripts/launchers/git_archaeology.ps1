cd "c:\Users\Manuel\Desktop\HMA_MetaLabeling"

# Initialize Git
git init
git remote add origin https://github.com/manuel-amado/ws-mavericks.git

# Set user configuration locally just in case
git config user.name "Antigravity Quant"
git config user.email "quant@mavericks.fund"

# Path to the source files
$srcDir = "C:\Users\Manuel\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Experts\Alpha_Sniper"

# Array of versions to commit
$versions = @(
    @{ File = "Alpha_Sniper_v5.mq5"; Date = "2026-07-06 13:29:00"; Msg = "feat: Alpha_Sniper_v5 - Initial MetaLabeling architecture and data extraction" },
    @{ File = "Alpha_Sniper_v6.mq5"; Date = "2026-07-14 12:20:00"; Msg = "feat: Alpha_Sniper_v6 - XGBoost Universal Brain integration and multi-asset logic" },
    @{ File = "Alpha_Sniper_v7.mq5"; Date = "2026-07-14 16:32:00"; Msg = "feat: Alpha_Sniper_v7 - Structural Label Shuffling and Anti-Overfitting constraints" },
    @{ File = "Alpha_Sniper_v8.mq5"; Date = "2026-07-15 13:49:00"; Msg = "feat: Alpha_Sniper_v8 - OOS Interleaved Blocks and Time Embargo Purge" },
    @{ File = "Alpha_Sniper_v9.mq5"; Date = "2026-07-17 18:02:00"; Msg = "feat: Alpha_Sniper_v9 - Structural Kinematics, Elastic Tension and Asymmetric Gravity" }
)

# Loop through and commit
foreach ($v in $versions) {
    $srcFile = Join-Path $srcDir $v.File
    if (Test-Path $srcFile) {
        Copy-Item -Path $srcFile -Destination "c:\Users\Manuel\Desktop\HMA_MetaLabeling\Alpha_Sniper.mq5" -Force
        git add Alpha_Sniper.mq5
        $env:GIT_AUTHOR_DATE = $v.Date
        $env:GIT_COMMITTER_DATE = $v.Date
        git commit -m "$($v.Msg)"
    } else {
        Write-Host "Warning: $($srcFile) not found."
    }
}

# Cleanup env vars
Remove-Item Env:\GIT_AUTHOR_DATE
Remove-Item Env:\GIT_COMMITTER_DATE

# Show the log
git log --pretty=fuller

# Push to origin main
Write-Host "Attempting push to origin main..."
git branch -M main
git push -u origin main