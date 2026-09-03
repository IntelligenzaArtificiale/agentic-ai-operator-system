[CmdletBinding()]
param(
    [string]$ProcedureRoot=(Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'Agentic AI Operator System'),
    [switch]$Open
)
$ErrorActionPreference='Stop'
$programRoot=Split-Path -Parent $PSCommandPath
$licenseCheck=Join-Path $programRoot 'licensing\check.py'
$licensePython=Join-Path $env:APPDATA 'uv\tools\windows-mcp\Scripts\python.exe'
if(-not(Test-Path -LiteralPath $licenseCheck) -or -not(Test-Path -LiteralPath $licensePython)){throw 'Componente licenza non installato.'}
& $licensePython $licenseCheck | Out-Null
if($LASTEXITCODE -ne 0){
    $activation=Join-Path $programRoot 'licensing\activation_ui.py'
    $licensePythonW=Join-Path (Split-Path $licensePython) 'pythonw.exe'
    Start-Process -FilePath $licensePythonW -ArgumentList @($activation) -WindowStyle Hidden
    throw 'Licenza non attiva. Usa la finestra di attivazione dedicata.'
}
$dashboardRoot=Join-Path $programRoot 'dashboard-live'
$sourceDashboard=Join-Path $PSScriptRoot 'dashboard'
$dataFile=Join-Path $dashboardRoot 'data.js'
New-Item -ItemType Directory -Force -Path $dashboardRoot|Out-Null
foreach($asset in 'index.html','styles.css','dashboard.js'){
    Copy-Item -LiteralPath (Join-Path $sourceDashboard $asset) -Destination $dashboardRoot -Force
}

function Find-Codex {
    $root=Join-Path $env:LOCALAPPDATA 'OpenAI\Codex\bin'
    $candidate=Get-ChildItem -LiteralPath $root -Filter codex.exe -Recurse -File -ErrorAction SilentlyContinue|Sort-Object LastWriteTime -Descending|Select-Object -First 1
    if($candidate){return $candidate.FullName}
    $command=Get-Command codex.exe -ErrorAction SilentlyContinue
    if($command){return $command.Source}
    return $null
}

function To-FileUri([string]$Path){return ([Uri]([IO.Path]::GetFullPath($Path))).AbsoluteUri}

function Read-Runs([string]$ProcedurePath){
    $runs=@()
    $runsPath=Join-Path $ProcedurePath 'runs'
    if(Test-Path -LiteralPath $runsPath){
        Get-ChildItem -LiteralPath $runsPath -Filter '*.json' -File -ErrorAction SilentlyContinue|ForEach-Object{
            try{
                $run=Get-Content -Raw -LiteralPath $_.FullName|ConvertFrom-Json
                if($null-ne $run.duration_ms -and $run.run_id){$runs+=$run}
            }catch{}
        }
    }
    return @($runs)
}

function Read-IncidentCount([string]$ProcedurePath){
    $path=Join-Path $ProcedurePath 'experience\errors.jsonl'
    if(-not(Test-Path -LiteralPath $path)){return 0}
    return @(Get-Content -LiteralPath $path -ErrorAction SilentlyContinue|Where-Object{
        if(-not $_.Trim()){return $false}
        try{$_|ConvertFrom-Json|Out-Null;return $true}catch{return $false}
    }).Count
}

function Read-SharedExperience([string]$Root){
    $result=[ordered]@{files=0;lessons=0;candidates=0;validated=0}
    $path=Join-Path $Root 'experience'
    if(-not(Test-Path -LiteralPath $path)){return $result}
    Get-ChildItem -LiteralPath $path -Filter '*.json' -Recurse -File -ErrorAction SilentlyContinue|Where-Object{$_.Name-ne 'index.json'}|ForEach-Object{
        try{
            $document=Get-Content -Raw -LiteralPath $_.FullName|ConvertFrom-Json
            $result.files++
            foreach($lesson in @($document.lessons)){
                $result.lessons++
                if($lesson.status-eq 'validated'){$result.validated++}else{$result.candidates++}
            }
        }catch{}
    }
    return $result
}

