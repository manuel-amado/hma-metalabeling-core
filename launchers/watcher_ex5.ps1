$folderToWatch = "C:\Users\Manuel\AppData\Roaming\MetaQuotes\Terminal\D0E8209F77C8CF37AD8BF550E51FF075\MQL5\Experts\Alpha_Sniper"
$filter = "*.ex5"

$watcher = New-Object IO.FileSystemWatcher $folderToWatch, $filter -Property @{
    IncludeSubdirectories = $false
    EnableRaisingEvents = $true
}

Write-Host "Nexus Protocol: Monitoring $folderToWatch for $filter changes..."

$action = {
    $path = $Event.SourceEventArgs.FullPath
    $name = $Event.SourceEventArgs.Name
    $changeType = $Event.SourceEventArgs.ChangeType
    $timeStamp = $Event.TimeGenerated
    
    Write-Host "[$timeStamp] Milestone detected: $name was $changeType"
    
    # Execute the python script
    $pythonScript = "C:\Users\Manuel\Desktop\HMA_MetaLabeling\git_auto_push.py"
    $pythonExe = "python"
    
    # We delay execution slightly to ensure the compiler finishes writing the file
    Start-Sleep -Seconds 2
    
    try {
        & $pythonExe $pythonScript --milestone
    } catch {
        Write-Host "Error invoking git_auto_push.py"
    }
}

Register-ObjectEvent $watcher "Changed" -Action $action > $null
Register-ObjectEvent $watcher "Created" -Action $action > $null

# Keep the script running
try {
    while ($true) {
        Start-Sleep -Seconds 5
    }
} finally {
    Unregister-Event -SourceIdentifier "Changed" -ErrorAction SilentlyContinue
    Unregister-Event -SourceIdentifier "Created" -ErrorAction SilentlyContinue
}
