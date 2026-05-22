$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendRoot = Join-Path $projectRoot "backend"
$python = Join-Path $backendRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $python)) {
    $python = "python"
}

Set-Location $backendRoot
Write-Host "Starting GitHub Dev Card Generator at http://127.0.0.1:8080"
& $python main.py
