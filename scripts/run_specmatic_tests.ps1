$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    $python = "python"
}

$listener = [System.Net.Sockets.TcpListener]::Create(0)
$listener.Start()
$port = ($listener.LocalEndpoint).Port
$listener.Stop()

$env:CLARA_CONTRACT_TEST_MODE = "1"

$process = Start-Process -FilePath $python -ArgumentList @('-m', 'uvicorn', 'main:app', '--host', '127.0.0.1', '--port', [string]$port) -WorkingDirectory $root -NoNewWindow -PassThru

try {
    $ready = $false
    for ($i = 0; $i -lt 30; $i++) {
        try {
            Invoke-RestMethod -Uri "http://127.0.0.1:$port/health" -TimeoutSec 1 | Out-Null
            $ready = $true
            break
        } catch {
            Start-Sleep -Seconds 1
        }
    }

    if (-not $ready) {
        throw "Clara did not become ready on http://127.0.0.1:$port"
    }

    Push-Location $root
    try {
        npx specmatic test contracts/clara_api.yaml --examples contracts/clara_api_examples --testBaseURL=http://127.0.0.1:$port
    } finally {
        Pop-Location
    }
} finally {
    if ($process -and -not $process.HasExited) {
        Stop-Process -Id $process.Id -Force
    }
}
