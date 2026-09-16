[CmdletBinding()]
param(
    [string]$ProcedureRoot=(Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'Agentic AI Operator System'),
    [switch]$Open
)
$ErrorActionPreference='Stop'
$programRoot=Split-Path -Parent $PSCommandPath
. (Join-Path $programRoot 'Invoke-BackgroundCommand.ps1')
$licensePython=Join-Path $env:APPDATA 'uv\tools\windows-mcp\Scripts\python.exe'
$licenseCheck=Join-Path $programRoot 'licensing\check.py'
if(-not(Test-Path -LiteralPath $licenseCheck) -or -not(Test-Path -LiteralPath $licensePython)){throw 'Componente licenza non installato.'}
$licenseResult=Invoke-AiosBackgroundCommand -FilePath $licensePython -Arguments @($licenseCheck)
if($licenseResult.ExitCode -ne 0){throw 'Licenza non attiva. Apri dal Desktop Attiva Agentic AI Operator System e verifica lo stato.'}
$dashboardRoot=Join-Path $programRoot 'dashboard-live'
New-Item -ItemType Directory -Force -Path $dashboardRoot|Out-Null
foreach($asset in 'index.html','styles.css','tokens.css','workspace.css','dashboard.js','view.js','detail.js'){
    Copy-Item -LiteralPath (Join-Path $programRoot "dashboard\$asset") -Destination $dashboardRoot -Force
}
function Find-Codex {
    $root=Join-Path $env:LOCALAPPDATA 'OpenAI\Codex\bin'
    $candidate=Get-ChildItem -LiteralPath $root -Filter codex.exe -Recurse -File -ErrorAction SilentlyContinue|Sort-Object LastWriteTime -Descending|Select-Object -First 1
    if($candidate){return $candidate.FullName}
    $command=Get-Command codex.exe -ErrorAction SilentlyContinue
    if($command){return $command.Source}
    return $null
}
$codex=Find-Codex
$mcp=$false;$plugin=$false;$runner=$false
if($codex){
    try{$result=Invoke-AiosBackgroundCommand -FilePath $codex -Arguments @('mcp','get','windows-mcp');$mcp=($result.ExitCode -eq 0 -and $result.Output -match 'enabled:\s+true')}catch{}
    try{$result=Invoke-AiosBackgroundCommand -FilePath $codex -Arguments @('mcp','get','procedure-runner');$runner=($result.ExitCode -eq 0 -and $result.Output -match 'enabled:\s+true')}catch{}
    try{$result=Invoke-AiosBackgroundCommand -FilePath $codex -Arguments @('plugin','list');$plugin=($result.ExitCode -eq 0 -and $result.Output -match '(?m)^automazione-totale-procedure@personal\s+installed, enabled')}catch{}
}
$recorder=[bool](Get-ChildItem -LiteralPath (Join-Path $programRoot 'OpenSteps') -Filter OpenSteps.App.exe -Recurse -File -ErrorAction SilentlyContinue|Select-Object -First 1)
$settings=[ordered]@{
    procedure_root=[IO.Path]::GetFullPath($ProcedureRoot)
    system=[ordered]@{codex=[bool]$codex;mcp=$mcp;runner=$runner;plugin=$plugin;recorder=$recorder;checked_at=(Get-Date).ToString('o')}
}
$settingsPath=Join-Path $dashboardRoot 'settings.json'
$tempSettings=Join-Path $dashboardRoot ('settings-'+[guid]::NewGuid().ToString('N')+'.tmp')
try{
    [IO.File]::WriteAllText($tempSettings,($settings|ConvertTo-Json -Depth 5),[Text.UTF8Encoding]::new($false))
    Move-Item -LiteralPath $tempSettings -Destination $settingsPath -Force
}finally{if(Test-Path -LiteralPath $tempSettings){Remove-Item -LiteralPath $tempSettings -Force}}
# Keep the default URL ready even when the caller only wants a link.
& {
    $serverUrl='http://127.0.0.1:8765/'
    $running=$false
    try{
        $response=Invoke-WebRequest -Uri $serverUrl -UseBasicParsing -TimeoutSec 2
        if($response.Headers['X-AIOS-Dashboard'] -ne '1'){throw 'La porta 8765 è occupata da un altro servizio.'}
        $running=$true
    }catch{
        if($_.Exception.Response){
            if($_.Exception.Response.Headers['X-AIOS-Dashboard'] -eq '1'){$running=$true}
            else{throw 'La porta 8765 è occupata da un altro servizio o da una dashboard precedente. Riavvia AIOS.'}
        }elseif($_.Exception.Message -like '*porta 8765*'){throw}
    }
    if(-not $running){
        $server=Join-Path $programRoot 'licensing\dashboard_server.py'
        $licensePythonW=Join-Path (Split-Path $licensePython) 'pythonw.exe'
        Start-Process -FilePath $licensePythonW -ArgumentList @(('"'+$server+'"')) -WindowStyle Hidden
        for($attempt=0;$attempt -lt 20;$attempt++){
            Start-Sleep -Milliseconds 250
            try{
                $response=Invoke-WebRequest -Uri $serverUrl -UseBasicParsing -TimeoutSec 1
                if($response.Headers['X-AIOS-Dashboard'] -eq '1'){$running=$true;break}
            }catch{}
        }
        if(-not $running){throw 'Dashboard non avviata. Verifica la licenza e riprova.'}
    }
    if($Open){Start-Process $serverUrl}
}
[pscustomobject]@{ready=$true;url='http://127.0.0.1:8765/';procedure_root=$settings.procedure_root}