function Get-Metrics([array]$Runs,[int]$IncidentCount){
    $completed=@($Runs|Where-Object{$_.outcome -in @('succeeded','failed','unverified','cancelled')})
    $verified=@($completed|Where-Object{$_.outcome-eq 'succeeded' -and $_.verification_status-eq 'verified'})
    $durations=@($verified|ForEach-Object{[double]$_.duration_ms})
    $stepSamples=@{}
    foreach($run in $verified){
        foreach($step in @($run.steps)){
            if($null-eq $step.duration_ms){continue}
            $key=if($step.step_id){[string]$step.step_id}else{[string]$step.label}
            if(-not $stepSamples.ContainsKey($key)){$stepSamples[$key]=[ordered]@{label=[string]$step.label;values=@()}}
            $stepSamples[$key].values+= [double]$step.duration_ms
        }
    }
    $slow=@($stepSamples.Values|ForEach-Object{
        [ordered]@{label=$_.label;samples=$_.values.Count;average_duration_ms=[math]::Round(($_.values|Measure-Object -Average).Average)}
    }|Sort-Object average_duration_ms -Descending|Select-Object -First 5)
    $aiInterventions=0;$deterministicBlocks=0
    foreach($run in $completed){
        if($run.metrics.ai_interventions){$aiInterventions+=[int]$run.metrics.ai_interventions}
        if($run.metrics.deterministic_blocks){$deterministicBlocks+=[int]$run.metrics.deterministic_blocks}
    }
    return [ordered]@{
        run_count=$completed.Count
        successful_runs=$verified.Count
        failed_runs=@($completed|Where-Object{$_.outcome-eq 'failed'}).Count
        unverified_runs=@($completed|Where-Object{$_.outcome-eq 'unverified' -or ($_.outcome-eq 'succeeded' -and $_.verification_status-ne 'verified')}).Count
        average_duration_ms=if($durations.Count){[math]::Round(($durations|Measure-Object -Average).Average)}else{$null}
        best_duration_ms=if($durations.Count){[math]::Round(($durations|Measure-Object -Minimum).Minimum)}else{$null}
        last_duration_ms=if($verified.Count){[math]::Round([double]$verified[-1].duration_ms)}else{$null}
        incident_count=$IncidentCount
        ai_interventions=$aiInterventions
        deterministic_blocks=$deterministicBlocks
        slowest_steps=$slow
    }
}

