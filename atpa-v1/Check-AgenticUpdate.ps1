[CmdletBinding()]
param([string]$ManifestUrl,[switch]$Install)
$ErrorActionPreference='Stop'
$programRoot=Join-Path $env:LOCALAPPDATA 'Programs\Intelligenza Artificiale Italia\Agentic AI Operator System'
$settingsFile=Join-Path $programRoot 'update-settings.json'
$defaultManifest='https://github.com/IntelligenzaArtificiale/agentic-ai-operator-system/releases/latest/download/release-manifest.json'
if(-not $ManifestUrl -and (Test-Path -LiteralPath $settingsFile)){$ManifestUrl=(Get-Content -Raw -LiteralPath $settingsFile|ConvertFrom-Json).update_manifest_url}
if(-not $ManifestUrl){$ManifestUrl=$defaultManifest}
if(-not $ManifestUrl.StartsWith('https://')){throw 'Il manifest aggiornamenti deve usare HTTPS.'}
$manifest=Invoke-RestMethod -Uri $ManifestUrl -Method Get
foreach($field in 'product','version','zip_url','sha256'){if(-not $manifest.$field){throw "Campo manifest mancante: $field"}}
if($manifest.product -ne 'Agentic AI Operator System'){throw 'Manifest destinato a un prodotto diverso.'}
if(-not ([string]$manifest.zip_url).StartsWith('https://')){throw 'zip_url deve usare HTTPS.'}
$installedManifest=Join-Path $programRoot 'installed-version.json'
$current='0.0.0'
if(Test-Path -LiteralPath $installedManifest){$current=(Get-Content -Raw -LiteralPath $installedManifest|ConvertFrom-Json).version}
$available=[version]$manifest.version -gt [version]$current
$status=[ordered]@{ok=$true;product=$manifest.product;current_version=$current;latest_version=$manifest.version;update_available=$available;installed=$false}
if($Install -and $available){
    $tempRoot=Join-Path ([IO.Path]::GetTempPath()) ('AgenticAIUpdate-'+[guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $tempRoot|Out-Null
    try{
        $zip=Join-Path $tempRoot 'Agentic-AI-Operator-System.zip'
        Invoke-WebRequest -Uri $manifest.zip_url -OutFile $zip
        $actual=(Get-FileHash -LiteralPath $zip -Algorithm SHA256).Hash
        if($actual -ne ([string]$manifest.sha256).ToUpperInvariant()){throw 'SHA-256 del pacchetto non valido.'}
        $expanded=Join-Path $tempRoot 'expanded';Expand-Archive -LiteralPath $zip -DestinationPath $expanded
        $installer=Get-ChildItem -LiteralPath $expanded -Filter Install-System.ps1 -Recurse -File|Select-Object -First 1
        if(-not $installer){throw 'Install-System.ps1 non trovato nel pacchetto.'}
        & $installer.FullName -NonInteractive -UpdateManifestUrl $ManifestUrl
        if($LASTEXITCODE -ne 0){throw 'Installazione aggiornamento non riuscita.'}
        $status.installed=$true
    }finally{if(Test-Path -LiteralPath $tempRoot){Remove-Item -LiteralPath $tempRoot -Recurse -Force}}
}
$status|ConvertTo-Json
