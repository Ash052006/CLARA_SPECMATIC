$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Push-Location $root
try {
    & npx.cmd specmatic stub contracts/clara_api.yaml --host=127.0.0.1 --port=9000
} finally {
    Pop-Location
}
