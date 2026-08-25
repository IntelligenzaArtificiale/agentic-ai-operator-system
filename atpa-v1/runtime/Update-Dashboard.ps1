[CmdletBinding()]
param(
    [string]$ProcedureRoot = (Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'Agentic AI Operator System'),
    [switch]$Open
)
$ErrorActionPreference='Stop'
$dashboardRoot=Join-Path $ProcedureRoot 'catalogo'
$dataFile=Join-Path $dashboardRoot 'data.js'
$indexFile=Join-Path $dashboardRoot 'index.html'
New-Item -ItemType Directory -Force -Path $dashboardRoot | Out-Null
Copy-Item -LiteralPath (Join-Path $PSScriptRoot 'dashboard\index.html') -Destination $indexFile -Force

function Find-Codex {
    $root=Join-Path $env:LOCALAPPDATA 'OpenAI\Codex\bin'
    $candidate=Get-ChildItem -LiteralPath $root -Filter codex.exe -Recurse -File -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if($candidate){return $candidate.FullName}
    $cmd=Get-Command codex.exe -ErrorAction SilentlyContinue
    if($cmd){return $cmd.Source}
    return $null
}
function To-FileUri([string]$Path){ return ([Uri]([IO.Path]::GetFullPath($Path))).AbsoluteUri }

$codex=Find-Codex
$mcp=$false;$plugin=$false
if($codex){
    try{$mcp=((& $codex mcp get windows-mcp 2>$null | Out-String) -match 'enabled:\s+true')}catch{}
    try{$plugin=((& $codex plugin list 2>$null | Out-String) -match '(?m)^automazione-totale-procedure@personal\s+installed, enabled')}catch{}
}
$chatgpt=[bool](Get-AppxPackage -ErrorAction SilentlyContinue | Where-Object {$_.Name -match 'ChatGPT|OpenAI' -or $_.PackageFullName -match 'ChatGPT|OpenAI'} | Select-Object -First 1)
$recorder=[bool](Get-ChildItem -LiteralPath (Join-Path $env:LOCALAPPDATA 'Programs\Intelligenza Artificiale Italia\Agentic AI Operator System\OpenSteps') -Filter OpenSteps.App.exe -Recurse -File -ErrorAction SilentlyContinue | Select-Object -First 1)
$items=@()
$proceduresPath=Join-Path $ProcedureRoot 'procedure'
if(Test-Path -LiteralPath $proceduresPath){
    Get-ChildItem -LiteralPath $proceduresPath -Directory | ForEach-Object {
        $metaPath=Join-Path $_.FullName 'procedure.json'
        if(Test-Path -LiteralPath $metaPath){
            try{
                $meta=Get-Content -Raw -LiteralPath $metaPath | ConvertFrom-Json
                $shots=@(Get-ChildItem -LiteralPath (Join-Path $_.FullName 'references\screenshots') -File -ErrorAction SilentlyContinue | Select-Object -First 6 | ForEach-Object {To-FileUri $_.FullName})
                $items += [ordered]@{meta=$meta;path=$_.FullName;folder_uri=(To-FileUri $_.FullName);screenshots=$shots}
            }catch{}
        }
    }
}
$counts=[ordered]@{total=$items.Count;draft=@($items|Where-Object {$_.meta.status -eq 'draft'}).Count;validated=@($items|Where-Object {$_.meta.status -eq 'validated'}).Count;active=@($items|Where-Object {$_.meta.status -eq 'active'}).Count}
$payload=[ordered]@{
    generated_at=(Get-Date).ToString('o');version='2.0.0';product='Agentic AI Operator System';brand='Intelligenza Artificiale Italia';author='Alessandro Ciciarelli';root=$ProcedureRoot
    system=[ordered]@{chatgpt=$chatgpt;codex=[bool]$codex;mcp=$mcp;plugin=$plugin;recorder=$recorder}
    counts=$counts;procedures=$items
}
$json=$payload|ConvertTo-Json -Depth 20 -Compress
[IO.File]::WriteAllText($dataFile,"window.ATPA_DATA=$json;",[Text.UTF8Encoding]::new($false))
if($Open){Start-Process $indexFile}
$payload