$codex=Find-Codex
$mcp=$false;$plugin=$false
if($codex){
    try{$mcp=((& $codex mcp get windows-mcp 2>$null|Out-String)-match 'enabled:\s+true')}catch{}
    try{$plugin=((& $codex plugin list 2>$null|Out-String)-match '(?m)^automazione-totale-procedure@personal\s+installed, enabled')}catch{}
}
$chatgpt=[bool](Get-AppxPackage -ErrorAction SilentlyContinue|Where-Object{$_.Name-match 'ChatGPT|OpenAI' -or $_.PackageFullName-match 'ChatGPT|OpenAI'}|Select-Object -First 1)
$recorder=[bool](Get-ChildItem -LiteralPath (Join-Path $env:LOCALAPPDATA 'Programs\Intelligenza Artificiale Italia\Agentic AI Operator System\OpenSteps') -Filter OpenSteps.App.exe -Recurse -File -ErrorAction SilentlyContinue|Select-Object -First 1)
$items=@()
$proceduresPath=Join-Path $ProcedureRoot 'procedure'
if(Test-Path -LiteralPath $proceduresPath){
    Get-ChildItem -LiteralPath $proceduresPath -Directory|ForEach-Object{
        $metaPath=Join-Path $_.FullName 'procedure.json'
        if(Test-Path -LiteralPath $metaPath){
            try{
                $meta=Get-Content -Raw -LiteralPath $metaPath|ConvertFrom-Json
                $runs=Read-Runs $_.FullName
                $metrics=Get-Metrics $runs (Read-IncidentCount $_.FullName)
                $planStatus='missing';$planBlocks=0
                $planPath=Join-Path $_.FullName 'execution-plan.json'
                if(Test-Path -LiteralPath $planPath){
                    $plan=Get-Content -Raw -LiteralPath $planPath|ConvertFrom-Json
                    $planStatus=[string]$plan.status;$planBlocks=@($plan.blocks).Count
                }
                $shots=@(Get-ChildItem -LiteralPath (Join-Path $_.FullName 'references\screenshots') -File -ErrorAction SilentlyContinue|Select-Object -First 6|ForEach-Object{To-FileUri $_.FullName})
                $items+=[ordered]@{meta=$meta;plan=[ordered]@{status=$planStatus;blocks=$planBlocks};metrics=$metrics;path=$_.FullName;folder_uri=(To-FileUri $_.FullName);screenshots=$shots}
            }catch{}
        }
    }
}
$allMetrics=@($items|ForEach-Object{$_.metrics})
$allDurations=@($allMetrics|Where-Object{$null-ne $_.average_duration_ms}|ForEach-Object{[double]$_.average_duration_ms})
$totalRuns=0;$totalSuccessful=0;$totalUnverified=0;$totalIncidents=0;$totalAi=0
foreach($metrics in $allMetrics){
    $totalRuns+=[int]$metrics.run_count
    $totalSuccessful+=[int]$metrics.successful_runs
    $totalUnverified+=[int]$metrics.unverified_runs
    $totalIncidents+=[int]$metrics.incident_count
    $totalAi+=[int]$metrics.ai_interventions
}
$counts=[ordered]@{
    total=$items.Count
    draft=@($items|Where-Object{$_.meta.status-eq 'draft'}).Count
    validated=@($items|Where-Object{$_.meta.status-eq 'validated'}).Count
    active=@($items|Where-Object{$_.meta.status-eq 'active'}).Count
    runs=$totalRuns
    successful_runs=$totalSuccessful
    unverified_runs=$totalUnverified
    incidents=$totalIncidents
    compiled=@($items|Where-Object{$_.plan.status-eq 'compiled'}).Count
    ai_interventions=$totalAi
    average_duration_ms=if($allDurations.Count){[math]::Round(($allDurations|Measure-Object -Average).Average)}else{$null}
}
$sharedExperience=Read-SharedExperience $ProcedureRoot
$counts.shared_lessons=$sharedExperience.lessons
$payload=[ordered]@{
    generated_at=(Get-Date).ToString('o');version='2.5.1';product='Agentic AI Operator System';brand='Intelligenza Artificiale Italia';author='Alessandro Ciciarelli';root=$ProcedureRoot
    system=[ordered]@{chatgpt=$chatgpt;codex=[bool]$codex;mcp=$mcp;plugin=$plugin;recorder=$recorder}
    company=[ordered]@{status='not_configured'}
    counts=$counts;experience=$sharedExperience;procedures=$items
}
$companyPath=Join-Path $ProcedureRoot 'company-profile.json'
if(Test-Path -LiteralPath $companyPath){
    try{$payload.company=Get-Content -Raw -LiteralPath $companyPath|ConvertFrom-Json}catch{}
}
$json=$payload|ConvertTo-Json -Depth 30 -Compress
[IO.File]::WriteAllText($dataFile,"window.ATPA_DATA=$json;",[Text.UTF8Encoding]::new($false))
if($Open){
    $serverUrl='http://127.0.0.1:8765/'
    $running=$false
    try{Invoke-WebRequest -Uri $serverUrl -UseBasicParsing -TimeoutSec 1|Out-Null;$running=$true}catch{}
    if(-not $running){
        $server=Join-Path $programRoot 'licensing\dashboard_server.py'
        $licensePythonW=Join-Path (Split-Path $licensePython) 'pythonw.exe'
        Start-Process -FilePath $licensePythonW -ArgumentList @($server) -WindowStyle Hidden
        Start-Sleep -Milliseconds 500
    }
    Start-Process $serverUrl
}
$payload
