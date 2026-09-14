# Internal CLI commands: no console window, captured output, bounded wait.
function ConvertTo-AiosProcessArgument([string]$Value) {
    $escaped=[regex]::Replace($Value,'(\\*)"','$1$1\"')
    $escaped=[regex]::Replace($escaped,'(\\+)$','$1$1')
    return '"'+$escaped+'"'
}

function Invoke-AiosBackgroundCommand {
    param([Parameter(Mandatory)][string]$FilePath,[string[]]$Arguments=@(),[ValidateRange(1,300)][int]$TimeoutSeconds=30)
    $info=New-Object System.Diagnostics.ProcessStartInfo
    $info.FileName=$FilePath
    $info.Arguments=(@($Arguments|ForEach-Object {ConvertTo-AiosProcessArgument $_}) -join ' ')
    $info.UseShellExecute=$false
    $info.CreateNoWindow=$true
    $info.RedirectStandardOutput=$true
    $info.RedirectStandardError=$true
    $info.RedirectStandardInput=$true
    $process=New-Object System.Diagnostics.Process
    $process.StartInfo=$info
    try {
        if(-not $process.Start()){throw 'Avvio comando di servizio non riuscito.'}
        $process.StandardInput.Close()
        $stdout=$process.StandardOutput.ReadToEndAsync()
        $stderr=$process.StandardError.ReadToEndAsync()
        if(-not $process.WaitForExit($TimeoutSeconds*1000)){
            $process.Kill()
            throw "Timeout del comando di servizio: $([IO.Path]::GetFileName($FilePath))"
        }
        if(-not [Threading.Tasks.Task]::WaitAll([Threading.Tasks.Task[]]@($stdout,$stderr),1000)){
            throw 'Timeout durante la lettura del risultato del comando di servizio.'
        }
        [pscustomobject]@{ExitCode=$process.ExitCode;Output=$stdout.GetAwaiter().GetResult();Error=$stderr.GetAwaiter().GetResult()}
    } finally {$process.Dispose()}
}
