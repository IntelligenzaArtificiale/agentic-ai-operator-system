[CmdletBinding()]
param([string]$Version = '0.6.0')

$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$python = Join-Path $root '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) { throw 'Eseguire prima: py -3.12 -m venv .venv' }

& $python -m pip install -e . pyinstaller
if ($LASTEXITCODE -ne 0) { throw 'Installazione dipendenze di build non riuscita.' }
& $python -m PyInstaller --noconfirm --clean --onedir --name winbridge --hidden-import winbridge.selftest (Join-Path $root 'src\winbridge\launcher.py')
if ($LASTEXITCODE -ne 0) { throw 'Creazione eseguibile non riuscita.' }

$releaseRoot = Join-Path $root "release\WinBridge-$Version-Windows-x64"
if (Test-Path -LiteralPath $releaseRoot) { Remove-Item -LiteralPath $releaseRoot -Recurse -Force }
New-Item -ItemType Directory -Force -Path $releaseRoot | Out-Null
Copy-Item -LiteralPath (Join-Path $root 'dist\winbridge') -Destination (Join-Path $releaseRoot 'app') -Recurse
Copy-Item -LiteralPath (Join-Path $root 'plugin') -Destination (Join-Path $releaseRoot 'plugin') -Recurse
Copy-Item -Path (Join-Path $root 'installer\*') -Destination $releaseRoot -Recurse
Copy-Item -LiteralPath (Join-Path $root 'README.md') -Destination $releaseRoot

$zip = "$releaseRoot.zip"
if (Test-Path -LiteralPath $zip) { Remove-Item -LiteralPath $zip -Force }
Compress-Archive -LiteralPath $releaseRoot -DestinationPath $zip -CompressionLevel Optimal
Write-Host $zip
