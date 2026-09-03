$ErrorActionPreference='Stop'
$testRoot=Join-Path ([IO.Path]::GetTempPath()) ('agentic-dashboard-test-'+[guid]::NewGuid().ToString('N'))
$procedureRoot=Join-Path $testRoot 'Agentic AI Operator System'
$procedure=Join-Path $procedureRoot 'procedure\processo-test'
$utf8=[Text.UTF8Encoding]::new($false)
try{
    New-Item -ItemType Directory -Force -Path (Join-Path $procedure 'runs'),(Join-Path $procedure 'experience'),(Join-Path $procedure 'references\screenshots')|Out-Null
    $meta=@{name='Processo test';slug='processo-test';description='Fixture';department='QA';category='Test';roles=@();status='validated';version='1.0.0';flow=@{nodes=@();edges=@()}}
    [IO.File]::WriteAllText((Join-Path $procedure 'procedure.json'),($meta|ConvertTo-Json -Depth 10),$utf8)
    $company=@{schema_version=1;status='configured';identity=@{display_name='Azienda QA'};business=@{summary='Profilo di prova';sectors=@('Servizi')};operations=@{departments=@('Qualita')};sources=@(@{title='Fonte'})}
    [IO.File]::WriteAllText((Join-Path $procedureRoot 'company-profile.json'),($company|ConvertTo-Json -Depth 10),$utf8)
    $plan=@{schema_version=1;procedure_slug='processo-test';status='compiled';blocks=@(@{id='work';executor='deterministic';side_effect='none'})}
    [IO.File]::WriteAllText((Join-Path $procedure 'execution-plan.json'),($plan|ConvertTo-Json -Depth 10),$utf8)
    $run1=@{schema_version=3;run_id='run-1';outcome='succeeded';verification_status='verified';duration_ms=4200;metrics=@{ai_interventions=1;deterministic_blocks=2};steps=@(@{step_id='read';label='Leggi elemento';duration_ms=1200})}
    $run2=@{schema_version=1;run_id='run-2';outcome='unverified';verification_status='unverified';duration_ms=2100;steps=@(@{step_id='write';label='Modifica elemento';duration_ms=700})}
    $legacyFalsePositive=@{schema_version=1;run_id='run-legacy';outcome='succeeded';duration_ms=900;steps=@(@{step_id='write';label='Modifica elemento';duration_ms=300})}
    [IO.File]::WriteAllText((Join-Path $procedure 'runs\run-1.json'),($run1|ConvertTo-Json -Depth 10),$utf8)
    [IO.File]::WriteAllText((Join-Path $procedure 'runs\run-2.json'),($run2|ConvertTo-Json -Depth 10),$utf8)
    [IO.File]::WriteAllText((Join-Path $procedure 'runs\run-legacy.json'),($legacyFalsePositive|ConvertTo-Json -Depth 10),$utf8)
    [IO.File]::WriteAllText((Join-Path $procedure 'experience\errors.jsonl'),'{"incident_id":"incident-1"}',$utf8)
    $sharedPath=Join-Path $procedureRoot 'experience\patterns';New-Item -ItemType Directory -Force -Path $sharedPath|Out-Null
    $shared=@{schema_version=1;lessons=@(@{lesson_id='shared-1';status='candidate'},@{lesson_id='shared-2';status='validated'})}
    [IO.File]::WriteAllText((Join-Path $sharedPath 'fixture.json'),($shared|ConvertTo-Json -Depth 10),$utf8)
    & (Join-Path $PSScriptRoot '..\atpa-v1\runtime\Update-Dashboard.ps1') -ProcedureRoot $procedureRoot|Out-Null
    $data=Get-Content -Raw -LiteralPath (Join-Path $procedureRoot 'catalogo\data.js')
    if($data -notmatch '"runs":3'){throw "Conteggio run non corretto. Data: $data"}
    if($data -notmatch '"incidents":1'){throw 'Conteggio incidenti non corretto.'}
    if($data -notmatch '"successful_runs":1'){throw 'Conteggio successi verificati non corretto.'}
    if($data -notmatch '"unverified_runs":2'){throw 'Conteggio run non verificate non corretto.'}
    if($data -notmatch '"best_duration_ms":4200'){throw 'Una run non verificata ha contaminato le durate.'}
    if($data -notmatch '"compiled":1'){throw 'Piano compilato non contato.'}
    if($data -notmatch '"ai_interventions":1'){throw 'Interventi IA non conteggiati.'}
    if($data -notmatch '"deterministic_blocks":2'){throw 'Blocchi locali non conteggiati.'}
    if($data -notmatch '"shared_lessons":2'){throw 'Esperienze condivise non conteggiate.'}
    if($data -notmatch '"candidates":1'){throw 'Esperienze candidate non conteggiate.'}
    if($data -notmatch '"validated":1'){throw 'Esperienze validate non conteggiate.'}
    if($data -notmatch '"display_name":"Azienda QA"'){throw 'Profilo azienda non incluso.'}
    if($data -notmatch '"version":"2.4.0"'){throw 'Versione dashboard non corretta.'}
    foreach($asset in 'index.html','styles.css','dashboard.js','data.js'){
        if(-not(Test-Path -LiteralPath (Join-Path $procedureRoot "catalogo\$asset"))){throw "Asset dashboard mancante: $asset"}
    }
    Write-Host 'Dashboard telemetry test passed.'
}finally{
    if(Test-Path -LiteralPath $testRoot){Remove-Item -LiteralPath $testRoot -Recurse -Force}
}
