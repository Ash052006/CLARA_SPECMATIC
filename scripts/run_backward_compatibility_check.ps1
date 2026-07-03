param(
    [string]$BaseBranch = "origin/main",
    [string]$TargetPath = "contracts/clara_api.yaml"
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Push-Location $root
try {
    npx specmatic backward-compatibility-check --repo-dir=. --base-branch=$BaseBranch --target-path=$TargetPath
} finally {
    Pop-Location
}
