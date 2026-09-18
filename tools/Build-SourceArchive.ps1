# Export tracked development sources, bundled payloads and pinned upstream sources.
# Never exports Git history, old releases, local installation results or secrets.
[CmdletBinding()]
param([Parameter(Mandatory)][string]$OutputPath)
$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot -Parent
$output=[IO.Path]::GetFullPath($OutputPath)
if(Test-Path -LiteralPath $output){throw 'Archive already exists; choose a new path.'}
Add-Type -AssemblyName System.IO.Compression.FileSystem
$files=@(& git -C $root ls-files) | Where-Object {
    $_ -notmatch '^release/' -and $_ -notmatch '(^|/)INSTALL_RESULT\.json$' -and
    $_ -ne 'windows-mcp-package/upstream'
}
if($LASTEXITCODE -ne 0){throw 'Cannot enumerate repository files.'}
$upstream=Join-Path $root 'windows-mcp-package/upstream'
if(-not(Test-Path -LiteralPath (Join-Path $upstream '.git'))){throw 'Windows MCP upstream checkout is required; see docs/DEVELOPMENT-HANDOFF.md.'}
$upstreamFiles=@(& git -C $upstream ls-files)
if($LASTEXITCODE -ne 0){throw 'Cannot enumerate Windows MCP source.'}
$files+=@($upstreamFiles | ForEach-Object {'windows-mcp-package/upstream/'+$_})
$sourceCommit=(& git -C $root rev-parse HEAD).Trim()
$windowsCommit=(& git -C $upstream rev-parse HEAD).Trim()
$openstepsCommit='59def45d2d5ea3da98d4883eee4ac99a53e0efd7'
$temporary=Join-Path ([IO.Path]::GetTempPath()) ('aios-source-'+[guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $temporary | Out-Null
$download=Join-Path $temporary 'opensteps-source.zip'
Invoke-WebRequest -UseBasicParsing -Uri "https://codeload.github.com/ebanez8/openstep/zip/$openstepsCommit" -OutFile $download
$opensteps=[IO.Compression.ZipFile]::OpenRead($download)
$archive=[IO.Compression.ZipFile]::Open($output,[IO.Compression.ZipArchiveMode]::Create)
$inventory=[Collections.Generic.List[object]]::new()
$prefix='Agentic-AI-Operator-System-Source/'
function Add-SourceStream([string]$relative,[IO.Stream]$stream){
    if($relative -match '(^|/)(\.git|\.env|__pycache__)(/|$)' -or
       $relative -match '^license-server/private/(config\.php|license\.json|setup-token\.txt|provisioning\.php)$' -or
       $relative -match '(^|/)\.\.?(/|$)' -or $relative.StartsWith('/')){throw "Forbidden archive path: $relative"}
    $entry=$archive.CreateEntry($prefix+$relative,[IO.Compression.CompressionLevel]::Optimal)
    $target=$entry.Open()
    $sha=[Security.Cryptography.SHA256]::Create()
    try {
        $memory=[IO.MemoryStream]::new()
        try {
            $stream.CopyTo($memory)
            $memory.Position=0
            $hash=[BitConverter]::ToString($sha.ComputeHash($memory)).Replace('-','').ToLowerInvariant()
            $memory.Position=0
            $memory.CopyTo($target)
            $inventory.Add([ordered]@{path=$relative;bytes=$memory.Length;sha256=$hash})
        } finally {$memory.Dispose()}
    } finally {$target.Dispose();$sha.Dispose()}
}
try {
    foreach($relative in ($files | Sort-Object -Unique)){
        $file=Join-Path $root $relative
        if(-not(Test-Path -LiteralPath $file -PathType Leaf)){throw "Missing source: $relative"}
        $stream=[IO.File]::OpenRead($file)
        try {Add-SourceStream $relative $stream} finally {$stream.Dispose()}
    }
    foreach($entry in $opensteps.Entries){
        if($entry.FullName.EndsWith('/')){continue}
        $relative=$entry.FullName.Substring($entry.FullName.IndexOf('/')+1)
        $stream=$entry.Open()
        try {Add-SourceStream ('third-party/opensteps/'+$relative) $stream} finally {$stream.Dispose()}
    }
    $manifest=[ordered]@{
        schema_version=1;created_at=[DateTime]::UtcNow.ToString('o');source_commit=$sourceCommit
        repository='https://github.com/IntelligenzaArtificiale/agentic-ai-operator-system'
        windows_mcp_commit=$windowsCommit;opensteps_commit=$openstepsCommit
        exclusions=@('credentials and license databases','Git history','old release archives','local install results','virtual environments and caches')
        files=$inventory.ToArray()
    }
    $manifestEntry=$archive.CreateEntry($prefix+'SOURCE-MANIFEST.json')
    $writer=[IO.StreamWriter]::new($manifestEntry.Open(),[Text.UTF8Encoding]::new($false))
    try {$writer.Write(($manifest | ConvertTo-Json -Depth 8))} finally {$writer.Dispose()}
} finally {$archive.Dispose();$opensteps.Dispose()}
# Keep the uniquely named temporary upstream download for auditing; do not delete broad paths.
[pscustomobject]@{archive=$output;files=$inventory.Count;sha256=(Get-FileHash -LiteralPath $output -Algorithm SHA256).Hash;source_commit=$sourceCommit}
