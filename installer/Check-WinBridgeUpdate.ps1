[CmdletBinding()]
param([string]$ManifestUrl,[switch]$Install)
$ErrorActionPreference = 'Stop'
$programRoot = Join-Path $env:LOCALAPPDATA 'Programs\Agentic AI Operator System'
$settingsFile = Join-Path $programRoot 'update-settings.json'
$pluginManifest = Join-Path $HOME 'plugins\winbridge\.codex-plugin\plugin.json'
if (-not $ManifestUrl -and (Test-Path -LiteralPath $settingsFile)) { $ManifestUrl = (Get-Content -Raw -LiteralPath $settingsFile | ConvertFrom-Json).update_manifest_url }
if (-not $ManifestUrl) { [pscustomobject]@{ok=$true;configured=$false;update_available=$false;message='URL manifest aggiornamenti non configurato.'} | ConvertTo-Json; exit 0 }
if (-not $ManifestUrl.StartsWith('https://')) { throw 'Il manifest aggiornamenti deve usare HTTPS.' }
if (-not (Test-Path -LiteralPath $pluginManifest)) { throw 'Plugin Agentic AI Operator System non installato.' }
$current = (Get-Content -Raw -LiteralPath $pluginManifest | ConvertFrom-Json).version.Split('+')[0]
$manifest = Invoke-RestMethod -Uri $ManifestUrl -Method Get
foreach ($field in 'version','zip_url','sha256') { if (-not $manifest.$field) { throw "Campo manifest mancante: $field" } }
if (-not ([string]$manifest.zip_url).StartsWith('https://')) { throw 'zip_url deve usare HTTPS.' }
$available = [version]$manifest.version -gt [version]$current
$status = [ordered]@{ok=$true;configured=$true;current_version=$current;latest_version=$manifest.version;update_available=$available;installed=$false}
if ($Install -and $available) {
    $tempRoot = Join-Path ([IO.Path]::GetTempPath()) ("Agentic AI Operator SystemUpdate-" + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $tempRoot | Out-Null
    try {
        $zip = Join-Path $tempRoot 'Agentic AI Operator System.zip'
        Invoke-WebRequest -Uri $manifest.zip_url -OutFile $zip
        if ((Get-FileHash -LiteralPath $zip -Algorithm SHA256).Hash -ne ([string]$manifest.sha256).ToUpperInvariant()) { throw 'SHA-256 del pacchetto non valido.' }
        $expanded = Join-Path $tempRoot 'expanded'
        Expand-Archive -LiteralPath $zip -DestinationPath $expanded
        $installer = Get-ChildItem -LiteralPath $expanded -Filter Install-WinBridge.ps1 -Recurse -File | Select-Object -First 1
        if (-not $installer) { throw 'Installer non trovato nel pacchetto aggiornamento.' }
        & $installer.FullName -NonInteractive -UpdateManifestUrl $ManifestUrl
        $status.installed = $true
    } finally {
        if (Test-Path -LiteralPath $tempRoot) { Remove-Item -LiteralPath $tempRoot -Recurse -Force }
    }
}
$status | ConvertTo-Json
