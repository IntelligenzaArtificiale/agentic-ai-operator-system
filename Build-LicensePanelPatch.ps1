[CmdletBinding()]
param([Parameter(Mandatory)][ValidatePattern('^\d+\.\d+\.\d+$')][string]$Version)
$ErrorActionPreference='Stop'
$stage=Join-Path $PSScriptRoot "release\AIOS-License-Panel-$Version-Patch"
$zip="$stage.zip"
if((Test-Path -LiteralPath $stage) -or (Test-Path -LiteralPath $zip)){throw 'Patch già presente: non sovrascrivo.'}
New-Item -ItemType Directory -Path $stage,(Join-Path $stage 'src'),(Join-Path $stage 'templates') | Out-Null
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'license-server\src\DeliveryMessage.php') -Destination (Join-Path $stage 'src')
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'license-server\templates\admin.php') -Destination (Join-Path $stage 'templates')
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'license-server\PANEL-PATCH.md') -Destination $stage
Compress-Archive -Path (Join-Path $stage '*') -DestinationPath $zip -CompressionLevel Optimal
Get-Item -LiteralPath $zip | Select-Object FullName,Length
