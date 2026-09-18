# Package only the public Setup skill; never includes the license server or runtime.
[CmdletBinding()]
param([string]$OutputPath)
$ErrorActionPreference='Stop'
$repositoryRoot=Split-Path $PSScriptRoot -Parent
$pluginRoot=Join-Path $repositoryRoot 'marketplace\agentic-ai-operator-system-setup'
$assetsPath=Join-Path $pluginRoot 'assets'
$manifest=Get-Content -LiteralPath (Join-Path $pluginRoot '.codex-plugin\plugin.json') -Raw | ConvertFrom-Json
if(-not $OutputPath){$OutputPath=Join-Path $repositoryRoot ('release\AIOS-Setup-Plugin-'+$manifest.version+'-'+(Get-Date -Format 'yyyyMMdd-HHmmss')+'.zip')}
if(Test-Path -LiteralPath $OutputPath){throw 'Output already exists; choose a new archive path.'}
New-Item -ItemType Directory -Path $assetsPath -Force | Out-Null
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.IO.Compression.FileSystem
Add-Type -AssemblyName System.IO.Compression

# Code-native geometric brand mark, matching the existing emerald AIOS palette.
foreach($asset in @(@{Name='logo.png';Size=512},@{Name='icon.png';Size=128})){
    $bitmap=New-Object Drawing.Bitmap($asset.Size,$asset.Size)
    $graphics=[Drawing.Graphics]::FromImage($bitmap)
    $ink=New-Object Drawing.SolidBrush([Drawing.ColorTranslator]::FromHtml('#10B981'))
    $light=New-Object Drawing.SolidBrush([Drawing.ColorTranslator]::FromHtml('#EDF6F3'))
    try{
        $graphics.SmoothingMode=[Drawing.Drawing2D.SmoothingMode]::AntiAlias
        $graphics.Clear([Drawing.ColorTranslator]::FromHtml('#0B1715'))
        $graphics.ScaleTransform($asset.Size/512.0,$asset.Size/512.0)
        $points=[Drawing.PointF[]]@(
            [Drawing.PointF]::new(88,366),[Drawing.PointF]::new(176,146),
            [Drawing.PointF]::new(244,146),[Drawing.PointF]::new(332,366),
            [Drawing.PointF]::new(262,366),[Drawing.PointF]::new(246,320),
            [Drawing.PointF]::new(174,320),[Drawing.PointF]::new(158,366)
        )
        $graphics.FillPolygon($ink,$points)
        $cutout=New-Object Drawing.SolidBrush([Drawing.ColorTranslator]::FromHtml('#0B1715'))
        try{$graphics.FillPolygon($cutout,[Drawing.PointF[]]@([Drawing.PointF]::new(189,272),[Drawing.PointF]::new(210,208),[Drawing.PointF]::new(231,272)))}finally{$cutout.Dispose()}
        $graphics.FillRectangle($light,354,214,64,152)
        $graphics.FillEllipse($ink,354,146,64,48)
        $bitmap.Save((Join-Path $assetsPath $asset.Name),[Drawing.Imaging.ImageFormat]::Png)
    }finally{$graphics.Dispose();$bitmap.Dispose();$ink.Dispose();$light.Dispose()}
}

$allowedFiles=@('.codex-plugin/plugin.json','assets/icon.png','assets/logo.png',
    'skills/configura-aios/SKILL.md','skills/configura-aios/references/installazione.md',
    'skills/configura-aios/references/primi-passi.md')
$archive=[IO.Compression.ZipFile]::Open($OutputPath,[IO.Compression.ZipArchiveMode]::Create)
try{
    foreach($relativePath in $allowedFiles){
        $source=Join-Path $pluginRoot $relativePath
        if(-not(Test-Path -LiteralPath $source -PathType Leaf)){throw "Missing package file: $relativePath"}
        [IO.Compression.ZipFileExtensions]::CreateEntryFromFile($archive,$source,$relativePath,[IO.Compression.CompressionLevel]::Optimal) | Out-Null
    }
}finally{$archive.Dispose()}
Get-FileHash -LiteralPath $OutputPath -Algorithm SHA256 | Format-List
