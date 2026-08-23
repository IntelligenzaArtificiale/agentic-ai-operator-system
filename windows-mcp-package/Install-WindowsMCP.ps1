[CmdletBinding()]
param([switch]$NonInteractive, [string]$ResultPath)

$ErrorActionPreference = 'Stop'
$packageRoot = $PSScriptRoot
$payloadRoot = Join-Path $packageRoot 'payload'
$uv = Join-Path $payloadRoot 'uv.exe'
$wheel = Join-Path $payloadRoot 'windows_mcp-0.8.5-py3-none-any.whl'
$userRoot = [IO.Path]::GetFullPath($env:USERPROFILE)
$pluginRoot = Join-Path $userRoot 'plugins\windows-mcp'
$marketplaceRoot = Join-Path $userRoot '.agents\plugins'
$marketplaceFile = Join-Path $marketplaceRoot 'marketplace.json'
$installedExe = Join-Path $userRoot '.local\bin\windows-mcp.exe'

function Write-Utf8NoBom([string]$Path, [string]$Content) {
    [IO.File]::WriteAllText($Path, $Content, [Text.UTF8Encoding]::new($false))
}

function Find-CodexCli {
    $binRoot = Join-Path $env:LOCALAPPDATA 'OpenAI\Codex\bin'
    $candidate = Get-ChildItem -LiteralPath $binRoot -Filter codex.exe -Recurse -File -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($candidate) { return $candidate.FullName }
    $command = Get-Command codex.exe -ErrorAction SilentlyContinue
    if ($command -and $command.Source -notlike '*\WindowsApps\*') { return $command.Source }
    throw 'Codex CLI non trovato. Installa o aggiorna prima l app ChatGPT/Codex.'
}

if ($env:OS -ne 'Windows_NT' -or -not [Environment]::Is64BitOperatingSystem) {
    throw 'Questo pacchetto richiede Windows x64.'
}
if (-not (Test-Path -LiteralPath $uv) -or -not (Test-Path -LiteralPath $wheel)) {
    throw 'Pacchetto incompleto: payload uv/wheel mancante.'
}
if (-not (Test-Path -LiteralPath (Join-Path $packageRoot 'plugin\.codex-plugin\plugin.json'))) {
    throw 'Pacchetto incompleto: plugin Codex mancante.'
}

$codex = Find-CodexCli

# Prefer PyPI so future `uv tool upgrade` works; the bundled wheel is the offline fallback.
& $uv tool install --force 'windows-mcp==0.8.5'
if ($LASTEXITCODE -ne 0) {
    & $uv tool install --force $wheel
    if ($LASTEXITCODE -ne 0) { throw 'Installazione Windows-MCP non riuscita.' }
}
if (-not (Test-Path -LiteralPath $installedExe)) { throw 'windows-mcp.exe non trovato dopo l installazione.' }

# Remove the former custom bridge if present, then register the absolute executable path.
& $codex plugin remove 'winbridge@personal' 2>$null | Out-Null
& $codex mcp remove winbridge 2>$null | Out-Null
& $codex mcp remove windows-mcp 2>$null | Out-Null
& $codex mcp add windows-mcp -- $installedExe serve
if ($LASTEXITCODE -ne 0) { throw 'Registrazione MCP in Codex non riuscita.' }

New-Item -ItemType Directory -Force -Path (Split-Path $pluginRoot),$marketplaceRoot | Out-Null
if (Test-Path -LiteralPath $pluginRoot) {
    Move-Item -LiteralPath $pluginRoot -Destination "$pluginRoot.backup.$(Get-Date -Format 'yyyyMMddHHmmss')"
}
Copy-Item -LiteralPath (Join-Path $packageRoot 'plugin') -Destination $pluginRoot -Recurse

if (Test-Path -LiteralPath $marketplaceFile) {
    Copy-Item -LiteralPath $marketplaceFile -Destination "$marketplaceFile.backup.$(Get-Date -Format 'yyyyMMddHHmmss')"
    $marketplace = Get-Content -Raw -LiteralPath $marketplaceFile | ConvertFrom-Json
} else {
    $marketplace = [pscustomobject]@{name='personal';interface=[pscustomobject]@{displayName='Personal'};plugins=@()}
}
if ($marketplace.name -ne 'personal') { throw 'Il marketplace personale esistente non si chiama personal.' }
$others = @($marketplace.plugins | Where-Object { $_.name -notin @('winbridge','windows-mcp') })
$entry = [pscustomobject]@{
    name='windows-mcp'
    source=[pscustomobject]@{source='local';path='./plugins/windows-mcp'}
    policy=[pscustomobject]@{installation='AVAILABLE';authentication='ON_INSTALL'}
    category='Productivity'
}
$marketplace.plugins = @($others + $entry)
Write-Utf8NoBom $marketplaceFile ($marketplace | ConvertTo-Json -Depth 10)

& $codex plugin add 'windows-mcp@personal'
if ($LASTEXITCODE -ne 0) { throw 'Installazione plugin Windows-MCP non riuscita.' }

$mcpStatus = (& $codex mcp get windows-mcp | Out-String)
$pluginStatus = (& $codex plugin list | Out-String)
$ok = $mcpStatus -match 'enabled:\s+true' -and $pluginStatus -match '(?m)^windows-mcp@personal\s+installed, enabled'
$result = [ordered]@{
    ok=$ok
    version='0.8.5'
    mcp_executable=$installedExe
    mcp_configured=($mcpStatus -match 'enabled:\s+true')
    plugin_installed=($pluginStatus -match '(?m)^windows-mcp@personal\s+installed, enabled')
    restart_required=$true
}
$resultFile = if ($ResultPath) { $ResultPath } else { Join-Path $packageRoot 'INSTALL_RESULT.json' }
Write-Utf8NoBom $resultFile ($result | ConvertTo-Json -Depth 5)
if (-not $ok) { throw "Verifica finale fallita. Leggi $resultFile" }
Write-Host "Windows-MCP 0.8.5 installato e configurato. Risultato: $resultFile"
Write-Host 'Chiudi completamente ChatGPT/Codex, riaprilo e crea una nuova task.'
