[CmdletBinding()]
param([string]$OutputPath=(Join-Path ([IO.Path]::GetTempPath()) 'AIOS-License-Server-Deploy.zip'))
$ErrorActionPreference='Stop'
$source=Join-Path $PSScriptRoot 'license-server'
$provisioning=Join-Path $source 'private\provisioning.php'
$setupToken=Join-Path $source 'private\setup-token.txt'
foreach($required in @($provisioning,$setupToken,(Join-Path $source '.htaccess'),(Join-Path $source 'api.php'),(Join-Path $source 'index.php'))){
    if(-not(Test-Path -LiteralPath $required)){throw "File di deploy mancante: $required"}
}
$resolvedOutput=[IO.Path]::GetFullPath($OutputPath)
if(Test-Path -LiteralPath $resolvedOutput){Remove-Item -LiteralPath $resolvedOutput -Force}
Add-Type -AssemblyName System.IO.Compression.FileSystem
[IO.Compression.ZipFile]::CreateFromDirectory($source,$resolvedOutput,[IO.Compression.CompressionLevel]::Optimal,$false)
[pscustomobject]@{package=$resolvedOutput;sha256=(Get-FileHash -LiteralPath $resolvedOutput -Algorithm SHA256).Hash;contains_private_provisioning=$true}
