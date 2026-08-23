[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$pluginRoot = Join-Path $HOME 'plugins\winbridge'
$marketplaceFile = Join-Path $HOME '.agents\plugins\marketplace.json'
$binRoot = Join-Path $env:LOCALAPPDATA 'OpenAI\Codex\bin'
$codex = Get-ChildItem -LiteralPath $binRoot -Filter codex.exe -Recurse -File -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if ($codex) {
    & $codex.FullName mcp remove 'winbridge' 2>$null
    & $codex.FullName plugin remove 'winbridge@personal' 2>$null
}
if (Test-Path -LiteralPath $marketplaceFile) {
    $marketplace = Get-Content -Raw -LiteralPath $marketplaceFile | ConvertFrom-Json
    $marketplace.plugins = @($marketplace.plugins | Where-Object { $_.name -ne 'winbridge' })
    [IO.File]::WriteAllText($marketplaceFile, ($marketplace | ConvertTo-Json -Depth 10), [Text.UTF8Encoding]::new($false))
}
if (Test-Path -LiteralPath $pluginRoot) { Remove-Item -LiteralPath $pluginRoot -Recurse -Force }
$programRoot = Join-Path $env:LOCALAPPDATA 'Programs\WinBridge'
if (Test-Path -LiteralPath $programRoot) { Remove-Item -LiteralPath $programRoot -Recurse -Force }
Write-Host 'Plugin WinBridge disinstallato.'
