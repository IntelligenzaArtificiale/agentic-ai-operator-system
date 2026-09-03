[CmdletBinding()]
param(
    [switch]$NonInteractive,
    [string]$ResultPath,
    [string]$UpdateManifestUrl='https://github.com/IntelligenzaArtificiale/agentic-ai-operator-system/releases/latest/download/release-manifest.json'
)
$ErrorActionPreference='Stop'
$packageRoot=$PSScriptRoot
$userRoot=[IO.Path]::GetFullPath($env:USERPROFILE)
$programRoot=Join-Path $env:LOCALAPPDATA 'Programs\Intelligenza Artificiale Italia\Agentic AI Operator System'
$procedureRoot=Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'Agentic AI Operator System'
$sharedExperienceRoot=Join-Path $procedureRoot 'experience'
$legacyProcedureRoot=Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'Automazioni Aziendali'
$pluginName='automazione-totale-procedure'
$pluginSource=Join-Path $packageRoot "bundle\$pluginName"
$pluginRoot=Join-Path $userRoot "plugins\$pluginName"
$marketplaceRoot=Join-Path $userRoot '.agents\plugins'
$marketplaceFile=Join-Path $marketplaceRoot 'marketplace.json'
$uv=Join-Path $packageRoot 'payload\uv.exe'
$wheel=Join-Path $packageRoot 'payload\windows_mcp-0.8.5-py3-none-any.whl'
$recorderArchive=Join-Path $packageRoot 'payload\OpenSteps-0.1.0-win-x64.zip'
if(-not(Test-Path -LiteralPath $recorderArchive)){$recorderArchive=Join-Path $packageRoot 'payload\ProcedureRecorder-0.1.0-win-x64.zip'}
$windowsMcpExe=Join-Path $userRoot '.local\bin\windows-mcp.exe'
$runnerPython=Join-Path $env:APPDATA 'uv\tools\windows-mcp\Scripts\python.exe'

function Write-Utf8([string]$Path,[string]$Text){[IO.File]::WriteAllText($Path,$Text,[Text.UTF8Encoding]::new($false))}
function Find-Codex {
    $bin=Join-Path $env:LOCALAPPDATA 'OpenAI\Codex\bin'
    $candidate=Get-ChildItem -LiteralPath $bin -Filter codex.exe -Recurse -File -ErrorAction SilentlyContinue|Sort-Object LastWriteTime -Descending|Select-Object -First 1
    if($candidate){return $candidate.FullName}
    $cmd=Get-Command codex.exe -ErrorAction SilentlyContinue
    if($cmd -and $cmd.Source -notlike '*\WindowsApps\*'){return $cmd.Source}
    throw 'Codex CLI non trovato. Installa o aggiorna ChatGPT/Codex prima di continuare.'
}
if($env:OS -ne 'Windows_NT' -or -not [Environment]::Is64BitOperatingSystem){throw 'Richiesto Windows 10/11 x64.'}
foreach($required in @($uv,$wheel,$recorderArchive,(Join-Path $pluginSource '.codex-plugin\plugin.json'),(Join-Path $packageRoot 'runtime\Update-Dashboard.ps1'),(Join-Path $packageRoot 'runtime\procedure-runner\server.py'),(Join-Path $packageRoot 'runtime\procedure-runner\experience.py'),(Join-Path $packageRoot 'template\company-profile.json'),(Join-Path $packageRoot 'template\shared-experience\index.json'))){if(-not(Test-Path -LiteralPath $required)){throw "Pacchetto incompleto: $required"}}
$codex=Find-Codex

