param(
    [Parameter(Mandatory=$true)]
    [string]$Task,
    [switch]$KeepAlive
)

# 1. Check if Ollama is already active
$ollamaRunning = $false
try {
    $res = Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 1 -ErrorAction SilentlyContinue
    if ($res) { $ollamaRunning = $true }
} catch {}

$startedByScript = $false

if (-not $ollamaRunning) {
    Write-Host "[Auto-Hermes] Starting Ollama background server..." -ForegroundColor Cyan
    Start-Process -FilePath "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe" -ArgumentList "serve" -WindowStyle Hidden
    $startedByScript = $true
    
    # Wait for service readiness (max 15 sec)
    for ($i=0; $i -lt 15; $i++) {
        Start-Sleep -Seconds 1
        try {
            $res = Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 1 -ErrorAction SilentlyContinue
            if ($res) { break }
        } catch {}
    }
}

# 2. Execute task via Hermes Agent
Write-Host "[Auto-Hermes] Executing task via Hermes Agent..." -ForegroundColor Green
& "$env:LOCALAPPDATA\hermes\bin\hermes.cmd" -z "$Task"

# 3. Automatic teardown and VRAM cleanup
if ($startedByScript -and -not $KeepAlive) {
    Write-Host "[Auto-Hermes] Task finished. Stopping Ollama and freeing VRAM..." -ForegroundColor Yellow
    Stop-Process -Name "*ollama*" -Force -ErrorAction SilentlyContinue
    Write-Host "[Auto-Hermes] VRAM successfully released." -ForegroundColor Gray
}
