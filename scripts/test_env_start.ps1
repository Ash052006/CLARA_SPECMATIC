$startInfo = New-Object System.Diagnostics.ProcessStartInfo
$startInfo.FileName = 'python'
$startInfo.Arguments = '-c "import os; print(os.getenv(\"TEST_ENV_VAR\"))"'
$startInfo.UseShellExecute = $false
$startInfo.RedirectStandardOutput = $true
$startInfo.RedirectStandardError = $true
$startInfo.CreateNoWindow = $true
$startInfo.EnvironmentVariables['TEST_ENV_VAR'] = '1'
$proc = [System.Diagnostics.Process]::Start($startInfo)
$proc.WaitForExit()
Write-Output "RC=$($proc.ExitCode)"
Write-Output "OUT=$($proc.StandardOutput.ReadToEnd())"
Write-Output "ERR=$($proc.StandardError.ReadToEnd())"