# Motore Windows locale: PyPI per aggiornabilità, wheel incluso come fallback.
$engineRoots=@(
    [IO.Path]::GetFullPath((Join-Path $userRoot '.local\bin\')),
    [IO.Path]::GetFullPath((Join-Path $env:APPDATA 'uv\tools\windows-mcp\'))
)
Get-CimInstance Win32_Process -ErrorAction SilentlyContinue|ForEach-Object{
    $engineProcess=$_
    if($engineProcess.ExecutablePath -and ($engineRoots|Where-Object{$engineProcess.ExecutablePath.StartsWith($_,[StringComparison]::OrdinalIgnoreCase)})){
        Stop-Process -Id $engineProcess.ProcessId -Force -ErrorAction SilentlyContinue
    }
}
Start-Sleep -Milliseconds 500
& $uv tool install --force 'windows-mcp==0.8.5'
if($LASTEXITCODE -ne 0){& $uv tool install --force $wheel}
if($LASTEXITCODE -ne 0 -or -not(Test-Path -LiteralPath $windowsMcpExe)){throw 'Installazione motore Windows non riuscita.'}
if(-not(Test-Path -LiteralPath $runnerPython)){throw 'Runtime Python del motore Windows non trovato.'}
& $codex mcp remove windows-mcp 2>$null|Out-Null
& $codex mcp remove winbridge 2>$null|Out-Null
& $codex mcp add windows-mcp -- $windowsMcpExe serve
if($LASTEXITCODE -ne 0){throw 'Registrazione MCP non riuscita.'}

# Runtime, aggiornamenti e OpenSteps portatile.
New-Item -ItemType Directory -Force -Path $programRoot | Out-Null
Copy-Item -LiteralPath (Join-Path $packageRoot 'runtime\Update-Dashboard.ps1') -Destination $programRoot -Force
Copy-Item -LiteralPath (Join-Path $packageRoot 'runtime\dashboard') -Destination $programRoot -Recurse -Force
Copy-Item -LiteralPath (Join-Path $packageRoot 'runtime\procedure-runner') -Destination $programRoot -Recurse -Force
$runnerServer=Join-Path $programRoot 'procedure-runner\server.py'
& $codex mcp remove procedure-runner 2>$null|Out-Null
& $codex mcp add procedure-runner --env "AGENTIC_PROCEDURE_ROOT=$procedureRoot\procedure" -- $runnerPython $runnerServer
if($LASTEXITCODE -ne 0){throw 'Registrazione procedure runner non riuscita.'}
$updaterSource=Join-Path $packageRoot 'Check-AgenticUpdate.ps1'
if(-not(Test-Path -LiteralPath $updaterSource)){throw 'Pacchetto incompleto: Check-AgenticUpdate.ps1'}
Copy-Item -LiteralPath $updaterSource -Destination $programRoot -Force
Write-Utf8 (Join-Path $programRoot 'update-settings.json') (@{update_manifest_url=$UpdateManifestUrl}|ConvertTo-Json)
Write-Utf8 (Join-Path $programRoot 'installed-version.json') (@{product='Agentic AI Operator System';version='2.4.0';installed_at=(Get-Date).ToString('o')}|ConvertTo-Json)
$recorderRoot=Join-Path $programRoot 'OpenSteps\0.1.0'
if(-not(Test-Path -LiteralPath $recorderRoot)){New-Item -ItemType Directory -Force -Path $recorderRoot|Out-Null;Expand-Archive -LiteralPath $recorderArchive -DestinationPath $recorderRoot}
$recorderExe=Get-ChildItem -LiteralPath $recorderRoot -Filter OpenSteps.App.exe -Recurse -File|Select-Object -First 1
if(-not $recorderExe){throw 'Registratore non trovato dopo l estrazione.'}
$desktop=[Environment]::GetFolderPath('Desktop')
$shell=New-Object -ComObject WScript.Shell
$shortcut=$shell.CreateShortcut((Join-Path $desktop 'Agentic AI Operator System - OpenSteps.lnk'))
$shortcut.TargetPath=$recorderExe.FullName;$shortcut.WorkingDirectory=$recorderExe.DirectoryName;$shortcut.Description='Agentic AI Operator System · Intelligenza Artificiale Italia';$shortcut.Save()

# Migrazione non distruttiva e struttura procedure senza creare procedure reali.
if((Test-Path -LiteralPath $legacyProcedureRoot) -and -not(Test-Path -LiteralPath $procedureRoot)){
    Copy-Item -LiteralPath $legacyProcedureRoot -Destination $procedureRoot -Recurse
}
New-Item -ItemType Directory -Force -Path $procedureRoot,(Join-Path $procedureRoot 'procedure'),(Join-Path $procedureRoot 'registrazioni'),(Join-Path $procedureRoot 'catalogo')|Out-Null
New-Item -ItemType Directory -Force -Path $sharedExperienceRoot,(Join-Path $sharedExperienceRoot 'software'),(Join-Path $sharedExperienceRoot 'business'),(Join-Path $sharedExperienceRoot 'patterns')|Out-Null
$sharedTemplate=Join-Path $packageRoot 'template\shared-experience'
foreach($sharedFile in (Get-ChildItem -LiteralPath $sharedTemplate -Filter '*.json' -Recurse -File)){
    $relative=$sharedFile.FullName.Substring($sharedTemplate.Length).TrimStart('\')
    $target=Join-Path $sharedExperienceRoot $relative
    New-Item -ItemType Directory -Force -Path (Split-Path $target)|Out-Null
    if(-not(Test-Path -LiteralPath $target)){Copy-Item -LiteralPath $sharedFile.FullName -Destination $target}
}
$templateTarget=Join-Path $procedureRoot 'TEMPLATE-PROCEDURA'
if(-not(Test-Path -LiteralPath $templateTarget)){New-Item -ItemType Directory -Path $templateTarget|Out-Null}
Copy-Item -Path (Join-Path $packageRoot 'template\TEMPLATE-PROCEDURA\*') -Destination $templateTarget -Recurse -Force
Copy-Item -LiteralPath (Join-Path $packageRoot 'GUIDA-UTENTE.md') -Destination (Join-Path $procedureRoot 'GUIDA-UTENTE.md') -Force
Copy-Item -LiteralPath (Join-Path $packageRoot 'GUIDA-STRUTTURA-PROCEDURE.md') -Destination (Join-Path $procedureRoot 'GUIDA-STRUTTURA-PROCEDURE.md') -Force
$companyProfile=Join-Path $procedureRoot 'company-profile.json'
if(-not(Test-Path -LiteralPath $companyProfile)){Copy-Item -LiteralPath (Join-Path $packageRoot 'template\company-profile.json') -Destination $companyProfile}

# Migrazione non distruttiva a telemetria 3 e piano compilabile.
$proceduresPath=Join-Path $procedureRoot 'procedure'
Get-ChildItem -LiteralPath $proceduresPath -Directory -ErrorAction SilentlyContinue|ForEach-Object{
    $procedurePath=$_.FullName
    $experiencePath=Join-Path $procedurePath 'experience'
    New-Item -ItemType Directory -Force -Path (Join-Path $procedurePath 'runs'),$experiencePath|Out-Null
    $errorsPath=Join-Path $experiencePath 'errors.jsonl'
    if(-not(Test-Path -LiteralPath $errorsPath)){Write-Utf8 $errorsPath ''}
    $lessonsPath=Join-Path $experiencePath 'lessons.json'
    if(-not(Test-Path -LiteralPath $lessonsPath)){Write-Utf8 $lessonsPath (@{schema_version=1;procedure_slug=$_.Name;updated_at='';lessons=@()}|ConvertTo-Json -Depth 5)}
    $metaPath=Join-Path $procedurePath 'procedure.json'
    if(Test-Path -LiteralPath $metaPath){
        $meta=Get-Content -Raw -LiteralPath $metaPath|ConvertFrom-Json
        if(-not $meta.PSObject.Properties['experience_context']){$meta|Add-Member -NotePropertyName experience_context -NotePropertyValue ([pscustomobject]@{applications=@();departments=@();categories=@();patterns=@();refs=@()})}
        foreach($node in @($meta.flow.nodes)){if(-not $node.PSObject.Properties['required'] -and $node.type -notin @('start','end')){$node|Add-Member -NotePropertyName required -NotePropertyValue $true}}
        if(-not $meta.telemetry){$meta|Add-Member -NotePropertyName telemetry -NotePropertyValue ([pscustomobject]@{schema_version=3;run_count=0;successful_runs=0;failed_runs=0;unverified_runs=0;last_duration_ms=$null;best_duration_ms=$null;ai_interventions=0;deterministic_blocks=0})}
        elseif(-not $meta.telemetry.PSObject.Properties['unverified_runs']){$meta.telemetry|Add-Member -NotePropertyName unverified_runs -NotePropertyValue 0}
        if(-not $meta.telemetry.PSObject.Properties['ai_interventions']){$meta.telemetry|Add-Member -NotePropertyName ai_interventions -NotePropertyValue 0}
        if(-not $meta.telemetry.PSObject.Properties['deterministic_blocks']){$meta.telemetry|Add-Member -NotePropertyName deterministic_blocks -NotePropertyValue 0}
        $meta.telemetry.schema_version=3
        Write-Utf8 $metaPath ($meta|ConvertTo-Json -Depth 30)
    }
    $schemaSource=Join-Path $templateTarget 'references\telemetry-schema.md'
    $schemaTarget=Join-Path $procedurePath 'references\telemetry-schema.md'
    if((Test-Path -LiteralPath $schemaSource) -and -not(Test-Path -LiteralPath $schemaTarget)){Copy-Item -LiteralPath $schemaSource -Destination $schemaTarget -Force}
    $planSchemaSource=Join-Path $templateTarget 'references\execution-plan-schema.md'
    $planSchemaTarget=Join-Path $procedurePath 'references\execution-plan-schema.md'
    if((Test-Path -LiteralPath $planSchemaSource) -and -not(Test-Path -LiteralPath $planSchemaTarget)){Copy-Item -LiteralPath $planSchemaSource -Destination $planSchemaTarget -Force}
    $sharedSchemaSource=Join-Path $templateTarget 'references\shared-experience-schema.md'
    $sharedSchemaTarget=Join-Path $procedurePath 'references\shared-experience-schema.md'
    if((Test-Path -LiteralPath $sharedSchemaSource) -and -not(Test-Path -LiteralPath $sharedSchemaTarget)){Copy-Item -LiteralPath $sharedSchemaSource -Destination $sharedSchemaTarget -Force}
    $planPath=Join-Path $procedurePath 'execution-plan.json'
    if(-not(Test-Path -LiteralPath $planPath)){
        $plan=[ordered]@{schema_version=1;procedure_slug=$_.Name;plan_version='1.0.0';status='exploratory';variables=@();environment=[ordered]@{strategy='controlled';fingerprints=@()};promotion=[ordered]@{minimum_clean_runs=3;clean_runs=0;maximum_duration_variance=0.2;last_evaluated_at=''};blocks=@()}
        Write-Utf8 $planPath ($plan|ConvertTo-Json -Depth 20)
    }
}

# Plugin personale integrato.
& $codex plugin remove 'windows-mcp@personal' 2>$null|Out-Null
& $codex plugin remove "$pluginName@personal" 2>$null|Out-Null
New-Item -ItemType Directory -Force -Path (Split-Path $pluginRoot),$marketplaceRoot|Out-Null
if(Test-Path -LiteralPath $pluginRoot){Move-Item -LiteralPath $pluginRoot -Destination "$pluginRoot.backup.$(Get-Date -Format 'yyyyMMddHHmmss')"}
Copy-Item -LiteralPath $pluginSource -Destination $pluginRoot -Recurse
if(Test-Path -LiteralPath $marketplaceFile){Copy-Item -LiteralPath $marketplaceFile -Destination "$marketplaceFile.backup.$(Get-Date -Format 'yyyyMMddHHmmss')";$market=Get-Content -Raw -LiteralPath $marketplaceFile|ConvertFrom-Json}else{$market=[pscustomobject]@{name='personal';interface=[pscustomobject]@{displayName='Personal'};plugins=@()}}
if($market.name -ne 'personal'){throw 'Marketplace personale incompatibile.'}
$others=@($market.plugins|Where-Object{$_.name -notin @($pluginName,'windows-mcp','winbridge')})
$entry=[pscustomobject]@{name=$pluginName;source=[pscustomobject]@{source='local';path="./plugins/$pluginName"};policy=[pscustomobject]@{installation='AVAILABLE';authentication='ON_INSTALL'};category='Productivity'}
$market.plugins=@($others+$entry);Write-Utf8 $marketplaceFile ($market|ConvertTo-Json -Depth 10)
& $codex plugin add "$pluginName@personal"
if($LASTEXITCODE -ne 0){throw 'Installazione plugin non riuscita.'}

# Dashboard e verifica finale.
$dashboardScript=Join-Path $programRoot 'Update-Dashboard.ps1'
& $dashboardScript -ProcedureRoot $procedureRoot | Out-Null
$mcpText=& $codex mcp get windows-mcp 2>$null|Out-String
$runnerText=& $codex mcp get procedure-runner 2>$null|Out-String
$pluginText=& $codex plugin list 2>$null|Out-String
$result=[ordered]@{ok=$false;product='Agentic AI Operator System';version='2.4.0';mcp_configured=($mcpText-match 'enabled:\s+true');runner_configured=($runnerText-match 'enabled:\s+true');plugin_installed=($pluginText-match "(?m)^$pluginName@personal\s+installed, enabled");opensteps_installed=[bool](Test-Path -LiteralPath $recorderExe.FullName);updater_installed=(Test-Path -LiteralPath (Join-Path $programRoot 'Check-AgenticUpdate.ps1'));update_manifest_url=$UpdateManifestUrl;dashboard_ready=(Test-Path -LiteralPath (Join-Path $procedureRoot 'catalogo\index.html'));company_profile_ready=(Test-Path -LiteralPath $companyProfile);procedure_root=$procedureRoot;restart_required=$true}
$result.ok=$result.mcp_configured -and $result.runner_configured -and $result.plugin_installed -and $result.opensteps_installed -and $result.updater_installed -and $result.dashboard_ready -and $result.company_profile_ready
$out=if($ResultPath){$ResultPath}else{Join-Path $packageRoot 'INSTALL_RESULT.json'};Write-Utf8 $out ($result|ConvertTo-Json -Depth 6)
if(-not $result.ok){throw "Verifica fallita. Leggi $out"}
if(-not $NonInteractive){& $dashboardScript -ProcedureRoot $procedureRoot -Open|Out-Null}
Write-Host 'Agentic AI Operator System 2.4.0 installato correttamente.'
Write-Host "Risultato: $out"
Write-Host 'Chiudi completamente ChatGPT/Codex, riaprilo e crea una nuova task. Il sistema e pronto per la prima procedura.'
