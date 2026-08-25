$ErrorActionPreference='Stop'
$testRoot=Join-Path ([IO.Path]::GetTempPath()) ('agentic-dashboard-test-'+[guid]::NewGuid().ToString('N'))
$procedureRoot=Join-Path $testRoot 'Agentic AI Operator System'
$procedure=Join-Path $procedureRoot 'procedure\invio-email-test'
$utf8=[Text.UTF8Encoding]::new($false)
try{
    New-Item -ItemType Directory -Force -Path (Join-Path $procedure 'runs'),(Join-Path $procedure 'experience'),(Join-Path $procedure 'references\screenshots')|Out-Null
    $meta=@{name='Invio email test';slug='invio-email-test';description='Fixture';department='QA';category='Test';roles=@();status='validated';version='1.0.0';flow=@{nodes=@();edges=@()}}
    [IO.File]::WriteAllText((Join-Path $procedure 'procedure.json'),($meta|ConvertTo-Json -Depth 10),$utf8)
    $run1=@{schema_version=1;run_id='run-1';outcome='succeeded';verification_status='verified';duration_ms=4200;steps=@(@{step_id='read';label='Leggi elemento';duration_ms=1200})}
    $run2=@{schema_version=1;run_id='run-2';outcome='unverified';verification_status='unverified';duration_ms=2100;steps=@(@{step_id='write';label='Modifica elemento';duration_ms=700})}
    $legacyFalsePositive=@{schema_version=1;run_id='run-legacy';outcome='succeeded';duration_ms=900;steps=@(@{step_id='write';label='Modifica elemento';duration_ms=300})}
    [IO.File]::WriteAllText((Join-Path $procedure 'runs\run-1.json'),($run1|ConvertTo-Json -Depth 10),$utf8)
    [IO.File]::WriteAllText((Join-Path $procedure 'runs\run-2.json'),($run2|ConvertTo-Json -Depth 10),$utf8)
    [IO.File]::WriteAllText((Join-Path $procedure 'runs\run-legacy.json'),($legacyFalsePositive|ConvertTo-Json -Depth 10),$utf8)
    [IO.File]::WriteAllText((Join-Path $procedure 'experience\errors.jsonl'),'{"incident_id":"incident-1"}',$utf8)
    & (Join-Path $PSScriptRoot '..\atpa-v1\runtime\Update-Dashboard.ps1') -ProcedureRoot $procedureRoot|Out-Null
    $data=Get-Content -Raw -LiteralPath (Join-Path $procedureRoot 'catalogo\data.js')
    if($data -notmatch '"runs":3'){throw "Conteggio run non corretto. Data: $data"}
    if($data -notmatch '"incidents":1'){throw 'Conteggio incidenti non corretto.'}
    if($data -notmatch '"successful_runs":1'){throw 'Conteggio successi verificati non corretto.'}
    if($data -notmatch '"unverified_runs":2'){throw 'Conteggio run non verificate non corretto.'}
    if($data -notmatch '"best_duration_ms":4200'){throw 'Una run non verificata ha contaminato le durate.'}
    foreach($asset in 'index.html','styles.css','dashboard.js','data.js'){
        if(-not(Test-Path -LiteralPath (Join-Path $procedureRoot "catalogo\$asset"))){throw "Asset dashboard mancante: $asset"}
    }
    Write-Host 'Dashboard telemetry test passed.'
}finally{
    if(Test-Path -LiteralPath $testRoot){Remove-Item -LiteralPath $testRoot -Recurse -Force}
}
