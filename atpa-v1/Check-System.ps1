[CmdletBinding()]param([switch]$OpenDashboard)
$program=Join-Path $env:LOCALAPPDATA 'Programs\Intelligenza Artificiale Italia\Automazione Totale Procedure Aziendali'
$script=Join-Path $program 'Update-Dashboard.ps1'
if(-not(Test-Path -LiteralPath $script)){throw 'Sistema non installato o incompleto.'}
& $script -Open:$OpenDashboard
