[CmdletBinding()]
param([switch]$Install)

$ErrorActionPreference = 'Stop'
$uv = Join-Path $PSScriptRoot 'payload\uv.exe'
$current = (& (Join-Path $env:USERPROFILE '.local\bin\windows-mcp.exe') --help 2>&1 | Out-String)
$latest = (Invoke-RestMethod -Uri 'https://pypi.org/pypi/windows-mcp/json' -TimeoutSec 15).info.version
Write-Host "Ultima versione PyPI: $latest"
if ($Install) {
    & $uv tool install --force "windows-mcp==$latest"
    if ($LASTEXITCODE -ne 0) { throw 'Aggiornamento non riuscito.' }
    Write-Host 'Aggiornamento completato. Riavvia ChatGPT/Codex.'
}
