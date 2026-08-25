[CmdletBinding()]
param([switch]$NonInteractive,[string]$ResultPath,[string]$UpdateManifestUrl)
$ErrorActionPreference = 'Stop'
$packageRoot = $PSScriptRoot
$sourceApp = Join-Path $packageRoot 'app'
$sourcePlugin = Join-Path $packageRoot 'plugin'
$programRoot = Join-Path $env:LOCALAPPDATA 'Programs\Agentic AI Operator System'
$personalRoot = Join-Path $HOME '.agents\plugins'
$pluginRoot = Join-Path $HOME 'plugins\winbridge'
$marketplaceFile = Join-Path $personalRoot 'marketplace.json'

function Write-Utf8NoBom([string]$Path, [string]$Content) {
    [IO.File]::WriteAllText($Path, $Content, [Text.UTF8Encoding]::new($false))
}

function Find-CodexCli {
    # The MSIX WindowsApps binary can be visible in PATH while direct execution is
    # denied. Prefer the per-user CLI copy distributed by the desktop app.
    $binRoot = Join-Path $env:LOCALAPPDATA 'OpenAI\Codex\bin'
    $candidate = Get-ChildItem -LiteralPath $binRoot -Filter codex.exe -Recurse -File -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($candidate) { return $candidate.FullName }
    $command = Get-Command codex.exe -ErrorAction SilentlyContinue
    if ($command -and $command.Source -notlike '*\WindowsApps\*') { return $command.Source }
    throw 'Codex CLI eseguibile non trovato. Installa o aggiorna l app ChatGPT/Codex.'
}

if (-not [Environment]::Is64BitOperatingSystem -or $env:OS -ne 'Windows_NT') { throw 'Agentic AI Operator System 0.6.0 richiede Windows x64.' }
if (-not (Test-Path -LiteralPath (Join-Path $sourceApp 'winbridge.exe'))) { throw 'Pacchetto non valido: app\winbridge.exe non trovato.' }
if (-not (Test-Path -LiteralPath (Join-Path $sourcePlugin '.codex-plugin\plugin.json'))) { throw 'Pacchetto non valido: plugin Agentic AI Operator System non trovato.' }

$codexCli = Find-CodexCli
$allowedProcessRoots = @(
    [IO.Path]::GetFullPath((Join-Path $HOME 'plugins\winbridge')),
    [IO.Path]::GetFullPath((Join-Path $HOME '.codex\plugins\cache\personal\winbridge')),
    [IO.Path]::GetFullPath($programRoot)
)
Get-CimInstance Win32_Process -Filter "Name='winbridge.exe'" -ErrorAction SilentlyContinue | ForEach-Object {
    if ($_.ExecutablePath) {
        $runningPath = [IO.Path]::GetFullPath($_.ExecutablePath)
        if ($allowedProcessRoots | Where-Object { $runningPath.StartsWith($_, [StringComparison]::OrdinalIgnoreCase) }) {
            Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
        }
    }
}
New-Item -ItemType Directory -Force -Path $programRoot,$personalRoot,(Split-Path $pluginRoot) | Out-Null
if (Test-Path -LiteralPath $pluginRoot) {
    Move-Item -LiteralPath $pluginRoot -Destination "$pluginRoot.backup.$(Get-Date -Format 'yyyyMMddHHmmss')"
}
Copy-Item -LiteralPath $sourcePlugin -Destination $pluginRoot -Recurse
Copy-Item -LiteralPath $sourceApp -Destination (Join-Path $pluginRoot 'app') -Recurse

if (Test-Path -LiteralPath $marketplaceFile) {
    Copy-Item -LiteralPath $marketplaceFile -Destination "$marketplaceFile.winbridge-backup-$(Get-Date -Format 'yyyyMMddHHmmss')"
    $marketplace = Get-Content -Raw -LiteralPath $marketplaceFile | ConvertFrom-Json
} else {
    $marketplace = [pscustomobject]@{ name='personal'; interface=[pscustomobject]@{displayName='Personal'}; plugins=@() }
}
if ($marketplace.name -ne 'personal') { throw 'Il marketplace personale esistente non si chiama personal.' }
$others = @($marketplace.plugins | Where-Object { $_.name -ne 'winbridge' })
$entry = [pscustomobject]@{ name='winbridge'; source=[pscustomobject]@{source='local';path='./plugins/winbridge'}; policy=[pscustomobject]@{installation='AVAILABLE';authentication='ON_INSTALL'}; category='Productivity' }
$marketplace.plugins = @($others + $entry)
Write-Utf8NoBom $marketplaceFile ($marketplace | ConvertTo-Json -Depth 10)

$sourceVersion = (Get-Content -Raw -LiteralPath (Join-Path $pluginRoot '.codex-plugin\plugin.json') | ConvertFrom-Json).version
$pluginListBefore = (& $codexCli plugin list | Out-String)
$alreadyCurrent = $pluginListBefore -match ("(?m)^winbridge@personal\s+installed, enabled\s+" + [regex]::Escape($sourceVersion) + "\s")
if (-not $alreadyCurrent) {
    & $codexCli plugin add 'winbridge@personal'
    if ($LASTEXITCODE -ne 0) { throw 'Installazione del plugin Agentic AI Operator System non riuscita.' }
}
$directExe = Join-Path $pluginRoot 'app\winbridge.exe'
$mcpConfigure = (& $directExe --configure-mcp --executable $directExe | Out-String)
if ($LASTEXITCODE -ne 0 -or $mcpConfigure -notmatch '"ok": true') { throw 'Registrazione MCP diretta di Agentic AI Operator System non riuscita.' }
Copy-Item -LiteralPath (Join-Path $packageRoot 'Check-WinBridgeUpdate.ps1') -Destination $programRoot -Force
Copy-Item -LiteralPath (Join-Path $packageRoot 'Uninstall-WinBridge.ps1') -Destination $programRoot -Force
if ($UpdateManifestUrl) {
    if (-not $UpdateManifestUrl.StartsWith('https://')) { throw 'UpdateManifestUrl deve usare HTTPS.' }
    Write-Utf8NoBom (Join-Path $programRoot 'update-settings.json') (@{update_manifest_url=$UpdateManifestUrl} | ConvertTo-Json)
}

$pluginList = (& $codexCli plugin list | Out-String)
$mcpList = (& $codexCli mcp list | Out-String)
$result = [ordered]@{ ok=($pluginList -match 'winbridge@personal' -and $mcpList -match '(?m)^winbridge\s'); version='0.6.0'; plugin_installed=($pluginList -match 'winbridge@personal'); mcp_configured=($mcpList -match '(?m)^winbridge\s'); plugin_root=$pluginRoot; marketplace=$marketplaceFile; update_manifest_configured=[bool]$UpdateManifestUrl; restart_required=$true; persistent_background_service=$false }
$resultFile = if ($ResultPath) {$ResultPath} else {Join-Path $programRoot 'INSTALL_RESULT.json'}
Write-Utf8NoBom $resultFile ($result | ConvertTo-Json -Depth 5)
if (-not $result.ok) { throw 'Verifica finale plugin/MCP non riuscita. Controllare INSTALL_RESULT.json.' }
Write-Host "Agentic AI Operator System 0.6.0 installato come plugin personale e MCP globale: $pluginRoot"
Write-Host "Risultato: $resultFile"
Write-Host 'Chiudi completamente ChatGPT/Codex, riaprilo e crea una nuova task.'
