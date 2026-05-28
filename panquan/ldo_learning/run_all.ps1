$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$circuitDir = Join-Path $root "circuits"

Push-Location $circuitDir
try {
    Get-ChildItem -Filter "*.cir" | Sort-Object Name | ForEach-Object {
        $circuit = $_.Name
        $log = "$($_.BaseName).log"
        Write-Host "Running $circuit"
        Start-Process -FilePath "ngspice" -ArgumentList @("-b", "-o", $log, $circuit) -WindowStyle Hidden -Wait
        if (-not (Test-Path $log)) {
            throw "ngspice did not create $log for $($_.Name)"
        }
    }
}
finally {
    Pop-Location
}
