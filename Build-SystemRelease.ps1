[CmdletBinding()]
param([Parameter(Mandatory)][ValidatePattern('^\d+\.\d+\.\d+$')][string]$Version)
$ErrorActionPreference='Stop'
$repoRoot=$PSScriptRoot
$source=Join-Path $repoRoot 'atpa-v1'
$releaseBase="Agentic-AI-Operator-System-$Version-Windows-x64"
$releaseRoot=Join-Path $repoRoot "release\$releaseBase"
$zip="$releaseRoot.zip"
if(Test-Path -LiteralPath $releaseRoot){Remove-Item -LiteralPath $releaseRoot -Recurse -Force}
$updateExisting=$false
if(Test-Path -LiteralPath $zip){
    try{Remove-Item -LiteralPath $zip -Force}
    catch{$updateExisting=$true}
}
New-Item -ItemType Directory -Path $releaseRoot|Out-Null
foreach($directory in 'bundle','payload','runtime','template','third-party-notices'){
    Copy-Item -LiteralPath (Join-Path $source $directory) -Destination $releaseRoot -Recurse
}
foreach($file in 'AGENTS.md','Check-AgenticUpdate.ps1','Check-System.ps1','GUIDA-STRUTTURA-PROCEDURE.md','GUIDA-UTENTE.md','INSTALLA.cmd','Install-System.ps1','PACKAGE-MANIFEST.json','PROMPT-INSTALLAZIONE.txt','TELEMETRIA-E-OTTIMIZZAZIONE.md'){
    Copy-Item -LiteralPath (Join-Path $source $file) -Destination $releaseRoot
}
if($updateExisting){
    Compress-Archive -LiteralPath $releaseRoot -DestinationPath $zip -CompressionLevel Optimal -Update
}else{
    Compress-Archive -LiteralPath $releaseRoot -DestinationPath $zip -CompressionLevel Optimal
}
$hash=(Get-FileHash -LiteralPath $zip -Algorithm SHA256).Hash
$manifest=[ordered]@{
    schema_version=1
    product='Agentic AI Operator System'
    version=$Version
    channel='stable'
    platform='windows-x64'
    zip_url="https://github.com/IntelligenzaArtificiale/agentic-ai-operator-system/releases/download/v$Version/$releaseBase.zip"
    sha256=$hash
    published_at=(Get-Date).ToUniversalTime().ToString('o')
    minimum_windows='10'
}
$manifestPath=Join-Path $repoRoot 'release-manifest.json'
[IO.File]::WriteAllText($manifestPath,($manifest|ConvertTo-Json),[Text.UTF8Encoding]::new($false))
[pscustomobject]@{zip=$zip;manifest=$manifestPath;sha256=$hash}
